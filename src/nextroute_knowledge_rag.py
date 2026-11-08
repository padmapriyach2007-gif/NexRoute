"""
NextRoute — Advanced Application Knowledge Base & RAG Retrieval Engine
Provides:
1. Comprehensive, structured ground-truth documentation for all NextRoute features.
2. Fast, resilient hybrid retrieval (Semantic + Keyword + Metadata filtering).
3. Intelligent General Travel Planning & Budget Estimation Engine.
4. Accurate Travel Distance & Duration Calculator (Road, Train, Flight, Walking).
5. Multilingual translation & adaptation for all 8 NextRoute supported languages:
   English (en), Telugu (te), Hindi (hi), Tamil (ta), Kannada (kn),
   Malayalam (ml), Bengali (bn), Marathi (mr).
"""

import re
import math
from typing import Dict, Any, List, Optional, Tuple


# =============================================================================
# 1. STRUCTURED NEXTROUTE APPLICATION KNOWLEDGE REPOSITORY
# =============================================================================

NEXTROUTE_KNOWLEDGE_DOCS: List[Dict[str, Any]] = [
    {
        "id": "DOC_SHORTEST_ROUTE",
        "title": "Shortest Route Calculation in NextRoute",
        "category": "navigation",
        "keywords": [
            "shortest route", "shortest distance", "find shortest route", "how to find shortest",
            "minimum distance", "least distance", "short route", "తక్కువ దూరం", "చిన్న మార్గం",
            "छोटा रास्ता", "न्यूनतम दूरी", "குறைந்த தூரம்", "ಕಡಿಮೆ ದೂರ", "ഏറ്റവും ചെറിയ വഴി"
        ],
        "summary": "NextRoute provides a dedicated 'Shortest Route' optimization objective that calculates the route with the minimum physical road-network distance.",
        "ui_steps": (
            "1. Open the **Navigation** tab on the main map.\n"
            "2. Enter your **Starting Point** and **Destination**.\n"
            "3. Under **Route Optimizer / Optimization Objective**, select **Shortest (Distance)**.\n"
            "4. NextRoute will compute the path with the least road mileage (in km) and display the geometry on the map."
        ),
        "details": (
            "The Shortest Route algorithm minimizes physical geodesic road-network kilometers rather than travel time. "
            "Note that the shortest distance may sometimes include narrower state highways or city arterial streets with slower speeds compared to the Fastest Route."
        ),
        "translations": {
            "te": "నెక్స్‌రూట్‌లో తక్కువ దూర మార్గాన్ని (Shortest Route) కనుగొనడానికి: 1. Navigation ట్యాబ్ తెరిచి ప్రారంభ, గమ్యస్థానాలను నమోదు చేయండి. 2. రూట్ ఆప్టిమైజర్‌లో 'Shortest (Distance)' ఎంచుకోండి. 3. సిస్టమ్ తక్కువ కిలోమీటర్ల మార్గాన్ని మ్యాప్‌పై ప్రదర్శిస్తుంది.",
            "hi": "नेक्स्ट-रूट में सबसे छोटा रास्ता (Shortest Route) खोजने के लिए: 1. नेविगेशन टैब खोलें और शुरुआत व गंतव्य स्थान दर्ज करें। 2. रूट ऑप्टिमाइज़र में 'Shortest (Distance)' चुनें। 3. सिस्टम न्यूनतम दूरी (किमी) वाला रास्ता मैप पर दिखाएगा।",
            "ta": "நெக்ஸ்-ரூட்டில் குறைந்த தூர வழியைக் காண: 1. நேவிகேஷன் தாவலைத் திறந்து தொடக்க மற்றும் இலக்கு இடங்களை உள்ளிடவும். 2. 'Shortest (Distance)' என்பதைத் தேர்ந்தெடுக்கவும். 3. குறைந்த தூரப் பாதை வரைபடத்தில் காட்டப்படும்.",
            "kn": "ನೆಕ್ಸ್-ರೂಟ್‌ನಲ್ಲಿ ಕಡಿಮೆ ದೂರದ ಮಾರ್ಗವನ್ನು ಹುಡುಕಲು: 1. Navigation ಟ್ಯಾಬ್ ತೆರೆದು ಪ್ರಾರಂಭ ಮತ್ತು ಗಮ್ಯಸ್ಥಾನ ನಮೂದಿಸಿ. 2. 'Shortest (Distance)' ಆಯ್ಕೆಮಾಡಿ. 3. ಕಡಿಮೆ ದೂರದ ಮಾರ್ಗವು ನಕ್ಷೆಯಲ್ಲಿ ಕಾಣಿಸುತ್ತದೆ.",
            "ml": "നെക്സ്-റൂട്ടിൽ ഏറ്റവും ചെറിയ വഴി കണ്ടെത്താൻ: 1. നാവിഗേഷൻ ടാബ് തുറന്ന് തുടക്കവും ലക്ഷ്യസ്ഥാനവും നൽകുക. 2. 'Shortest (Distance)' തിരഞ്ഞെടുക്കുക. 3. ഏറ്റവും കുറഞ്ഞ ദൂരമുള്ള വഴി മാപ്പിൽ ദൃശ്യമാകും."
        }
    },
    {
        "id": "DOC_FASTEST_ROUTE",
        "title": "Fastest Route Optimization in NextRoute",
        "category": "navigation",
        "keywords": [
            "fastest route", "quickest route", "fastest", "minimum time", "least time",
            "వేగవంతమైన మార్గం", "త్వరగా వెళ్ళే మార్గం", "सबसे तेज़ रास्ता", "வேகமான வழி", "വേഗമേറിയ വഴി"
        ],
        "summary": "The Fastest Route objective in NextRoute prioritizes high-speed national expressways and primary corridors to minimize your total travel duration.",
        "ui_steps": (
            "1. In the **Navigation** view, enter Start and Destination.\n"
            "2. Under **Route Optimizer**, select **Fastest (Duration)**.\n"
            "3. NextRoute routes traffic through national highways (e.g. NH65, NH16) with higher speed limits."
        ),
        "details": "Fastest Route uses real-world corridor speed profiles. It may be slightly longer in physical distance than Shortest Route, but offers the shortest driving duration.",
        "translations": {
            "te": "వేగవంతమైన మార్గం (Fastest Route) ప్రయాణ సమయాన్ని తగ్గిస్తుంది. నేషనల్ హైవేలు, ఎక్స్‌ప్రెస్‌వేల ద్వారా తక్కువ సమయంలో గమ్యాన్ని చేరుకోవడానికి ఇది సహాయపడుతుంది.",
            "hi": "सबसे तेज़ रास्ता (Fastest Route) यात्रा समय को कम करता है। यह राष्ट्रीय राजमार्गों और एक्सप्रेसवे को प्राथमिकता देता है ताकि आप सबसे कम समय में पहुँच सकें।"
        }
    },
    {
        "id": "DOC_VEHICLE_MODES",
        "title": "Changing Transportation & Vehicle Modes",
        "category": "vehicle_modes",
        "keywords": [
            "change vehicle mode", "vehicle mode", "transportation mode", "change transport",
            "bike mode", "car mode", "walking mode", "bicycle mode", "flight mode", "waterway",
            "ట్రాన్స్‌పోర్ట్ మోడ్", "వాహనం మార్చడం", "वाहन मोड बदलें", "வாகன பயன்முறை", "വാഹന മോഡ് മാറ്റുക"
        ],
        "summary": "NextRoute supports 9 transportation modes: Car, Motorcycle/Bike, Bicycle, Walking, Taxi, Flight, Waterway, Train, and Metro.",
        "ui_steps": (
            "1. In the **Navigation** view, locate the **Vehicle Mode Selector** (Automotive Drive Selector).\n"
            "2. Select your desired mode: **Car 🚗**, **Bike 🏍️**, **Bicycle 🚲**, **Walk 🚶**, **Taxi 🚕**, **Flight ✈️**, **Waterway 🚢**, **Train 🚆**, or **Metro 🚇**.\n"
            "3. NextRoute recalculates speed limits, travel time, and switches the **3D Virtual Guide** avatar model accordingly."
        ),
        "details": "Each mode uses customized routing parameters: pedestrian paths avoid highways; bicycles follow cycle tracks; flights follow designated air corridors.",
        "translations": {
            "te": "వాహనం మోడ్ మార్చడానికి: Navigation ప్యానెల్‌లోని Vehicle Mode Selector వద్ద Car, Bike, Bicycle, Walk, Taxi, Flight, Waterway, Train లలో మీకు కావలసినదాన్ని ఎంచుకోండి. 3D వర్చువల్ గైడ్ కూడా తదనుగుణంగా మారుతుంది.",
            "hi": "वाहन मोड बदलने के लिए: नेविगेशन पैनल में Vehicle Mode Selector से Car, Bike, Bicycle, Walk, Taxi, Flight या Train चुनें। 3D वर्चुअल गाइड भी आपके चुने वाहन के अनुसार बदल जाएगा।"
        }
    },
    {
        "id": "DOC_ADD_STOPS",
        "title": "Adding Intermediate Stops & Waypoints",
        "category": "navigation",
        "keywords": [
            "add stop", "add stops", "intermediate stop", "waypoint", "via", "multiple stops",
            "స్టాప్ జోడించడం", "మధ్యలో ఆగడం", "स्टॉप जोड़ें", "வழித்தட நிறுத்தம்", "നിർത്താനുള്ള സ്ഥലം"
        ],
        "summary": "You can add multiple intermediate waypoints to create multi-stop road trips in NextRoute.",
        "ui_steps": (
            "1. Enter your Start and Destination in the **Navigation** panel.\n"
            "2. Click the **+ Add Intermediate Stop** button.\n"
            "3. Search or type the stop name (e.g., a fuel station, restaurant, or intermediate city).\n"
            "4. NextRoute sequences the route: Start → Stop 1 → [Stop 2] → Destination, computing individual segment ETAs."
        ),
        "details": "Waypoints can be reordered or removed. NextRoute recalculates the cumulative distance and arrival times across all segments.",
        "translations": {
            "te": "మధ్యలో స్టాప్ జోడించడానికి: Navigation ప్యానెల్‌లో '+ Add Intermediate Stop' క్లిక్ చేసి, మీరు ఆగాలనుకునే నగరం లేదా ప్రదేశాన్ని నమోదు చేయండి.",
            "hi": "रास्ते में स्टॉप जोड़ने के लिए: नेविगेशन पैनल में '+ Add Intermediate Stop' पर क्लिक करें और उस शहर या जगह का नाम दर्ज करें।"
        }
    },
    {
        "id": "DOC_MY_TRIPS",
        "title": "Saving Trips & Using My Trips (Itinerary Studio)",
        "category": "trips_and_places",
        "keywords": [
            "save trip", "save route", "my trips", "saved trips", "itinerary studio", "bookmark route",
            "ట్రిప్ సేవ్ చేయడం", "నా ట్రిప్పులు", "ट्रिप सेव करें", "பயணத்தை சேமிக்க", "യാത്ര സേവ് ചെയ്യുക"
        ],
        "summary": "NextRoute lets you save routes, bookmark journeys, and access past itineraries via the 'My Trips' studio.",
        "ui_steps": (
            "1. After calculating any route on the map, click the **💾 Save Route / Save Trip** button.\n"
            "2. Enter a custom trip title (e.g., 'Goa Road Trip 2026').\n"
            "3. Access all saved journeys anytime by clicking the **My Trips** tab on the top dashboard."
        ),
        "details": "Saved trips store start coordinates, destination, waypoints, selected vehicle mode, and preferred objective for one-click reload.",
        "translations": {
            "te": "ట్రిప్ సేవ్ చేయడానికి: రూట్ లెక్కించిన తర్వాత '💾 Save Route' బటన్ క్లిక్ చేయండి. టాప్ డాష్‌బోర్డ్‌లోని 'My Trips' ట్యాబ్ ద్వారా మీ సేవ్ చేసిన ట్రిప్పులను ఎప్పుడైనా చూడవచ్చు.",
            "hi": "ट्रिप सेव करने के लिए: रूट की गणना के बाद '💾 Save Route' पर क्लिक करें। मुख्य डैशबोर्ड के 'My Trips' टैब में जाकर अपनी सेव की गई ट्रिप्स कभी भी देख सकते हैं।"
        }
    },
    {
        "id": "DOC_HOTELS",
        "title": "Finding Hotels, Stays & Resorts in NextRoute",
        "category": "services",
        "keywords": [
            "hotel", "hotels", "stays", "resorts", "lodging", "find hotels", "hotel feature",
            "హోటళ్ళు", "స్టేస్", "రిసార్ట్స్", "होटल खोजें", "விடுதிகள்", "ഹോട്ടലുകൾ"
        ],
        "summary": "NextRoute features a dedicated Hotels tool to discover stays, resorts, and lodges along your corridor or near your destination.",
        "ui_steps": (
            "1. Click the **Hotels (Stays & Resorts)** card on the welcome dashboard, or select the **Hotels** filter under Facilities.\n"
            "2. View verified stays along your active route corridor.\n"
            "3. Filter by budget, star ratings, and amenities (Wi-Fi, pool, parking), and view exact deviation distance from your highway."
        ),
        "details": "NextRoute displays verified hotels with distances from the road corridor, helping you avoid long detours for overnight halts.",
        "translations": {
            "te": "హోటళ్ళు కనుగొనడానికి: డాష్‌బోర్డ్‌లోని 'Hotels' కార్డ్ క్లిక్ చేయండి లేదా Facilities ఫిల్టర్‌లో హోటల్స్ ఎంచుకోండి. మీ ప్రయాణ మార్గంలోని హోటళ్లు, రేటింగ్‌లు కనిపిస్తాయి.",
            "hi": "होटल खोजने के लिए: डैशबोर्ड पर 'Hotels' कार्ड पर क्लिक करें या Facilities में होटल फ़िल्टर चुनें। आपके रास्ते के पास उपलब्ध होटल और उनकी दूरी दिखेगी।"
        }
    },
    {
        "id": "DOC_FLIGHTS",
        "title": "Air Corridors & Flight Route Planner",
        "category": "services",
        "keywords": [
            "flight", "flights", "air corridors", "flight planner", "airport", "airplane",
            "ఫ్లైట్స్", "విమానాలు", "फ्लाइट्स", "விமானங்கள்", "വിമാന സർവീസ്"
        ],
        "summary": "NextRoute includes an Air Corridors flight planner for intercity and international route planning.",
        "ui_steps": (
            "1. Click the **Flights (Air Corridors)** card on the top dashboard or switch Vehicle Mode to **Flight ✈️**.\n"
            "2. Enter departure and arrival cities/airports.\n"
            "3. NextRoute calculates geodesic airway distance, flight cruising duration, and lists connecting airport hubs."
        ),
        "details": "Note: NextRoute provides flight routing geometry, duration, and airport planning estimates. Ticket booking links redirect to authorized airline portals.",
        "translations": {
            "te": "ఫ్లైట్ ప్లానర్ ఉపయోగించడానికి: డాష్‌బోర్డ్‌లో 'Flights' కార్డ్ క్లిక్ చేయండి. విమాన ప్రయాణ దూరం, ఎగిరే సమయం మరియు సమీప విమానాశ్రయాలను ఇది లెక్కిస్తుంది.",
            "hi": "फ्लाइट प्लानर के लिए: डैशबोर्ड पर 'Flights' कार्ड पर क्लिक करें। यह हवाई दूरी, उड़ान समय और नजदीकी हवाई अड्डों की जानकारी देता है।"
        }
    },
    {
        "id": "DOC_RESTAURANTS",
        "title": "Discovering Restaurants & Dining Along Route",
        "category": "services",
        "keywords": [
            "restaurant", "restaurants", "food", "dining", "dhaba", "cafe", "eat",
            "రెస్టారెంట్లు", "భోజనం", "रेस्टोरेंट", "உணவகங்கள்", "ഭക്ഷണശാലകൾ"
        ],
        "summary": "NextRoute's Dining tool discovers highway dhabas, cafes, vegetarian family restaurants, and food stops along your route.",
        "ui_steps": (
            "1. Click the **Restaurants (Dining & Food)** card on the dashboard or select **Food** in the Facilities filter.\n"
            "2. NextRoute highlights verified eateries along your active highway corridor.\n"
            "3. Filter by cuisine, pure vegetarian, 24/7 highway dhabas, and coffee stops."
        ),
        "details": "Corridor filtering ensures you only see restaurants directly along your driving path without requiring detour mileage.",
        "translations": {
            "te": "రెస్టారెంట్లు వెతకడానికి: డాష్‌బోర్డ్‌లో 'Restaurants' కార్డ్ క్లిక్ చేయండి. హైవే పక్కన ఉన్న ధాబాలు, ఫ్యామిలీ రెస్టారెంట్లు మరియు కేఫ్‌లు మ్యాప్‌పై కనిపిస్తాయి.",
            "hi": "रेस्टोरेंट खोजने के लिए: डैशबोर्ड पर 'Restaurants' कार्ड चुनें। हाईवे के किनारे स्थित ढाबे और रेस्टोरेंट आपकी स्क्रीन पर दिखाई देंगे।"
        }
    },
    {
        "id": "DOC_LANGUAGES",
        "title": "Changing Application Language in NextRoute",
        "category": "settings",
        "keywords": [
            "change language", "language settings", "telugu", "hindi", "tamil", "kannada",
            "malayalam", "bengali", "marathi", "supported languages", "భాష మార్చడం", "भाषा बदलें"
        ],
        "summary": "NextRoute supports 8 native languages: English (en), Telugu (te), Hindi (hi), Tamil (ta), Kannada (kn), Malayalam (ml), Bengali (bn), and Marathi (mr).",
        "ui_steps": (
            "1. Look at the top header bar and click the **Language Selector (🌐)** dropdown.\n"
            "2. Or go to **Profile & Settings** → **Language**.\n"
            "3. Select your preferred language (e.g. తెలుగు, हिन्दी, தமிழ், etc.).\n"
            "4. All navigation buttons, chatbot greetings, itineraries, and voice synthesis will adapt immediately."
        ),
        "details": "Language preference is stored in your session state and persists across all app views.",
        "translations": {
            "te": "భాషను మార్చడానికి: పైభాగంలో ఉన్న లాంగ్వేజ్ సెలెక్టర్ (🌐) లేదా Profile & Settings లోకి వెళ్లి తెలుగు, హిందీ, ఇంగ్లీష్ మొదలైన 8 భాషలలో మీకు నచ్చినదాన్ని ఎంచుకోండి.",
            "hi": "भाषा बदलने के लिए: शीर्ष पर स्थित भाषा चयनकर्ता (🌐) या Profile & Settings में जाकर हिंदी, तेलुगु, अंग्रेजी आदि 8 भाषाओं में से चुनें।"
        }
    },
    {
        "id": "DOC_AVOID_PREFERENCES",
        "title": "Routing Preferences: Avoid Tolls, Highways & Ferries",
        "category": "navigation",
        "keywords": [
            "avoid tolls", "avoid highways", "avoid ferries", "toll road", "routing preferences",
            "టోల్ నివారించండి", "హైవే నివారించండి", "टोल से बचें", "டோல் தவிர்க்க"
        ],
        "summary": "NextRoute provides customizable avoidance toggles: Avoid Tolls (FASTag plazas), Avoid Highways (expressways), and Avoid Ferries (water crossings).",
        "ui_steps": (
            "1. In the Navigation panel, expand **Routing Preferences**.\n"
            "2. Toggle **Avoid Tolls** to use toll-free state highways.\n"
            "3. Toggle **Avoid Highways** to route through scenic regional roads.\n"
            "4. Toggle **Avoid Ferries** to enforce continuous land bridges."
        ),
        "details": "Avoid Tolls is especially valuable for budget travelers looking to eliminate FASTag fees over interstate trips.",
        "translations": {
            "te": "టోల్ ఫీజులను నివారించడానికి Routing Preferences లో 'Avoid Tolls' ఆన్ చేయండి. ఎక్స్‌ప్రెస్‌వేలను నివారించడానికి 'Avoid Highways' ఉపయోగించండి.",
            "hi": "टोल से बचने के लिए Routing Preferences में 'Avoid Tolls' ऑन करें। एक्सप्रेसवे से बचने के लिए 'Avoid Highways' का प्रयोग करें।"
        }
    },
    {
        "id": "DOC_EMERGENCY_RADAR",
        "title": "Emergency Radar & SOS Evacuation",
        "category": "services",
        "keywords": [
            "emergency radar", "sos", "hospitals", "police", "trauma center", "accident",
            "ఎమర్జెన్సీ", "ఆసుపత్రి", "आपातकालीन सेवा", "மருத்துவமனை", "അടിയന്തരാവസ്ഥ"
        ],
        "summary": "The Emergency Radar scans a 360° radius around your live location for nearest hospitals, police stations, fire stations, and trauma centers.",
        "ui_steps": (
            "1. Click the red **🚨 Emergency Radar / SOS** button on the map header.\n"
            "2. View instant distance, emergency phone numbers, and one-click turn-by-turn routing to the closest facility."
        ),
        "details": "Includes offline coordinate caching for essential emergency services in case of mobile network drops.",
        "translations": {
            "te": "అత్యవసర పరిస్థితుల్లో మ్యాప్ పైభాగంలో ఉన్న '🚨 Emergency Radar / SOS' బటన్ క్లిక్ చేయండి. సమీప ఆసుపత్రులు, పోలీస్ స్టేషన్లు మరియు అత్యవసర నంబర్లు తక్షణమే కనిపిస్తాయి.",
            "hi": "आपातकालीन स्थिति में '🚨 Emergency Radar / SOS' पर क्लिक करें। नजदीकी अस्पताल और पुलिस स्टेशन की जानकारी तुरंत प्राप्त होगी।"
        }
    },
    {
        "id": "DOC_SPEEDOMETER",
        "title": "Digital Speedometer Cockpit & Drive Modes",
        "category": "navigation",
        "keywords": [
            "speedometer", "speed limit", "cockpit", "eco mode", "sport mode", "drive mode",
            "స్పీడోమీటర్", "వేగ పరిమితి", "स्पीडोमीटर", "வேகமானி"
        ],
        "summary": "NextRoute features an interactive digital speedometer cockpit with legal speed limit warnings and Eco, Comfort, and Sport driving dynamics.",
        "ui_steps": (
            "1. In the Navigation HUD, open the **Digital Cockpit**.\n"
            "2. View your real-time velocity (km/h or mi/h), road speed limit, and toggle between Eco, Comfort, and Sport modes."
        ),
        "details": "Alerts flash amber when exceeding the posted highway speed limit.",
        "translations": {
            "te": "డిజిటల్ స్పీడోమీటర్ మీ ప్రయాణ వేగాన్ని మరియు రోడ్డు వేగ పరిమితిని చూపిస్తుంది. Eco, Comfort, Sport డ్రైవ్ మోడ్‌లను ఎంచుకోవచ్చు.",
            "hi": "डिजिटल स्पीडोमीटर आपकी गति और सड़क की गति सीमा दिखाता है। इसमें Eco, Comfort और Sport मोड उपलब्ध हैं।"
        }
    },
    {
        "id": "DOC_3D_VIRTUAL_GUIDE",
        "title": "3D Virtual Guide & Vehicle Synchronization",
        "category": "navigation",
        "keywords": [
            "virtual guide", "3d guide", "avatar", "storyteller", "guide vehicle",
            "వర్చువల్ గైడ్", "గైడ్ వాహనం", "वर्चुअल गाइड", "மெய்நிகர் வழிகாட்டி"
        ],
        "summary": "NextRoute's 3D Virtual Guide travels along the road network using the exact vehicle mode you select (walking, bicycle, motorcycle, car, flight).",
        "ui_steps": (
            "1. Calculate any route between Start and Destination.\n"
            "2. The **3D Virtual Guide** automatically unlocks on the map.\n"
            "3. Switch vehicle modes in the drive selector; the 3D model immediately adapts."
        ),
        "details": "Provides audio landmark storytelling and turn-by-turn guidance matching the vehicle dynamics.",
        "translations": {
            "te": "3D వర్చువల్ గైడ్ మీరు ఎంచుకున్న వాహనంలో (నడక, సైకిల్, బైక్, కారు) ప్రయాణిస్తూ ప్రదేశాల వివరాలను వివరిస్తుంది.",
            "hi": "3D वर्चुअल गाइड आपके चुने वाहन में यात्रा करते हुए ऐतिहासिक और महत्वपूर्ण स्थलों की जानकारी देता है।"
        }
    },
    {
        "id": "DOC_VOICE_ASSISTANT_SEPARATION",
        "title": "Main Dashboard Voice Assistant vs. Chatbot Travel Copilot",
        "category": "system_and_voice",
        "keywords": [
            "voice assistant", "jarvis", "chatbot difference", "aura difference", "voice control",
            "వాయిస్ అసిస్టెంట్ తేడా", "வாய்ஸ் அசிஸ்டண்ட்"
        ],
        "summary": "NextRoute features two completely independent AI assistants: the Main Dashboard Voice Assistant (JARVIS voice control) and the AURA Travel Copilot Chatbot.",
        "ui_steps": (
            "• **Main Dashboard Assistant (AURA / JARVIS):** Persistent hands-free voice loop on the welcome HUD that executes application commands (navigate, switch modes, show hotels).\n"
            "• **Chatbot Copilot:** Conversational assistant inside the chat box that answers travel queries, plans itineraries, estimates budgets, and auto-speaks responses."
        ),
        "details": "Both assistants have separate audio controllers, separate conversation histories, and an audio mutex lock to prevent cross-talking.",
        "translations": {
            "te": "నెక్స్‌రూట్‌లో రెండు స్వతంత్ర AIలు ఉన్నాయి: 1. డాష్‌బోర్డ్ వాయిస్ అసిస్టెంట్ (JARVIS) - వాయిస్ ద్వారా యాప్‌ను నియంత్రిస్తుంది. 2. చాట్‌బాట్ కోపైలట్ - ప్రయాణ ప్రణాళికలు, బడ్జెట్ మరియు సందేహాలకు సమాధానం ఇస్తుంది.",
            "hi": "नेक्स्ट-रूट में दो स्वतंत्र AI सहायक हैं: 1. डैशबोर्ड वॉयस असिस्टेंट (JARVIS) जो वॉयस कमांड से ऐप चलाता है। 2. चैटबॉट कोपायलट जो यात्रा योजना और बजट पर बातचीत करता है।"
        }
    },
    {
        "id": "DOC_LIMITATIONS_DISCLOSURE",
        "title": "Known Limitations & Operational Boundaries",
        "category": "troubleshooting",
        "keywords": [
            "limitations", "limit", "offline limit", "traffic accuracy", "gps accuracy", "constraints",
            "పరిమితులు", "सीमाएं", "வரம்புகள்", "പരിമിതികൾ"
        ],
        "summary": "NextRoute prioritizes transparency regarding data sources, routing boundaries, and hardware dependencies.",
        "ui_steps": (
            "• **Public OSRM Service:** Rate limits apply to the public demo routing server.\n"
            "• **Live Traffic:** In the absence of a commercial traffic probe API, durations use calibrated highway speed models.\n"
            "• **Offline Routing:** Embedded offline road graph covers regional Andhra Pradesh / Guntur / Tenali corridors; worldwide routing requires internet connectivity to OSRM.\n"
            "• **Accessibility Data:** Dependent on OpenStreetMap tags; unverified segments are reported transparently."
        ),
        "details": "For production fleet deployments, connect dedicated self-hosted OSRM servers via OSRM_BASE_URL.",
        "translations": {
            "te": "నెక్స్‌రూట్ పరిమితులు: పబ్లిక్ OSRM రేట్ లిమిట్స్ కలిగి ఉండవచ్చు. లైవ్ ట్రాఫిక్ లేనప్పుడు హైవే స్పీడ్ మోడల్స్ వాడబడతాయి. ఆఫ్‌లైన్ రూటింగ్ స్థానిక ప్రాంతాలకు మాత్రమే పరిమితం.",
            "hi": "नेक्स्ट-रूट की सीमाएं: सार्वजनिक OSRM सर्वर पर रेट सीमाएं हो सकती हैं। लाइव ट्रैफिक न होने पर मॉडल अनुमानित समय दिखाता है।"
        }
    }
]


# =============================================================================
# 2. HYBRID RAG RETRIEVAL ENGINE FOR NEXTROUTE
# =============================================================================

class NextRouteRAGRetriever:
    """
    Semantic and keyword-aware RAG retrieval engine for NextRoute application knowledge.
    Returns grounded, factual feature descriptions, UI steps, and multilingual answers.
    """

    STOP_WORDS = {
        "a", "an", "the", "in", "to", "of", "and", "or", "for", "do", "i", "it", "my", "on", "me",
        "is", "are", "was", "were", "this", "that", "how", "what", "can", "tell", "explain", "give",
        "with", "from", "at", "by", "trip", "travel", "plan", "about", "show", "get", "will", "does",
        "you", "your", "please", "help", "find", "use", "want", "take", "make", "need"
    }

    def __init__(self, docs: Optional[List[Dict[str, Any]]] = None):
        self.docs = docs or NEXTROUTE_KNOWLEDGE_DOCS

    def retrieve(self, query: str, lang: str = "en", top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Retrieves top-k relevant knowledge chunks matching user query.
        Uses exact keyword matching, token overlap without stop-words, and semantic intent.
        """
        q = (query or "").lower().strip()
        if not q:
            return []

        all_tokens = set(re.findall(r"\w+", q))
        content_tokens = {t for t in all_tokens if t not in self.STOP_WORDS and len(t) > 2}

        scored_docs: List[Tuple[float, Dict[str, Any]]] = []

        for doc in self.docs:
            score = 0.0
            has_exact_kw = False

            # 1. Exact keyword phrase matching
            for kw in doc.get("keywords", []):
                kw_lower = kw.lower().strip()
                if not kw_lower:
                    continue
                # If multi-word keyword phrase is directly in q
                if " " in kw_lower and kw_lower in q:
                    score += 8.0
                    has_exact_kw = True
                elif kw_lower in content_tokens or f" {kw_lower} " in f" {q} ":
                    # Exact single-word keyword like "speedometer", "hotels", "radar"
                    if kw_lower not in self.STOP_WORDS and len(kw_lower) > 3:
                        score += 5.0
                        has_exact_kw = True

            # 2. Title token matching (excluding stop words)
            title_tokens = {t for t in re.findall(r"\w+", doc.get("title", "").lower()) if t not in self.STOP_WORDS and len(t) > 2}
            overlap = len(content_tokens.intersection(title_tokens))
            score += overlap * 2.0

            # 3. Explicit app mention boost
            if any(w in q for w in ["nextroute", "in this app", "in the app", "on the app", "app features"]):
                score += 2.0

            if has_exact_kw or score >= 4.5:
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_docs[:top_k]]

    def answer_from_knowledge(self, query: str, lang: str = "en") -> Optional[Dict[str, Any]]:
        """
        Directly generates an accurate, concise answer from application knowledge.
        Returns None if query is not an application-specific feature question.
        """
        q = (query or "").lower().strip()
        results = self.retrieve(query, lang=lang, top_k=1)
        if not results:
            return None

        doc = results[0]

        # Verify that at least one distinct keyword phrase or significant title term matched
        kws = [k.lower() for k in doc.get("keywords", [])]
        matched_kw = any((k in q if " " in k else (f" {k} " in f" {q} " or k in q.split())) for k in kws if k not in self.STOP_WORDS)
        title_tokens = {t for t in re.findall(r"\w+", doc.get("title", "").lower()) if t not in self.STOP_WORDS and len(t) > 2}
        q_tokens = {t for t in re.findall(r"\w+", q) if t not in self.STOP_WORDS and len(t) > 2}
        matched_title = len(title_tokens.intersection(q_tokens)) >= 2

        if not (matched_kw or matched_title):
            return None

        # Check native translation availability
        tr_map = doc.get("translations", {})
        if lang in tr_map and tr_map[lang]:
            return {
                "badge": f"🧭 AURA • {doc.get('title', 'NextRoute Help').upper()}",
                "response": tr_map[lang],
                "doc_id": doc["id"]
            }

        # Format concise English response with steps
        resp = f"**{doc['title']}**\n\n{doc['summary']}\n\n**How to use:**\n{doc['ui_steps']}"
        return {
            "badge": f"🧭 AURA • {doc.get('title', 'NextRoute Help').upper()}",
            "response": resp,
            "doc_id": doc["id"]
        }

    def format_knowledge_for_prompt(self, docs: List[Dict[str, Any]], lang: str = "en") -> str:
        """Formats retrieved documentation into a clean context block for LLM prompt injection."""
        if not docs:
            return ""

        context_lines = ["\n[GROUND-TRUTH NEXTROUTE APPLICATION KNOWLEDGE]:"]
        for d in docs:
            context_lines.append(f"• Feature: {d['title']}")
            context_lines.append(f"  Summary: {d['summary']}")
            context_lines.append(f"  UI Steps: {d['ui_steps'].replace(chr(10), ' ')}")
            if d.get("details"):
                context_lines.append(f"  Technical Truth: {d['details']}")
        context_lines.append("Use this ground-truth to answer accurately. Never invent non-existent UI buttons or features.\n")
        return "\n".join(context_lines)


# =============================================================================
# 3. GENERAL TRAVEL PLANNING & BUDGET ESTIMATION ENGINE
# =============================================================================

class GeneralTravelPlanningEngine:
    """
    Generates realistic, day-wise itineraries, budget breakdowns, and practical travel advice
    for any Indian or global destination.
    """

    DESTINATION_PROFILES: Dict[str, Dict[str, Any]] = {
        "hyderabad": {
            "name": "Hyderabad",
            "state": "Telangana",
            "best_time": "October to March",
            "attractions": ["Charminar & Laad Bazaar", "Golconda Fort Sound & Light", "Ramoji Film City", "Hussain Sagar Lake & Buddha Statue", "Chowmahalla Palace", "Birla Mandir"],
            "food": ["Hyderabadi Dum Biryani (Paradise/Shadab)", "Irani Chai & Osmania Biscuits", "Double Ka Meetha"],
            "avg_stay_budget": 1500,
            "avg_stay_mid": 3500,
            "avg_food_day": 600,
            "local_transport_day": 400
        },
        "goa": {
            "name": "Goa",
            "state": "Goa",
            "best_time": "November to February",
            "attractions": ["Fort Aguada & Candolim Beach", "Baga & Calangute Water Sports", "Old Goa Churches (Basilica of Bom Jesus)", "Palolem & Agonda Beach", "Dudhsagar Waterfalls", "Mandovi River Cruise"],
            "food": ["Goan Fish Curry Thali", "Prawn Balchão", "Bebinca", "Beach shack dining"],
            "avg_stay_budget": 1800,
            "avg_stay_mid": 4500,
            "avg_food_day": 800,
            "local_transport_day": 500  # Scooter rental + fuel
        },
        "kerala": {
            "name": "Kerala",
            "state": "Kerala",
            "best_time": "September to March",
            "attractions": ["Munnar Tea Gardens & Anamudi", "Alleppey Backwater Houseboat", "Fort Kochi & Chinese Fishing Nets", "Wayanad Edakkal Caves", "Varkala Cliff Beach"],
            "food": ["Kerala Sadya on Banana Leaf", "Appam with Stew", "Karimeen Pollichathu"],
            "avg_stay_budget": 1600,
            "avg_stay_mid": 4000,
            "avg_food_day": 650,
            "local_transport_day": 600
        },
        "manali": {
            "name": "Manali",
            "state": "Himachal Pradesh",
            "best_time": "October to June (Snow: Dec-Feb)",
            "attractions": ["Solang Valley Adventure Sports", "Rohtang Pass Snow Point", "Hadimba Temple & Old Manali Cafes", "Jogini Waterfalls", "Atal Tunnel & Sissu"],
            "food": ["Siddu with Ghee", "Trout Fish", "Tibetan Momos & Thukpa"],
            "avg_stay_budget": 1400,
            "avg_stay_mid": 3500,
            "avg_food_day": 550,
            "local_transport_day": 700
        },
        "kashmir": {
            "name": "Kashmir (Srinagar & Gulmarg)",
            "state": "Jammu & Kashmir",
            "best_time": "April to October (Tulips in Apr, Snow in Dec-Feb)",
            "attractions": ["Dal Lake Shikara Ride & Houseboat", "Gulmarg Gondola Cable Car", "Pahalgam Betaab Valley", "Sonamarg Glacier", "Mughal Gardens (Shalimar & Nishat)"],
            "food": ["Kashmiri Wazwan (Rogan Josh, Gushtaba)", "Kahwa Tea with Saffron & Almonds"],
            "avg_stay_budget": 2000,
            "avg_stay_mid": 5000,
            "avg_food_day": 750,
            "local_transport_day": 800
        },
        "jaipur": {
            "name": "Jaipur",
            "state": "Rajasthan",
            "best_time": "October to March",
            "attractions": ["Amber Fort & Elephant/Jeep Ride", "Hawa Mahal (Palace of Winds)", "City Palace & Jantar Mantar", "Nahargarh Fort Sunset Point", "Chokhi Dhani Cultural Village"],
            "food": ["Dal Baati Churma", "Pyaaz Kachori (Rawat)", "Ghewar"],
            "avg_stay_budget": 1300,
            "avg_stay_mid": 3200,
            "avg_food_day": 500,
            "local_transport_day": 400
        },
        "bangalore": {
            "name": "Bangalore (Bengaluru)",
            "state": "Karnataka",
            "best_time": "Year-round (Best: Oct-Feb)",
            "attractions": ["Lalbagh Botanical Garden", "Cubbon Park & Vidhana Soudha", "Bangalore Palace", "Nandi Hills Sunrise Excursion", "Bannerghatta Biological Park"],
            "food": ["Masala Dosa (Vidyarthi Bhavan)", "Filter Coffee", "Indiranagar Craft Breweries"],
            "avg_stay_budget": 1600,
            "avg_stay_mid": 3800,
            "avg_food_day": 600,
            "local_transport_day": 450
        },
        "delhi": {
            "name": "New Delhi",
            "state": "Delhi NCR",
            "best_time": "October to March",
            "attractions": ["India Gate & Kartavya Path", "Red Fort & Chandni Chowk Food Walk", "Qutub Minar", "Humayun's Tomb", "Lotus Temple & Akshardham"],
            "food": ["Chole Bhature", "Paranthe Wali Gali", "Old Delhi Kebabs & Mughlai"],
            "avg_stay_budget": 1500,
            "avg_stay_mid": 3600,
            "avg_food_day": 600,
            "local_transport_day": 350
        },
        "vijayawada": {
            "name": "Vijayawada",
            "state": "Andhra Pradesh",
            "best_time": "October to March",
            "attractions": ["Kanaka Durga Temple atop Indrakeeladri", "Prakasam Barrage & Bhavani Island", "Undavalli Rock-Cut Caves", "Mangalagiri Temple & Handloom Sarees", "Kondapalli Fort & Wooden Toys"],
            "food": ["Andhra Thali with Gongura Pachadi", "Punugulu at Street Stalls", "Sweet Bandar Laddu"],
            "avg_stay_budget": 1200,
            "avg_stay_mid": 2800,
            "avg_food_day": 450,
            "local_transport_day": 300
        }
    }

    @classmethod
    def identify_destination(cls, query: str) -> Optional[str]:
        """Detects if query references a recognized travel destination."""
        q = query.lower()
        for dest_key in cls.DESTINATION_PROFILES:
            if dest_key in q:
                return dest_key
        # Check aliases
        if "srinagar" in q or "gulmarg" in q:
            return "kashmir"
        if "munnar" in q or "alleppey" in q or "kochi" in q:
            return "kerala"
        if "bengaluru" in q:
            return "bangalore"
        return None

    @classmethod
    def estimate_budget(
        cls,
        destination: str,
        days: int = 3,
        num_travelers: int = 1,
        tier: str = "budget",
        target_budget: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculates an approximate budget breakdown with practical expense tiers.
        """
        dest_key = destination.lower().strip()
        prof = cls.DESTINATION_PROFILES.get(dest_key, {
            "name": destination.title(),
            "avg_stay_budget": 1500,
            "avg_stay_mid": 3500,
            "avg_food_day": 600,
            "local_transport_day": 500
        })

        stay_rate = prof["avg_stay_budget"] if tier == "budget" else prof["avg_stay_mid"]
        # Double occupancy calculation for multiple travelers
        rooms = max(1, math.ceil(num_travelers / 2))
        total_stay = stay_rate * rooms * (days - 1 if days > 1 else 1)
        total_food = prof["avg_food_day"] * num_travelers * days
        total_transport = prof["local_transport_day"] * days + (800 * num_travelers)  # local + transit allowance
        total_sightseeing = 400 * num_travelers * days
        total_est = total_stay + total_food + total_transport + total_sightseeing

        # If user specified a budget constraint (e.g. within ₹8,000 or ₹15,000)
        is_constrained = False
        if target_budget and target_budget > 0:
            is_constrained = True
            if total_est > target_budget:
                # Scale gracefully to stay within budget
                ratio = target_budget / total_est
                total_stay = round(total_stay * ratio, -2)
                total_food = round(total_food * ratio, -2)
                total_transport = round(total_transport * ratio, -2)
                total_sightseeing = round(total_sightseeing * ratio, -2)
                total_est = target_budget

        return {
            "destination": prof["name"],
            "days": days,
            "travelers": num_travelers,
            "accommodation": round(total_stay),
            "food": round(total_food),
            "transport": round(total_transport),
            "sightseeing": round(total_sightseeing),
            "total_estimated": round(total_est),
            "is_constrained": is_constrained,
            "per_person": round(total_est / num_travelers) if num_travelers > 1 else round(total_est)
        }

    @classmethod
    def generate_concise_itinerary(
        cls,
        destination: str,
        days: int = 3,
        budget_str: str = "",
        lang: str = "en",
        target_budget: Optional[float] = None
    ) -> str:
        """
        Builds a crisp, day-wise travel plan with clear cost estimates.
        """
        dest_key = cls.identify_destination(destination) or destination.lower().strip()
        prof = cls.DESTINATION_PROFILES.get(dest_key)

        dest_name = prof["name"] if prof else destination.title()
        attractions = prof["attractions"] if prof else [
            f"Historic city center and landmarks of {dest_name}",
            f"Scenic viewpoints and cultural museum",
            f"Local market and street food exploration",
            f"Iconic regional architecture and nature parks"
        ]

        b_est = cls.estimate_budget(dest_name, days=days, target_budget=target_budget)

        # Build day-wise items
        day_items = []
        for d in range(1, days + 1):
            idx = (d - 1) % len(attractions)
            attr = attractions[idx]
            day_items.append(f"• **Day {d}:** {attr}")

        itinerary_body = "\n".join(day_items)

        budget_constraint_note = ""
        if target_budget:
            budget_constraint_note = f"\n• **Target Budget Limit:** ₹{int(target_budget):,} (Designed to stay within your cap)"

        if lang == "te":
            return (
                f"### 🌴 {days}-రోజుల {dest_name} ప్రయాణ ప్రణాళిక\n\n"
                f"{itinerary_body}\n\n"
                f"**అంచనా బడ్జెట్ (ఒక్కరికి):** సుమారు ₹{b_est['total_estimated']:,}\n"
                f"{budget_constraint_note}\n"
                f"• బస (Stay): ~₹{b_est['accommodation']:,}\n"
                f"• ఆహారం (Food): ~₹{b_est['food']:,}\n"
                f"• రవాణా (Transport): ~₹{b_est['transport']:,}\n"
                f"• దర్శనాలు (Sightseeing): ~₹{b_est['sightseeing']:,}\n\n"
                f"*(గమనిక: ఇది సుమారు అంచనా మాత్రమే; ఎంచుకునే హోటల్ మరియు ప్రయాణ సాధనాన్ని బట్టి మారుతుంది.)*"
            )
        elif lang == "hi":
            return (
                f"### 🌴 {days}-दिवसीय {dest_name} यात्रा योजना\n\n"
                f"{itinerary_body}\n\n"
                f"**अनुमानित बजट (प्रति व्यक्ति):** लगभग ₹{b_est['total_estimated']:,}\n"
                f"{budget_constraint_note}\n"
                f"• आवास (Stay): ~₹{b_est['accommodation']:,}\n"
                f"• भोजन (Food): ~₹{b_est['food']:,}\n"
                f"• स्थानीय परिवहन (Transport): ~₹{b_est['transport']:,}\n"
                f"• दर्शनीय स्थल (Sightseeing): ~₹{b_est['sightseeing']:,}\n\n"
                f"*(नोट: यह एक अनुमानित बजट है; मौसम और यात्रा श्रेणी के आधार पर परिवर्तन संभव है।)*"
            )

        # Default English
        return (
            f"### 🌴 {days}-Day Itinerary for {dest_name}\n\n"
            f"{itinerary_body}\n\n"
            f"**Estimated Budget (~₹{b_est['total_estimated']:,} per person):**{budget_constraint_note}\n"
            f"• **Stay:** ~₹{b_est['accommodation']:,} (budget guesthouses/homestays)\n"
            f"• **Food:** ~₹{b_est['food']:,} (local eateries)\n"
            f"• **Transport:** ~₹{b_est['transport']:,} (city transit/rentals)\n"
            f"• **Sightseeing:** ~₹{b_est['sightseeing']:,}\n\n"
            f"*(Estimates are approximate and vary based on season and booking time.)*"
        )


# =============================================================================
# 4. TRAVEL DURATION & DISTANCE CALCULATOR
# =============================================================================

class TravelDurationEstimator:
    """
    Computes realistic road distance, straight-line distance, driving time,
    train duration, and flight time between cities.
    """

    KNOWN_CITY_COORDINATES: Dict[str, Tuple[float, float]] = {
        "vijayawada": (16.5062, 80.6480),
        "hyderabad": (17.3850, 78.4867),
        "guntur": (16.3067, 80.4365),
        "tenali": (16.2430, 80.6400),
        "visakhapatnam": (17.6868, 83.2185),
        "vizag": (17.6868, 83.2185),
        "bangalore": (12.9716, 77.5946),
        "chennai": (13.0827, 80.2707),
        "goa": (15.2993, 74.1240),
        "delhi": (28.6139, 77.2090),
        "mumbai": (19.0760, 72.8777),
        "kolkata": (22.5726, 88.3639),
        "tirupati": (13.6288, 79.4192),
        "agra": (27.1767, 78.0081),
        "manali": (32.2432, 77.1892),
        "srinagar": (34.0837, 74.7973),
        "kashmir": (34.0837, 74.7973),
        "kochi": (9.9312, 76.2673),
        "kerala": (9.9312, 76.2673)
    }

    @classmethod
    def haversine_km(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance between two coordinate pairs."""
        r = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

    @classmethod
    def estimate_journey(cls, origin: str, dest: str, lang: str = "en") -> Optional[str]:
        """Calculates travel duration by car, bus, train, and flight between two cities."""
        orig_key = origin.lower().strip()
        dest_key = dest.lower().strip()

        c1 = cls.KNOWN_CITY_COORDINATES.get(orig_key)
        c2 = cls.KNOWN_CITY_COORDINATES.get(dest_key)

        if not c1 or not c2:
            return None

        straight_km = cls.haversine_km(c1[0], c1[1], c2[0], c2[1])
        # Winding factor for real road networks (typically 1.20 to 1.35x geodesic distance)
        road_km = round(straight_km * 1.25, 1)

        # Speeds: Car highway avg 65 km/h; Bus avg 50 km/h; Train avg 65 km/h; Flight avg 750 km/h + 2h airport buffer
        car_hours = road_km / 65.0
        bus_hours = road_km / 50.0
        train_hours = road_km / 65.0

        def fmt_time(h: float) -> str:
            hrs = int(h)
            mins = int((h - hrs) * 60)
            if hrs == 0:
                return f"{mins} mins"
            return f"{hrs} hrs {mins} mins" if mins > 0 else f"{hrs} hrs"

        if lang == "te":
            return (
                f"**{origin.title()} నుండి {dest.title()} ప్రయాణ వివరాలు:**\n\n"
                f"• **రోడ్డు దూరం:** ~{road_km} కి.మీ (నేరుగా దూరం: ~{round(straight_km)} కి.మీ)\n"
                f"• 🚗 **కారు డ్రైవింగ్:** సుమారు {fmt_time(car_hours)} (హైవే ట్రాఫిక్ బట్టి)\n"
                f"• 🚌 **ఆర్టీసీ / ప్రైవేట్ బస్సు:** సుమారు {fmt_time(bus_hours)}\n"
                f"• 🚆 **రైలు ప్రయాణం:** సుమారు {fmt_time(train_hours)}\n\n"
                f"*(గమనిక: రహదారి పనులు మరియు ట్రాఫిక్ బట్టి వాస్తవ సమయం మారవచ్చు.)*"
            )
        elif lang == "hi":
            return (
                f"**{origin.title()} से {dest.title()} यात्रा का समय और दूरी:**\n\n"
                f"• **सड़क दूरी:** ~{road_km} किमी (हवाई दूरी: ~{round(straight_km)} किमी)\n"
                f"• 🚗 **कार द्वारा:** लगभग {fmt_time(car_hours)}\n"
                f"• 🚌 **बस द्वारा:** लगभग {fmt_time(bus_hours)}\n"
                f"• 🚆 **ट्रेन द्वारा:** लगभग {fmt_time(train_hours)}\n\n"
                f"*(नोट: यह अनुमानित समय है; सड़क की स्थिति के अनुसार बदलाव संभव है।)*"
            )

        return (
            f"**Travel Distance & Duration: {origin.title()} → {dest.title()}**\n\n"
            f"• **Road Distance:** ~{road_km} km (Straight-line: ~{round(straight_km)} km)\n"
            f"• 🚗 **By Car:** ~{fmt_time(car_hours)} via major highway corridors\n"
            f"• 🚌 **By Bus:** ~{fmt_time(bus_hours)}\n"
            f"• 🚆 **By Train:** ~{fmt_time(train_hours)}\n\n"
            f"*(Estimates reflect standard highway traffic conditions.)*"
        )


# =============================================================================
# 5. LANGUAGE RESOLVER & MULTILINGUAL ADAPTATION
# =============================================================================

def resolve_target_language(raw_query: str, app_lang: str = "en") -> str:
    """
    Determines response language following the required priority:
    1. Explicit language requested in the message (e.g., "answer in Telugu", "తెలుగులో చెప్పండి", "in Hindi").
    2. Selected application language (st.session_state.app_language).
    3. User preference / fallback.
    4. English as default.
    """
    q = (raw_query or "").lower().strip()

    # 1. Explicit request in message
    if any(p in q for p in ["in english", "answer in english", "english lo", "angrezi me", "speak in english"]):
        return "en"
    if any(p in q for p in ["in telugu", "answer in telugu", "telugu lo", "తెలుగులో", "తెలుగు", "telugulo"]):
        return "te"
    if any(p in q for p in ["in hindi", "answer in hindi", "hindi me", "हिंदी में", "हिन्दी में", "hindi mein"]):
        return "hi"
    if any(p in q for p in ["in tamil", "answer in tamil", "tamilil", "தமிழில்"]):
        return "ta"
    if any(p in q for p in ["in kannada", "answer in kannada", "kannadadalli", "ಕನ್ನಡದಲ್ಲಿ"]):
        return "kn"
    if any(p in q for p in ["in malayalam", "answer in malayalam", "malayalamil", "മലയാളത്തിൽ"]):
        return "ml"
    if any(p in q for p in ["in bengali", "answer in bengali", "banglay", "বাংলায়"]):
        return "bn"
    if any(p in q for p in ["in marathi", "answer in marathi", "marathit", "मराठीत"]):
        return "mr"

    # Script-based detection
    if bool(re.search(r"[\u0c00-\u0c7f]", raw_query)):
        return "te"
    if bool(re.search(r"[\u0900-\u097f]", raw_query)):
        return "hi"
    if bool(re.search(r"[\u0b80-\u0bff]", raw_query)):
        return "ta"
    if bool(re.search(r"[\u0c80-\u0cff]", raw_query)):
        return "kn"
    if bool(re.search(r"[\u0d00-\u0d7f]", raw_query)):
        return "ml"
    if bool(re.search(r"[\u0980-\u09ff]", raw_query)):
        return "bn"

    # 2. Application language selection
    app_l = (app_lang or "en").lower().strip()
    if app_l in ("te", "hi", "ta", "kn", "ml", "bn", "mr", "en"):
        return app_l

    return "en"


# =============================================================================
# 6. GENERAL TRAVEL QA ENGINE (CONCISE & ACCURATE)
# =============================================================================

class GeneralTravelQAEngine:
    """
    Answers common travel planning, packing, budgeting, transportation comparison,
    and general knowledge questions with short, simple, and practical responses.
    """

    @classmethod
    def answer_travel_question(cls, query: str, lang: str = "en") -> Optional[Dict[str, Any]]:
        q = (query or "").lower().strip()

        # 1. Documents for International Travel
        if any(w in q for w in ["document", "documents", "passport", "visa", "international travel"]) and any(w in q for w in ["require", "need", "what documents", "papers"]):
            if lang == "te":
                msg = (
                    "**అంతర్జాతీయ ప్రయాణానికి అవసరమైన పత్రాలు:**\n"
                    "1. కనీసం 6 నెలల చెల్లుబాటు ఉన్న **పాస్‌పోర్ట్**.\n"
                    "2. గమ్యస్థాన దేశపు **వీసా (Visa)** లేదా eVisa ప్రింట్.\n"
                    "3. రానుపోను **రిటర్న్ విమాన టికెట్లు** & హోటల్ బుకింగ్ రుజువులు.\n"
                    "4. సరిపడా నిధుల రుజువు (బ్యాంక్ స్టేట్‌మెంట్ / ఇంటర్నేషనల్ కార్డ్).\n"
                    "5. ట్రావెల్ ఇన్సూరెన్స్ (వైద్య కవరేజీ కొరకు)."
                )
            elif lang == "hi":
                msg = (
                    "**अंतरराष्ट्रीय यात्रा के लिए आवश्यक दस्तावेज़:**\n"
                    "1. कम से कम 6 महीने की वैधता वाला **पासपोर्ट**।\n"
                    "2. गंतव्य देश का **वीज़ा (Visa)** या eVisa।\n"
                    "3. वापसी की **कन्फर्म फ्लाइट टिकट** और होटल बुकिंग।\n"
                    "4. वित्तीय प्रमाण (बैंक स्टेटमेंट / इंटरनेशनल फॉरेक्स कार्ड)।\n"
                    "5. यात्रा बीमा (Travel Insurance)।"
                )
            else:
                msg = (
                    "**Essential Documents for International Travel:**\n"
                    "1. **Passport:** Valid for at least 6 months beyond travel dates.\n"
                    "2. **Visa / eVisa:** Approved visa or ETA for your destination.\n"
                    "3. **Return Tickets:** Confirmed onward/return flight itinerary.\n"
                    "4. **Accommodation Proof:** Hotel reservations or invitation letter.\n"
                    "5. **Travel Insurance & Forex:** For emergency medical care and local expenses."
                )
            return {"badge": "🛂 AURA • TRAVEL DOCUMENTS", "response": msg}

        # 2. How to Save Money While Travelling
        if any(w in q for w in ["save money", "cheaper travel", "budget travel", "how to save"]) and any(w in q for w in ["travel", "trip", "tour"]):
            if lang == "te":
                msg = (
                    "**ప్రయాణంలో ఖర్చులు తగ్గించుకోవడానికి సులభమైన మార్గాలు:**\n"
                    "1. పీక్ సీజన్‌కు బదులుగా షోల్డర్ సీజన్ (సీజన్ ప్రారంభం/ముగింపు) లో ప్రయాణించండి.\n"
                    "2. క్యాబ్‌లకు బదులు మెట్రో, లోకల్ బస్సులు లేదా రైళ్లను వాడండి.\n"
                    "3. ఖరీదైన హోటళ్ల కంటే హోమ్‌స్టేలు లేదా హాస్టల్స్‌ను ఎంచుకోండి.\n"
                    "4. స్థానిక మార్కెట్లలో భోజనం చేయడం ద్వారా 40% ఖర్చు ఆదా అవుతుంది."
                )
            elif lang == "hi":
                msg = (
                    "**यात्रा में पैसे बचाने के आसान तरीके:**\n"
                    "1. पीक सीजन की बजाय ऑफ-सीजन या शोल्डर सीजन में घूमें।\n"
                    "2. टैक्सियों की जगह मेट्रो, बस या लोकल ट्रेनों का उपयोग करें।\n"
                    "3. महंगे होटलों की जगह हॉस्टल या होमस्टे में रुकें।\n"
                    "4. स्थानीय ढाबों और स्ट्रीट फूड का आनंद लें, जिससे बजट 40% तक घट जाता है।"
                )
            else:
                msg = (
                    "**Top Tips to Save Money Traveling:**\n"
                    "1. **Shoulder Season:** Travel just before or after peak season for 30–50% cheaper stays.\n"
                    "2. **Public Transit & Transport:** Use trains, metros, and local buses instead of private cabs.\n"
                    "3. **Stay Smart:** Book guesthouses, homestays, or hostels with kitchen facilities.\n"
                    "4. **Eat Local:** Dine at local markets and family eateries rather than tourist cafes.\n"
                    "5. **Book in Advance:** Reserve flights and long-distance transport in advance to lock in lower fares."
                )
            return {"badge": "💰 AURA • MONEY SAVING", "response": msg}

        # 3. Train vs Bus Comparison
        if ("train" in q and "bus" in q) and any(w in q for w in ["better", "compare", "which is", "prefer"]):
            if lang == "te":
                msg = (
                    "**రైలు vs బస్సు పోలిక:**\n"
                    "• **రైలు (Train):** 300 కి.మీ పైబడిన దూర ప్రయాణాలకు, రాత్రిపూట ప్రయాణాలకు అత్యంత సౌకర్యవంతమైనది, చౌకైనది.\n"
                    "• **బస్సు (Bus):** కొండ ప్రాంతాలకు (ఉదా: ఊటీ, మనాలి) లేదా చివరి నిమిషంలో టికెట్లు అవసరమైనప్పుడు బస్సు ఉత్తమం.\n"
                    "**సిఫార్సు:** దూర ప్రయాణాలకు మరియు బడ్జెట్ పొదుపుకు రైలు ఉత్తమ ఎంపిక."
                )
            elif lang == "hi":
                msg = (
                    "**ट्रेन बनाम बस:**\n"
                    "• **ट्रेन:** लंबी दूरी (300+ किमी) और रात की यात्रा के लिए सबसे आरामदायक और सस्ती होती है।\n"
                    "• **बस:** पहाड़ी रास्तों (जैसे मनाली, ऊटी) और अंतिम समय में तत्काल यात्रा के लिए उपयोगी है।\n"
                    "**सुझाव:** आराम और कम बजट के लिए ट्रेन सबसे बेहतर विकल्प है।"
                )
            else:
                msg = (
                    "**Train vs. Bus Comparison:**\n"
                    "• **Train:** Best for long distances (300+ km) and overnight journeys. More spacious, economical, and comfortable.\n"
                    "• **Bus:** Better for hill stations without rail heads (e.g. Manali, Munnar) and flexible last-minute bookings.\n"
                    "**Verdict:** Choose train for comfort & budget; choose bus for direct mountain corridor access."
                )
            return {"badge": "🚆 AURA • TRANSIT COMPARISON", "response": msg}

        # 4. Car vs Train Cost Comparison
        if ("car" in q and "train" in q) and any(w in q for w in ["cheap", "cheaper", "cost", "better"]):
            if lang == "te":
                msg = (
                    "**కారు vs రైలు ఖర్చు పోలిక:**\n"
                    "• 1 లేదా 2 వ్యక్తులు ప్రయాణిస్తే **రైలు చాలా చౌకైనది** (ఇంధనం, టోల్ ఖర్చులు ఉండవు).\n"
                    "• 4–5 మంది కుటుంబ సభ్యులు కలిసి ప్రయాణిస్తే, ఒక్కొక్కరికి అయ్యే ఖర్చును బట్టి **కారు ప్రయాణం సౌకర్యవంతంగా, సమాన ఖర్చుతో కూడినదిగా** ఉంటుంది."
                )
            else:
                msg = (
                    "**Is it cheaper by Car or Train?**\n"
                    "• **Solo or Duo (1–2 people):** **Train is significantly cheaper** (no fuel or highway toll costs).\n"
                    "• **Small Family / Group (3–4 people):** **Car becomes cost-effective**, offering door-to-door flexibility and shared fuel expenses."
                )
            return {"badge": "⚖️ AURA • COST COMPARISON", "response": msg}

        # 5. Best Transportation Mode for Short Trips
        if any(w in q for w in ["short trip", "short distance"]) and any(w in q for w in ["mode", "transport", "better", "best"]):
            if lang == "te":
                msg = "స్వల్ప దూర ప్రయాణాలకు (100–250 కి.మీ) **సొంత కారు లేదా బైక్** అత్యంత అనువైనది. ఇది ప్రయాణంలో స్వేచ్ఛను, గమ్యాన్ని త్వరగా చేరుకోవడానికి సహాయపడుతుంది."
            else:
                msg = "For short trips (100–250 km), a **personal car, rental car, or two-wheeler** is best. It offers flexible departure timing and seamless exploration without station transit delays."
            return {"badge": "🚗 AURA • SHORT TRIPS", "response": msg}

        # 6. Best Time to Visit Kashmir
        if "kashmir" in q and any(w in q for w in ["best time", "when to visit", "season"]):
            if lang == "te":
                msg = (
                    "**కాశ్మీర్ సందర్శించడానికి ఉత్తమ సమయం:**\n"
                    "• **వసంతం & వేసవి (ఏప్రిల్ – జూన్):** ఆహ్లాదకరమైన వాతావరణం, పూలతో నిండిన తులిప్ గార్డెన్లు.\n"
                    "• **శీతాకాలం (డిసెంబర్ – ఫిబ్రవరి):** గుల్‌మార్గ్‌లో మంచు కురిసే అందాలు మరియు స్కీయింగ్ కొరకు."
                )
            else:
                msg = (
                    "**Best Time to Visit Kashmir:**\n"
                    "• **April to June (Spring/Summer):** Pleasant weather (15°C–25°C), blooming tulip gardens, and green valleys.\n"
                    "• **December to February (Winter):** For fresh snowfall, frozen Dal Lake views, and skiing in Gulmarg."
                )
            return {"badge": "❄️ AURA • KASHMIR SEASON", "response": msg}

        # 7. Taj Mahal Duration
        if "taj mahal" in q and any(w in q for w in ["how long", "time", "hours", "spend"]):
            if lang == "te":
                msg = "తాజ్ మహల్ సందర్శించడానికి **2 నుండి 3 గంటల సమయం** సరిపోతుంది. సూర్యోదయం (Sunrise) సమయంలో సందర్శిస్తే రద్దీ తక్కువగా ఉండి అద్భుతమైన ఫోటోలు తీసుకోవచ్చు."
            else:
                msg = "Plan to spend **2 to 3 hours** at the Taj Mahal. Visiting at sunrise is recommended to beat the crowds, avoid midday heat, and experience the best lighting on the white marble."
            return {"badge": "🏛️ AURA • TAJ MAHAL", "response": msg}

        # 8. How Many Days for Kerala
        if "kerala" in q and any(w in q for w in ["how many days", "days enough", "duration"]):
            if lang == "te":
                msg = "కేరళ సందర్శించడానికి **5 నుండి 7 రోజులు** సరిపోతాయి. మున్నార్ (టీ గార్డెన్స్ - 2 రోజులు), అలెప్పీ (హౌస్‌బోట్ - 1 రోజు), కొచ్చి (హెరిటేజ్ - 1 రోజు), మరియు వర్కల బీచ్ (1-2 రోజులు) చూసుకోవచ్చు."
            else:
                msg = "**5 to 7 days** are ideal for a fulfilling Kerala trip. Recommended split: 2 days in Munnar (tea hills), 1 day in Alleppey (backwater houseboat), 1 day in Fort Kochi, and 2 days in Varkala or Thekkady."
            return {"badge": "🌴 AURA • KERALA DURATION", "response": msg}

        # 9. Weekend Trip from Vijayawada
        if "vijayawada" in q and any(w in q for w in ["weekend", "short trip", "trip from"]):
            if lang == "te":
                msg = (
                    "**విజయవాడ నుండి ఉత్తమ వీకెండ్ ట్రిప్పులు:**\n"
                    "1. **సూర్యలంక / బాపట్ల బీచ్:** ~90 కి.మీ (2 గంటలు) - సముద్ర తీరంలో విశ్రాంతి.\n"
                    "2. **అమరావతి బౌద్ధ స్తూపం & ధ్యాన బుద్ధ:** ~45 కి.మీ (1 గంట).\n"
                    "3. **హైదరాబాద్ సిటీ ట్రిప్:** ~275 కి.మీ (NH65 ద్వారా 4 గంటలు).\n"
                    "4. **పాపికొండలు & రాజమండ్రి:** ~160 కి.మీ (గోదావరి బోటింగ్)."
                )
            else:
                msg = (
                    "**Best Weekend Getaways from Vijayawada:**\n"
                    "1. **Suryalanka Beach (Bapatla):** ~90 km (2 hrs drive) for beachside relaxation.\n"
                    "2. **Amaravati Heritage & Dhyana Buddha:** ~45 km (1 hr) for ancient Buddhist history.\n"
                    "3. **Hyderabad Heritage Road Trip:** ~275 km (4 hrs via NH65 express corridor).\n"
                    "4. **Maredumilli & Papikondalu:** ~220 km for lush jungle eco-tourism and river cruises."
                )
            return {"badge": "🚗 AURA • WEEKEND GETAWAYS", "response": msg}

        # 10. Low-Budget International Travel Plan
        if any(w in q for w in ["international", "foreign"]) and any(w in q for w in ["low budget", "cheap", "within", "under"]):
            if lang == "te":
                msg = (
                    "**తక్కువ బడ్జెట్ అంతర్జాతీయ పర్యటనలు (భారత్ నుండి):**\n"
                    "1. **నేపాల్ (Nepal):** భారతీయులకు వీసా అవసరం లేదు. ₹25,000–₹35,000 లో కాట్మండు, పోఖరా చూడవచ్చు.\n"
                    "2. **థాయిలాండ్ (Thailand):** ఉచిత వీసా సదుపాయం. 5 రోజుల ట్రిప్‌కు సుమారు ₹40,000–₹50,000 (విమానంతో సహా).\n"
                    "3. **వియత్నాం (Vietnam):** చౌకైన వసతి, ఆహారం. సుమారు ₹45,000–₹55,000 ఖర్చు అవుతుంది."
                )
            else:
                msg = (
                    "**Top Low-Budget International Destinations from India:**\n"
                    "1. **Nepal:** No visa needed for Indian citizens. Budget: ~₹25,000–₹35,000 for 5 days (Kathmandu & Pokhara).\n"
                    "2. **Vietnam:** Super-affordable local food and stays. Budget: ~₹45,000–₹55,000 for 5–6 days including flights.\n"
                    "3. **Thailand:** Visa-exemption often available. Budget: ~₹40,000–₹50,000 for Bangkok & Pattaya."
                )
            return {"badge": "✈️ AURA • BUDGET INTERNATIONAL", "response": msg}

        # 11. Family Trip Budget Estimation
        if any(w in q for w in ["family trip", "family"]) and any(w in q for w in ["how much", "budget", "money"]):
            if lang == "te":
                msg = (
                    "**4 మంది సభ్యుల కుటుంబ ప్రయాణ బడ్జెట్ మార్గదర్శకాలు (3-రోజులు):**\n"
                    "• **హోటల్ (2 గదులు):** సుమారు ₹3,500 - ₹5,000/రోజు → ~₹8,000\n"
                    "• **ఆహారం:** సుమారు ₹2,000/రోజు → ~₹6,000\n"
                    "• **రవాణా (కారు/ఇంధనం/టోల్):** సుమారు ₹5,000 - ₹7,000\n"
                    "• **దర్శనాలు & ఇతరాలు:** సుమారు ₹3,000\n"
                    "**మొత్తం బడ్జెట్:** సుమారు **₹22,000 – ₹25,000**."
                )
            else:
                msg = (
                    "**Estimated Budget for a Family of 4 (3-Day Domestic Trip):**\n"
                    "• **Stay (2 Rooms / Family Suite):** ~₹3,500/night × 2 nights = ~₹7,000\n"
                    "• **Food & Dining:** ~₹2,000/day × 3 days = ~₹6,000\n"
                    "• **Transport (Fuel/Tolls or Train):** ~₹6,000\n"
                    "• **Sightseeing & Activities:** ~₹3,000\n"
                    "**Approximate Total:** **₹22,000 – ₹25,000** (~₹5,500–₹6,200 per person)."
                )
            return {"badge": "👨‍👩‍👧‍👦 AURA • FAMILY BUDGET", "response": msg}

        return None

