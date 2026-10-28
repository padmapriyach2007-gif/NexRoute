"""
Comprehensive Test Suite for Small Hospitals, Clinics, Dispensaries,
Supermarkets, and Daily Provisions Detection in P.A.T.H.F.I.N.D.E.R.
"""

import pytest
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.facilities_service import (
    FacilityCategory,
    CATEGORY_CONFIG,
    VERIFIED_FACILITIES_DATABASE,
    WORLDWIDE_REGIONAL_POIS,
    CATEGORY_OSM_SEARCH_MAP,
    get_facilities_for_category,
    get_facilities_around_journey,
    resolve_custom_search_facility,
    synthesize_localized_facilities,
)
from src.places_and_driving_modes import (
    generate_suggested_places_at_location,
)
from src.google_maps_platform import (
    build_google_maps_javascript_html,
    load_and_georeference_saved_locations
)


class TestSmallHospitalsAndSupermarketsDetection:
    """Verifies that Pathfinder accurately identifies small hospitals, clinics,
    dispensaries, PHCs, and supermarkets across all services and map renderers."""

    def test_facility_category_supermarkets_defined(self):
        """FacilityCategory.SUPERMARKETS is defined and has valid configuration."""
        assert hasattr(FacilityCategory, "SUPERMARKETS")
        assert FacilityCategory.SUPERMARKETS == "supermarkets"
        assert FacilityCategory.SUPERMARKETS in CATEGORY_CONFIG
        
        cfg = CATEGORY_CONFIG[FacilityCategory.SUPERMARKETS]
        assert "icon" in cfg
        assert cfg["icon"] == "🛒"
        assert "supermarket" in cfg["label"].lower()
        assert "desc" in cfg

    def test_verified_database_contains_small_hospitals_and_clinics(self):
        """Database contains verified small hospitals, clinics, nursing homes, and PHCs."""
        clinic_facilities = [
            f for f in VERIFIED_FACILITIES_DATABASE
            if any(term in (f["name"] + " " + f.get("facility_type", "") + " " + f.get("description", "")).lower()
                   for term in ["clinic", "phc", "nursing home", "dispensary", "day-care hospital"])
        ]
        assert len(clinic_facilities) >= 4, f"Found {len(clinic_facilities)} small clinics/hospitals"
        
        names = [f["name"] for f in clinic_facilities]
        assert any("Sanjeevani" in n for n in names)
        assert any("Primary Health Centre" in n or "PHC" in n for n in names)
        assert any("Nursing Home" in n for n in names)
        assert any("LifeLine" in n for n in names)

    def test_verified_database_contains_supermarkets(self):
        """Database contains verified supermarkets, marts, and daily grocery stores."""
        supermarket_facilities = [
            f for f in VERIFIED_FACILITIES_DATABASE
            if f.get("category") == FacilityCategory.SUPERMARKETS or
               any(term in (f["name"] + " " + f.get("facility_type", "")).lower()
                   for term in ["supermarket", "mart", "grocery", "smart point", "provisions"])
        ]
        assert len(supermarket_facilities) >= 5, f"Found {len(supermarket_facilities)} supermarkets"
        
        names = [f["name"] for f in supermarket_facilities]
        assert any("More Supermarket" in n for n in names)
        assert any("Reliance Smart Point" in n for n in names)
        assert any("Ratnadeep" in n for n in names)
        assert any("Spencer" in n for n in names)
        assert any("Campus Mart" in n for n in names)

    def test_query_small_hospitals_via_get_facilities_for_category(self):
        """Querying HOSPITAL_CLINICS returns both hospitals and small clinics."""
        facilities = get_facilities_for_category(
            FacilityCategory.HOSPITAL_CLINICS,
            origin_coords=(16.234, 80.548),
            radius_km=30.0
        )
        assert len(facilities) > 0
        
        clinic_found = any(
            any(w in f["name"].lower() or w in f.get("facility_type", "").lower()
                for w in ["clinic", "phc", "nursing", "centre", "center", "health"])
            for f in facilities
        )
        assert clinic_found, "HOSPITAL_CLINICS query must include small clinics/health centers"

    def test_query_supermarkets_via_get_facilities_for_category(self):
        """Querying SUPERMARKETS returns supermarkets and daily grocery marts."""
        facilities = get_facilities_for_category(
            FacilityCategory.SUPERMARKETS,
            origin_coords=(16.234, 80.548),
            radius_km=30.0
        )
        assert len(facilities) > 0
        for f in facilities:
            assert f.get("category") == FacilityCategory.SUPERMARKETS or "supermarket" in f.get("facility_type", "").lower()
            assert f.get("amenity_icon") == "🛒"

    def test_custom_search_resolves_small_hospital_terms(self):
        """Custom search matches 'small hospital', 'clinic', 'phc', 'dispensary'."""
        terms = ["small hospital", "clinic", "dispensary", "primary health centre", "nursing home"]
        for term in terms:
            res = resolve_custom_search_facility(
                term,
                origin_coords=(16.234, 80.548)
            )
            assert res is not None, f"Query '{term}' should resolve facility result"
            assert res["category"] == FacilityCategory.CUSTOM_SEARCH

    def test_custom_search_resolves_supermarket_terms(self):
        """Custom search matches 'supermarket', 'grocery', 'provisions', 'supermaeket'."""
        terms = ["supermarket", "grocery store", "daily needs mart", "provisions", "supermaeket"]
        for term in terms:
            res = resolve_custom_search_facility(
                term,
                origin_coords=(16.234, 80.548)
            )
            assert res is not None, f"Query '{term}' should resolve supermarket result"
            assert res["category"] == FacilityCategory.CUSTOM_SEARCH

    def test_regional_pois_include_clinics_and_supermarkets(self):
        """Worldwide / regional POIs database contains localized clinics and supermarkets."""
        ranjole_pois = WORLDWIDE_REGIONAL_POIS.get("ranjole", [])
        assert len(ranjole_pois) > 0
        has_clinic = any("clinic" in p["name"].lower() or "hospital" in p["name"].lower() for p in ranjole_pois)
        has_supermarket = any("supermarket" in p["name"].lower() or "mart" in p["name"].lower() for p in ranjole_pois)
        assert has_clinic, "Regional POIs should include local day-care clinic/hospital"
        assert has_supermarket, "Regional POIs should include local daily needs supermarket"

    def test_osm_search_map_coverage(self):
        """CATEGORY_OSM_SEARCH_MAP includes specialized search terms for small medical and groceries."""
        hosp_entry = CATEGORY_OSM_SEARCH_MAP.get(FacilityCategory.HOSPITAL_CLINICS)
        assert hosp_entry is not None
        hosp_terms = hosp_entry[0]
        assert any("clinic" in t for t in hosp_terms)
        assert any("dispensary" in t for t in hosp_terms)
        assert any("nursing" in t or "health" in t for t in hosp_terms)

        sup_entry = CATEGORY_OSM_SEARCH_MAP.get(FacilityCategory.SUPERMARKETS)
        assert sup_entry is not None
        sup_terms = sup_entry[0]
        assert len(sup_terms) >= 3
        assert any("supermarket" in t for t in sup_terms)
        assert any("grocery" in t for t in sup_terms)

    def test_synthesize_localized_facilities_generates_supermarkets_and_clinics(self):
        """Synthetic fallback generates supermarkets and small clinics for any coordinate."""
        lat, lon = 15.500, 78.500
        synth = synthesize_localized_facilities(lat, lon, count=25)
        
        has_clinic = any(
            any(w in f["name"].lower() for w in ["clinic", "dispensary", "health centre", "day-care"])
            for f in synth
        )
        has_supermarket = any(
            f.get("category") == FacilityCategory.SUPERMARKETS or
            any(w in f["name"].lower() for w in ["supermarket", "mart", "grocery", "provisions"])
            for f in synth
        )
        assert has_clinic, "Synthesized facilities should produce local clinics/dispensaries"
        assert has_supermarket, "Synthesized facilities should produce local supermarkets"

    def test_places_and_driving_modes_includes_supermarket_and_clinic(self):
        """generate_suggested_places_at_location produces supermarket and clinic recommendations."""
        places = generate_suggested_places_at_location(16.234, 80.548, "Vadlamudi Area", radius_km=15.0)
        assert len(places) > 0
        
        has_grocery = any(p.get("tag") == "🛒 GROCERY" or "supermarket" in p.get("name", "").lower() or "mart" in p.get("name", "").lower() for p in places)
        has_health = any(p.get("tag") == "🩺 HEALTH" or "clinic" in p.get("name", "").lower() or "hospital" in p.get("name", "").lower() for p in places)
        
        assert has_grocery, "Recommended places must detect supermarkets/groceries"
        assert has_health, "Recommended places must detect small health clinics/hospitals"

    def test_get_facilities_around_journey_includes_supermarket_and_clinic(self):
        """Facilities detected along corridor include small hospitals/clinics and supermarkets."""
        origin = (16.234, 80.548)
        destination = (16.240, 80.600)
        corridor_facs = get_facilities_around_journey(
            category="🌐 All Facilities",
            origin_coords=origin,
            dest_coords=destination,
            radius_km=25.0
        )
        assert len(corridor_facs) > 0
        categories_found = {f["category"] for f in corridor_facs}
        assert FacilityCategory.HOSPITAL_CLINICS in categories_found or FacilityCategory.HOSPITALS in categories_found
        assert FacilityCategory.SUPERMARKETS in categories_found

    def test_google_maps_html_includes_supermarkets_filter_pill_and_category(self):
        """Map HTML contains Supermarkets filter pill and CATEGORY_CONFIG."""
        html = build_google_maps_javascript_html(
            center_lat=16.234,
            center_lon=80.548,
            zoom=14,
            amenities=[
                {
                    "name": "Sanjeevani Clinic",
                    "latitude": 16.234,
                    "longitude": 80.548,
                    "category": "hospitals",
                    "facility_type": "Primary Health Clinic"
                },
                {
                    "name": "More Supermarket",
                    "latitude": 16.236,
                    "longitude": 80.550,
                    "category": "supermarkets",
                    "facility_type": "Supermarket"
                }
            ]
        )
        assert 'data-filter="SUPERMARKETS"' in html
        assert '🛒 Supermarkets' in html
        assert "'SUPERMARKETS':" in html
        assert "Sanjeevani Clinic" in html
        assert "More Supermarket" in html
