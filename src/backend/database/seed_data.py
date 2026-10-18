"""
Seed Data Generator for Next-Gen Maps Backend
Populates initial users, vehicles, places, entrances, parking, transit, and road network.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from src.backend.auth.security import hash_password
from src.backend.database.connection import SessionLocal
from src.backend.database.models import (
    User, UserPreferences, VehicleProfile, Place, PlaceEntrance, PlaceParking,
    PlaceReview, RoadSegment, TransitStop, TransitSchedule, VisualLandmark,
    OfflinePackage, RoadConditionReport
)

logger = logging.getLogger("pathfinder.seed")


def seed_database(db: Session = None):
    close_db_when_done = False
    if db is None:
        db = SessionLocal()
        close_db_when_done = True

    try:
        # Check if already seeded
        if db.query(User).filter(User.email == "admin@pathfinder.org").first():
            logger.info("Database is already seeded.")
            return

        logger.info("Seeding initial database records...")

        # 1. Admin User
        admin_user = User(
            email="admin@pathfinder.org",
            username="admin",
            hashed_password=hash_password("AdminPassword123!"),
            full_name="P.A.T.H.F.I.N.D.E.R. System Administrator",
            role="ADMIN",
            is_active=True
        )
        db.add(admin_user)
        db.flush()

        admin_prefs = UserPreferences(
            user_id=admin_user.id,
            default_routing_profile="FASTEST",
            require_accessible=False,
            share_location_consent=True
        )
        db.add(admin_prefs)

        # 2. Standard Demo User
        demo_user = User(
            email="user@pathfinder.org",
            username="demonavigator",
            hashed_password=hash_password("UserPassword123!"),
            full_name="Navin Sharma",
            role="USER",
            is_active=True
        )
        db.add(demo_user)
        db.flush()

        user_prefs = UserPreferences(
            user_id=demo_user.id,
            default_routing_profile="ECO",
            require_accessible=True,
            avoid_stairs=True,
            prefer_curb_ramps=True,
            prefer_well_lit=True,
            share_location_consent=True
        )
        db.add(user_prefs)

        # Vehicles for demo user
        sedan = VehicleProfile(
            user_id=demo_user.id,
            name="Honda City 1.5 i-VTEC",
            vehicle_type="CAR",
            fuel_type="PETROL",
            fuel_efficiency_km_per_litre=16.5,
            is_default=True
        )
        ev_scooter = VehicleProfile(
            user_id=demo_user.id,
            name="Ather 450X Gen 3",
            vehicle_type="EV",
            fuel_type="ELECTRIC",
            battery_capacity_kwh=3.7,
            electric_range_km=105.0,
            current_charge_percent=85.0,
            connector_type="Type 2",
            is_default=False
        )
        db.add_all([sedan, ev_scooter])

        # 3. Places with Entrances, Parking & Amenities
        places_data = [
            {
                "name": "Vignan University Main Campus",
                "category": "UNIVERSITY",
                "lat": 16.2335,
                "lon": 80.5505,
                "address": "Vadlamudi, Chebrolu Mandal, Guntur, Andhra Pradesh 522213",
                "rating": 4.8,
                "reviews_count": 3400,
                "price_level": 1,
                "amenities": ["wifi", "parking", "wheelchair_ramp", "restrooms", "cafeteria", "outlets", "first_aid"],
                "is_accessible": True,
                "description": "Premier Deemed-to-be University campus sprawling across lush green acreage in Vadlamudi.",
                "entrances": [
                    {"name": "Main Entrance Gate 1 (West Arch)", "type": "MAIN", "lat": 16.2325, "lon": 80.5490, "accessible": True},
                    {"name": "North Gate (Library & CSE Access)", "type": "PEDESTRIAN", "lat": 16.2348, "lon": 80.5515, "accessible": True},
                    {"name": "Emergency Medical Gate (Health Center)", "type": "EMERGENCY", "lat": 16.2340, "lon": 80.5530, "accessible": True}
                ],
                "parking": [
                    {"name": "Central Visitor Parking Plaza", "lat": 16.2322, "lon": 80.5488, "capacity": 150, "ev": True, "fee": 0.0},
                    {"name": "North Staff & Student Two-Wheeler Bay", "lat": 16.2350, "lon": 80.5520, "capacity": 300, "ev": False, "fee": 0.0}
                ]
            },
            {
                "name": "NTR Vignan Central Library",
                "category": "LIBRARY",
                "lat": 16.2338,
                "lon": 80.5512,
                "address": "Vignan University Central Zone",
                "rating": 4.9,
                "reviews_count": 890,
                "price_level": 1,
                "amenities": ["wifi", "outlets", "quiet_zone", "air_conditioned", "wheelchair_ramp", "digital_catalog"],
                "is_accessible": True,
                "description": "Multi-tier state-of-the-art digital knowledge center with high-speed fiber internet and study pods.",
                "entrances": [
                    {"name": "Ground Floor Ramp Entrance", "type": "MAIN", "lat": 16.2338, "lon": 80.5512, "accessible": True}
                ],
                "parking": []
            },
            {
                "name": "Artisan Coffee Roastery & Lounge",
                "category": "CAFE",
                "lat": 16.2370,
                "lon": 80.5440,
                "address": "Tenali Road, Near Vadlamudi Junction",
                "rating": 4.7,
                "reviews_count": 520,
                "price_level": 2,
                "amenities": ["wifi", "outlets", "vegan", "outdoor_seating", "parking", "wheelchair_ramp", "family_friendly"],
                "is_accessible": True,
                "description": "Cozy specialty coffee lounge with hand-crafted pour-overs, artisan sandwiches, and quiet work spaces.",
                "entrances": [
                    {"name": "Front Glass Door Entrance", "type": "MAIN", "lat": 16.2370, "lon": 80.5440, "accessible": True}
                ],
                "parking": [
                    {"name": "Cafe Dedicated Customer Parking", "lat": 16.2369, "lon": 80.5442, "capacity": 20, "ev": True, "fee": 0.0}
                ]
            },
            {
                "name": "Royal Spice Multi-Cuisine Diner",
                "category": "RESTAURANT",
                "lat": 16.2410,
                "lon": 80.5600,
                "address": "Vadlamudi - Tenali Highway Corridor",
                "rating": 4.6,
                "reviews_count": 1280,
                "price_level": 2,
                "amenities": ["vegan", "vegetarian_options", "parking", "air_conditioned", "family_friendly", "takeaway"],
                "is_accessible": True,
                "description": "Popular family restaurant serving traditional Andhra thalis, clay pot biryanis, and North Indian curries.",
                "entrances": [
                    {"name": "Main Entrance Arch", "type": "MAIN", "lat": 16.2410, "lon": 80.5600, "accessible": True}
                ],
                "parking": [
                    {"name": "Diner Valet & Self Parking Lot", "lat": 16.2412, "lon": 80.5602, "capacity": 45, "ev": False, "fee": 0.0}
                ]
            },
            {
                "name": "Tenali Multi-Speciality Community Hospital",
                "category": "HOSPITAL",
                "lat": 16.2450,
                "lon": 80.6400,
                "address": "Bypass Road, Tenali, Andhra Pradesh",
                "rating": 4.8,
                "reviews_count": 1420,
                "price_level": 2,
                "amenities": ["wheelchair_ramp", "elevator", "parking", "first_aid", "pharmacy", "emergency_room"],
                "is_accessible": True,
                "description": "24/7 Trauma and acute care emergency healthcare center equipped with ambulance bays.",
                "entrances": [
                    {"name": "Emergency Trauma Ambulance Bay", "type": "EMERGENCY", "lat": 16.2452, "lon": 80.6402, "accessible": True},
                    {"name": "OPD Main Reception Gate", "type": "MAIN", "lat": 16.2450, "lon": 80.6398, "accessible": True}
                ],
                "parking": [
                    {"name": "Hospital Underground & Surface Parking", "lat": 16.2448, "lon": 80.6395, "capacity": 80, "ev": True, "fee": 20.0}
                ]
            },
            {
                "name": "Guntur Autonagar EV Fast Supercharger Hub",
                "category": "EV_CHARGING",
                "lat": 16.2890,
                "lon": 80.4550,
                "address": "NH16 Express Corridor, Autonagar, Guntur",
                "rating": 4.9,
                "reviews_count": 310,
                "price_level": 2,
                "amenities": ["ev_charging", "restrooms", "wifi", "cafe", "air_conditioned"],
                "is_accessible": True,
                "description": "60kW dual-gun DC Fast Charging Station compatible with CCS2 and Type-2 EVs.",
                "entrances": [
                    {"name": "Charging Bay Drive-Through Entrance", "type": "VEHICLE", "lat": 16.2890, "lon": 80.4550, "accessible": True}
                ],
                "parking": [
                    {"name": "Dedicated EV Charge Bays", "lat": 16.2890, "lon": 80.4550, "capacity": 8, "ev": True, "fee": 150.0}
                ]
            }
        ]

        for p_data in places_data:
            place = Place(
                name=p_data["name"],
                category=p_data["category"],
                latitude=p_data["lat"],
                longitude=p_data["lon"],
                address=p_data["address"],
                rating=p_data["rating"],
                reviews_count=p_data["reviews_count"],
                price_level=p_data["price_level"],
                amenities=p_data["amenities"],
                is_accessible=p_data["is_accessible"],
                description=p_data["description"]
            )
            db.add(place)
            db.flush()

            for ent in p_data["entrances"]:
                entrance = PlaceEntrance(
                    place_id=place.id,
                    name=ent["name"],
                    entrance_type=ent["type"],
                    latitude=ent["lat"],
                    longitude=ent["lon"],
                    is_wheelchair_accessible=ent["accessible"],
                    has_curb_ramp=ent["accessible"]
                )
                db.add(entrance)

            for prk in p_data["parking"]:
                parking = PlaceParking(
                    place_id=place.id,
                    name=prk["name"],
                    latitude=prk["lat"],
                    longitude=prk["lon"],
                    capacity=prk["capacity"],
                    has_ev_charging=prk["ev"],
                    hourly_rate_inr=prk["fee"]
                )
                db.add(parking)

        # 4. Transit Stops & Schedules
        stops = [
            TransitStop(id="STOP_VIGNAN", name="Vignan University Transit Terminal", transit_type="BUS", latitude=16.2335, longitude=80.5505, is_wheelchair_accessible=True),
            TransitStop(id="STOP_VADLAMUDI", name="Vadlamudi Junction Bus Stand", transit_type="BUS", latitude=16.2385, longitude=80.5420, is_wheelchair_accessible=True),
            TransitStop(id="STOP_TENALI", name="Tenali Central Bus Station & Rail Terminal", transit_type="BUS", latitude=16.2420, longitude=80.6450, is_wheelchair_accessible=True),
            TransitStop(id="STOP_GUNTUR", name="Guntur NTR RTC Bus Complex", transit_type="BUS", latitude=16.3067, longitude=80.4365, is_wheelchair_accessible=True)
        ]
        db.add_all(stops)
        db.flush()

        schedules = [
            TransitSchedule(id="SCHED_VIG_TEN_1", route_name="Line 22 - Vadlamudi to Tenali Express", from_stop_id="STOP_VIGNAN", to_stop_id="STOP_TENALI", departure_time="08:00", arrival_time="08:35", fare_inr=25.0, frequency_minutes=15),
            TransitSchedule(id="SCHED_VIG_GUN_1", route_name="Line 14 - Vadlamudi to Guntur City", from_stop_id="STOP_VIGNAN", to_stop_id="STOP_GUNTUR", departure_time="08:15", arrival_time="09:05", fare_inr=35.0, frequency_minutes=20)
        ]
        db.add_all(schedules)

        # 5. Visual Landmarks
        landmarks = [
            VisualLandmark(
                name="Vignan University Main Gateway Arch",
                latitude=16.2325,
                longitude=80.5490,
                heading_facing_degrees=90.0,
                visual_cue_description="Grand neoclassical white arch with golden university emblem and security boom barriers.",
                turn_reference_instruction="Proceed straight through the main arch to enter the university campus.",
                is_verified=True
            ),
            VisualLandmark(
                name="Vadlamudi Overbridge & Clock Tower",
                latitude=16.2385,
                longitude=80.5420,
                heading_facing_degrees=0.0,
                visual_cue_description="Elevated road junction with prominent four-faced clock tower at the roundabout.",
                turn_reference_instruction="Take the second exit at the clock tower roundabout towards Tenali.",
                is_verified=True
            )
        ]
        db.add_all(landmarks)

        # 6. Offline Map Package
        pkg = OfflinePackage(
            id="PKG_VIGNAN_GUNTUR_V1",
            region_name="Vignan University - Tenali - Guntur Regional District",
            version="1.0.0",
            min_latitude=16.1500,
            min_longitude=80.4000,
            max_latitude=16.3500,
            max_longitude=80.7000,
            file_size_bytes=1420580,
            sha256_checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            download_url="/api/v2/offline/packages/PKG_VIGNAN_GUNTUR_V1/download",
            poi_count=97,
            road_segment_count=45
        )
        db.add(pkg)

        # 7. Sample Initial Road Condition Report (Verified road closure for construction)
        sample_report = RoadConditionReport(
            reporter_id=admin_user.id,
            reporter_type="VERIFIED_OPERATOR",
            category="ROAD_CLOSURE",
            severity="HIGH",
            status="VERIFIED",
            latitude=16.2350,
            longitude=80.5050,
            affected_radius_meters=150.0,
            road_name="Sangam Jagarlamudi Canal Bridge",
            description="Bridge resurfacing and expansion joint reconstruction. Detour via Narakodur Junction.",
            confidence_score=0.98,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            verified_at=datetime.now(timezone.utc)
        )
        db.add(sample_report)

        db.commit()
        logger.info("Database seeding successfully completed.")

    except Exception as e:
        db.rollback()
        logger.error(f"Error during database seed: {e}")
        raise
    finally:
        if close_db_when_done:
            db.close()
