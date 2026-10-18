"""
Backend Configuration & Settings Management
Uses environment variables with safe defaults for local development and production.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    # Application & Environment
    APP_NAME: str = "P.A.T.H.F.I.N.D.E.R. Next-Gen Maps Backend"
    APP_VERSION: str = "2.5.0"
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"))
    
    # Database
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./data/pathfinder_maps.db")
    )
    
    # Security & JWT Auth
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY", "pathfinder-nextgen-maps-secret-key-production-389102")
    )
    JWT_ALGORITHM: str = Field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    )
    
    # Geospatial & External Providers
    OSRM_BASE_URL: str = Field(
        default_factory=lambda: os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org")
    )
    ROUTING_TIMEOUT_SEC: float = Field(
        default_factory=lambda: float(os.getenv("ROUTING_TIMEOUT_SEC", "4.0"))
    )
    NOMINATIM_BASE_URL: str = Field(
        default_factory=lambda: os.getenv("NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org")
    )
    OPEN_METEO_BASE_URL: str = Field(
        default_factory=lambda: os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1")
    )
    GOOGLE_MAPS_API_KEY: str = Field(
        default_factory=lambda: os.getenv("GOOGLE_MAPS_API_KEY", "")
    )
    
    # Default Center Coordinates (Vignan / Vadlamudi / Tenali / Guntur)
    DEFAULT_LATITUDE: float = Field(
        default_factory=lambda: float(os.getenv("DEFAULT_LATITUDE", "16.2335"))
    )
    DEFAULT_LONGITUDE: float = Field(
        default_factory=lambda: float(os.getenv("DEFAULT_LONGITUDE", "80.5505"))
    )
    
    # Offline Packages Directory
    OFFLINE_PACKAGES_DIR: str = Field(
        default_factory=lambda: os.getenv("OFFLINE_PACKAGES_DIR", "./data/offline_packages")
    )
    
    # Fuel & Energy Cost Baselines (INR / Litre & kWh)
    DEFAULT_PETROL_PRICE_PER_LITRE: float = 104.50
    DEFAULT_DIESEL_PRICE_PER_LITRE: float = 92.50
    DEFAULT_ELECTRICITY_PRICE_PER_KWH: float = 8.50
    
    # Road Report Thresholds
    REPORT_DUPLICATE_DISTANCE_METERS: float = 50.0
    MIN_CONFIDENCE_FOR_ROUTE_AVOIDANCE: float = 0.65


settings = Settings()
