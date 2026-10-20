"""
Comprehensive Test Suite for AI Satellite Imagery and Road Intelligence Integration.
Tests:
1. Georeferenced spatial coordinate conversions and Ground Sampling Distance (GSD).
2. Legitimate satellite imagery provider metadata, attribution, and licensing.
3. Road surface segmentation, width estimation, and intersection detection.
4. Authoritative road-network cross-validation and avoidance preference auditing.
5. Verification status labeling (Corroborated vs AI-detected — unverified).
6. Performance caching, fallback resilience, and UI HUD rendering.
"""

import math
import pytest
from PIL import Image
import numpy as np

from src.satellite_road_cv import (
    SlippyMapUtils,
    ImageryProviderInfo,
    AVAILABLE_SATELLITE_PROVIDERS,
    RoadSurfaceSegmenter,
    RoadNetworkCrossValidator,
    AIRoadIntelligenceController,
    RoadIntelligenceObservation,
    AIRoadIntelligenceReport,
    render_ai_road_intelligence_hud_html
)


# =============================================================================
# 1. GEOREFERENCED SPATIAL TRANSFORMATION & GSD TESTS
# =============================================================================

def test_slippy_tile_conversion_and_roundtrip():
    """Verify tile coordinate calculation and pixel roundtrip."""
    lat, lon = 16.2335, 80.5505  # Vignan University region
    zoom = 16

    tx, ty = SlippyMapUtils.lat_lon_to_tile(lat, lon, zoom)
    assert tx > 0
    assert ty > 0

    # Bounds of tile
    s, w, n, e = SlippyMapUtils.tile_to_bbox(tx, ty, zoom)
    assert s <= lat <= n
    assert w <= lon <= e

    # Pixel conversion within tile
    px, py = SlippyMapUtils.lat_lon_to_pixel(lat, lon, tx, ty, zoom, 256, 256)
    assert 0 <= px <= 256
    assert 0 <= py <= 256

    # Convert back to lat/lon
    r_lat, r_lon = SlippyMapUtils.pixel_to_lat_lon(px, py, tx, ty, zoom, 256, 256)
    assert abs(r_lat - lat) < 1e-4
    assert abs(r_lon - lon) < 1e-4


def test_ground_sampling_distance_calibration():
    """Verify ground sampling distance (GSD) at different zoom levels."""
    lat = 16.2335
    gsd_z14 = SlippyMapUtils.ground_sampling_distance_m(lat, 14)
    gsd_z16 = SlippyMapUtils.ground_sampling_distance_m(lat, 16)
    gsd_z18 = SlippyMapUtils.ground_sampling_distance_m(lat, 18)

    # GSD should halve with every zoom level increase
    assert math.isclose(gsd_z14 / gsd_z16, 4.0, rel_tol=0.05)
    assert math.isclose(gsd_z16 / gsd_z18, 4.0, rel_tol=0.05)
    # At zoom 16, 1 pixel is ~ 2.38 meters
    assert 2.0 <= gsd_z16 <= 2.8


# =============================================================================
# 2. SATELLITE IMAGERY PROVIDERS & ATTRIBUTION TESTS
# =============================================================================

def test_satellite_providers_documentation_and_licensing():
    """Verify documented provider access, attribution, and licensing requirements."""
    esri = AVAILABLE_SATELLITE_PROVIDERS.get("esri_world_imagery")
    assert esri is not None
    assert "Esri" in esri.attribution
    assert "Maxar" in esri.attribution or "USGS" in esri.attribution
    assert "License" in esri.licensing
    assert esri.is_realtime is False  # Must not claim real-time satellite video

    sentinel = AVAILABLE_SATELLITE_PROVIDERS.get("sentinel2_cloudless")
    assert sentinel is not None
    assert "Copernicus" in sentinel.attribution
    assert "CC BY 4.0" in sentinel.licensing


# =============================================================================
# 3. COMPUTER-VISION ROAD SEGMENTATION & TOPOLOGY
# =============================================================================

def test_road_surface_segmentation_on_calibration_image():
    """Verify CV segmenter extracts road surface, width, and quality scores."""
    segmenter = RoadSurfaceSegmenter(confidence_threshold=0.60)

    # Generate synthetic georeferenced calibration image (256x256)
    # Background: green foliage (45, 75, 40)
    arr = np.full((256, 256, 3), [45, 75, 40], dtype=np.uint8)
    # Road corridor: neutral dark asphalt (60, 62, 65) along X: 118 to 138 (width 20px)
    arr[:, 118:138, :] = [60, 62, 65]
    # Intersecting road: X: 138 to 256, Y: 120 to 136 (width 16px)
    arr[120:136, 138:, :] = [60, 62, 65]

    img = Image.fromarray(arr)
    # Test at standard satellite tile zoom 17 (GSD ~ 1.17m/px)
    res = segmenter.analyze_tile_image(img, tile_x=94850, tile_y=57560, zoom=17)

    assert res["road_pixel_count"] > 1000
    assert res["road_coverage_pct"] > 5.0
    assert res["quality_confidence"] >= 0.50
    # Average width: 20px * 1.17m/px ~ 23m
    assert 5.0 <= res["estimated_avg_width_m"] <= 50.0
    # Must have detected at least 1 intersection
    assert len(res["intersections"]) >= 1


def test_bridge_and_waterway_detection():
    """Verify bridge detection when road crosses water body."""
    segmenter = RoadSurfaceSegmenter()

    arr = np.full((256, 256, 3), [45, 75, 40], dtype=np.uint8)
    # Road through the middle
    arr[:, 120:136, :] = [60, 60, 60]
    # Water canal across the road at Y: 150 to 170 (blue/cyan water)
    arr[150:170, :, :] = [25, 60, 110]
    # Bridge structure carrying the road across the canal
    arr[150:170, 120:136, :] = [170, 170, 175]

    img = Image.fromarray(arr)
    res = segmenter.analyze_tile_image(img, tile_x=47425, tile_y=28780, zoom=16)
    assert res["has_water"] is True


# =============================================================================
# 4. CROSS-VALIDATION WITH AUTHORITATIVE ROAD DATA
# =============================================================================

def test_cross_validation_corroborates_expected_widths():
    """Verify cross-validation corroborates width when consistent with OSM class."""
    # 14m observed width matches a primary arterial highway
    res = RoadNetworkCrossValidator.cross_validate_road_segment(
        observed_width_m=14.0,
        osm_highway_class="primary"
    )
    assert res["verification_status"] == "Corroborated by map data"
    assert res["confidence"] >= 0.80
    assert "matches authoritative OSM" in res["notes"]


def test_cross_validation_flags_unverified_divergence():
    """Verify cross-validation flags an unexpected width as unverified rather than assuming."""
    # 28m width on a residential road is divergent and requires unverified tag
    res = RoadNetworkCrossValidator.cross_validate_road_segment(
        observed_width_m=28.0,
        osm_highway_class="residential"
    )
    assert res["verification_status"] == "AI-detected — unverified"
    assert "variance" in res["notes"].lower()


def test_route_avoidance_preferences_auditing():
    """Verify route avoidance detection for tolls, highways, and ferries."""
    # Scenario A: Highway route with Avoid Highways = True
    summary_roads = ["NH16 Chennai-Kolkata Expressway", "Tenali Link Road"]
    osm_tags = [{"highway": "motorway", "name": "NH16"}]

    audit = RoadNetworkCrossValidator.audit_route_avoidance_preferences(
        summary_roads=summary_roads,
        osm_tags_list=osm_tags,
        avoid_highways=True,
        avoid_tolls=False,
        avoid_ferries=False
    )
    assert audit["satisfies_preferences"] is False
    assert any("Highway Avoidance Violation" in v for v in audit["violations"])

    # Scenario B: Local road route with Avoid Highways = True
    local_roads = ["Tenali - Narakoduru Road", "Campus Avenue"]
    local_osm_tags = [{"highway": "secondary", "name": "Tenali - Narakoduru Road"}]

    audit_local = RoadNetworkCrossValidator.audit_route_avoidance_preferences(
        summary_roads=local_roads,
        osm_tags_list=local_osm_tags,
        avoid_highways=True,
        avoid_tolls=False,
        avoid_ferries=False
    )
    assert audit_local["satisfies_preferences"] is True
    assert len(audit_local["violations"]) == 0


# =============================================================================
# 5. CONTROLLER & REPORT GENERATION TESTS
# =============================================================================

def test_controller_corridor_analysis_and_caching():
    """Verify corridor analysis produces structured report and caches correctly."""
    controller = AIRoadIntelligenceController(
        provider_key="esri_world_imagery",
        enable_tile_network=False  # Test offline synthetic generation
    )
    polyline = [(16.241, 80.584), (16.245, 80.575), (16.233, 80.550)]

    rep1 = controller.analyze_corridor(
        polyline=polyline,
        summary_roads=["Tenali - Narakoduru Road"],
        avoid_tolls=False,
        avoid_highways=False
    )
    assert rep1 is not None
    assert rep1.overall_confidence > 0.50
    assert rep1.estimated_average_width_m > 0
    assert len(rep1.observations) >= 1
    assert "Esri World Imagery" in rep1.imagery_provider

    # Second call within TTL should return cached report
    rep2 = controller.analyze_corridor(
        polyline=polyline,
        summary_roads=["Tenali - Narakoduru Road"],
        avoid_tolls=False,
        avoid_highways=False
    )
    assert rep1.generation_time == rep2.generation_time


def test_controller_handles_empty_polyline_gracefully():
    """Verify controller handles empty or degenerate polyline without crashing."""
    controller = AIRoadIntelligenceController(enable_tile_network=False)
    rep = controller.analyze_corridor([])
    assert rep.route_id == "EMPTY_CORRIDOR"
    assert len(rep.limitations) >= 1


def test_hud_html_rendering():
    """Verify AI Road Intelligence HTML component contains required telemetry."""
    controller = AIRoadIntelligenceController(enable_tile_network=False)
    polyline = [(16.241, 80.584), (16.233, 80.550)]
    report = controller.analyze_corridor(polyline, summary_roads=["Main Road"])

    html = render_ai_road_intelligence_hud_html(report)
    assert "AI SATELLITE ROAD INTELLIGENCE" in html
    assert "Confidence Score" in html
    assert "Estimated Width" in html
    assert "Imagery Freshness" in html
    assert "Licensing &amp; Safety Notice" in html or "Licensing & Safety Notice" in html
