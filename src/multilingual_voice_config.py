"""
NextRoute — Centralized Multilingual Voice Capability Map & Configuration
Defines exact voice synthesis, speech recognition, native scripts, preferred voices,
and fallback policies across all officially supported languages in NextRoute.

Supported Languages:
1. English (en) — English (India / US)
2. Telugu (te) — తెలుగు (India)
3. Hindi (hi) — हिन्दी (India)
4. Tamil (ta) — தமிழ் (India)
5. Kannada (kn) — ಕನ್ನಡ (India)
6. Malayalam (ml) — മലയാളം (India)
7. Bengali (bn) — বাংলা (India)
8. Marathi (mr) — मराठी (India)
"""

from typing import Dict, Any, List, Optional


MULTILINGUAL_VOICE_CAPABILITY_MAP: Dict[str, Dict[str, Any]] = {
    "en": {
        "language_name": "English",
        "native_name": "English",
        "iso_code": "en",
        "bcp47": "en-IN",
        "speech_recognition_supported": True,
        "speech_recognition_engine": "Web Speech API (webkitSpeechRecognition) / Google Cloud STT / Microsoft Speech",
        "speech_synthesis_supported": True,
        "speech_synthesis_engine": "Browser SpeechSynthesis / OS Voice Synthesizer",
        "preferred_voices": [
            "Microsoft Ravi - English (India)",
            "Microsoft Heera - English (India)",
            "Google US English",
            "Google UK English Male",
            "Google UK English Female",
            "Samantha",
            "David"
        ],
        "voice_search_keywords": ["ravi", "heera", "natural", "neural", "google", "david", "guy", "george", "samantha", "en-in", "en-us"],
        "fallback_behavior": "Default to standard available English voice (en-IN or en-US).",
        "translation_coverage": "100% (Native base language)"
    },
    "te": {
        "language_name": "Telugu",
        "native_name": "తెలుగు",
        "iso_code": "te",
        "bcp47": "te-IN",
        "speech_recognition_supported": True,
        "speech_recognition_engine": "Web Speech API (webkitSpeechRecognition) / Google Speech te-IN",
        "speech_synthesis_supported": True,
        "speech_synthesis_engine": "Browser SpeechSynthesis / Microsoft SAPI / Google TTS / iOS Enhanced",
        "preferred_voices": [
            "Microsoft Mohan - Telugu (India)",
            "Microsoft Shruti - Telugu (India)",
            "Google తెలుగు",
            "te-in-x-tee-local",
            "Telugu India"
        ],
        "voice_search_keywords": ["mohan", "shruti", "తెలుగు", "telugu", "te-in"],
        "fallback_behavior": "Search for any voice with lang='te-IN' or prefix 'te'. If no Telugu voice is installed on client device, suppress audio and present clean Telugu text without cross-language voice mangling.",
        "translation_coverage": "100% (Complete UI & Copilot native translations)"
    },
    "hi": {
        "language_name": "Hindi",
        "native_name": "हिन्दी",
        "iso_code": "hi",
        "bcp47": "hi-IN",
        "speech_recognition_supported": True,
        "speech_recognition_engine": "Web Speech API (webkitSpeechRecognition) / Google Speech hi-IN",
        "speech_synthesis_supported": True,
        "speech_synthesis_engine": "Browser SpeechSynthesis / Microsoft SAPI / Google TTS / iOS Lekha",
        "preferred_voices": [
            "Microsoft Hemant - Hindi (India)",
            "Microsoft Kalpana - Hindi (India)",
            "Google हिन्दी",
            "hi-in-x-hie-local",
            "Lekha",
            "Swara",
            "Madhur"
        ],
        "voice_search_keywords": ["hemant", "kalpana", "हिन्दी", "hindi", "swara", "madhur", "lekha", "hi-in"],
        "fallback_behavior": "Search for any voice with lang='hi-IN' or prefix 'hi'. If no Hindi voice is installed on client device, suppress audio and present clean Devanagari text.",
        "translation_coverage": "100% (Complete UI & Copilot native translations)"
    },
    "ta": {
        "language_name": "Tamil",
        "native_name": "தமிழ்",
        "iso_code": "ta",
        "bcp47": "ta-IN",
        "speech_recognition_supported": True,
        "speech_recognition_engine": "Web Speech API (webkitSpeechRecognition) / Google Speech ta-IN",
        "speech_synthesis_supported": True,
        "speech_synthesis_engine": "Browser SpeechSynthesis / Microsoft SAPI / Google TTS / iOS Enhanced",
        "preferred_voices": [
            "Microsoft Valluvar - Tamil (India)",
            "Microsoft Pallavi - Tamil (India)",
            "Google தமிழ்",
            "ta-in-x-tag-local",
            "Tamil India"
        ],
        "voice_search_keywords": ["valluvar", "pallavi", "தமிழ்", "tamil", "ta-in"],
        "fallback_behavior": "Search for any voice with lang='ta-IN' or prefix 'ta'. If no Tamil voice is installed, suppress audio and present clean Tamil text.",
        "translation_coverage": "100% (Complete UI & Copilot native translations)"
    },
    "kn": {
        "language_name": "Kannada",
        "native_name": "ಕನ್ನಡ",
        "iso_code": "kn",
        "bcp47": "kn-IN",
        "speech_recognition_supported": True,
        "speech_recognition_engine": "Web Speech API (webkitSpeechRecognition) / Google Speech kn-IN",
        "speech_synthesis_supported": True,
        "speech_synthesis_engine": "Browser SpeechSynthesis / Microsoft SAPI / Google TTS / iOS Enhanced",
        "preferred_voices": [
            "Microsoft Gagan - Kannada (India)",
            "Microsoft Sapna - Kannada (India)",
            "Google ಕನ್ನಡ",
            "kn-in-x-knf-local",
            "Kannada India"
        ],
        "voice_search_keywords": ["gagan", "sapna", "ಕನ್ನಡ", "kannada", "kn-in"],
        "fallback_behavior": "Search for any voice with lang='kn-IN' or prefix 'kn'. If no Kannada voice is installed, suppress audio and present clean Kannada text.",
        "translation_coverage": "100% (Complete UI & Copilot native translations)"
    },
    "ml": {
        "language_name": "Malayalam",
        "native_name": "മലയാളം",
        "iso_code": "ml",
        "bcp47": "ml-IN",
        "speech_recognition_supported": True,
        "speech_recognition_engine": "Web Speech API (webkitSpeechRecognition) / Google Speech ml-IN",
        "speech_synthesis_supported": True,
        "speech_synthesis_engine": "Browser SpeechSynthesis / Microsoft SAPI / Google TTS / iOS Enhanced",
        "preferred_voices": [
            "Microsoft Midhun - Malayalam (India)",
            "Microsoft Sobhana - Malayalam (India)",
            "Google മലയാളം",
            "ml-in-x-mlc-local",
            "Malayalam India"
        ],
        "voice_search_keywords": ["midhun", "sobhana", "മലയാളം", "malayalam", "ml-in"],
        "fallback_behavior": "Search for any voice with lang='ml-IN' or prefix 'ml'. If no Malayalam voice is installed, suppress audio and present clean Malayalam text.",
        "translation_coverage": "100% (Complete UI & Copilot native translations)"
    },
    "bn": {
        "language_name": "Bengali",
        "native_name": "বাংলা",
        "iso_code": "bn",
        "bcp47": "bn-IN",
        "speech_recognition_supported": True,
        "speech_recognition_engine": "Web Speech API (webkitSpeechRecognition) / Google Speech bn-IN",
        "speech_synthesis_supported": True,
        "speech_synthesis_engine": "Browser SpeechSynthesis / Microsoft SAPI / Google TTS / iOS Enhanced",
        "preferred_voices": [
            "Microsoft Bashkar - Bengali (India)",
            "Microsoft Tanishaa - Bengali (India)",
            "Google বাংলা",
            "bn-in-x-bng-local",
            "Bengali India",
            "Bangla"
        ],
        "voice_search_keywords": ["bashkar", "tanishaa", "বাংলা", "bengali", "bangla", "bn-in"],
        "fallback_behavior": "Search for any voice with lang='bn-IN' or prefix 'bn'. If no Bengali voice is installed, suppress audio and present clean Bengali text.",
        "translation_coverage": "100% (Complete UI & Copilot native translations)"
    },
    "mr": {
        "language_name": "Marathi",
        "native_name": "मराठी",
        "iso_code": "mr",
        "bcp47": "mr-IN",
        "speech_recognition_supported": True,
        "speech_recognition_engine": "Web Speech API (webkitSpeechRecognition) / Google Speech mr-IN",
        "speech_synthesis_supported": True,
        "speech_synthesis_engine": "Browser SpeechSynthesis / Microsoft SAPI / Google TTS / iOS Enhanced",
        "preferred_voices": [
            "Microsoft Manohar - Marathi (India)",
            "Microsoft Aarohi - Marathi (India)",
            "Google मराठी",
            "mr-in-x-mrf-local",
            "Marathi India"
        ],
        "voice_search_keywords": ["manohar", "aarohi", "मराठी", "marathi", "mr-in"],
        "fallback_behavior": "Search for any voice with lang='mr-IN' or prefix 'mr'. If no Marathi voice is installed, suppress audio and present clean Marathi text.",
        "translation_coverage": "100% (Complete UI & Copilot native translations)"
    }
}


def get_supported_language_codes() -> List[str]:
    """Returns the list of 8 supported ISO 639-1 language codes."""
    return list(MULTILINGUAL_VOICE_CAPABILITY_MAP.keys())


def get_voice_capability(lang_code: str) -> Optional[Dict[str, Any]]:
    """Returns the capability dictionary for a given language code."""
    return MULTILINGUAL_VOICE_CAPABILITY_MAP.get(lang_code.lower())


def get_bcp47_code_for_voice(lang_code: str) -> str:
    """Returns the exact BCP-47 speech recognition/synthesis code."""
    cap = get_voice_capability(lang_code)
    return cap["bcp47"] if cap else "en-IN"


def get_preferred_voice_keywords(lang_code: str) -> List[str]:
    """Returns preferred voice name matching keywords for SpeechSynthesis."""
    cap = get_voice_capability(lang_code)
    return cap.get("voice_search_keywords", ["en-in"]) if cap else ["en-in"]
