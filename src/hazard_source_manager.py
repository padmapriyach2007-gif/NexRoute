"""
Real-Hazard Source Integration & Source Health Architecture for CampusAegis v2.0
Adheres to Section 5 & 6:
- Pluggable source adapter architecture (fetch, normalize, validate, health)
- Real, documented public feeds (USGS Earthquake, Open-Meteo Severe Weather)
- Source health tracking, freshness checking, and deduplication
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import math
import time
from typing import Any, Dict, List, Optional, Tuple
import requests

from src.hazard_data_model import (
    UnifiedIncident,
    HazardType,
    HazardSeverity,
    VerificationStatus,
    IncidentStatus,
    HazardGeometry,
    GeometryType,
    EnvironmentMode,
)


@dataclass
class SourceHealthMetrics:
    source_id: str
    source_name: str
    last_successful_sync: Optional[datetime] = None
    last_failed_sync: Optional[datetime] = None
    feed_latency_ms: float = 0.0
    consecutive_failures: int = 0
    total_incidents_retrieved: int = 0
    coverage_region: str = "Global / Regional"
    is_available: bool = True
    status_message: str = "Initialized"

    @property
    def is_stale(self, max_staleness_sec: float = 300.0) -> bool:
        if not self.last_successful_sync:
            return True
        age = (datetime.now(timezone.utc) - self.last_successful_sync).total_seconds()
        return age > max_staleness_sec

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "last_success": self.last_successful_sync.isoformat() if self.last_successful_sync else None,
            "last_failure": self.last_failed_sync.isoformat() if self.last_failed_sync else None,
            "latency_ms": round(self.feed_latency_ms, 2),
            "consecutive_failures": self.consecutive_failures,
            "total_incidents": self.total_incidents_retrieved,
            "coverage_region": self.coverage_region,
            "is_available": self.is_available,
            "is_stale": self.is_stale,
            "status_message": self.status_message
        }


class BaseHazardSourceAdapter(ABC):
    """Abstract base class for all external hazard feed integrations."""

    def __init__(self, source_id: str, source_name: str, coverage_region: str):
        self.source_id = source_id
        self.source_name = source_name
        self.coverage_region = coverage_region
        self.health = SourceHealthMetrics(
            source_id=source_id,
            source_name=source_name,
            coverage_region=coverage_region
        )
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "CampusAegis-Disaster-Ingest/2.0"})

    @abstractmethod
    def fetch_incidents(self, center_lat: float, center_lon: float, radius_km: float = 50.0) -> List[UnifiedIncident]:
        """Queries external endpoint and returns normalized incidents."""
        pass

    @abstractmethod
    def normalize_incident(self, raw_item: Dict[str, Any]) -> Optional[UnifiedIncident]:
        """Transforms provider-specific payload into a unified incident."""
        pass

    def validate_incident(self, incident: UnifiedIncident) -> bool:
        """Validates geographic boundaries, confidence, and timestamps."""
        valid, errors = incident.validate()
        return valid

    def get_source_health(self) -> SourceHealthMetrics:
        return self.health


class USGSEarthquakeAdapter(BaseHazardSourceAdapter):
    """
    Real Integration: USGS Geological Survey Earthquake GeoJSON Feed.
    Endpoint: https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson
    Publicly accessible, real government disaster monitoring, zero API credentials required.
    """

    def __init__(self):
        super().__init__(
            source_id="USGS_EARTHQUAKE_FEED",
            source_name="USGS National Earthquake Information Center",
            coverage_region="Global & Regional Seismic Monitor"
        )
        self.feed_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

    def fetch_incidents(self, center_lat: float, center_lon: float, radius_km: float = 500.0) -> List[UnifiedIncident]:
        t0 = time.perf_counter()
        incidents: List[UnifiedIncident] = []
        try:
            resp = self.session.get(self.feed_url, timeout=4.5)
            self.health.feed_latency_ms = (time.perf_counter() - t0) * 1000.0
            if resp.status_code == 200:
                data = resp.json()
                features = data.get("features", [])
                for f in features:
                    inc = self.normalize_incident(f)
                    if inc and self.validate_incident(inc):
                        incidents.append(inc)

                self.health.last_successful_sync = datetime.now(timezone.utc)
                self.health.consecutive_failures = 0
                self.health.total_incidents_retrieved += len(incidents)
                self.health.is_available = True
                self.health.status_message = f"Synchronized {len(incidents)} seismic events from USGS."
            else:
                self._record_failure(f"HTTP Status {resp.status_code}")
        except Exception as e:
            self.health.feed_latency_ms = (time.perf_counter() - t0) * 1000.0
            self._record_failure(str(e))

        return incidents

    def normalize_incident(self, raw_item: Dict[str, Any]) -> Optional[UnifiedIncident]:
        props = raw_item.get("properties", {})
        geom = raw_item.get("geometry", {})
        coords = geom.get("coordinates", [])
        if len(coords) < 2:
            return None

        lon, lat = coords[0], coords[1]
        mag = props.get("mag") or 0.0
        place = props.get("place", "Seismic Disturbance")
        eq_id = raw_item.get("id", f"USGS-{int(time.time())}")
        
        # Severity calculation based on Richter scale
        if mag >= 6.0:
            severity = HazardSeverity.CRITICAL
            rad_m = 15000.0
        elif mag >= 4.5:
            severity = HazardSeverity.HIGH
            rad_m = 8000.0
        elif mag >= 3.0:
            severity = HazardSeverity.MEDIUM
            rad_m = 4000.0
        else:
            severity = HazardSeverity.LOW
            rad_m = 1500.0

        ts_ms = props.get("time")
        obs_time = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc) if ts_ms else datetime.now(timezone.utc)

        return UnifiedIncident(
            incident_id=f"REAL-USGS-{eq_id}",
            external_source_id=eq_id,
            source_name=self.source_name,
            source_type="GOVERNMENT_SEISMIC",
            environment=EnvironmentMode.REAL,
            hazard_type=HazardType.EARTHQUAKE,
            geometry=HazardGeometry(
                geometry_type=GeometryType.POINT_BUFFER,
                latitude=lat,
                longitude=lon,
                radius_meters=rad_m
            ),
            affected_radius_meters=rad_m,
            severity=severity,
            confidence=0.98,
            verification_status=VerificationStatus.CONFIRMED,
            incident_status=IncidentStatus.ACTIVE,
            observed_at=obs_time,
            published_at=obs_time,
            expires_at=obs_time + timedelta(hours=24),
            source_url=props.get("url"),
            raw_payload=raw_item
        )

    def _record_failure(self, err_msg: str):
        self.health.last_failed_sync = datetime.now(timezone.utc)
        self.health.consecutive_failures += 1
        if self.health.consecutive_failures > 3:
            self.health.is_available = False
        self.health.status_message = f"Sync Error: {err_msg}"


class OpenMeteoSevereWeatherAdapter(BaseHazardSourceAdapter):
    """
    Real Integration: Open-Meteo Severe Meteorological & Precipitation API.
    Endpoint: https://api.open-meteo.com/v1/forecast
    100% public, real meteorological sensor grids, zero API key required.
    """

    def __init__(self):
        super().__init__(
            source_id="OPEN_METEO_SEVERE_WEATHER",
            source_name="Open-Meteo Global Severe Weather Model",
            coverage_region="Global Terrestrial Coordinates"
        )
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def fetch_incidents(self, center_lat: float, center_lon: float, radius_km: float = 30.0) -> List[UnifiedIncident]:
        t0 = time.perf_counter()
        incidents: List[UnifiedIncident] = []
        params = {
            "latitude": center_lat,
            "longitude": center_lon,
            "current": "weather_code,wind_speed_10m,precipitation",
            "timezone": "UTC"
        }
        try:
            resp = self.session.get(self.base_url, params=params, timeout=4.0)
            self.health.feed_latency_ms = (time.perf_counter() - t0) * 1000.0
            if resp.status_code == 200:
                data = resp.json()
                curr = data.get("current", {})
                w_code = curr.get("weather_code", 0)
                wind = curr.get("wind_speed_10m", 0.0)
                precip = curr.get("precipitation", 0.0)

                # WMO Codes: 95, 96, 99 = Thunderstorm; 65, 75, 82 = Violent Rain/Flooding
                if w_code in (95, 96, 99) or wind > 55.0 or precip > 15.0:
                    inc = UnifiedIncident(
                        incident_id=f"REAL-METEO-{int(time.time())}",
                        external_source_id=f"METEO-W{w_code}-{int(center_lat*100)}_{int(center_lon*100)}",
                        source_name=self.source_name,
                        source_type="METEOROLOGICAL_SENSOR",
                        environment=EnvironmentMode.REAL,
                        hazard_type=HazardType.SEVERE_WEATHER if w_code in (95, 96, 99) else HazardType.FLOODED_ROAD,
                        geometry=HazardGeometry(
                            geometry_type=GeometryType.POINT_BUFFER,
                            latitude=center_lat,
                            longitude=center_lon,
                            radius_meters=3500.0
                        ),
                        affected_radius_meters=3500.0,
                        severity=HazardSeverity.HIGH if wind > 65.0 else HazardSeverity.MEDIUM,
                        confidence=0.92,
                        verification_status=VerificationStatus.CONFIRMED,
                        incident_status=IncidentStatus.ACTIVE,
                        observed_at=datetime.now(timezone.utc),
                        published_at=datetime.now(timezone.utc),
                        expires_at=datetime.now(timezone.utc) + timedelta(hours=4),
                        source_url="https://open-meteo.com",
                        raw_payload=curr
                    )
                    incidents.append(inc)

                self.health.last_successful_sync = datetime.now(timezone.utc)
                self.health.consecutive_failures = 0
                self.health.total_incidents_retrieved += len(incidents)
                self.health.is_available = True
                self.health.status_message = "Weather telemetry active."
            else:
                self._record_failure(f"HTTP {resp.status_code}")
        except Exception as e:
            self.health.feed_latency_ms = (time.perf_counter() - t0) * 1000.0
            self._record_failure(str(e))

        return incidents

    def normalize_incident(self, raw_item: Dict[str, Any]) -> Optional[UnifiedIncident]:
        return None  # Normalized directly in fetch_incidents

    def _record_failure(self, err_msg: str):
        self.health.last_failed_sync = datetime.now(timezone.utc)
        self.health.consecutive_failures += 1
        if self.health.consecutive_failures > 3:
            self.health.is_available = False
        self.health.status_message = f"Weather Sync Error: {err_msg}"


class RealHazardSourceManager:
    """
    Coordinates external source adapters, deduplicates incoming incidents,
    enforces rate-limits, and tracks health and data staleness across all feeds.
    """

    def __init__(self):
        self.adapters: Dict[str, BaseHazardSourceAdapter] = {
            "USGS": USGSEarthquakeAdapter(),
            "OPEN_METEO": OpenMeteoSevereWeatherAdapter()
        }
        self._cached_incidents: Dict[str, UnifiedIncident] = {}
        self._last_poll_time: Optional[datetime] = None
        self._min_poll_interval_sec: float = 30.0

    def poll_all_sources(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float = 50.0,
        force: bool = False
    ) -> List[UnifiedIncident]:
        """Polls all registered sources if interval expired or forced."""
        now = datetime.now(timezone.utc)
        if not force and self._last_poll_time:
            elapsed = (now - self._last_poll_time).total_seconds()
            if elapsed < self._min_poll_interval_sec:
                # Return active cached incidents
                return [inc for inc in self._cached_incidents.values() if inc.is_active]

        self._last_poll_time = now
        new_incidents: List[UnifiedIncident] = []

        for name, adapter in self.adapters.items():
            try:
                fetched = adapter.fetch_incidents(center_lat, center_lon, radius_km)
                for inc in fetched:
                    # Deduplication key based on source and coordinates
                    dedup_key = f"{inc.source_type}:{round(inc.geometry.latitude, 3)}_{round(inc.geometry.longitude, 3)}"
                    self._cached_incidents[dedup_key] = inc
                    new_incidents.append(inc)
            except Exception as e:
                adapter.health.status_message = f"Execution exception: {e}"

        return list(self._cached_incidents.values())

    def get_source_health_summary(self) -> List[Dict[str, Any]]:
        return [adapter.get_source_health().to_dict() for adapter in self.adapters.values()]
