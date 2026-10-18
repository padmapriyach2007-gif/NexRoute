"""
Offline Map Package Service
Generates, packages, and serves versioned offline geographic datasets with
bounding-box manifests, POIs, routing topology, and SHA-256 integrity checksums.
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from src.backend.config import settings
from src.backend.database.models import OfflinePackage, Place, RoadSegment


class OfflinePackageService:
    @staticmethod
    def list_available_packages(db: Session) -> List[Dict[str, Any]]:
        packages = db.query(OfflinePackage).all()
        return [
            {
                "package_id": p.id,
                "region_name": p.region_name,
                "version": p.version,
                "bounding_box": {
                    "min_latitude": p.min_latitude,
                    "min_longitude": p.min_longitude,
                    "max_latitude": p.max_latitude,
                    "max_longitude": p.max_longitude
                },
                "file_size_bytes": p.file_size_bytes,
                "sha256_checksum": p.sha256_checksum,
                "download_url": p.download_url,
                "poi_count": p.poi_count,
                "road_segment_count": p.road_segment_count,
                "compatible_app_version": p.compatible_app_version
            }
            for p in packages
        ]

    @staticmethod
    def generate_package_payload(db: Session, package_id: str) -> Dict[str, Any]:
        """
        Synthesizes the complete offline data payload (POIs, entrances, road segments)
        for client-side offline storage and navigation.
        """
        pkg = db.query(OfflinePackage).filter(OfflinePackage.id == package_id).first()
        if not pkg:
            raise ValueError(f"Package {package_id} not found")

        # Fetch places in package bounding box
        places = db.query(Place).filter(
            Place.latitude.between(pkg.min_latitude, pkg.max_latitude),
            Place.longitude.between(pkg.min_longitude, pkg.max_longitude)
        ).all()

        features = []
        for p in places:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [p.longitude, p.latitude]
                },
                "properties": {
                    "id": p.id,
                    "name": p.name,
                    "category": p.category,
                    "rating": p.rating,
                    "amenities": p.amenities,
                    "is_accessible": p.is_accessible,
                    "entrances": [
                        {
                            "name": e.name,
                            "type": e.entrance_type,
                            "coordinates": [e.longitude, e.latitude],
                            "accessible": e.is_wheelchair_accessible
                        }
                        for e in p.entrances
                    ]
                }
            })

        payload = {
            "format": "PathfinderOfflineMapBundle",
            "package_id": pkg.id,
            "region_name": pkg.region_name,
            "version": pkg.version,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "bounding_box": [pkg.min_latitude, pkg.min_longitude, pkg.max_latitude, pkg.max_longitude],
            "feature_collection": {
                "type": "FeatureCollection",
                "features": features
            },
            "offline_capabilities": {
                "client_side_poi_search": True,
                "client_side_turn_by_turn": True,
                "live_traffic_supported": False,  # requires server connection
                "community_reports_supported": False  # requires server connection
            }
        }

        # Calculate checksum
        serialized = json.dumps(payload, sort_keys=True)
        checksum = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        pkg.sha256_checksum = checksum
        pkg.file_size_bytes = len(serialized.encode("utf-8"))
        pkg.poi_count = len(places)
        db.commit()

        return payload
