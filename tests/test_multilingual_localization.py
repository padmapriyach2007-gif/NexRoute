"""
Unit test suite verifying complete 8-language multilingual localization across NexRoute.
Verifies:
1. All 8 languages (en, te, hi, ta, kn, ml, bn, mr) have complete translation mappings for:
   - Places tabs & categories
   - Facility cards & category badges
   - Corridor Storybook headers, bento cards & category filter pills
   - Smart search radius options
   - AURA HUD status and prompts
   - Place card tags and photo badges
2. render_place_details_card_html produces fully localized Telugu markup without raw English leaks.
"""

import pytest
from src.i18n import SUPPORTED_LANGUAGES, t
from src.places_and_driving_modes import render_place_details_card_html


ALL_LANGS = ["en", "te", "hi", "ta", "kn", "ml", "bn", "mr"]

CRITICAL_KEYS = [
    # Places
    "places.tab_explore",
    "places.tab_saved",
    "places.cat_all_places",
    "places.cat_famous_attractions",
    "places.cat_healthcare",
    "places.cat_essential_facilities",
    "places.cat_food_stays",
    "places.cat_educational_institutions",
    "places.radius_label",
    "places.radius_5km",
    "places.radius_10km",
    "places.radius_25km",
    "places.radius_50km",
    "places.search_input_label",
    "places.search_placeholder",
    "places.famous_banner_title",
    "places.cultural_heritage",
    # Badges & tags
    "places.tag_health",
    "places.tag_heritage",
    "places.tag_popular",
    "places.tag_verified",
    "places.photo_landmark",
    "places.photo_place",
    "places.photo_category",
    "places.photo_commons",
    # Facility categories
    "cat.supermarket",
    "cat.hotel",
    "cat.hotels",
    "cat.atm",
    "cat.hospital",
    "cat.clinic",
    "cat.clinic_dispensary",
    "cat.heritage_landmark",
    "cat.scenic",
    "cat.shopping",
    "cat.dining",
    "cat.fuel",
    "cat.attractions",
    "cat.all_places",
    "cat.medical",
    "nav.mins",
    "fac.corridor_distance",
    # Storybook
    "storybook.header",
    "storybook.culture",
    "storybook.living_arts",
    "storybook.nature",
    "storybook.landscape",
    "storybook.photospot",
    "storybook.visual_spot",
    "storybook.local_food",
    "storybook.regional_food",
    "storybook.explore_lore",
    "storybook.heritage_records",
    "storybook.ai_intel",
    "storybook.hidden_gem",
    "storybook.what_to_look_for",
    "storybook.travel_tip",
    # AURA HUD
    "aura.status_idle",
    "aura.status_idle_prompt",
]


def test_supported_languages_list():
    """Verify all 8 languages are registered in SUPPORTED_LANGUAGES."""
    for l in ALL_LANGS:
        assert l in SUPPORTED_LANGUAGES, f"Language {l} missing from SUPPORTED_LANGUAGES"
        assert "native" in SUPPORTED_LANGUAGES[l]
        assert "name" in SUPPORTED_LANGUAGES[l]


@pytest.mark.parametrize("lang_code", ALL_LANGS)
def test_critical_keys_present_in_each_language(lang_code):
    """Verify that every critical key has a non-empty translation in each of the 8 languages."""
    for k in CRITICAL_KEYS:
        val = t(k, lang=lang_code)
        assert val is not None and val != "" and val != k, (
            f"Missing translation for key '{k}' in language '{lang_code}'"
        )


def test_telugu_specific_storybook_and_places():
    """Verify specific expected Telugu translations match user requirements."""
    assert "కారిడార్ స్టోరీబుక్" in t("storybook.header", lang="te")
    assert "సంస్కృతి" in t("storybook.culture", lang="te")
    assert "ప్రదేశాలు అన్వేషించండి" in t("places.tab_explore", lang="te")
    assert "భద్రపరిచిన ప్రదేశాలు" in t("places.tab_saved", lang="te")
    assert "సూపర్‌మార్కెట్" in t("cat.supermarket", lang="te")
    assert "ఆసుపత్రి" in t("cat.hospital", lang="te")
    assert "నిమిషాలు" in t("nav.mins", lang="te")
    assert "ప్రసిద్ధ సాంస్కృతిక" in t("places.famous_banner_title", lang="te")
    assert "సాంస్కృతిక వారసత్వం" in t("places.cultural_heritage", lang="te")
    assert "ఆరోగ్యం" in t("places.tag_health", lang="te")
    assert "ధృవీకరించబడిన మైలురాయి ఫోటో" in t("places.photo_landmark", lang="te")


def test_place_card_rendering_telugu_localization():
    """Verify render_place_details_card_html localizes tag, photo badge, category, and distance."""
    mock_place = {
        "name": "Sravani Skin Clinic",
        "category": "Local Clinic & Dispensary",
        "category_group": "healthcare",
        "tag": "HEALTH",
        "tag_color": "#ef4444",
        "photo_badge": "📸 Verified Category Photo",
        "distance_km": 2.4,
        "eta_minutes": 6,
        "highlights": ["clinic", "transit"],
        "open_status": "Operating hours not published"
    }

    card_html = render_place_details_card_html(mock_place, lang="te")
    # Tag HEALTH must be translated to ఆరోగ్యం
    assert "ఆరోగ్యం" in card_html
    assert ">HEALTH<" not in card_html

    # Photo badge Verified Category Photo must be translated to ధృవీకరించబడిన వర్గం ఫోటో
    assert "ధృవీకరించబడిన వర్గం ఫోటో" in card_html

    # Category Local Clinic & Dispensary must be translated to స్థానిక క్లినిక్ & డిస్పెన్సరీ
    assert "స్థానిక క్లినిక్ & డిస్పెన్సరీ" in card_html

    # ETA minutes must use Telugu నిమిషాలు
    assert "నిమిషాలు" in card_html
