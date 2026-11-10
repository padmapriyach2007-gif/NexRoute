# -*- coding: utf-8 -*-
"""
Centralized Language Configuration for NexRoute
Defines the authorized 8 languages, BCP-47 speech codes, native scripts,
Unicode font mappings, and protected entity definitions.
"""

from typing import Dict, Any, List, Set
import re

# Strictly authorized 8 languages
SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {
        "name": "English",
        "native": "English",
        "bcp47": "en-IN",
        "flag": "🌐",
        "script": "Latin",
        "font_family": "'Inter', 'Segoe UI', -apple-system, sans-serif"
    },
    "te": {
        "name": "Telugu",
        "native": "తెలుగు",
        "bcp47": "te-IN",
        "flag": "🇮🇳",
        "script": "Telugu",
        "font_family": "'Noto Sans Telugu', 'Gautami', 'Mandali', sans-serif"
    },
    "hi": {
        "name": "Hindi",
        "native": "हिन्दी",
        "bcp47": "hi-IN",
        "flag": "🇮🇳",
        "script": "Devanagari",
        "font_family": "'Noto Sans Devanagari', 'Mangal', sans-serif"
    },
    "kn": {
        "name": "Kannada",
        "native": "ಕನ್ನಡ",
        "bcp47": "kn-IN",
        "flag": "🇮🇳",
        "script": "Kannada",
        "font_family": "'Noto Sans Kannada', 'Tunga', sans-serif"
    },
    "ta": {
        "name": "Tamil",
        "native": "தமிழ்",
        "bcp47": "ta-IN",
        "flag": "🇮🇳",
        "script": "Tamil",
        "font_family": "'Noto Sans Tamil', 'Latha', sans-serif"
    },
    "ml": {
        "name": "Malayalam",
        "native": "മലയാളം",
        "bcp47": "ml-IN",
        "flag": "🇮🇳",
        "script": "Malayalam",
        "font_family": "'Noto Sans Malayalam', 'Kartika', sans-serif"
    },
    "mr": {
        "name": "Marathi",
        "native": "मराठी",
        "bcp47": "mr-IN",
        "flag": "🇮🇳",
        "script": "Devanagari",
        "font_family": "'Noto Sans Devanagari', 'Mangal', sans-serif"
    },
    "bn": {
        "name": "Bengali",
        "native": "বাংলা",
        "bcp47": "bn-IN",
        "flag": "🇮🇳",
        "script": "Bengali",
        "font_family": "'Noto Sans Bengali', 'Vrinda', sans-serif"
    },
}

DEFAULT_LANGUAGE = "en"

# Proper Nouns & Protected Entities that MUST NEVER be corrupted or translated incorrectly
PROTECTED_ENTITIES: List[str] = [
    # Application & Core AI
    "NexRoute",
    "AURA",
    "CampusAegis",
    "Pathfinder",

    # Geographical Rivers, Canals, Waterways
    "Krishna River",
    "Buckingham Canal",
    "Godavari River",
    "Tungabhadra River",
    "Prakasam Barrage",
    "Bhavani Island",
    "Nagarjuna Sagar",
    "Bay of Bengal",

    # Key Cities, Towns, Localities
    "Tenali",
    "Guntur",
    "Vijayawada",
    "Mangalagiri",
    "Amaravati",
    "Dharanikota",
    "Bapatla",
    "Suryalanka",
    "Kondaveedu",
    "Undavalli",
    "Uppalapadu",
    "Narakoduru",
    "Chilakaluripet",
    "Narasaraopet",
    "Machilipatnam",
    "Hyderabad",
    "Bengaluru",
    "Bangalore",
    "Chennai",
    "Mumbai",
    "Kolkata",
    "Delhi",
    "Charminar",
    "Golconda",

    # Regional Culinary & Heritage Specialties
    "Gongura Pacchadi",
    "Gongura",
    "Hyderabadi Biryani",
    "Pesarattu",
    "Pootharekulu",
    "Filter Coffee",
    "Mirchi Bajji",
    "Ulava Charu",
    "Rava Dosa",

    # Technical & Measurement Terms
    "OpenStreetMap",
    "OSM",
    "OSRM",
    "GPS",
    "EV",
    "SOS",
    "CO2",
    "ETA",
    "HTTP",
    "HTTPS",
    "API",
    "URL",
]

# Compiled regex for fast entity matching
_PROTECTED_REGEX = re.compile(
    r"\b(" + "|".join(re.escape(term) for term in sorted(PROTECTED_ENTITIES, key=len, reverse=True)) + r")\b",
    re.IGNORECASE
)
