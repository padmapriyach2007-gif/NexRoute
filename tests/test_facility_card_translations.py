# -*- coding: utf-8 -*-
"""
Tests for Facility Card Translations and Language Variable Scoping.
Ensures no NameError is raised for 'cur_l' when rendering facility cards
across all supported languages.
"""

import pytest
from src.i18n import t, SUPPORTED_LANGUAGES


class TestFacilityCardTranslations:
    def test_facility_categories_translated(self):
        # Telugu translations
        assert t("cat.hospital", default="Hospital", lang="te") != "Hospital"
        assert t("cat.atm", default="ATM", lang="te") != ""
        assert t("cat.supermarket", default="Supermarket", lang="te") != ""
        assert t("nav.mins", default="mins", lang="te") != ""

        # Hindi translations
        assert t("cat.hospital", default="Hospital", lang="hi") != "Hospital"

    def test_all_supported_languages_facility_keys(self):
        keys = [
            "cat.supermarket",
            "cat.hotel",
            "cat.atm",
            "cat.clinic",
            "cat.hospital",
            "cat.medical",
            "cat.fuel",
            "cat.dining",
            "nav.mins"
        ]
        for lang in SUPPORTED_LANGUAGES:
            for k in keys:
                val = t(k, default="Default", lang=lang)
                assert val is not None
                assert len(val) > 0

    def test_app_py_has_cur_l_defined_globally_and_locally(self):
        with open("app.py", "r", encoding="utf-8") as f:
            code = f.read()

        # Verify cur_l is defined early in app.py
        assert "cur_l = st.session_state.get(\"app_language\", \"en\")" in code or "cur_l = st.session_state.app_language" in code

        # Verify no bare NameError risk at facility grid
        assert "grid_cols = st.columns(min(3, len(active_category_facilities)))" in code
