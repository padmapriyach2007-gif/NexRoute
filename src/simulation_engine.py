"""
Controlled Hazard Simulator & Repeatable Scenario Engine for CampusAegis v2.0
Adheres to Sections 3.B, 3.C, and 14:
- Generates all required fictional emergency types with unmistakable SIMULATED designation
- Implements 18 repeatable test scenarios with deterministic outcomes
- Enforces strict isolation: simulated hazards never leak into production alert channels
"""

from datetime import datetime, timezone, timedelta
import math
import uuid
from typing import Any, Dict, List, Optional, Tuple

from src.hazard_data_model import (
    UnifiedIncident,
    HazardType,
    HazardSeverity,
    VerificationStatus,
    IncidentStatus,
    HazardGeometry,
    GeometryType,
    EnvironmentMode,
    OperatingMode
)


class SimulationEngine:
    """
    Controlled sandbox hazard simulator for developers and authorized testers.
    Maintains clean state, deterministic repeatable scenarios, and strict environment tagging.
    """

    def __init__(self):
        self.simulated_incidents: Dict[str, UnifiedIncident] = {}
        self.active_scenario_name: Optional[str] = None
        self._scenario_history: List[str] = []

    def reset(self):
        """Resets the simulation to a clean, zero-hazard state."""
        self.simulated_incidents.clear()
        self.active_scenario_name = "CLEAN_BASELINE"
        self._scenario_history.append("RESET_CLEAN_STATE")

    def generate_incident(
        self,
        hazard_type: HazardType,
        latitude: float,
        longitude: float,
        radius_meters: float = 250.0,
        severity: HazardSeverity = HazardSeverity.HIGH,
        confidence: float = 1.0,
        verification_status: VerificationStatus = VerificationStatus.CONFIRMED,
        affected_road_name: Optional[str] = None,
        description: Optional[str] = None,
        duration_minutes: float = 120.0
    ) -> UnifiedIncident:
        """
        Creates a synthetic emergency event with mandatory SIMULATED provenance.
        """
        now = datetime.now(timezone.utc)
        sim_id = f"SIMULATED-{hazard_type.value}-{uuid.uuid4().hex[:6].upper()}"
        desc = description or f"Simulated {hazard_type.value.replace('_', ' ').title()}"

        incident = UnifiedIncident(
            incident_id=sim_id,
            external_source_id=f"TESTER-SIM-{uuid.uuid4().hex[:4]}",
            source_name="Authorized Emergency Simulator",
            source_type="SIMULATOR_ENGINE",
            environment=EnvironmentMode.SIMULATED,
            hazard_type=hazard_type,
            geometry=HazardGeometry(
                geometry_type=GeometryType.POINT_BUFFER,
                latitude=latitude,
                longitude=longitude,
                radius_meters=radius_meters
            ),
            affected_radius_meters=radius_meters,
            severity=severity,
            confidence=confidence,
            verification_status=verification_status,
            incident_status=IncidentStatus.ACTIVE,
            observed_at=now,
            published_at=now,
            expires_at=now + timedelta(minutes=duration_minutes),
            affected_road_segments=[affected_road_name] if affected_road_name else [],
            source_url="https://campusaegis.internal/simulator",
            resolution_reason=None
        )

        self.simulated_incidents[sim_id] = incident
        return incident

    def resolve_incident(self, incident_id: str, reason: str = "Incident Controlled & Cleared") -> bool:
        if incident_id in self.simulated_incidents:
            inc = self.simulated_incidents[incident_id]
            inc.incident_status = IncidentStatus.RESOLVED
            inc.verification_status = VerificationStatus.RESOLVED
            inc.resolution_reason = reason
            inc.last_updated_at = datetime.now(timezone.utc)
            return True
        return False

    def remove_incident(self, incident_id: str) -> bool:
        if incident_id in self.simulated_incidents:
            del self.simulated_incidents[incident_id]
            return True
        return False

    def load_scenario(self, scenario_number: int) -> Dict[str, Any]:
        """
        Loads one of the 18 deterministic benchmark scenarios defined in Section 14.
        """
        self.reset()
        ref_lat, ref_lon = 16.2335, 80.5505  # Vignan University reference corridor
        scenario_meta = {"scenario_id": scenario_number, "name": "", "incidents_created": 0}

        if scenario_number == 1:
            scenario_meta["name"] = "No Hazards (Nominal Transit Baseline)"
            self.active_scenario_name = scenario_meta["name"]

        elif scenario_number == 2:
            scenario_meta["name"] = "Fire on Selected Arterial Route"
            self.generate_incident(
                hazard_type=HazardType.BUILDING_FIRE,
                latitude=16.2798, longitude=80.4568,
                radius_meters=850.0,
                severity=HazardSeverity.CRITICAL,
                affected_road_name="Tenali - Guntur Highway",
                description="Structural Fire & Heavy Smoke Plume Crossing Highway"
            )
            scenario_meta["incidents_created"] = 1

        elif scenario_number == 3:
            scenario_meta["name"] = "Road Collapse on Selected Route"
            self.generate_incident(
                hazard_type=HazardType.ROAD_CAVE_IN,
                latitude=16.2950, longitude=80.4420,
                radius_meters=300.0,
                severity=HazardSeverity.HIGH,
                affected_road_name="Guntur Ringroad",
                description="Underground Main Rupture Causing Roadway Collapse"
            )
            scenario_meta["incidents_created"] = 1

        elif scenario_number == 4:
            scenario_meta["name"] = "Multiple Simultaneous Hazards"
            self.generate_incident(HazardType.BUILDING_FIRE, 16.3075, 80.4280, radius_meters=280.0, affected_road_name="Pattabhipuram Road")
            self.generate_incident(HazardType.FLOODED_ROAD, 16.2650, 80.4980, radius_meters=320.0, affected_road_name="Narakodur Cross")
            self.generate_incident(HazardType.CHEMICAL_LEAK, 16.2410, 80.5350, radius_meters=400.0, affected_road_name="Vadlamudi Access")
            scenario_meta["incidents_created"] = 3

        elif scenario_number == 5:
            scenario_meta["name"] = "Hazard Appearing While In-Transit (Dynamic Reroute Trigger)"
            self.generate_incident(
                hazard_type=HazardType.VEHICLE_ACCIDENT,
                latitude=16.2800, longitude=80.4700,
                radius_meters=220.0,
                severity=HazardSeverity.HIGH,
                affected_road_name="Mid-Transit Connector",
                description="Tanker Jackknife Blocking Both Directions"
            )
            scenario_meta["incidents_created"] = 1

        elif scenario_number == 6:
            scenario_meta["name"] = "All Routes Blocked to Destination (Cut-Off Trigger)"
            # Surround destination (Guntur City Center: 16.3067, 80.4365) from all access approaches
            self.generate_incident(HazardType.ROAD_CLOSURE, 16.3040, 80.4350, radius_meters=600.0, affected_road_name="South Approach")
            self.generate_incident(HazardType.ROAD_CLOSURE, 16.3090, 80.4370, radius_meters=600.0, affected_road_name="North Approach")
            self.generate_incident(HazardType.ROAD_CLOSURE, 16.3060, 80.4410, radius_meters=600.0, affected_road_name="East Approach")
            self.generate_incident(HazardType.ROAD_CLOSURE, 16.3070, 80.4310, radius_meters=600.0, affected_road_name="West Approach")
            scenario_meta["incidents_created"] = 4

        elif scenario_number == 7:
            scenario_meta["name"] = "No Verified Safe Destination Available (Shelter-in-Place Only)"
            # Close all safe havens and regional hubs
            self.generate_incident(HazardType.SHELTER_CLOSURE, 16.2360, 80.5520, radius_meters=800.0, description="Civil Defense Safe Haven Compromised by Fumes")
            scenario_meta["incidents_created"] = 1

        elif scenario_number == 8:
            scenario_meta["name"] = "Source Feed Becoming Stale"
            inc = self.generate_incident(HazardType.SMOKE_PLUME, 16.2500, 80.5100, radius_meters=300.0)
            inc.verification_status = VerificationStatus.STALE
            inc.observed_at = datetime.now(timezone.utc) - timedelta(hours=3)
            scenario_meta["incidents_created"] = 1

        elif scenario_number == 9:
            scenario_meta["name"] = "Conflicting Reports From Two Sources"
            inc1 = self.generate_incident(HazardType.BUILDING_FIRE, 16.2600, 80.5000, radius_meters=400.0, description="Source A: Critical Fire")
            inc2 = self.generate_incident(HazardType.RESOLVED_INCIDENT, 16.2600, 80.5000, radius_meters=400.0, description="Source B: Fire Contained")
            inc1.verification_status = VerificationStatus.CONFLICTING
            inc2.verification_status = VerificationStatus.CONFLICTING
            scenario_meta["incidents_created"] = 2

        elif scenario_number == 10:
            scenario_meta["name"] = "External API Failure (Graceful Fallback Mode)"
            # Zero external incidents, internal offline heuristics only
            scenario_meta["incidents_created"] = 0

        elif scenario_number == 11:
            scenario_meta["name"] = "GPS Permission Denied (Manual Pin Drop Navigation)"
            scenario_meta["incidents_created"] = 0

        elif scenario_number == 12:
            scenario_meta["name"] = "Loss of Network Connectivity (Edge Offline Graph Mode)"
            scenario_meta["incidents_created"] = 0

        elif scenario_number == 13:
            scenario_meta["name"] = "Notification Submission Failure (Retry & Fallback Queue)"
            scenario_meta["incidents_created"] = 0

        elif scenario_number == 14:
            scenario_meta["name"] = "Hazard Resolved & Corridor Re-opened"
            inc = self.generate_incident(HazardType.FLOODED_ROAD, 16.2700, 80.4900, radius_meters=300.0)
            self.resolve_incident(inc.incident_id, "Drainage cleared by municipal pumps")
            scenario_meta["incidents_created"] = 1

        elif scenario_number == 15:
            scenario_meta["name"] = "Route Becoming Available Again After Recalculation"
            scenario_meta["incidents_created"] = 0

        elif scenario_number == 16:
            scenario_meta["name"] = "Destination Closing During Navigation"
            self.generate_incident(HazardType.SHELTER_CLOSURE, 16.3067, 80.4365, radius_meters=400.0, description="Destination Evacuated Due to Gas Leak")
            scenario_meta["incidents_created"] = 1

        elif scenario_number == 17:
            scenario_meta["name"] = "Accessible Route Becoming Unavailable (Wheelchair Constraint Violation)"
            self.generate_incident(HazardType.BLOCKED_STAIRCASE, 16.2340, 80.5510, radius_meters=80.0, description="Elevator Disabled / Ramp Blocked by Debris")
            scenario_meta["incidents_created"] = 1

        elif scenario_number == 18:
            scenario_meta["name"] = "Simulated Hazard Prevented from Entering Production Alerts"
            sim = self.generate_incident(HazardType.WILDFIRE, 16.2500, 80.5200, radius_meters=1000.0, description="Simulated Wildfire Boundary Test")
            # Enforce that environment is SIMULATED
            assert sim.is_simulated is True
            scenario_meta["incidents_created"] = 1

        self.active_scenario_name = scenario_meta["name"]
        return scenario_meta

    def get_active_simulated_incidents(self) -> List[UnifiedIncident]:
        """Returns currently active simulated hazards."""
        return [inc for inc in self.simulated_incidents.values() if inc.is_active]
