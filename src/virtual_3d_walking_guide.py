"""
Realistic 3D Human Walking Guide & Step-by-Step Visual Navigation
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Predictive Adaptive Transit & Hazard-Free Intelligent Navigation

Transforms route geometry and turn-by-turn navigation instructions into a
realistic, articulated 3D human walking instructor. The virtual human performs
natural walking movements along the actual road geometry, decelerates and gestures
at junctions, follows road curves, waits and looks safely at pedestrian crossings,
and arrives at the mapped destination.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import math
import re
from typing import Any, Dict, List, Optional, Tuple, Union


class WalkingGuideState(str, Enum):
    """
    Dedicated state machine states for the 3D Walking Guide Animation Controller.
    """
    IDLE = "IDLE"
    WALKING_STRAIGHT = "WALKING_STRAIGHT"
    APPROACHING_TURN = "APPROACHING_TURN"
    TURNING_LEFT = "TURNING_LEFT"
    TURNING_RIGHT = "TURNING_RIGHT"
    FOLLOWING_CURVE = "FOLLOWING_CURVE"
    WAITING_AT_CROSSING = "WAITING_AT_CROSSING"
    CROSSING = "CROSSING"
    JUMPING = "JUMPING"
    CELEBRATING = "CELEBRATING"
    ROUTE_DEVIATION = "ROUTE_DEVIATION"
    STOPPING = "STOPPING"
    ARRIVING = "ARRIVING"
    ARRIVED = "ARRIVED"
    PAUSED = "PAUSED"
    ROUTE_UNAVAILABLE = "ROUTE_UNAVAILABLE"


@dataclass
class NavigationManeuver3D:
    """
    Represents an individual navigation maneuver correlated to real route geometry stationing.
    """
    step_index: int
    direction_type: str  # START, STRAIGHT, LEFT, RIGHT, SLIGHT_LEFT, SLIGHT_RIGHT, U_TURN, CROSSING, ARRIVE
    headline: str
    instruction_text: str
    spoken_instruction: str
    road_name: str
    distance_m: float
    start_station_m: float
    junction_station_m: float
    end_station_m: float
    icon: str
    turn_angle_deg: float = 0.0
    has_crossing: bool = False
    crossing_type: str = "zebra"
    accessible_guidance: str = ""
    tactile_crossing_note: str = ""
    what_to_look_for: str = ""
    coordinates: Optional[List[float]] = None


@dataclass
class Route3DPoint:
    """
    Local metric 3D path vertex along the route.
    """
    x: float
    y: float
    z: float
    lat: float
    lon: float
    station_m: float
    bearing_deg: float
    tangent: Tuple[float, float, float]
    curvature: float = 0.0
    maneuver_index: int = 0
    is_crossing: bool = False


class Route3DGeometryEngine:
    """
    Converts geographic GPS coordinates (latitude, longitude) into metric 3D
    scene coordinates, builds smoothed paths, calculates curvature, and correlates
    maneuver instructions with route stations.
    """

    EARTH_RADIUS_M = 6371000.0

    @classmethod
    def lat_lon_to_local_3d(
        cls,
        lat: float,
        lon: float,
        origin_lat: float,
        origin_lon: float
    ) -> Tuple[float, float, float]:
        """
        Projects latitude/longitude to local metric Cartesian coordinates (X, Y, Z).
        X = Easting in meters
        Z = Northing (negative for Three.js forward Z) in meters
        Y = Elevation (default 0.0)
        """
        lat_rad = math.radians(origin_lat)
        x = (lon - origin_lon) * (math.pi / 180.0) * cls.EARTH_RADIUS_M * math.cos(lat_rad)
        z = -(lat - origin_lat) * (math.pi / 180.0) * cls.EARTH_RADIUS_M
        return (round(x, 3), 0.0, round(z, 3))

    @classmethod
    def local_3d_to_lat_lon(
        cls,
        x: float,
        z: float,
        origin_lat: float,
        origin_lon: float
    ) -> Tuple[float, float]:
        """
        Inverse projection from local 3D Cartesian coordinates back to lat/lon.
        """
        lat_rad = math.radians(origin_lat)
        lat = origin_lat - (z / (cls.EARTH_RADIUS_M * (math.pi / 180.0)))
        lon = origin_lon + (x / (cls.EARTH_RADIUS_M * math.cos(lat_rad) * (math.pi / 180.0)))
        return (lat, lon)

    @classmethod
    def calculate_bearing(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Computes forward azimuth/bearing between two geographic points in degrees [0, 360).
        """
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        d_lambda = math.radians(lon2 - lon1)

        y = math.sin(d_lambda) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda)
        bearing = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0
        return round(bearing, 2)

    @classmethod
    def calculate_angle_diff(cls, b1: float, b2: float) -> float:
        """
        Calculates signed shortest angle difference between two bearings in degrees [-180, 180].
        Negative = Left turn, Positive = Right turn.
        """
        diff = (b2 - b1 + 180.0) % 360.0 - 180.0
        return round(diff, 2)

    @classmethod
    def haversine_distance_m(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Computes great-circle distance between two GPS coordinates in meters.
        """
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (
            math.sin(d_lat / 2.0) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
        return cls.EARTH_RADIUS_M * c

    @classmethod
    def clean_polyline(
        cls,
        polyline: Optional[List[Any]]
    ) -> List[Tuple[float, float]]:
        """
        Normalizes polyline input into a clean list of (lat, lon) floats.
        Supports lists of lists, tuples, or dicts with lat/lng keys.
        """
        if not polyline:
            return []

        cleaned: List[Tuple[float, float]] = []
        for pt in polyline:
            if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                try:
                    cleaned.append((float(pt[0]), float(pt[1])))
                except (ValueError, TypeError):
                    continue
            elif isinstance(pt, dict):
                lat = pt.get("lat") or pt.get("latitude")
                lon = pt.get("lon") or pt.get("lng") or pt.get("longitude")
                if lat is not None and lon is not None:
                    try:
                        cleaned.append((float(lat), float(lon)))
                    except (ValueError, TypeError):
                        continue

        # Deduplicate consecutive identical points
        deduped: List[Tuple[float, float]] = []
        for p in cleaned:
            if not deduped or cls.haversine_distance_m(deduped[-1][0], deduped[-1][1], p[0], p[1]) > 0.4:
                deduped.append(p)

        return deduped

    @classmethod
    def generate_resampled_3d_path(
        cls,
        polyline: List[Tuple[float, float]],
        resolution_m: float = 2.0
    ) -> List[Route3DPoint]:
        """
        Resamples a GPS polyline into smooth, continuous 3D points with fixed spacing,
        calculating station distances, tangents, bearings, and curvature.
        """
        if not polyline or len(polyline) < 2:
            return []

        origin_lat, origin_lon = polyline[0]

        # First convert raw polyline points to 3D Cartesian coordinates
        raw_3d: List[Dict[str, Any]] = []
        cumulative_dist = 0.0

        for i, (lat, lon) in enumerate(polyline):
            x, y, z = cls.lat_lon_to_local_3d(lat, lon, origin_lat, origin_lon)
            if i > 0:
                prev = raw_3d[-1]
                seg_d = math.hypot(x - prev["x"], z - prev["z"])
                cumulative_dist += seg_d
            raw_3d.append({
                "lat": lat,
                "lon": lon,
                "x": x,
                "y": y,
                "z": z,
                "station_m": cumulative_dist
            })

        total_length = cumulative_dist
        if total_length < 0.1:
            return []

        # Resample along station distance at resolution_m intervals
        resampled: List[Route3DPoint] = []
        num_samples = max(2, int(math.ceil(total_length / resolution_m)) + 1)
        sample_stations = [min(i * resolution_m, total_length) for i in range(num_samples)]
        if sample_stations[-1] < total_length:
            sample_stations.append(total_length)

        raw_idx = 0
        for s in sample_stations:
            while raw_idx < len(raw_3d) - 2 and raw_3d[raw_idx + 1]["station_m"] < s:
                raw_idx += 1

            p1 = raw_3d[raw_idx]
            p2 = raw_3d[raw_idx + 1]
            seg_len = p2["station_m"] - p1["station_m"]

            if seg_len > 0.0001:
                t = max(0.0, min(1.0, (s - p1["station_m"]) / seg_len))
            else:
                t = 0.0

            cur_x = p1["x"] + t * (p2["x"] - p1["x"])
            cur_z = p1["z"] + t * (p2["z"] - p1["z"])
            cur_lat = p1["lat"] + t * (p2["lat"] - p1["lat"])
            cur_lon = p1["lon"] + t * (p2["lon"] - p1["lon"])

            # Compute tangent direction
            dx = p2["x"] - p1["x"]
            dz = p2["z"] - p1["z"]
            norm = math.hypot(dx, dz)
            if norm > 0.0001:
                tx, tz = dx / norm, dz / norm
            else:
                tx, tz = 0.0, -1.0

            bearing = (math.degrees(math.atan2(tx, -tz)) + 360.0) % 360.0

            resampled.append(Route3DPoint(
                x=round(cur_x, 3),
                y=0.0,
                z=round(cur_z, 3),
                lat=round(cur_lat, 7),
                lon=round(cur_lon, 7),
                station_m=round(s, 2),
                bearing_deg=round(bearing, 2),
                tangent=(round(tx, 4), 0.0, round(tz, 4)),
                curvature=0.0
            ))

        # Calculate curvature (change in heading per meter)
        for i in range(1, len(resampled) - 1):
            prev_b = resampled[i - 1].bearing_deg
            next_b = resampled[i + 1].bearing_deg
            ds = resampled[i + 1].station_m - resampled[i - 1].station_m
            if ds > 0.001:
                angle_diff = cls.calculate_angle_diff(prev_b, next_b)
                resampled[i].curvature = round(abs(angle_diff) / ds, 4)

        return resampled

    @classmethod
    def build_maneuvers(
        cls,
        steps: List[Any],
        polyline: List[Tuple[float, float]],
        total_distance_m: float = 0.0,
        origin_name: str = "Origin",
        dest_name: str = "Destination"
    ) -> List[NavigationManeuver3D]:
        """
        Parses navigation steps and correlates them with exact route stations and maneuver types.
        Detects road crossings, turns, straight corridors, and arrival.
        """
        maneuvers: List[NavigationManeuver3D] = []
        num_steps = len(steps) if steps else 0

        # If no steps provided, generate a sensible default start-cruise-arrive sequence
        if num_steps == 0:
            half = total_distance_m / 2.0 if total_distance_m > 0 else 250.0
            end = total_distance_m if total_distance_m > 0 else 500.0
            return [
                NavigationManeuver3D(
                    step_index=0,
                    direction_type="START",
                    headline=f"Start walking from {origin_name}",
                    instruction_text=f"Begin journey at {origin_name} along the pedestrian pathway.",
                    spoken_instruction=f"Starting your journey from {origin_name}. Walk straight along the pedestrian corridor.",
                    road_name="Departure Pathway",
                    distance_m=half,
                    start_station_m=0.0,
                    junction_station_m=0.0,
                    end_station_m=half,
                    icon="🟢",
                    turn_angle_deg=0.0,
                    has_crossing=False,
                    accessible_guidance="Step-free accessible sidewalk with smooth curb ramp.",
                    tactile_crossing_note="Tactile guidance tiles installed along sidewalk.",
                    what_to_look_for="Look for the main exit gate and pedestrian signpost."
                ),
                NavigationManeuver3D(
                    step_index=1,
                    direction_type="ARRIVE",
                    headline=f"Safely arrive at {dest_name}",
                    instruction_text=f"You have reached your destination: {dest_name}.",
                    spoken_instruction=f"You have safely arrived at {dest_name}.",
                    road_name="Destination Terminal",
                    distance_m=end - half,
                    start_station_m=half,
                    junction_station_m=end,
                    end_station_m=end,
                    icon="🏁",
                    turn_angle_deg=0.0,
                    has_crossing=False,
                    accessible_guidance="Accessible step-free entryway at destination.",
                    tactile_crossing_note="Arrival entrance paving guide.",
                    what_to_look_for=f"Look for the destination entrance for {dest_name}."
                )
            ]

        # Normalize raw step objects (can be dicts or dataclasses)
        norm_steps: List[Dict[str, Any]] = []
        for s in steps:
            if hasattr(s, "__dict__"):
                norm_steps.append(dict(s.__dict__))
            elif isinstance(s, dict):
                norm_steps.append(dict(s))
            else:
                norm_steps.append({"instruction": str(s)})

        # Compute cumulative stations per step
        curr_station = 0.0
        for idx, s in enumerate(norm_steps):
            dist_val = s.get("distance_meters") or s.get("distance_m") or s.get("dist") or 0.0
            if isinstance(dist_val, str):
                try:
                    dist_val = float(dist_val.replace("km", "000").replace("m", "").strip())
                except ValueError:
                    dist_val = 150.0
            dist_m = float(dist_val)
            if dist_m <= 0.0 and idx < len(norm_steps) - 1:
                dist_m = max(50.0, (total_distance_m - curr_station) / max(1, len(norm_steps) - idx))

            raw_type = str(
                s.get("direction_type")
                or s.get("instruction_type")
                or s.get("type")
                or ""
            ).upper()
            instr = str(
                s.get("instruction_text")
                or s.get("action_headline")
                or s.get("instruction")
                or s.get("headline")
                or f"Step {idx + 1}"
            )
            spoken = str(
                s.get("spoken_instruction")
                or s.get("spoken_text")
                or s.get("virtual_guide_speech")
                or instr
            )
            road = str(s.get("road_name") or s.get("road") or "")
            icon = str(s.get("icon") or "📍")
            look = str(s.get("what_to_look_for") or s.get("landmarks") or "Look for pedestrian signage.")
            access = str(s.get("accessible_guidance") or "Step-free continuous accessible route.")
            tactile = str(s.get("tactile_crossing_note") or "Standard pedestrian walkway.")

            # Infer direction type from instruction text if generic
            instr_l = instr.lower()
            if not raw_type or raw_type in ["STRAIGHT", "CONTINUE"]:
                if "left" in instr_l:
                    raw_type = "SLIGHT_LEFT" if "slight" in instr_l or "bear" in instr_l else "LEFT"
                elif "right" in instr_l:
                    raw_type = "SLIGHT_RIGHT" if "slight" in instr_l or "bear" in instr_l else "RIGHT"
                elif "cross" in instr_l or "zebra" in instr_l or "pedestrian signal" in instr_l:
                    raw_type = "CROSSING"
                elif "arrive" in instr_l or "destination" in instr_l or idx == len(norm_steps) - 1:
                    raw_type = "ARRIVE"
                elif idx == 0 and ("start" in instr_l or "head" in instr_l or "depart" in instr_l):
                    raw_type = "START"
                else:
                    raw_type = "STRAIGHT"

            # Compute turn angles and crossing flags
            turn_angle = 0.0
            has_crossing = False

            if raw_type == "LEFT":
                turn_angle = -90.0
                has_crossing = True  # Junctions have crossings
                if icon == "📍":
                    icon = "⬅️"
            elif raw_type == "RIGHT":
                turn_angle = 90.0
                has_crossing = True
                if icon == "📍":
                    icon = "➡️"
            elif raw_type == "SLIGHT_LEFT":
                turn_angle = -45.0
                if icon == "📍":
                    icon = "↖️"
            elif raw_type == "SLIGHT_RIGHT":
                turn_angle = 45.0
                if icon == "📍":
                    icon = "↗️"
            elif raw_type == "CROSSING" or "cross" in instr_l:
                has_crossing = True
                raw_type = "CROSSING"
                icon = "🚸"
            elif raw_type == "ARRIVE" or idx == len(norm_steps) - 1:
                raw_type = "ARRIVE"
                icon = "🏁"
            elif raw_type == "START" or idx == 0:
                raw_type = "START"
                icon = "🟢"
            else:
                raw_type = "STRAIGHT"
                if icon == "📍":
                    icon = "⬆️"

            start_s = curr_station
            end_s = curr_station + dist_m
            junction_s = end_s if raw_type not in ["ARRIVE", "START"] else curr_station

            maneuvers.append(NavigationManeuver3D(
                step_index=idx,
                direction_type=raw_type,
                headline=instr.split(".")[0],
                instruction_text=instr,
                spoken_instruction=spoken,
                road_name=road or f"Route Segment {idx + 1}",
                distance_m=round(dist_m, 1),
                start_station_m=round(start_s, 1),
                junction_station_m=round(junction_s, 1),
                end_station_m=round(end_s, 1),
                icon=icon,
                turn_angle_deg=turn_angle,
                has_crossing=has_crossing,
                crossing_type="zebra" if has_crossing else "none",
                accessible_guidance=access,
                tactile_crossing_note=tactile,
                what_to_look_for=look
            ))

            curr_station = end_s

        return maneuvers

    @classmethod
    def generate_synthetic_curved_polyline(
        cls,
        origin_lat: float = 16.2335,
        origin_lon: float = 80.5505,
        dest_lat: float = 16.2395,
        dest_lon: float = 80.5585,
        num_points: int = 12
    ) -> List[Tuple[float, float]]:
        """
        Generates an authentic, realistic curved route polyline for demonstration
        when the external map provider supplies only 2 endpoints.
        """
        pts: List[Tuple[float, float]] = []
        d_lat = dest_lat - origin_lat
        d_lon = dest_lon - origin_lon

        for i in range(num_points):
            t = i / float(num_points - 1)
            # Add realistic road curvature with sine offsets
            lateral_offset = math.sin(t * math.pi) * 0.0018
            lat = origin_lat + t * d_lat + lateral_offset * 0.5
            lon = origin_lon + t * d_lon + lateral_offset
            pts.append((round(lat, 7), round(lon, 7)))

        return pts


class WalkingGuideAnimationController:
    """
    Dedicated animation controller governing the 3D Virtual Human's gait,
    speed, orientation, and navigation state machine.
    """

    def __init__(
        self,
        maneuvers: List[NavigationManeuver3D],
        total_distance_m: float,
        base_walking_speed_mps: float = 1.35
    ):
        self.maneuvers = maneuvers
        self.total_distance_m = max(1.0, total_distance_m)
        self.base_speed = base_walking_speed_mps
        self.current_state = WalkingGuideState.IDLE
        self.current_station_m = 0.0
        self.current_step_index = 0
        self.is_paused = False

    def evaluate_state(
        self,
        station_m: float,
        is_paused: bool = False
    ) -> Tuple[WalkingGuideState, float, Optional[NavigationManeuver3D]]:
        """
        Evaluates the active state, recommended walking speed, and current maneuver
        based on the virtual guide's current station position along the route.
        """
        if is_paused:
            return WalkingGuideState.PAUSED, 0.0, self.get_maneuver_at_station(station_m)

        if not self.maneuvers:
            return WalkingGuideState.ROUTE_UNAVAILABLE, 0.0, None

        # Check for destination arrival (at the very end of route)
        if station_m >= self.total_distance_m - 2.5:
            return WalkingGuideState.ARRIVED, 0.0, self.maneuvers[-1]

        active_m = self.get_maneuver_at_station(station_m) or self.maneuvers[0]

        # Check if approaching destination arrival (only if on the final arrival segment)
        if station_m >= self.total_distance_m - 12.0 and active_m == self.maneuvers[-1]:
            return WalkingGuideState.ARRIVING, self.base_speed * 0.45, self.maneuvers[-1]

        # Check all maneuvers to detect if we are in an upcoming or active junction/crossing zone
        for m in self.maneuvers:
            dist_to_junction = m.junction_station_m - station_m

            # 1. Road Crossing Checks (if explicitly crossing maneuver or crossing flag without turn)
            if (m.direction_type == "CROSSING" or (m.has_crossing and m.direction_type not in ["LEFT", "RIGHT", "SLIGHT_LEFT", "SLIGHT_RIGHT"])) and -4.0 <= dist_to_junction <= 8.0:
                if 0.0 <= dist_to_junction <= 3.5:
                    # Stopped at curb ramp, checking traffic and waiting for walk signal
                    return WalkingGuideState.WAITING_AT_CROSSING, 0.0, m
                elif -4.0 <= dist_to_junction < 0.0:
                    # Stepping across zebra crosswalk
                    return WalkingGuideState.CROSSING, self.base_speed * 0.9, m

            # 2. Turn Checks
            if m.direction_type in ["LEFT", "SLIGHT_LEFT"]:
                if 3.5 < dist_to_junction <= 18.0:
                    return WalkingGuideState.APPROACHING_TURN, self.base_speed * 0.7, m
                elif -4.0 <= dist_to_junction <= 3.5:
                    return WalkingGuideState.TURNING_LEFT, self.base_speed * 0.55, m
            elif m.direction_type in ["RIGHT", "SLIGHT_RIGHT"]:
                if 3.5 < dist_to_junction <= 18.0:
                    return WalkingGuideState.APPROACHING_TURN, self.base_speed * 0.7, m
                elif -4.0 <= dist_to_junction <= 3.5:
                    return WalkingGuideState.TURNING_RIGHT, self.base_speed * 0.55, m

        # Default walking behavior
        return WalkingGuideState.WALKING_STRAIGHT, self.base_speed, active_m

    def get_maneuver_at_station(self, station_m: float) -> Optional[NavigationManeuver3D]:
        """
        Finds the navigation maneuver corresponding to a given route station.
        """
        for m in self.maneuvers:
            if m.start_station_m <= station_m <= m.end_station_m:
                return m
        return self.maneuvers[-1] if self.maneuvers else None


def build_3d_walking_guide_html(
    origin_name: str,
    dest_name: str,
    polyline: Optional[List[Any]] = None,
    steps: Optional[List[Any]] = None,
    travel_mode: str = "walking",
    total_distance_m: Optional[float] = None,
    user_coords: Optional[List[float]] = None,
    user_speed_kmh: float = 0.0,
    is_live_moving: bool = False,
    is_simulation_mode: bool = True
) -> str:
    """
    Renders the complete 3D Human Walking Guide and Visual Navigation Scene.
    Embeds a responsive WebGL/Three.js engine with procedural articulated walking
    humanoid character, dynamic camera controllers, AR trajectory ribbon, step-free
    crossing assist, and synchronized voice instruction.
    """
    cleaned_poly = Route3DGeometryEngine.clean_polyline(polyline)

    # Fallback to realistic synthetic curved polyline if fewer than 2 points provided
    if len(cleaned_poly) < 2:
        cleaned_poly = Route3DGeometryEngine.generate_synthetic_curved_polyline(
            origin_lat=16.2335,
            origin_lon=80.5505,
            dest_lat=16.2415,
            dest_lon=80.5590
        )

    # Calculate total distance if not provided
    calculated_total_dist = 0.0
    for i in range(len(cleaned_poly) - 1):
        p1 = cleaned_poly[i]
        p2 = cleaned_poly[i + 1]
        calculated_total_dist += Route3DGeometryEngine.haversine_distance_m(p1[0], p1[1], p2[0], p2[1])

    final_total_dist = float(total_distance_m) if total_distance_m and total_distance_m > 10.0 else max(200.0, calculated_total_dist)

    # Generate resampled 3D path and maneuver sequence
    path_3d = Route3DGeometryEngine.generate_resampled_3d_path(cleaned_poly, resolution_m=2.0)
    maneuvers = Route3DGeometryEngine.build_maneuvers(
        steps=steps or [],
        polyline=cleaned_poly,
        total_distance_m=final_total_dist,
        origin_name=origin_name,
        dest_name=dest_name
    )

    # Prepare JSON serializable scene data
    path_points_data = [
        {
            "x": pt.x,
            "y": pt.y,
            "z": pt.z,
            "s": pt.station_m,
            "b": pt.bearing_deg,
            "tx": pt.tangent[0],
            "tz": pt.tangent[2],
            "curv": pt.curvature
        }
        for pt in path_3d
    ]

    maneuvers_data = [asdict(m) for m in maneuvers]

    scene_payload = {
        "origin": origin_name,
        "destination": dest_name,
        "travel_mode": travel_mode.lower(),
        "total_distance_m": round(final_total_dist, 1),
        "path_points": path_points_data,
        "maneuvers": maneuvers_data,
        "is_simulation_mode": is_simulation_mode,
        "user_coords": user_coords if user_coords and len(user_coords) >= 2 else None,
        "user_speed_kmh": round(user_speed_kmh, 1),
        "is_live_moving": is_live_moving
    }

    payload_json = json.dumps(scene_payload, default=str)

    return f"""
    <div id='walking-guide-3d-root' class='walking-guide-container'>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&display=swap');

            .walking-guide-container {{
                font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: linear-gradient(135deg, #060d1a 0%, #0b172a 100%);
                border: 1.5px solid rgba(56, 189, 248, 0.4);
                border-radius: 18px;
                padding: 18px;
                margin: 12px 0 20px 0;
                color: #f8fafc;
                box-shadow: 0 16px 48px rgba(0, 0, 0, 0.75), 0 0 24px rgba(56, 189, 248, 0.15);
                position: relative;
                overflow: hidden;
            }}

            /* Header HUD */
            .guide-top-hud {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 12px;
                padding-bottom: 14px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.12);
            }}

            .guide-brand-badge {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}

            .guide-avatar-orb {{
                width: 52px;
                height: 52px;
                border-radius: 50%;
                background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
                border: 2.5px solid #38bdf8;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 26px;
                box-shadow: 0 0 18px rgba(56, 189, 248, 0.5);
                transition: transform 0.3s ease;
            }}

            .guide-state-pill {{
                padding: 4px 12px;
                border-radius: 999px;
                font-size: 0.74rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                transition: all 0.3s ease;
            }}

            .state-WALKING_STRAIGHT {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }}
            .state-APPROACHING_TURN {{ background: rgba(250, 204, 21, 0.2); color: #fde047; border: 1px solid #facc15; }}
            .state-TURNING_LEFT, .state-TURNING_RIGHT {{ background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #38bdf8; }}
            .state-WAITING_AT_CROSSING {{ background: rgba(239, 68, 68, 0.25); color: #f87171; border: 1px solid #ef4444; }}
            .state-CROSSING {{ background: rgba(16, 185, 129, 0.25); color: #6ee7b7; border: 1px solid #10b981; }}
            .state-JUMPING, .state-CELEBRATING {{ background: rgba(236, 72, 153, 0.25); color: #f472b6; border: 1px solid #ec4899; }}
            .state-ROUTE_DEVIATION {{ background: rgba(245, 158, 11, 0.25); color: #fbbf24; border: 1px solid #f59e0b; }}
            .state-STOPPING, .state-PAUSED {{ background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid #94a3b8; }}
            .state-ARRIVING, .state-ARRIVED {{ background: rgba(245, 158, 11, 0.25); color: #fbbf24; border: 1px solid #f59e0b; }}

            /* 3D Viewport Stage */
            .viewport-3d-stage {{
                position: relative;
                width: 100%;
                height: 480px;
                border-radius: 14px;
                overflow: hidden;
                margin-top: 14px;
                border: 1.5px solid rgba(56, 189, 248, 0.3);
                background: #020617;
                box-shadow: inset 0 0 40px rgba(0, 0, 0, 0.85);
            }}

            #threejs-canvas {{
                width: 100% !important;
                height: 100% !important;
                display: block;
            }}

            /* Floating Navigation Overlays inside 3D Scene - Perfect Box Alignment */
            .floating-instruction-card {{
                position: absolute;
                top: 14px;
                left: 14px;
                right: auto;
                width: calc(100% - 130px);
                max-width: 460px;
                background: rgba(10, 20, 40, 0.90);
                backdrop-filter: blur(14px);
                -webkit-backdrop-filter: blur(14px);
                border: 1.5px solid rgba(56, 189, 248, 0.4);
                border-radius: 14px;
                padding: 12px 16px;
                color: #ffffff;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.75);
                pointer-events: auto;
                z-index: 10;
                transition: all 0.3s ease;
                box-sizing: border-box;
            }}

            .maneuver-headline-row {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}

            .maneuver-icon-badge {{
                width: 40px;
                height: 40px;
                border-radius: 10px;
                background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
                border: 1.5px solid #38bdf8;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                flex-shrink: 0;
            }}

            /* Camera & View Controls Floating Toolbar - Non-overlapping Clean Dock */
            .camera-toolbar {{
                position: absolute;
                top: 14px;
                right: 14px;
                display: flex;
                flex-direction: column;
                gap: 6px;
                z-index: 15;
            }}

            .cam-btn {{
                background: rgba(15, 23, 42, 0.85);
                backdrop-filter: blur(8px);
                border: 1px solid rgba(56, 189, 248, 0.35);
                color: #e2e8f0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 0.72rem;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                gap: 6px;
                white-space: nowrap;
            }}

            .cam-btn:hover, .cam-btn.active {{
                background: #0284c7;
                color: #ffffff;
                border-color: #38bdf8;
                box-shadow: 0 0 12px rgba(56, 189, 248, 0.5);
            }}

            /* Responsive Layout to Guarantee No Element Overlap */
            @media (max-width: 680px) {{
                .floating-instruction-card {{
                    width: calc(100% - 28px);
                    max-width: none;
                    top: 10px;
                    left: 14px;
                    padding: 10px 12px;
                }}
                .camera-toolbar {{
                    top: auto;
                    bottom: 14px;
                    right: 14px;
                    flex-direction: row;
                    background: rgba(10, 20, 40, 0.90);
                    padding: 4px;
                    border-radius: 10px;
                    border: 1px solid rgba(56, 189, 248, 0.35);
                }}
            }}

            /* Pedestrian Crossing Safety Banner */
            .crossing-alert-banner {{
                position: absolute;
                bottom: 80px;
                left: 50%;
                transform: translateX(-50%);
                background: linear-gradient(135deg, rgba(8, 28, 52, 0.94) 0%, rgba(12, 38, 48, 0.95) 100%);
                border: 2px solid #10b981;
                border-radius: 12px;
                padding: 10px 20px;
                color: #ffffff;
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.75), 0 0 20px rgba(16, 185, 129, 0.4);
                display: none;
                align-items: center;
                gap: 12px;
                z-index: 15;
                animation: pulseGlow 1.5s infinite alternate ease-in-out;
            }}

            @keyframes pulseGlow {{
                0% {{ box-shadow: 0 0 10px rgba(16, 185, 129, 0.3); }}
                100% {{ box-shadow: 0 0 25px rgba(16, 185, 129, 0.65); }}
            }}

            /* Timeline & Playback Controller Bar */
            .guide-control-bar {{
                background: rgba(15, 23, 42, 0.95);
                border: 1px solid rgba(56, 189, 248, 0.3);
                border-radius: 12px;
                padding: 12px 18px;
                margin-top: 14px;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}

            .scrubber-row {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}

            .scrubber-slider {{
                flex: 1;
                -webkit-appearance: none;
                height: 8px;
                border-radius: 4px;
                background: #1e293b;
                outline: none;
                cursor: pointer;
            }}

            .scrubber-slider::-webkit-slider-thumb {{
                -webkit-appearance: none;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background: #38bdf8;
                border: 2.5px solid #ffffff;
                box-shadow: 0 0 10px rgba(56, 189, 248, 0.8);
                cursor: pointer;
            }}

            .btn-action {{
                background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
                color: #ffffff;
                border: 1px solid #38bdf8;
                border-radius: 8px;
                padding: 7px 14px;
                font-size: 0.80rem;
                font-weight: 800;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                transition: all 0.25s ease;
            }}

            .btn-action:hover {{
                background: #0284c7;
                box-shadow: 0 0 14px rgba(56, 189, 248, 0.5);
                transform: translateY(-1px);
            }}

            .btn-secondary {{
                background: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(148, 163, 184, 0.3);
                color: #cbd5e1;
            }}

            .btn-secondary:hover {{
                background: rgba(51, 65, 85, 0.9);
                color: #ffffff;
                border-color: #94a3b8;
            }}

            /* Maneuvers Step Ribbon */
            .steps-carousel {{
                display: flex;
                gap: 8px;
                overflow-x: auto;
                padding: 6px 0;
                scrollbar-width: thin;
                scrollbar-color: #0284c7 #0f172a;
            }}

            .step-chip {{
                flex-shrink: 0;
                padding: 8px 12px;
                background: rgba(15, 23, 42, 0.7);
                border: 1px solid rgba(56, 189, 248, 0.25);
                border-radius: 8px;
                font-size: 0.74rem;
                color: #cbd5e1;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                gap: 6px;
            }}

            .step-chip:hover, .step-chip.active {{
                background: rgba(2, 132, 199, 0.3);
                border-color: #38bdf8;
                color: #38bdf8;
                font-weight: 700;
            }}

            /* 2D Fallback Overlay */
            #canvas-2d-fallback {{
                display: none;
                width: 100%;
                height: 100%;
                position: absolute;
                top: 0;
                left: 0;
                background: #0f172a;
            }}
        </style>

        <!-- Top Header & Status -->
        <div class='guide-top-hud'>
            <div class='guide-brand-badge'>
                <div id='guide-avatar-orb' class='guide-avatar-orb' title='Virtual Walking Guide'>
                    🚶‍♂️
                </div>
                <div>
                    <div style='font-size: 0.95rem; font-weight: 900; color: #ffffff; display: flex; align-items: center; gap: 8px;'>
                        <span>3D VIRTUAL WALKING INSTRUCTOR</span>
                        <span style='background: rgba(16, 185, 129, 0.2); color: #34d399; font-size: 0.68rem; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.4);'>
                            ● REAL-ROUTE SYNC
                        </span>
                    </div>
                    <div style='font-size: 0.76rem; color: #94a3b8; margin-top: 2px;'>
                        Interactive 3D Pedestrian Simulation: Teaches every turn, curve, and street crossing visually
                    </div>
                </div>
            </div>

            <div style='display: flex; align-items: center; gap: 10px; flex-wrap: wrap;'>
                <div id='guide-state-badge' class='guide-state-pill state-WALKING_STRAIGHT'>
                    <span id='state-dot'>●</span> <span id='state-label'>WALKING STRAIGHT</span>
                </div>
                <button id='btn-mode-toggle' class='btn-action btn-secondary' onclick='toggleMode()' title='Switch between Practice Demonstration and Live GPS'>
                    <span id='mode-icon'>🎯</span> <span id='mode-text'>Demonstration Mode</span>
                </button>
                <button id='btn-voice-toggle' class='btn-action btn-secondary' onclick='toggleVoice()' title='Toggle Spoken Voice & Crosswalk Audio'>
                    <span id='voice-icon'>🔊</span> <span id='voice-text'>Voice: On</span>
                </button>
            </div>
        </div>

        <!-- 3D Navigation Scene Viewport -->
        <div class='viewport-3d-stage' id='viewport-stage'>
            <!-- WebGL Canvas Container -->
            <div id='webgl-container' style='width: 100%; height: 100%;'></div>

            <!-- Fallback 2D Canvas if WebGL is unavailable -->
            <canvas id='canvas-2d-fallback'></canvas>

            <!-- Floating Next-Maneuver Instruction Card -->
            <div class='floating-instruction-card' id='instruction-card'>
                <div class='maneuver-headline-row'>
                    <div id='card-icon-badge' class='maneuver-icon-badge'>⬆️</div>
                    <div style='flex: 1;'>
                        <div id='card-headline' style='font-size: 0.95rem; font-weight: 800; color: #38bdf8;'>
                            Proceed Straight along Route
                        </div>
                        <div id='card-road' style='font-size: 0.78rem; color: #cbd5e1; margin-top: 2px;'>
                            Main Pedestrian Corridor • 150m ahead
                        </div>
                    </div>
                    <div style='text-align: right;'>
                        <div id='card-distance' style='font-size: 1.15rem; font-weight: 900; color: #10b981;'>
                            150 m
                        </div>
                        <div id='card-time' style='font-size: 0.70rem; color: #94a3b8;'>
                            ~2 mins walk
                        </div>
                    </div>
                </div>

                <!-- Virtual Guide Speech Bubble -->
                <div style='margin-top: 8px; background: rgba(15, 23, 42, 0.65); border-left: 3px solid #38bdf8; border-radius: 6px; padding: 6px 10px; font-size: 0.78rem; color: #e2e8f0; line-height: 1.4;'>
                    <span style='color: #38bdf8; font-weight: 800;'>🧑‍🎓 Guide: </span>
                    <span id='card-speech'>Walking forward along the sidewalk. Keep to the right side of the path.</span>
                </div>

                <!-- Landmark & Accessibility Hints -->
                <div style='display: flex; gap: 8px; margin-top: 8px; font-size: 0.72rem; flex-wrap: wrap;'>
                    <span style='background: rgba(56, 189, 248, 0.15); color: #7dd3fc; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(56, 189, 248, 0.3);'>
                        👀 <span id='card-landmark'>Look for pedestrian signs</span>
                    </span>
                    <span style='background: rgba(16, 185, 129, 0.15); color: #6ee7b7; padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3);'>
                        ♿ <span id='card-access'>Step-free drop curb ramp</span>
                    </span>
                </div>
            </div>

            <!-- Floating Multi-Angle Camera Switcher Toolbar -->
            <div class='camera-toolbar'>
                <button id='cam-follow' class='cam-btn active' onclick='setCameraView("follow")' title='Follow Behind Virtual Guide (Third-Person)'>
                    <span>👤</span> Follow
                </button>
                <button id='cam-instructor' class='cam-btn' onclick='setCameraView("instructor")' title='Instructor Face-to-Face View'>
                    <span>🧑‍🏫</span> Instructor
                </button>
                <button id='cam-drone' class='cam-btn' onclick='setCameraView("drone")' title='Cinematic Drone Perspective'>
                    <span>🚁</span> Cinematic
                </button>
                <button id='cam-top' class='cam-btn' onclick='setCameraView("top")' title='Top-Down Bird&#39;s-Eye AR View'>
                    <span>🗺️</span> Overhead
                </button>
            </div>

            <!-- Pedestrian Crossing Safety Banner -->
            <div id='crossing-banner' class='crossing-alert-banner'>
                <div style='font-size: 24px;'>🚦</div>
                <div>
                    <div style='font-weight: 900; font-size: 0.88rem; color: #10b981;'>
                        SAFE PEDESTRIAN CROSSING IN PROGRESS
                    </div>
                    <div id='crossing-detail' style='font-size: 0.76rem; color: #e2e8f0;'>
                        Waiting at drop-curb ramp • Looking left & right • Audio walk signal active
                    </div>
                </div>
            </div>
        </div>

        <!-- Timeline & Playback Controller Bar -->
        <div class='guide-control-bar'>
            <!-- Scrubber Slider -->
            <div class='scrubber-row'>
                <button id='btn-play-pause' class='btn-action' onclick='togglePlayPause()' title='Play / Pause Demonstration'>
                    <span id='play-icon'>⏸</span> <span id='play-text'>Pause</span>
                </button>

                <button class='btn-action btn-secondary' onclick='prevManeuver()' title='Previous Step'>
                    ◀ Step
                </button>

                <input type='range' id='route-scrubber' class='scrubber-slider' min='0' max='100' value='0' oninput='onScrub(this.value)'>

                <button class='btn-action btn-secondary' onclick='nextManeuver()' title='Next Step'>
                    Step ▶
                </button>

                <button id='btn-cute-hop' class='btn-action btn-secondary' onclick='triggerCuteHop()' title='Trigger Cute Hop & Wave'>
                    ✨ Cute Hop
                </button>

                <button class='btn-action btn-secondary' onclick='restartJourney()' title='Restart from Beginning'>
                    ⏮ Restart
                </button>
            </div>

            <!-- Status & Speed Controls -->
            <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;'>
                <div style='font-size: 0.78rem; color: #cbd5e1; display: flex; align-items: center; gap: 12px;'>
                    <span>Progress: <b id='hud-progress-pct' style='color: #38bdf8;'>0%</b> (<span id='hud-station-m'>0</span> / <span id='hud-total-m'>{round(final_total_dist)}</span> m)</span>
                    <span>Walking Speed: <b id='hud-speed-val' style='color: #10b981;'>4.8 km/h</b></span>
                </div>

                <div style='display: flex; align-items: center; gap: 6px;'>
                    <span style='font-size: 0.70rem; color: #94a3b8; font-weight: 700;'>SIM SPEED:</span>
                    <button id='speed-btn-05' class='cam-btn' onclick='setSimSpeed(0.5)'>0.5x</button>
                    <button id='speed-btn-1' class='cam-btn active' onclick='setSimSpeed(1.0)'>1x</button>
                    <button id='speed-btn-2' class='cam-btn' onclick='setSimSpeed(2.0)'>2x</button>
                    <button id='speed-btn-4' class='cam-btn' onclick='setSimSpeed(4.0)'>4x</button>
                </div>
            </div>

            <!-- Steps Carousel -->
            <div class='steps-carousel' id='steps-carousel'>
                <!-- Dynamically populated via JavaScript -->
            </div>
        </div>
    </div>

    <!-- Include Three.js via CDN with resilient fallback -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

    <script>
    (function() {{
        const SCENE_PAYLOAD = {payload_json};
        const PATH_POINTS = SCENE_PAYLOAD.path_points || [];
        const MANEUVERS = SCENE_PAYLOAD.maneuvers || [];
        const TOTAL_DISTANCE_M = SCENE_PAYLOAD.total_distance_m || 200.0;

        let currentStationM = 0.0;
        let isPlaying = true;
        let simSpeedMultiplier = 1.0;
        let activeCameraMode = 'follow'; // 'follow', 'instructor', 'drone', 'top'
        let isVoiceEnabled = true;
        let isDemoMode = SCENE_PAYLOAD.is_simulation_mode;
        let lastTimestamp = performance.now();
        let currentManeuverIdx = 0;
        let lastSpokenManeuverIdx = -1;
        let gaitPhase = 0.0;
        let jumpStartTime = -1;
        const JUMP_DURATION_MS = 650;
        let animFrameId = null;
        let fallbackAnimId = null;
        const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        window.triggerCuteHop = function() {{
            const nowTime = performance.now();
            if (jumpStartTime < 0 || nowTime - jumpStartTime > JUMP_DURATION_MS + 400) {{
                jumpStartTime = nowTime;
                playSignalChime(true);
            }}
        }};

        // Three.js instances
        let scene, camera, renderer, characterGroup, roadMesh, arRibbonMesh;
        let characterLimbs = {{}};
        let crossingLightBeacon = null;
        let destinationGate = null;
        let isThreeJsReady = false;

        // Sound Synthesizer via Web Audio API for Pedestrian Signals & Turns
        let audioCtx = null;
        function playSignalChime(isWalk) {{
            if (!isVoiceEnabled) return;
            try {{
                if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const now = audioCtx.currentTime;
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(isWalk ? 880 : 440, now);
                osc.frequency.exponentialRampToValueAtTime(isWalk ? 1760 : 220, now + 0.15);
                gain.gain.setValueAtTime(0.18, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.18);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.2);
            }} catch (e) {{}}
        }}

        function speakText(text) {{
            if (!isVoiceEnabled || !('speechSynthesis' in window)) return;
            try {{
                window.speechSynthesis.cancel();
                const utter = new SpeechSynthesisUtterance(text);
                utter.rate = 1.05;
                utter.pitch = 1.0;
                window.speechSynthesis.speak(utter);
            }} catch (e) {{}}
        }}

        // Initialize 3D Engine
        function initThreeScene() {{
            const container = document.getElementById('webgl-container');
            if (!container || typeof THREE === 'undefined') {{
                init2DFallback();
                return;
            }}

            try {{
                scene = new THREE.Scene();
                scene.background = new THREE.Color(0x38bdf8);
                scene.fog = new THREE.FogExp2(0xc7d2fe, 0.0065);

                const width = container.clientWidth || 800;
                const height = container.clientHeight || 480;

                camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 1000);
                renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true, powerPreference: "high-performance" }});
                renderer.setSize(width, height);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                renderer.shadowMap.enabled = true;
                renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                container.appendChild(renderer.domElement);

                // Natural Atmosphere & Lighting
                const hemiLight = new THREE.HemisphereLight(0x7dd3fc, 0x15803d, 0.85);
                scene.add(hemiLight);

                const ambientLight = new THREE.AmbientLight(0xffffff, 0.35);
                scene.add(ambientLight);

                const dirLight = new THREE.DirectionalLight(0xfffaed, 1.3);
                dirLight.position.set(35, 65, 45);
                dirLight.castShadow = true;
                scene.add(dirLight);

                // Build Realistic Scenery (Sky Dome, Clouds, Grass Terrain, Trees)
                buildRealisticLandscape();

                // Build 3D Road along Route Spline
                build3DRoad();

                // Build Articulated 3D Humanoid Guide
                buildProceduralHumanoid();

                // Build Destination Hologram Gate
                buildDestinationGate();

                isThreeJsReady = true;

                window.addEventListener('resize', onWindowResize);
                document.addEventListener('visibilitychange', onVisibilityChange);
                animFrameId = requestAnimationFrame(animationLoop);
            }} catch (err) {{
                console.warn("WebGL initialization failed, falling back to 2D:", err);
                init2DFallback();
            }}
        }}

        // Build 3D Road, Sidewalks, and AR Navigation Ribbon
        function build3DRoad() {{
            if (!PATH_POINTS || PATH_POINTS.length < 2) return;

            const curvePoints = PATH_POINTS.map(p => new THREE.Vector3(p.x, p.y, p.z));
            const spline = new THREE.CatmullRomCurve3(curvePoints);

            // Road surface
            const roadGeo = new THREE.TubeGeometry(spline, PATH_POINTS.length * 3, 2.8, 8, false);
            const roadMat = new THREE.MeshStandardMaterial({{
                color: 0x1e293b,
                roughness: 0.85,
                metalness: 0.15
            }});
            roadMesh = new THREE.Mesh(roadGeo, roadMat);
            roadMesh.receiveShadow = true;
            roadMesh.scale.set(1, 0.08, 1); // Flatten into road plane
            scene.add(roadMesh);

            // Glowing AR Trajectory Ribbon Carpet
            const ribbonGeo = new THREE.TubeGeometry(spline, PATH_POINTS.length * 3, 0.45, 6, false);
            const ribbonMat = new THREE.MeshBasicMaterial({{
                color: 0x00f2fe,
                transparent: true,
                opacity: 0.75,
                wireframe: false
            }});
            arRibbonMesh = new THREE.Mesh(ribbonGeo, ribbonMat);
            arRibbonMesh.position.y = 0.12;
            scene.add(arRibbonMesh);

            // Sidewalk Curbs along Road
            const curbLeftGeo = new THREE.TubeGeometry(spline, PATH_POINTS.length * 2, 0.35, 6, false);
            const curbMat = new THREE.MeshStandardMaterial({{ color: 0x94a3b8, roughness: 0.8 }});
            const curbLeft = new THREE.Mesh(curbLeftGeo, curbMat);
            curbLeft.position.set(-2.6, 0.15, 0);
            scene.add(curbLeft);

            const curbRight = new THREE.Mesh(curbLeftGeo, curbMat);
            curbRight.position.set(2.6, 0.15, 0);
            scene.add(curbRight);

            // Place Zebra Crossings & Tactile Paving at Junction Maneuvers
            MANEUVERS.forEach((m, idx) => {{
                if (m.has_crossing) {{
                    const stationPos = getPointAtStation(m.junction_station_m);
                    if (stationPos) {{
                        buildZebraCrossing(stationPos.x, stationPos.y + 0.08, stationPos.z, stationPos.b);
                    }}
                }}
            }});
        }}

        // Build Realistic Outdoor Landscape (Sky Dome, Sun, Ground Lawn, Foliage)
        function buildRealisticLandscape() {{
            function makeSkyTex(topHex, midHex, botHex) {{
                const sc = document.createElement('canvas');
                sc.width = 128; sc.height = 256;
                const sctx = sc.getContext('2d');
                const grad = sctx.createLinearGradient(0, 0, 0, 256);
                grad.addColorStop(0.0, topHex);
                grad.addColorStop(0.55, midHex);
                grad.addColorStop(1.0, botHex);
                sctx.fillStyle = grad;
                sctx.fillRect(0, 0, 128, 256);
                const tex = new THREE.CanvasTexture(sc);
                tex.generateMipmaps = false;
                tex.minFilter = THREE.LinearFilter;
                return tex;
            }}

            const skyGeo = new THREE.SphereGeometry(320, 32, 16);
            const skyMat = new THREE.MeshBasicMaterial({{
                map: makeSkyTex('#1d4ed8', '#38bdf8', '#e0f2fe'),
                side: THREE.BackSide
            }});
            const skyMesh = new THREE.Mesh(skyGeo, skyMat);
            scene.add(skyMesh);

            // Sun
            const sunGeo = new THREE.CircleGeometry(8.0, 24);
            const sunMat = new THREE.MeshBasicMaterial({{ color: 0xfffae0, side: THREE.DoubleSide }});
            const sunMesh = new THREE.Mesh(sunGeo, sunMat);
            sunMesh.position.set(50, 80, 140);
            sunMesh.lookAt(0, 0, 0);
            scene.add(sunMesh);

            // Grass Ground Plane
            function makeGrassTex() {{
                const gc = document.createElement('canvas');
                gc.width = 256; gc.height = 256;
                const gctx = gc.getContext('2d');
                gctx.fillStyle = '#2d6a2e';
                gctx.fillRect(0, 0, 256, 256);
                for (let i = 0; i < 600; i++) {{
                    const gx = Math.random() * 256;
                    const gy = Math.random() * 256;
                    gctx.fillStyle = Math.random() > 0.5 ? 'rgba(54, 138, 56, 0.45)' : 'rgba(28, 77, 30, 0.45)';
                    gctx.beginPath();
                    gctx.arc(gx, gy, 2 + Math.random() * 4, 0, Math.PI * 2);
                    gctx.fill();
                }}
                const tex = new THREE.CanvasTexture(gc);
                tex.wrapS = THREE.RepeatWrapping;
                tex.wrapT = THREE.RepeatWrapping;
                tex.repeat.set(40, 40);
                return tex;
            }}

            const groundGeo = new THREE.PlaneGeometry(500, 500, 16, 16);
            const groundMat = new THREE.MeshStandardMaterial({{
                map: makeGrassTex(),
                roughness: 0.95,
                metalness: 0.05
            }});
            const groundMesh = new THREE.Mesh(groundGeo, groundMat);
            groundMesh.rotation.x = -Math.PI / 2;
            groundMesh.position.y = -0.06;
            groundMesh.receiveShadow = true;
            scene.add(groundMesh);

            // Roadside Trees along PATH_POINTS
            if (PATH_POINTS && PATH_POINTS.length >= 2) {{
                const trunkMat = new THREE.MeshStandardMaterial({{ color: 0x4a2e18, roughness: 0.9 }});
                const greenMats = [
                    new THREE.MeshStandardMaterial({{ color: 0x15803d, roughness: 0.82 }}),
                    new THREE.MeshStandardMaterial({{ color: 0x16a34a, roughness: 0.85 }}),
                    new THREE.MeshStandardMaterial({{ color: 0x14532d, roughness: 0.90 }})
                ];
                for (let i = 0; i < PATH_POINTS.length; i += 3) {{
                    const pt = PATH_POINTS[i];
                    [-6.5, 6.5].forEach((offset, sIdx) => {{
                        const tree = new THREE.Group();
                        tree.position.set(pt.x + offset + (Math.random() - 0.5) * 2, 0, pt.z + (Math.random() - 0.5) * 2);
                        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.22, 2.0, 8), trunkMat);
                        trunk.position.y = 1.0;
                        tree.add(trunk);
                        const crown = new THREE.Mesh(new THREE.DodecahedronGeometry(1.5, 1), greenMats[(i + sIdx) % greenMats.length]);
                        crown.position.y = 2.8;
                        crown.castShadow = true;
                        tree.add(crown);
                        scene.add(tree);
                    }});
                }}
            }}
        }}

        function buildZebraCrossing(x, y, z, bearing) {{
            const crossGroup = new THREE.Group();
            crossGroup.position.set(x, y, z);
            crossGroup.rotation.y = -THREE.MathUtils.degToRad(bearing);

            // White zebra stripes
            const stripeMat = new THREE.MeshBasicMaterial({{ color: 0xffffff }});
            for (let i = -3; i <= 3; i++) {{
                const stripeGeo = new THREE.BoxGeometry(0.5, 0.04, 2.6);
                const stripe = new THREE.Mesh(stripeGeo, stripeMat);
                stripe.position.set(i * 0.75, 0, 0);
                crossGroup.add(stripe);
            }}

            // Yellow tactile blister warning paving on curb drops
            const tactileMat = new THREE.MeshBasicMaterial({{ color: 0xfacc15 }});
            const tactileLeft = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.06, 2.8), tactileMat);
            tactileLeft.position.set(-3.2, 0.02, 0);
            crossGroup.add(tactileLeft);

            const tactileRight = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.06, 2.8), tactileMat);
            tactileRight.position.set(3.2, 0.02, 0);
            crossGroup.add(tactileRight);

            // Pedestrian Signal Post
            const poleGeo = new THREE.CylinderGeometry(0.06, 0.06, 3.2, 8);
            const poleMat = new THREE.MeshStandardMaterial({{ color: 0x334155 }});
            const pole = new THREE.Mesh(poleGeo, poleMat);
            pole.position.set(3.2, 1.6, 1.4);
            crossGroup.add(pole);

            // Signal Box
            const boxGeo = new THREE.BoxGeometry(0.35, 0.7, 0.3);
            const boxMat = new THREE.MeshStandardMaterial({{ color: 0x0f172a }});
            const signalBox = new THREE.Mesh(boxGeo, boxMat);
            signalBox.position.set(3.2, 2.8, 1.4);
            crossGroup.add(signalBox);

            // Walk Light Glow
            const lightGeo = new THREE.SphereGeometry(0.12, 12, 12);
            const lightMat = new THREE.MeshBasicMaterial({{ color: 0x10b981 }});
            const walkLight = new THREE.Mesh(lightGeo, lightMat);
            walkLight.position.set(3.2, 2.7, 1.25);
            crossGroup.add(walkLight);

            scene.add(crossGroup);
        }}

        // Build Cute, Friendly Articulated 3D Humanoid Campus Guide
        function buildProceduralHumanoid() {{
            characterGroup = new THREE.Group();

            // Curated harmonious aesthetic materials
            const skinMat = new THREE.MeshStandardMaterial({{ color: 0xffdbb4, roughness: 0.55 }});
            const hairMat = new THREE.MeshStandardMaterial({{ color: 0x382216, roughness: 0.75 }});
            const jacketMat = new THREE.MeshStandardMaterial({{ color: 0x0284c7, roughness: 0.6, metalness: 0.08 }});
            const collarWhiteMat = new THREE.MeshStandardMaterial({{ color: 0xf8fafc, roughness: 0.4 }});
            const pantsMat = new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.7 }});
            const backpackMat = new THREE.MeshStandardMaterial({{ color: 0xd97706, roughness: 0.65 }});
            const strapMat = new THREE.MeshStandardMaterial({{ color: 0x334155, roughness: 0.8 }});
            const sneakerMat = new THREE.MeshStandardMaterial({{ color: 0x2563eb, roughness: 0.5 }});
            const soleWhiteMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, roughness: 0.3 }});
            const eyeWhiteMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, roughness: 0.2 }});
            const pupilMat = new THREE.MeshStandardMaterial({{ color: 0x0f172a, roughness: 0.1 }});
            const catchlightMat = new THREE.MeshBasicMaterial({{ color: 0xffffff }});
            const cheekMat = new THREE.MeshBasicMaterial({{ color: 0xf472b6, transparent: true, opacity: 0.55 }});
            const mouthMat = new THREE.MeshBasicMaterial({{ color: 0x9f1239 }});
            const cyanAccentMat = new THREE.MeshBasicMaterial({{ color: 0x38bdf8 }});

            // 1. Pelvis (Root Joint)
            const pelvis = new THREE.Group();
            pelvis.position.y = 0.95;
            characterGroup.add(pelvis);
            characterLimbs.pelvis = pelvis;

            // 2. Torso with Campus Explorer Jacket
            const torso = new THREE.Group();
            const jacketMesh = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.56, 0.26), jacketMat);
            jacketMesh.castShadow = true;
            torso.add(jacketMesh);

            // Inner white collar & zipper line
            const collar = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.07, 0.28), collarWhiteMat);
            collar.position.set(0, 0.26, 0);
            torso.add(collar);

            const zipperLine = new THREE.Mesh(new THREE.BoxGeometry(0.022, 0.46, 0.27), collarWhiteMat);
            zipperLine.position.set(0, 0.0, 0.01);
            torso.add(zipperLine);

            // Glowing Navigator Compass Chest Pin
            const compassBadge = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.02, 16), cyanAccentMat);
            compassBadge.rotation.x = Math.PI / 2;
            compassBadge.position.set(0.12, 0.12, 0.14);
            torso.add(compassBadge);

            // Student Mini-Backpack
            const backpack = new THREE.Group();
            backpack.position.set(0, 0.04, -0.19);
            const bpBody = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.36, 0.15), backpackMat);
            bpBody.castShadow = true;
            backpack.add(bpBody);

            const bpPocket = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.18, 0.06), backpackMat);
            bpPocket.position.set(0, -0.06, -0.10);
            backpack.add(bpPocket);

            // Shoulder Straps wrapping over jacket
            const strapL = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.44, 0.28), strapMat);
            strapL.position.set(-0.12, 0.06, 0.06);
            backpack.add(strapL);

            const strapR = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.44, 0.28), strapMat);
            strapR.position.set(0.12, 0.06, 0.06);
            backpack.add(strapR);

            torso.add(backpack);
            pelvis.add(torso);
            characterLimbs.torso = torso;

            // 3. Cute Expressive Human Head
            const headGroup = new THREE.Group();
            headGroup.position.y = 0.48;

            // Rounded cute face
            const headMesh = new THREE.Mesh(new THREE.SphereGeometry(0.19, 24, 24), skinMat);
            headMesh.castShadow = true;
            headGroup.add(headMesh);

            // Soft styled hair fringe
            const hairBack = new THREE.Mesh(new THREE.SphereGeometry(0.20, 20, 20, 0, Math.PI * 2, 0, Math.PI * 0.55), hairMat);
            hairBack.rotation.x = -0.15;
            headGroup.add(hairBack);

            const hairFringe = new THREE.Mesh(new THREE.ConeGeometry(0.065, 0.12, 6), hairMat);
            hairFringe.rotation.set(-0.6, 0.2, -0.4);
            hairFringe.position.set(-0.06, 0.12, 0.16);
            headGroup.add(hairFringe);

            // Campus Explorer Cap
            const capMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.19, 0.20, 0.07, 20), jacketMat);
            capMesh.position.y = 0.14;
            headGroup.add(capMesh);

            const capBrim = new THREE.Mesh(new THREE.CylinderGeometry(0.21, 0.21, 0.02, 20, 1, false, 0, Math.PI), jacketMat);
            capBrim.position.set(0, 0.12, 0.08);
            capBrim.rotation.x = 0.15;
            headGroup.add(capBrim);

            // Expressive Eyes (Left & Right)
            const eyeWhiteGeo = new THREE.SphereGeometry(0.042, 16, 16);
            const eyeWhiteL = new THREE.Mesh(eyeWhiteGeo, eyeWhiteMat);
            eyeWhiteL.scale.set(1.0, 1.25, 0.35);
            eyeWhiteL.position.set(-0.072, 0.02, 0.172);
            headGroup.add(eyeWhiteL);

            const eyeWhiteR = new THREE.Mesh(eyeWhiteGeo, eyeWhiteMat);
            eyeWhiteR.scale.set(1.0, 1.25, 0.35);
            eyeWhiteR.position.set(0.072, 0.02, 0.172);
            headGroup.add(eyeWhiteR);

            // Dark Pupils
            const pupilGeo = new THREE.SphereGeometry(0.024, 12, 12);
            const pupilL = new THREE.Mesh(pupilGeo, pupilMat);
            pupilL.scale.set(1.0, 1.15, 0.4);
            pupilL.position.set(-0.072, 0.02, 0.185);
            headGroup.add(pupilL);

            const pupilR = new THREE.Mesh(pupilGeo, pupilMat);
            pupilR.scale.set(1.0, 1.15, 0.4);
            pupilR.position.set(0.072, 0.02, 0.185);
            headGroup.add(pupilR);

            // Catchlight Specular Reflections (Brings Eyes to Life!)
            const catchlightGeo = new THREE.SphereGeometry(0.009, 8, 8);
            const catchlightL = new THREE.Mesh(catchlightGeo, catchlightMat);
            catchlightL.position.set(-0.062, 0.032, 0.194);
            headGroup.add(catchlightL);

            const catchlightR = new THREE.Mesh(catchlightGeo, catchlightMat);
            catchlightR.position.set(0.082, 0.032, 0.194);
            headGroup.add(catchlightR);

            // Eyelids for Procedural Blinking
            const eyelidGeo = new THREE.SphereGeometry(0.046, 14, 14, 0, Math.PI * 2, 0, Math.PI * 0.5);
            const eyelidL = new THREE.Mesh(eyelidGeo, skinMat);
            eyelidL.position.set(-0.072, 0.02, 0.174);
            eyelidL.rotation.x = Math.PI;
            eyelidL.scale.set(1.05, 0.05, 0.5);
            headGroup.add(eyelidL);

            const eyelidR = new THREE.Mesh(eyelidGeo, skinMat);
            eyelidR.position.set(0.072, 0.02, 0.174);
            eyelidR.rotation.x = Math.PI;
            eyelidR.scale.set(1.05, 0.05, 0.5);
            headGroup.add(eyelidR);

            characterLimbs.leftEyelid = eyelidL;
            characterLimbs.rightEyelid = eyelidR;

            // Rosy Blushing Cheeks
            const cheekGeo = new THREE.SphereGeometry(0.032, 12, 12);
            const cheekL = new THREE.Mesh(cheekGeo, cheekMat);
            cheekL.scale.set(1.2, 0.65, 0.2);
            cheekL.position.set(-0.11, -0.04, 0.155);
            headGroup.add(cheekL);

            const cheekR = new THREE.Mesh(cheekGeo, cheekMat);
            cheekR.scale.set(1.2, 0.65, 0.2);
            cheekR.position.set(0.11, -0.04, 0.155);
            headGroup.add(cheekR);

            // Friendly Natural Smile
            const smileMesh = new THREE.Mesh(new THREE.TorusGeometry(0.038, 0.009, 8, 16, Math.PI * 0.75), mouthMat);
            smileMesh.rotation.set(0, 0, Math.PI * 1.12);
            smileMesh.position.set(0, -0.07, 0.175);
            headGroup.add(smileMesh);

            torso.add(headGroup);
            characterLimbs.head = headGroup;

            // 4. Arms with Natural Joints & Hands
            function makeArm(isLeft) {{
                const shoulderGroup = new THREE.Group();
                const sign = isLeft ? -1 : 1;
                shoulderGroup.position.set(sign * 0.28, 0.22, 0);

                const upperArm = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.048, 0.32, 12), jacketMat);
                upperArm.position.y = -0.16;
                upperArm.castShadow = true;
                shoulderGroup.add(upperArm);

                const elbowGroup = new THREE.Group();
                elbowGroup.position.y = -0.32;

                const forearm = new THREE.Mesh(new THREE.CylinderGeometry(0.048, 0.042, 0.28, 12), skinMat);
                forearm.position.y = -0.14;
                forearm.castShadow = true;
                elbowGroup.add(forearm);

                // Rounded Hand with thumb
                const hand = new THREE.Mesh(new THREE.SphereGeometry(0.052, 12, 12), skinMat);
                hand.position.y = -0.30;
                hand.scale.set(1.0, 1.2, 0.7);
                elbowGroup.add(hand);

                const thumb = new THREE.Mesh(new THREE.SphereGeometry(0.022, 8, 8), skinMat);
                thumb.position.set(sign * -0.038, -0.28, 0.02);
                elbowGroup.add(thumb);

                shoulderGroup.add(elbowGroup);
                return {{ shoulder: shoulderGroup, elbow: elbowGroup, hand: hand }};
            }}

            characterLimbs.leftArm = makeArm(true);
            torso.add(characterLimbs.leftArm.shoulder);

            characterLimbs.rightArm = makeArm(false);
            torso.add(characterLimbs.rightArm.shoulder);

            // 5. Legs with Joggers & Two-Tone Sneakers
            function makeLeg(isLeft) {{
                const hipGroup = new THREE.Group();
                const sign = isLeft ? -1 : 1;
                hipGroup.position.set(sign * 0.14, -0.10, 0);

                const thigh = new THREE.Mesh(new THREE.CylinderGeometry(0.078, 0.065, 0.44, 12), pantsMat);
                thigh.position.y = -0.22;
                thigh.castShadow = true;
                hipGroup.add(thigh);

                const kneeGroup = new THREE.Group();
                kneeGroup.position.y = -0.44;

                const shin = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.055, 0.42, 12), pantsMat);
                shin.position.y = -0.21;
                shin.castShadow = true;
                kneeGroup.add(shin);

                // Two-tone Campus Sneakers (blue upper + crisp white rubber sole)
                const sneakerBody = new THREE.Mesh(new THREE.BoxGeometry(0.115, 0.075, 0.22), sneakerMat);
                sneakerBody.position.set(0, -0.39, 0.05);
                sneakerBody.castShadow = true;
                kneeGroup.add(sneakerBody);

                const sneakerSole = new THREE.Mesh(new THREE.BoxGeometry(0.125, 0.032, 0.24), soleWhiteMat);
                sneakerSole.position.set(0, -0.43, 0.05);
                sneakerSole.receiveShadow = true;
                kneeGroup.add(sneakerSole);

                hipGroup.add(kneeGroup);
                return {{ hip: hipGroup, knee: kneeGroup, foot: sneakerBody, sole: sneakerSole }};
            }}

            characterLimbs.leftLeg = makeLeg(true);
            pelvis.add(characterLimbs.leftLeg.hip);

            characterLimbs.rightLeg = makeLeg(false);
            pelvis.add(characterLimbs.rightLeg.hip);

            // 6. Ground Radar Aura Ring below character
            const auraGeo = new THREE.RingGeometry(0.4, 0.65, 24);
            const auraMat = new THREE.MeshBasicMaterial({{
                color: 0x10b981,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.6
            }});
            const aura = new THREE.Mesh(auraGeo, auraMat);
            aura.rotation.x = Math.PI / 2;
            aura.position.y = 0.03;
            characterGroup.add(aura);

            scene.add(characterGroup);
        }}

        // Build Destination Holographic Gate / Landmark
        function buildDestinationGate() {{
            if (!PATH_POINTS || PATH_POINTS.length === 0) return;
            const endPt = PATH_POINTS[PATH_POINTS.length - 1];

            destinationGate = new THREE.Group();
            destinationGate.position.set(endPt.x, 0, endPt.z);

            // Floating Golden Pin Beacon
            const pinGeo = new THREE.ConeGeometry(0.6, 1.8, 16);
            const pinMat = new THREE.MeshStandardMaterial({{
                color: 0xfacc15,
                metalness: 0.8,
                roughness: 0.2,
                emissive: 0xf59e0b,
                emissiveIntensity: 0.4
            }});
            const pin = new THREE.Mesh(pinGeo, pinMat);
            pin.rotation.x = Math.PI;
            pin.position.y = 3.2;
            destinationGate.add(pin);

            // Rotating Halo Rings
            const ringGeo = new THREE.TorusGeometry(1.2, 0.06, 8, 24);
            const ringMat = new THREE.MeshBasicMaterial({{ color: 0xfde047 }});
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.rotation.x = Math.PI / 2;
            ring.position.y = 2.4;
            destinationGate.add(ring);
            destinationGate.ring = ring;

            scene.add(destinationGate);
        }}

        // Spline Station Locator
        function getPointAtStation(s) {{
            if (!PATH_POINTS || PATH_POINTS.length === 0) return null;
            if (s <= 0) return PATH_POINTS[0];
            if (s >= TOTAL_DISTANCE_M) return PATH_POINTS[PATH_POINTS.length - 1];

            for (let i = 0; i < PATH_POINTS.length - 1; i++) {{
                const p1 = PATH_POINTS[i];
                const p2 = PATH_POINTS[i + 1];
                if (p1.s <= s && s <= p2.s) {{
                    const segLen = p2.s - p1.s;
                    const t = segLen > 0.001 ? (s - p1.s) / segLen : 0;
                    return {{
                        x: p1.x + t * (p2.x - p1.x),
                        y: p1.y + t * (p2.y - p1.y),
                        z: p1.z + t * (p2.z - p1.z),
                        b: p1.b + t * (p2.b - p1.b),
                        tx: p1.tx + t * (p2.tx - p1.tx),
                        tz: p1.tz + t * (p2.tz - p1.tz),
                        curv: p1.curv || 0
                    }};
                }}
            }}
            return PATH_POINTS[PATH_POINTS.length - 1];
        }}

        // Evaluates active maneuver & UI updates
        function updateNavigationState() {{
            let activeIdx = 0;
            for (let i = 0; i < MANEUVERS.length; i++) {{
                if (MANEUVERS[i].start_station_m <= currentStationM && currentStationM <= MANEUVERS[i].end_station_m) {{
                    activeIdx = i;
                    break;
                }}
            }}
            currentManeuverIdx = activeIdx;
            const m = MANEUVERS[activeIdx] || MANEUVERS[0];

            const distRemaining = Math.max(0, m.end_station_m - currentStationM);
            const totalRemaining = Math.max(0, TOTAL_DISTANCE_M - currentStationM);

            // Determine State
            let stateName = 'WALKING_STRAIGHT';
            let stateLabel = 'WALKING STRAIGHT';
            let crossingActive = false;

            if (currentStationM >= TOTAL_DISTANCE_M - 2.5) {{
                stateName = 'ARRIVED';
                stateLabel = 'ARRIVED AT DESTINATION 🏁';
            }} else if (currentStationM >= TOTAL_DISTANCE_M - 12.0) {{
                stateName = 'ARRIVING';
                stateLabel = 'ARRIVING AT TERMINAL';
            }} else if (m.has_crossing && distRemaining <= 8.0 && distRemaining >= -3.0) {{
                crossingActive = true;
                if (distRemaining > 3.0) {{
                    stateName = 'WAITING_AT_CROSSING';
                    stateLabel = 'CHECKING PEDESTRIAN CROSSING 🚦';
                }} else {{
                    stateName = 'CROSSING';
                    stateLabel = 'CROSSING ZEBRA SAFELY 🚶‍♂️';
                }}
            }} else if (m.direction_type.includes('LEFT') && distRemaining <= 16.0) {{
                stateName = distRemaining > 3.5 ? 'APPROACHING_TURN' : 'TURNING_LEFT';
                stateLabel = distRemaining > 3.5 ? 'APPROACHING LEFT TURN' : 'TURNING LEFT ⬅️';
            }} else if (m.direction_type.includes('RIGHT') && distRemaining <= 16.0) {{
                stateName = distRemaining > 3.5 ? 'APPROACHING_TURN' : 'TURNING_RIGHT';
                stateLabel = distRemaining > 3.5 ? 'APPROACHING RIGHT TURN' : 'TURNING RIGHT ➡️';
            }} else if (!isPlaying) {{
                stateName = 'PAUSED';
                stateLabel = 'GUIDE PAUSED';
            }}

            // Update DOM State Pill
            const stateBadge = document.getElementById('guide-state-badge');
            const stateLabelEl = document.getElementById('state-label');
            if (stateBadge && stateLabelEl) {{
                stateBadge.className = 'guide-state-pill state-' + stateName;
                stateLabelEl.innerText = stateLabel;
            }}

            // Update Floating Card
            const cardHeadline = document.getElementById('card-headline');
            const cardRoad = document.getElementById('card-road');
            const cardDist = document.getElementById('card-distance');
            const cardTime = document.getElementById('card-time');
            const cardSpeech = document.getElementById('card-speech');
            const cardIcon = document.getElementById('card-icon-badge');
            const cardLandmark = document.getElementById('card-landmark');
            const cardAccess = document.getElementById('card-access');

            if (cardHeadline) cardHeadline.innerText = m.headline || m.instruction_text;
            if (cardRoad) cardRoad.innerText = (m.road_name || 'Corridor') + ' • ' + Math.round(distRemaining) + 'm ahead';
            if (cardDist) cardDist.innerText = Math.round(distRemaining) + ' m';
            if (cardTime) cardTime.innerText = '~' + Math.max(1, Math.round(distRemaining / 75)) + ' min walk';
            if (cardSpeech) cardSpeech.innerText = m.spoken_instruction || m.instruction_text;
            if (cardIcon) cardIcon.innerText = m.icon || '⬆️';
            if (cardLandmark) cardLandmark.innerText = m.what_to_look_for || 'Look for pedestrian signs';
            if (cardAccess) cardAccess.innerText = m.accessible_guidance || 'Step-free accessible ramp';

            // Crossing Banner
            const crossBanner = document.getElementById('crossing-banner');
            if (crossBanner) {{
                crossBanner.style.display = crossingActive ? 'flex' : 'none';
            }}

            // Trigger Voice / Chimes on New Maneuver
            if (activeIdx !== lastSpokenManeuverIdx) {{
                lastSpokenManeuverIdx = activeIdx;
                if (crossingActive) playSignalChime(true);
                speakText(m.spoken_instruction || m.headline);
            }}

            // Update Scrubber & HUD
            const scrubber = document.getElementById('route-scrubber');
            const pctEl = document.getElementById('hud-progress-pct');
            const stationEl = document.getElementById('hud-station-m');
            const pct = Math.min(100, Math.round((currentStationM / TOTAL_DISTANCE_M) * 100));

            if (scrubber) scrubber.value = pct;
            if (pctEl) pctEl.innerText = pct + '%';
            if (stationEl) stationEl.innerText = Math.round(currentStationM);

            // Update active chip
            const chips = document.querySelectorAll('.step-chip');
            chips.forEach((c, idx) => {{
                if (idx === activeIdx) c.classList.add('active');
                else c.classList.remove('active');
            }});

            return stateName;
        }}

        // Main Animation Loop
        function animationLoop(timestamp) {{
            const root = document.getElementById('walking-guide-3d-root');
            if (!root || !root.isConnected) {{
                // DOM node unmounted/re-rendered: perform full resource cleanup
                cleanupThreeScene();
                return;
            }}

            if (document.hidden) {{
                // Pause animation loop while tab is hidden to prevent CPU/GPU drain
                animFrameId = null;
                return;
            }}

            animFrameId = requestAnimationFrame(animationLoop);

            const dt = Math.min((timestamp - lastTimestamp) / 1000.0, 0.1);
            lastTimestamp = timestamp;

            const stateName = updateNavigationState();

            // Determine Walking Speed based on State & Simulation Mode
            let currentSpeedMps = 1.35 * simSpeedMultiplier;
            if (!isPlaying || stateName === 'PAUSED' || stateName === 'ARRIVED') {{
                currentSpeedMps = 0.0;
            }} else if (stateName === 'WAITING_AT_CROSSING') {{
                currentSpeedMps = 0.0;
            }} else if (stateName === 'TURNING_LEFT' || stateName === 'TURNING_RIGHT') {{
                currentSpeedMps = 0.75 * simSpeedMultiplier;
            }} else if (stateName === 'APPROACHING_TURN' || stateName === 'ARRIVING') {{
                currentSpeedMps = 0.90 * simSpeedMultiplier;
            }}

            // Advance Character Station along path
            if (isPlaying && currentSpeedMps > 0.0 && currentStationM < TOTAL_DISTANCE_M) {{
                currentStationM = Math.min(TOTAL_DISTANCE_M, currentStationM + currentSpeedMps * dt);
            }}

            // Advance Gait Cycle
            if (currentSpeedMps > 0.0) {{
                gaitPhase += dt * (currentSpeedMps / 1.35) * 8.5;
            }}

            const pos = getPointAtStation(currentStationM);
            if (pos && characterGroup) {{
                // Update Character Position & Rotation
                characterGroup.position.set(pos.x, pos.y, pos.z);
                const targetYaw = -THREE.MathUtils.degToRad(pos.b);
                characterGroup.rotation.y = THREE.MathUtils.lerp(characterGroup.rotation.y, targetYaw, 0.15);

                // Articulate Character Limbs with Biomechanical Walking Cycle
                animateCharacterLimbs(stateName, currentSpeedMps);

                // Update Camera to follow guide
                updateCameraFollow(pos);
            }}

            // Rotate Destination Gate Halo
            if (destinationGate && destinationGate.ring) {{
                destinationGate.ring.rotation.z += dt * 0.8;
            }}

            if (renderer && scene && camera) {{
                renderer.render(scene, camera);
            }}
        }}

        // Articulates Pelvis, Torso, Head, Eyelids, Legs, and Arms for natural human walking, turning, jumping, and idling
        function animateCharacterLimbs(stateName, speed) {{
            if (!characterLimbs.pelvis) return;

            const now = performance.now();
            const isMoving = speed > 0.05;

            // 1. Procedural Natural Blinking (Quick 140ms blink every 3.5s)
            const blinkPhase = (now % 3500);
            const isBlinking = blinkPhase < 140;
            const targetEyelidScale = isBlinking ? 1.05 : 0.05;
            if (characterLimbs.leftEyelid && characterLimbs.rightEyelid) {{
                characterLimbs.leftEyelid.scale.y = THREE.MathUtils.lerp(characterLimbs.leftEyelid.scale.y, targetEyelidScale, 0.4);
                characterLimbs.rightEyelid.scale.y = THREE.MathUtils.lerp(characterLimbs.rightEyelid.scale.y, targetEyelidScale, 0.4);
            }}

            // 2. Cute Hop / Jumping Sequence (Anticipation -> Spring -> Apex -> Cushioned Landing)
            let isJumping = false;
            let jumpT = 0.0;
            if (jumpStartTime > 0) {{
                const elapsed = now - jumpStartTime;
                if (elapsed < JUMP_DURATION_MS) {{
                    isJumping = true;
                    jumpT = elapsed / JUMP_DURATION_MS;
                }} else {{
                    jumpStartTime = -1;
                }}
            }}

            if (isJumping) {{
                let jumpY = 0.95;
                let kneeFlex = 0.0;
                let armLift = 0.0;

                if (jumpT < 0.2) {{
                    // Phase 1: Anticipation crouch
                    const crouchProg = jumpT / 0.2;
                    jumpY = 0.95 - 0.08 * crouchProg;
                    kneeFlex = 0.40 * crouchProg;
                    armLift = 0.30 * crouchProg;
                    characterLimbs.leftArm.shoulder.rotation.x = armLift;
                    characterLimbs.rightArm.shoulder.rotation.x = armLift;
                }} else if (jumpT < 0.65) {{
                    // Phase 2 & 3: Spring upward & Airborne apex with tucked knees
                    const flightProg = (jumpT - 0.2) / 0.45;
                    const sinArc = Math.sin(flightProg * Math.PI);
                    jumpY = 0.95 + 0.26 * sinArc;
                    kneeFlex = 0.50 * sinArc;
                    // Joyful cheer arms during apex
                    characterLimbs.leftArm.shoulder.rotation.x = -1.8 * sinArc;
                    characterLimbs.leftArm.shoulder.rotation.z = -0.5 * sinArc;
                    characterLimbs.rightArm.shoulder.rotation.x = -1.8 * sinArc;
                    characterLimbs.rightArm.shoulder.rotation.z = 0.5 * sinArc;
                    characterLimbs.head.rotation.x = -0.15 * sinArc;
                }} else {{
                    // Phase 4: Soft landing compression & settle
                    const landProg = (jumpT - 0.65) / 0.35;
                    const sinCompress = Math.sin(landProg * Math.PI);
                    jumpY = 0.95 - 0.06 * sinCompress;
                    kneeFlex = 0.35 * sinCompress;
                    characterLimbs.leftArm.shoulder.rotation.x = 0.1 * sinCompress;
                    characterLimbs.rightArm.shoulder.rotation.x = 0.1 * sinCompress;
                    characterLimbs.leftArm.shoulder.rotation.z = 0.1;
                    characterLimbs.rightArm.shoulder.rotation.z = -0.1;
                    characterLimbs.head.rotation.x = 0;
                }}

                characterLimbs.pelvis.position.y = jumpY;
                characterLimbs.leftLeg.hip.rotation.x = kneeFlex * 0.5;
                characterLimbs.rightLeg.hip.rotation.x = kneeFlex * 0.5;
                characterLimbs.leftLeg.knee.rotation.x = kneeFlex;
                characterLimbs.rightLeg.knee.rotation.x = kneeFlex;
                return;
            }}

            // 3. Biomechanical Walking vs Balanced Standing Idle
            if (isMoving) {{
                // Natural alternating leg swings (Hip flexion/extension)
                const hipSwingAmp = 0.65;
                const kneeFlexAmp = 0.75;

                const leftHipAngle = Math.sin(gaitPhase) * hipSwingAmp;
                const rightHipAngle = Math.sin(gaitPhase + Math.PI) * hipSwingAmp;

                characterLimbs.leftLeg.hip.rotation.x = leftHipAngle;
                characterLimbs.rightLeg.hip.rotation.x = rightHipAngle;

                // Knee flexes naturally during backward swing & foot recovery
                characterLimbs.leftLeg.knee.rotation.x = Math.max(0, -Math.sin(gaitPhase - 0.4) * kneeFlexAmp);
                characterLimbs.rightLeg.knee.rotation.x = Math.max(0, -Math.sin(gaitPhase + Math.PI - 0.4) * kneeFlexAmp);

                // Pelvis vertical bounce (2x gait phase frequency) & subtle lateral sway
                characterLimbs.pelvis.position.y = 0.95 + Math.abs(Math.sin(gaitPhase * 2)) * 0.045;
                characterLimbs.pelvis.position.x = Math.sin(gaitPhase) * 0.012;

                // Torso lateral counter-rotation opposing the hip swing
                characterLimbs.torso.rotation.y = -Math.sin(gaitPhase) * 0.10;
                characterLimbs.torso.scale.set(1.0, 1.0, 1.0);
            }} else {{
                // Balanced Standing Idle: subtle breathing bob & relaxed limbs
                const breathVal = Math.sin(now * 0.0022);
                characterLimbs.pelvis.position.y = 0.95 + breathVal * 0.012;
                characterLimbs.pelvis.position.x = 0;

                // Gentle chest expansion with breathing
                const chestScale = 1.0 + breathVal * 0.01;
                characterLimbs.torso.scale.set(chestScale, 1.0, chestScale);
                characterLimbs.torso.rotation.y = 0;

                // Relaxed leg stance
                characterLimbs.leftLeg.hip.rotation.x = 0;
                characterLimbs.rightLeg.hip.rotation.x = 0;
                characterLimbs.leftLeg.knee.rotation.x = 0;
                characterLimbs.rightLeg.knee.rotation.x = 0;
            }}

            // 4. Maneuver Specific Navigation Gestures
            if (stateName === 'TURNING_LEFT') {{
                // Left arm raised pointing towards left road with open friendly hand
                characterLimbs.leftArm.shoulder.rotation.x = -1.15;
                characterLimbs.leftArm.shoulder.rotation.z = -0.75;
                characterLimbs.leftArm.elbow.rotation.x = 0.25;
                characterLimbs.rightArm.shoulder.rotation.x = Math.sin(gaitPhase) * 0.3;
                characterLimbs.rightArm.shoulder.rotation.z = -0.1;
                characterLimbs.head.rotation.y = THREE.MathUtils.lerp(characterLimbs.head.rotation.y, 0.45, 0.15); // Look left into turn
                characterLimbs.head.rotation.z = 0;
            }} else if (stateName === 'TURNING_RIGHT') {{
                // Right arm raised pointing towards right road with open friendly hand
                characterLimbs.rightArm.shoulder.rotation.x = -1.15;
                characterLimbs.rightArm.shoulder.rotation.z = 0.75;
                characterLimbs.rightArm.elbow.rotation.x = 0.25;
                characterLimbs.leftArm.shoulder.rotation.x = Math.sin(gaitPhase) * 0.3;
                characterLimbs.leftArm.shoulder.rotation.z = 0.1;
                characterLimbs.head.rotation.y = THREE.MathUtils.lerp(characterLimbs.head.rotation.y, -0.45, 0.15); // Look right into turn
                characterLimbs.head.rotation.z = 0;
            }} else if (stateName === 'WAITING_AT_CROSSING') {{
                // Pedestrian traffic scan: looks left, checks center, looks right safely
                characterLimbs.leftArm.shoulder.rotation.x = 0.08;
                characterLimbs.leftArm.shoulder.rotation.z = 0.08;
                characterLimbs.rightArm.shoulder.rotation.x = 0.08;
                characterLimbs.rightArm.shoulder.rotation.z = -0.08;
                characterLimbs.head.rotation.y = Math.sin(now * 0.0028) * 0.70;
                characterLimbs.head.rotation.x = 0.05;
                characterLimbs.head.rotation.z = 0;
            }} else if (stateName === 'CROSSING') {{
                // Alert, confident pedestrian stride across zebra crossing
                const armSwingAmp = 0.55;
                characterLimbs.leftArm.shoulder.rotation.x = -Math.sin(gaitPhase) * armSwingAmp;
                characterLimbs.rightArm.shoulder.rotation.x = -Math.sin(gaitPhase + Math.PI) * armSwingAmp;
                characterLimbs.leftArm.shoulder.rotation.z = 0.1;
                characterLimbs.rightArm.shoulder.rotation.z = -0.1;
                characterLimbs.head.rotation.y = Math.sin(now * 0.004) * 0.20; // Quick road check
                characterLimbs.head.rotation.z = 0;
            }} else if (stateName === 'ARRIVED' || stateName === 'CELEBRATING') {{
                // Destination victory celebration: cheerful hop bob & friendly dual-arm wave
                const wave = Math.sin(now * 0.006) * 0.35;
                characterLimbs.leftArm.shoulder.rotation.x = -2.1;
                characterLimbs.leftArm.shoulder.rotation.z = -0.4 + wave;
                characterLimbs.rightArm.shoulder.rotation.x = -2.1;
                characterLimbs.rightArm.shoulder.rotation.z = 0.4 - wave;
                characterLimbs.head.rotation.y = 0;
                characterLimbs.head.rotation.z = Math.sin(now * 0.004) * 0.12; // Happy head tilt
                characterLimbs.pelvis.position.y = 0.95 + Math.abs(Math.sin(now * 0.005)) * 0.08; // Happy celebration bob
            }} else if (stateName === 'ROUTE_DEVIATION') {{
                // Route deviation: quizzical pause with hand scratching temple
                characterLimbs.head.rotation.z = 0.32; // Puzzled tilt
                characterLimbs.head.rotation.y = Math.sin(now * 0.002) * 0.2;
                characterLimbs.rightArm.shoulder.rotation.x = -1.9;
                characterLimbs.rightArm.shoulder.rotation.z = 0.35;
                characterLimbs.rightArm.elbow.rotation.x = 1.3;
                characterLimbs.leftArm.shoulder.rotation.x = 0.1;
                characterLimbs.leftArm.shoulder.rotation.z = 0.1;
            }} else if (isMoving) {{
                // Standard Natural Walking: Arms swing opposite to legs with natural elbow flexion
                const armSwingAmp = 0.55;
                const leftArmX = -Math.sin(gaitPhase) * armSwingAmp;
                const rightArmX = -Math.sin(gaitPhase + Math.PI) * armSwingAmp;

                characterLimbs.leftArm.shoulder.rotation.x = leftArmX;
                characterLimbs.rightArm.shoulder.rotation.x = rightArmX;
                characterLimbs.leftArm.shoulder.rotation.z = 0.1;
                characterLimbs.rightArm.shoulder.rotation.z = -0.1;

                // Elbows flex slightly on the forward swing stroke
                characterLimbs.leftArm.elbow.rotation.x = Math.max(0, -leftArmX * 0.4);
                characterLimbs.rightArm.elbow.rotation.x = Math.max(0, -rightArmX * 0.4);

                characterLimbs.head.rotation.y = 0;
                characterLimbs.head.rotation.z = 0;
                characterLimbs.head.rotation.x = 0;
            }} else {{
                // Idle Natural micro-movements: relaxed arm sway & occasional head look-around
                const idleSway = Math.sin(now * 0.0018) * 0.04;
                characterLimbs.leftArm.shoulder.rotation.x = 0.05 + idleSway;
                characterLimbs.rightArm.shoulder.rotation.x = 0.05 + idleSway;
                characterLimbs.leftArm.shoulder.rotation.z = 0.08;
                characterLimbs.rightArm.shoulder.rotation.z = -0.08;
                characterLimbs.leftArm.elbow.rotation.x = 0.10;
                characterLimbs.rightArm.elbow.rotation.x = 0.10;

                // Subtle natural head looking around
                characterLimbs.head.rotation.y = Math.sin(now * 0.0012) * 0.09;
                characterLimbs.head.rotation.x = Math.cos(now * 0.0016) * 0.04;
                characterLimbs.head.rotation.z = 0;
            }}
        }}

        // Dynamic Camera Controller
        function updateCameraFollow(pos) {{
            if (!camera || !pos) return;

            const charPos = new THREE.Vector3(pos.x, pos.y, pos.z);
            const forward = new THREE.Vector3(pos.tx, 0, pos.tz).normalize();
            const right = new THREE.Vector3(-pos.tz, 0, pos.tx).normalize();

            let targetCamPos = new THREE.Vector3();
            let lookAtTarget = new THREE.Vector3();

            if (activeCameraMode === 'follow') {{
                // Third-person chase cam trailing smoothly behind character
                targetCamPos.copy(charPos).sub(forward.clone().multiplyScalar(4.5)).add(new THREE.Vector3(0, 2.8, 0));
                lookAtTarget.copy(charPos).add(new THREE.Vector3(0, 1.2, 0)).add(forward.clone().multiplyScalar(2.0));
            }} else if (activeCameraMode === 'instructor') {{
                // Instructor face-to-face view looking at the virtual guide
                targetCamPos.copy(charPos).add(forward.clone().multiplyScalar(3.2)).add(new THREE.Vector3(0, 1.8, 0));
                lookAtTarget.copy(charPos).add(new THREE.Vector3(0, 1.4, 0));
            }} else if (activeCameraMode === 'drone') {{
                // Isometric cinematic perspective
                targetCamPos.copy(charPos).sub(forward.clone().multiplyScalar(10.0)).add(right.clone().multiplyScalar(7.0)).add(new THREE.Vector3(0, 9.0, 0));
                lookAtTarget.copy(charPos).add(new THREE.Vector3(0, 0.8, 0));
            }} else if (activeCameraMode === 'top') {{
                // Bird's eye overhead view
                targetCamPos.copy(charPos).add(new THREE.Vector3(0, 16.0, 0.01));
                lookAtTarget.copy(charPos);
            }}

            camera.position.lerp(targetCamPos, 0.1);
            camera.lookAt(lookAtTarget);
        }}

        // Fallback 2D Procedural Perspective Canvas if WebGL is unsupported
        function init2DFallback() {{
            const canvas = document.getElementById('canvas-2d-fallback');
            if (!canvas) return;
            canvas.style.display = 'block';
            const ctx = canvas.getContext('2d');

            function render2D() {{
                const root = document.getElementById('walking-guide-3d-root');
                if (!root || !root.isConnected) return;

                if (document.hidden) {{
                    fallbackAnimId = null;
                    return;
                }}

                fallbackAnimId = requestAnimationFrame(render2D);

                canvas.width = canvas.clientWidth || 800;
                canvas.height = canvas.clientHeight || 480;

                ctx.fillStyle = '#0b172a';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                // Perspective road
                ctx.fillStyle = '#1e293b';
                ctx.beginPath();
                ctx.moveTo(canvas.width * 0.45, canvas.height * 0.4);
                ctx.lineTo(canvas.width * 0.55, canvas.height * 0.4);
                ctx.lineTo(canvas.width * 0.85, canvas.height);
                ctx.lineTo(canvas.width * 0.15, canvas.height);
                ctx.closePath();
                ctx.fill();

                // Direction arrow carpet
                ctx.fillStyle = '#10b981';
                ctx.font = 'bold 36px Outfit, sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('⬆️', canvas.width * 0.5, canvas.height * 0.7);

                // Guide avatar 2D
                ctx.font = '54px Outfit, sans-serif';
                ctx.fillText('🚶‍♂️', canvas.width * 0.5, canvas.height * 0.85);
            }}

            fallbackAnimId = requestAnimationFrame(render2D);

            document.addEventListener('visibilitychange', function() {{
                if (!document.hidden && !fallbackAnimId) {{
                    fallbackAnimId = requestAnimationFrame(render2D);
                }}
            }});
        }}

        function onVisibilityChange() {{
            if (!document.hidden && !animFrameId) {{
                lastTimestamp = performance.now();
                animFrameId = requestAnimationFrame(animationLoop);
            }}
        }}

        function cleanupThreeScene() {{
            if (animFrameId) {{
                cancelAnimationFrame(animFrameId);
                animFrameId = null;
            }}
            window.removeEventListener('resize', onWindowResize);
            document.removeEventListener('visibilitychange', onVisibilityChange);

            if (renderer) {{
                renderer.dispose();
                if (renderer.domElement && renderer.domElement.parentNode) {{
                    renderer.domElement.parentNode.removeChild(renderer.domElement);
                }}
            }}

            if (scene) {{
                scene.traverse(function(obj) {{
                    if (obj.geometry) {{
                        obj.geometry.dispose();
                    }}
                    if (obj.material) {{
                        if (Array.isArray(obj.material)) {{
                            obj.material.forEach(m => m.dispose());
                        }} else {{
                            obj.material.dispose();
                        }}
                    }}
                }});
            }}
        }}

        function onWindowResize() {{
            const container = document.getElementById('webgl-container');
            if (!container || !camera || !renderer) return;
            const w = container.clientWidth;
            const h = container.clientHeight;
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
            renderer.setSize(w, h);
        }}

        // Populate Steps Carousel
        function populateStepsCarousel() {{
            const container = document.getElementById('steps-carousel');
            if (!container) return;
            container.innerHTML = '';

            MANEUVERS.forEach((m, idx) => {{
                const chip = document.createElement('div');
                chip.className = 'step-chip' + (idx === 0 ? ' active' : '');
                chip.innerHTML = '<span>' + (m.icon || '📍') + '</span> <span>' + (m.headline || m.instruction_text) + '</span>';
                chip.onclick = function() {{
                    currentStationM = m.start_station_m;
                    updateNavigationState();
                }};
                container.appendChild(chip);
            }});
        }}

        // Public Control Handlers
        window.togglePlayPause = function() {{
            isPlaying = !isPlaying;
            const icon = document.getElementById('play-icon');
            const txt = document.getElementById('play-text');
            if (icon) icon.innerText = isPlaying ? '⏸' : '▶';
            if (txt) txt.innerText = isPlaying ? 'Pause' : 'Play';
        }};

        window.prevManeuver = function() {{
            if (currentManeuverIdx > 0) {{
                currentStationM = MANEUVERS[currentManeuverIdx - 1].start_station_m;
                updateNavigationState();
            }}
        }};

        window.nextManeuver = function() {{
            if (currentManeuverIdx < MANEUVERS.length - 1) {{
                currentStationM = MANEUVERS[currentManeuverIdx + 1].start_station_m;
                updateNavigationState();
            }}
        }};

        window.restartJourney = function() {{
            currentStationM = 0.0;
            isPlaying = true;
            const icon = document.getElementById('play-icon');
            const txt = document.getElementById('play-text');
            if (icon) icon.innerText = '⏸';
            if (txt) txt.innerText = 'Pause';
            updateNavigationState();
        }};

        window.onScrub = function(pct) {{
            currentStationM = (parseFloat(pct) / 100.0) * TOTAL_DISTANCE_M;
            updateNavigationState();
        }};

        window.setSimSpeed = function(multiplier) {{
            simSpeedMultiplier = multiplier;
            ['05', '1', '2', '4'].forEach(k => {{
                const btn = document.getElementById('speed-btn-' + k);
                if (btn) btn.classList.remove('active');
            }});
            const activeKey = multiplier === 0.5 ? '05' : String(multiplier);
            const activeBtn = document.getElementById('speed-btn-' + activeKey);
            if (activeBtn) activeBtn.classList.add('active');

            const speedEl = document.getElementById('hud-speed-val');
            if (speedEl) speedEl.innerText = (4.8 * multiplier).toFixed(1) + ' km/h';
        }};

        window.setCameraView = function(mode) {{
            activeCameraMode = mode;
            ['follow', 'instructor', 'drone', 'top'].forEach(m => {{
                const btn = document.getElementById('cam-' + m);
                if (btn) btn.classList.remove('active');
            }});
            const activeBtn = document.getElementById('cam-' + mode);
            if (activeBtn) activeBtn.classList.add('active');
        }};

        window.toggleMode = function() {{
            isDemoMode = !isDemoMode;
            const icon = document.getElementById('mode-icon');
            const txt = document.getElementById('mode-text');
            if (icon) icon.innerText = isDemoMode ? '🎯' : '🛰️';
            if (txt) txt.innerText = isDemoMode ? 'Demonstration Mode' : 'Live Satellite Mode';
        }};

        window.toggleVoice = function() {{
            isVoiceEnabled = !isVoiceEnabled;
            const icon = document.getElementById('voice-icon');
            const txt = document.getElementById('voice-text');
            if (icon) icon.innerText = isVoiceEnabled ? '🔊' : '🔇';
            if (txt) txt.innerText = isVoiceEnabled ? 'Voice: On' : 'Voice: Muted';
            if (!isVoiceEnabled && 'speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
            }}
        }};

        // Launch
        populateStepsCarousel();
        initThreeScene();
    }})();
    </script>
    """
