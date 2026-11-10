# -*- coding: utf-8 -*-
"""
Central Language Manager for NexRoute
Coordinates global language selection, session persistence across reruns,
bcp-47 voice codes, metric formatting, and key translation lookups.
"""

import builtins
import logging
from typing import Optional, Dict, Any

from localization.language_config import (
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE
)
from src.i18n import TRANSLATIONS

logger = logging.getLogger("nexroute.localization.language_manager")


def get_selected_language() -> str:
    """
    Returns the currently active application language code (e.g. 'te', 'hi', 'en').
    Prioritizes Streamlit session_state, then builtins.cur_l, defaulting to 'en'.
    """
    try:
        import streamlit as st
        if "app_language" in st.session_state and st.session_state.app_language in SUPPORTED_LANGUAGES:
            return st.session_state.app_language
    except Exception:
        pass

    if hasattr(builtins, "cur_l") and builtins.cur_l in SUPPORTED_LANGUAGES:
        return builtins.cur_l

    return DEFAULT_LANGUAGE


def set_selected_language(lang_code: str) -> None:
    """
    Sets the application-wide active language.
    Updates Streamlit session_state, builtins.cur_l, and module globals simultaneously.
    """
    if lang_code in SUPPORTED_LANGUAGES:
        builtins.cur_l = lang_code
        try:
            import streamlit as st
            st.session_state.app_language = lang_code
        except Exception:
            pass


def get_bcp47_code(lang_code: Optional[str] = None) -> str:
    """Returns the BCP-47 speech synthesis and recognition code for the language."""
    c = lang_code or get_selected_language()
    info = SUPPORTED_LANGUAGES.get(c, SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE])
    return info.get("bcp47", "en-IN")


def get_language_native_name(lang_code: Optional[str] = None) -> str:
    """Returns the native display name for a language (e.g. 'తెలుగు', 'हिन्दी')."""
    c = lang_code or get_selected_language()
    info = SUPPORTED_LANGUAGES.get(c, SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE])
    return info.get("native", "English")


def t(
    key: str,
    *args,
    default: Optional[str] = None,
    language: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs
) -> str:
    """
    Central Translation Lookup Function.
    - Resolves language code (explicit arg, kwarg 'language', kwarg 'lang', or session state).
    - Supports default fallback string (positional arg or kwargs).
    - Looks up key in language table with automatic fallback chain to English.
    - Safely interpolates kwargs placeholders e.g. {count}, {name}, {status}.
    """
    target_lang = language or lang
    default_text = default

    for arg in args:
        if isinstance(arg, str):
            if arg in SUPPORTED_LANGUAGES and not target_lang:
                target_lang = arg
            elif not default_text:
                default_text = arg

    if not target_lang:
        target_lang = get_selected_language()

    if target_lang not in SUPPORTED_LANGUAGES:
        target_lang = DEFAULT_LANGUAGE

    # 1. Lookup in target language table
    lang_table = TRANSLATIONS.get(target_lang, {})
    val = lang_table.get(key)

    # 2. Fallback to English
    if val is None:
        val = TRANSLATIONS.get(DEFAULT_LANGUAGE, {}).get(key)

    # 3. Fallback to default provided text or formatted key
    if val is None:
        val = default_text if default_text is not None else key.split(".")[-1].replace("_", " ").title()

    # Interpolate kwargs
    if kwargs:
        try:
            return val.format(**kwargs)
        except Exception:
            return val

    return str(val)


def format_distance(dist_km: float, lang_code: Optional[str] = None) -> str:
    """Formats distance with localized unit."""
    c = lang_code or get_selected_language()
    unit = t("unit.km", default="km", language=c)
    unit_m = t("unit.m", default="m", language=c)
    if dist_km < 1.0:
        return f"{int(dist_km * 1000)} {unit_m}"
    return f"{dist_km:.1f} {unit}"


def format_duration(duration_minutes: float, lang_code: Optional[str] = None) -> str:
    """Formats duration in localized hours and minutes."""
    c = lang_code or get_selected_language()
    h_lbl = t("unit.h", default="h", language=c)
    min_lbl = t("unit.min", default="min", language=c)
    mins = int(round(duration_minutes))
    if mins < 60:
        return f"{mins} {min_lbl}"
    hours = mins // 60
    rem_mins = mins % 60
    if rem_mins == 0:
        return f"{hours} {h_lbl}"
    return f"{hours} {h_lbl} {rem_mins} {min_lbl}"
