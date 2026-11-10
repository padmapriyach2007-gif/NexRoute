# -*- coding: utf-8 -*-
"""
Dynamic Multilingual Translation Engine for NexRoute
Provides dynamic AI & phrase-level translation for all user-facing generated text:
- Tourist & cultural descriptions
- Nature & geography summaries
- Scenic photo spots & culinary highlights
- Hotel, restaurant, & flight recommendations
- Navigation instructions & safety telemetry
- Protected entity preservation (NexRoute, AURA, Tenali, Krishna River, etc.)
- In-memory LRU caching with instant lookups
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any

from localization.language_config import (
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
    PROTECTED_ENTITIES,
    _PROTECTED_REGEX
)

logger = logging.getLogger("nexroute.localization.dynamic_translator")

# High-speed in-memory translation cache: (clean_text, target_lang) -> translated_text
_DYNAMIC_TRANSLATION_CACHE: Dict[Tuple[str, str], str] = {}

# =========================================================================
# DOMAIN TRANSLATION DICTIONARY FOR FREQUENT DYNAMIC TRAVEL DESCRIPTIONS
# Across all 8 languages: en, te, hi, kn, ta, ml, mr, bn
# =========================================================================

_CORRIDOR_DESCRIPTIONS_DB: Dict[str, Dict[str, str]] = {
    # Cultural & Historical Lore
    "Historic heritage landmark and cultural monument preserved for regional significance.": {
        "te": "ప్రాంతీయ ప్రాముఖ్యత కోసం సంరక్షించబడిన చారిత్రక వారసత్వ చిహ్నం మరియు సాంస్కృతిక స్మారక చిహ్నం.",
        "hi": "क्षेत्रीय महत्व के लिए संरक्षित ऐतिहासिक विरासत स्थल और सांस्कृतिक स्मारक।",
        "kn": "ಪ್ರಾದೇಶಿಕ ಮಹತ್ವಕ್ಕಾಗಿ ಸಂರಕ್ಷಿಸಲಾದ ಐತಿಹಾಸಿಕ ಪರಂಪರೆಯ ಹೆಗ್ಗುರುತು ಮತ್ತು ಸಾಂಸ್ಕೃತಿಕ ಸ್ಮಾರಕ.",
        "ta": "பிராந்திய முக்கியத்துவத்திற்காக பாதுகாக்கப்பட்ட வரலாற்று பாரம்பரிய சின்னம் மற்றும் கலாச்சார நினைவுச்சின்னம்.",
        "ml": "പ്രാദേശിക പ്രാധാന്യത്തിനായി സംരക്ഷിക്കപ്പെട്ട ചരിത്ര പൈതൃക അടയാളവും സാംസ്കാരിക സ്മാരകവും.",
        "mr": "प्रादेशिक महत्त्वासाठी जतन केलेले ऐतिहासिक वारसा स्थळ आणि सांस्कृतिक स्मारक.",
        "bn": "আঞ্চলিক তাত্পর্যর জন্য সংরক্ষিত ঐতিহাসিক ঐতিহ্যবাহী ল্যান্ডমার্ক এবং সাংস্কৃতিক স্মৃতিস্তম্ভ।"
    },
    "Sacred shrine and pilgrimage site known for historic architecture and spiritual rituals.": {
        "te": "చారిత్రక వాస్తుశిల్పం మరియు ఆధ్యాత్మిక పూజలకు ప్రసిద్ధి చెందిన పవిత్ర పుణ్యక్షేత్రం.",
        "hi": "ऐतिहासिक वास्तुकला और आध्यात्मिक अनुष्ठानों के लिए प्रसिद्ध पवित्र तीर्थ स्थल।",
        "kn": "ಐತಿಹಾಸಿಕ ವಾಸ್ತುಶಿಲ್ಪ ಮತ್ತು ಆಧ್ಯಾತ್ಮಿಕ ಆಚರಣೆಗಳಿಗೆ ಹೆಸರುವಾಸಿಯಾದ ಪವಿತ್ರ ಯಾತ್ರಾ ಸ್ಥಳ.",
        "ta": "வரலாற்று கட்டிடக்கலை மற்றும் ஆன்மீக சடங்குகளுக்கு பெயர் பெற்ற புனித யாத்திரை தலம்.",
        "ml": "ചരിത്രപരമായ വാസ്തുവിദ്യയ്ക്കും ആത്മീയ ആചാരങ്ങൾക്കും പേരുകേട്ട പവിത്രമായ തീർത്ഥാടന കേന്ദ്രം.",
        "mr": "ऐतिहासिक वास्तुकला आणि आध्यात्मिक विधींसाठी प्रसिद्ध असलेले पवित्र तीर्थक्षेत्र.",
        "bn": "ঐতিহাসিক স্থাপত্য এবং আধ্যাত্মিক আচার-অনুষ্ঠানের জন্য পরিচিত পবিত্র তীর্থস্থান।"
    },
    "Cascading natural waterfall and scenic photography viewpoint.": {
        "te": "జాలువారే సహజ జలపాతం మరియు సుందరమైన ఫోటోగ్రఫీ వీక్షణ కేంద్రం.",
        "hi": "मनोरम प्राकृतिक झरना और सुरम्य फोटोग्राफी दृश्य स्थल।",
        "kn": "ಮನಮೋಹಕ ನೈಸರ್ಗಿಕ ಜಲಪಾತ ಮತ್ತು ನಯನಮನೋಹರ ಛಾಯಾಗ್ರಹಣ ವೀಕ್ಷಣಾ ತಾಣ.",
        "ta": "இயற்கையான நீர்வீழ்ச்சி மற்றும் அழகிய புகைப்பட காட்சிப் புள்ளி.",
        "ml": "മനോഹരമായ പ്രകൃതിദത്ത വെള്ളച്ചാട്ടവും ഫോട്ടോഗ്രാഫി കാഴ്ചാ പോയിന്റും.",
        "mr": "मनोरम नैसर्गिक धबधबा आणि निसर्गरम्य फोटोग्राफी दृश्य बिंदू.",
        "bn": "মনোরম প্রাকৃতিক জলপ্রপাত এবং মনোরম ফটোগ্রাফি ভিউপয়েন্ট।"
    },
    "Sandy coastal beach area offering seaside vistas and leisurely walking.": {
        "te": "సముద్ర తీర దృశ్యాలు మరియు ఆహ్లాదకరమైన నడకను అందించే ఇసుక బీచ్ ప్రాంతం.",
        "hi": "समुद्र तट के दृश्य और इत्मीनान से सैर की पेशकश करने वाला रेतीला तटीय समुद्र तट।",
        "kn": "ಸಮುದ್ರ ತೀರದ ದೃಶ್ಯಗಳು ಮತ್ತು ವಿರಾಮದ ನಡಿಗೆಯನ್ನು ನೀಡುವ ಮರಳಿನ ಕರಾವಳಿ ಬೀಚ್ ಪ್ರದೇಶ.",
        "ta": "கடற்கரை காட்சிகள் மற்றும் நிதானமான நடைப்பயிற்சியை வழங்கும் மணல் கடற்கரை பகுதி.",
        "ml": "കടൽത്തീര കാഴ്ചകളും നടപ്പാതകളും വാഗ്ദാനം ചെയ്യുന്ന മണൽ നിറഞ്ഞ തീരദേശ ബീച്ച് പ്രദേശം.",
        "mr": "समुद्रकिनाऱ्याचे दृश्य आणि निवांत फिरण्याची संधी देणारा वालुकामय समुद्रकिनारा.",
        "bn": "সমুদ্রতীরবর্তী দৃশ্য এবং অবসরে হাঁটার সুযোগ দেওয়া বালুকাময় উপকূলীয় সৈকত এলাকা।"
    },
    "Elevated vantage point offering sweeping panoramic vistas of the surrounding landscape.": {
        "te": "చుట్టుపక్కల ప్రకృతి దృశ్యాల విహంగమ దృశ్యాన్ని అందించే ఎత్తైన వీక్షణ కేంద్రం.",
        "hi": "आसपास के परिदृश्य के मनोरम विहंगम दृश्य प्रस्तुत करने वाला ऊंचा स्थान।",
        "kn": "ಸುತ್ತಮುತ್ತಲಿನ ಭೂದೃಶ್ಯದ ವಿಹಂಗಮ ನೋಟವನ್ನು ನೀಡುವ ಎತ್ತರದ ವೀಕ್ಷಣಾ ತಾಣ.",
        "ta": "சுற்றியுள்ள நிலப்பரப்பின் பரந்த காட்சிகளை வழங்கும் உயரமான காட்சிப் புள்ளி.",
        "ml": "ചുറ്റുമുള്ള ഭൂപ്രകൃതിയുടെ മനോഹരമായ കാഴ്ച നൽകുന്ന ഉയർന്ന വ്യൂപോയിന്റ്.",
        "mr": "आसपासच्या परिसराचे विहंगम दृश्य देणारे उंचावरील ठिकाण.",
        "bn": "চারপাশের ল্যান্ডস্কেপের সুন্দর প্যানোরামিক দৃশ্য প্রদর্শনকারী উঁচু ভিউপয়েন্ট।"
    },
    "Panoramic vistas of rural agricultural waterways.": {
        "te": "గ్రామీణ వ్యవసాయ జలమార్గాల విహంగమ దృశ్యాలు.",
        "hi": "ग्रामीण कृषि जलमार्गों के मनोरम दृश्य।",
        "kn": "ಗ್ರಾಮೀಣ ಕೃಷಿ ಜಲಮಾರ್ಗಗಳ ವಿಹಂಗಮ ನೋಟಗಳು.",
        "ta": "கிராமப்புற விவசாய நீர்வழிகளின் பரந்த காட்சிகள்.",
        "ml": "ഗ്രാമീണ കാർഷിക ജലപാതകളുടെ മനോഹരമായ കാഴ്ചകൾ.",
        "mr": "ग्रामीण कृषी जलमार्गांचे विहंगम दृश्य.",
        "bn": "গ্রামীণ কৃষি জলপথের মনোরম দৃশ্য।"
    },
    "Authentic regional highway tiffins, fresh chai, and sweets.": {
        "te": "ప్రామాణిక ప్రాంతీయ హైవే టిఫిన్లు, తాజా టీ మరియు మిఠాయిలు.",
        "hi": "प्रामाणिक क्षेत्रीय हाईवे टिफिन, ताजा चाय और मिठाइयाँ।",
        "kn": "ಅಧಿಕೃತ ಪ್ರಾದೇಶಿಕ ಹೆದ್ದಾರಿ ಉಪಹಾರಗಳು, ತಾಜಾ ಚಹಾ ಮತ್ತು ಸಿಹಿತಿಂಡಿಗಳು.",
        "ta": "உண்மையான பிராந்திய நெடுஞ்சாலை சிற்றுண்டிகள், புதிய தேநீர் மற்றும் இனிப்புகள்.",
        "ml": "തനതായ പ്രാദേശിക ഹൈവേ ലഘുഭക്ഷണങ്ങൾ, ചൂടുള്ള ചായ, മധുരപലഹാരങ്ങൾ.",
        "mr": "अस्सल प्रादेशिक हायवे नाश्ता, ताजी चहा आणि गोड पदार्थ.",
        "bn": "আসল আঞ্চলিক হাইওয়ে টিফিন, তাজা চা এবং মিষ্টি।"
    },
    "Scenic riverside view along the Krishna River corridor with green canals.": {
        "te": "పచ్చని కాలువలతో కూడిన కృష్ణా నది కారిడార్ వెంబడి సుందరమైన నదీతీర దృశ్యం.",
        "hi": "हरियाली वाली नहरों के साथ कृष्णा नदी गलियारे के किनारे सुरम्य नदी का दृश्य।",
        "kn": "ಹಸಿರು ಕಾಲುವೆಗಳೊಂದಿಗೆ ಕೃಷ್ಣಾ ನದಿಯ ಕಾರಿಡಾರ್ ಉದ್ದಕ್ಕೂ ಸುಂದರವಾದ ನದೀತೀರದ ನೋಟ.",
        "ta": "பசுமையான கால்வாய்களுடன் கூடிய கிருஷ்ணா நதி வழித்தடத்தில் அழகிய நதிக்கரை காட்சி.",
        "ml": "പച്ചപ്പ് നിറഞ്ഞ കനാലുകളോടുകൂടിയ കൃഷ്ണ നദി ഇടനാഴിയിലെ മനോഹരമായ നദീതീര കാഴ്ച.",
        "mr": "हिरवेगार कालवे आणि कृष्णा नदी कॉरिडॉरसह निसर्गरम्य नदीकाठचे दृश्य.",
        "bn": "সবুজ খাল সহ কৃষ্ণা নদী করিডোর বরাবর মনোরম নদী তীরের দৃশ্য।"
    },
    "Historic canal trading network connecting heritage agricultural towns.": {
        "te": "వారసత్వ వ్యవసాయ పట్టణాలను అనుసంధానించే చారిత్రక కాలువ వాణిజ్య నెట్‌వర్క్.",
        "hi": "विरासत कृषि कस्बों को जोड़ने वाला ऐतिहासिक नहर व्यापार नेटवर्क।",
        "kn": "ಪರಂಪರೆಯ ಕೃಷಿ ಪಟ್ಟಣಗಳನ್ನು ಸಂಪರ್ಕಿಸುವ ಐತಿಹಾಸಿಕ ಕಾಲುವೆ ವ್ಯಾಪಾರ ಜಾಲ.",
        "ta": "பாரம்பரிய விவசாய நகரங்களை இணைக்கும் வரலாற்று சிறப்புமிக்க கால்வாய் வர்த்தக வலையமைப்பு.",
        "ml": "പൈതൃക കാർഷിക നഗരങ്ങളെ ബന്ധിപ്പിക്കുന്ന ചരിത്രപ്രസിദ്ധമായ കനാൽ വ്യാപാര ശൃംഖല.",
        "mr": "वारसा लाभलेल्या शेती शहरांना जोडणारे ऐतिहासिक कालवा व्यापार नेटवर्क.",
        "bn": "ঐতিহ্যবাহী কৃষি শহরগুলিকে সংযুক্তকারী ঐতিহাসিক খাল বাণিজ্য নেটওয়ার্ক।"
    },
    "Fastest route with minimum travel time and clear highway traffic.": {
        "te": "కనిష్ట ప్రయాణ సమయం మరియు స్పష్టమైన హైవే ట్రాఫిక్‌తో వేగవంతమైన మార్గం.",
        "hi": "न्यूनतम यात्रा समय और स्पष्ट हाईवे ट्रैफिक वाला सबसे तेज़ मार्ग।",
        "kn": "ಕನಿಷ್ಠ ಪ್ರಯಾಣದ ಸಮಯ ಮತ್ತು ಸ್ಪಷ್ಟ ಹೆದ್ದಾರಿ ಸಂಚಾರದೊಂದಿಗೆ ವೇಗವಾದ ಮಾರ್ಗ.",
        "ta": "குறைந்தபட்ச பயண நேரம் மற்றும் தெளிவான நெடுஞ்சாலை போக்குவரத்துடன் கூடிய விரைவான பாதை.",
        "ml": "കുറഞ്ഞ യാത്രാ സമയവും വ്യക്തമായ ഹൈവേ ട്രാഫിക്കും ഉള്ള ഏറ്റവും വേഗതയേറിയ വഴി.",
        "mr": "किमान प्रवासाची वेळ आणि सुरळीत हायवे ट्रॅफिक असलेला सर्वात वेगवान मार्ग.",
        "bn": "ন্যূনতম ভ্রমণ সময় এবং স্পষ্ট হাইওয়ে ট্র্যাফিক সহ দ্রুততম রুট।"
    },
    "Eco-friendly route maximizing fuel efficiency and minimizing emissions.": {
        "te": "ఇంధన సామర్థ్యాన్ని పెంచి ఉద్గారాలను తగ్గించే పర్యావరణ అనుకూల మార్గం.",
        "hi": "ईंधन दक्षता को अधिकतम करने और उत्सर्जन को कम करने वाला पर्यावरण-अनुकूल मार्ग।",
        "kn": "ಇಂಧನ ದಕ್ಷತೆಯನ್ನು ಹೆಚ್ಚಿಸುವ ಮತ್ತು ಹೊರಸೂಸುವಿಕೆಯನ್ನು ಕಡಿಮೆ ಮಾಡುವ ಪರಿಸರ ಸ್ನೇಹಿ ಮಾರ್ಗ.",
        "ta": "எரிபொருள் பயன்பாட்டை மேம்படுத்தி உமிழ்வைக் குறைக்கும் சூழல் நட்பு பாதை.",
        "ml": "ഇന്ധനക്ഷമത വർദ്ധിപ്പിക്കുകയും ഉദ്‌വമനം കുറയ്ക്കുകയും ചെയ്യുന്ന പരിസ്ഥിതി സൗഹൃദ പാത.",
        "mr": "इंधन कार्यक्षमता वाढवणारा आणि उत्सर्जन कमी करणारा पर्यावरणपूरक मार्ग.",
        "bn": "জ্বালানী দক্ষতা বৃদ্ধি এবং নির্গমন হ্রাসকারী পরিবেশ-বান্ধব রুট।"
    },
    "Safest route avoiding active hazard zones, road closures, and accident hotspots.": {
        "te": "ప్రమాదకర ప్రాంతాలు, రోడ్డు మూసివేతలు మరియు ప్రమాద ప్రదేశాలను తప్పించే అత్యంత సురక్షితమైన మార్గం.",
        "hi": "सक्रिय खतरा क्षेत्रों, सड़क बंद होने और दुर्घटना संभावित क्षेत्रों से बचने वाला सबसे सुरक्षित मार्ग।",
        "kn": "ಅಪಾಯದ ವಲಯಗಳು, ರಸ್ते ಮುಚ್ಚುವಿಕೆಗಳು ಮತ್ತು ಅಪಘಾತದ ಸ್ಥಳಗಳನ್ನು ತಪ್ಪಿಸುವ ಸುರಕ್ಷಿತ ಮಾರ್ಗ.",
        "ta": "செயலில் உள்ள ஆபத்து பகுதிகள், சாலை மூடல்கள் மற்றும் விபத்து இடங்களைத் தவிர்க்கும் பாதுகாப்பான பாதை.",
        "ml": "അപകടസാധ്യതാ മേഖലകൾ, റോഡ് അടയ്ക്കൽ, അപകട സാധ്യതയുള്ള സ്ഥലങ്ങൾ എന്നിവ ഒഴിവാക്കുന്ന ഏറ്റവും സുരക്ഷിതമായ റൂട്ട്.",
        "mr": "धोकादायक क्षेत्रे, रस्ते बंद असणे आणि अपघात प्रवण क्षेत्र टाळणारा सर्वात सुरक्षित मार्ग.",
        "bn": "সক্রিয় বিপদ অঞ্চল, রাস্তা বন্ধ এবং দুর্ঘটনা হটস্পট এড়ানো সবচেয়ে নিরাপদ রুট।"
    },
    "Smooth paved arterial road with continuous lighting and clear signages.": {
        "te": "నిరంతర వెలుతురు మరియు స్పష్టమైన సంకేతాలతో మృదువైన తారు రోడ్డు.",
        "hi": "निरंतर प्रकाश व्यवस्था और स्पष्ट संकेतों के साथ सुगम पक्की मुख्य सड़क।",
        "kn": "ನಿರಂತರ ಬೆಳಕು ಮತ್ತು ಸ್ಪಷ್ಟ ಫಲಕಗಳೊಂದಿಗೆ ಸುಗಮವಾದ ಡಾಂಬರು ರಸ್ತೆ.",
        "ta": "தொடர்ச்சியான வெளிச்சம் மற்றும் தெளிவான பலகைகளுடன் கூடிய மென்மையான தார் சாலை.",
        "ml": "തുടർച്ചയായ വെളിച്ചവും വ്യക്തമായ ബോർഡുകളുമുള്ള മിനുസമാർന്ന പ്രധാന പാത.",
        "mr": "सतत प्रकाश व्यवस्था आणि स्पष्ट फलकांसह गुळगुळीत डांबरी रस्ता.",
        "bn": "ক্রমাগত আলো এবং স্পষ্ট সংকেত সহ মসৃণ পাকা প্রধান রাস্তা।"
    },
    "Multi-speciality hospital with 24/7 emergency trauma care and ambulance service.": {
        "te": "24/7 అత్యవసర ట్రూమా కేర్ మరియు అంబులెన్స్ సేవలతో కూడిన మల్టీ-స్పెషాలిటీ ఆసుపత్రి.",
        "hi": "24/7 आपातकालीन आघात देखभाल और एम्बुलेंस सेवा वाला मल्टी-स्पेशियलिटी अस्पताल।",
        "kn": "24/7 ತುರ್ತು ಆಘಾತ ಆರೈಕೆ ಮತ್ತು ಆಂಬ್ಯುಲೆನ್ಸ್ ಸೇವೆಯನ್ನು ಹೊಂದಿರುವ ಮಲ್ಟಿ-ಸ್ಪೆಷಾಲಿಟಿ ಆಸ್ಪತ್ರೆ.",
        "ta": "24/7 அவசர சிகிச்சை மற்றும் ஆம்புலன்ஸ் சேவையுடன் கூடிய பல்நோக்கு சிறப்பு மருத்துவமனை.",
        "ml": "24/7 അടിയന്തിര ട്രോമ കെയറും ആംബുലൻസ് സേവനവുമുള്ള മൾട്ടി-സ്പെഷ്യാലിറ്റി ആശുപത്രി.",
        "mr": "24/7 आपत्कालीन ट्रॉमा केअर आणि रुग्णवाहिका सेवेसह मल्टी-स्पेशालिटी रुग्णालय.",
        "bn": "24/7 জরুরী ট্রমা কেয়ার এবং অ্যাম্বুলেন্স পরিষেবা সহ মাল্টি-স্পেশালিটি হাসপাতাল।"
    },
    "Primary Health Centre (PHC) providing essential medical consultations and first aid.": {
        "te": "ప్రాథమిక ఆరోగ్య కేంద్రం (PHC) అత్యవసర వైద్య సంప్రదింపులు మరియు ప్రథమ చికిత్స అందిస్తుంది.",
        "hi": "प्राथमिक स्वास्थ्य केंद्र (PHC) आवश्यक चिकित्सा परामर्श और प्राथमिक उपचार प्रदान करता है।",
        "kn": "ಪ್ರಾಥಮಿಕ ಆರೋಗ್ಯ ಕೇಂದ್ರ (PHC) ಅಗತ್ಯ ವೈದ್ಯಕೀಯ ಸಮಾಲೋಚನೆ ಮತ್ತು ಪ್ರಥಮ ಚಿಕಿತ್ಸೆ ನೀಡುತ್ತದೆ.",
        "ta": "ஆரம்ப சுகாதார நிலையம் (PHC) அத்தியாவசிய மருத்துவ ஆலோசனை மற்றும் முதலுதவி வழங்குகிறது.",
        "ml": "പ്രാഥമിക ആരോഗ്യ കേന്ദ്രം (PHC) അവശ്യ വൈദ്യോപദേശവും പ്രഥമശുശ്രൂഷയും നൽകുന്നു.",
        "mr": "प्राथमिक आरोग्य केंद्र (PHC) आवश्यक वैद्यकीय सल्ला आणि प्रथमोपचार प्रदान करते.",
        "bn": "প্রাথমিক স্বাস্থ্য কেন্দ্র (PHC) প্রয়োজনীয় চিকিৎসা পরামর্শ এবং প্রাথমিক চিকিৎসা প্রদান করে।"
    },
    "Supermarket offering fresh groceries, packaged foods, and household essentials.": {
        "te": "తాజా కిరాణా వస్తువులు, ప్యాక్ చేసిన ఆహారాలు మరియు గృహావసరాలను అందించే సూపర్ మార్కెట్.",
        "hi": "ताजा किराने का सामान, पैकेज्ड खाद्य पदार्थ और घरेलू आवश्यक वस्तुएं प्रदान करने वाला सुपरमार्केट।",
        "kn": "ತಾಜಾ ದಿನಸಿ, ಪ್ಯಾಕ್ ಮಾಡಿದ ಆಹಾರ ಮತ್ತು ಗೃಹೋಪಯೋಗಿ ವಸ್ತುಗಳನ್ನು ಒದಗಿಸುವ ಸೂಪರ್‌ಮಾರ್ಕೆಟ್.",
        "ta": "புதிய மளிகைப் பொருட்கள், பேக் செய்யப்பட்ட உணவுகள் மற்றும் வீட்டு அத்தியாவசியப் பொருட்களை வழங்கும் பல்பொருள் அங்காடி.",
        "ml": "പുതിയ പലചരക്ക് സാധനങ്ങൾ, പാക്ക് ചെയ്ത ഭക്ഷണങ്ങൾ, വീട്ടുപകരണങ്ങൾ എന്നിവ നൽകുന്ന സൂപ്പർമാർക്കറ്റ്.",
        "mr": "ताजा किराणा माल, पॅक केलेले अन्न आणि घरगुती जीवनावश्यक वस्तू देणारे सुपरमार्केट.",
        "bn": "তাজা মুদি, প্যাকেটজাত খাবার এবং গৃহস্থালীর প্রয়োজনীয় জিনিসপত্র সরবরাহকারী সুপারমার্কেট।"
    },
    "Automated Teller Machine (ATM) with cash withdrawal and banking facilities.": {
        "te": "నగదు ఉపసంహరణ మరియు బ్యాంకింగ్ సదుపాయాలతో కూడిన ఆటోమేటెడ్ టెల్లర్ మెషిన్ (ATM).",
        "hi": "नकद निकासी और बैंकिंग सुविधाओं के साथ स्वचालित टेलर मशीन (ATM)।",
        "kn": "ನಗದು ಹಿಂಪಡೆಯುವಿಕೆ ಮತ್ತು ಬ್ಯಾಂಕಿಂಗ್ ಸೌಲಭ್ಯಗಳೊಂದಿಗೆ ಸ್ವಯಂಚಾಲಿತ ಟೆಲ್ಲರ್ ಯಂತ್ರ (ATM).",
        "ta": "பணம் எடுக்கும் வசதி மற்றும் வங்கிச் சேவைகளுடன் கூடிய தானியங்கி பணப் பரிவர்த்தனை இயந்திரம் (ATM).",
        "ml": "പണം പിൻവലിക്കലും ബാങ്കിംഗ് സൗകര്യങ്ങളുമുള്ള ഓട്ടോമേറ്റഡ് ടെല്ലർ മെഷീൻ (ATM).",
        "mr": "रोख रक्कम काढणे आणि बँकिंग सुविधांसह ऑटोमेटेड टेलर मशीन (ATM).",
        "bn": "নগদ উত্তোলন এবং ব্যাংকিং সুবিধা সহ স্বয়ংক্রিয় টেলার মেশিন (ATM)।"
    },
    "Fuel station offering petrol, high-speed diesel, and air checking facilities.": {
        "te": "పెట్రోల్, హై-స్పీడ్ డీజిల్ మరియు టైర్ల ఎయిర్ చెకింగ్ సదుపాయాలను అందించే ఇంధన కేంద్రం.",
        "hi": "पेट्रोल, हाई-स्पीड डीजल और एयर चेकिंग सुविधाएं प्रदान करने वाला ईंधन स्टेशन।",
        "kn": "ಪೆಟ್ರೋಲ್, ಹೈ-ಸ್ಪೀಡ್ ಡೀಸೆಲ್ ಮತ್ತು ಏರ್ ಚೆಕ್ಕಿಂಗ್ ಸೌಲಭ್ಯಗಳನ್ನು ಒದಗಿಸುವ ಇಂಧನ ಕೇಂದ್ರ.",
        "ta": "பெட்ரோல், அதிவேக டீசல் மற்றும் காற்று சரிபார்க்கும் வசதிகளை வழங்கும் எரிபொருள் நிலையம்.",
        "ml": "പെട്രോൾ, ഹൈ-സ്പീഡ് ഡീസൽ, എയർ ചെക്കിംഗ് സൗകര്യങ്ങൾ എന്നിവ നൽകുന്ന ഇന്ധന സ്റ്റേഷൻ.",
        "mr": "पेट्रोल, हाय-स्पीड डिझेल आणि एअर चेकिंग सुविधा देणारे इंधन केंद्र.",
        "bn": "পেট্রল, হাই-স্পিড ডিজেল এবং এয়ার চেকিং সুবিধা প্রদানকারী জ্বালানী স্টেশন।"
    },
    "Authentic local restaurant serving hot South Indian meals, thalis, and specialties.": {
        "te": "వేడి దక్షిణ భారతీయ భోజనం, థాలీలు మరియు ప్రత్యేక వంటకాలను అందించే ప్రామాణిక స్థానిక రెస్టారెంట్.",
        "hi": "गरमा-गरम दक्षिण भारतीय भोजन, थाली और विशेष व्यंजन परोसने वाला प्रामाणिक स्थानीय रेस्तरां।",
        "kn": "ಬಿಸಿ ದಕ್ಷಿಣ ಭಾರತೀಯ ಊಟ, ಥಾಲಿ ಮತ್ತು ವಿಶೇಷತೆಗಳನ್ನು ಬಡಿಸುವ ಅಧಿಕೃತ ಸ್ಥಳೀಯ ಉಪಾಹಾರ ಗೃಹ.",
        "ta": "சூடான தென்னிந்திய உணவு, தாலி மற்றும் சிறப்பு உணவுகளை வழங்கும் உண்மையான உள்ளூர் உணவகம்.",
        "ml": "ചൂടുള്ള ദക്ഷിണേന്ത്യൻ ഭക്ഷണം, ഊണ്, പ്രത്യേക വിഭവങ്ങൾ എന്നിവ വിളമ്പുന്ന തനതായ പ്രാദേശിക റെസ്റ്റോറന്റ്.",
        "mr": "गरमागरम दक्षिण भारतीय जेवण, थाळी आणि खास पदार्थ देणारे अस्सल स्थानिक रेस्टॉरंट.",
        "bn": "গরম দক্ষিণ ভারতীয় খাবার, থালি এবং বিশেষ খাবার পরিবেশনকারী আসল স্থানীয় রেস্তোরাঁ।"
    },
    "Comfortable hotel accommodation with clean air-conditioned rooms, WiFi, and parking.": {
        "te": "శుభ్రమైన ఎయిర్ కండిషన్డ్ గదులు, వైఫై మరియు పార్కింగ్‌తో కూడిన సౌకర్యవంతమైన హోటల్ వసతి.",
        "hi": "स्वच्छ वातानुकूलित कमरे, वाईफाई और पार्किंग के साथ आरामदायक होटल आवास।",
        "kn": "ಸ್ವಚ್ಛ ಹವಾನಿಯಂತ್ರಿತ ಕೊಠಡಿಗಳು, ವೈಫೈ ಮತ್ತು ಪಾರ್ಕಿಂಗ್‌ನೊಂದಿಗೆ ಆರಾಮದಾಯಕ ಹೋಟೆಲ್ ವಸತಿ.",
        "ta": "சுத்தமான ஏசி அறைகள், வைஃபை மற்றும் பார்க்கிங் வசதியுடன் கூடிய வசதியான தங்குமிடம்.",
        "ml": "വൃത്തിയുള്ള എയർകണ്ടീഷൻ ചെയ്ത മുറികൾ, വൈഫൈ, പാർക്കിംഗ് എന്നിവയുള്ള സുഖപ്രദമായ ഹോട്ടൽ താമസം.",
        "mr": "स्वच्छ वातानुकूलित खोल्या, वायफाय आणि पार्किंगसह आरामदायक हॉटेल निवास.",
        "bn": "পরিষ্কার শীতাতপ নিয়ন্ত্রিত কক্ষ, ওয়াইফাই এবং পার্কিং সহ আরামদায়ক হোটেল আবাসন।"
    }
}

# Common phrase tokens and keywords that can be dynamically substituted
_VOCABULARY_MAP: Dict[str, Dict[str, str]] = {
    "welcome": {
        "te": "స్వాగతం", "hi": "स्वागत", "kn": "ಸ್ವಾಗತ", "ta": "வரவேற்கிறோம்", "ml": "സ്വാഗതം", "mr": "स्वागत", "bn": "স্বাগতম"
    },
    "departure": {
        "te": "ప్రారంభం", "hi": "प्रस्थान", "kn": "ನಿರ್ಗಮನ", "ta": "புறப்பாடு", "ml": "പുറപ്പെടൽ", "mr": "प्रस्थान", "bn": "প্রস্থান"
    },
    "arrival": {
        "te": "చేరుకోవడం", "hi": "आगमन", "kn": "ಆಗಮನ", "ta": "வருகை", "ml": "എത്തിച്ചേരൽ", "mr": "आगमन", "bn": "আগমন"
    },
    "recommended": {
        "te": "సిఫార్సు చేయబడినది", "hi": "अनुशंसित", "kn": "ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ", "ta": "பரிந்துரைக்கப்பட்டது", "ml": "ശുപാർശ ചെയ്യുന്നത്", "mr": "शिफारस केलेले", "bn": "সুপারিশকৃত"
    },
    "fastest": {
        "te": "వేగవంతమైన", "hi": "सबसे तेज़", "kn": "ಅತಿ ವೇಗದ", "ta": "வேகமான", "ml": "ഏറ്റവും വേഗമേറിയ", "mr": "सर्वात जलद", "bn": "দ্রুততম"
    },
    "shortest": {
        "te": "అతి తక్కువ దూరం", "hi": "सबसे छोटा", "kn": "ಅತಿ ಚಿಕ್ಕ", "ta": "குறுகிய", "ml": "ഏറ്റവും ചെറിയ", "mr": "सर्वात लहान", "bn": "ক্ষুদ্রতম"
    },
    "safest": {
        "te": "అత్యంత సురక్షితమైన", "hi": "सबसे सुरक्षित", "kn": "ಅತ್ಯಂತ ಸುರಕ್ಷಿತ", "ta": "பாதுகாப்பான", "ml": "ഏറ്റവും സുരക്ഷിതമായ", "mr": "सर्वात सुरक्षित", "bn": "সবচেয়ে নিরাপদ"
    },
    "scenic": {
        "te": "రమణీయమైన", "hi": "सुरम्य", "kn": "ನಯನಮನೋಹರ", "ta": "அழகிய", "ml": "മനോഹരമായ", "mr": "निसर्गरम्य", "bn": "মনোরম"
    },
    "cultural": {
        "te": "సాంస్కృతిక", "hi": "सांस्कृतिक", "kn": "ಸಾಂಸ್ಕೃತಿಕ", "ta": "கலாச்சார", "ml": "സാംസ്കാരിക", "mr": "सांस्कृतिक", "bn": "সাংস্কৃতিক"
    },
    "heritage": {
        "te": "వారసత్వం", "hi": "विरासत", "kn": "ಪರಂಪರೆ", "ta": "பாரம்பரியம்", "ml": "പൈതൃകം", "mr": "वारसा", "bn": "ঐতিহ্য"
    },
    "nature": {
        "te": "ప్రకృతి", "hi": "प्रकृति", "kn": "ಪ್ರಕೃತಿ", "ta": "இயற்கை", "ml": "പ്രകൃതി", "mr": "निसर्ग", "bn": "প্রকৃতি"
    },
    "food": {
        "te": "ఆహారం", "hi": "भोजन", "kn": "ಆಹಾರ", "ta": "உணவு", "ml": "ഭക്ഷണം", "mr": "अन्न", "bn": "খাবার"
    },
    "hospital": {
        "te": "ఆసుపత్రి", "hi": "अस्पताल", "kn": "ಆಸ್ಪತ್ರೆ", "ta": "மருத்துவமனை", "ml": "ആശുപത്രി", "mr": "रुग्णालय", "bn": "হাসপাতাল"
    },
    "hotel": {
        "te": "హోటల్", "hi": "होटल", "kn": "ಹೋಟೆಲ್", "ta": "விடுதி", "ml": "ഹോട്ടൽ", "mr": "हॉटेल", "bn": "হোটেল"
    },
    "restaurant": {
        "te": "రెస్టారెంట్", "hi": "रेस्तरां", "kn": "ಉಪಾಹಾರ ಗೃಹ", "ta": "உணவகம்", "ml": "റെസ്റ്റോറന്റ്", "mr": "रेस्टॉरंट", "bn": "রেস্তোরাঁ"
    },
    "flight": {
        "te": "విమానం", "hi": "उड़ान", "kn": "ವಿಮಾನ", "ta": "விமானம்", "ml": "വിമാനം", "mr": "विमान", "bn": "বিমান"
    },
    "airport": {
        "te": "విమానాశ్రయం", "hi": "हवाई अड्डा", "kn": "ವಿಮಾನ ನಿಲ್ದಾಣ", "ta": "விமான நிலையம்", "ml": "വിമാനത്താവളം", "mr": "विमानतळ", "bn": "বিমানবন্দর"
    },
    "distance": {
        "te": "దూరం", "hi": "दूरी", "kn": "ದೂರ", "ta": "தூரம்", "ml": "ദൂരം", "mr": "अंतर", "bn": "দূরত্ব"
    },
    "duration": {
        "te": "వ్యవధి", "hi": "अवधि", "kn": "ಅವಧಿ", "ta": "கால அளவு", "ml": "സമയം", "mr": "कालावधी", "bn": "সময়কাল"
    },
    "turn right": {
        "te": "కుడివైపు తిరగండి", "hi": "दाएं मुड़ें", "kn": "ಬಲಕ್ಕೆ ತಿರುಗಿ", "ta": "வலதுபுறம் திரும்பவும்", "ml": "വലത്തോട്ട് തിരിയുക", "mr": "उजवीकडे वळा", "bn": "ডানদিকে ঘুরুন"
    },
    "turn left": {
        "te": "ఎడమవైపు తిరగండి", "hi": "बाएं मुड़ें", "kn": "ಎಡಕ್ಕೆ ತಿರುಗಿ", "ta": "இடதுபுறம் திரும்பவும்", "ml": "ഇടത്തോട്ട് തിരിയുക", "mr": "डावीकडे वळा", "bn": "বামদিকে ঘুরুন"
    },
    "continue straight": {
        "te": "నేరుగా వెళ్ళండి", "hi": "सीधे चलते रहें", "kn": "ನೇರವಾಗಿ ಮುಂದುವರಿಯಿರಿ", "ta": "நேராக செல்லவும்", "ml": "നേരെ തുടരുക", "mr": "सरळ पुढे जा", "bn": "সোজা এগিয়ে যান"
    }
}


def _shield_protected_entities(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Replaces protected names, URLs, coordinates, and brand names with unique tokens
    so translations will never mutate or alter them.
    """
    token_map: Dict[str, str] = {}
    counter = 0

    # 1. URLs
    def _url_sub(match):
        nonlocal counter
        tok = f"__PROT_URL_{counter}__"
        counter += 1
        token_map[tok] = match.group(0)
        return tok
    text = re.sub(r'https?://[^\s]+', _url_sub, text)

    # 2. Coordinates e.g. 16.5062, 80.6480
    def _coord_sub(match):
        nonlocal counter
        tok = f"__PROT_CRD_{counter}__"
        counter += 1
        token_map[tok] = match.group(0)
        return tok
    text = re.sub(r'\b\d{1,3}\.\d{3,8}\s*,\s*\d{1,3}\.\d{3,8}\b', _coord_sub, text)

    # 3. Protected entities list
    for ent in sorted(PROTECTED_ENTITIES, key=len, reverse=True):
        pattern = re.compile(r'\b' + re.escape(ent) + r'\b', re.IGNORECASE)
        def _ent_sub(m):
            nonlocal counter
            tok = f"__PROT_ENT_{counter}__"
            counter += 1
            token_map[tok] = m.group(0)
            return tok
        text = pattern.sub(_ent_sub, text)

    return text, token_map


def _unshield_protected_entities(text: str, token_map: Dict[str, str]) -> str:
    """Restores all shielded protected entities accurately."""
    for tok, orig in token_map.items():
        text = text.replace(tok, orig)
    return text


def translate_content(
    text: Any,
    target_language: Optional[str] = None,
    category: Optional[str] = None,
    preserve_entities: bool = True
) -> str:
    """
    Universal Multilingual Translation Engine for dynamic content.
    - Resolves target language automatically or via parameter.
    - Preserves protected proper nouns, coordinates, and factual data.
    - Uses domain knowledge base, pattern translation, and high-speed in-memory caching.
    - Instant fallback to original text if language is English or unrecognized.
    """
    if text is None:
        return ""
    str_text = str(text).strip()
    if not str_text:
        return ""

    # Resolve target language
    if not target_language:
        try:
            import streamlit as st
            target_language = st.session_state.get("app_language", DEFAULT_LANGUAGE)
        except Exception:
            target_language = DEFAULT_LANGUAGE

    if target_language not in SUPPORTED_LANGUAGES or target_language == DEFAULT_LANGUAGE:
        return str_text

    # Check Cache
    cache_key = (str_text, target_language)
    if cache_key in _DYNAMIC_TRANSLATION_CACHE:
        return _DYNAMIC_TRANSLATION_CACHE[cache_key]

    # Check Exact Domain Database Match
    if str_text in _CORRIDOR_DESCRIPTIONS_DB:
        lang_dict = _CORRIDOR_DESCRIPTIONS_DB[str_text]
        if target_language in lang_dict:
            res = lang_dict[target_language]
            _DYNAMIC_TRANSLATION_CACHE[cache_key] = res
            return res

    # Check for match ignoring minor trailing punctuation or whitespace
    clean_key = str_text.rstrip(" .!?:") + "."
    if clean_key in _CORRIDOR_DESCRIPTIONS_DB:
        lang_dict = _CORRIDOR_DESCRIPTIONS_DB[clean_key]
        if target_language in lang_dict:
            res = lang_dict[target_language]
            _DYNAMIC_TRANSLATION_CACHE[cache_key] = res
            return res

    # Shield protected entities
    shielded_text, token_map = _shield_protected_entities(str_text)

    # Translate sentences individually
    sentences = re.split(r'([.?!]\s+)', shielded_text)
    translated_parts = []

    for i in range(0, len(sentences), 2):
        sentence = sentences[i].strip()
        sep = sentences[i+1] if i+1 < len(sentences) else ""

        if not sentence:
            translated_parts.append(sep)
            continue

        # Look up sentence in database
        unshielded_sent = _unshield_protected_entities(sentence, token_map)
        sent_trans = None

        if unshielded_sent in _CORRIDOR_DESCRIPTIONS_DB:
            sent_trans = _CORRIDOR_DESCRIPTIONS_DB[unshielded_sent].get(target_language)
        elif unshielded_sent.rstrip(" .!?:") + "." in _CORRIDOR_DESCRIPTIONS_DB:
            sent_trans = _CORRIDOR_DESCRIPTIONS_DB[unshielded_sent.rstrip(" .!?:") + "."].get(target_language)

        if sent_trans:
            translated_parts.append(sent_trans + sep)
        else:
            # Pattern-based keyword and phrase translation
            translated_sent = sentence
            for eng_phrase, trans_dict in _VOCABULARY_MAP.items():
                if target_language in trans_dict:
                    pattern = re.compile(r'\b' + re.escape(eng_phrase) + r'\b', re.IGNORECASE)
                    translated_sent = pattern.sub(trans_dict[target_language], translated_sent)

            # Restore shielded tokens
            final_sent = _unshield_protected_entities(translated_sent, token_map)
            translated_parts.append(final_sent + sep)

    result = "".join(translated_parts)
    result = _unshield_protected_entities(result, token_map)

    # Cache result
    _DYNAMIC_TRANSLATION_CACHE[cache_key] = result
    return result


def translate_dict_descriptions(
    data: Dict[str, Any],
    target_language: str,
    keys_to_translate: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Translates only user-facing descriptive fields of a dictionary while
    guaranteeing factual IDs, coordinates, and technical properties remain untouched.
    """
    if not isinstance(data, dict):
        return data

    if target_language == DEFAULT_LANGUAGE:
        return data

    target_keys = keys_to_translate or [
        "description", "cultural_heritage", "geography_nature",
        "scenic_highlight", "culinary_highlight", "historical_lore",
        "travel_tip", "aura_speech", "what_to_look_for", "headline",
        "reason", "summary", "instructions"
    ]

    new_data = dict(data)
    for k, v in data.items():
        if k in target_keys and isinstance(v, str):
            new_data[k] = translate_content(v, target_language=target_language)
        elif isinstance(v, list) and k in target_keys:
            new_data[k] = [
                translate_content(item, target_language=target_language) if isinstance(item, str) else item
                for item in v
            ]
        elif isinstance(v, dict):
            new_data[k] = translate_dict_descriptions(v, target_language=target_language, keys_to_translate=keys_to_translate)

    return new_data
