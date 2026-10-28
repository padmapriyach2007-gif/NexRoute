"""
Pathfinder Concurrency-Safe Ollama Limiter & Bounded Queue Engine
Treats local Ollama as a capacity-limited resource to prevent GPU/CPU RAM exhaustion,
thread starvation, and application crashes under multi-user concurrency.

Features:
- Configurable maximum concurrent generations (default: 1 or 2)
- Bounded request queue with fast backpressure rejection
- Per-user / per-session sliding window rate limiting
- Automatic context window truncation & output token bounding
- Dynamic health checking & automatic recovery cooldown (no permanent blacklisting)
- Real-time observability metrics (active, queued, rejected, avg latency)
"""

import os
import time
import json
import uuid
import logging
import threading
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
import requests

logger = logging.getLogger("pathfinder.ollama_limiter")


class OllamaConcurrencyManager:
    """Singleton manager controlling multi-user access to the local Ollama instance."""

    _instance: Optional["OllamaConcurrencyManager"] = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "OllamaConcurrencyManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self):
        # Configuration from environment with robust defaults
        self.max_concurrent = int(os.getenv("OLLAMA_MAX_CONCURRENT", "2"))
        self.max_queue_size = int(os.getenv("OLLAMA_MAX_QUEUE_SIZE", "8"))
        self.request_timeout = float(os.getenv("OLLAMA_TIMEOUT_SEC", "14.0"))
        self.per_user_rate_limit_per_min = int(os.getenv("OLLAMA_PER_USER_RPM", "8"))
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = os.getenv("OLLAMA_MODEL", "llama3.2")

        # Concurrency primitives
        self._semaphore = threading.BoundedSemaphore(self.max_concurrent)
        self._queue_lock = threading.Lock()
        self._queued_count = 0

        # Rate limiting state: user_id -> deque of timestamps
        self._user_requests: Dict[str, deque] = {}
        self._user_lock = threading.Lock()

        # Circuit breaker & health state
        self._is_healthy = True
        self._last_health_check = 0.0
        self._health_check_interval = 25.0
        self._consecutive_failures = 0
        self._failure_threshold = 3
        self._circuit_open_until = 0.0
        self._cooldown_seconds = 20.0

        # Telemetry metrics
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "rejected_queue_full": 0,
            "rejected_rate_limited": 0,
            "timed_out": 0,
            "circuit_breaker_rejections": 0,
            "total_latency_ms": 0.0,
            "active_generations": 0,
            "current_queue_depth": 0
        }

    # =========================================================================
    # HEALTH & CIRCUIT BREAKER
    # =========================================================================
    def check_health(self, force: bool = False) -> bool:
        """Polls Ollama /api/tags to verify daemon responsiveness without locking."""
        now = time.time()
        if not force and (now - self._last_health_check < self._health_check_interval):
            return self._is_healthy

        # Check circuit breaker cooldown
        if now < self._circuit_open_until:
            return False

        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=1.2)
            self._is_healthy = (resp.status_code == 200)
            if self._is_healthy:
                self._consecutive_failures = 0
                self._circuit_open_until = 0.0
            self._last_health_check = now
            return self._is_healthy
        except Exception:
            self._is_healthy = False
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._failure_threshold:
                self._circuit_open_until = now + self._cooldown_seconds
                logger.warning(f"Ollama circuit tripped. Cooling down for {self._cooldown_seconds}s.")
            self._last_health_check = now
            return False

    # =========================================================================
    # RATE LIMITING PER USER / SESSION
    # =========================================================================
    def check_user_rate_limit(self, user_id: str) -> bool:
        """Enforces sliding-window rate limit per user."""
        now = time.time()
        one_min_ago = now - 60.0

        with self._user_lock:
            if user_id not in self._user_requests:
                self._user_requests[user_id] = deque()

            user_queue = self._user_requests[user_id]
            while user_queue and user_queue[0] < one_min_ago:
                user_queue.popleft()

            if len(user_queue) >= self.per_user_rate_limit_per_min:
                return False

            user_queue.append(now)
            return True

    # =========================================================================
    # CONCURRENCY-CONTROLLED INFERENCE DISPATCH
    # =========================================================================
    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        user_id: str = "anonymous",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 800
    ) -> Tuple[Optional[str], str, Dict[str, Any]]:
        """
        Executes bounded, concurrency-safe Ollama generation.
        Returns: (response_text_or_None, status_badge, telemetry_info)
        """
        self.stats["total_requests"] += 1
        req_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        chosen_model = model or self.default_model

        # 1. Check Circuit Breaker
        if not self.check_health():
            self.stats["circuit_breaker_rejections"] += 1
            return (
                None,
                "OLLAMA_OVERLOADED_OR_OFFLINE",
                {"error": "Local Ollama daemon is currently recovering. Using high-speed cognitive engine fallback.", "retry_after": 5}
            )

        # 2. Check Per-User Rate Limit
        if not self.check_user_rate_limit(user_id):
            self.stats["rejected_rate_limited"] += 1
            return (
                None,
                "USER_RATE_LIMITED",
                {"error": f"Rate limit reached ({self.per_user_rate_limit_per_min} req/min). Please wait a moment before sending more messages.", "retry_after": 10}
            )

        # 3. Check Bounded Queue Capacity
        with self._queue_lock:
            if self._queued_count >= self.max_queue_size:
                self.stats["rejected_queue_full"] += 1
                return (
                    None,
                    "QUEUE_FULL",
                    {"error": "AI Copilot is processing peak traffic. Request gracefully throttled.", "retry_after": 3}
                )
            self._queued_count += 1
            self.stats["current_queue_depth"] = self._queued_count

        # 4. Wait for Semaphore Slot (Bounded Concurrency)
        acquired = False
        try:
            # Wait up to 5 seconds to acquire a concurrency generation slot
            acquired = self._semaphore.acquire(timeout=5.0)
            if not acquired:
                self.stats["rejected_queue_full"] += 1
                return (
                    None,
                    "CONCURRENCY_TIMEOUT",
                    {"error": "AI processing queue deadline exceeded. Seamlessly falling back to cognitive engine.", "retry_after": 2}
                )

            with self._queue_lock:
                self._queued_count = max(0, self._queued_count - 1)
                self.stats["current_queue_depth"] = self._queued_count
                self.stats["active_generations"] += 1

            # 5. Sanitize & Bound Input Context
            bounded_messages = self._sanitize_and_bound_context(messages, max_tokens=1500)
            chat_payload = [{"role": "system", "content": system_prompt}] + bounded_messages

            # 6. Execute Actual Ollama Request
            call_start = time.time()
            post_payload = {
                "model": chosen_model,
                "messages": chat_payload,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": min(max_tokens, 800)
                }
            }

            resp = requests.post(
                f"{self.base_url}/api/chat",
                json=post_payload,
                timeout=self.request_timeout
            )

            latency_ms = round((time.time() - call_start) * 1000, 1)

            if resp.status_code == 200:
                data = resp.json()
                content = data.get("message", {}).get("content", "")
                if content:
                    self.stats["successful_requests"] += 1
                    self.stats["total_latency_ms"] += latency_ms
                    self._consecutive_failures = 0
                    return (
                        content,
                        f"Ollama ({chosen_model})",
                        {"latency_ms": latency_ms, "model": chosen_model, "request_id": req_id}
                    )

            # Non-200 error from Ollama
            self._consecutive_failures += 1
            return (
                None,
                "OLLAMA_HTTP_ERROR",
                {"error": f"Ollama HTTP {resp.status_code}: {resp.text[:120]}", "retry_after": 5}
            )

        except requests.exceptions.Timeout:
            self.stats["timed_out"] += 1
            self._consecutive_failures += 1
            return (
                None,
                "OLLAMA_TIMEOUT",
                {"error": f"Ollama request exceeded safety timeout ({self.request_timeout}s).", "retry_after": 5}
            )
        except Exception as e:
            self._consecutive_failures += 1
            return (
                None,
                "OLLAMA_EXCEPTION",
                {"error": str(e), "retry_after": 5}
            )
        finally:
            if acquired:
                with self._queue_lock:
                    self.stats["active_generations"] = max(0, self.stats["active_generations"] - 1)
                self._semaphore.release()

    def _sanitize_and_bound_context(self, messages: List[Dict[str, str]], max_tokens: int = 1500) -> List[Dict[str, str]]:
        """Keeps recent messages within a safe token budget (approx 4 chars per token)."""
        char_budget = max_tokens * 4
        total_chars = 0
        bounded = []

        # Iterate backwards to preserve the most recent turns
        for msg in reversed(messages):
            content = msg.get("content", "")
            if total_chars + len(content) > char_budget:
                remaining = char_budget - total_chars
                if remaining > 100:
                    bounded.insert(0, {"role": msg["role"], "content": content[-remaining:]})
                break
            bounded.insert(0, msg)
            total_chars += len(content)

        return bounded

    def get_telemetry(self) -> Dict[str, Any]:
        """Returns live monitoring stats for load & queue observability."""
        total = max(1, self.stats["total_requests"])
        success = self.stats["successful_requests"]
        avg_latency = (
            round(self.stats["total_latency_ms"] / max(1, success), 1)
            if success > 0 else 0.0
        )
        return {
            "is_healthy": self._is_healthy,
            "circuit_breaker_state": "OPEN" if not self._is_healthy and time.time() < self._circuit_open_until else "CLOSED",
            "max_concurrent": self.max_concurrent,
            "active_generations": self.stats["active_generations"],
            "current_queue_depth": self.stats["current_queue_depth"],
            "queue_depth": self.stats["current_queue_depth"],
            "max_queue_size": self.max_queue_size,
            "total_requests": self.stats["total_requests"],
            "successful_requests": success,
            "success_rate_pct": round((success / total) * 100, 1),
            "rejected_queue_full": self.stats["rejected_queue_full"],
            "rejected_rate_limited": self.stats["rejected_rate_limited"],
            "timed_out": self.stats["timed_out"],
            "avg_latency_ms": avg_latency
        }

    def get_stats(self) -> Dict[str, Any]:
        """Alias for get_telemetry() for operational parity."""
        return self.get_telemetry()


class OllamaLimiterException(Exception):
    """Exception raised when an Ollama concurrency or queue limit is exceeded."""
    pass


def get_ollama_manager() -> OllamaConcurrencyManager:
    """Convenience accessor for the global singleton OllamaConcurrencyManager."""
    return OllamaConcurrencyManager.get_instance()
