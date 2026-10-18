"""
AI-Powered Place Discovery Service
Parses natural-language queries, performs structured geospatial and amenity filtering,
provides explainable ranking rationale, and generates place comparisons.
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session

from src.hazard_map import haversine_distance_m
from src.backend.database.models import Place


AMENITY_KEYWORDS = {
    "wifi": ["wifi", "internet", "wi-fi", "wireless"],
    "outlets": ["outlet", "outlets", "charging", "plug", "socket", "power"],
    "vegan": ["vegan", "vegetarian", "pure veg", "plant-based"],
    "parking": ["parking", "garage", "valet", "car park"],
    "wheelchair_ramp": ["wheelchair", "accessible", "ramp", "step-free", "disability"],
    "quiet_zone": ["quiet", "peaceful", "silent", "study"],
    "outdoor_seating": ["outdoor", "patio", "terrace", "open air", "garden"],
    "family_friendly": ["family", "kids", "children"],
    "ev_charging": ["ev", "electric vehicle", "supercharger", "charger"],
    "air_conditioned": ["ac", "air conditioned", "air conditioning"]
}

CATEGORY_KEYWORDS = {
    "CAFE": ["cafe", "coffee", "roastery", "bakery", "espresso", "latte"],
    "RESTAURANT": ["restaurant", "diner", "food", "dining", "biryani", "thali", "meals", "eat"],
    "HOSPITAL": ["hospital", "clinic", "emergency", "doctor", "trauma", "medical"],
    "UNIVERSITY": ["university", "college", "campus", "department", "academic", "hostel"],
    "LIBRARY": ["library", "books", "reading room"],
    "SHOPPING": ["shopping", "mall", "market", "bazaar", "store"],
    "EV_CHARGING": ["ev charging", "charging station", "ev charger"]
}


class PlaceDiscoveryService:
    @staticmethod
    def parse_natural_language_query(query: str) -> Dict[str, Any]:
        """
        Extracts structured filters (category, desired amenities, price constraints)
        from free-form natural language query text.
        """
        q_lower = query.lower()
        
        # Category detection
        detected_category = None
        for cat, synonyms in CATEGORY_KEYWORDS.items():
            if any(syn in q_lower for syn in synonyms):
                detected_category = cat
                break

        # Amenity detection
        detected_amenities: Set[str] = set()
        for amenity, syns in AMENITY_KEYWORDS.items():
            if any(syn in q_lower for syn in syns):
                detected_amenities.add(amenity)

        # Budget / Price detection
        max_price = 4
        if "cheap" in q_lower or "budget" in q_lower or "affordable" in q_lower or "low cost" in q_lower:
            max_price = 1
        elif "moderate" in q_lower or "mid-range" in q_lower:
            max_price = 2
        elif "luxury" in q_lower or "fine dining" in q_lower or "premium" in q_lower:
            max_price = 4

        return {
            "raw_query": query,
            "category": detected_category,
            "required_amenities": list(detected_amenities),
            "max_price_level": max_price
        }

    @staticmethod
    def search_and_rank(
        db: Session,
        query_text: str,
        user_lat: float,
        user_lon: float,
        radius_km: float = 15.0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Performs preference-aware place ranking with explainable match rationale.
        """
        parsed = PlaceDiscoveryService.parse_natural_language_query(query_text)
        req_amenities = set(parsed["required_amenities"])
        target_category = parsed["category"]
        max_price = parsed["max_price_level"]

        # Fetch candidate places from DB
        all_places = db.query(Place).all()
        scored_places = []

        for p in all_places:
            dist_km = haversine_distance_m(user_lat, user_lon, p.latitude, p.longitude) / 1000.0
            if dist_km > radius_km:
                continue

            # Price constraint check
            if p.price_level > max_price:
                continue

            # Calculate match factors
            category_match = 1.0 if (target_category is None or p.category == target_category) else 0.3
            
            # Amenities match
            place_amenities = set(p.amenities or [])
            matched_amenities = req_amenities.intersection(place_amenities)
            amenity_score = len(matched_amenities) / len(req_amenities) if req_amenities else 1.0

            # Distance decay: closer places score higher
            dist_score = 1.0 / (1.0 + 0.3 * dist_km)

            # Rating quality
            rating_score = (p.rating or 4.0) / 5.0

            # Overall Composite Score
            final_score = (
                (category_match * 0.30) +
                (amenity_score * 0.35) +
                (dist_score * 0.20) +
                (rating_score * 0.15)
            )

            # Build explainable rationale
            reasons = []
            if matched_amenities:
                formatted_amenities = [a.replace("_", " ").title() for a in matched_amenities]
                reasons.append(f"Offers requested: {', '.join(formatted_amenities)}")
            if target_category and p.category == target_category:
                reasons.append(f"Matches category '{p.category.title()}'")
            if dist_km <= 2.0:
                reasons.append(f"Very close ({dist_km:.1f} km away)")
            if p.rating >= 4.7:
                reasons.append(f"Highly rated ({p.rating}★ from {p.reviews_count} reviews)")

            explainable_text = " • ".join(reasons) if reasons else "Nearby verified location"

            scored_places.append({
                "place_id": p.id,
                "name": p.name,
                "category": p.category,
                "rating": p.rating,
                "reviews_count": p.reviews_count,
                "price_level": p.price_level,
                "distance_km": round(dist_km, 2),
                "is_open_now": p.is_open_now,
                "amenities": p.amenities,
                "is_accessible": p.is_accessible,
                "match_score": round(final_score, 3),
                "match_explanation": explainable_text,
                "location": {"latitude": p.latitude, "longitude": p.longitude},
                "address": p.address
            })

        # Rank by composite match score descending
        scored_places.sort(key=lambda x: x["match_score"], reverse=True)
        return scored_places[:limit]

    @staticmethod
    def compare_places(
        db: Session,
        place_ids: List[str],
        user_lat: float,
        user_lon: float
    ) -> Dict[str, Any]:
        """
        Generates structured multi-dimensional comparison for selected places.
        """
        places = db.query(Place).filter(Place.id.in_(place_ids)).all()
        comparison_items = []

        for p in places:
            dist_km = haversine_distance_m(user_lat, user_lon, p.latitude, p.longitude) / 1000.0
            comparison_items.append({
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "rating": p.rating,
                "reviews_count": p.reviews_count,
                "price_level": p.price_level,
                "distance_km": round(dist_km, 2),
                "estimated_drive_minutes": round((dist_km / 35.0) * 60, 1),
                "is_open_now": p.is_open_now,
                "is_wheelchair_accessible": p.is_accessible,
                "amenities": p.amenities,
                "parking_capacity": sum(prk.capacity for prk in p.parking_lots) if p.parking_lots else 0,
                "has_ev_charging": any(prk.has_ev_charging for prk in p.parking_lots) if p.parking_lots else False
            })

        return {
            "comparison_count": len(comparison_items),
            "places": comparison_items
        }
