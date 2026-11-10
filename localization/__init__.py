# -*- coding: utf-8 -*-
"""
NexRoute Global Localization Package
Centralized, application-wide translation engine supporting:
- 8 authorized Indian languages with native scripts & BCP-47 speech codes
- Static UI key translations with English fallback
- Dynamic AI & corridor description translations
- Protected entity shielding (NexRoute, AURA, Tenali, Krishna River, etc.)
- Dynamic web font injection (Noto Sans) for pristine Unicode rendering
- Session-persistent language state across Streamlit reruns
"""

from localization.language_config import (
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
    PROTECTED_ENTITIES
)
from localization.language_manager import (
    get_selected_language,
    set_selected_language,
    t,
    get_bcp47_code,
    get_language_native_name,
    format_distance,
    format_duration
)
from localization.dynamic_translator import (
    translate_content,
    translate_dict_descriptions
)
from localization.font_manager import (
    get_font_injection_html
)
from localization.translations import (
    TRANSLATIONS
)

__all__ = [
    "SUPPORTED_LANGUAGES",
    "DEFAULT_LANGUAGE",
    "PROTECTED_ENTITIES",
    "get_selected_language",
    "set_selected_language",
    "t",
    "get_bcp47_code",
    "get_language_native_name",
    "format_distance",
    "format_duration",
    "translate_content",
    "translate_dict_descriptions",
    "get_font_injection_html",
    "TRANSLATIONS"
]
