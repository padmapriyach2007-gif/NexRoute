"""
Spatial Query Utilities for Road Intelligence
Provides bounding-box indexed radius searches and along-route polyline corridor queries.
"""

import math
from typing import List, Tuple
from sqlalchemy.orm import Session

from src.hazard_map import distance_point_to_segment_m, haversine_distance_m
from src.backend.database.models import RoadConditionReport


def find_reports_in_radius(
    db: Session,
    latitude: float,
    longitude: float,
    radius_meters: float,
    include_pending: bool = True
) -> List[Tuple[RoadConditionReport, float]]:
    """
    Returns list of (report, distance_meters) within radius_meters.
    Uses bounding-box pre-filtering for database efficiency.
    """
    # 1 degree latitude ~ 111,000 meters
    delta_lat = radius_meters / 111000.0
    cos_lat = max(0.1, math.cos(math.radians(latitude)))
    delta_lon = radius_meters / (111000.0 * cos_lat)

    query = db.query(RoadConditionReport).filter(
        RoadConditionReport.latitude.between(latitude - delta_lat, latitude + delta_lat),
        RoadConditionReport.longitude.between(longitude - delta_lon, longitude + delta_lon)
    )

    if not include_pending:
        query = query.filter(RoadConditionReport.status == "VERIFIED")
    else:
        query = query.filter(RoadConditionReport.status.in_(["VERIFIED", "PENDING"]))

    candidates = query.all()
    results = []
    for c in candidates:
        dist_m = haversine_distance_m(latitude, longitude, c.latitude, c.longitude)
        if dist_m <= radius_meters:
            results.append((c, dist_m))

    results.sort(key=lambda x: x[1])
    return results


def find_reports_along_corridor(
    db: Session,
    polyline: List[Tuple[float, float]],
    corridor_meters: float = 100.0,
    include_pending: bool = True
) -> List[Tuple[RoadConditionReport, float]]:
    """
    Finds reports that lie within corridor_meters of any line segment along the polyline.
    """
    if not polyline or len(polyline) < 2:
        return []

    # Calculate overall polyline bounding box
    lats = [p[0] for p in polyline]
    lons = [p[1] for p in polyline]
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    delta_lat = corridor_meters / 111000.0
    delta_lon = corridor_meters / (111000.0 * max(0.1, math.cos(math.radians((min_lat + max_lat) / 2.0))))

    query = db.query(RoadConditionReport).filter(
        RoadConditionReport.latitude.between(min_lat - delta_lat, max_lat + delta_lat),
        RoadConditionReport.longitude.between(min_lon - delta_lon, max_lon + delta_lon)
    )

    if not include_pending:
        query = query.filter(RoadConditionReport.status == "VERIFIED")
    else:
        query = query.filter(RoadConditionReport.status.in_(["VERIFIED", "PENDING"]))

    candidates = query.all()
    corridor_hits = []

    for report in candidates:
        min_dist_m = float("inf")
        for i in range(len(polyline) - 1):
            p1 = polyline[i]
            p2 = polyline[i + 1]
            dist_m = distance_point_to_segment_m(
                report.latitude, report.longitude,
                p1[0], p1[1],
                p2[0], p2[1]
            )
            if dist_m < min_dist_m:
                min_dist_m = dist_m

        if min_dist_m <= (report.affected_radius_meters + corridor_meters):
            corridor_hits.append((report, min_dist_m))

    corridor_hits.sort(key=lambda x: x[1])
    return corridor_hits
