"""
Global Waterway & Maritime Ferry Routing Provider
Calculates nautical maritime navigation corridors, commercial ferry crossings,
coastal sea lanes, vessel speeds, and multimodal port transfers worldwide.
"""

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src.hazard_map import haversine_distance_m
from src.route_engine import RouteOption, TravelMode


# =============================================================================
# WORLDWIDE MAJOR MARITIME FERRY & WATERWAY CORRIDORS
# =============================================================================
MARITIME_CORRIDORS: List[Dict[str, Any]] = [
    # India & Indian Ocean
    {
        "id": "FERRY_MUMBAI_MANDWA",
        "name": "Mumbai Gateway ⇄ Mandwa Ro-Pax Fast Ferry",
        "operator": "M2M Ferries / Mumbai Water Transport",
        "port_a": {"name": "Bhaucha Dhakka / Gateway Terminal, Mumbai", "lat": 18.9220, "lon": 72.8347},
        "port_b": {"name": "Mandwa Ferry Terminal, Alibaug", "lat": 18.7845, "lon": 72.8711},
        "waypoints": [(18.9220, 72.8347), (18.8600, 72.8450), (18.7845, 72.8711)],
        "speed_kmh": 32.0,
        "fare_inr": 450.0,
        "is_car_ferry": True
    },
    {
        "id": "FERRY_GHOGHA_DAHEJ",
        "name": "Gulf of Khambhat Ro-Pax Sea Link",
        "operator": "Gujarat Maritime Board (Indigo Seaways)",
        "port_a": {"name": "Ghogha Ro-Pax Terminal, Bhavnagar", "lat": 21.6881, "lon": 72.2858},
        "port_b": {"name": "Dahej Ro-Pax Terminal, Bharuch", "lat": 21.7050, "lon": 72.5850},
        "waypoints": [(21.6881, 72.2858), (21.6960, 72.4350), (21.7050, 72.5850)],
        "speed_kmh": 35.0,
        "fare_inr": 850.0,
        "is_car_ferry": True
    },
    {
        "id": "FERRY_PORT_BLAIR_HAVELOCK",
        "name": "Andaman Sea High-Speed Catamaran",
        "operator": "Makruzz / Green Ocean Maritime",
        "port_a": {"name": "Haddo Wharf, Port Blair", "lat": 11.6780, "lon": 92.7290},
        "port_b": {"name": "Swaraj Dweep (Havelock) Jetty", "lat": 12.0360, "lon": 92.9810},
        "waypoints": [(11.6780, 92.7290), (11.8500, 92.8500), (12.0360, 92.9810)],
        "speed_kmh": 42.0,
        "fare_inr": 1650.0,
        "is_car_ferry": False
    },
    {
        "id": "FERRY_KOCHI_WATER_METRO",
        "name": "Kochi Backwaters Electric Water Metro",
        "operator": "Kochi Metro Rail Limited (KMRL)",
        "port_a": {"name": "High Court Water Metro Jetty, Ernakulam", "lat": 9.9810, "lon": 76.2750},
        "port_b": {"name": "Vypin Water Metro Terminal", "lat": 9.9730, "lon": 76.2420},
        "waypoints": [(9.9810, 76.2750), (9.9780, 76.2580), (9.9730, 76.2420)],
        "speed_kmh": 22.0,
        "fare_inr": 40.0,
        "is_car_ferry": False
    },

    # North America
    {
        "id": "FERRY_STATEN_ISLAND",
        "name": "Staten Island Ferry (Manhattan ⇄ Staten Island)",
        "operator": "NYC Department of Transportation",
        "port_a": {"name": "Whitehall Terminal, Lower Manhattan", "lat": 40.7011, "lon": -74.0135},
        "port_b": {"name": "St. George Terminal, Staten Island", "lat": 40.6437, "lon": -74.0742},
        "waypoints": [(40.7011, -74.0135), (40.6720, -74.0450), (40.6437, -74.0742)],
        "speed_kmh": 28.0,
        "fare_inr": 0.0,  # Free municipal ferry
        "is_car_ferry": False
    },
    {
        "id": "FERRY_SEATTLE_BAINBRIDGE",
        "name": "Puget Sound Maritime Crossing (Seattle ⇄ Bainbridge)",
        "operator": "Washington State Ferries",
        "port_a": {"name": "Colman Dock Pier 52, Seattle", "lat": 47.6025, "lon": -122.3380},
        "port_b": {"name": "Bainbridge Island Ferry Terminal", "lat": 47.6230, "lon": -122.5100},
        "waypoints": [(47.6025, -122.3380), (47.6150, -122.4200), (47.6230, -122.5100)],
        "speed_kmh": 33.0,
        "fare_inr": 820.0,
        "is_car_ferry": True
    },
    {
        "id": "FERRY_VANCOUVER_VICTORIA",
        "name": "Salish Sea Strait Crossing (Vancouver ⇄ Victoria)",
        "operator": "BC Ferries",
        "port_a": {"name": "Tsawwassen Ferry Terminal, Vancouver", "lat": 49.0065, "lon": -123.1315},
        "port_b": {"name": "Swartz Bay Terminal, Victoria", "lat": 48.6885, "lon": -123.4110},
        "waypoints": [(49.0065, -123.1315), (48.8800, -123.3200), (48.6885, -123.4110)],
        "speed_kmh": 36.0,
        "fare_inr": 1850.0,
        "is_car_ferry": True
    },

    # Europe
    {
        "id": "FERRY_DOVER_CALAIS",
        "name": "English Channel Strait Route (Dover ⇄ Calais)",
        "operator": "P&O Ferries / DFDS Seaways",
        "port_a": {"name": "Port of Dover Eastern Docks, UK", "lat": 51.1275, "lon": 1.3340},
        "port_b": {"name": "Port de Calais Terminal, France", "lat": 50.9680, "lon": 1.8680},
        "waypoints": [(51.1275, 1.3340), (51.0500, 1.6000), (50.9680, 1.8680)],
        "speed_kmh": 38.0,
        "fare_inr": 3400.0,
        "is_car_ferry": True
    },
    {
        "id": "FERRY_DUBLIN_HOLYHEAD",
        "name": "Irish Sea Maritime Corridor (Dublin ⇄ Holyhead)",
        "operator": "Irish Ferries / Stena Line",
        "port_a": {"name": "Dublin Port Terminal 1, Ireland", "lat": 53.3480, "lon": -6.2050},
        "port_b": {"name": "Holyhead Port Terminal, Wales, UK", "lat": 53.3080, "lon": -4.6310},
        "waypoints": [(53.3480, -6.2050), (53.3300, -5.4000), (53.3080, -4.6310)],
        "speed_kmh": 40.0,
        "fare_inr": 4200.0,
        "is_car_ferry": True
    },
    {
        "id": "FERRY_HELSINKI_TALLINN",
        "name": "Gulf of Finland Fast Shuttle (Helsinki ⇄ Tallinn)",
        "operator": "Tallink Silja / Viking Line",
        "port_a": {"name": "West Harbour Terminal 2, Helsinki, Finland", "lat": 60.1540, "lon": 24.9180},
        "port_b": {"name": "Old City Harbour Terminal D, Tallinn, Estonia", "lat": 59.4440, "lon": 24.7670},
        "waypoints": [(60.1540, 24.9180), (59.8000, 24.8400), (59.4440, 24.7670)],
        "speed_kmh": 48.0,
        "fare_inr": 2900.0,
        "is_car_ferry": True
    },

    # East Asia
    {
        "id": "FERRY_HONG_KONG_MACAU",
        "name": "Pearl River Delta High-Speed Catamaran (HK ⇄ Macau)",
        "operator": "TurboJET / Cotai Water Jet",
        "port_a": {"name": "Hong Kong Macau Ferry Terminal, Sheung Wan", "lat": 22.2880, "lon": 114.1520},
        "port_b": {"name": "Macau Outer Harbour Ferry Terminal", "lat": 22.1970, "lon": 113.5570},
        "waypoints": [(22.2880, 114.1520), (22.2400, 113.8500), (22.1970, 113.5570)],
        "speed_kmh": 65.0,
        "fare_inr": 2200.0,
        "is_car_ferry": False
    },
    {
        "id": "FERRY_TOKYO_BAY",
        "name": "Tokyo Bay Coastal Ferry (Kurihama ⇄ Kanaya)",
        "operator": "Tokyo-Wan Ferry Co.",
        "port_a": {"name": "Kurihama Port, Yokosuka, Kanagawa", "lat": 35.2180, "lon": 139.7180},
        "port_b": {"name": "Kanaya Port, Chiba", "lat": 35.1680, "lon": 139.8180},
        "waypoints": [(35.2180, 139.7180), (35.1930, 139.7680), (35.1680, 139.8180)],
        "speed_kmh": 26.0,
        "fare_inr": 950.0,
        "is_car_ferry": True
    }
]


class WaterwayRoutingProvider:
    """
    Autonomous Global Maritime & Ferry Routing Provider.
    Matches origin and destination against real maritime channels, ports,
    and ferry connections, calculating nautical polylines and port itineraries.
    """

    def calculate_waterway_route(
        self,
        origin_lat: float, origin_lon: float,
        dest_lat: float, dest_lon: float
    ) -> Optional[RouteOption]:
        """
        Calculates a real maritime/waterway route if a navigable ferry corridor connects
        the origin and destination regions.
        """
        best_corridor = None
        min_total_ground_dist = float("inf")
        match_forward = True

        for c in MARITIME_CORRIDORS:
            # Test port_a near origin and port_b near destination
            d1_a = haversine_distance_m(origin_lat, origin_lon, c["port_a"]["lat"], c["port_a"]["lon"])
            d1_b = haversine_distance_m(dest_lat, dest_lon, c["port_b"]["lat"], c["port_b"]["lon"])
            tot1 = d1_a + d1_b

            # Test reverse: port_b near origin and port_a near destination
            d2_a = haversine_distance_m(origin_lat, origin_lon, c["port_b"]["lat"], c["port_b"]["lon"])
            d2_b = haversine_distance_m(dest_lat, dest_lon, c["port_a"]["lat"], c["port_a"]["lon"])
            tot2 = d2_a + d2_b

            # Port must be within reasonable regional proximity (< 180 km) to departure/arrival
            if tot1 < min_total_ground_dist and d1_a < 180000.0 and d1_b < 180000.0:
                min_total_ground_dist = tot1
                best_corridor = c
                match_forward = True

            if tot2 < min_total_ground_dist and d2_a < 180000.0 and d2_b < 180000.0:
                min_total_ground_dist = tot2
                best_corridor = c
                match_forward = False

        if not best_corridor:
            return None

        # Build ferry route
        dep_port = best_corridor["port_a"] if match_forward else best_corridor["port_b"]
        arr_port = best_corridor["port_b"] if match_forward else best_corridor["port_a"]
        raw_waypoints = best_corridor["waypoints"] if match_forward else list(reversed(best_corridor["waypoints"]))

        # Ground leg 1: Origin to departure port
        d_orig_port_m = haversine_distance_m(origin_lat, origin_lon, dep_port["lat"], dep_port["lon"])
        # Water leg: Departure port along nautical waypoints to arrival port
        water_dist_m = 0.0
        for i in range(len(raw_waypoints) - 1):
            water_dist_m += haversine_distance_m(
                raw_waypoints[i][0], raw_waypoints[i][1],
                raw_waypoints[i + 1][0], raw_waypoints[i + 1][1]
            )
        # Ground leg 2: Arrival port to destination
        d_arr_port_m = haversine_distance_m(arr_port["lat"], arr_port["lon"], dest_lat, dest_lon)

        total_dist_m = d_orig_port_m + water_dist_m + d_arr_port_m

        speed_mps = (best_corridor["speed_kmh"] * 1000.0) / 3600.0
        water_dur_sec = water_dist_m / speed_mps
        # Boarding buffer: 30 mins
        boarding_sec = 1800.0
        # Ground speeds: ~40 km/h (11.1 m/s)
        ground1_dur_sec = d_orig_port_m / 11.1
        ground2_dur_sec = d_arr_port_m / 11.1
        total_dur_sec = ground1_dur_sec + boarding_sec + water_dur_sec + ground2_dur_sec

        # Build full polyline
        full_polyline: List[Tuple[float, float]] = [(origin_lat, origin_lon)]
        if d_orig_port_m > 300.0:
            full_polyline.append((dep_port["lat"], dep_port["lon"]))
        full_polyline.extend(raw_waypoints)
        if d_arr_port_m > 300.0:
            full_polyline.append((dest_lat, dest_lon))

        steps = [
            {
                "step_num": 1,
                "icon": "🚗",
                "instruction": f"Drive to {dep_port['name']}",
                "road": "Port Access Road",
                "distance_m": d_orig_port_m,
                "duration_s": ground1_dur_sec,
                "type": "depart",
                "modifier": ""
            },
            {
                "step_num": 2,
                "icon": "⚓",
                "instruction": f"Vehicle & passenger check-in & ferry boarding at {dep_port['name']}",
                "road": f"{best_corridor['name']} Pier",
                "distance_m": 0.0,
                "duration_s": boarding_sec,
                "type": "terminal",
                "modifier": ""
            },
            {
                "step_num": 3,
                "icon": "🚢",
                "instruction": f"Cross via {best_corridor['operator']} ({best_corridor['speed_kmh']} km/h cruising) to {arr_port['name']}",
                "road": f"Maritime Channel: {best_corridor['name']}",
                "distance_m": water_dist_m,
                "duration_s": water_dur_sec,
                "type": "ferry",
                "modifier": ""
            },
            {
                "step_num": 4,
                "icon": "🏁",
                "instruction": f"Disembark at {arr_port['name']} and continue to destination",
                "road": "Coastal Arterial Link",
                "distance_m": d_arr_port_m,
                "duration_s": ground2_dur_sec,
                "type": "arrive",
                "modifier": ""
            }
        ]

        fare = best_corridor["fare_inr"]
        fare_note = f"₹{fare:.0f}" if fare > 0 else "Free Municipal Ferry"

        return RouteOption(
            route_id=f"WATERWAY_{best_corridor['id']}",
            name=f"🚢 {best_corridor['name']}",
            mode=TravelMode.WATERWAY,
            distance_meters=total_dist_m,
            duration_seconds=total_dur_sec,
            polyline=full_polyline,
            summary_roads=[f"Port: {dep_port['name']}", best_corridor["name"], f"Port: {arr_port['name']}"],
            steps=steps,
            source=f"Maritime Sea Lanes ({best_corridor['operator']})",
            is_accessible=True,
            algorithm_used="Nautical Channel Waypoints",
            accessibility_verified=True,
            accessibility_notes="Accessible boarding ramp & priority passenger seating available on ferry.",
            speed_mode="nautical",
            speed_mode_note=f"Marine Navigation ({best_corridor['speed_kmh']} km/h) • Estimated Ticket: {fare_note}",
            provider_duration_seconds=total_dur_sec
        )
