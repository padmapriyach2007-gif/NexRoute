"""
Health and Operational Observability Endpoints
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Scalability & Reliability Engine

Provides:
- GET /health/live: Kubernetes/Docker Liveness probe
- GET /health/ready: Readiness check validating Database, Ollama, and Route Engine
- GET /metrics: Operational telemetry exposing resource consumption, cache efficiency, Ollama queue depth, and DB status
"""

import os
import time
import psutil
from fastapi import APIRouter, Response, status
from sqlalchemy import text

from src.backend.database.connection import get_db_session
from src.backend.ai.ollama_limiter import get_ollama_manager
from src.backend.routing.route_cache import get_route_cache_manager

health_router = APIRouter(tags=["Health & Monitoring"])

_START_TIME = time.time()


@health_router.get("/health/live", summary="Liveness Probe")
def liveness_probe():
    """
    Lightweight probe confirming the HTTP server is alive and accepting events.
    """
    return {
        "status": "alive",
        "timestamp": time.time(),
        "uptime_seconds": round(time.time() - _START_TIME, 2)
    }


@health_router.get("/health/ready", summary="Readiness Probe")
def readiness_probe(response: Response):
    """
    Readiness probe validating dependencies (Database, Caching, Concurrency Managers).
    Returns 503 if critical dependencies are unreachable.
    """
    checks = {}
    is_ready = True

    # 1. Database Check
    db_start = time.perf_counter()
    try:
        with get_db_session() as session:
            session.execute(text("SELECT 1;"))
            db_duration_ms = round((time.perf_counter() - db_start) * 1000, 2)
            checks["database"] = {
                "status": "connected",
                "latency_ms": db_duration_ms
            }
    except Exception as e:
        checks["database"] = {
            "status": "failed",
            "error": str(e)
        }
        is_ready = False

    # 2. Ollama Limiter Check
    ollama_mgr = get_ollama_manager()
    ollama_stats = ollama_mgr.get_stats()
    checks["ollama"] = {
        "circuit_breaker": ollama_stats["circuit_breaker_state"],
        "active_generations": ollama_stats["active_generations"],
        "queued_requests": ollama_stats["queue_depth"]
    }

    # 3. Route Cache Manager Check
    cache_mgr = get_route_cache_manager()
    cache_stats = cache_mgr.get_stats()
    checks["route_cache"] = {
        "status": "active",
        "entries": cache_stats["cache_entries"],
        "in_flight_locks": cache_stats["in_flight_requests"]
    }

    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if is_ready else "degraded",
        "checks": checks,
        "timestamp": time.time(),
        "uptime_seconds": round(time.time() - _START_TIME, 2)
    }


@health_router.get("/metrics", summary="Operational Metrics & Telemetry")
def metrics_endpoint():
    """
    Comprehensive operational metrics including memory, CPU, cache hit rates,
    and Ollama throughput for real-time monitoring and alert hooks.
    """
    proc = psutil.Process()
    mem_info = proc.memory_info()

    ollama_mgr = get_ollama_manager()
    ollama_stats = ollama_mgr.get_stats()

    cache_mgr = get_route_cache_manager()
    cache_stats = cache_mgr.get_stats()

    return {
        "system": {
            "pid": proc.pid,
            "cpu_percent": proc.cpu_percent(interval=None),
            "memory_rss_bytes": mem_info.rss,
            "memory_rss_mb": round(mem_info.rss / (1024 * 1024), 2),
            "threads_count": proc.num_threads(),
            "uptime_seconds": round(time.time() - _START_TIME, 2)
        },
        "ollama_ai": ollama_stats,
        "route_cache": cache_stats,
        "timestamp": time.time()
    }
