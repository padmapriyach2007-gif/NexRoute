"""
Hazard Mode Manager & Operating Mode Controller for CampusAegis v2.0
Adheres to Section 3:
- Manages REAL_HAZARD_MODE, SIMULATION_MODE, and HYBRID_MODE
- Enforces strict environment boundaries to prevent test alerts from leaking into production
- Bridges UnifiedIncident objects into the routing engine's HazardMap
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

from src.hazard_data_model import (
    UnifiedIncident,
    OperatingMode,
    EnvironmentMode,
    HazardSeverity,
    VerificationStatus,
    IncidentStatus
)
from src.hazard_source_manager import RealHazardSourceManager
from src.simulation_engine import SimulationEngine
from src.hazard_map import GeographicHazard, HazardSeverity as LegacySeverity, HazardMap


class HazardModeManager:
    """
    Central coordinator enforcing operating modes (REAL, SIMULATION, HYBRID)
    and strictly partitioning simulated data away from production life-safety channels.
    """

    def __init__(self, initial_mode: OperatingMode = OperatingMode.HYBRID_MODE):
        self.operating_mode: OperatingMode = initial_mode
        self.real_source_manager = RealHazardSourceManager()
        self.simulation_engine = SimulationEngine()
        self.active_incidents: Dict[str, UnifiedIncident] = {}

    def set_mode(self, mode: OperatingMode):
        self.operating_mode = mode
        self.synchronize_incidents(16.2335, 80.5505)

    def synchronize_incidents(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float = 40.0,
        force_refresh: bool = False
    ) -> List[UnifiedIncident]:
        """
        Polls or synthesizes incidents strictly according to the active operating mode.
        """
        self.active_incidents.clear()

        # 1. Ingest Real Feeds if REAL or HYBRID
        if self.operating_mode in (OperatingMode.REAL_HAZARD_MODE, OperatingMode.HYBRID_MODE):
            real_data = self.real_source_manager.poll_all_sources(
                center_lat=center_lat,
                center_lon=center_lon,
                radius_km=radius_km,
                force=force_refresh
            )
            for inc in real_data:
                # Ensure it is marked REAL
                if inc.environment == EnvironmentMode.REAL and inc.is_active:
                    self.active_incidents[inc.incident_id] = inc

        # 2. Ingest Simulated Feeds if SIMULATION or HYBRID
        if self.operating_mode in (OperatingMode.SIMULATION_MODE, OperatingMode.HYBRID_MODE):
            sim_data = self.simulation_engine.get_active_simulated_incidents()
            for inc in sim_data:
                if inc.is_active:
                    self.active_incidents[inc.incident_id] = inc

        # 3. Mode Invariant Check:
        # In REAL_HAZARD_MODE, reject any incident marked SIMULATED
        if self.operating_mode == OperatingMode.REAL_HAZARD_MODE:
            self.active_incidents = {
                k: v for k, v in self.active_incidents.items()
                if not v.is_simulated
            }

        return list(self.active_incidents.values())

    def update_hazard_map(self, target_hazard_map: HazardMap):
        """
        Populates a HazardMap instance with currently synchronized incidents,
        converting them to GeographicHazard objects with appropriate spatial buffers.
        """
        if hasattr(target_hazard_map, "clear_all_hazards"):
            target_hazard_map.clear_all_hazards()
        else:
            if hasattr(target_hazard_map, "_hazards"):
                target_hazard_map._hazards.clear()
            if hasattr(target_hazard_map, "_road_closures"):
                target_hazard_map._road_closures.clear()
        for inc in self.active_incidents.values():
            if not inc.is_active:
                continue

            # Map unified severity to legacy severity
            if inc.severity == HazardSeverity.CRITICAL:
                leg_sev = LegacySeverity.CRITICAL
            elif inc.severity == HazardSeverity.HIGH:
                leg_sev = LegacySeverity.HIGH
            elif inc.severity == HazardSeverity.MEDIUM:
                leg_sev = LegacySeverity.MEDIUM
            else:
                leg_sev = LegacySeverity.LOW

            # Convert to GeographicHazard
            gh = GeographicHazard(
                hazard_id=inc.incident_id,
                incident_type=f"{'[SIMULATED] ' if inc.is_simulated else ''}{inc.hazard_type.value}",
                severity=leg_sev,
                latitude=inc.geometry.latitude,
                longitude=inc.geometry.longitude,
                radius_meters=inc.affected_radius_meters,
                description=f"{inc.source_name}: {inc.hazard_type.value} ({inc.verification_status.value})",
                is_confirmed=(inc.verification_status == VerificationStatus.CONFIRMED),
                affected_road_name=inc.affected_road_segments[0] if inc.affected_road_segments else None,
                source=f"{inc.source_type} ({inc.environment.value})"
            )
            target_hazard_map.add_hazard(gh)

    def get_environment_indicator(self) -> Dict[str, Any]:
        """Provides prominent environment status for dashboard and operator alerts."""
        if self.operating_mode == OperatingMode.REAL_HAZARD_MODE:
            return {
                "mode": self.operating_mode.value,
                "label": "🟢 REAL HAZARD PRODUCTION MODE",
                "color": "#10b981",
                "description": "Consuming live verified external government and meteorological feeds. Zero simulated hazards permitted.",
                "allows_simulation": False
            }
        elif self.operating_mode == OperatingMode.SIMULATION_MODE:
            return {
                "mode": self.operating_mode.value,
                "label": "🟣 CONTROLLED SIMULATION MODE (TESTING)",
                "color": "#a855f7",
                "description": "Developer sandbox active. All hazards marked [SIMULATED]. Public notifications disabled.",
                "allows_simulation": True
            }
        else:
            return {
                "mode": self.operating_mode.value,
                "label": "🟡 HYBRID DEVELOPMENT & DRILL MODE",
                "color": "#f59e0b",
                "description": "Operating real feeds alongside controlled simulation scenarios. Provenance strictly tracked.",
                "allows_simulation": True
            }
