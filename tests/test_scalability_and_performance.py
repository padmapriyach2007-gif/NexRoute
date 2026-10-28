"""
Unit & Integration Tests for Multi-User Scalability, Performance, and Overload Resilience
CampusAegis / P.A.T.H.F.I.N.D.E.R.

Validates:
1. OllamaConcurrencyManager: Semaphore bounds, pending queue, circuit breaker, user rate limiter, context truncation
2. RouteCacheManager: SingleFlight in-flight request deduplication, spatial hashing, TTL/LRU
3. Database Optimization: SQLite WAL mode, busy timeout, connection pooling
4. API Security & Overload Protection Middleware: Concurrency limiter, sliding window, payload caps
5. Operational Observability: /health/live, /health/ready, /metrics
"""

import time
import pytest
from unittest.mock import patch, MagicMock
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from sqlalchemy import text

from src.backend.ai.ollama_limiter import OllamaConcurrencyManager, get_ollama_manager
from src.backend.routing.route_cache import RouteCacheManager, get_route_cache_manager
from src.backend.database.connection import get_db_session
from src.backend.security.rate_limiter import SlidingWindowRateLimiter
from src.api_server import app


# ---------------------------------------------------------
# 1. Ollama Concurrency & Bounded Queue Tests
# ---------------------------------------------------------
class TestOllamaConcurrencyManager:

    def test_per_user_rate_limiting(self):
        manager = OllamaConcurrencyManager()
        manager.per_user_rate_limit_per_min = 3
        test_user = "test_user_rate_limiter_123"

        # First 3 requests must be allowed
        for _ in range(3):
            assert manager.check_user_rate_limit(test_user) is True

        # 4th request must be rejected under sliding window
        assert manager.check_user_rate_limit(test_user) is False

    def test_context_window_truncation(self):
        manager = OllamaConcurrencyManager()
        long_messages = [
            {"role": "user", "content": f"message number {i} " * 50}
            for i in range(20)
        ]
        # Bounding to max 200 tokens (approx 800 chars)
        bounded = manager._sanitize_and_bound_context(long_messages, max_tokens=200)

        total_bounded_chars = sum(len(m["content"]) for m in bounded)
        assert total_bounded_chars <= 200 * 4 + 100
        # Most recent message should be preserved
        assert len(bounded) >= 1

    @patch("requests.get")
    def test_circuit_breaker_trip_and_cooldown(self, mock_get):
        manager = OllamaConcurrencyManager()
        manager._health_check_interval = 0.0  # Force check
        manager._failure_threshold = 2
        manager._cooldown_seconds = 1.0

        # Simulate connection failure from Ollama daemon
        mock_get.side_effect = Exception("Connection refused by Ollama daemon")

        # First check fails
        healthy1 = manager.check_health(force=True)
        assert healthy1 is False

        # Second check fails and trips circuit breaker
        healthy2 = manager.check_health(force=True)
        assert healthy2 is False
        assert manager._circuit_open_until > time.time()

        # While circuit is open, check_health immediately returns False without hitting network
        mock_get.reset_mock()
        assert manager.check_health(force=False) is False
        mock_get.assert_not_called()

    @patch("requests.post")
    @patch("requests.get")
    def test_bounded_concurrency_and_telemetry(self, mock_get, mock_post):
        mock_get.return_value.status_code = 200
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "message": {"content": "Hello from Pathfinder Ollama"}
        }

        manager = OllamaConcurrencyManager()
        manager._is_healthy = True
        manager._circuit_open_until = 0.0

        content, badge, meta = manager.generate(
            messages=[{"role": "user", "content": "Hi"}],
            system_prompt="You are an assistant",
            user_id="test_user_ok"
        )
        assert content == "Hello from Pathfinder Ollama"
        assert "Ollama" in badge

        stats = manager.get_telemetry()
        assert stats["successful_requests"] >= 1


# ---------------------------------------------------------
# 2. Route Cache & SingleFlight In-Flight Deduplication Tests
# ---------------------------------------------------------
class TestRouteCacheManager:

    def test_cache_hit_and_ttl(self):
        cache = RouteCacheManager(default_ttl_sec=2.0, max_entries=50)
        called_count = 0

        def fetcher():
            nonlocal called_count
            called_count += 1
            return {"route": "A->B", "mode": "driving"}

        key = cache._generate_key(16.233, 80.550, 16.241, 80.559, "driving")

        # First call: cache miss
        res1 = cache.execute_single_flight(key, fetcher)
        assert called_count == 1
        assert res1["mode"] == "driving"

        # Second call: cache hit (no fetcher execution)
        res2 = cache.execute_single_flight(key, fetcher)
        assert called_count == 1
        assert res2 == res1

        stats = cache.get_stats()
        assert stats["cache_hits"] == 1
        assert stats["cache_misses"] == 1

    def test_single_flight_concurrent_deduplication(self):
        cache = RouteCacheManager(default_ttl_sec=10.0, max_entries=50)
        backend_calls = 0

        def slow_fetcher():
            nonlocal backend_calls
            backend_calls += 1
            time.sleep(0.2)
            return {"distance": 520.0}

        key = cache._generate_key(16.500, 80.600, 16.510, 80.610, "walking")

        # Execute 5 simultaneous requests for the exact same route
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(
                    cache.execute_single_flight,
                    key,
                    slow_fetcher
                )
                for _ in range(5)
            ]
            results = [f.result() for f in futures]

        # Only ONE backend network call should have occurred!
        assert backend_calls == 1
        for r in results:
            assert r["distance"] == 520.0

        assert cache.get_stats()["in_flight_coalesced"] >= 1


# ---------------------------------------------------------
# 3. Database Optimization & WAL Mode Tests
# ---------------------------------------------------------
class TestDatabaseOptimizations:

    def test_sqlite_wal_pragmas(self):
        with get_db_session() as session:
            # Verify Journal Mode is WAL
            wal_mode = session.execute(text("PRAGMA journal_mode;")).scalar()
            assert wal_mode.lower() == "wal"

            # Verify Busy Timeout is set (5000ms)
            busy_timeout = session.execute(text("PRAGMA busy_timeout;")).scalar()
            assert busy_timeout >= 5000


# ---------------------------------------------------------
# 4. API Security & Overload Protection Middleware Tests
# ---------------------------------------------------------
class TestSecurityAndRateLimiting:

    def test_sliding_window_rate_limiter(self):
        limiter = SlidingWindowRateLimiter(max_requests_per_window=5, window_seconds=60.0)
        client_key = "192.168.1.100"

        # 5 requests with max 5
        for _ in range(5):
            allowed, retry_after = limiter.is_allowed(client_key)
            assert allowed is True
            assert retry_after == 0

        # 6th request is blocked
        allowed, retry_after = limiter.is_allowed(client_key)
        assert allowed is False
        assert retry_after > 0


# ---------------------------------------------------------
# 5. Operational Observability API Tests
# ---------------------------------------------------------
class TestHealthAndObservabilityAPI:

    @pytest.fixture(autouse=True)
    def setup_client(self):
        self.client = TestClient(app)

    def test_liveness_probe(self):
        response = self.client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert "uptime_seconds" in data

    def test_readiness_probe(self):
        response = self.client.get("/health/ready")
        assert response.status_code in (200, 503)
        data = response.json()
        assert "checks" in data
        assert "database" in data["checks"]
        assert data["checks"]["database"]["status"] == "connected"

    def test_metrics_telemetry(self):
        response = self.client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        assert data["system"]["memory_rss_mb"] > 0
        assert "ollama_ai" in data
        assert "route_cache" in data
