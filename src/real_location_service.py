"""
Compatibility shim for real_location_service.
Aliases src.location_service and provides a singleton real_location_service instance.
"""

from src.location_service import (
    LocationService,
    LocationPermissionStatus,
    haversine_distance_m,
    calculate_bearing_deg,
    bearing_to_cardinal,
)

real_location_service = LocationService()

__all__ = [
    "LocationService",
    "LocationPermissionStatus",
    "haversine_distance_m",
    "calculate_bearing_deg",
    "bearing_to_cardinal",
    "real_location_service",
]
