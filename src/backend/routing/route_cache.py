"""
Pathfinder High-Performance Route Cache & In-Flight Request Deduplicator
Implements the SingleFlight pattern and thread-safe LRU/TTL caching to protect
external routing providers (Google Maps, OSRM, Nominatim) from quota exhaustion,
duplicate network calls, and latency spikes under high concurrent user load.
"""

import time
import hashlib
import threading
from typing import Dict, Any, Optional, Callable, Tuple
from collections import OrderedDict


class RouteCacheManager:
    """Thread-safe LRU + TTL cache with SingleFlight in-flight deduplication."""

    _instance: Optional["RouteCacheManager"] = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "RouteCacheManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self, max_entries: int = 1000, default_ttl_sec: float = 600.0):
        self.max_entries = max_entries
        self.default_ttl_sec = default_ttl_sec

        # Cache storage: cache_key -> (data, expires_at)
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._cache_lock = threading.Lock()

        # In-Flight SingleFlight state: flight_key -> Condition variable + result container
        self._in_flight: Dict[str, Dict[str, Any]] = {}
        self._flight_lock = threading.Lock()

        # Metrics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "deduplicated_flights": 0,
            "evictions": 0
        }

    def _generate_key(
        self,
        orig_lat: float,
        orig_lon: float,
        dest_lat: float,
        dest_lon: float,
        mode: str,
        avoidances: str = ""
    ) -> str:
        """
        Generates a privacy-preserving spatial hash by rounding coords to 3 decimals (~100m).
        Ensures local privacy while allowing efficient corridor-level caching.
        """
        raw = f"{orig_lat:.3f}:{orig_lon:.3f}->{dest_lat:.3f}:{dest_lon:.3f}|{mode.lower()}|{avoidances}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    def get(self, key: str) -> Optional[Any]:
        """Retrieves cached item if present and unexpired."""
        now = time.time()
        with self._cache_lock:
            if key in self._cache:
                data, expires_at = self._cache[key]
                if now < expires_at:
                    self._cache.move_to_end(key)
                    self.stats["hits"] += 1
                    return data
                else:
                    # Expired
                    del self._cache[key]
            self.stats["misses"] += 1
            return None

    def set(self, key: str, value: Any, ttl_sec: Optional[float] = None):
        """Stores item in cache with LRU eviction."""
        ttl = ttl_sec or self.default_ttl_sec
        expires_at = time.time() + ttl
        with self._cache_lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = (value, expires_at)

            # Evict oldest if exceeding capacity
            if len(self._cache) > self.max_entries:
                self._cache.popitem(last=False)
                self.stats["evictions"] += 1

    def execute_single_flight(
        self,
        key: str,
        worker_fn: Callable[[], Any],
        ttl_sec: Optional[float] = None
    ) -> Any:
        """
        SingleFlight pattern:
        If multiple concurrent threads request the exact same route calculation simultaneously,
        only ONE worker executes the external API call. All other threads wait and share the result.
        """
        # 1. Check existing cache
        cached = self.get(key)
        if cached is not None:
            return cached

        # 2. Check or register in-flight call
        leader = False
        flight = None

        with self._flight_lock:
            if key in self._in_flight:
                # Follower thread: wait for leader
                flight = self._in_flight[key]
                self.stats["deduplicated_flights"] += 1
            else:
                # Leader thread: will execute worker_fn
                leader = True
                cond = threading.Condition(self._flight_lock)
                flight = {
                    "cond": cond,
                    "done": False,
                    "result": None,
                    "error": None
                }
                self._in_flight[key] = flight

        if not leader:
            # Wait for leader to finish
            cond = flight["cond"]
            with cond:
                while not flight["done"]:
                    cond.wait(timeout=10.0)

            if flight["error"]:
                raise flight["error"]
            return flight["result"]

        # 3. Leader execution
        res = None
        err = None
        try:
            res = worker_fn()
            # Cache the successful result
            if res is not None:
                self.set(key, res, ttl_sec)
        except Exception as e:
            err = e
        finally:
            # Notify all waiting follower threads
            with self._flight_lock:
                flight["done"] = True
                flight["result"] = res
                flight["error"] = err
                cond = flight["cond"]
                del self._in_flight[key]

            with cond:
                cond.notify_all()

        if err is not None:
            raise err
        return res

    def get_telemetry(self) -> Dict[str, Any]:
        """Telemetry metrics for cache observability."""
        total = self.stats["hits"] + self.stats["misses"]
        hit_ratio = round((self.stats["hits"] / max(1, total)) * 100, 1)
        return {
            "cached_entries": len(self._cache),
            "cache_entries": len(self._cache),
            "max_entries": self.max_entries,
            "hits": self.stats["hits"],
            "cache_hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "cache_misses": self.stats["misses"],
            "hit_ratio_pct": hit_ratio,
            "deduplicated_flights": self.stats["deduplicated_flights"],
            "in_flight_coalesced": self.stats["deduplicated_flights"],
            "in_flight_requests": len(self._in_flight),
            "evictions": self.stats["evictions"]
        }

    def get_stats(self) -> Dict[str, Any]:
        """Alias for get_telemetry() for operational parity."""
        return self.get_telemetry()


def get_route_cache_manager() -> RouteCacheManager:
    """Convenience accessor for the global singleton RouteCacheManager."""
    return RouteCacheManager.get_instance()
