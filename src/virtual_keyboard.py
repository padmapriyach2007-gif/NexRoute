"""
Virtual Multilingual Keyboard Component for P.A.T.H.F.I.N.D.E.R.
Supports 8 Indian & Global Languages:
- English (en)
- Telugu (te) - అచ్చులు, హల్లులు, గుణింతాలు & ప్రసిద్ధ ప్రదేశాలు
- Hindi (hi) - स्वर, व्यंजन, मात्राएँ & प्रमुख नगर
- Tamil (ta) - உயிர், மெய், குறிகள் & முக்கிய நகரங்கள்
- Kannada (kn) - ಸ್ವರ, ವ್ಯಂಜನ, ಗುಣಿತಾಕ್ಷರಗಳು & ಪ್ರಮುಖ ನಗರಗಳು
- Malayalam (ml) - സ്വരങ്ങൾ, വ്യഞ്ജനങ്ങൾ & പ്രധാന നഗരങ്ങൾ
- Bengali (bn) - স্বরবর্ণ, ব্যঞ্জনবর্ণ, কার & প্রধান শহর
- Marathi (mr) - स्वर, व्यंजने, मात्रा & प्रमुख शहरे

Features:
- Automatically pops up whenever the user focuses or clicks on any location or text input field.
- Floating ⌨️ toggle button docked bottom-right to open/minimize anytime.
- Real-time React/Streamlit event propagation (dispatches native 'input' and 'change' events via prototype setter).
- Quick location shortcut chips in the selected native script.
- Cyber-Neon Glassmorphic UI matching Pathfinder aesthetics.
"""

import json
from typing import Dict, Any

KEYBOARD_LAYOUTS: Dict[str, Dict[str, Any]] = {
    "te": {
        "name": "తెలుగు",
        "flag": "🇮🇳",
        "vowels": ["అ", "ఆ", "ఇ", "ఈ", "ఉ", "ఊ", "ఋ", "ఎ", "ఏ", "ఐ", "ఒ", "ఓ", "ఔ", "అం", "అః"],
        "consonants": [
            "క", "ఖ", "గ", "ఘ", "ఙ",
            "చ", "ఛ", "జ", "ఝ", "ఞ",
            "ట", "ఠ", "డ", "ఢ", "ణ",
            "త", "థ", "ద", "ధ", "న",
            "ప", "ఫ", "బ", "భ", "మ",
            "య", "ర", "ల", "వ", "శ", "ష", "స", "హ", "ళ", "క్ష", "ఱ"
        ],
        "matras": ["ా", "ి", "ీ", "ు", "ూ", "ృ", "ె", "ే", "ై", "ొ", "ో", "ౌ", "్", "ం", "ః"],
        "places": ["గుంటూరు", "విజయవాడ", "హైదరాబాదు", "అమరావతి", "తెనాలి", "విశాఖపట్నం", "తిరుపతి", "బాపట్ల", "మంగళగిరి", "చెన్నై"]
    },
    "hi": {
        "name": "हिन्दी",
        "flag": "🇮🇳",
        "vowels": ["अ", "आ", "इ", "ई", "उ", "ऊ", "ऋ", "ए", "ऐ", "ओ", "औ", "अं", "अः"],
        "consonants": [
            "क", "ख", "ग", "घ", "ङ",
            "च", "छ", "ज", "झ", "ञ",
            "ट", "ठ", "ड", "ढ", "ण",
            "त", "थ", "द", "ध", "न",
            "प", "फ", "ब", "भ", "म",
            "य", "र", "ल", "व", "श", "ष", "स", "ह", "क्ष", "त्र", "ज्ञ"
        ],
        "matras": ["ा", "ि", "ी", "ु", "ू", "ृ", "े", "ै", "ो", "ौ", "्", "ं", "ः", "ँ"],
        "places": ["गुंटूर", "विजयवाड़ा", "दिल्ली", "मुम्बई", "हैदराबाद", "जयपुर", "वाराणसी", "बेंगलुरु", "कोलकाता", "आगरा"]
    },
    "ta": {
        "name": "தமிழ்",
        "flag": "🇮🇳",
        "vowels": ["அ", "ஆ", "இ", "ஈ", "உ", "ஊ", "எ", "ஏ", "ஐ", "ஒ", "ஓ", "ஔ", "ஃ"],
        "consonants": [
            "க", "ங", "ச", "ஞ", "ட", "ண",
            "த", "ந", "ப", "ம", "ய", "ர",
            "ல", "வ", "ழ", "ள", "ற", "ன",
            "ஜ", "ஷ", "ஸ", "ஹ", "க்ஷ"
        ],
        "matras": ["ா", "ி", "ீ", "ு", "ூ", "ெ", "ே", "ை", "ொ", "ோ", "ௌ", "்"],
        "places": ["குண்டூர்", "விஜயவாடா", "சென்னை", "மதுரை", "கோயம்புத்தூர்", "திருச்சி", "சேலம்", "ஹைதராபாத்", "பெங்களூரு"]
    },
    "kn": {
        "name": "ಕನ್ನಡ",
        "flag": "🇮🇳",
        "vowels": ["ಅ", "ಆ", "ಇ", "ಈ", "ಉ", "ಊ", "ಋ", "ಎ", "ಏ", "ಐ", "ಒ", "ಓ", "ಔ", "ಅಂ", "ಅಃ"],
        "consonants": [
            "ಕ", "ಖ", "ಗ", "ಘ", "ಙ",
            "ಚ", "ಛ", "ಜ", "ಝ", "ಞ",
            "ಟ", "ಠ", "ಡ", "ಢ", "ಣ",
            "ತ", "ಥ", "ದ", "ಧ", "ನ",
            "ಪ", "ಫ", "ಬ", "ಭ", "ಮ",
            "ಯ", "ರ", "ಲ", "ವ", "ಶ", "ಷ", "ಸ", "ಹ", "ಳ"
        ],
        "matras": ["ಾ", "ಿ", "ೀ", "ು", "ೂ", "ೃ", "ೆ", "ೇ", "ೈ", "ೊ", "ೋ", "ೌ", "್", "ಂ", "ಃ"],
        "places": ["ಗುಂಟೂರು", "ವಿಜಯವಾಡ", "ಬೆಂಗಳೂರು", "ಮೈಸೂರು", "ಮಂಗಳೂರು", "ಹುಬ್ಬಳ್ಳಿ", "ಬೆಳಗಾವಿ", "ಹೈದರಾಬಾದ್"]
    },
    "ml": {
        "name": "മലയാളം",
        "flag": "🇮🇳",
        "vowels": ["അ", "ആ", "ഇ", "ഈ", "ഉ", "ഊ", "ഋ", "എ", "ഏ", "ഐ", "ഒ", "ഓ", "ഔ", "അം", "അഃ"],
        "consonants": [
            "ക", "ഖ", "ഗ", "ഘ", "ങ",
            "ച", "ഛ", "ജ", "ഝ", "ഞ",
            "ട", "ഠ", "ഡ", "ഢ", "ണ",
            "ത", "ഥ", "ദ", "ധ", "ന",
            "പ", "ഫ", "ബ", "ഭ", "മ",
            "യ", "ര", "ല", "വ", "ശ", "ഷ", "സ", "ഹ", "ള", "ഴ", "റ"
        ],
        "matras": ["ാ", "ി", "ീ", "ു", "ൂ", "ൃ", "െ", "േ", "ൈ", "ൊ", "ോ", "ൌ", "്", "ം", "ഃ"],
        "places": ["ഗുണ്ടൂർ", "വിജയവാഡ", "തിരുവനന്തപുരം", "കൊച്ചി", "കോഴിക്കോട്", "തൃശ്ശൂർ", "ഹൈദരാബാദ്", "ചെന്നൈ"]
    },
    "bn": {
        "name": "বাংলা",
        "flag": "🇮🇳",
        "vowels": ["অ", "আ", "ই", "ঈ", "উ", "ঊ", "ঋ", "এ", "ঐ", "ও", "ঔ", "অং", "অঃ"],
        "consonants": [
            "ক", "খ", "গ", "ঘ", "ঙ",
            "চ", "ছ", "জ", "ঝ", "ঞ",
            "ট", "ঠ", "ড", "ঢ", "ণ",
            "ত", "থ", "দ", "ধ", "ন",
            "প", "ফ", "ব", "ভ", "ম",
            "য", "র", "ল", "ব", "শ", "ষ", "স", "হ", "ক্ষ", "ড়", "ঢ়", "য়"
        ],
        "matras": ["া", "ি", "ী", "ু", "ূ", "ৃ", "ে", "ৈ", "ো", "ৌ", "্", "ং", "ঃ", "ঁ"],
        "places": ["গুন্টুর", "বিজয়ওয়াড়া", "কলকাতা", "ঢাকা", "হাওড়া", "শিলিগুড়ি", "হায়দরাবাদ", "দিল্লি"]
    },
    "mr": {
        "name": "मराठी",
        "flag": "🇮🇳",
        "vowels": ["अ", "आ", "इ", "ई", "उ", "ऊ", "ऋ", "ए", "ऐ", "ओ", "औ", "अं", "अः"],
        "consonants": [
            "क", "ख", "ग", "घ", "ङ",
            "च", "छ", "ज", "झ", "ञ",
            "ट", "ठ", "ड", "ढ", "ण",
            "त", "थ", "द", "ध", "न",
            "प", "फ", "ब", "भ", "म",
            "य", "र", "ल", "व", "श", "ष", "स", "ह", "ळ", "क्ष", "ज्ञ"
        ],
        "matras": ["ा", "ि", "ी", "ु", "ू", "ृ", "े", "ै", "ो", "ौ", "्", "ं", "ः"],
        "places": ["गुंटूर", "विजयवाडा", "मुंबई", "पुणे", "नागपूर", "नाशिक", "छत्रपती संभाजीनगर", "हैदराबाद"]
    },
    "en": {
        "name": "English",
        "flag": "🌐",
        "vowels": ["A", "E", "I", "O", "U"],
        "consonants": [
            "Q", "W", "R", "T", "Y", "P",
            "S", "D", "F", "G", "H", "J", "K", "L",
            "Z", "X", "C", "V", "B", "N", "M"
        ],
        "matras": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", ",", "."],
        "places": ["Guntur", "Vijayawada", "Hyderabad", "Amaravati", "Tenali", "Visakhapatnam", "Tirupati", "Bapatla", "Mangalagiri", "Chennai"]
    }
}


_JS_TEMPLATE = r"""
<div id="pathfinder-vk-mount-point" style="display:none;"></div>
<script>
(function() {
    try {
        var pWin = window.parent || window;
        var pDoc = (pWin && pWin.document) ? pWin.document : document;
        if (!pDoc || !pDoc.body) return;

        // Remove previous instance if existing
        var existingKb = pDoc.getElementById('pathfinder-virtual-keyboard-root');
        if (existingKb) {
            existingKb.remove();
        }
        var existingFab = pDoc.getElementById('pathfinder-vk-fab-trigger');
        if (existingFab) {
            existingFab.remove();
        }

        var LAYOUTS = __LAYOUTS_JSON__;
        var currentLang = ("__ACTIVE_LANG__" in LAYOUTS) ? "__ACTIVE_LANG__" : "te";
        var activeInputEl = null;

        // 1. Create Floating Keyboard Trigger FAB (Docked Bottom Right above Chatbot, 64x64 matching AURA)
        var fab = pDoc.createElement('div');
        fab.id = 'pathfinder-vk-fab-trigger';
        fab.innerHTML = '<span style="font-size: 1.6rem; pointer-events: none; filter: drop-shadow(0 0 8px rgba(0, 217, 255, 0.6));">⌨️</span>';
        fab.title = 'Open Virtual Multilingual Keyboard (వర్చువల్ కీబోర్డ్)';
        fab.style.cssText = [
            'position: fixed !important',
            'bottom: 100px !important',
            'right: 24px !important',
            'width: 64px !important',
            'height: 64px !important',
            'min-width: 64px !important',
            'max-width: 64px !important',
            'min-height: 64px !important',
            'max-height: 64px !important',
            'box-sizing: border-box !important',
            'border-radius: 50% !important',
            'background: linear-gradient(135deg, #091a32 0%, #0369a1 100%) !important',
            'border: 2.5px solid #00D9FF !important',
            'box-shadow: 0 0 24px rgba(0, 217, 255, 0.65), 0 8px 22px rgba(0,0,0,0.85) !important',
            'display: flex !important',
            'align-items: center !important',
            'justify-content: center !important',
            'cursor: pointer !important',
            'z-index: 99998 !important',
            'transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important',
            'user-select: none !important',
            'padding: 0 !important',
            'margin: 0 !important'
        ].join(';');

        fab.onmouseenter = function() {
            this.style.transform = 'scale(1.12) translateY(-3px)';
            this.style.boxShadow = '0 0 35px rgba(0, 240, 181, 0.95), 0 10px 28px rgba(0,0,0,0.85)';
            this.style.borderColor = '#00F0B5';
        };
        fab.onmouseleave = function() {
            this.style.transform = 'scale(1) translateY(0)';
            this.style.boxShadow = '0 0 24px rgba(0, 217, 255, 0.65), 0 8px 22px rgba(0,0,0,0.85)';
            this.style.borderColor = '#00D9FF';
        };

        // 2. Create the Virtual Keyboard Container (Cyberpunk Glassmorphic Drawer)
        var kbRoot = pDoc.createElement('div');
        kbRoot.id = 'pathfinder-virtual-keyboard-root';
        kbRoot.style.cssText = [
            'position: fixed !important',
            'bottom: 12px !important',
            'left: 50% !important',
            'transform: translateX(-50%) translateY(120%) !important',
            'width: min(880px, calc(100vw - 32px)) !important',
            'max-height: 52vh !important',
            'background: linear-gradient(135deg, rgba(8, 18, 36, 0.96) 0%, rgba(13, 27, 49, 0.98) 100%) !important',
            'backdrop-filter: blur(24px) !important',
            '-webkit-backdrop-filter: blur(24px) !important',
            'border: 1.5px solid rgba(0, 217, 255, 0.45) !important',
            'border-radius: 18px !important',
            'box-shadow: 0 16px 48px -4px rgba(0, 0, 0, 0.85), 0 0 32px rgba(0, 217, 255, 0.25), inset 0 1px 1px rgba(255, 255, 255, 0.15) !important',
            'z-index: 99999 !important',
            'padding: 12px 16px 14px 16px !important',
            'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Mukta", "Gautami", sans-serif !important',
            'transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease !important',
            'opacity: 0 !important',
            'pointer-events: none !important',
            'overflow-y: auto !important',
            'box-sizing: border-box !important'
        ].join(';');

        function openKeyboard() {
            kbRoot.style.transform = 'translateX(-50%) translateY(0)';
            kbRoot.style.opacity = '1';
            kbRoot.style.pointerEvents = 'auto';
        }

        function closeKeyboard() {
            kbRoot.style.transform = 'translateX(-50%) translateY(120%)';
            kbRoot.style.opacity = '0';
            kbRoot.style.pointerEvents = 'none';
        }

        fab.onclick = function(e) {
            e.stopPropagation();
            if (kbRoot.style.opacity === '1') {
                closeKeyboard();
            } else {
                findBestTargetInput();
                openKeyboard();
            }
        };

        function findBestTargetInput() {
            var inputs = pDoc.querySelectorAll('div[data-testid="stTextInput"] input, input[type="text"], input[type="search"], #pac-input');
            if (inputs.length > 0) {
                for (var i = 0; i < inputs.length; i++) {
                    if (pDoc.activeElement === inputs[i]) {
                        activeInputEl = inputs[i];
                        return;
                    }
                }
                activeInputEl = inputs[inputs.length > 1 ? 1 : 0];
                return;
            }
            try {
                var iframes = pDoc.querySelectorAll('iframe');
                for (var j = 0; j < iframes.length; j++) {
                    try {
                        var iDoc = iframes[j].contentDocument || iframes[j].contentWindow.document;
                        if (iDoc) {
                            var ifrInputs = iDoc.querySelectorAll('input[type="text"], input[type="search"], #pac-input');
                            if (ifrInputs.length > 0) {
                                activeInputEl = ifrInputs[0];
                                return;
                            }
                        }
                    } catch(ex) {}
                }
            } catch(e) {}
        }

        // Prevent keyboard clicks from unfocusing the active text input
        kbRoot.addEventListener('mousedown', function(e) {
            e.preventDefault();
        });

        // Auto-trigger on focus or click of any text input field
        function handleInputActivation(e) {
            if (e.target && e.target.tagName === 'INPUT' && (e.target.type === 'text' || !e.target.type || e.target.type === 'search')) {
                activeInputEl = e.target;
                openKeyboard();
            }
        }
        pDoc.addEventListener('focusin', handleInputActivation, true);
        pDoc.addEventListener('click', handleInputActivation, true);

        // Bind input listeners inside map or component iframes
        function bindIframeInputs() {
            try {
                var iframes = pDoc.querySelectorAll('iframe');
                iframes.forEach(function(ifr) {
                    try {
                        var iDoc = ifr.contentDocument || ifr.contentWindow.document;
                        if (iDoc && !ifr.getAttribute('data-vk-bound')) {
                            ifr.setAttribute('data-vk-bound', '1');
                            iDoc.addEventListener('focusin', handleInputActivation, true);
                            iDoc.addEventListener('click', handleInputActivation, true);
                        }
                    } catch(ex) {}
                });
            } catch(e) {}
        }
        bindIframeInputs();
        setInterval(bindIframeInputs, 2000);

        // Render Keyboard Inner Structure
        function renderKeyboardLayout() {
            var layout = LAYOUTS[currentLang] || LAYOUTS["te"];
            
            var html = '';
            html += '<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid rgba(0, 217, 255, 0.20); padding-bottom: 8px;">';
            html += '  <div style="display: flex; align-items: center; gap: 8px;">';
            html += '    <span style="font-size: 1.15rem;">⌨️</span>';
            html += '    <b style="font-size: 0.86rem; color: #EAF7FF; letter-spacing: 0.03em;">NEXROUTE Virtual Keyboard • <span style="color: #00D9FF;">' + layout.name + '</span></b>';
            html += '  </div>';
            html += '  <div style="display: flex; gap: 4px; overflow-x: auto; max-width: 60%; padding-bottom: 2px;">';

            for (var langCode in LAYOUTS) {
                var l = LAYOUTS[langCode];
                var isSel = (langCode === currentLang);
                var btnStyle = isSel
                    ? 'background: linear-gradient(135deg, #0284c7 0%, #00f2fe 100%); color: #ffffff; border: 1px solid #38bdf8; font-weight: 800;'
                    : 'background: rgba(15, 23, 42, 0.7); color: #94a3b8; border: 1px solid rgba(56, 189, 248, 0.2);';
                html += '<button type="button" class="vk-lang-tab" data-lang="' + langCode + '" style="' + btnStyle + ' border-radius: 6px; padding: 3px 8px; font-size: 0.70rem; cursor: pointer; white-space: nowrap; transition: all 0.15s;">' + l.flag + ' ' + l.name + '</button>';
            }

            html += '  </div>';
            html += '  <button type="button" id="btn-vk-close" style="background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.4); color: #fca5a5; border-radius: 6px; padding: 3px 10px; font-size: 0.75rem; font-weight: 800; cursor: pointer;">✕</button>';
            html += '</div>';

            // Popular Local Places Chips
            html += '<div style="display: flex; align-items: center; gap: 6px; overflow-x: auto; margin-bottom: 10px; padding: 2px 0;">';
            html += '  <span style="font-size: 0.68rem; color: #38bdf8; font-weight: 800; white-space: nowrap;">⚡ Quick:</span>';

            for (var pi = 0; pi < layout.places.length; pi++) {
                var placeName = layout.places[pi];
                html += '<button type="button" class="vk-place-chip" data-text="' + placeName + '" style="background: rgba(14, 165, 233, 0.14); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 12px; color: #e0f2fe; padding: 2px 9px; font-size: 0.74rem; cursor: pointer; white-space: nowrap; font-weight: 600;">📍 ' + placeName + '</button>';
            }
            html += '</div>';

            // Character Grids
            html += '<div style="display: flex; flex-direction: column; gap: 6px;">';
            
            // Row 1: Vowels
            html += '  <div style="display: flex; flex-wrap: wrap; gap: 4px; background: rgba(10, 25, 47, 0.5); padding: 5px 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">';
            html += '    <span style="font-size: 0.62rem; color: #94a3b8; font-weight: 800; width: 100%; margin-bottom: 2px;">VOWELS / అచ్చులు / स्वर:</span>';
            for (var vi = 0; vi < layout.vowels.length; vi++) {
                var vChar = layout.vowels[vi];
                html += '<button type="button" class="vk-key-btn" data-char="' + vChar + '">' + vChar + '</button>';
            }
            html += '  </div>';

            // Row 2: Matras
            html += '  <div style="display: flex; flex-wrap: wrap; gap: 4px; background: rgba(10, 25, 47, 0.5); padding: 5px 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">';
            html += '    <span style="font-size: 0.62rem; color: #34d399; font-weight: 800; width: 100%; margin-bottom: 2px;">SIGNS & MATRAS / గుణింతాలు / मात्राएँ:</span>';
            for (var mi = 0; mi < layout.matras.length; mi++) {
                var mChar = layout.matras[mi];
                html += '<button type="button" class="vk-key-btn vk-key-matra" data-char="' + mChar + '">' + mChar + '</button>';
            }
            html += '  </div>';

            // Row 3: Consonants
            html += '  <div style="display: flex; flex-wrap: wrap; gap: 4px; background: rgba(10, 25, 47, 0.5); padding: 5px 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">';
            html += '    <span style="font-size: 0.62rem; color: #38bdf8; font-weight: 800; width: 100%; margin-bottom: 2px;">CONSONANTS / హల్లులు / व्यंजन:</span>';
            for (var ci = 0; ci < layout.consonants.length; ci++) {
                var cChar = layout.consonants[ci];
                html += '<button type="button" class="vk-key-btn" data-char="' + cChar + '">' + cChar + '</button>';
            }
            html += '  </div>';

            // Row 4: Controls (Space, Del, Clear, Done)
            html += '  <div style="display: flex; gap: 6px; margin-top: 4px;">';
            html += '    <button type="button" id="btn-vk-space" style="flex: 3; background: rgba(30, 41, 59, 0.8); border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 8px; color: #f1f5f9; height: 38px; font-weight: 800; font-size: 0.84rem; cursor: pointer;">␣ Space</button>';
            html += '    <button type="button" id="btn-vk-del" style="flex: 1.5; background: rgba(239, 68, 68, 0.25); border: 1px solid rgba(239, 68, 68, 0.5); border-radius: 8px; color: #fca5a5; height: 38px; font-weight: 800; font-size: 0.82rem; cursor: pointer;">⌫ Del</button>';
            html += '    <button type="button" id="btn-vk-clear" style="flex: 1.2; background: rgba(245, 158, 11, 0.25); border: 1px solid rgba(245, 158, 11, 0.5); border-radius: 8px; color: #fde68a; height: 38px; font-weight: 800; font-size: 0.82rem; cursor: pointer;">✖ Clear</button>';
            html += '    <button type="button" id="btn-vk-enter" style="flex: 1.8; background: linear-gradient(135deg, #059669 0%, #10b981 100%); border: 1px solid #34d399; border-radius: 8px; color: #ffffff; height: 38px; font-weight: 900; font-size: 0.84rem; cursor: pointer; box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);">Done ⏎</button>';
            html += '  </div>';
            html += '</div>';

            kbRoot.innerHTML = html;
            attachKeyboardEvents();
        }

        // Inject styles for keys
        var styleEl = pDoc.getElementById('pathfinder-vk-styles');
        if (!styleEl) {
            styleEl = pDoc.createElement('style');
            styleEl.id = 'pathfinder-vk-styles';
            pDoc.head.appendChild(styleEl);
        }
        styleEl.textContent = `
            .vk-key-btn {
                min-width: 32px;
                height: 32px;
                padding: 0 6px;
                background: rgba(15, 23, 42, 0.85);
                border: 1px solid rgba(56, 189, 248, 0.25);
                border-radius: 6px;
                color: #ffffff;
                font-size: 0.95rem;
                font-weight: 700;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.12s ease;
                user-select: none;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            .vk-key-btn:hover {
                background: rgba(56, 189, 248, 0.35);
                border-color: #00D9FF;
                transform: translateY(-2px) scale(1.08);
                box-shadow: 0 0 10px rgba(0, 217, 255, 0.6);
                z-index: 2;
            }
            .vk-key-btn:active {
                transform: translateY(0) scale(0.96);
                background: #0284c7;
            }
            .vk-key-matra {
                background: rgba(5, 150, 105, 0.25);
                border-color: rgba(52, 211, 153, 0.35);
                color: #6ee7b7;
            }
            .vk-place-chip:hover {
                background: rgba(56, 189, 248, 0.35) !important;
                border-color: #38bdf8 !important;
                transform: translateY(-1px);
            }
        `;

        function setNativeInputValue(el, val) {
            var ownerWin = (el.ownerDocument && el.ownerDocument.defaultView) ? el.ownerDocument.defaultView : pWin;
            var proto = (ownerWin && ownerWin.HTMLInputElement) ? ownerWin.HTMLInputElement.prototype : (pWin.HTMLInputElement ? pWin.HTMLInputElement.prototype : null);
            var nativeSetter = proto && Object.getOwnPropertyDescriptor(proto, 'value') ? Object.getOwnPropertyDescriptor(proto, 'value').set : null;
            if (nativeSetter) {
                nativeSetter.call(el, val);
            } else {
                el.value = val;
            }
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }

        function typeStringIntoInput(str) {
            if (!activeInputEl) {
                findBestTargetInput();
            }
            if (!activeInputEl) return;

            var start = (activeInputEl.selectionStart !== null && activeInputEl.selectionStart !== undefined) ? activeInputEl.selectionStart : activeInputEl.value.length;
            var end = (activeInputEl.selectionEnd !== null && activeInputEl.selectionEnd !== undefined) ? activeInputEl.selectionEnd : activeInputEl.value.length;
            var val = activeInputEl.value || "";
            
            var newVal = val.slice(0, start) + str + val.slice(end);
            setNativeInputValue(activeInputEl, newVal);

            var nextPos = start + str.length;
            try {
                activeInputEl.setSelectionRange(nextPos, nextPos);
            } catch(e) {}
            try {
                activeInputEl.focus();
            } catch(e) {}
        }

        function deleteCharacter() {
            if (!activeInputEl) {
                findBestTargetInput();
            }
            if (!activeInputEl) return;

            var start = (activeInputEl.selectionStart !== null && activeInputEl.selectionStart !== undefined) ? activeInputEl.selectionStart : activeInputEl.value.length;
            var end = (activeInputEl.selectionEnd !== null && activeInputEl.selectionEnd !== undefined) ? activeInputEl.selectionEnd : activeInputEl.value.length;
            var val = activeInputEl.value || "";

            if (start === end && start > 0) {
                var prefix = Array.from(val.slice(0, start));
                prefix.pop();
                var newStart = prefix.join('');
                var newVal = newStart + val.slice(end);
                setNativeInputValue(activeInputEl, newVal);
                try {
                    activeInputEl.setSelectionRange(newStart.length, newStart.length);
                    activeInputEl.focus();
                } catch(e) {}
            } else if (start !== end) {
                var newVal = val.slice(0, start) + val.slice(end);
                setNativeInputValue(activeInputEl, newVal);
                try {
                    activeInputEl.setSelectionRange(start, start);
                    activeInputEl.focus();
                } catch(e) {}
            }
        }

        function clearInput() {
            if (!activeInputEl) {
                findBestTargetInput();
            }
            if (!activeInputEl) return;

            setNativeInputValue(activeInputEl, "");
            try {
                activeInputEl.focus();
            } catch(e) {}
        }

        function attachKeyboardEvents() {
            var langTabs = kbRoot.querySelectorAll('.vk-lang-tab');
            langTabs.forEach(function(btn) {
                btn.onclick = function(e) {
                    e.stopPropagation();
                    currentLang = btn.getAttribute('data-lang');
                    renderKeyboardLayout();
                };
            });

            var closeBtn = kbRoot.querySelector('#btn-vk-close');
            if (closeBtn) {
                closeBtn.onclick = function(e) {
                    e.stopPropagation();
                    closeKeyboard();
                };
            }

            var placeChips = kbRoot.querySelectorAll('.vk-place-chip');
            placeChips.forEach(function(chip) {
                chip.onclick = function(e) {
                    e.stopPropagation();
                    var text = chip.getAttribute('data-text');
                    clearInput();
                    typeStringIntoInput(text);
                };
            });

            var keyBtns = kbRoot.querySelectorAll('.vk-key-btn');
            keyBtns.forEach(function(k) {
                k.onclick = function(e) {
                    e.stopPropagation();
                    var ch = k.getAttribute('data-char');
                    typeStringIntoInput(ch);
                };
            });

            var spaceBtn = kbRoot.querySelector('#btn-vk-space');
            if (spaceBtn) {
                spaceBtn.onclick = function(e) {
                    e.stopPropagation();
                    typeStringIntoInput(" ");
                };
            }

            var delBtn = kbRoot.querySelector('#btn-vk-del');
            if (delBtn) {
                delBtn.onclick = function(e) {
                    e.stopPropagation();
                    deleteCharacter();
                };
            }

            var clearBtn = kbRoot.querySelector('#btn-vk-clear');
            if (clearBtn) {
                clearBtn.onclick = function(e) {
                    e.stopPropagation();
                    clearInput();
                };
            }

            var enterBtn = kbRoot.querySelector('#btn-vk-enter');
            if (enterBtn) {
                enterBtn.onclick = function(e) {
                    e.stopPropagation();
                    closeKeyboard();
                    if (activeInputEl) {
                        activeInputEl.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true }));
                    }
                };
            }
        }

        pDoc.body.appendChild(fab);
        pDoc.body.appendChild(kbRoot);

        renderKeyboardLayout();

    } catch(err) {
        console.error("Pathfinder Virtual Keyboard Error:", err);
    }
})();
</script>
"""


def get_virtual_keyboard_html(active_lang: str = "te") -> str:
    """
    Renders the HTML & JavaScript snippet that injects the Virtual Multilingual Keyboard
    directly into window.parent.document, binding to all search inputs on the page.
    """
    layouts_json = json.dumps(KEYBOARD_LAYOUTS, ensure_ascii=False)
    current_lang = active_lang if active_lang in KEYBOARD_LAYOUTS else "te"
    return _JS_TEMPLATE.replace("__LAYOUTS_JSON__", layouts_json).replace("__ACTIVE_LANG__", current_lang)
