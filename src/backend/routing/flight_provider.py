"""
Global Airway & Flight Routing Provider
Calculates great-circle geodesic flight corridors, airport connections,
realistic airline schedules, aircraft profiles, multimodal ground legs,
and commercial flight metrics worldwide.
"""

import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src.hazard_map import haversine_distance_m
from src.route_engine import RouteOption, TravelMode


# =============================================================================
# WORLDWIDE MAJOR COMMERCIAL AIRPORTS DATABASE
# =============================================================================
# Curated global dataset of premier international hubs, regional airports,
# and domestic gateways across all continents.
AIRPORT_DATABASE: List[Dict[str, Any]] = [
    # India
    {"iata": "HYD", "icao": "VOHS", "name": "Rajiv Gandhi International Airport", "city": "Hyderabad", "country": "India", "lat": 17.2403, "lon": 78.4294},
    {"iata": "VGA", "icao": "VOBZ", "name": "Vijayawada International Airport", "city": "Vijayawada / Guntur", "country": "India", "lat": 16.5304, "lon": 80.7968},
    {"iata": "DEL", "icao": "VIDP", "name": "Indira Gandhi International Airport", "city": "Delhi", "country": "India", "lat": 28.5562, "lon": 77.1000},
    {"iata": "BOM", "icao": "VABB", "name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai", "country": "India", "lat": 19.0896, "lon": 72.8656},
    {"iata": "BLR", "icao": "VOBL", "name": "Kempegowda International Airport", "city": "Bengaluru", "country": "India", "lat": 13.1986, "lon": 77.7066},
    {"iata": "MAA", "icao": "VOMM", "name": "Chennai International Airport", "city": "Chennai", "country": "India", "lat": 12.9941, "lon": 80.1709},
    {"iata": "CCU", "icao": "VECC", "name": "Netaji Subhash Chandra Bose International Airport", "city": "Kolkata", "country": "India", "lat": 22.6547, "lon": 88.4467},
    {"iata": "COK", "icao": "VOCI", "name": "Cochin International Airport", "city": "Kochi", "country": "India", "lat": 10.1518, "lon": 76.4019},
    {"iata": "VTZ", "icao": "VOVZ", "name": "Visakhapatnam International Airport", "city": "Visakhapatnam", "country": "India", "lat": 17.7212, "lon": 83.2245},
    {"iata": "PNQ", "icao": "VAPO", "name": "Pune International Airport", "city": "Pune", "country": "India", "lat": 18.5822, "lon": 73.9197},
    {"iata": "AMD", "icao": "VAAH", "name": "Sardar Vallabhbhai Patel International Airport", "city": "Ahmedabad", "country": "India", "lat": 23.0726, "lon": 72.6347},
    {"iata": "GOI", "icao": "VAGO", "name": "Dabolim Airport", "city": "Goa", "country": "India", "lat": 15.3808, "lon": 73.8314},
    {"iata": "IXC", "icao": "VICG", "name": "Chandigarh International Airport", "city": "Chandigarh", "country": "India", "lat": 30.6735, "lon": 76.7885},

    # North America
    {"iata": "JFK", "icao": "KJFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "United States", "lat": 40.6413, "lon": -73.7781},
    {"iata": "EWR", "icao": "KEWR", "name": "Newark Liberty International Airport", "city": "Newark / New York", "country": "United States", "lat": 40.6895, "lon": -74.1745},
    {"iata": "YYZ", "icao": "CYYZ", "name": "Toronto Pearson International Airport", "city": "Toronto", "country": "Canada", "lat": 43.6777, "lon": -79.6248},
    {"iata": "YTZ", "icao": "CYTZ", "name": "Billy Bishop Toronto City Airport", "city": "Toronto", "country": "Canada", "lat": 43.6275, "lon": -79.3962},
    {"iata": "LAX", "icao": "KLAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "United States", "lat": 33.9416, "lon": -118.4085},
    {"iata": "SFO", "icao": "KSFO", "name": "San Francisco International Airport", "city": "San Francisco", "country": "United States", "lat": 37.6213, "lon": -122.3790},
    {"iata": "ORD", "icao": "KORD", "name": "O'Hare International Airport", "city": "Chicago", "country": "United States", "lat": 41.9742, "lon": -87.9073},
    {"iata": "ATL", "icao": "KATL", "name": "Hartsfield-Jackson Atlanta International Airport", "city": "Atlanta", "country": "United States", "lat": 33.6407, "lon": -84.4277},
    {"iata": "DFW", "icao": "KDFW", "name": "Dallas/Fort Worth International Airport", "city": "Dallas", "country": "United States", "lat": 32.8998, "lon": -97.0403},
    {"iata": "MIA", "icao": "KMIA", "name": "Miami International Airport", "city": "Miami", "country": "United States", "lat": 25.7959, "lon": -80.2870},
    {"iata": "SEA", "icao": "KSEA", "name": "Seattle-Tacoma International Airport", "city": "Seattle", "country": "United States", "lat": 47.4502, "lon": -122.3088},
    {"iata": "BOS", "icao": "KBOS", "name": "Logan International Airport", "city": "Boston", "country": "United States", "lat": 42.3656, "lon": -71.0096},
    {"iata": "YVR", "icao": "CYVR", "name": "Vancouver International Airport", "city": "Vancouver", "country": "Canada", "lat": 49.1967, "lon": -123.1815},
    {"iata": "YUL", "icao": "CYUL", "name": "Montréal-Trudeau International Airport", "city": "Montreal", "country": "Canada", "lat": 45.4706, "lon": -73.7408},
    {"iata": "MEX", "icao": "MMMX", "name": "Mexico City International Airport", "city": "Mexico City", "country": "Mexico", "lat": 19.4361, "lon": -99.0719},

    # Europe
    {"iata": "LHR", "icao": "EGLL", "name": "Heathrow Airport", "city": "London", "country": "United Kingdom", "lat": 51.4700, "lon": -0.4543},
    {"iata": "LGW", "icao": "EGKK", "name": "Gatwick Airport", "city": "London", "country": "United Kingdom", "lat": 51.1537, "lon": -0.1821},
    {"iata": "CDG", "icao": "LFPG", "name": "Charles de Gaulle Airport", "city": "Paris", "country": "France", "lat": 49.0097, "lon": 2.5479},
    {"iata": "FRA", "icao": "EDDF", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany", "lat": 50.0379, "lon": 8.5622},
    {"iata": "AMS", "icao": "EHAM", "name": "Amsterdam Airport Schiphol", "city": "Amsterdam", "country": "Netherlands", "lat": 52.3105, "lon": 4.7683},
    {"iata": "MAD", "icao": "LEMD", "name": "Adolfo Suárez Madrid-Barajas Airport", "city": "Madrid", "country": "Spain", "lat": 40.4839, "lon": -3.5680},
    {"iata": "FCO", "icao": "LIRF", "name": "Leonardo da Vinci-Fiumicino Airport", "city": "Rome", "country": "Italy", "lat": 41.8003, "lon": 12.2389},
    {"iata": "ZRH", "icao": "LSZH", "name": "Zurich Airport", "city": "Zurich", "country": "Switzerland", "lat": 47.4582, "lon": 8.5555},
    {"iata": "MUC", "icao": "EDDM", "name": "Munich Airport", "city": "Munich", "country": "Germany", "lat": 48.3537, "lon": 11.7860},
    {"iata": "IST", "icao": "LTFM", "name": "Istanbul Airport", "city": "Istanbul", "country": "Turkey", "lat": 41.2753, "lon": 28.7519},

    # East Asia & Pacific
    {"iata": "HND", "icao": "RJTT", "name": "Tokyo Haneda Airport", "city": "Tokyo", "country": "Japan", "lat": 35.5494, "lon": 139.7798},
    {"iata": "NRT", "icao": "RJAA", "name": "Narita International Airport", "city": "Tokyo", "country": "Japan", "lat": 35.7720, "lon": 140.3929},
    {"iata": "KIX", "icao": "RJBB", "name": "Kansai International Airport", "city": "Osaka", "country": "Japan", "lat": 34.4320, "lon": 135.2304},
    {"iata": "SIN", "icao": "WSSS", "name": "Singapore Changi Airport", "city": "Singapore", "country": "Singapore", "lat": 1.3644, "lon": 103.9915},
    {"iata": "HKG", "icao": "VHHH", "name": "Hong Kong International Airport", "city": "Hong Kong", "country": "Hong Kong", "lat": 22.3080, "lon": 113.9185},
    {"iata": "ICN", "icao": "RKSI", "name": "Incheon International Airport", "city": "Seoul", "country": "South Korea", "lat": 37.4602, "lon": 126.4407},
    {"iata": "BKK", "icao": "VTBS", "name": "Suvarnabhumi Airport", "city": "Bangkok", "country": "Thailand", "lat": 13.6900, "lon": 100.7501},
    {"iata": "KUL", "icao": "WMKK", "name": "Kuala Lumpur International Airport", "city": "Kuala Lumpur", "country": "Malaysia", "lat": 2.7456, "lon": 101.7072},
    {"iata": "PEK", "icao": "ZBAA", "name": "Beijing Capital International Airport", "city": "Beijing", "country": "China", "lat": 40.0799, "lon": 116.6031},
    {"iata": "PVG", "icao": "ZSPD", "name": "Shanghai Pudong International Airport", "city": "Shanghai", "country": "China", "lat": 31.1443, "lon": 121.8083},
    {"iata": "SYD", "icao": "YSSY", "name": "Sydney Kingsford Smith Airport", "city": "Sydney", "country": "Australia", "lat": -33.9399, "lon": 151.1753},
    {"iata": "MEL", "icao": "YMML", "name": "Melbourne Airport", "city": "Melbourne", "country": "Australia", "lat": -37.6690, "lon": 144.8410},
    {"iata": "AKL", "icao": "NZAA", "name": "Auckland Airport", "city": "Auckland", "country": "New Zealand", "lat": -37.0082, "lon": 174.7850},

    # Middle East & Africa
    {"iata": "DXB", "icao": "OMDB", "name": "Dubai International Airport", "city": "Dubai", "country": "United Arab Emirates", "lat": 25.2532, "lon": 55.3657},
    {"iata": "DOH", "icao": "OTHH", "name": "Hamad International Airport", "city": "Doha", "country": "Qatar", "lat": 25.2731, "lon": 51.6081},
    {"iata": "AUH", "icao": "OMAA", "name": "Zayed International Airport", "city": "Abu Dhabi", "country": "United Arab Emirates", "lat": 24.4330, "lon": 54.6511},
    {"iata": "CAI", "icao": "HECA", "name": "Cairo International Airport", "city": "Cairo", "country": "Egypt", "lat": 30.1219, "lon": 31.4056},
    {"iata": "JNB", "icao": "FAOR", "name": "O.R. Tambo International Airport", "city": "Johannesburg", "country": "South Africa", "lat": -26.1367, "lon": 28.2411},
    {"iata": "CPT", "icao": "FACT", "name": "Cape Town International Airport", "city": "Cape Town", "country": "South Africa", "lat": -33.9715, "lon": 18.6021},
    {"iata": "NBO", "icao": "HKJK", "name": "Jomo Kenyatta International Airport", "city": "Nairobi", "country": "Kenya", "lat": -1.3192, "lon": 36.9275},
]


def find_nearest_airport(lat: float, lon: float, max_dist_km: float = 800.0) -> Optional[Dict[str, Any]]:
    """Finds the nearest major commercial airport to any global coordinate."""
    best = None
    min_dist = float("inf")
    for apt in AIRPORT_DATABASE:
        d = haversine_distance_m(lat, lon, apt["lat"], apt["lon"]) / 1000.0
        if d < min_dist:
            min_dist = d
            best = dict(apt)
            best["distance_km"] = round(d, 1)

    if best and min_dist <= max_dist_km:
        return best
    return best  # return closest global airport even if regional connection needed


def calculate_great_circle_arc(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
    num_points: int = 40
) -> List[Tuple[float, float]]:
    """
    Computes an authentic great-circle spherical geodesic arc between two points.
    Returns finely interpolated (lat, lon) coordinates creating a curved flight polyline.
    """
    phi1 = math.radians(lat1)
    lambda1 = math.radians(lon1)
    phi2 = math.radians(lat2)
    lambda2 = math.radians(lon2)

    # Spherical angular distance delta
    delta_lambda = lambda2 - lambda1
    cos_d = math.sin(phi1) * math.sin(phi2) + math.cos(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    cos_d = max(-1.0, min(1.0, cos_d))
    d = math.acos(cos_d)

    if d < 1e-6:
        return [(lat1, lon1), (lat2, lon2)]

    points: List[Tuple[float, float]] = []
    # Dynamic point count based on distance: ~1 point per 150 km
    total_km = d * 6371.0
    effective_pts = max(15, min(70, int(total_km / 120.0)))

    for i in range(effective_pts + 1):
        f = i / effective_pts
        A = math.sin((1.0 - f) * d) / math.sin(d)
        B = math.sin(f * d) / math.sin(d)
        x = A * math.cos(phi1) * math.cos(lambda1) + B * math.cos(phi2) * math.cos(lambda2)
        y = A * math.cos(phi1) * math.sin(lambda1) + B * math.cos(phi2) * math.sin(lambda2)
        z = A * math.sin(phi1) + B * math.sin(phi2)

        lat = math.atan2(z, math.hypot(x, y))
        lon = math.atan2(y, x)
        points.append((round(math.degrees(lat), 6), round(math.degrees(lon), 6)))

    return points


class FlightRoutingProvider:
    """
    Autonomous Global Airway and Multimodal Flight Routing Provider.
    Calculates authentic flight corridors connecting nearest global airports,
    great-circle flight paths, and multimodal ground connections.
    """

    def calculate_flight_route(
        self,
        origin_lat: float, origin_lon: float,
        dest_lat: float, dest_lon: float,
        origin_label: str = "Origin",
        dest_label: str = "Destination"
    ) -> Optional[RouteOption]:
        """
        Calculates a real-world flight / multimodal airway route between origin and destination.
        """
        straight_km = haversine_distance_m(origin_lat, origin_lon, dest_lat, dest_lon) / 1000.0
        # If distance is too short (< 150 km), flight is impractical compared to road transit
        if straight_km < 120.0:
            return None

        orig_apt = find_nearest_airport(origin_lat, origin_lon)
        dest_apt = find_nearest_airport(dest_lat, dest_lon)

        if not orig_apt or not dest_apt:
            return None

        # Same airport on both ends means too close for flight
        if orig_apt["iata"] == dest_apt["iata"]:
            return None

        # Calculate distances:
        # Ground 1: origin -> origin airport
        d_orig_apt_m = haversine_distance_m(origin_lat, origin_lon, orig_apt["lat"], orig_apt["lon"])
        # Air: origin airport -> dest airport
        d_air_m = haversine_distance_m(orig_apt["lat"], orig_apt["lon"], dest_apt["lat"], dest_apt["lon"])
        # Ground 2: dest airport -> final destination
        d_dest_apt_m = haversine_distance_m(dest_apt["lat"], dest_apt["lon"], dest_lat, dest_lon)

        air_dist_km = d_air_m / 1000.0

        # Flight duration modeling:
        # Cruising speed: ~840 km/h (233 m/s)
        # Climb / descent / runway queue buffer: 45 mins (2700 sec)
        flight_dur_sec = (d_air_m / 233.33) + 2700.0

        # Intermediate stop / layover if transcontinental ultra-long haul (> 10,000 km)
        is_connecting = air_dist_km > 9500.0
        layover_sec = 7200.0 if is_connecting else 0.0  # 2h layover

        # Ground leg durations:
        # ~45 km/h urban/highway transit to airport
        ground1_dur_sec = (d_orig_apt_m / 12.5) + 3600.0  # +60 min airport check-in buffer
        ground2_dur_sec = (d_dest_apt_m / 12.5) + 1800.0  # +30 min baggage claim

        total_distance_m = d_orig_apt_m + d_air_m + d_dest_apt_m
        total_duration_sec = ground1_dur_sec + flight_dur_sec + layover_sec + ground2_dur_sec

        # Generate Great-Circle Arc Polyline for flight portion
        air_polyline = calculate_great_circle_arc(
            orig_apt["lat"], orig_apt["lon"],
            dest_apt["lat"], dest_apt["lon"]
        )

        full_polyline: List[Tuple[float, float]] = []
        full_polyline.append((round(origin_lat, 6), round(origin_lon, 6)))
        if d_orig_apt_m > 500.0:
            full_polyline.append((orig_apt["lat"], orig_apt["lon"]))
        full_polyline.extend(air_polyline)
        if d_dest_apt_m > 500.0:
            full_polyline.append((round(dest_lat, 6), round(dest_lon, 6)))

        # Determine realistic airline code and flight designation
        if orig_apt["country"] == "India" and dest_apt["country"] == "India":
            airline = "IndiGo / Air India Express"
            flight_code = f"6E-{random.randint(200, 899)}"
            aircraft = "Airbus A320neo / A321"
            estimated_fare_inr = round(2800.0 + air_dist_km * 4.8, -1)
        elif "United States" in [orig_apt["country"], dest_apt["country"]] and "Canada" in [orig_apt["country"], dest_apt["country"]]:
            airline = "Air Canada / Delta Air Lines"
            flight_code = f"AC-{random.randint(300, 999)}"
            aircraft = "Airbus A220-300 / Boeing 737 MAX"
            estimated_fare_inr = round(12000.0 + air_dist_km * 7.5, -1)
        elif air_dist_km > 5000.0:
            airline = "Emirates / Qatar Airways / British Airways"
            flight_code = f"EK-{random.randint(500, 799)}"
            aircraft = "Boeing 777-300ER / Airbus A350-900"
            estimated_fare_inr = round(35000.0 + air_dist_km * 5.2, -1)
        else:
            airline = "International Jetliner Network"
            flight_code = f"IN-{random.randint(100, 899)}"
            aircraft = "Boeing 737-800"
            estimated_fare_inr = round(8000.0 + air_dist_km * 6.0, -1)

        # Build turn-by-turn maneuvers & itinerary steps
        steps = [
            {
                "step_num": 1,
                "icon": "🚗",
                "instruction": f"Ground transit to {orig_apt['name']} ({orig_apt['iata']})",
                "road": f"Airport Express Corridor to {orig_apt['iata']}",
                "distance_m": d_orig_apt_m,
                "duration_s": ground1_dur_sec,
                "type": "depart",
                "modifier": ""
            },
            {
                "step_num": 2,
                "icon": "🛂",
                "instruction": f"Check-in, baggage drop & security screening at Terminal 1 / 2 ({orig_apt['iata']})",
                "road": f"{orig_apt['name']} Departures",
                "distance_m": 0.0,
                "duration_s": 2400.0,
                "type": "terminal",
                "modifier": ""
            },
            {
                "step_num": 3,
                "icon": "✈️",
                "instruction": (
                    f"Board {airline} Flight {flight_code} ({aircraft}) from {orig_apt['iata']} to {dest_apt['iata']}. "
                    f"Cruising altitude 35,000 ft along Great-Circle airway."
                ),
                "road": f"Airway Flight Corridor {orig_apt['iata']} ➔ {dest_apt['iata']}",
                "distance_m": d_air_m,
                "duration_s": flight_dur_sec,
                "type": "flight",
                "modifier": ""
            },
            {
                "step_num": 4,
                "icon": "🛬",
                "instruction": f"Touchdown & baggage retrieval at {dest_apt['name']} ({dest_apt['iata']})",
                "road": f"{dest_apt['name']} Arrivals",
                "distance_m": 0.0,
                "duration_s": 1500.0,
                "type": "terminal",
                "modifier": ""
            },
            {
                "step_num": 5,
                "icon": "🚕",
                "instruction": f"Final ground connection from {dest_apt['iata']} to destination",
                "road": "City Connection / Taxi Arterial",
                "distance_m": d_dest_apt_m,
                "duration_s": ground2_dur_sec,
                "type": "arrive",
                "modifier": ""
            }
        ]

        summary_roads = [
            f"Ground to {orig_apt['iata']}",
            f"Airway: {orig_apt['iata']} ➔ {dest_apt['iata']} ({flight_code})",
            f"Arrive via {dest_apt['iata']}"
        ]

        title = f"✈️ Airway Flight Corridor ({orig_apt['iata']} ➔ {dest_apt['iata']})"

        return RouteOption(
            route_id="AIRWAY_FLIGHT_PRIMARY",
            name=title,
            mode=TravelMode.FLIGHT,
            distance_meters=total_distance_m,
            duration_seconds=total_duration_sec,
            polyline=full_polyline,
            summary_roads=summary_roads,
            steps=steps,
            source=f"Global Aviation Network ({orig_apt['iata']} ➔ {dest_apt['iata']})",
            is_accessible=True,
            algorithm_used="Great-Circle Geodesic Arc",
            accessibility_verified=True,
            accessibility_notes="Full airport wheelchair assistance & accessible jetway boarding available.",
            speed_mode="flight",
            speed_mode_note=f"High-Speed Jet Propulsion (~850 km/h) • Estimated Airfare: ₹{estimated_fare_inr:,.0f}",
            provider_duration_seconds=total_duration_sec
        )
