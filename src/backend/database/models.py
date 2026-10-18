"""
Comprehensive Database Models for Next-Generation Maps Backend
Supports spatial entities, users, vehicle profiles, places, entrances, road reports,
multimodal transit, collaborative trips, offline packages, and audit trails.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey,
    Enum, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship

from src.backend.database.connection import Base


def utcnow():
    return datetime.now(timezone.utc)


# =============================================================================
# 1. USERS, PREFERENCES & VEHICLE PROFILES
# =============================================================================

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=True)
    role = Column(String(50), default="USER", nullable=False)  # USER, TRUSTED_REPORTER, ADMIN, DISPATCHER
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    vehicles = relationship("VehicleProfile", back_populates="user", cascade="all, delete-orphan")
    saved_routes = relationship("SavedRoute", back_populates="user", cascade="all, delete-orphan")
    saved_places = relationship("SavedPlace", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("RoadConditionReport", back_populates="reporter")


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Routing Preferences
    default_routing_profile = Column(String(50), default="FASTEST")  # FASTEST, SHORTEST, ECO, FEWER_TOLLS, ROAD_QUALITY
    avoid_highways = Column(Boolean, default=False)
    avoid_tolls = Column(Boolean, default=False)
    avoid_unpaved = Column(Boolean, default=True)
    
    # Accessibility Preferences
    require_accessible = Column(Boolean, default=False)
    avoid_stairs = Column(Boolean, default=False)
    prefer_curb_ramps = Column(Boolean, default=False)
    max_incline_percent = Column(Float, default=8.0)
    prefer_well_lit = Column(Boolean, default=False)
    audio_guidance_enabled = Column(Boolean, default=True)
    
    # Location & Privacy Preferences
    share_location_consent = Column(Boolean, default=False)
    retain_location_history = Column(Boolean, default=False)
    
    # Relationship
    user = relationship("User", back_populates="preferences")


class VehicleProfile(Base):
    __tablename__ = "vehicle_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # e.g., "Family Sedan", "Ather EV", "Commercial Truck"
    vehicle_type = Column(String(50), nullable=False)  # CAR, MOTORCYCLE, EV, BICYCLE, COMMERCIAL_TRUCK
    fuel_type = Column(String(50), default="PETROL")  # PETROL, DIESEL, ELECTRIC, HYBRID, NONE
    
    # Efficiency & Range
    fuel_efficiency_km_per_litre = Column(Float, default=15.0)  # for ICE
    battery_capacity_kwh = Column(Float, default=0.0)          # for EV
    electric_range_km = Column(Float, default=0.0)             # for EV
    current_charge_percent = Column(Float, default=100.0)      # for EV
    connector_type = Column(String(50), default="CCS2")        # Type 2, CCS2, CHAdeMO
    
    # Dimensions & Restrictions (Commercial/Heavy vehicles)
    height_meters = Column(Float, default=1.5)
    width_meters = Column(Float, default=1.8)
    weight_tons = Column(Float, default=1.5)
    is_commercial = Column(Boolean, default=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="vehicles")


# =============================================================================
# 2. PLACES, ENTRANCES, PARKING & AMENITIES
# =============================================================================

class Place(Base):
    __tablename__ = "places"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # CAFE, RESTAURANT, HOSPITAL, UNIVERSITY, LANDMARK, SHOPPING, EV_CHARGING
    sub_category = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    address = Column(String(300), nullable=True)
    city = Column(String(100), default="Guntur", index=True)
    state = Column(String(100), default="Andhra Pradesh")
    country = Column(String(100), default="India")
    
    # Details & Metrics
    rating = Column(Float, default=4.5)
    reviews_count = Column(Integer, default=0)
    price_level = Column(Integer, default=2)  # 1 (Budget) to 4 (Luxury)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    opening_hours_json = Column(JSON, default=dict)  # {"monday": "09:00-21:00", ...}
    is_open_now = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True)
    verified_at = Column(DateTime, default=utcnow)
    
    # Amenities & Accessibility Tags (Stored as JSON for dynamic filtering)
    amenities = Column(JSON, default=list)  # ["wifi", "outlets", "vegan", "parking", "wheelchair_ramp", "family_friendly"]
    is_accessible = Column(Boolean, default=True)
    accessibility_notes = Column(Text, nullable=True)
    
    # Description & Meta
    description = Column(Text, nullable=True)
    photo_urls = Column(JSON, default=list)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    entrances = relationship("PlaceEntrance", back_populates="place", cascade="all, delete-orphan")
    parking_lots = relationship("PlaceParking", back_populates="place", cascade="all, delete-orphan")
    reviews = relationship("PlaceReview", back_populates="place", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_place_coords", "latitude", "longitude"),
        Index("idx_place_cat_city", "category", "city"),
    )


class PlaceEntrance(Base):
    __tablename__ = "place_entrances"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    place_id = Column(String(36), ForeignKey("places.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)  # "Main Gate", "North Pedestrian Gate", "Emergency ER Entrance"
    entrance_type = Column(String(50), default="MAIN")  # MAIN, PEDESTRIAN, VEHICLE, DELIVERY, EMERGENCY
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Accessibility & Restrictions
    is_wheelchair_accessible = Column(Boolean, default=True)
    has_curb_ramp = Column(Boolean, default=True)
    has_tactile_paving = Column(Boolean, default=False)
    has_automatic_door = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    notes = Column(String(255), nullable=True)

    place = relationship("Place", back_populates="entrances")


class PlaceParking(Base):
    __tablename__ = "place_parking"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    place_id = Column(String(36), ForeignKey("places.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    parking_type = Column(String(50), default="SURFACE")  # SURFACE, UNDERGROUND, MULTI_STORY, TWO_WHEELER
    capacity = Column(Integer, default=50)
    available_spaces = Column(Integer, default=25)
    hourly_rate_inr = Column(Float, default=20.0)
    has_ev_charging = Column(Boolean, default=False)
    has_accessible_spots = Column(Boolean, default=True)
    walking_time_to_entrance_seconds = Column(Integer, default=60)

    place = relationship("Place", back_populates="parking_lots")


class PlaceReview(Base):
    __tablename__ = "place_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    place_id = Column(String(36), ForeignKey("places.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    author_name = Column(String(100), nullable=False)
    rating = Column(Float, nullable=False)
    text = Column(Text, nullable=True)
    helpful_votes = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)

    place = relationship("Place", back_populates="reviews")


# =============================================================================
# 3. ROAD NETWORK & DIGITAL TWIN
# =============================================================================

class RoadSegment(Base):
    __tablename__ = "road_segments"

    id = Column(String(64), primary_key=True)  # Unique identifier or OSM way ID
    name = Column(String(150), nullable=False, index=True)
    road_type = Column(String(50), default="PRIMARY")  # MOTORWAY, TRUNK, PRIMARY, SECONDARY, RESIDENTIAL, PEDESTRIAN
    start_latitude = Column(Float, nullable=False)
    start_longitude = Column(Float, nullable=False)
    end_latitude = Column(Float, nullable=False)
    end_longitude = Column(Float, nullable=False)
    length_meters = Column(Float, nullable=False)
    speed_limit_kmh = Column(Float, default=40.0)
    lane_count = Column(Integer, default=2)
    is_one_way = Column(Boolean, default=False)
    is_toll = Column(Boolean, default=False)
    toll_fee_inr = Column(Float, default=0.0)
    surface_quality = Column(Float, default=0.9)  # 0.0 (Destroyed) to 1.0 (Flawless asphalt)
    has_sidewalk = Column(Boolean, default=True)
    is_illuminated = Column(Boolean, default=True)
    is_wheelchair_accessible = Column(Boolean, default=True)
    geometry_polyline = Column(JSON, default=list)  # [[lat, lon], ...]
    created_at = Column(DateTime, default=utcnow)


# =============================================================================
# 4. REAL-TIME ROAD INTELLIGENCE (INCIDENTS, HAZARDS, COMMUNITY REPORTS)
# =============================================================================

class RoadConditionReport(Base):
    __tablename__ = "road_condition_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    reporter_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reporter_type = Column(String(50), default="COMMUNITY")  # COMMUNITY, VERIFIED_OPERATOR, POLICE, SENSOR
    
    # Classification
    category = Column(String(50), nullable=False, index=True)
    # POTHOLE, FLOODING, ROAD_CLOSURE, ACCIDENT, BROKEN_SIGNAL, DANGEROUS_TURN, PEDESTRIAN_HAZARD, POOR_LIGHTING
    severity = Column(String(50), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(50), default="PENDING", nullable=False, index=True)  # PENDING, VERIFIED, RESOLVED, REJECTED, EXPIRED
    
    # Location
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    affected_radius_meters = Column(Float, default=50.0)
    road_segment_id = Column(String(64), nullable=True)
    road_name = Column(String(150), nullable=True)
    
    # Details & Provenance
    description = Column(Text, nullable=False)
    photo_url = Column(String(500), nullable=True)
    confidence_score = Column(Float, default=0.5)  # 0.0 to 1.0 based on reliability formula
    upvotes = Column(Integer, default=1)
    downvotes = Column(Integer, default=0)
    dispute_count = Column(Integer, default=0)
    
    # Lifecycle
    created_at = Column(DateTime, default=utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    verified_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    reporter = relationship("User", back_populates="reports")
    confirmations = relationship("ReportConfirmation", back_populates="report", cascade="all, delete-orphan")
    audit_logs = relationship("ReportAuditLog", back_populates="report", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_reports_spatial", "latitude", "longitude", "status"),
    )


class ReportConfirmation(Base):
    __tablename__ = "report_confirmations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("road_condition_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmation_type = Column(String(50), nullable=False)  # STILL_PRESENT, CLEARED, DISPUTE, ABUSE
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    report = relationship("RoadConditionReport", back_populates="confirmations")


class ReportAuditLog(Base):
    __tablename__ = "report_audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("road_condition_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(100), nullable=False)  # CREATED, CONFIRMED, DISPUTED, STATUS_CHANGED, EXPIRED
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=True)
    performed_by = Column(String(100), default="SYSTEM")
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    report = relationship("RoadConditionReport", back_populates="audit_logs")


# =============================================================================
# 5. SAVED ROUTES & SAVED PLACES
# =============================================================================

class SavedRoute(Base):
    __tablename__ = "saved_routes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    origin_name = Column(String(150), nullable=False)
    origin_lat = Column(Float, nullable=False)
    origin_lon = Column(Float, nullable=False)
    dest_name = Column(String(150), nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_lon = Column(Float, nullable=False)
    travel_mode = Column(String(50), default="DRIVING")
    distance_km = Column(Float, nullable=False)
    duration_minutes = Column(Float, nullable=False)
    polyline = Column(JSON, default=list)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="saved_routes")


class SavedPlace(Base):
    __tablename__ = "saved_places"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    place_id = Column(String(36), ForeignKey("places.id", ondelete="CASCADE"), nullable=True)
    custom_label = Column(String(100), nullable=False)  # "Home", "Work", "Vignan Lab", "Favorite Diner"
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="saved_places")


# =============================================================================
# 6. MULTIMODAL PUBLIC TRANSIT & ITINERARIES
# =============================================================================

class TransitStop(Base):
    __tablename__ = "transit_stops"

    id = Column(String(50), primary_key=True)
    name = Column(String(150), nullable=False, index=True)
    transit_type = Column(String(50), default="BUS")  # BUS, METRO, TRAIN
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_wheelchair_accessible = Column(Boolean, default=True)


class TransitSchedule(Base):
    __tablename__ = "transit_schedules"

    id = Column(String(50), primary_key=True)
    route_name = Column(String(100), nullable=False, index=True)  # "Line 22 Vadlamudi Express"
    from_stop_id = Column(String(50), ForeignKey("transit_stops.id"), nullable=False)
    to_stop_id = Column(String(50), ForeignKey("transit_stops.id"), nullable=False)
    departure_time = Column(String(10), nullable=False)  # "08:15"
    arrival_time = Column(String(10), nullable=False)    # "08:45"
    fare_inr = Column(Float, default=25.0)
    frequency_minutes = Column(Integer, default=15)
    is_live_tracking_supported = Column(Boolean, default=True)


# =============================================================================
# 7. WEATHER OBSERVATIONS & HAZARDS
# =============================================================================

class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temperature_c = Column(Float, nullable=False)
    precipitation_mm_per_hr = Column(Float, default=0.0)
    wind_speed_kmh = Column(Float, default=0.0)
    visibility_km = Column(Float, default=10.0)
    condition_code = Column(String(50), default="CLEAR")  # CLEAR, RAIN, HEAVY_RAIN, THUNDERSTORM, FOG, EXTREME_HEAT
    is_active_hazard = Column(Boolean, default=False)
    hazard_warning = Column(String(255), nullable=True)
    recorded_at = Column(DateTime, default=utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    __table_args__ = (
        Index("idx_weather_spatial", "latitude", "longitude", "expires_at"),
    )


# =============================================================================
# 8. COLLABORATIVE MAPS & TRIP PLANNING
# =============================================================================

class CollaborativeMap(Base):
    __tablename__ = "collaborative_maps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    share_token = Column(String(64), unique=True, nullable=False, index=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    members = relationship("MapMember", back_populates="collab_map", cascade="all, delete-orphan")
    stops = relationship("CollaborativeStop", back_populates="collab_map", cascade="all, delete-orphan", order_by="CollaborativeStop.sequence_order")
    audit_logs = relationship("CollabAuditLog", back_populates="collab_map", cascade="all, delete-orphan")


class MapMember(Base):
    __tablename__ = "map_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    map_id = Column(String(36), ForeignKey("collaborative_maps.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), default="VIEWER")  # OWNER, EDITOR, VIEWER
    joined_at = Column(DateTime, default=utcnow)

    collab_map = relationship("CollaborativeMap", back_populates="members")
    __table_args__ = (UniqueConstraint("map_id", "user_id", name="uq_map_member"),)


class CollaborativeStop(Base):
    __tablename__ = "collaborative_stops"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    map_id = Column(String(36), ForeignKey("collaborative_maps.id", ondelete="CASCADE"), nullable=False)
    suggested_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(150), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    sequence_order = Column(Integer, default=1)
    planned_arrival = Column(DateTime, nullable=True)
    vote_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)

    collab_map = relationship("CollaborativeMap", back_populates="stops")
    votes = relationship("StopVote", back_populates="stop", cascade="all, delete-orphan")


class StopVote(Base):
    __tablename__ = "stop_votes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stop_id = Column(String(36), ForeignKey("collaborative_stops.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    vote_value = Column(Integer, default=1)  # +1 or -1
    created_at = Column(DateTime, default=utcnow)

    stop = relationship("CollaborativeStop", back_populates="votes")
    __table_args__ = (UniqueConstraint("stop_id", "user_id", name="uq_stop_vote"),)


class CollabAuditLog(Base):
    __tablename__ = "collab_audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    map_id = Column(String(36), ForeignKey("collaborative_maps.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), nullable=True)
    action = Column(String(100), nullable=False)  # ADD_STOP, DELETE_STOP, REORDER, INVITE_MEMBER
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utcnow)

    collab_map = relationship("CollaborativeMap", back_populates="audit_logs")


# =============================================================================
# 9. VISUAL & CAMERA-ASSISTED NAVIGATION LANDMARKS
# =============================================================================

class VisualLandmark(Base):
    __tablename__ = "visual_landmarks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(150), nullable=False)  # "Vignan Main Entrance Arch", "NTR Library Clock Tower"
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    elevation_meters = Column(Float, default=0.0)
    heading_facing_degrees = Column(Float, default=0.0)  # Visual face bearing
    visual_cue_description = Column(String(300), nullable=False)  # "Tall white gateway arch with golden insignia"
    turn_reference_instruction = Column(String(255), nullable=True)  # "Take left immediately after passing this arch"
    photo_url = Column(String(500), nullable=True)
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


# =============================================================================
# 10. OFFLINE MAP PACKAGES
# =============================================================================

class OfflinePackage(Base):
    __tablename__ = "offline_packages"

    id = Column(String(64), primary_key=True)  # e.g., "PKG_VIGNAN_CAMPUS_V1", "PKG_GUNTUR_DIST_V1"
    region_name = Column(String(150), nullable=False)
    version = Column(String(20), default="1.0.0")
    min_latitude = Column(Float, nullable=False)
    min_longitude = Column(Float, nullable=False)
    max_latitude = Column(Float, nullable=False)
    max_longitude = Column(Float, nullable=False)
    file_size_bytes = Column(Integer, default=0)
    sha256_checksum = Column(String(64), nullable=False)
    download_url = Column(String(300), nullable=False)
    compatible_app_version = Column(String(50), default=">=2.0.0")
    poi_count = Column(Integer, default=0)
    road_segment_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)
    expires_at = Column(DateTime, nullable=True)


# =============================================================================
# 11. DATA INGESTION JOBS & PROVENANCE AUDIT
# =============================================================================

class DataIngestionJob(Base):
    __tablename__ = "data_ingestion_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider_name = Column(String(100), nullable=False)  # OPEN_STREET_MAP, GTFS_APSRTC, OPEN_METEO, CROWD_REPORT
    data_type = Column(String(50), nullable=False)       # ROADS, PLACES, TRANSIT_SCHEDULES, WEATHER
    records_ingested = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    status = Column(String(50), default="COMPLETED")     # RUNNING, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)


# =============================================================================
# 12. LIVE VIRTUAL TRAVEL COMPANION & NAVIGATION SESSIONS
# =============================================================================

class NavigationSession(Base):
    __tablename__ = "navigation_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    route_id = Column(String(64), nullable=False, default="ROUTE_ACTIVE")
    route_version = Column(Integer, default=1, nullable=False)
    origin_name = Column(String(200), nullable=False)
    origin_lat = Column(Float, nullable=False)
    origin_lon = Column(Float, nullable=False)
    dest_name = Column(String(200), nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_lon = Column(Float, nullable=False)
    entrance_id = Column(String(36), ForeignKey("place_entrances.id", ondelete="SET NULL"), nullable=True)
    
    # Mode: WALKING, RUNNING, DRIVING, CYCLING, MOTORCYCLE, TRANSIT
    travel_mode = Column(String(50), default="WALKING", nullable=False)
    
    # State Machine State:
    # IDLE, ROUTE_READY, STARTING, MOVING, APPROACHING_TURN, TURNING, TEMPORARILY_STOPPED,
    # TRAFFIC_DELAY, OFF_ROUTE, REROUTING, GPS_UNCERTAIN, RESUMING, ARRIVED, PAUSED, CANCELLED
    status = Column(String(50), default="ROUTE_READY", nullable=False)
    
    current_step_index = Column(Integer, default=0, nullable=False)
    current_step_id = Column(String(36), nullable=True)
    completed_steps_count = Column(Integer, default=0, nullable=False)
    total_steps_count = Column(Integer, default=0, nullable=False)
    
    current_lat = Column(Float, nullable=False)
    current_lon = Column(Float, nullable=False)
    current_speed_kmh = Column(Float, default=0.0, nullable=False)
    current_heading = Column(Float, default=0.0, nullable=False)
    accuracy_meters = Column(Float, default=5.0, nullable=False)
    
    progress_percent = Column(Float, default=0.0, nullable=False)
    distance_remaining_meters = Column(Float, default=0.0, nullable=False)
    duration_remaining_seconds = Column(Float, default=0.0, nullable=False)
    total_distance_meters = Column(Float, default=0.0, nullable=False)
    total_duration_seconds = Column(Float, default=0.0, nullable=False)
    
    is_traffic_delay = Column(Boolean, default=False, nullable=False)
    consecutive_stops_count = Column(Integer, default=0, nullable=False)
    consecutive_moving_count = Column(Integer, default=0, nullable=False)
    
    polyline_json = Column(JSON, default=list)
    metadata_json = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    steps = relationship("NavigationRouteStep", back_populates="session", cascade="all, delete-orphan", order_by="NavigationRouteStep.sequence_number")
    checkpoints = relationship("NavigationCheckpoint", back_populates="session", cascade="all, delete-orphan", order_by="NavigationCheckpoint.sequence_number")
    events = relationship("NavigationProgressEvent", back_populates="session", cascade="all, delete-orphan", order_by="NavigationProgressEvent.timestamp")


class NavigationRouteStep(Base):
    __tablename__ = "navigation_route_steps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("navigation_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    route_version = Column(Integer, default=1, nullable=False)
    sequence_number = Column(Integer, nullable=False, index=True)
    step_key = Column(String(50), nullable=False)  # Stable ID e.g. "STEP_0"
    
    instruction_type = Column(String(50), default="STRAIGHT", nullable=False)  # START, STRAIGHT, LEFT, RIGHT, SLIGHT_LEFT, SLIGHT_RIGHT, U_TURN, ROUNDABOUT, TRANSIT_BOARD, TRANSIT_ALIGHT, CROSSING, ENTRANCE, ARRIVE
    instruction_text = Column(String(300), nullable=False)
    road_name = Column(String(150), nullable=True)
    start_lat = Column(Float, nullable=False)
    start_lon = Column(Float, nullable=False)
    end_lat = Column(Float, nullable=False)
    end_lon = Column(Float, nullable=False)
    distance_meters = Column(Float, default=0.0, nullable=False)
    duration_seconds = Column(Float, default=0.0, nullable=False)
    
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    is_superseded = Column(Boolean, default=False, nullable=False)
    icon = Column(String(20), default="📍", nullable=False)
    visual_cue = Column(String(255), nullable=True)
    
    session = relationship("NavigationSession", back_populates="steps")


class NavigationCheckpoint(Base):
    __tablename__ = "navigation_checkpoints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("navigation_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id = Column(String(36), ForeignKey("navigation_route_steps.id", ondelete="SET NULL"), nullable=True)
    
    checkpoint_type = Column(String(50), nullable=False)  # START, INTERSECTION, TURN, PEDESTRIAN_CROSSING, TRANSPORT_STOP, TRANSFER_POINT, ROAD_TRANSITION, ENTRANCE, DESTINATION
    name = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    sequence_number = Column(Integer, nullable=False, index=True)
    radius_meters = Column(Float, default=35.0, nullable=False)
    completion_action = Column(String(50), default="AUTO_PROXIMITY", nullable=False)  # AUTO_PROXIMITY, MANUAL_CONFIRM, USER_PASS
    
    is_reached = Column(Boolean, default=False, nullable=False)
    reached_at = Column(DateTime, nullable=True)
    display_badge = Column(String(20), default="🚩", nullable=False)
    
    session = relationship("NavigationSession", back_populates="checkpoints")


class NavigationProgressEvent(Base):
    __tablename__ = "navigation_progress_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("navigation_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(60), nullable=False)  # START, MOVEMENT_UPDATE, STOP, RESUME, TURN_APPROACH, TURN_EXECUTED, CHECKPOINT_REACHED, STEP_COMPLETED, OFF_ROUTE_DETECTED, REROUTE_COMPLETED, GPS_UNCERTAIN, TRAFFIC_DELAY_ENTER, TRAFFIC_DELAY_EXIT, ARRIVAL, PAUSE, CANCEL
    state = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed_kmh = Column(Float, default=0.0, nullable=False)
    heading = Column(Float, default=0.0, nullable=False)
    accuracy_meters = Column(Float, default=5.0, nullable=False)
    step_index = Column(Integer, default=0, nullable=False)
    checkpoint_id = Column(String(36), nullable=True)
    details = Column(String(300), nullable=True)
    timestamp = Column(DateTime, default=utcnow, nullable=False)
    idempotency_key = Column(String(100), nullable=True, index=True)
    
    session = relationship("NavigationSession", back_populates="events")

