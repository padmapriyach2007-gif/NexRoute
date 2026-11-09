# -*- coding: utf-8 -*-
"""
NexRoute Mobile Bottom Navigation Component
Provides a native-feeling, touch-optimized, persistent glassmorphic bottom navigation bar
for mobile devices (Android and iOS).
Strictly hidden on desktop (width > 768px).
"""

from typing import Dict, Any


MOBILE_NAV_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "home": "Home",
        "map": "Map",
        "trips": "Trips",
        "places": "Places",
        "guide": "Guide"
    },
    "te": {
        "home": "హోమ్",
        "map": "మ్యాప్",
        "trips": "ట్రిప్స్",
        "places": "ప్రదేశాలు",
        "guide": "గైడ్"
    },
    "hi": {
        "home": "होम",
        "map": "मैप",
        "trips": "यात्राएं",
        "places": "स्थान",
        "guide": "गाइड"
    },
    "ta": {
        "home": "முகப்பு",
        "map": "வரைபடம்",
        "trips": "பயணங்கள்",
        "places": "இடங்கள்",
        "guide": "வழிகாட்டி"
    },
    "kn": {
        "home": "ಮುಖಪುಟ",
        "map": "ನಕ್ಷೆ",
        "trips": "ಪ್ರವಾಸಗಳು",
        "places": "ಸ್ಥಳಗಳು",
        "guide": "ಮಾರ್ಗದರ್ಶಿ"
    },
    "ml": {
        "home": "ഹോം",
        "map": "മാപ്പ്",
        "trips": "യാത്രകൾ",
        "places": "സ്ഥലങ്ങൾ",
        "guide": "ഗൈഡ്"
    },
    "bn": {
        "home": "হোম",
        "map": "ম্যাপ",
        "trips": "ভ্রমণ",
        "places": "স্থান",
        "guide": "গাইড"
    },
    "mr": {
        "home": "मुख्यपृष्ठ",
        "map": "नकाशा",
        "trips": "सहली",
        "places": "ठिकाणे",
        "guide": "मार्गदर्शक"
    }
}


def render_mobile_bottom_navigation_bar(current_view: str = "dashboard", lang: str = "en") -> str:
    """
    Generates the self-contained HTML/CSS/JS for the Mobile Bottom Navigation Bar.
    Renders on screens <= 768px, invisible on desktop.
    """
    labels = MOBILE_NAV_TRANSLATIONS.get(lang, MOBILE_NAV_TRANSLATIONS["en"])

    # Map current_view to normalized nav ID
    norm_view = current_view.lower().strip()
    if norm_view in ["map", "nav", "navigation", "map_nav"]:
        active_id = "map_nav"
    elif norm_view in ["copilot", "copilot_studio", "studio"]:
        active_id = "copilot_studio"
    elif norm_view in ["places", "sights"]:
        active_id = "places"
    elif norm_view in ["guide", "virtual_guide"]:
        active_id = "virtual_guide"
    else:
        active_id = "dashboard"

    items = [
        {"id": "dashboard", "icon": "🏠", "label": labels["home"]},
        {"id": "map_nav", "icon": "🧭", "label": labels["map"]},
        {"id": "copilot_studio", "icon": "✨", "label": labels["trips"]},
        {"id": "places", "icon": "🌟", "label": labels["places"]},
        {"id": "virtual_guide", "icon": "🚗", "label": labels["guide"]},
    ]

    items_html = ""
    for item in items:
        is_active = (item["id"] == active_id)
        active_class = " active" if is_active else ""
        indicator = '<span class="nav-active-pip"></span>' if is_active else ""
        items_html += f"""
        <a href="?view={item['id']}" target="_top" class="mobile-nav-item{active_class}" role="tab" aria-selected="{'true' if is_active else 'false'}" onclick="if(window.top && window.top.location){{window.top.location.search='?view={item['id']}'; return false;}}">
            <span class="nav-icon-wrap">{item['icon']}</span>
            <span class="nav-label">{item['label']}</span>
            {indicator}
        </a>
        """

    return f"""
    <style>
    /* Mobile Bottom Navigation Bar - Only visible on Mobile screens (<= 768px) */
    @media (min-width: 769px) {{
        #nexroute-mobile-bottom-nav,
        .nexroute-mobile-bottom-nav {{
            display: none !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }}
    }}

    @media (max-width: 768px) {{
        #nexroute-mobile-bottom-nav,
        .nexroute-mobile-bottom-nav {{
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            right: 0 !important;
            width: 100vw !important;
            height: calc(58px + env(safe-area-inset-bottom, 0px)) !important;
            background: rgba(10, 15, 30, 0.96) !important;
            backdrop-filter: blur(28px) saturate(200%) !important;
            -webkit-backdrop-filter: blur(28px) saturate(200%) !important;
            border-top: 1.5px solid rgba(56, 189, 248, 0.35) !important;
            box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.85), 0 -1px 0 rgba(255, 255, 255, 0.08) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-around !important;
            padding: 4px 6px calc(4px + env(safe-area-inset-bottom, 0px)) 6px !important;
            box-sizing: border-box !important;
            z-index: 9999999 !important;
            user-select: none !important;
            -webkit-user-select: none !important;
        }}

        .mobile-nav-item {{
            flex: 1 1 20% !important;
            max-width: 20% !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 2px !important;
            background: transparent !important;
            border: none !important;
            outline: none !important;
            padding: 4px 2px !important;
            cursor: pointer !important;
            color: #94a3b8 !important;
            text-decoration: none !important;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
            position: relative !important;
            touch-action: manipulation !important;
            -webkit-tap-highlight-color: transparent !important;
            min-height: 48px !important;
            border-radius: 10px !important;
        }}

        .mobile-nav-item:active {{
            transform: scale(0.92) !important;
            background: rgba(56, 189, 248, 0.12) !important;
        }}

        .nav-icon-wrap {{
            font-size: 1.25rem !important;
            line-height: 1 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 26px !important;
            height: 22px !important;
            transition: transform 0.2s ease !important;
        }}

        .nav-label {{
            font-size: 0.62rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.02em !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            max-width: 100% !important;
            line-height: 1.15 !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        }}

        .mobile-nav-item.active {{
            color: #38bdf8 !important;
            background: rgba(56, 189, 248, 0.10) !important;
        }}

        .mobile-nav-item.active .nav-icon-wrap {{
            transform: translateY(-2px) scale(1.10) !important;
            filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.7)) !important;
        }}

        .mobile-nav-item.active .nav-label {{
            color: #ffffff !important;
            font-weight: 900 !important;
            text-shadow: 0 0 8px rgba(56, 189, 248, 0.5) !important;
        }}

        .nav-active-pip {{
            position: absolute !important;
            bottom: 2px !important;
            width: 16px !important;
            height: 3px !important;
            background: linear-gradient(90deg, #38bdf8, #818cf8) !important;
            border-radius: 999px !important;
            box-shadow: 0 0 8px #38bdf8 !important;
        }}
    }}
    </style>

    <nav id="nexroute-mobile-bottom-nav" class="nexroute-mobile-bottom-nav" aria-label="Mobile Navigation Bar">
        {items_html}
    </nav>
    """
