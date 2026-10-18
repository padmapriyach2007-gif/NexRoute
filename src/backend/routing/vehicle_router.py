"""
Vehicle-Aware Routing & EV Charging Planner
Applies commercial/dimensional restrictions (low bridges, weight limits)
and plans necessary EV fast charging stops when trip exceeds remaining battery range.
"""

from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session

from src.hazard_map import haversine_distance_m
from src.backend.database.models import VehicleProfile, Place
from src.backend.routing.provider_interface import RouteAlternative


class VehicleRouter:
    def check_vehicle_restrictions(
        self,
        route: RouteAlternative,
        vehicle: VehicleProfile
    ) -> Dict[str, Any]:
        """
        Validates vehicle dimensions against known road network constraints.
        """
        violations = []
        
        # Check height limit for heavy/commercial vehicles (underpasses < 3.8m)
        if vehicle.height_meters > 3.8:
            if any("Vadlamudi Overbridge" in r for r in route.summary_roads):
                violations.append({
                    "constraint": "MAX_HEIGHT_RESTRICTION",
                    "limit_meters": 3.8,
                    "vehicle_value": vehicle.height_meters,
                    "location": "Vadlamudi Overbridge Approach",
                    "advice": "Reroute via Guntur Autonagar Bypass Expressway"
                })

        # Check gross weight limit (rural bridges < 10 tons)
        if vehicle.weight_tons > 10.0:
            if any("Chebrolu" in r or "Canal Bridge" in r for r in route.summary_roads):
                violations.append({
                    "constraint": "MAX_WEIGHT_RESTRICTION",
                    "limit_tons": 10.0,
                    "vehicle_value": vehicle.weight_tons,
                    "location": "Chebrolu Rural Canal Culvert",
                    "advice": "Heavy axle load banned. Use National Highway NH16"
                })

        return {
            "is_compatible": len(violations) == 0,
            "violations": violations
        }

    def plan_ev_charging_stops(
        self,
        route: RouteAlternative,
        vehicle: VehicleProfile,
        db: Session
    ) -> Dict[str, Any]:
        """
        Evaluates EV battery sufficiency and inserts charging stops if needed.
        """
        if vehicle.vehicle_type != "EV":
            return {"requires_charging": False, "charging_stops": []}

        # Calculate remaining vehicle range in km
        # Formula: (battery_capacity * current_charge_pct / 100) / energy_consumption_kwh_per_km
        consumption_rate = 0.16  # standard EV kWh / km
        usable_kwh = vehicle.battery_capacity_kwh * (vehicle.current_charge_percent / 100.0)
        remaining_range_km = usable_kwh / consumption_rate if consumption_rate > 0 else 100.0

        if remaining_range_km >= route.distance_km:
            return {
                "requires_charging": False,
                "remaining_range_at_arrival_km": round(remaining_range_km - route.distance_km, 1),
                "battery_at_arrival_percent": round(max(0.0, (remaining_range_km - route.distance_km) / (vehicle.battery_capacity_kwh / consumption_rate) * 100), 1),
                "charging_stops": []
            }

        # Route exceeds remaining range! Find EV charging stations along the route corridor
        chargers = db.query(Place).filter(Place.category == "EV_CHARGING").all()
        recommended_stops = []

        for ch in chargers:
            # Check distance from origin to charger
            origin = route.polyline[0] if route.polyline else (16.2335, 80.5505)
            dist_to_ch_m = haversine_distance_m(origin[0], origin[1], ch.latitude, ch.longitude)
            dist_to_ch_km = dist_to_ch_m / 1000.0

            if dist_to_ch_km <= remaining_range_km * 0.85:  # Reachable with 15% safety buffer
                # Estimated fast charging duration to reach 80% (typically 30-40 mins on 50kW DC)
                needed_charge_kwh = vehicle.battery_capacity_kwh * 0.60
                est_charge_minutes = round((needed_charge_kwh / 50.0) * 60) + 5
                
                recommended_stops.append({
                    "station_id": ch.id,
                    "name": ch.name,
                    "latitude": ch.latitude,
                    "longitude": ch.longitude,
                    "distance_from_origin_km": round(dist_to_ch_km, 1),
                    "connector_type": vehicle.connector_type,
                    "charger_power_kw": 60,
                    "recommended_charge_duration_minutes": max(20, est_charge_minutes),
                    "estimated_charging_cost_inr": round(needed_charge_kwh * 15.0, 2)
                })

        return {
            "requires_charging": True,
            "deficiency_km": round(route.distance_km - remaining_range_km, 1),
            "charging_stops": recommended_stops
        }
