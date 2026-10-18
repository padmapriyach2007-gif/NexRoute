"""
Camera-Assisted & Visual Navigation Service
Provides geotagged landmarks, visual reference cues, and field-of-view (FOV)
heading alignment calculations for augmented on-screen camera directions.
"""

import math
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from src.hazard_map import haversine_distance_m
from src.backend.database.models import VisualLandmark


def calculate_bearing_degrees(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates forward compass azimuth from point 1 to point 2 in degrees [0, 360)."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360.0) % 360.0


class VisualNavigationService:
    @staticmethod
    def get_landmarks_in_camera_view(
        db: Session,
        user_lat: float,
        user_lon: float,
        user_heading_degrees: float,
        camera_fov_degrees: float = 65.0,
        max_distance_meters: float = 500.0
    ) -> List[Dict[str, Any]]:
        """
        Finds verified landmarks within the user's camera viewport cone and calculates relative angles.
        """
        all_landmarks = db.query(VisualLandmark).filter(VisualLandmark.is_verified == True).all()
        visible_cues = []

        half_fov = camera_fov_degrees / 2.0

        for lm in all_landmarks:
            dist_m = haversine_distance_m(user_lat, user_lon, lm.latitude, lm.longitude)
            if dist_m > max_distance_meters:
                continue

            # Calculate bearing towards landmark
            landmark_bearing = calculate_bearing_degrees(user_lat, user_lon, lm.latitude, lm.longitude)
            
            # Difference from camera heading
            angle_diff = (landmark_bearing - user_heading_degrees + 180.0) % 360.0 - 180.0

            # Check if landmark falls inside camera field of view cone
            is_in_viewport = abs(angle_diff) <= half_fov

            # Relative position on screen (-1.0 left edge to +1.0 right edge)
            screen_x_normalized = max(-1.0, min(1.0, angle_diff / half_fov))

            visible_cues.append({
                "landmark_id": lm.id,
                "name": lm.name,
                "distance_meters": round(dist_m, 1),
                "bearing_degrees": round(landmark_bearing, 1),
                "relative_angle_degrees": round(angle_diff, 1),
                "screen_x_normalized": round(screen_x_normalized, 2),
                "is_in_camera_view": is_in_viewport,
                "visual_cue_description": lm.visual_cue_description,
                "turn_reference_instruction": lm.turn_reference_instruction,
                "photo_url": lm.photo_url
            })

        visible_cues.sort(key=lambda x: x["distance_meters"])
        return visible_cues
