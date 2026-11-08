"""
P.A.T.H.F.I.N.D.E.R. • AURA Complete Start-to-Destination Journey Experience Engine
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Human-Centric Visual Journey System

Orchestrates the complete 19-stage end-to-end interactive journey experience featuring
Aura (the 3D robot companion) from initial welcome and location input to dynamic
turn-by-turn navigation, maneuver guide, storybook gallery, and arrival celebration.
"""

import os
import json
import math
import base64
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple, Union


class AuraJourneyStage(str, Enum):
    """The 19 stages of the end-to-end journey experience."""
    WELCOME = "WELCOME"
    START_INPUT = "START_INPUT"
    START_CONFIRMED = "START_CONFIRMED"
    DEST_INPUT = "DEST_INPUT"
    DEST_CONFIRMED = "DEST_CONFIRMED"
    MODE_SELECT = "MODE_SELECT"
    CALCULATING_ROUTES = "CALCULATING_ROUTES"
    ALTERNATIVES_READY = "ALTERNATIVES_READY"
    ROUTE_CHOSEN = "ROUTE_CHOSEN"
    ROUTE_OVERVIEW = "ROUTE_OVERVIEW"
    JOURNEY_CONFIRMED = "JOURNEY_CONFIRMED"
    NAVIGATING = "NAVIGATING"
    MANEUVER_APPROACHING = "MANEUVER_APPROACHING"
    LANDMARK_DISCOVERED = "LANDMARK_DISCOVERED"
    OFF_ROUTE = "OFF_ROUTE"
    NEAR_DESTINATION = "NEAR_DESTINATION"
    ARRIVED = "ARRIVED"
    JOURNEY_SUMMARY = "JOURNEY_SUMMARY"


class AuraPose(str, Enum):
    """Aura's distinct 3D / graphic character poses."""
    WELCOME = "welcome"
    POINTING = "pointing"
    THINKING = "thinking"
    EXCITED = "excited"
    TALKING = "talking"
    WAVING = "waving"


@dataclass
class AuraManeuverStep:
    """Rich maneuver model for every individual turn on the journey."""
    step_num: int
    total_steps: int
    direction_type: str  # START, STRAIGHT, LEFT, RIGHT, SLIGHT_LEFT, SLIGHT_RIGHT, SHARP_LEFT, SHARP_RIGHT, KEEP_LEFT, KEEP_RIGHT, MERGE, ROUNDABOUT, U_TURN, CROSSING, ARRIVE
    headline: str
    instruction: str
    spoken_text: str
    aura_speech: str
    road_name: str
    distance_m: float
    distance_human: str
    time_estimate: str
    icon: str
    aura_pose: AuraPose = AuraPose.TALKING
    what_to_look_for: str = ""
    accessible_guidance: str = ""
    roundabout_exit: Optional[int] = None
    coordinates: Optional[List[float]] = None
    status: str = "UPCOMING"  # COMPLETED, ACTIVE, UPCOMING


class AuraPoseAssetManager:
    """Manages cached base64 URIs for Aura's mascot poses."""
    _poses: Dict[str, str] = {}
    _loaded: bool = False

    @classmethod
    def load_poses(cls) -> Dict[str, str]:
        if cls._loaded and cls._poses:
            return cls._poses

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        poses_json_path = os.path.join(base_dir, "data", "mascot_poses_trans.json")
        assets_dir = os.path.join(base_dir, "assets")

        loaded = {}
        if os.path.exists(poses_json_path):
            try:
                with open(poses_json_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
            except Exception:
                pass

        # Fallback to direct PNG files in assets
        pose_files = {
            "welcome": "mascot_welcome_trans.png",
            "pointing": "mascot_pointing_trans.png",
            "thinking": "mascot_thinking_trans.png",
            "excited": "mascot_excited_trans.png",
            "talking": "mascot_talking_trans.png",
            "waving": "mascot_waving.png"
        }

        for pose_key, filename in pose_files.items():
            if pose_key not in loaded or not loaded[pose_key]:
                fpath = os.path.join(assets_dir, filename)
                if not os.path.exists(fpath):
                    fpath = os.path.join(assets_dir, filename.replace("_trans", "_clean"))
                if os.path.exists(fpath):
                    try:
                        with open(fpath, "rb") as img_file:
                            b64 = base64.b64encode(img_file.read()).decode("utf-8")
                            loaded[pose_key] = f"data:image/png;base64,{b64}"
                    except Exception:
                        pass

        cls._poses = loaded
        cls._loaded = True
        return cls._poses

    @classmethod
    def get_pose_uri(cls, pose: Union[AuraPose, str]) -> str:
        poses = cls.load_poses()
        key = pose.value if isinstance(pose, AuraPose) else str(pose).lower()
        return poses.get(key) or poses.get("welcome") or ""


class AuraSpeechGenerator:
    """Generates warm, expressive speech and thoughts matching actual journey events across all 8 languages."""

    @staticmethod
    def get_speech_for_stage(stage: AuraJourneyStage, context: Optional[Dict[str, Any]] = None, language: Optional[str] = "en") -> Tuple[str, AuraPose]:
        ctx = context or {}
        orig = ctx.get("origin", "Start")
        dest = ctx.get("destination", "Destination")
        mode = ctx.get("travel_mode", "car").lower()
        dist = ctx.get("distance_km", "")
        time_est = ctx.get("duration_mins", "")
        clean_lang = (language or "en").lower().split("-")[0]
        if clean_lang not in ("en", "te", "hi", "ta", "kn", "ml", "bn", "mr"):
            clean_lang = "en"

        MULTILINGUAL_SPEECH = {
            AuraJourneyStage.WELCOME: {
                "en": "Hey, traveler! I'm Aura, your NexRoute companion. Where shall our adventure begin?",
                "te": "హలో ప్రయాణికుడా! నేను మీ నెక్స్‌రూట్ సహచరి ఔరాను. మన ప్రయాణం ఎక్కడి నుండి మొదలవుతుంది?",
                "hi": "नमस्ते यात्री! मैं ऑरा हूँ, आपकी नेक्ससूट साथी। हमारी यात्रा कहाँ से शुरू होगी?",
                "ta": "வணக்கம் பயணியே! நான் உங்கள் நெக்ஸ்ரூட் துணைவி ஆரா. நமது பயணம் எங்கிருந்து தொடங்குகிறது?",
                "kn": "ನಮಸ್ಕಾರ ಪ್ರಯಾಣಿಕರೇ! ನಾನು ನಿಮ್ಮ ನೆಕ್ಸ್‌ರೂಟ್ ಒಡನಾಡಿ ಔರಾ. ನಮ್ಮ ಸಾಹಸ ಎಲ್ಲಿಂದ ಪ್ರಾರಂಭವಾಗಲಿದೆ?",
                "ml": "നമസ്കാരം യാത്രികാ! ഞാൻ നിങ്ങളുടെ നെക്സ്റൂട്ട് കൂട്ടുകാരി ഓറ. നമ്മുടെ യാത്ര എവിടെ നിന്ന് തുടങ്ങണം?",
                "bn": "নমস্কার যাত্রী! আমি অরা, আপনার নেক্সরুট সঙ্গী। আমাদের যাত্রা কোথা থেকে শুরু হবে?",
                "mr": "नमस्कार प्रवाशा! मी ऑरा आहे, तुमची नेक्सरूट साथीदार. आपला प्रवास कुठून सुरू करायचा?"
            },
            AuraJourneyStage.START_INPUT: {
                "en": "Let's choose our starting point. You can enter an address, a landmark, or use your current location.",
                "te": "మన ప్రారంభ స్థానాన్ని ఎంచుకుందాం. మీరు చిరునామా, మైలురాయిని నమోదు చేయవచ్చు లేదా మీ ప్రస్తుత స్థానాన్ని ఉపయోగించవచ్చు.",
                "hi": "आइए अपना शुरुआती बिंदु चुनें। आप कोई पता, लैंडमार्क दर्ज कर सकते हैं या अपने वर्तमान स्थान का उपयोग कर सकते हैं।",
                "ta": "நமது தொடக்கப் புள்ளியைத் தேர்ந்தெடுப்போம். நீங்கள் முகவரி, அடையாளக் குறியீட்டை உள்ளிடலாம் அல்லது தற்போதைய இருப்பிடத்தைப் பயன்படுத்தலாம்.",
                "kn": "ನಮ್ಮ ಪ್ರಾರಂಭಿಕ ಬಿಂದುವನ್ನು ಆರಿಸೋಣ. ನೀವು ವಿಳಾಸ, ಹೆಗ್ಗುರುತನ್ನು ನಮೂದಿಸಬಹುದು ಅಥವಾ ನಿಮ್ಮ ಪ್ರಸ್ತುತ ಸ್ಥಳವನ್ನು ಬಳಸಬಹುದು.",
                "ml": "നമുക്ക് ആരംഭ സ്ഥാനം തിരഞ്ഞെടുക്കാം. നിങ്ങൾക്ക് ഒരു വിലാസമോ ലാൻഡ്‌മാർക്കോ നൽകാം അല്ലെങ്കിൽ നിങ്ങളുടെ നിലവിലെ ലൊക്കേഷൻ ഉപയോഗിക്കാം.",
                "bn": "আসুন আমাদের শুরুর স্থান নির্বাচন করি। আপনি একটি ঠিকানা, ল্যান্ডমার্ক প্রবেশ করাতে পারেন বা আপনার বর্তমান অবস্থান ব্যবহার করতে পারেন।",
                "mr": "चला आपला सुरुवातीचा बिंदू निवडूया. आपण पत्ता, लँडमार्क प्रविष्ट करू शकता किंवा आपले वर्तमान स्थान वापरू शकता."
            },
            AuraJourneyStage.START_CONFIRMED: {
                "en": f"Great! I've got our starting point at {orig}. Now let's choose where we're heading.",
                "te": f"చాలా బాగుంది! మన ప్రారంభ స్థానం {orig} వద్ద సెట్ చేయబడింది. ఇప్పుడు మనం ఎక్కడికి వెళ్తున్నామో ఎంచుకుందాం.",
                "hi": f"शानदार! हमारे पास {orig} पर प्रारंभिक बिंदु है। अब चुनते हैं कि हम कहाँ जा रहे हैं।",
                "ta": f"அருமை! {orig} இல் நமது தொடக்கப் புள்ளி அமைக்கப்பட்டது. இப்போது நாம் எங்கு செல்கிறோம் என்பதைத் தேர்ந்தெடுப்போம்.",
                "kn": f"ಉತ್ತಮ! {orig} ನಲ್ಲಿ ನಮ್ಮ ಆರಂಭಿಕ ಬಿಂದು ಸಿದ್ಧವಾಗಿದೆ. ಈಗ ನಾವು ಎಲ್ಲಿಗೆ ಹೋಗುತ್ತಿದ್ದೇವೆ ಎಂಬುದನ್ನು ಆರಿಸೋಣ.",
                "ml": f"വളരെ നല്ലത്! {orig} ൽ നമ്മുടെ ആരംഭ സ്ഥാനം രേഖപ്പെടുത്തി. ഇനി നമ്മൾ എങ്ങോട്ടാണ് പോകുന്നതെന്ന് തിരഞ്ഞെടുക്കാം.",
                "bn": f"চমৎকার! {orig}-এ আমাদের শুরুর স্থান নির্ধারণ হয়েছে। এখন বেছে নিন আমরা কোথায় যাচ্ছি।",
                "mr": f"छान! आपल्याकडे {orig} येथे सुरुवातीचा बिंदू आहे. आता आपण कुठे जात आहोत ते निवडूया."
            },
            AuraJourneyStage.DEST_INPUT: {
                "en": "Where would you like to go? Tell me your destination and I'll help plan the journey.",
                "te": "మీరు ఎక్కడికి వెళ్లాలనుకుంటున్నారు? మీ గమ్యస్థానాన్ని చెప్పండి, ప్రయాణాన్ని ప్లాన్ చేయడంలో నేను మీకు సహాయం చేస్తాను.",
                "hi": "आप कहाँ जाना चाहेंगे? मुझे अपना गंतव्य बताएं और मैं यात्रा की योजना बनाने में मदद करूँगी।",
                "ta": "நீங்கள் எங்கு செல்ல விரும்புகிறீர்கள்? உங்கள் சேருமிடத்தைச் சொல்லுங்கள், பயணத்தைத் திட்டமிட உதவுகிறேன்.",
                "kn": "ನೀವು ಎಲ್ಲಿಗೆ ಹೋಗಲು ಬಯಸುತ್ತೀರಿ? ನಿಮ್ಮ ಗಮ್ಯಸ್ಥಾನವನ್ನು ತಿಳಿಸಿ, ಪ್ರಯಾಣವನ್ನು ಯೋಜಿಸಲು ನಾನು ಸಹಾಯ ಮಾಡುತ್ತೇನೆ.",
                "ml": "നിങ്ങൾക്ക് എങ്ങോട്ടാണ് പോകേണ്ടത്? ലക്ഷ്യസ്ഥാനം പറയൂ, യാത്ര പ്ലാൻ ചെയ്യാൻ ഞാൻ സഹായിക്കാം.",
                "bn": "আপনি কোথায় যেতে চান? আপনার গন্তব্য বলুন এবং আমি ভ্রমণের পরিকল্পনা করতে সহায়তা করব।",
                "mr": "आपण कुठे जाऊ इच्छिता? मला आपले गंतव्य सांगा आणि मी प्रवासाचे नियोजन करण्यास मदत करेन."
            },
            AuraJourneyStage.DEST_CONFIRMED: {
                "en": f"Destination selected: {dest}! Let's find a suitable route.",
                "te": f"గమ్యస్థానం ఎంచుకోబడింది: {dest}! అనువైన మార్గాన్ని కనుగొందాం.",
                "hi": f"गंतव्य चुना गया: {dest}! आइए एक उपयुक्त मार्ग खोजें।",
                "ta": f"சேருமிடம் தேர்ந்தெடுக்கப்பட்டது: {dest}! பொருத்தமான வழியைக் கண்டுபிடிப்போம்.",
                "kn": f"ಗಮ್ಯಸ್ಥಾನವನ್ನು ಆಯ್ಕೆ ಮಾಡಲಾಗಿದೆ: {dest}! ಸೂಕ್ತವಾದ ಮಾರ್ಗವನ್ನು ಕಂಡುಹಿಡಿಯೋಣ.",
                "ml": f"ലക്ഷ്യസ്ഥാനം തിരഞ്ഞെടുത്തു: {dest}! അനുയോജ്യമായ വഴി കണ്ടെത്താം.",
                "bn": f"গন্তব্য নির্বাচিত: {dest}! আসুন একটি উপযুক্ত রুট খুঁজে বের করি।",
                "mr": f"गंतव्य निवडले: {dest}! चला एक योग्य मार्ग शोधूया."
            },
            AuraJourneyStage.MODE_SELECT: {
                "en": "How would you like to travel? I'll adjust the route to match your choice.",
                "te": "మీరు ఎలా ప్రయాణించాలనుకుంటున్నారు? మీ ఎంపికకు తగినట్లుగా మార్గాన్ని సర్దుబాటు చేస్తాను.",
                "hi": "आप कैसे यात्रा करना चाहेंगे? मैं आपकी पसंद के अनुसार मार्ग समायोजित करूँगी।",
                "ta": "நீங்கள் எவ்வாறு பயணிக்க விரும்புகிறீர்கள்? உங்கள் விருப்பத்திற்கு ஏற்ப வழியை மாற்றியமைப்பேன்.",
                "kn": "ನೀವು ಹೇಗೆ ಪ್ರಯಾಣಿಸಲು ಬಯಸುತ್ತೀರಿ? ನಿಮ್ಮ ಆಯ್ಕೆಗೆ ತಕ್ಕಂತೆ ಮಾರ್ಗವನ್ನು ಹೊಂದಿಸುತ್ತೇನೆ.",
                "ml": "നിങ്ങൾ എങ്ങനെ യാത്ര ചെയ്യാനാണ് ആഗ്രഹിക്കുന്നത്? നിങ്ങളുടെ ഇഷ്ടത്തിനനുസരിച്ച് ഞാൻ വഴി ക്രമീകരിക്കും.",
                "bn": "আপনি কীভাবে ভ্রমণ করতে চান? আপনার পছন্দ অনুসারে আমি রুটটি সাজিয়ে দেব।",
                "mr": "आपण कसा प्रवास करू इच्छिता? मी आपल्या पसंतीनुसार मार्ग जुळवून घेईन."
            },
            AuraJourneyStage.ALTERNATIVES_READY: {
                "en": "I've found some ways to get there. Let's choose the route that works best for you.",
                "te": "అక్కడికి చేరుకోవడానికి కొన్ని మార్గాలను కనుగొన్నాను. మీకు ఉత్తమంగా సరిపోయే మార్గాన్ని ఎంచుకుందాం.",
                "hi": "मुझे वहां पहुंचने के कुछ रास्ते मिले हैं। आइए वह मार्ग चुनें जो आपके लिए सबसे अच्छा हो।",
                "ta": "அங்கு செல்ல சில வழிகளைக் கண்டுபிடித்துள்ளேன். உங்களுக்கு மிகவும் பொருத்தமான வழியைத் தேர்ந்தெடுப்போம்.",
                "kn": "ಅಲ್ಲಿಗೆ ತಲುಪಲು ಕೆಲವು ಮಾರ್ಗಗಳನ್ನು ಕಂಡುಕೊಂಡಿದ್ದೇನೆ. ನಿಮಗೆ ಉತ್ತಮವಾಗಿ ಹೊಂದಿಕೊಳ್ಳುವ ಮಾರ್ಗವನ್ನು ಆರಿಸೋಣ.",
                "ml": "അവിടെയെത്താൻ ചില വഴികൾ ഞാൻ കണ്ടെത്തിയിട്ടുണ്ട്. നിങ്ങൾക്ക് ഏറ്റവും അനുയോജ്യമായത് തിരഞ്ഞെടുക്കാം.",
                "bn": "সেখানে পৌঁছানোর কয়েকটি রুট পেয়েছি। আপনার জন্য যেটি সবচেয়ে উপযুক্ত তা বেছে নিন।",
                "mr": "मला तिथे पोहोचण्यासाठी काही मार्ग सापडले आहेत. आपल्यासाठी सर्वोत्तम मार्ग निवडूया."
            },
            AuraJourneyStage.ROUTE_OVERVIEW: {
                "en": f"Route ready! {dist} km across approximately {time_est} mins. Ready to begin?",
                "te": f"మార్గం సిద్ధంగా ఉంది! దాదాపు {time_est} నిమిషాలలో {dist} కి.మీ. ప్రారంభించడానికి సిద్ధంగా ఉన్నారా?",
                "hi": f"मार्ग तैयार है! लगभग {time_est} मिनट में {dist} किमी। क्या आप शुरू करने के लिए तैयार हैं?",
                "ta": f"பயணப்பாதை தயார்! சுமார் {time_est} நிமிடங்களில் {dist} கி.மீ. தொடங்கத் தயாரா?",
                "kn": f"ಮಾರ್ಗ ಸಿದ್ಧವಾಗಿದೆ! ಸುಮಾರು {time_est} ನಿಮಿಷಗಳಲ್ಲಿ {dist} ಕಿ.ಮೀ. ಪ್ರಾರಂಭಿಸಲು ಸಿದ್ಧರಿದ್ದೀರಾ?",
                "ml": f"റൂട്ട് തയ്യാറാണ്! ഏകദേശം {time_est} മിനിറ്റിൽ {dist} കി.മീ. ആരംഭിക്കാൻ തയ്യാറാണോ?",
                "bn": f"রুট প্রস্তুত! প্রায় {time_est} মিনিটে {dist} কিমি। যাত্রা শুরু করতে প্রস্তুত?",
                "mr": f"मार्ग तयार आहे! सुमारे {time_est} मिनिटांत {dist} किमी। सुरू करण्यास तयार आहात?"
            },
            AuraJourneyStage.JOURNEY_CONFIRMED: {
                "en": "Ready? Let's begin our adventure. I'll guide you step by step.",
                "te": "సిద్ధంగా ఉన్నారా? మన ప్రయాణాన్ని ప్రారంభిద్దాం. నేను అడుగడుగునా మీకు మార్గదర్శనం చేస్తాను.",
                "hi": "तैयार हैं? आइए अपनी यात्रा शुरू करें। मैं कदम दर कदम आपका मार्गदर्शन करूँगी।",
                "ta": "தயாரா? நமது பயணத்தைத் தொடங்குவோம். நான் படிப்படியாக உங்களுக்கு வழிகாட்டுவேன்.",
                "kn": "ಸಿದ್ಧರಿದ್ದೀರಾ? ನಮ್ಮ ಸಾಹಸವನ್ನು ಪ್ರಾರಂಭಿಸೋಣ. ನಾನು ಹಂತ ಹಂತವಾಗಿ ನಿಮಗೆ ಮಾರ್ಗದರ್ಶನ ನೀಡುತ್ತೇನೆ.",
                "ml": "തയ്യാറാണോ? നമുക്ക് യാത്ര തുടങ്ങാം. ഓരോ ഘട്ടത്തിലും ഞാൻ വഴികാട്ടാം.",
                "bn": "প্রস্তুত? আসুন আমাদের যাত্রা শুরু করি। আমি ধাপে ধাপে পথ দেখাব।",
                "mr": "तयार आहात? चला आपला प्रवास सुरू करूया. मी प्रत्येक टप्प्यावर मार्गदर्शन करेन."
            },
            AuraJourneyStage.NAVIGATING: {
                "en": "Our adventure is underway! Following the mapped corridor safely.",
                "te": "మన ప్రయాణం ప్రారంభమైంది! మ్యాప్ చేయబడిన కారిడార్‌ను సురక్షితంగా అనుసరిస్తున్నాము.",
                "hi": "हमारी यात्रा शुरू हो चुकी है! मैप किए गए कॉरिडोर का सुरक्षित रूप से पालन कर रहे हैं।",
                "ta": "நமது பயணம் தொடங்கிவிட்டது! வழிகாட்டப்பட்ட பாதையை பாதுகாப்பாகப் பின்பற்றுகிறோம்.",
                "kn": "ನಮ್ಮ ಸಾಹಸ ಪ್ರಾರಂಭವಾಗಿದೆ! ಮ್ಯಾಪ್ ಮಾಡಿದ ಕಾರಿಡಾರ್ ಅನ್ನು ಸುರಕ್ಷಿತವಾಗಿ ಅನುಸರಿಸುತ್ತಿದ್ದೇವೆ.",
                "ml": "നമ്മുടെ യാത്ര ആരംഭിച്ചു! മാപ്പ് ചെയ്ത വഴിയിലൂടെ സുരക്ഷിതമായി മുന്നോട്ട് പോകുന്നു.",
                "bn": "আমাদের যাত্রা শুরু হয়েছে! ম্যাপ করা করিডোর নিরাপদে অনুসরণ করছি।",
                "mr": "आपला प्रवास सुरू झाला आहे! मॅप केलेल्या कॉरिडॉरचे सुरक्षितपणे अनुसरण करत आहोत."
            },
            AuraJourneyStage.ARRIVED: {
                "en": "We made it! You've reached your destination. Would you like to explore nearby places or plan your next adventure?",
                "te": "మనం చేరుకున్నాము! మీరు మీ గమ్యస్థానానికి చేరుకున్నారు. సమీప ప్రదేశాలను అన్వేషించాలనుకుంటున్నారా లేదా మీ తదుపరి ప్రయాణాన్ని ప్లాన్ చేయాలనుకుంటున్నారా?",
                "hi": "हम पहुंच गए! आप अपने गंतव्य पर पहुंच गए हैं। क्या आप आस-पास के स्थानों का पता लगाना चाहते हैं या अपनी अगली यात्रा की योजना बनाना चाहते हैं?",
                "ta": "நாம் அடைந்துவிட்டோம்! உங்கள் சேருமிடத்தை அடைந்துவிட்டீர்கள். அருகிலுள்ள இடங்களை ஆராய விரும்புகிறீர்களா அல்லது அடுத்த பயணத்தைத் திட்டமிட விரும்புகிறீர்களா?",
                "kn": "ನಾವು ತಲುಪಿದೆವು! ನೀವು ನಿಮ್ಮ ಗಮ್ಯಸ್ಥಾನವನ್ನು ತಲುಪಿದ್ದೀರಿ. ಹತ್ತಿರದ ಸ್ಥಳಗಳನ್ನು ಅನ್ವೇಷಿಸಲು ಅಥವಾ ನಿಮ್ಮ ಮುಂದಿನ ಸಾಹಸವನ್ನು ಯೋಜಿಸಲು ಬಯಸುತ್ತೀರಾ?",
                "ml": "നമ്മൾ എത്തിച്ചേർന്നു! നിങ്ങൾ ലക്ഷ്യസ്ഥാനത്ത് എത്തി. സമീപ സ്ഥലങ്ങൾ പര്യവേക്ഷണം ചെയ്യാനോ അടുത്ത യാത്ര പ്ലാൻ ചെയ്യാനോ ആഗ്രഹിക്കുന്നുണ്ടോ?",
                "bn": "আমরা পৌঁছে গেছি! আপনি আপনার গন্তব্যে পৌঁছেছেন। আপনি কি আশেপাশের স্থানগুলি ঘুরে দেখতে চান নাকি আপনার পরবর্তী ভ্রমণের পরিকল্পনা করতে চান?",
                "mr": "आम्ही पोहोचलो! आपण आपल्या गंतव्यावर पोहोचला आहात. आपण जवळील ठिकाणे पाहू इच्छिता की पुढील प्रवासाचे नियोजन करू इच्छिता?"
            }
        }

        pose_map = {
            AuraJourneyStage.WELCOME: AuraPose.WAVING,
            AuraJourneyStage.START_INPUT: AuraPose.POINTING,
            AuraJourneyStage.START_CONFIRMED: AuraPose.TALKING,
            AuraJourneyStage.DEST_INPUT: AuraPose.POINTING,
            AuraJourneyStage.DEST_CONFIRMED: AuraPose.THINKING,
            AuraJourneyStage.MODE_SELECT: AuraPose.POINTING,
            AuraJourneyStage.ALTERNATIVES_READY: AuraPose.TALKING,
            AuraJourneyStage.ROUTE_OVERVIEW: AuraPose.THINKING,
            AuraJourneyStage.JOURNEY_CONFIRMED: AuraPose.WAVING,
            AuraJourneyStage.NAVIGATING: AuraPose.TALKING,
            AuraJourneyStage.MANEUVER_APPROACHING: AuraPose.POINTING,
            AuraJourneyStage.LANDMARK_DISCOVERED: AuraPose.TALKING,
            AuraJourneyStage.OFF_ROUTE: AuraPose.THINKING,
            AuraJourneyStage.NEAR_DESTINATION: AuraPose.TALKING,
            AuraJourneyStage.ARRIVED: AuraPose.EXCITED
        }

        stage_dict = MULTILINGUAL_SPEECH.get(stage, {})
        speech_text = stage_dict.get(clean_lang) or stage_dict.get("en")
        if not speech_text:
            if stage == AuraJourneyStage.MANEUVER_APPROACHING:
                next_turn = ctx.get("next_turn", "the upcoming junction")
                speech_text = f"Approaching {next_turn}. Stay alert."
            elif stage == AuraJourneyStage.LANDMARK_DISCOVERED:
                lm = ctx.get("landmark_name", "a sight")
                speech_text = f"Landmark nearby: {lm}!"
            elif stage == AuraJourneyStage.OFF_ROUTE:
                speech_text = "You are off the planned route! Recalculating the optimal path."
            elif stage == AuraJourneyStage.NEAR_DESTINATION:
                speech_text = f"Destination {dest} is just ahead!"
            else:
                speech_text = "Guiding you safely along your journey."

        return (speech_text, pose_map.get(stage, AuraPose.TALKING))


class ManeuverSequenceBuilder:
    """Builds the complete ordered sequence of maneuvers from actual route data."""

    @staticmethod
    def build_sequence(
        steps: List[Any],
        origin_label: str,
        dest_label: str,
        total_distance_m: float,
        travel_mode: str = "car",
        language: Optional[str] = "en"
    ) -> List[AuraManeuverStep]:
        curr_l = (language or "en").lower().split("-")[0]
        clean_orig = origin_label.split(",")[0].strip() or "Departure Point"
        clean_dest = dest_label.split(",")[0].strip() or "Destination"

        if not steps or len(steps) < 2:
            # Fallback when provider returns empty steps list
            try:
                from src.i18n import t
            except ImportError:
                def t(k, **kw): return kw.get("default", k)

            h1 = f"{clean_orig} నుండి ప్రారంభించండి" if curr_l == "te" else (f"{clean_orig} से प्रस्थान करें" if curr_l == "hi" else f"Depart from {clean_orig}")
            h2 = "కనెక్టింగ్ హైవే వెంట కొనసాగండి" if curr_l == "te" else ("कनेक्टिंग हाईवे पर आगे बढ़ें" if curr_l == "hi" else "Continue along Connecting Highway")
            h3 = f"{clean_dest} వద్దకు సురక్షితంగా చేరుకోండి" if curr_l == "te" else (f"{clean_dest} पर सुरक्षित पहुंचे" if curr_l == "hi" else f"Arrive safely at {clean_dest}")

            return [
                AuraManeuverStep(
                    step_num=1,
                    total_steps=3,
                    direction_type="START",
                    headline=h1,
                    instruction=f"{clean_orig} -> {clean_dest}",
                    spoken_text=h1,
                    aura_speech=h1,
                    road_name="Departure Access Corridor",
                    distance_m=round(total_distance_m * 0.15, 1),
                    distance_human=f"{round(total_distance_m * 0.15 / 1000.0, 1)} km",
                    time_estimate="2 mins",
                    icon="🟢",
                    aura_pose=AuraPose.WAVING,
                    what_to_look_for="Access corridor",
                    status="ACTIVE"
                ),
                AuraManeuverStep(
                    step_num=2,
                    total_steps=3,
                    direction_type="STRAIGHT",
                    headline=h2,
                    instruction=h2,
                    spoken_text=h2,
                    aura_speech=h2,
                    road_name="Main Regional Highway",
                    distance_m=round(total_distance_m * 0.70, 1),
                    distance_human=f"{round(total_distance_m * 0.70 / 1000.0, 1)} km",
                    time_estimate="6 mins",
                    icon="⬆️",
                    aura_pose=AuraPose.TALKING,
                    what_to_look_for="Main corridor",
                    status="UPCOMING"
                ),
                AuraManeuverStep(
                    step_num=3,
                    total_steps=3,
                    direction_type="ARRIVE",
                    headline=h3,
                    instruction=h3,
                    spoken_text=h3,
                    aura_speech=h3,
                    road_name="Arrival Plaza Drive",
                    distance_m=round(total_distance_m * 0.15, 1),
                    distance_human="150 m",
                    time_estimate="1 min",
                    icon="🏁",
                    aura_pose=AuraPose.EXCITED,
                    what_to_look_for="Destination arrival",
                    status="UPCOMING"
                )
            ]

        maneuvers: List[AuraManeuverStep] = []
        total_count = len(steps)

        for idx, s in enumerate(steps):
            step_no = idx + 1
            road = ""
            instruction = ""
            distance_m = 0.0

            # Handle object, dict, or dataclass instances (including FriendlyTurnStep)
            if isinstance(s, dict):
                road = s.get("road") or s.get("road_name") or "Regional Corridor"
                action_headline = s.get("action_headline")
                instruction = s.get("instruction") or action_headline or f"Continue along {road}"
                distance_m = float(s.get("distance_m", 0.0) or s.get("distance_meters", 0.0) or s.get("distance", 0.0))
                dir_type = s.get("direction_type") or s.get("type") or "STRAIGHT"
                icon = s.get("icon") or "⬆️"
                aura_speech_in = s.get("virtual_guide_speech") or s.get("spoken_text")
                look_for_in = s.get("what_to_look_for")
                dist_human_in = s.get("distance_human")
                time_est_in = s.get("time_estimate")
            else:
                road = getattr(s, "road_name", None) or getattr(s, "road", "Regional Corridor")
                action_headline = getattr(s, "action_headline", None)
                instruction = getattr(s, "instruction", None) or action_headline or f"Continue along {road}"
                distance_m = float(getattr(s, "distance_meters", 0.0) or getattr(s, "distance_m", 0.0) or getattr(s, "distance", 0.0))
                dir_type = getattr(s, "direction_type", None) or getattr(s, "type", "STRAIGHT")
                icon = getattr(s, "icon", "⬆️")
                aura_speech_in = getattr(s, "virtual_guide_speech", None) or getattr(s, "spoken_text", None)
                look_for_in = getattr(s, "what_to_look_for", None)
                dist_human_in = getattr(s, "distance_human", None)
                time_est_in = getattr(s, "time_estimate", None)

            # Combined analysis of direction, headline, and instruction text
            dir_str = str(dir_type).upper()
            action_head_str = str(action_headline or "").upper()
            instr_str = str(instruction or "").upper()
            combined_desc = f"{dir_str} {action_head_str} {instr_str}"

            exit_num = s.get("exit") if isinstance(s, dict) else getattr(s, "exit", None)
            pose = AuraPose.TALKING

            if step_no == 1 or "START" in combined_desc or "DEPART" in combined_desc:
                dir_upper = "START"
                icon = "🟢"
                pose = AuraPose.WAVING
                headline = action_headline or f"Depart from {clean_orig}"
                aura_msg = aura_speech_in or f"Ready to roll! We're departing {clean_orig}. Follow my lead!"
            elif step_no == total_count or "ARRIV" in combined_desc or "DEST" in combined_desc:
                dir_upper = "ARRIVE"
                icon = "🏁" if not icon or icon == "⬆️" else icon
                pose = AuraPose.EXCITED
                headline = action_headline or f"Arrive safely at {clean_dest}"
                aura_msg = aura_speech_in or f"We've arrived at {clean_dest}! Awesome travel adventure!"
            elif "ROUNDABOUT" in combined_desc:
                dir_upper = "ROUNDABOUT"
                icon = "🔄"
                pose = AuraPose.POINTING
                exit_str = f"take exit {exit_num} onto " if exit_num else "onto "
                headline = action_headline or f"Enter Roundabout and {exit_str}{road}"
                aura_msg = aura_speech_in or f"Entering roundabout. Yield to traffic and take exit {exit_num or 1} toward {road}."
            elif "KEEP" in combined_desc and "RIGHT" in combined_desc:
                dir_upper = "KEEP_RIGHT"
                icon = "↗️"
                pose = AuraPose.POINTING
                headline = action_headline or f"Keep Right toward {road}"
                aura_msg = aura_speech_in or f"Keep right along {road}."
            elif "KEEP" in combined_desc and "LEFT" in combined_desc:
                dir_upper = "KEEP_LEFT"
                icon = "↖️"
                pose = AuraPose.POINTING
                headline = action_headline or f"Keep Left toward {road}"
                aura_msg = aura_speech_in or f"Keep left along {road}."
            elif "LEFT" in combined_desc:
                dir_upper = "TURN_LEFT"
                icon = "⬅️"
                pose = AuraPose.POINTING
                headline = action_headline or f"Turn Left onto {road}"
                aura_msg = aura_speech_in or f"Prepare to turn left onto {road}. Signal early and check mirrors."
            elif "RIGHT" in combined_desc:
                dir_upper = "TURN_RIGHT"
                icon = "➡️"
                pose = AuraPose.POINTING
                headline = action_headline or f"Turn Right onto {road}"
                aura_msg = aura_speech_in or f"Approaching a right turn onto {road}. Keep to the right side of the road."
            elif "MERGE" in combined_desc:
                dir_upper = "MERGE"
                icon = "🔀"
                pose = AuraPose.POINTING
                headline = action_headline or f"Merge onto {road}"
                aura_msg = aura_speech_in or f"Merge smoothly onto {road} matching corridor speed."
            elif "FOLLOW" in combined_desc or "PROCEED" in combined_desc:
                dir_upper = "PROCEED"
                icon = "🧭" if not icon or icon == "⬆️" else icon
                pose = AuraPose.TALKING
                headline = action_headline or f"Follow {road}"
                aura_msg = aura_speech_in or f"Follow along {road}. Stay steady on course."
            else:
                dir_upper = "STRAIGHT"
                icon = "⬆️"
                pose = AuraPose.TALKING
                headline = action_headline or f"Proceed Straight on {road}"
                aura_msg = aura_speech_in or f"Cruising along {road}. The path is clear."

            dist_human = dist_human_in if dist_human_in else (f"{round(distance_m / 1000.0, 1)} km" if distance_m >= 1000.0 else f"{int(distance_m)} m")
            mins = max(1, round(distance_m / 450.0)) if "walk" in travel_mode.lower() else max(1, round(distance_m / 800.0))
            time_est = time_est_in if time_est_in else f"{mins} min{'s' if mins > 1 else ''}"
            look_for = look_for_in or f"Signposts for {road} and clear pedestrian markings."

            maneuvers.append(AuraManeuverStep(
                step_num=step_no,
                total_steps=total_count,
                direction_type=dir_upper,
                headline=headline,
                instruction=instruction,
                spoken_text=f"Step {step_no}: {headline}. {instruction}",
                aura_speech=aura_msg,
                road_name=road,
                distance_m=distance_m,
                distance_human=dist_human,
                time_estimate=time_est,
                icon=icon,
                aura_pose=pose,
                what_to_look_for=look_for,
                accessible_guidance="Step-free pathway with audible signal crosswalk.",
                roundabout_exit=int(exit_num) if exit_num else None,
                status="ACTIVE" if step_no == 1 else "UPCOMING"
            ))

        return maneuvers


def build_aura_journey_cockpit_html(
    origin_name: str,
    dest_name: str,
    travel_mode: str,
    total_distance_km: float,
    total_duration_mins: float,
    maneuvers: List[AuraManeuverStep],
    current_step_idx: int = 0,
    aura_stage: str = "NAVIGATING",
    aura_thought: str = "Our adventure is underway! Following the mapped corridor safely.",
    is_live_moving: bool = False,
    user_speed_kmh: float = 0.0,
    camera_mode: str = "drone",  # pov, drone, iso
    env_lighting: str = "day",   # day, sunset, night
    lang: Optional[str] = None
) -> str:
    """
    Renders the complete high-fidelity Aura 3D / 2.5D Journey Cockpit HTML5/CSS3/JavaScript.
    Features:
    - Aura's animated Robot Mascot with glowing navigation stick & speech bubble
    - Dynamic Route Journey Pipeline showing all ordered maneuvers
    - Active maneuver banner with real distance countdown
    - 3D camera switcher (Driver POV, 3D Follow Drone, 3D Isometric Level)
    - Environment lighting switcher (Day, Sunset, Cyber Night)
    - Avatar action controls (Walk, Run, Turn, Jump, Cheer, Wave)
    - Integrated View All Pictures Journey Storybook Modal
    - Live audio synthesizer chime and SpeechSynthesis narration
    """
    from src.i18n import get_current_language, get_bcp47_code, t
    curr_lang = lang or get_current_language()
    bcp47_code = get_bcp47_code(curr_lang)

    STAGE_LOCALIZED = {
        "WELCOME": {"en": "WELCOME", "te": "స్వాగతం", "hi": "स्वागत", "ta": "வரவேற்பு", "kn": "ಸ್ವಾಗತ", "ml": "സ്വാഗതം", "bn": "স্বাগতম", "mr": "स्वागत"},
        "NAVIGATING": {"en": "GUIDING LIVE", "te": "లైవ్ మార్గదర్శనం", "hi": "लाइव मार्गदर्शन", "ta": "நேரடி வழிகாட்டல்", "kn": "ಲೈವ್ ಮಾರ್ಗದರ್ಶನ", "ml": "തത്സമയ വഴികാട്ടൽ", "bn": "লাইভ নির্দেশিকা", "mr": "थेट मार्गदर्शन"},
        "ARRIVED": {"en": "ARRIVED", "te": "చేరుకున్నారు", "hi": "पहुंच गए", "ta": "வந்து சேர்ந்தீர்கள்", "kn": "ತಲುಪಿದೆ", "ml": "എത്തിച്ചേർന്നു", "bn": "পৌঁছে গেছেন", "mr": "पोहोचले"}
    }
    stage_key = str(aura_stage).upper()
    aura_stage_display = STAGE_LOCALIZED.get(stage_key, {}).get(curr_lang, aura_stage)
    poses = AuraPoseAssetManager.load_poses()
    mascot_waving = poses.get("waving", "")
    mascot_pointing = poses.get("pointing", "")
    mascot_excited = poses.get("excited", "")
    mascot_talking = poses.get("talking", "")
    mascot_welcome = poses.get("welcome", "")

    # Clean display strings
    clean_orig = origin_name.split(",")[0].strip() or "Starting Point"
    clean_dest = dest_name.split(",")[0].strip() or "Destination"

    # Real-time local timezone day / sunset / night detection
    from datetime import datetime
    now_dt = datetime.now()
    cur_hour = now_dt.hour + now_dt.minute / 60.0
    if 17.0 <= cur_hour < 19.35:
        auto_detected_env = "sunset"
        time_desc = f"{now_dt.strftime('%I:%M %p')} • Sunset"
    elif 6.0 <= cur_hour < 17.0:
        auto_detected_env = "day"
        time_desc = f"{now_dt.strftime('%I:%M %p')} • Day"
    else:
        auto_detected_env = "night"
        time_desc = f"{now_dt.strftime('%I:%M %p')} • Cyber Night"

    if env_lighting == "day" or not env_lighting:
        env_lighting = auto_detected_env

    # Serialize maneuvers for JavaScript reactivity
    maneuvers_payload = [asdict(m) for m in maneuvers]
    maneuvers_json = json.dumps(maneuvers_payload, default=str)

    active_step = maneuvers[current_step_idx] if 0 <= current_step_idx < len(maneuvers) else maneuvers[0]

    from src.vehicle_navigation_controller import VehicleModeManager
    norm_travel_mode = VehicleModeManager.normalize_mode(travel_mode)
    vehicle_suite_js = VehicleModeManager.generate_threejs_vehicle_suite_js()

    return f"""
    <div id='aura-journey-root' class='aura-journey-shell'>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap');

            html, body {{
                margin: 0 !important;
                padding: 0 !important;
                background: transparent !important;
                overflow-x: hidden !important;
                box-sizing: border-box !important;
            }}

            .aura-journey-shell {{
                font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background: linear-gradient(135deg, #070f1e 0%, #0c1a30 50%, #061022 100%);
                border: 1.5px solid rgba(56, 189, 248, 0.45);
                border-radius: 20px;
                padding: 20px;
                margin: 0 0 10px 0;
                color: #f8fafc;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.85), 0 0 30px rgba(56, 189, 248, 0.15);
                position: relative;
                overflow: visible !important;
                box-sizing: border-box !important;
            }}

            /* Ambient glowing aura rings in background */
            .aura-journey-shell::before {{
                content: '';
                position: absolute;
                top: -80px;
                right: -80px;
                width: 240px;
                height: 240px;
                background: radial-gradient(circle, rgba(56, 189, 248, 0.18) 0%, transparent 70%);
                pointer-events: none;
            }}

            /* Top Stage & Header HUD */
            .aura-header-hud {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 12px;
                padding-bottom: 16px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.12);
            }}

            .aura-brand-group {{
                display: flex;
                align-items: center;
                gap: 14px;
            }}

            .aura-avatar-pod {{
                position: relative;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(56, 189, 248, 0.4) 0%, rgba(15, 23, 42, 0.95) 100%);
                border: 2.5px solid #38bdf8;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 0 20px rgba(56, 189, 248, 0.6);
                cursor: pointer;
                transition: transform 0.3s ease;
            }}
            .aura-avatar-pod:hover {{
                transform: scale(1.08);
            }}
            .aura-avatar-pod img {{
                width: 52px;
                height: 52px;
                object-fit: contain;
                filter: drop-shadow(0 0 6px rgba(56, 189, 248, 0.8));
            }}

            .aura-title-block {{
                display: flex;
                flex-direction: column;
                gap: 2px;
            }}

            .aura-stage-pill {{
                padding: 4px 12px;
                border-radius: 999px;
                font-size: 0.72rem;
                font-weight: 800;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: rgba(16, 185, 129, 0.2);
                color: #34d399;
                border: 1px solid rgba(16, 185, 129, 0.5);
            }}

            /* Interactive Aura Thought Bubble */
            .aura-thought-banner {{
                margin: 14px 0 10px 0;
                background: linear-gradient(90deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.7) 100%);
                border-left: 4px solid #38bdf8;
                border-radius: 12px;
                padding: 12px 18px;
                display: flex;
                align-items: center;
                gap: 14px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
            }}
            .aura-thought-text {{
                font-size: 0.90rem;
                font-weight: 600;
                color: #e2e8f0;
                line-height: 1.4;
                flex: 1;
            }}

            /* Real-Time Sensor Motion & Parallel Movement HUD Ribbon */
            .sensor-motion-hud {{
                margin: 0 0 14px 0;
                background: linear-gradient(90deg, rgba(15, 23, 42, 0.96) 0%, rgba(30, 41, 59, 0.92) 100%);
                border: 1px solid rgba(56, 189, 248, 0.35);
                border-radius: 12px;
                padding: 10px 16px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 12px;
                box-shadow: 0 4px 18px rgba(0, 0, 0, 0.45);
                flex-wrap: wrap;
            }}
            .sensor-motion-left, .sensor-motion-right {{
                display: flex;
                align-items: center;
                gap: 10px;
                flex-wrap: wrap;
            }}
            .sensor-status-badge {{
                display: inline-flex;
                align-items: center;
                gap: 7px;
                padding: 4px 11px;
                border-radius: 999px;
                font-size: 0.72rem;
                font-weight: 800;
                letter-spacing: 0.05em;
                background: rgba(100, 116, 139, 0.2);
                color: #94a3b8;
                border: 1px solid rgba(148, 163, 184, 0.4);
                transition: all 0.3s ease;
            }}
            .sensor-status-badge.moving {{
                background: rgba(16, 185, 129, 0.22);
                color: #34d399;
                border-color: rgba(16, 185, 129, 0.6);
                box-shadow: 0 0 12px rgba(16, 185, 129, 0.35);
            }}
            .sensor-status-badge.stationary {{
                background: rgba(245, 158, 11, 0.2);
                color: #fbbf24;
                border-color: rgba(245, 158, 11, 0.5);
            }}
            .sensor-status-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #94a3b8;
            }}
            .sensor-status-badge.moving .sensor-status-dot {{
                background: #10b981;
                box-shadow: 0 0 8px #10b981;
                animation: pulseSensorDot 1.4s infinite;
            }}
            .sensor-status-badge.stationary .sensor-status-dot {{
                background: #f59e0b;
            }}
            @keyframes pulseSensorDot {{
                0% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.35; transform: scale(1.3); }}
                100% {{ opacity: 1; transform: scale(1); }}
            }}
            .sensor-metric-chip {{
                display: inline-flex;
                align-items: center;
                gap: 5px;
                padding: 4px 10px;
                border-radius: 8px;
                background: rgba(15, 23, 42, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                font-size: 0.75rem;
            }}
            .sensor-step-countdown {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 4px 12px;
                border-radius: 8px;
                background: rgba(8, 47, 73, 0.6);
                border: 1px solid rgba(56, 189, 248, 0.35);
                font-size: 0.75rem;
            }}

            /* Dynamic Route Journey Pipeline (Horizontal Scroll) */
            .journey-pipeline-section {{
                margin: 16px 0;
            }}
            .pipeline-label-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.74rem;
                font-weight: 800;
                color: #94a3b8;
                letter-spacing: 0.05em;
                margin-bottom: 8px;
            }}
            .pipeline-track {{
                display: flex;
                gap: 10px;
                overflow-x: auto;
                padding: 6px 2px 12px 2px;
                scrollbar-width: thin;
                scrollbar-color: #38bdf8 rgba(15, 23, 42, 0.8);
            }}
            .pipeline-step-card {{
                flex: 0 0 195px;
                min-width: 195px;
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.92) 0%, rgba(10, 18, 36, 0.98) 100%);
                border: 1.5px solid rgba(255, 255, 255, 0.12);
                border-radius: 14px;
                padding: 0;
                cursor: pointer;
                transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45);
            }}
            .pipeline-step-card:hover {{
                border-color: #38bdf8;
                transform: translateY(-4px);
                box-shadow: 0 12px 28px rgba(56, 189, 248, 0.35);
            }}
            .pipeline-step-card.active {{
                border-color: #38bdf8;
                background: linear-gradient(180deg, rgba(2, 132, 199, 0.35) 0%, rgba(15, 23, 42, 0.98) 100%);
                box-shadow: 0 0 22px rgba(56, 189, 248, 0.6), 0 8px 24px rgba(0, 0, 0, 0.6);
            }}
            .pipeline-step-card.completed {{
                border-color: #10b981;
                background: linear-gradient(180deg, rgba(6, 78, 59, 0.35) 0%, rgba(15, 23, 42, 0.98) 100%);
                box-shadow: 0 0 16px rgba(16, 185, 129, 0.4);
            }}
            .step-picture-frame {{
                position: relative;
                width: 100%;
                height: 92px;
                overflow: hidden;
                background: #0f172a;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            }}
            .step-picture-frame svg {{
                transition: transform 0.4s ease;
            }}
            .pipeline-step-card:hover .step-picture-frame svg {{
                transform: scale(1.05);
            }}
            .step-pic-overlay-badge {{
                position: absolute;
                top: 6px;
                left: 6px;
                right: 6px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                pointer-events: none;
            }}
            .step-num-pill {{
                background: rgba(15, 23, 42, 0.85);
                backdrop-filter: blur(4px);
                border: 1px solid rgba(56, 189, 248, 0.6);
                color: #38bdf8;
                font-size: 0.68rem;
                font-weight: 800;
                padding: 2px 7px;
                border-radius: 999px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.5);
            }}
            .pipeline-step-card.active .step-num-pill {{
                background: #0284c7;
                color: #ffffff;
                border-color: #38bdf8;
                box-shadow: 0 0 10px #38bdf8;
            }}
            .pipeline-step-card.completed .step-num-pill {{
                background: #059669;
                color: #ffffff;
                border-color: #34d399;
            }}
            .step-icon-badge {{
                font-size: 1.05rem;
                filter: drop-shadow(0 2px 4px rgba(0,0,0,0.6));
            }}
            .step-card-body {{
                padding: 8px 10px 10px 10px;
                display: flex;
                flex-direction: column;
                gap: 3px;
                flex: 1;
                justify-content: space-between;
            }}
            .step-card-headline {{
                font-size: 0.78rem;
                font-weight: 700;
                color: #f1f5f9;
                line-height: 1.3;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
                overflow: hidden;
                min-height: 2.1em;
            }}
            .pipeline-step-card.active .step-card-headline {{
                color: #38bdf8;
            }}
            .pipeline-step-card.completed .step-card-headline {{
                color: #6ee7b7;
            }}
            .step-card-footer {{
                font-size: 0.67rem;
                color: #94a3b8;
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 4px;
                padding-top: 4px;
                border-top: 1px solid rgba(255, 255, 255, 0.06);
            }}
            .step-card-road {{
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 110px;
            }}
            .step-card-dist {{
                color: #38bdf8;
                font-weight: 800;
            }}

            /* Active Turn-by-Turn Card */
            .active-maneuver-stage {{
                background: rgba(15, 23, 42, 0.8);
                border: 2px solid #38bdf8;
                border-radius: 16px;
                padding: 18px;
                margin: 14px 0;
                display: flex;
                align-items: center;
                gap: 18px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
            }}
            .maneuver-big-icon {{
                width: 64px;
                height: 64px;
                border-radius: 14px;
                background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.2rem;
                box-shadow: 0 0 16px rgba(56, 189, 248, 0.6);
            }}
            .maneuver-details {{
                flex: 1;
            }}
            .maneuver-headline {{
                font-size: 1.15rem;
                font-weight: 800;
                color: #ffffff;
            }}
            .maneuver-sub {{
                font-size: 0.85rem;
                color: #94a3b8;
                margin-top: 4px;
            }}
            .maneuver-dist-badge {{
                font-size: 1.6rem;
                font-weight: 900;
                color: #34d399;
                font-family: 'JetBrains Mono', monospace;
                text-align: right;
            }}

            /* 3D Scene Viewport */
            .aura-3d-scene-container {{
                position: relative;
                width: 100%;
                height: 360px;
                border-radius: 14px;
                overflow: hidden;
                margin: 14px 0;
                border: 1.5px solid rgba(56, 189, 248, 0.4);
                box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.85), 0 8px 24px rgba(0, 0, 0, 0.5);
                background: radial-gradient(circle at 50% 30%, #1e40af 0%, #030712 100%);
            }}
            #aura-threejs-canvas, #aura-scenic-canvas {{
                width: 100%;
                height: 100%;
                position: absolute;
                top: 0;
                left: 0;
            }}
            .scene-hud-overlay {{
                position: absolute;
                top: 10px;
                left: 14px;
                display: flex;
                gap: 8px;
                pointer-events: none;
                z-index: 10;
            }}
            .scene-badge {{
                background: rgba(15, 23, 42, 0.85);
                border: 1px solid rgba(16, 185, 129, 0.5);
                color: #34d399;
                font-size: 0.68rem;
                font-weight: 800;
                padding: 3px 8px;
                border-radius: 6px;
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            .scene-cam-badge {{
                background: rgba(15, 23, 42, 0.85);
                border: 1px solid rgba(56, 189, 248, 0.4);
                color: #38bdf8;
                font-size: 0.68rem;
                font-weight: 800;
                padding: 3px 8px;
                border-radius: 6px;
            }}
            .pulse-dot {{
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: #34d399;
                box-shadow: 0 0 8px #34d399;
            }}

            /* Action Buttons & 3D Controls */
            .controls-toolbar {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 14px;
                padding-top: 14px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .btn-action-pill {{
                background: rgba(30, 41, 59, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 999px;
                padding: 6px 14px;
                font-size: 0.78rem;
                font-weight: 700;
                color: #f1f5f9;
                cursor: pointer;
                transition: all 0.2s ease;
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }}
            .btn-action-pill:hover {{
                background: rgba(56, 189, 248, 0.25);
                border-color: #38bdf8;
                color: #38bdf8;
            }}
            .btn-action-pill.active {{
                background: #0284c7;
                border-color: #38bdf8;
                color: #ffffff;
                box-shadow: 0 0 12px rgba(56, 189, 248, 0.5);
            }}

            /* View All Pictures Route Storyline Modal */
            .gallery-modal-overlay {{
                display: none;
                position: fixed;
                inset: 0;
                background: rgba(3, 7, 18, 0.92);
                backdrop-filter: blur(12px);
                z-index: 99999;
                align-items: center;
                justify-content: center;
                padding: 16px;
            }}
            .gallery-modal-card {{
                background: linear-gradient(135deg, #070f1e 0%, #0b172a 50%, #050b16 100%);
                border: 2px solid #38bdf8;
                border-radius: 22px;
                width: 95%;
                max-width: 1080px;
                max-height: 90vh;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                box-shadow: 0 28px 72px rgba(0, 0, 0, 0.95), 0 0 50px rgba(56, 189, 248, 0.3);
            }}
            .gallery-header {{
                padding: 16px 24px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: rgba(15, 23, 42, 0.88);
                border-bottom: 1.5px solid rgba(56, 189, 248, 0.25);
                gap: 14px;
                flex-wrap: wrap;
            }}
            .gallery-scroll-container {{
                flex: 1;
                overflow-y: auto;
                padding: 20px 24px 32px 24px;
                scroll-behavior: smooth;
            }}
            .gallery-scroll-container::-webkit-scrollbar {{
                width: 8px;
            }}
            .gallery-scroll-container::-webkit-scrollbar-track {{
                background: rgba(15, 23, 42, 0.6);
            }}
            .gallery-scroll-container::-webkit-scrollbar-thumb {{
                background: #0284c7;
                border-radius: 4px;
            }}
            /* Connected Storyline Stream */
            .storyline-stream {{
                display: flex;
                flex-direction: column;
                align-items: center;
                max-width: 840px;
                margin: 0 auto;
                width: 100%;
            }}
            .storyline-scene-card {{
                width: 100%;
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.96) 0%, rgba(9, 15, 30, 0.98) 100%);
                border: 2px solid rgba(255, 255, 255, 0.12);
                border-radius: 18px;
                overflow: hidden;
                box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
            }}
            .storyline-scene-card:hover {{
                border-color: #38bdf8;
                box-shadow: 0 16px 40px rgba(56, 189, 248, 0.28);
                transform: translateY(-2px);
            }}
            .storyline-scene-card.active {{
                border-color: #38bdf8;
                box-shadow: 0 0 32px rgba(56, 189, 248, 0.55), 0 12px 36px rgba(0, 0, 0, 0.8);
            }}
            .storyline-scene-card.completed {{
                border-color: rgba(52, 211, 153, 0.4);
            }}
            .storyline-scene-header {{
                padding: 12px 18px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: rgba(15, 23, 42, 0.85);
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                gap: 10px;
                flex-wrap: wrap;
            }}
            .scene-chapter-badge {{
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 0.80rem;
                font-weight: 800;
                color: #38bdf8;
                letter-spacing: 0.04em;
            }}
            .scene-metrics-badges {{
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .scene-pill-dist {{
                font-size: 0.72rem;
                font-weight: 800;
                color: #34d399;
                background: rgba(16, 185, 129, 0.16);
                border: 1px solid rgba(16, 185, 129, 0.35);
                padding: 3px 9px;
                border-radius: 999px;
            }}
            .scene-pill-time {{
                font-size: 0.72rem;
                font-weight: 700;
                color: #94a3b8;
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 3px 9px;
                border-radius: 999px;
            }}
            .scene-status-pill {{
                font-size: 0.70rem;
                font-weight: 800;
                padding: 3px 8px;
                border-radius: 999px;
            }}
            .scene-status-pill.active {{
                background: #0284c7;
                color: #ffffff;
                box-shadow: 0 0 10px rgba(56, 189, 248, 0.6);
            }}
            .scene-status-pill.completed {{
                background: rgba(16, 185, 129, 0.2);
                color: #34d399;
                border: 1px solid #10b981;
            }}
            .scene-status-pill.upcoming {{
                background: rgba(148, 163, 184, 0.15);
                color: #94a3b8;
                border: 1px solid rgba(148, 163, 184, 0.3);
            }}
            .storyline-pic-hero {{
                width: 100%;
                height: 180px;
                position: relative;
                overflow: hidden;
                background: #070f1e;
                cursor: pointer;
            }}
            .storyline-pic-hero svg {{
                width: 100%;
                height: 100%;
                display: block;
                transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }}
            .storyline-scene-card:hover .storyline-pic-hero svg {{
                transform: scale(1.03);
            }}
            .storyline-pic-overlay {{
                position: absolute;
                bottom: 10px;
                left: 12px;
                right: 12px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                pointer-events: none;
            }}
            .pic-road-pill {{
                background: rgba(15, 23, 42, 0.88);
                backdrop-filter: blur(6px);
                border: 1px solid #38bdf8;
                padding: 4px 12px;
                border-radius: 999px;
                font-size: 0.76rem;
                font-weight: 800;
                color: #e0f2fe;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
            }}
            .pic-jump-hint {{
                background: rgba(2, 132, 199, 0.88);
                backdrop-filter: blur(6px);
                border: 1px solid #7dd3fc;
                padding: 4px 10px;
                border-radius: 999px;
                font-size: 0.70rem;
                font-weight: 800;
                color: #ffffff;
                box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
            }}
            .storyline-narrative-box {{
                padding: 14px 18px;
                display: flex;
                flex-direction: column;
                gap: 8px;
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.4) 0%, rgba(10, 18, 36, 0.8) 100%);
            }}
            .storyline-headline {{
                font-size: 1.05rem;
                font-weight: 800;
                color: #ffffff;
                line-height: 1.35;
            }}
            .storyline-chronicle-text {{
                font-size: 0.82rem;
                color: #cbd5e1;
                line-height: 1.5;
            }}
            .storyline-landmark-strip {{
                display: flex;
                align-items: center;
                gap: 8px;
                background: rgba(56, 189, 248, 0.08);
                border-left: 3px solid #38bdf8;
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 0.76rem;
            }}
            .storyline-action-row {{
                padding: 0 18px 14px 18px;
                display: flex;
                justify-content: flex-end;
            }}
            .storyline-action-row .jump-btn {{
                background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
                border: none;
                color: #ffffff;
                font-weight: 800;
                padding: 6px 14px;
                box-shadow: 0 4px 14px rgba(56, 189, 248, 0.35);
            }}
            /* Connecting Storyline Ribbon */
            .storyline-connector-segment {{
                display: flex;
                flex-direction: column;
                align-items: center;
                margin: 8px 0;
                position: relative;
                width: 100%;
            }}
            .storyline-connector-line {{
                width: 3px;
                height: 22px;
                background: linear-gradient(180deg, #38bdf8 0%, rgba(56, 189, 248, 0.2) 100%);
            }}
            .storyline-connector-ribbon {{
                display: flex;
                align-items: center;
                gap: 10px;
                background: rgba(15, 23, 42, 0.95);
                border: 1.5px solid rgba(56, 189, 248, 0.45);
                padding: 6px 16px;
                border-radius: 999px;
                box-shadow: 0 0 16px rgba(56, 189, 248, 0.25);
            }}
            .connector-arrow {{
                font-size: 0.85rem;
                color: #38bdf8;
                font-weight: 900;
                animation: connectorPulse 1.6s infinite ease-in-out;
            }}
            .connector-badge {{
                font-size: 0.72rem;
                font-weight: 800;
                color: #bae6fd;
                letter-spacing: 0.04em;
                display: flex;
                align-items: center;
                gap: 6px;
            }}
            @keyframes connectorPulse {{
                0%, 100% {{ transform: translateY(0); opacity: 0.6; }}
                50% {{ transform: translateY(3px); opacity: 1; }}
            }}
            /* Grid View */
            .storyline-grid-container {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
                gap: 20px;
                width: 100%;
            }}

            /* =========================================================================
               MOBILE-FIRST RESPONSIVE ENGINE (ALL SMARTPHONES, FOLDABLES & TABLETS)
               Supports: Ultra-compact (320px–375px), Standard (376px–480px), Phablets (481px–768px)
               ========================================================================= */
            @media (max-width: 768px) {{
                .aura-journey-shell {{
                    padding: 10px 10px 14px 10px !important;
                    border-radius: 16px !important;
                    margin: 0 0 10px 0 !important;
                    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.75) !important;
                    box-sizing: border-box !important;
                    width: 100% !important;
                }}

                .aura-header-hud {{
                    flex-direction: column !important;
                    align-items: stretch !important;
                    gap: 10px !important;
                    padding-bottom: 10px !important;
                }}

                .aura-brand-group {{
                    justify-content: flex-start !important;
                    gap: 10px !important;
                    width: 100% !important;
                }}

                .aura-avatar-pod {{
                    width: 46px !important;
                    height: 46px !important;
                    min-width: 46px !important;
                }}
                .aura-avatar-pod img {{
                    width: 38px !important;
                    height: 38px !important;
                }}

                .aura-title-block {{
                    flex: 1 !important;
                    min-width: 0 !important;
                }}

                .aura-header-hud > div:last-child {{
                    display: flex !important;
                    flex-wrap: wrap !important;
                    gap: 6px !important;
                    justify-content: flex-start !important;
                    width: 100% !important;
                }}

                #cockpit-lang-select {{
                    flex: 1 1 auto !important;
                    min-width: 100px !important;
                    height: 36px !important;
                    font-size: 0.70rem !important;
                }}

                .aura-thought-banner {{
                    margin: 8px 0 !important;
                    padding: 8px 12px !important;
                    gap: 8px !important;
                    border-radius: 10px !important;
                }}
                .aura-thought-text {{
                    font-size: 0.78rem !important;
                    line-height: 1.35 !important;
                }}

                .sensor-motion-hud {{
                    flex-direction: column !important;
                    align-items: stretch !important;
                    gap: 8px !important;
                    padding: 8px 10px !important;
                    margin-bottom: 10px !important;
                }}
                .sensor-motion-left, .sensor-motion-right {{
                    width: 100% !important;
                    justify-content: space-between !important;
                }}

                .pipeline-track {{
                    padding: 4px 2px 8px 2px !important;
                    gap: 8px !important;
                    -webkit-overflow-scrolling: touch !important;
                    scroll-snap-type: x mandatory !important;
                }}
                .pipeline-step-card {{
                    flex: 0 0 150px !important;
                    min-width: 150px !important;
                    scroll-snap-align: start !important;
                    border-radius: 12px !important;
                }}
                .step-picture-frame {{
                    height: 72px !important;
                }}

                .active-maneuver-stage {{
                    padding: 10px 12px !important;
                    gap: 10px !important;
                    margin: 8px 0 !important;
                    border-radius: 12px !important;
                }}
                .maneuver-big-icon {{
                    width: 44px !important;
                    height: 44px !important;
                    min-width: 44px !important;
                    font-size: 1.5rem !important;
                    border-radius: 10px !important;
                }}
                .maneuver-headline {{
                    font-size: 0.90rem !important;
                    line-height: 1.2 !important;
                }}
                .maneuver-sub {{
                    font-size: 0.72rem !important;
                }}
                .maneuver-dist-badge {{
                    font-size: 1.20rem !important;
                }}

                .aura-3d-scene-container {{
                    height: clamp(200px, 34vh, 280px) !important;
                    margin: 8px 0 !important;
                    border-radius: 12px !important;
                }}

                .scene-hud-overlay {{
                    top: 6px !important;
                    left: 6px !important;
                    right: 6px !important;
                    flex-wrap: wrap !important;
                    gap: 4px !important;
                }}
                .scene-badge, .scene-cam-badge {{
                    font-size: 0.58rem !important;
                    padding: 2px 5px !important;
                }}

                .controls-toolbar {{
                    gap: 8px !important;
                    padding-top: 8px !important;
                    margin-top: 8px !important;
                }}

                .btn-action-pill {{
                    min-height: 38px !important;
                    padding: 4px 10px !important;
                    font-size: 0.72rem !important;
                    touch-action: manipulation !important;
                    -webkit-tap-highlight-color: transparent !important;
                }}

                /* Horizontal Swipeable Vehicle Mode Carousel on Mobile */
                .controls-toolbar > div:first-child {{
                    overflow-x: auto !important;
                    white-space: nowrap !important;
                    flex-wrap: nowrap !important;
                    -webkit-overflow-scrolling: touch !important;
                    padding-bottom: 6px !important;
                    scrollbar-width: thin !important;
                    gap: 5px !important;
                }}
                .btn-veh-selector {{
                    flex: 0 0 auto !important;
                    min-height: 36px !important;
                    padding: 4px 9px !important;
                    font-size: 0.70rem !important;
                }}
            }}

            @media (max-width: 375px) {{
                .aura-journey-shell {{
                    padding: 8px 6px 10px 6px !important;
                    border-radius: 12px !important;
                }}
                .pipeline-step-card {{
                    flex: 0 0 135px !important;
                    min-width: 135px !important;
                }}
                .maneuver-headline {{
                    font-size: 0.84rem !important;
                }}
                .maneuver-dist-badge {{
                    font-size: 1.05rem !important;
                }}
                .btn-action-pill {{
                    font-size: 0.68rem !important;
                    padding: 3px 8px !important;
                }}
            }}
        </style>

        <!-- Top Header & Brand -->
        <div class='aura-header-hud'>
            <div class='aura-brand-group'>
                <div class='aura-avatar-pod' onclick='triggerAuraAction("wave")' title='Click Aura to Wave!'>
                    <img id='aura-pod-img' src='{mascot_waving or mascot_welcome}' alt='Aura 3D Companion' />
                </div>
                <div class='aura-title-block'>
                    <div style='font-size: 1.05rem; font-weight: 900; color: #ffffff; display: flex; align-items: center; gap: 8px;'>
                        <span>{t('companion.cockpit_title', default='AURA • 3D JOURNEY COMPANION', lang=curr_lang)}</span>
                        <span class='aura-stage-pill'>● {aura_stage_display}</span>
                    </div>
                    <div style='font-size: 0.78rem; color: #94a3b8;'>
                        {t('companion.guiding_from_to', default=f'Guiding from {clean_orig} to {clean_dest} ({total_distance_km:.1f} km • ~{int(total_duration_mins)} min)', orig=clean_orig, dest=clean_dest, dist=f'{total_distance_km:.1f} km', time=f'{int(total_duration_mins)} min', lang=curr_lang)}
                    </div>
                </div>
            </div>

            <!-- Header Quick Actions + Direct Language Selector -->
            <div style='display: flex; gap: 8px; align-items: center; flex-wrap: wrap;'>
                <select id='cockpit-lang-select' onchange='handleCockpitLangChange(this.value)' style='background: rgba(15, 23, 42, 0.85); color: #38bdf8; border: 1.5px solid rgba(56, 189, 248, 0.5); border-radius: 20px; padding: 4px 10px; font-size: 0.74rem; font-weight: 800; cursor: pointer; outline: none; box-shadow: 0 0 10px rgba(56, 189, 248, 0.2);'>
                    <option value="en" {"selected" if curr_lang=="en" else ""}>🌐 English</option>
                    <option value="te" {"selected" if curr_lang=="te" else ""}>తెలుగు</option>
                    <option value="hi" {"selected" if curr_lang=="hi" else ""}>हिन्दी</option>
                    <option value="ta" {"selected" if curr_lang=="ta" else ""}>தமிழ்</option>
                    <option value="kn" {"selected" if curr_lang=="kn" else ""}>ಕನ್ನಡ</option>
                    <option value="ml" {"selected" if curr_lang=="ml" else ""}>മലയാളം</option>
                    <option value="bn" {"selected" if curr_lang=="bn" else ""}>বাংলা</option>
                    <option value="mr" {"selected" if curr_lang=="mr" else ""}>मराठी</option>
                </select>
                <button class='btn-action-pill' onclick='toggleVoiceAudio()'>
                    <span id='audio-icon'>🔊</span> <span id='audio-text'>{t('companion.voice_on', default='Voice: On', lang=curr_lang)}</span>
                </button>
                <button class='btn-action-pill' onclick='openPicturesGallery()'>
                    <span>🖼️</span> <span>{t('companion.view_pictures', default='View All Pictures', lang=curr_lang)}</span>
                </button>
            </div>
        </div>

        <!-- Aura Speech / Thoughts Banner -->
        <div class='aura-thought-banner'>
            <div style='font-size: 1.8rem;'>🤖</div>
            <div class='aura-thought-text' id='aura-thought-box'>
                <span style='color: #38bdf8; font-weight: 800;'>{t('companion.aura_says', default='Aura says:', lang=curr_lang)} </span>
                <span id='aura-speech-content'>{aura_thought}</span>
            </div>
        </div>

        <!-- Real-Time User Sensor Motion & Parallel Guide HUD Ribbon -->
        <div class='sensor-motion-hud' id='sensor-motion-hud-panel'>
            <div class='sensor-motion-left'>
                <div class='sensor-status-badge' id='sensor-status-badge'>
                    <span class='sensor-status-dot' id='sensor-status-dot'></span>
                    <span id='sensor-status-text'>SENSOR MOTION: STANDBY</span>
                </div>
                <div class='sensor-metric-chip'>
                    <span style='color: #94a3b8; font-size: 0.70rem;'>SPEED:</span>
                    <span id='sensor-speed-val' style='font-family: "JetBrains Mono", monospace; font-weight: 800; color: #38bdf8;'>0.0</span>
                    <span style='color: #94a3b8; font-size: 0.70rem;'>km/h</span>
                </div>
                <div class='sensor-metric-chip' id='sensor-cadence-chip'>
                    <span style='color: #94a3b8; font-size: 0.70rem;'>SOURCE:</span>
                    <span id='sensor-source-val' style='color: #a78bfa; font-weight: 700;'>🛰️ GPS & Accel</span>
                </div>
            </div>
            <div class='sensor-motion-right'>
                <div class='sensor-step-countdown'>
                    <span style='color: #94a3b8; font-size: 0.70rem;'>NEXT TURN STEP:</span>
                    <span id='step-remaining-dist' style='font-family: "JetBrains Mono", monospace; font-weight: 800; color: #34d399;'>{active_step.distance_human}</span>
                    <span id='step-countdown-time' style='font-size: 0.72rem; color: #67e8f9;'> (auto)</span>
                </div>
                <button class='btn-action-pill' id='btn-internal-move-toggle' onclick='toggleInternalMoveInParallel()' style='font-weight: 800; background: rgba(56, 189, 248, 0.2); border-color: rgba(56, 189, 248, 0.5);'>
                    <span id='btn-move-icon'>▶</span> <span id='btn-move-label'>Move in Parallel</span>
                </button>
            </div>
        </div>

        <!-- Dynamic Route Journey Pipeline (Every Turn Represented) -->
        <div class='journey-pipeline-section'>
            <div class='pipeline-label-row'>
                <span>{t('guide.pipeline_title', default=f'ROUTE JOURNEY PIPELINE ({len(maneuvers)} ORDERED STEPS)', count=len(maneuvers), lang=curr_lang)}</span>
                <span>{t('guide.step_of', default=f'STEP {{cur}} OF {{total}}', cur=f"<span id='hud-active-step'>{current_step_idx + 1}</span>", total=len(maneuvers), lang=curr_lang)}</span>
            </div>
            <div class='pipeline-track' id='pipeline-track-container'>
                <!-- Dynamically populated via JS -->
            </div>
        </div>

        <!-- 3D Three.js Animated Scene Viewport & Resilient 2.5D Scenic Companion -->
        <div class='aura-3d-scene-container' id='aura-3d-scene-box'>
            <!-- Dedicated WebGL Canvas (Only used by Three.js when WebGL is active) -->
            <canvas id='aura-threejs-canvas' style='display: none; width: 100%; height: 100%;'></canvas>
            <!-- Dedicated 2.5D Scenic Canvas (Zero-blank-screen guaranteed fallback) -->
            <canvas id='aura-scenic-canvas' style='display: block; width: 100%; height: 100%;'></canvas>
            <div class='scene-hud-overlay'>
                <div class='scene-badge' id='hud-runtime-badge'><span class='pulse-dot' id='hud-pulse-dot'></span> <span id='hud-runtime-text'>✦ 2.5D SCENIC RUNTIME ACTIVE</span></div>
                <div class='scene-cam-badge' id='hud-vehicle-mode'>VEHICLE: {norm_travel_mode}</div>
                <div class='scene-cam-badge' id='hud-cam-mode'>CAM: 3D FOLLOW DRONE</div>
                <div class='scene-cam-badge' id='hud-env-mode'>ENV: DAY</div>
                <button id='btn-toggle-engine' class='scene-cam-badge' style='cursor: pointer; pointer-events: auto; background: rgba(56, 189, 248, 0.25); border: 1px solid rgba(56, 189, 248, 0.6); color: #e0f2fe; font-weight: 700;' onclick='window.toggleEngineCompanion()'>{t('guide.toggle_engine', default='🔄 Toggle 3D / 2.5D', lang=curr_lang)}</button>
            </div>
        </div>

        <!-- Active Turn-by-Turn Maneuver Stage -->
        <div class='active-maneuver-stage' id='active-maneuver-box'>
            <div class='maneuver-big-icon' id='stage-icon'>{active_step.icon}</div>
            <div class='maneuver-details'>
                <div class='maneuver-headline' id='stage-headline'>{active_step.headline}</div>
                <div class='maneuver-sub' id='stage-sub'>{active_step.road_name} • {active_step.instruction}</div>
                <div style='font-size: 0.75rem; color: #38bdf8; margin-top: 4px;' id='stage-look'>👀 {active_step.what_to_look_for}</div>
            </div>
            <div>
                <div class='maneuver-dist-badge' id='stage-dist'>{active_step.distance_human}</div>
                <div style='font-size: 0.72rem; color: #94a3b8; text-align: right;' id='stage-time'>~{active_step.time_estimate}</div>
            </div>
        </div>

        <!-- 3D Camera & Avatar Action Toolbar -->
        <div class='controls-toolbar'>
            <!-- Dynamic Vehicle Mode Selector -->
            <div style='display: flex; gap: 5px; align-items: center; flex-wrap: wrap; width: 100%; padding-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 6px;'>
                <span style='font-size: 0.72rem; font-weight: 800; color: #38bdf8;'>{t('guide.travel_vehicle', default='TRAVEL VEHICLE:', lang=curr_lang)}</span>
                <button id='btn-veh-CAR' class='btn-action-pill btn-veh-selector {"active" if norm_travel_mode == "CAR" else ""}' data-mode='CAR' onclick='window.switchVehicleMode("CAR")'>🚗 {t('mode.car', default='Car', lang=curr_lang)}</button>
                <button id='btn-veh-BIKE' class='btn-action-pill btn-veh-selector {"active" if norm_travel_mode == "BIKE" else ""}' data-mode='BIKE' onclick='window.switchVehicleMode("BIKE")'>🏍️ {t('mode.bike', default='Bike', lang=curr_lang)}</button>
                <button id='btn-veh-BUS' class='btn-action-pill btn-veh-selector {"active" if norm_travel_mode == "BUS" else ""}' data-mode='BUS' onclick='window.switchVehicleMode("BUS")'>🚌 {t('mode.bus', default='Bus', lang=curr_lang)}</button>
                <button id='btn-veh-BICYCLE' class='btn-action-pill btn-veh-selector {"active" if norm_travel_mode == "BICYCLE" else ""}' data-mode='BICYCLE' onclick='window.switchVehicleMode("BICYCLE")'>🚴 {t('mode.cycle', default='Cycle', lang=curr_lang)}</button>
                <button id='btn-veh-WALK' class='btn-action-pill btn-veh-selector {"active" if norm_travel_mode == "WALK" else ""}' data-mode='WALK' onclick='window.switchVehicleMode("WALK")'>🚶 {t('mode.walk', default='Walk', lang=curr_lang)}</button>
                <button id='btn-veh-TRUCK' class='btn-action-pill btn-veh-selector {"active" if norm_travel_mode == "TRUCK" else ""}' data-mode='TRUCK' onclick='window.switchVehicleMode("TRUCK")'>🚚 {t('mode.truck', default='Truck', lang=curr_lang)}</button>
                <button id='btn-veh-TRACTOR' class='btn-action-pill btn-veh-selector {"active" if norm_travel_mode == "TRACTOR" else ""}' data-mode='TRACTOR' onclick='window.switchVehicleMode("TRACTOR")'>🚜 {t('mode.tractor', default='Tractor', lang=curr_lang)}</button>
                <button id='btn-veh-FLIGHT' class='btn-action-pill btn-veh-selector {"active" if norm_travel_mode == "FLIGHT" else ""}' data-mode='FLIGHT' onclick='window.switchVehicleMode("FLIGHT")'>✈️ {t('mode.flight', default='Flight', lang=curr_lang)}</button>
                <button id='btn-veh-WATERWAY' class='btn-action-pill btn-veh-selector {"active" if norm_travel_mode == "WATERWAY" else ""}' data-mode='WATERWAY' onclick='window.switchVehicleMode("WATERWAY")'>🚢 {t('mode.ship', default='Ship', lang=curr_lang)}</button>
                <button id='btn-veh-TRAIN' class='btn-action-pill btn-veh-selector {"active" if norm_travel_mode == "TRAIN" else ""}' data-mode='TRAIN' onclick='window.switchVehicleMode("TRAIN")'>🚆 {t('mode.train', default='Train', lang=curr_lang)}</button>
            </div>
            <!-- Avatar Actions -->
            <div style='display: flex; gap: 6px; align-items: center;'>
                <span style='font-size: 0.72rem; font-weight: 700; color: #94a3b8;'>AURA ACTIONS:</span>
                <button class='btn-action-pill' onclick='triggerAuraAction("walk")'>🚶 Walk</button>
                <button class='btn-action-pill' onclick='triggerAuraAction("run")'>🏃 Run</button>
                <button class='btn-action-pill' onclick='triggerAuraAction("jump")'>✨ Jump</button>
                <button class='btn-action-pill' onclick='triggerAuraAction("wave")'>👋 Wave</button>
            </div>

            <!-- 3D Camera Modes -->
            <div style='display: flex; gap: 6px; align-items: center;'>
                <span style='font-size: 0.72rem; font-weight: 700; color: #94a3b8;'>3D CAMERA:</span>
                <button id='cam-pov' class='btn-action-pill' onclick='setCameraPerspective("pov")'>🎥 Driver POV</button>
                <button id='cam-drone' class='btn-action-pill active' onclick='setCameraPerspective("drone")'>🚁 3D Follow Drone</button>
                <button id='cam-iso' class='btn-action-pill' onclick='setCameraPerspective("iso")'>🗺️ 3D Isometric</button>
            </div>

            <!-- Environment Lighting with Real-Time Zone Automatic Sync -->
            <div style='display: flex; gap: 6px; align-items: center;'>
                <span style='font-size: 0.72rem; font-weight: 700; color: #94a3b8;'>ENVIRONMENT:</span>
                <button id='env-auto' class='btn-action-pill active' onclick='toggleAutoRealTimeEnv()' title='Sync 3D Sky directly with real local timezone clock'>⚡ Auto ({time_desc})</button>
                <button id='env-day' class='btn-action-pill' onclick='setEnvLight("day")'>☀️ Day</button>
                <button id='env-sunset' class='btn-action-pill' onclick='setEnvLight("sunset")'>🌅 Sunset</button>
                <button id='env-night' class='btn-action-pill' onclick='setEnvLight("night")'>🌙 Cyber Night</button>
            </div>
        </div>

        <!-- View All Pictures Journey Storybook Modal -->
        <div id='pictures-modal' class='gallery-modal-overlay' onclick='if(event.target===this)closePicturesGallery()'>
            <div class='gallery-modal-card'>
                <div class='gallery-header'>
                    <div style='display: flex; flex-direction: column; gap: 4px;'>
                        <div style='font-weight: 900; font-size: 1.12rem; color: #38bdf8; display: flex; align-items: center; gap: 8px;'>
                            <span>🖼️</span> <span>VIEW ALL PICTURES: COMPLETE ROUTE STORYLINE</span>
                        </div>
                        <div style='font-size: 0.74rem; color: #94a3b8;'>
                            Visual connected storyline from departure to destination • Pictures depict road scenery, turns & milestones
                        </div>
                    </div>
                    <div style='display: flex; gap: 8px; align-items: center;'>
                        <div style='display: flex; background: rgba(15, 23, 42, 0.7); padding: 3px; border-radius: 999px; border: 1px solid rgba(255,255,255,0.1);'>
                            <button id='story-mode-timeline' class='btn-action-pill active' style='padding: 3px 10px; font-size: 0.72rem;' onclick='setStoryGalleryView("timeline")'>🎞️ Connected Storyline</button>
                            <button id='story-mode-grid' class='btn-action-pill' style='padding: 3px 10px; font-size: 0.72rem;' onclick='setStoryGalleryView("grid")'>🖼️ Picture Grid</button>
                        </div>
                        <button class='btn-action-pill' onclick='closePicturesGallery()'>✕ Close</button>
                    </div>
                </div>
                <div class='gallery-scroll-container' id='gallery-container-box'>
                    <!-- Dynamically populated via JS -->
                </div>
            </div>
        </div>
    </div>

    <!-- Load Three.js library with resilient multi-CDN mirrors -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
    if (typeof THREE === 'undefined') {{
        const cdnScript = document.createElement('script');
        cdnScript.src = 'https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js';
        cdnScript.onerror = function() {{
            const unpkgScript = document.createElement('script');
            unpkgScript.src = 'https://unpkg.com/three@0.128.0/build/three.min.js';
            document.head.appendChild(unpkgScript);
        }};
        document.head.appendChild(cdnScript);
    }}
    </script>

    <script>
    window.handleCockpitLangChange = function(newLang) {{
        try {{
            localStorage.setItem('nexroute_app_language', newLang);
            if (window.parent) {{
                window.parent.postMessage({{type: 'nexroute_set_language', language: newLang}}, '*');
            }}
            const url = new URL(window.location.href);
            url.searchParams.set('lang', newLang);
            window.location.href = url.toString();
        }} catch(e) {{
            console.error(e);
        }}
    }};

    (function() {{
        const MANEUVERS = {maneuvers_json};
        let activeIdx = {current_step_idx};
        let isVoiceOn = true;
        let activeCam = "{camera_mode}";
        let activeEnv = "{env_lighting}";
        let currentAnimState = "walk";

        // Live Real-Time Motion Sensor Tracking State
        let isLiveMoving = {"true" if is_live_moving else "false"};
        let currentSpeedKmh = {user_speed_kmh if user_speed_kmh > 0 else 4.8};
        let motionState = isLiveMoving ? "MOVING" : "STATIONARY";
        let remainingStepM = (MANEUVERS[activeIdx] && MANEUVERS[activeIdx].distance_m && MANEUVERS[activeIdx].distance_m > 0) ? MANEUVERS[activeIdx].distance_m : 250;
        let motionSensorSource = "🛰️ GPS & Accel";
        let stepIntervalTimer = null;
        let lastGpsPos = null;
        let lastGpsTime = 0;
        let lastAccelMag = 9.8;
        let lastStepTimestamp = 0;
        let stepCountCadence = 0;

        const AURA_POSES = {{
            "welcome": "{mascot_welcome}",
            "pointing": "{mascot_pointing}",
            "thinking": "{poses.get('thinking', '')}",
            "excited": "{mascot_excited}",
            "talking": "{mascot_talking}",
            "waving": "{mascot_waving}"
        }};

        // Sound Synthesis for Pedestrian & Turn Chimes
        let audioCtx = null;
        function playChime(freq = 660) {{
            if (!isVoiceOn) return;
            try {{
                if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(freq * 1.5, audioCtx.currentTime + 0.12);
                gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.16);
            }} catch(e) {{}}
        }}

        function speakText(txt) {{
            if (!isVoiceOn || !('speechSynthesis' in window)) return;
            try {{
                window.speechSynthesis.cancel();
                const u = new SpeechSynthesisUtterance(txt);
                u.lang = '{bcp47_code}';
                u.rate = 1.05;
                const voices = window.speechSynthesis.getVoices();
                const targetPrefix = u.lang.split('-')[0].toLowerCase();
                for (let i = 0; i < voices.length; i++) {{
                    const vLang = (voices[i].lang || '').toLowerCase().replace('_', '-');
                    if (vLang === u.lang.toLowerCase() || vLang.startsWith(targetPrefix)) {{
                        u.voice = voices[i];
                        break;
                    }}
                }}
                window.speechSynthesis.speak(u);
            }} catch(e) {{}}
        }}

        function getScenicStepSvg(dirType, roadName, stepNum, iconText, isCompleted, isActive) {{
            const rawDir = (dirType || '').toUpperCase();
            const cleanRoad = String(roadName || 'Corridor Route').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
            const shortRoad = cleanRoad.length > 22 ? cleanRoad.substring(0, 20) + '...' : cleanRoad;
            const uid = 'svg_' + stepNum + '_' + Math.random().toString(36).substr(2, 6);
            const labelBg = 'rgba(15, 23, 42, 0.88)';
            const borderCol = isActive ? '#38bdf8' : (isCompleted ? '#34d399' : '#0284c7');

            if (rawDir.includes('ARRIVE') || rawDir.includes('DEST')) {{
                return `
                <svg viewBox="0 0 360 170" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" style="display:block; border-radius:12px; overflow:hidden;">
                    <defs>
                        <linearGradient id="sky_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#022c22"/>
                            <stop offset="40%" stop-color="#065f46"/>
                            <stop offset="100%" stop-color="#10b981"/>
                        </linearGradient>
                        <linearGradient id="road_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#334155"/>
                            <stop offset="100%" stop-color="#0f172a"/>
                        </linearGradient>
                        <radialGradient id="sun_${{uid}}" cx="50%" cy="35%" r="50%">
                            <stop offset="0%" stop-color="#fef08a" stop-opacity="0.95"/>
                            <stop offset="50%" stop-color="#34d399" stop-opacity="0.4"/>
                            <stop offset="100%" stop-color="#065f46" stop-opacity="0"/>
                        </radialGradient>
                    </defs>
                    <rect width="360" height="170" fill="url(#sky_${{uid}})"/>
                    <circle cx="180" cy="55" r="55" fill="url(#sun_${{uid}})"/>
                    <polygon points="0,85 45,72 90,82 140,68 180,78 220,68 270,82 315,72 360,85 360,105 0,105" fill="#064e3b" opacity="0.6"/>
                    <rect y="95" width="360" height="75" fill="#047857"/>
                    <!-- Arrival Plaza Road -->
                    <polygon points="120,170 240,170 198,95 162,95" fill="url(#road_${{uid}})"/>
                    <polygon points="80,170 120,170 162,95 150,95" fill="#059669" opacity="0.6"/>
                    <polygon points="240,170 280,170 210,95 198,95" fill="#059669" opacity="0.6"/>
                    <line x1="180" y1="95" x2="180" y2="170" stroke="#34d399" stroke-width="3" stroke-dasharray="8,6"/>
                    <!-- Grand Destination Archway -->
                    <path d="M 130 170 L 130 65 Q 180 38 230 65 L 230 170" fill="none" stroke="#fef08a" stroke-width="4.5"/>
                    <path d="M 134 68 Q 180 44 226 68" fill="none" stroke="#34d399" stroke-width="2.5"/>
                    <rect x="142" y="48" width="76" height="18" rx="4" fill="#064e3b" stroke="#fef08a" stroke-width="1.5"/>
                    <text x="180" y="60.5" font-size="7.5" font-weight="900" fill="#fef08a" text-anchor="middle" font-family="sans-serif">★ DESTINATION REACHED ★</text>
                    <text x="114" y="70" font-size="16">🏁</text>
                    <text x="232" y="70" font-size="16">🏁</text>
                    <!-- Sparkles & Celebration -->
                    <text x="70" y="55" font-size="14">✨</text>
                    <text x="280" y="55" font-size="14">✨</text>
                    <text x="180" y="32" font-size="16">🎉</text>
                    <!-- Road Sign Pill -->
                    <rect x="14" y="138" width="130" height="22" rx="5" fill="${{labelBg}}" stroke="${{borderCol}}" stroke-width="1.5"/>
                    <text x="79" y="153" font-size="9" font-weight="800" fill="#a7f3d0" text-anchor="middle" font-family="sans-serif">🏁 ARRIVED • ${{shortRoad}}</text>
                </svg>`;
            }} else if (rawDir.includes('LEFT')) {{
                return `
                <svg viewBox="0 0 360 170" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" style="display:block; border-radius:12px; overflow:hidden;">
                    <defs>
                        <linearGradient id="sky_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#0369a1"/>
                            <stop offset="60%" stop-color="#0284c7"/>
                            <stop offset="100%" stop-color="#38bdf8"/>
                        </linearGradient>
                        <linearGradient id="road_${{uid}}" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0%" stop-color="#0f172a"/>
                            <stop offset="50%" stop-color="#1e293b"/>
                            <stop offset="100%" stop-color="#334155"/>
                        </linearGradient>
                    </defs>
                    <rect width="360" height="170" fill="url(#sky_${{uid}})"/>
                    <circle cx="310" cy="35" r="22" fill="#fef08a" opacity="0.85"/>
                    <ellipse cx="260" cy="32" rx="35" ry="10" fill="#ffffff" opacity="0.6"/>
                    <ellipse cx="120" cy="24" rx="28" ry="8" fill="#ffffff" opacity="0.5"/>
                    <rect y="80" width="360" height="90" fill="#0f766e"/>
                    <!-- Road Curving Smoothly to Left -->
                    <path d="M 0 88 Q 120 92 180 170 L 290 170 Q 220 84 0 74 Z" fill="url(#road_${{uid}})"/>
                    <path d="M 0 74 Q 220 84 290 170" fill="none" stroke="#64748b" stroke-width="3"/>
                    <path d="M 0 88 Q 120 92 180 170" fill="none" stroke="#64748b" stroke-width="3"/>
                    <path d="M 0 81 Q 170 88 235 170" fill="none" stroke="#fbbf24" stroke-width="3.5" stroke-dasharray="10,6"/>
                    <!-- High-Tech 3D Holographic Left Turn Arrow -->
                    <g transform="translate(130, 105) scale(0.95)">
                        <path d="M 40 45 C 40 24, 20 14, -4 14 L -4 22 L -24 9 L -4 -4 L -4 5 C 28 5, 50 18, 50 45 Z" fill="#ffffff" filter="drop-shadow(0 3px 8px rgba(0,0,0,0.6))"/>
                        <path d="M 38 43 C 38 25, 20 16, -2 16 L -2 20 L -18 9 L -2 0 L -2 7 C 26 7, 46 19, 46 43 Z" fill="#38bdf8"/>
                    </g>
                    <!-- Street Lampposts with Glowing Cones -->
                    <line x1="60" y1="46" x2="60" y2="86" stroke="#475569" stroke-width="3"/>
                    <line x1="60" y1="46" x2="72" y2="46" stroke="#475569" stroke-width="2.5"/>
                    <circle cx="72" cy="48" r="4" fill="#fef08a"/>
                    <polygon points="72,48 50,86 94,86" fill="#fef08a" opacity="0.18"/>
                    <!-- Roadside Trees and Buildings -->
                    <circle cx="330" cy="80" r="14" fill="#15803d"/><circle cx="330" cy="70" r="11" fill="#22c55e"/>
                    <rect x="280" y="55" width="34" height="35" rx="3" fill="#1e293b" opacity="0.9"/>
                    <rect x="286" y="62" width="8" height="8" fill="#38bdf8" opacity="0.8"/>
                    <rect x="300" y="62" width="8" height="8" fill="#fef08a" opacity="0.8"/>
                    <!-- Road Sign Pill -->
                    <rect x="14" y="138" width="145" height="22" rx="5" fill="${{labelBg}}" stroke="${{borderCol}}" stroke-width="1.5"/>
                    <text x="86" y="153" font-size="9" font-weight="800" fill="#e0f2fe" text-anchor="middle" font-family="sans-serif">↰ TURN LEFT • ${{shortRoad}}</text>
                </svg>`;
            }} else if (rawDir.includes('RIGHT')) {{
                return `
                <svg viewBox="0 0 360 170" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" style="display:block; border-radius:12px; overflow:hidden;">
                    <defs>
                        <linearGradient id="sky_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#0284c7"/>
                            <stop offset="60%" stop-color="#0369a1"/>
                            <stop offset="100%" stop-color="#60a5fa"/>
                        </linearGradient>
                        <linearGradient id="road_${{uid}}" x1="0" y1="0" x2="1" y2="1">
                            <stop offset="0%" stop-color="#0f172a"/>
                            <stop offset="50%" stop-color="#1e293b"/>
                            <stop offset="100%" stop-color="#334155"/>
                        </linearGradient>
                    </defs>
                    <rect width="360" height="170" fill="url(#sky_${{uid}})"/>
                    <circle cx="50" cy="35" r="22" fill="#fef08a" opacity="0.85"/>
                    <ellipse cx="100" cy="32" rx="35" ry="10" fill="#ffffff" opacity="0.6"/>
                    <ellipse cx="240" cy="24" rx="28" ry="8" fill="#ffffff" opacity="0.5"/>
                    <rect y="80" width="360" height="90" fill="#0f766e"/>
                    <!-- Road Curving Smoothly to Right -->
                    <path d="M 70 170 Q 140 92 360 88 L 360 74 Q 140 84 180 170 Z" fill="url(#road_${{uid}})"/>
                    <path d="M 180 170 Q 140 84 360 74" fill="none" stroke="#64748b" stroke-width="3"/>
                    <path d="M 70 170 Q 140 92 360 88" fill="none" stroke="#64748b" stroke-width="3"/>
                    <path d="M 125 170 Q 190 88 360 81" fill="none" stroke="#fbbf24" stroke-width="3.5" stroke-dasharray="10,6"/>
                    <!-- High-Tech 3D Holographic Right Turn Arrow -->
                    <g transform="translate(210, 105) scale(0.95)">
                        <path d="M -40 45 C -40 24, -20 14, 4 14 L 4 22 L 24 9 L 4 -4 L 4 5 C -28 5, -50 18, -50 45 Z" fill="#ffffff" filter="drop-shadow(0 3px 8px rgba(0,0,0,0.6))"/>
                        <path d="M -38 43 C -38 25, -20 16, 2 16 L 2 20 L 18 9 L 2 0 L 2 7 C -26 7, -46 19, -46 43 Z" fill="#38bdf8"/>
                    </g>
                    <!-- Street Lamppost on Left -->
                    <line x1="300" y1="46" x2="300" y2="86" stroke="#475569" stroke-width="3"/>
                    <line x1="300" y1="46" x2="288" y2="46" stroke="#475569" stroke-width="2.5"/>
                    <circle cx="288" cy="48" r="4" fill="#fef08a"/>
                    <polygon points="288,48 266,86 310,86" fill="#fef08a" opacity="0.18"/>
                    <!-- Roadside Trees and Buildings -->
                    <circle cx="30" cy="80" r="14" fill="#15803d"/><circle cx="30" cy="70" r="11" fill="#22c55e"/>
                    <rect x="45" y="55" width="34" height="35" rx="3" fill="#1e293b" opacity="0.9"/>
                    <rect x="52" y="62" width="8" height="8" fill="#38bdf8" opacity="0.8"/>
                    <rect x="66" y="62" width="8" height="8" fill="#fef08a" opacity="0.8"/>
                    <!-- Road Sign Pill -->
                    <rect x="200" y="138" width="145" height="22" rx="5" fill="${{labelBg}}" stroke="${{borderCol}}" stroke-width="1.5"/>
                    <text x="272" y="153" font-size="9" font-weight="800" fill="#e0f2fe" text-anchor="middle" font-family="sans-serif">↱ TURN RIGHT • ${{shortRoad}}</text>
                </svg>`;
            }} else if (rawDir.includes('START') || rawDir.includes('DEPART')) {{
                return `
                <svg viewBox="0 0 360 170" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" style="display:block; border-radius:12px; overflow:hidden;">
                    <defs>
                        <linearGradient id="sky_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#0284c7"/>
                            <stop offset="60%" stop-color="#38bdf8"/>
                            <stop offset="100%" stop-color="#bae6fd"/>
                        </linearGradient>
                        <linearGradient id="road_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#475569"/>
                            <stop offset="100%" stop-color="#1e293b"/>
                        </linearGradient>
                    </defs>
                    <rect width="360" height="170" fill="url(#sky_${{uid}})"/>
                    <!-- Horizon Sunrise -->
                    <ellipse cx="180" cy="80" rx="90" ry="26" fill="#fef08a" opacity="0.7"/>
                    <!-- Mountains Silhouette -->
                    <polygon points="10,80 40,62 65,80 100,56 130,80 160,65 190,80 220,58 260,80 300,66 330,80 360,70 360,88 0,88" fill="#0284c7" opacity="0.45"/>
                    <rect y="80" width="360" height="90" fill="#065f46"/>
                    <!-- Straight Departing Road -->
                    <polygon points="80,170 280,170 192,80 168,80" fill="url(#road_${{uid}})"/>
                    <polygon points="50,170 80,170 168,80 158,80" fill="#64748b"/>
                    <polygon points="280,170 310,170 202,80 192,80" fill="#64748b"/>
                    <line x1="180" y1="80" x2="180" y2="170" stroke="#fbbf24" stroke-width="3" stroke-dasharray="10,6"/>
                    <!-- Departure Gateway Structure -->
                    <rect x="135" y="105" width="90" height="12" rx="3" fill="#059669" stroke="#34d399" stroke-width="2"/>
                    <line x1="142" y1="117" x2="142" y2="160" stroke="#34d399" stroke-width="3.5"/>
                    <line x1="218" y1="117" x2="218" y2="160" stroke="#34d399" stroke-width="3.5"/>
                    <text x="180" y="114" font-size="7" font-weight="900" fill="#ffffff" text-anchor="middle" font-family="sans-serif">★ DEPARTURE GATEWAY ★</text>
                    <circle cx="180" cy="132" r="7" fill="#10b981"/>
                    <circle cx="180" cy="132" r="3" fill="#ffffff"/>
                    <!-- Roadside Foliage -->
                    <circle cx="35" cy="98" r="14" fill="#15803d"/><circle cx="35" cy="88" r="10" fill="#22c55e"/>
                    <circle cx="325" cy="98" r="14" fill="#15803d"/><circle cx="325" cy="88" r="10" fill="#22c55e"/>
                    <!-- Road Sign Pill -->
                    <rect x="14" y="138" width="145" height="22" rx="5" fill="${{labelBg}}" stroke="#10b981" stroke-width="1.5"/>
                    <text x="86" y="153" font-size="9" font-weight="800" fill="#a7f3d0" text-anchor="middle" font-family="sans-serif">🚀 START • ${{shortRoad}}</text>
                </svg>`;
            }} else if (rawDir.includes('ROUNDABOUT') || rawDir.includes('ROTARY')) {{
                return `
                <svg viewBox="0 0 360 170" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" style="display:block; border-radius:12px; overflow:hidden;">
                    <defs>
                        <linearGradient id="sky_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#0284c7"/>
                            <stop offset="100%" stop-color="#38bdf8"/>
                        </linearGradient>
                    </defs>
                    <rect width="360" height="170" fill="url(#sky_${{uid}})"/>
                    <rect y="75" width="360" height="95" fill="#065f46"/>
                    <!-- Roundabout Island Perspective -->
                    <ellipse cx="180" cy="120" rx="130" ry="42" fill="#334155" stroke="#64748b" stroke-width="3"/>
                    <ellipse cx="180" cy="120" rx="65" ry="20" fill="#15803d" stroke="#22c55e" stroke-width="3"/>
                    <circle cx="180" cy="116" r="9" fill="#f59e0b"/>
                    <ellipse cx="180" cy="120" rx="98" ry="31" fill="none" stroke="#fbbf24" stroke-width="2.5" stroke-dasharray="8,6"/>
                    <text x="110" y="124" font-size="16" fill="#ffffff">↺</text>
                    <text x="240" y="124" font-size="16" fill="#ffffff">↻</text>
                    <!-- Road Sign Pill -->
                    <rect x="14" y="138" width="155" height="22" rx="5" fill="${{labelBg}}" stroke="${{borderCol}}" stroke-width="1.5"/>
                    <text x="91" y="153" font-size="9" font-weight="800" fill="#e0f2fe" text-anchor="middle" font-family="sans-serif">🔄 ROUNDABOUT • ${{shortRoad}}</text>
                </svg>`;
            }} else {{
                // Cruising Straight Ahead
                return `
                <svg viewBox="0 0 360 170" width="100%" height="100%" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" style="display:block; border-radius:12px; overflow:hidden;">
                    <defs>
                        <linearGradient id="sky_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#0284c7"/>
                            <stop offset="50%" stop-color="#38bdf8"/>
                            <stop offset="100%" stop-color="#7dd3fc"/>
                        </linearGradient>
                        <linearGradient id="road_${{uid}}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="#475569"/>
                            <stop offset="100%" stop-color="#1e293b"/>
                        </linearGradient>
                    </defs>
                    <rect width="360" height="170" fill="url(#sky_${{uid}})"/>
                    <!-- Clouds -->
                    <ellipse cx="90" cy="30" rx="35" ry="10" fill="#ffffff" opacity="0.75"/>
                    <ellipse cx="270" cy="25" rx="42" ry="12" fill="#ffffff" opacity="0.65"/>
                    <!-- Distant Mountain Ranges -->
                    <polygon points="0,78 70,60 160,74 250,56 320,70 360,64 360,82 0,82" fill="#0369a1" opacity="0.55"/>
                    <rect y="78" width="360" height="92" fill="#047857"/>
                    <!-- Highway Vanishing Point Road -->
                    <polygon points="70,170 290,170 192,78 168,78" fill="url(#road_${{uid}})"/>
                    <polygon points="40,170 70,170 168,78 158,78" fill="#64748b"/>
                    <polygon points="290,170 320,170 202,78 192,78" fill="#64748b"/>
                    <line x1="180" y1="78" x2="180" y2="170" stroke="#fbbf24" stroke-width="3.5" stroke-dasharray="10,6"/>
                    <!-- Highway Overhead Guide Sign -->
                    <rect x="135" y="88" width="90" height="16" rx="3" fill="#0f172a" stroke="#38bdf8" stroke-width="1.8"/>
                    <text x="180" y="99.5" font-size="7" font-weight="900" fill="#38bdf8" text-anchor="middle" font-family="sans-serif">⬆ CRUISE STRAIGHT</text>
                    <!-- Roadside Trees & Utility Poles -->
                    <circle cx="36" cy="105" r="16" fill="#15803d"/><circle cx="36" cy="92" r="12" fill="#22c55e"/>
                    <circle cx="80" cy="90" r="10" fill="#15803d"/><circle cx="80" cy="82" r="7" fill="#22c55e"/>
                    <circle cx="324" cy="105" r="16" fill="#15803d"/><circle cx="324" cy="92" r="12" fill="#22c55e"/>
                    <circle cx="280" cy="90" r="10" fill="#15803d"/><circle cx="280" cy="82" r="7" fill="#22c55e"/>
                    <!-- Road Sign Pill -->
                    <rect x="14" y="138" width="145" height="22" rx="5" fill="${{labelBg}}" stroke="${{borderCol}}" stroke-width="1.5"/>
                    <text x="86" y="153" font-size="9" font-weight="800" fill="#e0f2fe" text-anchor="middle" font-family="sans-serif">🛣️ CRUISE • ${{shortRoad}}</text>
                </svg>`;
            }}
        }}

        // Render Pipeline Chips
        function renderPipeline() {{
            const cont = document.getElementById('pipeline-track-container');
            if (!cont) return;
            cont.innerHTML = '';

            MANEUVERS.forEach((m, idx) => {{
                const card = document.createElement('div');
                let cls = 'pipeline-step-card';
                const isCompleted = (idx < activeIdx);
                const isActive = (idx === activeIdx);
                if (isActive) cls += ' active';
                else if (isCompleted) cls += ' completed';
                card.className = cls;

                const picSvg = getScenicStepSvg(m.direction_type, m.road_name, m.step_num, m.icon, isCompleted, isActive);

                card.id = `step-card-${{idx}}`;
                card.innerHTML = `
                    <div class="step-picture-frame">
                        ${{picSvg}}
                        <div class="step-pic-overlay-badge">
                            <span class="step-num-pill">STEP ${{m.step_num}}</span>
                            <span class="step-icon-badge">${{m.icon}}</span>
                        </div>
                    </div>
                    <div class="step-card-body">
                        <div class="step-card-headline" title="${{m.headline}}">
                            ${{m.headline}}
                        </div>
                        <div class="step-card-footer">
                            <span class="step-card-road" title="${{m.road_name || ''}}">${{m.road_name || 'Corridor'}}</span>
                            <b class="step-card-dist">${{m.distance_human}}</b>
                        </div>
                    </div>
                `;

                card.onclick = () => selectStep(idx);
                cont.appendChild(card);
            }});
        }}

        window.selectStep = function(idx) {{
            if (idx < 0 || idx >= MANEUVERS.length) return;
            activeIdx = idx;
            const m = MANEUVERS[idx];

            // Update UI elements
            const hudStep = document.getElementById('hud-active-step');
            if (hudStep) hudStep.innerText = m.step_num;

            const iconEl = document.getElementById('stage-icon');
            if (iconEl) iconEl.innerText = m.icon;

            const headEl = document.getElementById('stage-headline');
            if (headEl) headEl.innerText = m.headline;

            const subEl = document.getElementById('stage-sub');
            if (subEl) subEl.innerText = `${{m.road_name}} • ${{m.instruction}}`;

            const distEl = document.getElementById('stage-dist');
            if (distEl) distEl.innerText = m.distance_human;

            const timeEl = document.getElementById('stage-time');
            if (timeEl) timeEl.innerText = `~${{m.time_estimate}}`;

            const lookEl = document.getElementById('stage-look');
            if (lookEl) lookEl.innerText = `👀 ${{m.what_to_look_for}}`;

            const speechEl = document.getElementById('aura-speech-content');
            if (speechEl) speechEl.innerText = m.aura_speech;

            // Trigger 2D Fallback Pose Matching
            const podImg = document.getElementById('aura-pod-img');
            const poseKey = m.aura_pose || (m.direction_type === 'ARRIVE' ? 'excited' : 'talking');
            if (podImg && AURA_POSES[poseKey]) {{
                podImg.src = AURA_POSES[poseKey];
            }}

            // Correlate 3D Animation State with Maneuver
            const dir = (m.direction_type || '').toUpperCase();
            if (dir === 'ARRIVE' || dir === 'DEST_REACHED') {{
                currentAnimState = 'arrive';
            }} else if (dir.includes('LEFT')) {{
                currentAnimState = 'turn_left';
            }} else if (dir.includes('RIGHT')) {{
                currentAnimState = 'turn_right';
            }} else if (dir === 'START') {{
                currentAnimState = 'wave';
            }} else if (dir.includes('ROUNDABOUT') || dir.includes('MERGE')) {{
                currentAnimState = 'turn_right';
            }} else {{
                currentAnimState = 'walk';
            }}

            playChime(660);
            speakText(m.spoken_text);
            renderPipeline();

            // Reset dynamic step countdown for newly activated maneuver
            remainingStepM = (m.distance_m && m.distance_m > 0) ? m.distance_m : 250;
            const remEl = document.getElementById('step-remaining-dist');
            if (remEl) remEl.innerText = m.distance_human || (remainingStepM + ' m');

            // Auto-scroll pipeline to center active card smoothly
            setTimeout(() => {{
                const activeCard = document.getElementById(`step-card-${{idx}}`);
                const cont = document.getElementById('pipeline-track-container');
                if (activeCard && cont) {{
                    const cardLeft = activeCard.offsetLeft;
                    const cardWidth = activeCard.offsetWidth;
                    const contWidth = cont.offsetWidth;
                    cont.scrollTo({{
                        left: cardLeft - (contWidth / 2) + (cardWidth / 2),
                        behavior: 'smooth'
                    }});
                }}
            }}, 50);
        }};

        window.triggerAuraAction = function(action) {{
            const podImg = document.getElementById('aura-pod-img');
            const speechEl = document.getElementById('aura-speech-content');

            if (action === 'wave') {{
                currentAnimState = 'wave';
                if (podImg && AURA_POSES.waving) podImg.src = AURA_POSES.waving;
                if (speechEl) speechEl.innerText = "Hey! I'm watching the road closely with you!";
                playChime(880);
                speakText("Hey! I'm watching the road closely with you!");
            }} else if (action === 'jump') {{
                currentAnimState = 'arrive';
                if (podImg && AURA_POSES.excited) podImg.src = AURA_POSES.excited;
                if (speechEl) speechEl.innerText = "Hooray! Great progress on our journey!";
                playChime(990);
                speakText("Hooray! Great progress on our journey!");
            }} else if (action === 'run') {{
                currentAnimState = 'run';
                if (podImg && AURA_POSES.pointing) podImg.src = AURA_POSES.pointing;
                if (speechEl) speechEl.innerText = "Picking up pace! Stay alert for corridor junctions.";
                playChime(750);
            }} else if (action === 'walk') {{
                currentAnimState = 'walk';
                if (podImg && AURA_POSES.talking) podImg.src = AURA_POSES.talking;
                if (speechEl) speechEl.innerText = "Walking comfortably along the designated route.";
                playChime(600);
            }}
        }};

        window.setCameraPerspective = function(mode) {{
            activeCam = mode;
            ['pov', 'drone', 'iso'].forEach(k => {{
                const btn = document.getElementById('cam-' + k);
                if (btn) btn.classList.remove('active');
            }});
            const btn = document.getElementById('cam-' + mode);
            if (btn) btn.classList.add('active');

            const camBadge = document.getElementById('hud-cam-mode');
            if (camBadge) {{
                camBadge.innerText = 'CAM: ' + (mode === 'pov' ? 'DRIVER POV' : (mode === 'iso' ? '3D ISOMETRIC' : '3D FOLLOW DRONE'));
            }}
        }};

        let isAutoRealTimeEnv = true;

        function formatUserLocalTime(d) {{
            let hours = d.getHours();
            const minutes = d.getMinutes();
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12;
            const strMinutes = minutes < 10 ? '0' + minutes : minutes;
            return hours + ':' + strMinutes + ' ' + ampm;
        }}

        function getRealTimeEnv() {{
            const now = new Date();
            const h = now.getHours() + (now.getMinutes() / 60.0);
            if (h >= 17.0 && h < 19.35) {{
                return 'sunset';
            }} else if (h >= 6.0 && h < 17.0) {{
                return 'day';
            }} else {{
                return 'night';
            }}
        }}

        function getRealTimeEnvInfo() {{
            const now = new Date();
            const env = getRealTimeEnv();
            const label = env === 'sunset' ? 'Sunset' : (env === 'night' ? 'Cyber Night' : 'Day');
            return {{
                env: env,
                label: label,
                timeStr: formatUserLocalTime(now),
                hour: now.getHours() + (now.getMinutes() / 60.0)
            }};
        }}

        function syncRealTimeAutoEnvironment() {{
            const info = getRealTimeEnvInfo();
            const autoBtn = document.getElementById('env-auto');
            if (autoBtn) {{
                autoBtn.innerHTML = '⚡ Auto (' + info.timeStr + ' • ' + info.label + ')';
                autoBtn.title = 'Real-time device clock synced: ' + info.timeStr + ' (' + info.label + ')';
            }}
            if (isAutoRealTimeEnv) {{
                window.setEnvLight(info.env, true);
            }}
        }}

        window.toggleAutoRealTimeEnv = function() {{
            isAutoRealTimeEnv = true;
            syncRealTimeAutoEnvironment();
        }};

        window.setEnvLight = function(env, fromAuto = false) {{
            if (!fromAuto) isAutoRealTimeEnv = false;
            activeEnv = env;
            ['day', 'sunset', 'night'].forEach(k => {{
                const btn = document.getElementById('env-' + k);
                if (btn) btn.classList.remove('active');
            }});
            const btn = document.getElementById('env-' + env);
            if (btn) btn.classList.add('active');

            const autoBtn = document.getElementById('env-auto');
            if (autoBtn) {{
                if (isAutoRealTimeEnv) autoBtn.classList.add('active');
                else autoBtn.classList.remove('active');
            }}

            const envBadge = document.getElementById('hud-env-mode');
            if (envBadge) {{
                const info = getRealTimeEnvInfo();
                envBadge.innerText = 'ENV: ' + env.toUpperCase() + (isAutoRealTimeEnv ? ' (LIVE ' + info.timeStr + ')' : ' (MANUAL)');
            }}

            if (threeEnv) {{
                threeEnv.updateLighting(env);
            }}
        }};

        // =========================================================================
        // REAL USER MOTION SENSORS & AUTOMATIC VIRTUAL GUIDE STEPPING
        // =========================================================================
        function updateMotionUI(speedKmh, state, source) {{
            currentSpeedKmh = speedKmh;
            motionState = state;
            if (source) motionSensorSource = source;

            const speedEl = document.getElementById('sensor-speed-val');
            if (speedEl) speedEl.innerText = speedKmh > 0 ? speedKmh.toFixed(1) : "0.0";

            const statusBadge = document.getElementById('sensor-status-badge');
            const statusTxt = document.getElementById('sensor-status-text');
            if (statusBadge && statusTxt) {{
                if (state === 'MOVING') {{
                    statusBadge.className = 'sensor-status-badge moving';
                    statusTxt.innerText = 'SENSOR MOTION: MOVING';
                }} else {{
                    statusBadge.className = 'sensor-status-badge stationary';
                    statusTxt.innerText = 'SENSOR MOTION: STATIONARY';
                }}
            }}

            const srcEl = document.getElementById('sensor-source-val');
            if (srcEl) srcEl.innerText = motionSensorSource;

            const btnIcon = document.getElementById('btn-move-icon');
            const btnLbl = document.getElementById('btn-move-label');
            if (btnIcon && btnLbl) {{
                if (isLiveMoving) {{
                    btnIcon.innerText = '⏸';
                    btnLbl.innerText = 'Pause Guide';
                }} else {{
                    btnIcon.innerText = '▶';
                    btnLbl.innerText = 'Move in Parallel';
                }}
            }}

            // Dynamically synchronize 3D Companion Animation with motion state & speed
            if (state === 'MOVING') {{
                if (currentSpeedKmh > 11.0) {{
                    currentAnimState = 'run';
                }} else if (currentAnimState !== 'turn_left' && currentAnimState !== 'turn_right' && currentAnimState !== 'arrive') {{
                    currentAnimState = 'walk';
                }}
            }} else if (state === 'STATIONARY') {{
                if (currentAnimState === 'walk' || currentAnimState === 'run') {{
                    currentAnimState = 'wave';
                }}
            }}
        }}

        function calcHaversineMeters(lat1, lon1, lat2, lon2) {{
            const R = 6371e3;
            const p1 = lat1 * Math.PI / 180;
            const p2 = lat2 * Math.PI / 180;
            const dp = (lat2 - lat1) * Math.PI / 180;
            const dl = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(dp / 2) * Math.sin(dp / 2) +
                      Math.cos(p1) * Math.cos(p2) *
                      Math.sin(dl / 2) * Math.sin(dl / 2);
            return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        }}

        function initSensorWatchers() {{
            // 1. Live Geolocation Watcher for Speed and Corridor Advancement
            if ('geolocation' in navigator) {{
                try {{
                    navigator.geolocation.watchPosition(
                        (pos) => {{
                            const now = Date.now();
                            let detectedSpeed = 0;
                            if (pos.coords.speed !== null && !isNaN(pos.coords.speed) && pos.coords.speed >= 0) {{
                                detectedSpeed = pos.coords.speed * 3.6; // convert m/s to km/h
                            }} else if (lastGpsPos && lastGpsTime > 0) {{
                                const dt = (now - lastGpsTime) / 1000;
                                if (dt >= 1.0) {{
                                    const dM = calcHaversineMeters(
                                        lastGpsPos.coords.latitude, lastGpsPos.coords.longitude,
                                        pos.coords.latitude, pos.coords.longitude
                                    );
                                    detectedSpeed = (dM / dt) * 3.6;
                                }}
                            }}
                            lastGpsPos = pos;
                            lastGpsTime = now;

                            if (detectedSpeed >= 1.2) {{
                                isLiveMoving = true;
                                updateMotionUI(detectedSpeed, 'MOVING', '🛰️ Live GPS Satellites');
                            }} else if (isLiveMoving && detectedSpeed < 0.6) {{
                                updateMotionUI(0.0, 'STATIONARY', '🛰️ Live GPS (Idle)');
                            }}
                        }},
                        (err) => {{
                            console.log('GPS Sensor notice:', err.message);
                        }},
                        {{ enableHighAccuracy: true, maximumAge: 1500, timeout: 6000 }}
                    );
                }} catch (e) {{
                    console.warn('Geolocation sensor error:', e);
                }}
            }}

            // 2. Physical Accelerometer & Device Motion for Step Cadence Detection
            if (window.DeviceMotionEvent) {{
                try {{
                    window.addEventListener('devicemotion', (evt) => {{
                        const acc = evt.accelerationIncludingGravity || evt.acceleration;
                        if (!acc) return;
                        const ax = acc.x || 0, ay = acc.y || 0, az = acc.z || 0;
                        const mag = Math.sqrt(ax * ax + ay * ay + az * az);
                        const delta = Math.abs(mag - lastAccelMag);
                        lastAccelMag = mag;

                        const now = Date.now();
                        // Physical step peak threshold
                        if (delta > 1.8 && (now - lastStepTimestamp) > 320) {{
                            const stepDt = (now - lastStepTimestamp) / 1000;
                            lastStepTimestamp = now;
                            if (stepDt < 2.0) {{
                                const spm = Math.round(60 / stepDt);
                                stepCountCadence = spm;
                                if (currentSpeedKmh < 1.0 || motionState === 'STATIONARY') {{
                                    const inferredSpeed = Math.min(12.0, Math.max(3.2, (spm * 0.72 * 60) / 1000));
                                    isLiveMoving = true;
                                    updateMotionUI(inferredSpeed, 'MOVING', `📱 Sensor Cadence (${{spm}} spm)`);
                                }}
                            }}
                        }}
                    }}, {{ passive: true }});
                }} catch (e) {{
                    console.warn('Accelerometer sensor error:', e);
                }}
            }}
        }}

        function startStepProgressionLoop() {{
            if (stepIntervalTimer) clearInterval(stepIntervalTimer);

            stepIntervalTimer = setInterval(() => {{
                if (!isLiveMoving) return;

                if (motionState === 'MOVING') {{
                    const speedMps = Math.max(1.2, currentSpeedKmh / 3.6);
                    // Dynamically decrement step distance according to sensor velocity
                    remainingStepM -= (speedMps * 1.0);

                    // Update UI countdown displays
                    const remEl = document.getElementById('step-remaining-dist');
                    const timeEl = document.getElementById('step-countdown-time');
                    const stageDistEl = document.getElementById('stage-dist');

                    const formattedDist = remainingStepM >= 1000 
                        ? (remainingStepM / 1000).toFixed(1) + ' km' 
                        : Math.max(0, Math.round(remainingStepM)) + ' m';

                    if (remEl) remEl.innerText = formattedDist;
                    if (stageDistEl) stageDistEl.innerText = formattedDist;

                    if (timeEl) {{
                        const secLeft = Math.max(0, Math.round(remainingStepM / speedMps));
                        timeEl.innerText = `(~${{secLeft}}s)`;
                    }}

                    // When step threshold reached (within 8 meters), AUTOMATICALLY MAKE THE NEXT STEP!
                    if (remainingStepM <= 8) {{
                        if (activeIdx < MANEUVERS.length - 1) {{
                            const nextIdx = activeIdx + 1;
                            selectStep(nextIdx);
                        }} else {{
                            // Destination reached!
                            isLiveMoving = false;
                            updateMotionUI(0.0, 'STATIONARY', '🏁 Destination Reached');
                            currentAnimState = 'arrive';
                            const thoughtEl = document.getElementById('aura-speech-content');
                            if (thoughtEl) {{
                                thoughtEl.innerText = '🎉 Congratulations! You have successfully reached your destination!';
                            }}
                            speakText('Congratulations! You have reached your destination.');
                            playChime(880);
                            setTimeout(() => playChime(1100), 200);
                        }}
                    }}
                }}
            }}, 1000);
        }}

        window.toggleInternalMoveInParallel = function() {{
            isLiveMoving = !isLiveMoving;
            if (isLiveMoving) {{
                if (typeof DeviceMotionEvent !== 'undefined' && typeof DeviceMotionEvent.requestPermission === 'function') {{
                    DeviceMotionEvent.requestPermission().catch(() => {{}});
                }}
                const spd = currentSpeedKmh > 0 ? currentSpeedKmh : 4.8;
                updateMotionUI(spd, 'MOVING', '🛰️ Parallel Sensor GPS');
                speakText("Moving in parallel. Sensor motion tracking active.");
                playChime(750);
            }} else {{
                updateMotionUI(0.0, 'STATIONARY', '⏸ Guide Paused');
                speakText("Virtual guide paused.");
                playChime(440);
            }}
        }};

        window.toggleVoiceAudio = function() {{
            isVoiceOn = !isVoiceOn;
            const icon = document.getElementById('audio-icon');
            const txt = document.getElementById('audio-text');
            if (icon) icon.innerText = isVoiceOn ? '🔊' : '🔇';
            if (txt) txt.innerText = isVoiceOn ? 'Voice: On' : 'Voice: Muted';
            if (!isVoiceOn && 'speechSynthesis' in window) window.speechSynthesis.cancel();
        }};

        window.currentStoryGalleryMode = 'timeline';

        window.openPicturesGallery = function() {{
            const modal = document.getElementById('pictures-modal');
            if (!modal) return;
            renderStorylineGallery(window.currentStoryGalleryMode || 'timeline');
            modal.style.display = 'flex';
        }};

        window.setStoryGalleryView = function(mode) {{
            window.currentStoryGalleryMode = mode;
            const btnTimeline = document.getElementById('story-mode-timeline');
            const btnGrid = document.getElementById('story-mode-grid');
            if (btnTimeline && btnGrid) {{
                if (mode === 'timeline') {{
                    btnTimeline.classList.add('active');
                    btnGrid.classList.remove('active');
                }} else {{
                    btnTimeline.classList.remove('active');
                    btnGrid.classList.add('active');
                }}
            }}
            renderStorylineGallery(mode);
        }};

        function renderStorylineGallery(mode) {{
            const container = document.getElementById('gallery-container-box') || document.getElementById('gallery-grid-items');
            if (!container) return;
            container.innerHTML = '';

            if (mode === 'grid') {{
                const gridDiv = document.createElement('div');
                gridDiv.className = 'storyline-grid-container';
                MANEUVERS.forEach((m, idx) => {{
                    const card = document.createElement('div');
                    card.className = 'storyline-scene-card' + (idx === activeIdx ? ' active' : (idx < activeIdx ? ' completed' : ''));
                    const picSvg = getScenicStepSvg(m.direction_type, m.road_name, m.step_num, m.icon, idx < activeIdx, idx === activeIdx);
                    const cleanNarrative = String(m.aura_speech || m.instruction || '').replace(/^"|"$/g, '');
                    card.innerHTML = `
                        <div class="storyline-scene-header">
                            <div class="scene-chapter-badge">
                                <span>🎬 SCENE #${{m.step_num}}</span>
                                <span style="font-size: 1.15rem;">${{m.icon}}</span>
                            </div>
                            <div class="scene-metrics-badges">
                                <span class="scene-pill-dist">${{m.distance_human}}</span>
                                ${{idx === activeIdx ? '<span class="scene-status-pill active">LIVE</span>' : (idx < activeIdx ? '<span class="scene-status-pill completed">✓</span>' : '<span class="scene-status-pill upcoming">NEXT</span>')}}
                            </div>
                        </div>
                        <div class="storyline-pic-hero" onclick="selectStep(${{idx}}); closePicturesGallery();" title="Jump to Scene #${{m.step_num}}">
                            ${{picSvg}}
                            <div class="storyline-pic-overlay">
                                <span class="pic-road-pill">🛣️ ${{m.road_name || 'Corridor Route'}}</span>
                                <span class="pic-jump-hint">🧭 Jump</span>
                            </div>
                        </div>
                        <div class="storyline-narrative-box">
                            <div class="storyline-headline">${{m.headline}}</div>
                            <div class="storyline-chronicle-text">${{cleanNarrative}}</div>
                            ${{idx < MANEUVERS.length - 1 ? `
                                <div style="display:flex; align-items:center; gap:6px; font-size:0.72rem; color:#38bdf8; font-weight:700; margin-top:4px;">
                                    <span>➔ Leads to:</span>
                                    <span style="color:#e0f2fe;">Scene #${{MANEUVERS[idx+1].step_num}} (${{MANEUVERS[idx+1].road_name || 'Road'}})</span>
                                </div>
                            ` : `
                                <div style="display:flex; align-items:center; gap:6px; font-size:0.72rem; color:#34d399; font-weight:800; margin-top:4px;">
                                    <span>🏁 Final Destination Arrived!</span>
                                </div>
                            `}}
                        </div>
                        <div class="storyline-action-row">
                            <button class="btn-action-pill jump-btn" onclick="selectStep(${{idx}}); closePicturesGallery();">
                                <span>🧭</span> Jump to Scene #${{m.step_num}}
                            </button>
                        </div>
                    `;
                    gridDiv.appendChild(card);
                }});
                container.appendChild(gridDiv);
            }} else {{
                // Continuous Connected Storyline Track
                const streamDiv = document.createElement('div');
                streamDiv.className = 'storyline-stream';

                // Storyline Journey Route Header Strip
                const banner = document.createElement('div');
                banner.style.cssText = 'width: 100%; display: flex; align-items: center; justify-content: space-between; background: rgba(15, 23, 42, 0.7); border: 1.5px solid rgba(56, 189, 248, 0.3); border-radius: 14px; padding: 12px 18px; margin-bottom: 22px; gap: 12px; flex-wrap: wrap; box-shadow: 0 4px 18px rgba(0,0,0,0.5); box-sizing: border-box;';
                banner.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 1.6rem;">🗺️</span>
                        <div>
                            <div style="font-size: 0.95rem; font-weight: 900; color: #ffffff;">VISUAL ROUTE STORYLINE • ${{MANEUVERS.length}} CONNECTED EPISODES</div>
                            <div style="font-size: 0.76rem; color: #94a3b8;">Sequential visual narrative linking departure to destination</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 0.74rem; font-weight: 800; color: #38bdf8; background: rgba(56, 189, 248, 0.12); border: 1px solid rgba(56, 189, 248, 0.3); padding: 4px 10px; border-radius: 999px;">
                            📍 Scene 1 ➔ Scene ${{MANEUVERS.length}}
                        </span>
                    </div>
                `;
                streamDiv.appendChild(banner);

                MANEUVERS.forEach((m, idx) => {{
                    const card = document.createElement('div');
                    card.className = 'storyline-scene-card' + (idx === activeIdx ? ' active' : (idx < activeIdx ? ' completed' : ''));
                    const picSvg = getScenicStepSvg(m.direction_type, m.road_name, m.step_num, m.icon, idx < activeIdx, idx === activeIdx);
                    const cleanNarrative = String(m.aura_speech || m.instruction || '').replace(/^"|"$/g, '');

                    let chapterTitle = 'WAYPOINT MILESTONE';
                    const dt = (m.direction_type || '').toUpperCase();
                    if (dt.includes('START') || dt.includes('DEPART')) chapterTitle = 'THE DEPARTURE JOURNEY';
                    else if (dt.includes('ARRIVE') || dt.includes('DEST')) chapterTitle = 'DESTINATION ARRIVAL CELEBRATION';
                    else if (dt.includes('LEFT')) chapterTitle = 'LEFT TURN CORRIDOR';
                    else if (dt.includes('RIGHT')) chapterTitle = 'RIGHT TURN CORRIDOR';
                    else if (dt.includes('ROUNDABOUT')) chapterTitle = 'ROTARY TRANSIT INTERCHANGE';
                    else if (dt.includes('CRUISE') || dt.includes('STRAIGHT')) chapterTitle = 'OPEN HIGHWAY CRUISING STRETCH';

                    card.innerHTML = `
                        <div class="storyline-scene-header">
                            <div class="scene-chapter-badge">
                                <span style="font-size: 1.15rem;">${{m.icon}}</span>
                                <span>🎬 CHAPTER ${{m.step_num}} OF ${{MANEUVERS.length}} • ${{chapterTitle}}</span>
                            </div>
                            <div class="scene-metrics-badges">
                                <span class="scene-pill-dist">📏 ${{m.distance_human}}</span>
                                <span class="scene-pill-time">⏱️ ~${{m.time_estimate}}</span>
                                ${{idx === activeIdx ? '<span class="scene-status-pill active">⚡ ACTIVE SCENE</span>' : (idx < activeIdx ? '<span class="scene-status-pill completed">✓ COMPLETED</span>' : '<span class="scene-status-pill upcoming">⏳ UPCOMING</span>')}}
                            </div>
                        </div>

                        <div class="storyline-pic-hero" onclick="selectStep(${{idx}}); closePicturesGallery();" title="Click to view Scene #${{m.step_num}} in 3D Companion">
                            ${{picSvg}}
                            <div class="storyline-pic-overlay">
                                <span class="pic-road-pill">🛣️ ${{m.road_name || 'Corridor Route'}}</span>
                                <span class="pic-jump-hint">🧭 Click Scene to View in 3D</span>
                            </div>
                        </div>

                        <div class="storyline-narrative-box">
                            <div class="storyline-headline">${{m.headline}}</div>
                            <div class="storyline-chronicle-text">
                                <span style="color: #38bdf8; font-weight: 700;">Storyline Chronicle: </span>
                                "${{cleanNarrative}}"
                            </div>
                            ${{m.what_to_look_for ? `
                                <div class="storyline-landmark-strip">
                                    <span style="font-size: 0.88rem;">👀</span>
                                    <span style="font-weight: 800; color: #38bdf8;">Visual Scenery Cues:</span>
                                    <span style="color: #e2e8f0;">${{m.what_to_look_for}}</span>
                                </div>
                            ` : ''}}
                        </div>

                        <div class="storyline-action-row">
                            <button class="btn-action-pill jump-btn" onclick="selectStep(${{idx}}); closePicturesGallery();">
                                <span>🧭</span> Jump Cockpit to Scene #${{m.step_num}}
                            </button>
                        </div>
                    `;
                    streamDiv.appendChild(card);

                    // Add visual Storyline Connector between scenes
                    if (idx < MANEUVERS.length - 1) {{
                        const nextM = MANEUVERS[idx + 1];
                        const connector = document.createElement('div');
                        connector.className = 'storyline-connector-segment';
                        connector.innerHTML = `
                            <div class="storyline-connector-line"></div>
                            <div class="storyline-connector-ribbon">
                                <span class="connector-arrow">↓</span>
                                <span class="connector-badge">
                                    <span>🛣️</span>
                                    <span>CONTINUING STORYLINE ➔ TRANSIT TO SCENE #${{nextM.step_num}}: ${{nextM.road_name || 'Corridor'}} (~${{nextM.distance_human}})</span>
                                </span>
                                <span class="connector-arrow">↓</span>
                            </div>
                            <div class="storyline-connector-line"></div>
                        `;
                        streamDiv.appendChild(connector);
                    }}
                }});

                container.appendChild(streamDiv);
            }}
        }}

        window.closePicturesGallery = function() {{
            const modal = document.getElementById('pictures-modal');
            if (modal) modal.style.display = 'none';
        }};

        // =========================================================================
        // DYNAMIC VEHICLE MODE-BASED VIRTUAL GUIDE SUITE
        // =========================================================================
        {vehicle_suite_js}

        window.activeVehicleMode = '{norm_travel_mode}';
        window.switchVehicleMode = function(newMode) {{
            const raw = String(newMode || 'CAR').toUpperCase().trim();
            const aliases = {{
                'CAR': 'CAR', 'DRIVING': 'CAR', 'AUTOMOBILE': 'CAR', 'TAXI': 'CAR', 'CAB': 'CAR',
                'BIKE': 'BIKE', 'MOTORCYCLE': 'BIKE', 'MOTORBIKE': 'BIKE', 'SCOOTER': 'BIKE',
                'BUS': 'BUS', 'TRANSIT': 'BUS', 'COACH': 'BUS',
                'CYCLE': 'BICYCLE', 'BICYCLE': 'BICYCLE', 'CYCLING': 'BICYCLE', 'BIKING': 'BICYCLE',
                'WALK': 'WALK', 'WALKING': 'WALK', 'PEDESTRIAN': 'WALK',
                'TRUCK': 'TRUCK', 'HEAVY': 'TRUCK', 'LORRY': 'TRUCK', 'SEMI': 'TRUCK',
                'TRACTOR': 'TRACTOR', 'AGRO': 'TRACTOR', 'FARM': 'TRACTOR',
                'FLIGHT': 'FLIGHT', 'PLANE': 'FLIGHT', 'AIRPLANE': 'FLIGHT', 'AIR': 'FLIGHT', 'AVIATION': 'FLIGHT',
                'SHIP': 'WATERWAY', 'BOAT': 'WATERWAY', 'FERRY': 'WATERWAY', 'WATERWAY': 'WATERWAY',
                'TRAIN': 'TRAIN', 'RAIL': 'TRAIN', 'RAILWAY': 'TRAIN', 'METRO': 'TRAIN', 'SUBWAY': 'TRAIN'
            }};
            const norm = aliases[raw] || 'CAR';
            window.activeVehicleMode = norm;

            // 1. Highlight clicked vehicle in the bottom toolbar
            const vehBtns = document.querySelectorAll('.btn-veh-selector');
            vehBtns.forEach(function(b) {{
                if (b.getAttribute('data-mode') === norm || b.id === 'btn-veh-' + norm) {{
                    b.classList.add('active');
                }} else {{
                    b.classList.remove('active');
                }}
            }});

            // 2. Synchronize HUD Vehicle Mode Badge
            const vBadge = document.getElementById('hud-vehicle-mode');
            if (vBadge) {{
                const modeNames = {{
                    'CAR': 'CAR', 'BIKE': 'BIKE / MOTO', 'BUS': 'TRANSIT BUS',
                    'BICYCLE': 'BICYCLE', 'WALK': 'PEDESTRIAN', 'TRUCK': 'HEAVY TRUCK',
                    'TRACTOR': 'AGRO TRACTOR', 'FLIGHT': 'AIR FLIGHT', 'WATERWAY': 'CRUISE SHIP',
                    'TRAIN': 'EXPRESS TRAIN'
                }};
                vBadge.innerText = 'VEHICLE: ' + (modeNames[norm] || norm);
            }}

            // 3. Synchronize 3D Three.js active vehicle controller if available
            if (window.activeVehicleController) {{
                window.activeVehicleController.setMode(norm);
            }}

            // 4. Futuristic High-Tech Audio Feedback Tone
            try {{
                const AudioCtx = window.AudioContext || window.webkitAudioContext;
                if (AudioCtx) {{
                    const actx = new AudioCtx();
                    const osc = actx.createOscillator();
                    const gain = actx.createGain();
                    osc.connect(gain);
                    gain.connect(actx.destination);
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(520, actx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(880, actx.currentTime + 0.12);
                    gain.gain.setValueAtTime(0.12, actx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, actx.currentTime + 0.15);
                    osc.start();
                    osc.stop(actx.currentTime + 0.16);
                }}
            }} catch(e) {{}}
        }};

        // =========================================================================
        // THREE.JS 3D AURA ROBOT & ROADWAY SCENE ENGINE
        // =========================================================================
        let threeEnv = null;
        let threeSceneStarted = false;
        let threeAnimId = null;
        let fallback2DAnimId = null;

        function safeLerp(a, b, t) {{
            return a + (b - a) * t;
        }}

        function initAuraThreeScene() {{
            const canvas = document.getElementById('aura-threejs-canvas');
            const scenicCanvas = document.getElementById('aura-scenic-canvas');
            const container = document.getElementById('aura-3d-scene-box');
            if (!canvas || !container || typeof THREE === 'undefined') return false;

            try {{
                // Ensure canvas is visible before WebGL context creation to avoid 0x0 buffer allocation
                canvas.style.display = 'block';

                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x38bdf8);
                scene.fog = new THREE.FogExp2(0xc7d2fe, 0.0075);

                const width = container.clientWidth > 0 ? container.clientWidth : 800;
                const height = container.clientHeight > 0 ? container.clientHeight : 360;

                const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 800);
                camera.position.set(0, 2.3, -4.2);
                camera.lookAt(0, 1.1, 3.0);

                const renderer = new THREE.WebGLRenderer({{
                    canvas: canvas,
                    antialias: true,
                    alpha: false,
                    powerPreference: "default",
                    preserveDrawingBuffer: true
                }});
                renderer.setSize(width, height);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

                canvas.addEventListener('webglcontextlost', function(e) {{
                    e.preventDefault();
                    console.warn("WebGL context lost; switching to resilient 2.5D companion.");
                    threeSceneStarted = false;
                    if (threeAnimId) cancelAnimationFrame(threeAnimId);
                    if (scenicCanvas) scenicCanvas.style.display = 'block';
                    canvas.style.display = 'none';
                    startScenicFallback2D();
                }}, false);

                // -----------------------------------------------------------------
                // 1. ATMOSPHERIC NATURAL LIGHTING
                // -----------------------------------------------------------------
                // Natural Hemisphere Light (Sky Blue above + Fresh Grass bounce below)
                const hemiLight = new THREE.HemisphereLight(0x7dd3fc, 0x15803d, 0.85);
                scene.add(hemiLight);

                const ambientLight = new THREE.AmbientLight(0xffffff, 0.35);
                scene.add(ambientLight);

                // Directional Sunlight with Soft Shadows
                const dirLight = new THREE.DirectionalLight(0xfffaed, 1.35);
                dirLight.position.set(28, 52, 28);
                dirLight.castShadow = true;
                dirLight.shadow.mapSize.width = 1024;
                dirLight.shadow.mapSize.height = 1024;
                dirLight.shadow.camera.near = 0.5;
                dirLight.shadow.camera.far = 180;
                dirLight.shadow.camera.left = -35;
                dirLight.shadow.camera.right = 35;
                dirLight.shadow.camera.top = 35;
                dirLight.shadow.camera.bottom = -35;
                scene.add(dirLight);

                // -----------------------------------------------------------------
                // 2. DYNAMIC REALISTIC SKY DOME & CELESTIAL BODIES
                // -----------------------------------------------------------------
                function makeSkyTexture(topHex, midHex, botHex) {{
                    const sc = document.createElement('canvas');
                    sc.width = 128; sc.height = 256;
                    const sctx = sc.getContext('2d');
                    const grad = sctx.createLinearGradient(0, 0, 0, 256);
                    grad.addColorStop(0.0, topHex);
                    grad.addColorStop(0.55, midHex);
                    grad.addColorStop(1.0, botHex);
                    sctx.fillStyle = grad;
                    sctx.fillRect(0, 0, 128, 256);
                    const tex = new THREE.CanvasTexture(sc);
                    tex.generateMipmaps = false;
                    tex.minFilter = THREE.LinearFilter;
                    return tex;
                }}

                const skyGeo = new THREE.SphereGeometry(260, 32, 16);
                const skyMat = new THREE.MeshBasicMaterial({{
                    map: makeSkyTexture('#1d4ed8', '#38bdf8', '#e0f2fe'),
                    side: THREE.BackSide
                }});
                const skyMesh = new THREE.Mesh(skyGeo, skyMat);
                scene.add(skyMesh);

                // Sun & Moon
                const celestialGroup = new THREE.Group();
                const sunGeo = new THREE.CircleGeometry(7.0, 24);
                const sunMat = new THREE.MeshBasicMaterial({{ color: 0xfffae0, side: THREE.DoubleSide }});
                const sunMesh = new THREE.Mesh(sunGeo, sunMat);
                sunMesh.position.set(40, 68, 110);
                sunMesh.lookAt(0, 0, 0);
                celestialGroup.add(sunMesh);

                const sunGlowGeo = new THREE.CircleGeometry(16.0, 24);
                const sunGlowMat = new THREE.MeshBasicMaterial({{ color: 0xfef08a, transparent: true, opacity: 0.35, side: THREE.DoubleSide }});
                const sunGlowMesh = new THREE.Mesh(sunGlowGeo, sunGlowMat);
                sunGlowMesh.position.copy(sunMesh.position);
                sunGlowMesh.lookAt(0, 0, 0);
                celestialGroup.add(sunGlowMesh);

                const moonGeo = new THREE.CircleGeometry(5.5, 24);
                const moonMat = new THREE.MeshBasicMaterial({{ color: 0xf1f5f9, transparent: true, opacity: 0, side: THREE.DoubleSide }});
                const moonMesh = new THREE.Mesh(moonGeo, moonMat);
                moonMesh.position.set(-35, 55, 95);
                moonMesh.lookAt(0, 0, 0);
                celestialGroup.add(moonMesh);
                scene.add(celestialGroup);

                // Soft 3D Procedural Drifting Clouds
                const cloudGroup = new THREE.Group();
                const cloudGeo = new THREE.DodecahedronGeometry(1.6, 1);
                const cloudMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, roughness: 0.95, transparent: true, opacity: 0.85 }});
                const cloudList = [];
                for (let c = 0; c < 9; c++) {{
                    const cluster = new THREE.Group();
                    const blobs = 5 + Math.floor(Math.random() * 4);
                    for (let b = 0; b < blobs; b++) {{
                        const puff = new THREE.Mesh(cloudGeo, cloudMat);
                        puff.position.set((Math.random() - 0.5) * 6, (Math.random() - 0.5) * 1.6, (Math.random() - 0.5) * 4);
                        const s = 1.3 + Math.random() * 1.9;
                        puff.scale.set(s, s * 0.5, s);
                        cluster.add(puff);
                    }}
                    cluster.position.set(-70 + Math.random() * 140, 26 + Math.random() * 16, -30 + Math.random() * 120);
                    cloudGroup.add(cluster);
                    cloudList.push({{ obj: cluster, speed: 0.012 + Math.random() * 0.016 }});
                }}
                scene.add(cloudGroup);

                // Twinkling Starfield (Active at Night)
                const starCount = 380;
                const starGeo = new THREE.BufferGeometry();
                const starPos = new Float32Array(starCount * 3);
                for (let i = 0; i < starCount; i++) {{
                    const u = Math.random();
                    const v = Math.random();
                    const theta = u * 2.0 * Math.PI;
                    const phi = Math.acos(2.0 * v - 1.0) * 0.48;
                    const r = 240;
                    starPos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
                    starPos[i * 3 + 1] = Math.abs(r * Math.cos(phi)) + 15;
                    starPos[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta);
                }}
                starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
                const starMat = new THREE.PointsMaterial({{ color: 0xffffff, size: 1.8, transparent: true, opacity: 0 }});
                const starField = new THREE.Points(starGeo, starMat);
                scene.add(starField);

                // -----------------------------------------------------------------
                // 3. LUSH CAMPUS LANDSCAPE & GRASS TERRAIN
                // -----------------------------------------------------------------
                function makeGrassTexture() {{
                    const gc = document.createElement('canvas');
                    gc.width = 256; gc.height = 256;
                    const gctx = gc.getContext('2d');
                    gctx.fillStyle = '#2d6a2e';
                    gctx.fillRect(0, 0, 256, 256);
                    for (let i = 0; i < 700; i++) {{
                        const gx = Math.random() * 256;
                        const gy = Math.random() * 256;
                        const gr = 2 + Math.random() * 5;
                        gctx.fillStyle = Math.random() > 0.5 ? 'rgba(54, 138, 56, 0.45)' : 'rgba(28, 77, 30, 0.45)';
                        gctx.beginPath();
                        gctx.arc(gx, gy, gr, 0, Math.PI * 2);
                        gctx.fill();
                    }}
                    const tex = new THREE.CanvasTexture(gc);
                    tex.wrapS = THREE.RepeatWrapping;
                    tex.wrapT = THREE.RepeatWrapping;
                    tex.repeat.set(36, 36);
                    return tex;
                }}

                const groundGeo = new THREE.PlaneGeometry(360, 360, 20, 20);
                const groundMat = new THREE.MeshStandardMaterial({{
                    map: makeGrassTexture(),
                    roughness: 0.95,
                    metalness: 0.05
                }});
                const groundMesh = new THREE.Mesh(groundGeo, groundMat);
                groundMesh.rotation.x = -Math.PI / 2;
                groundMesh.position.y = -0.05;
                groundMesh.receiveShadow = true;
                scene.add(groundMesh);

                // -----------------------------------------------------------------
                // 4. REALISTIC CURVING ROADWAY, CURBS, SIDEWALKS & MARKINGS
                // -----------------------------------------------------------------
                const roadGroup = new THREE.Group();
                const roadSplinePts = [];
                for (let i = 0; i <= 26; i++) {{
                    const z = (i - 8) * 4.5;
                    const x = Math.sin(i * 0.32) * 3.4;
                    roadSplinePts.push(new THREE.Vector3(x, 0, z));
                }}
                const roadSpline = new THREE.CatmullRomCurve3(roadSplinePts);

                // Main Asphalt Road Bed (Dark textured charcoal asphalt)
                const roadGeo = new THREE.TubeGeometry(roadSpline, 80, 2.7, 8, false);
                const roadMat = new THREE.MeshStandardMaterial({{ color: 0x1e242d, roughness: 0.86, metalness: 0.12 }});
                const roadMesh = new THREE.Mesh(roadGeo, roadMat);
                roadMesh.scale.set(1, 0.045, 1);
                roadMesh.receiveShadow = true;
                roadGroup.add(roadMesh);

                // Left & Right Raised Concrete Curbs
                const curbMat = new THREE.MeshStandardMaterial({{ color: 0x94a3b8, roughness: 0.75 }});
                const curbLeftGeo = new THREE.TubeGeometry(roadSpline, 80, 0.18, 6, false);
                const curbLeft = new THREE.Mesh(curbLeftGeo, curbMat);
                curbLeft.position.set(-2.7, 0.06, 0);
                roadGroup.add(curbLeft);

                const curbRight = new THREE.Mesh(curbLeftGeo, curbMat);
                curbRight.position.set(2.7, 0.06, 0);
                roadGroup.add(curbRight);

                // Left & Right Paved Sidewalks
                const swMat = new THREE.MeshStandardMaterial({{ color: 0x475569, roughness: 0.85 }});
                const swGeo = new THREE.TubeGeometry(roadSpline, 80, 1.25, 6, false);

                const swLeft = new THREE.Mesh(swGeo, swMat);
                swLeft.position.set(-3.85, 0.06, 0);
                swLeft.scale.set(1, 0.04, 1);
                roadGroup.add(swLeft);

                const swRight = new THREE.Mesh(swGeo, swMat);
                swRight.position.set(3.85, 0.06, 0);
                swRight.scale.set(1, 0.04, 1);
                roadGroup.add(swRight);

                // Road Edge Painted White Markings
                const edgeLineMat = new THREE.MeshBasicMaterial({{ color: 0xf8fafc }});
                const edgeLineGeo = new THREE.TubeGeometry(roadSpline, 80, 0.06, 4, false);

                const edgeL = new THREE.Mesh(edgeLineGeo, edgeLineMat);
                edgeL.position.set(-2.4, 0.06, 0);
                roadGroup.add(edgeL);

                const edgeR = new THREE.Mesh(edgeLineGeo, edgeLineMat);
                edgeR.position.set(2.4, 0.06, 0);
                roadGroup.add(edgeR);

                // Dashed Road Centerline
                const dashMat = new THREE.MeshBasicMaterial({{ color: 0xfbbf24 }});
                for (let s = 0; s < 40; s++) {{
                    if (s % 2 === 0) {{
                        const t = s / 40;
                        const pt = roadSpline.getPointAt(t);
                        const tan = roadSpline.getTangentAt(t);
                        const dashBox = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.02, 1.1), dashMat);
                        dashBox.position.set(pt.x, 0.065, pt.z);
                        dashBox.lookAt(pt.x + tan.x, 0.065, pt.z + tan.z);
                        roadGroup.add(dashBox);
                    }}
                }}

                // Glowing Cyan AR Trajectory Ribbon
                const ribbonGeo = new THREE.TubeGeometry(roadSpline, 80, 0.24, 6, false);
                const ribbonMat = new THREE.MeshBasicMaterial({{ color: 0x00f0ff, transparent: true, opacity: 0.92 }});
                const ribbonMesh = new THREE.Mesh(ribbonGeo, ribbonMat);
                ribbonMesh.position.y = 0.16;
                roadGroup.add(ribbonMesh);

                scene.add(roadGroup);

                // -----------------------------------------------------------------
                // 5. MODERN STREETLIGHTS & REALISTIC LAMP POSTS
                // -----------------------------------------------------------------
                const streetLampGroup = new THREE.Group();
                const lampLights = [];
                const poleMat = new THREE.MeshStandardMaterial({{ color: 0x1e293b, metalness: 0.7, roughness: 0.3 }});
                const lampHeadMat = new THREE.MeshStandardMaterial({{ color: 0x0f172a }});
                const lampGlassMat = new THREE.MeshBasicMaterial({{ color: 0xffffff }});

                const lampZList = [-22, -8, 8, 24, 40, 56, 72];
                lampZList.forEach((lz, idx) => {{
                    const t = Math.max(0, Math.min(1, (lz + 35) / 115));
                    const pt = roadSpline.getPointAt(t);
                    const side = (idx % 2 === 0) ? 1 : -1;
                    const postGroup = new THREE.Group();
                    postGroup.position.set(pt.x + side * 4.6, 0, pt.z);

                    // Vertical Steel Pole
                    const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.09, 4.4, 12), poleMat);
                    pole.position.y = 2.2;
                    pole.castShadow = true;
                    postGroup.add(pole);

                    // Curved Top Arm
                    const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.05, 1.5, 8), poleMat);
                    arm.rotation.z = -side * 1.1;
                    arm.position.set(-side * 0.6, 4.4, 0);
                    postGroup.add(arm);

                    // Lamp Fixture
                    const head = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.14, 0.24), lampHeadMat);
                    head.position.set(-side * 1.25, 4.25, 0);
                    postGroup.add(head);

                    const glass = new THREE.Mesh(new THREE.PlaneGeometry(0.38, 0.20), lampGlassMat);
                    glass.rotation.x = Math.PI / 2;
                    glass.position.set(-side * 1.25, 4.17, 0);
                    postGroup.add(glass);

                    // Illuminating PointLight onto the asphalt
                    const pLight = new THREE.PointLight(0xfef08a, 0.0, 11, 1.6);
                    pLight.position.set(pt.x + side * 3.35, 4.1, pt.z);
                    scene.add(pLight);
                    lampLights.push({{ light: pLight, glass: glass }});

                    streetLampGroup.add(postGroup);
                }});
                scene.add(streetLampGroup);

                // -----------------------------------------------------------------
                // 6. LUSH TREES, FOLIAGE & BLOOMING SHRUBS
                // -----------------------------------------------------------------
                const foliageGroup = new THREE.Group();
                const treeSwayList = [];

                const trunkMat = new THREE.MeshStandardMaterial({{ color: 0x4a2e18, roughness: 0.9 }});
                const greenMats = [
                    new THREE.MeshStandardMaterial({{ color: 0x15803d, roughness: 0.82 }}),
                    new THREE.MeshStandardMaterial({{ color: 0x16a34a, roughness: 0.85 }}),
                    new THREE.MeshStandardMaterial({{ color: 0x14532d, roughness: 0.90 }}),
                    new THREE.MeshStandardMaterial({{ color: 0x166534, roughness: 0.84 }})
                ];
                const flowerMats = [
                    new THREE.MeshBasicMaterial({{ color: 0xf43f5e }}),
                    new THREE.MeshBasicMaterial({{ color: 0xfbbf24 }}),
                    new THREE.MeshBasicMaterial({{ color: 0xec4899 }})
                ];

                for (let s = 0; s < 36; s++) {{
                    const t = s / 36;
                    const pt = roadSpline.getPointAt(t);
                    const side = (s % 2 === 0) ? -1 : 1;
                    const dist = 5.6 + Math.random() * 3.5;

                    const tree = new THREE.Group();
                    tree.position.set(pt.x + side * dist, 0, pt.z + (Math.random() - 0.5) * 3);

                    const isPine = (s % 3 === 0);
                    const heightScale = 0.8 + Math.random() * 0.5;

                    if (isPine) {{
                        // Conifer / Pine Tree
                        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.20, 2.2 * heightScale, 8), trunkMat);
                        trunk.position.y = 1.1 * heightScale;
                        tree.add(trunk);

                        const tiers = 3;
                        for (let tr = 0; tr < tiers; tr++) {{
                            const cMat = greenMats[tr % greenMats.length];
                            const cone = new THREE.Mesh(new THREE.ConeGeometry((1.6 - tr * 0.35) * heightScale, 1.8 * heightScale, 8), cMat);
                            cone.position.y = (1.8 + tr * 1.1) * heightScale;
                            cone.castShadow = true;
                            tree.add(cone);
                        }}
                    }} else {{
                        // Leafy Deciduous Canopy Tree
                        const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.24, 2.0 * heightScale, 8), trunkMat);
                        trunk.position.y = 1.0 * heightScale;
                        tree.add(trunk);

                        const crownMat = greenMats[s % greenMats.length];
                        const crown = new THREE.Mesh(new THREE.DodecahedronGeometry(1.6 * heightScale, 1), crownMat);
                        crown.position.y = 2.8 * heightScale;
                        crown.castShadow = true;
                        tree.add(crown);

                        const subCrown = new THREE.Mesh(new THREE.DodecahedronGeometry(1.1 * heightScale, 1), greenMats[(s + 1) % greenMats.length]);
                        subCrown.position.set(0.4 * heightScale, 3.4 * heightScale, 0.2 * heightScale);
                        tree.add(subCrown);
                    }}

                    // Shrub or blooming flower bush at the base
                    const shrub = new THREE.Mesh(new THREE.SphereGeometry(0.45 * heightScale, 8, 8), greenMats[2]);
                    shrub.position.set((Math.random() - 0.5) * 0.8, 0.25 * heightScale, (Math.random() - 0.5) * 0.8);
                    tree.add(shrub);

                    if (s % 2 === 0) {{
                        const fl = new THREE.Mesh(new THREE.DodecahedronGeometry(0.2, 0), flowerMats[s % flowerMats.length]);
                        fl.position.set(shrub.position.x + 0.1, 0.45 * heightScale, shrub.position.z + 0.1);
                        tree.add(fl);
                    }}

                    foliageGroup.add(tree);
                    treeSwayList.push({{ group: tree, phase: Math.random() * Math.PI * 2 }});
                }}
                scene.add(foliageGroup);

                // -----------------------------------------------------------------
                // 7. MODERN CAMPUS ARCHITECTURE & BACKGROUND BUILDINGS
                // -----------------------------------------------------------------
                const cityGroup = new THREE.Group();
                const windowMats = [];

                function makeBuildingWindowTexture(lit) {{
                    const wc = document.createElement('canvas');
                    wc.width = 64; wc.height = 128;
                    const wctx = wc.getContext('2d');
                    wctx.fillStyle = '#1e293b';
                    wctx.fillRect(0, 0, 64, 128);
                    for (let r = 0; r < 8; r++) {{
                        for (let c = 0; c < 4; c++) {{
                            if (lit) {{
                                const rand = Math.random();
                                wctx.fillStyle = rand > 0.4 ? '#fef08a' : (rand > 0.2 ? '#38bdf8' : '#0f172a');
                            }} else {{
                                wctx.fillStyle = Math.random() > 0.3 ? '#60a5fa' : '#334155';
                            }}
                            wctx.fillRect(c * 15 + 4, r * 15 + 6, 10, 10);
                        }}
                    }}
                    const tex = new THREE.CanvasTexture(wc);
                    tex.wrapS = THREE.RepeatWrapping;
                    tex.wrapT = THREE.RepeatWrapping;
                    return tex;
                }}

                const bldgColors = [0x1e293b, 0x334155, 0x0f172a, 0x1e242d, 0x475569];
                const bldgConfigs = [
                    {{ x: -18, z: -15, w: 9, d: 8, h: 14 }},
                    {{ x: -22, z: 12, w: 10, d: 9, h: 20 }},
                    {{ x: -19, z: 38, w: 8, d: 7, h: 16 }},
                    {{ x: -24, z: 65, w: 11, d: 10, h: 22 }},
                    {{ x: 19, z: -10, w: 9, d: 8, h: 15 }},
                    {{ x: 22, z: 18, w: 10, d: 9, h: 18 }},
                    {{ x: 20, z: 45, w: 8, d: 8, h: 13 }},
                    {{ x: 25, z: 72, w: 12, d: 10, h: 24 }},
                    {{ x: -32, z: 25, w: 14, d: 12, h: 28 }},
                    {{ x: 34, z: 32, w: 13, d: 11, h: 26 }}
                ];

                bldgConfigs.forEach((b, idx) => {{
                    const bGroup = new THREE.Group();
                    bGroup.position.set(b.x, 0, b.z);

                    const bMat = new THREE.MeshStandardMaterial({{
                        color: bldgColors[idx % bldgColors.length],
                        map: makeBuildingWindowTexture(false),
                        roughness: 0.65,
                        metalness: 0.2
                    }});
                    bMat.map.repeat.set(Math.ceil(b.w / 5), Math.ceil(b.h / 5));
                    windowMats.push(bMat);

                    const bMesh = new THREE.Mesh(new THREE.BoxGeometry(b.w, b.h, b.d), bMat);
                    bMesh.position.y = b.h / 2;
                    bMesh.castShadow = true;
                    bMesh.receiveShadow = true;
                    bGroup.add(bMesh);

                    // Modern Rooftop Parapet & Antenna
                    const roofTrim = new THREE.Mesh(new THREE.BoxGeometry(b.w + 0.4, 0.4, b.d + 0.4), new THREE.MeshStandardMaterial({{ color: 0x0f172a }}));
                    roofTrim.position.y = b.h + 0.2;
                    bGroup.add(roofTrim);

                    if (b.h > 16) {{
                        const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.12, 3.5, 6), new THREE.MeshStandardMaterial({{ color: 0x94a3b8 }}));
                        mast.position.y = b.h + 1.8;
                        bGroup.add(mast);

                        const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.2, 8, 8), new THREE.MeshBasicMaterial({{ color: 0xef4444 }}));
                        beacon.position.y = b.h + 3.6;
                        bGroup.add(beacon);
                    }}

                    cityGroup.add(bGroup);
                }});
                scene.add(cityGroup);

                // Build Aura: Cute 3D Robot Companion with Glowing Navigation Stick
                const auraRoot = new THREE.Group();

                // Materials
                const chassisMat = new THREE.MeshStandardMaterial({{ color: 0x0f2b48, metalness: 0.8, roughness: 0.25 }});
                const glowCyanMat = new THREE.MeshStandardMaterial({{ color: 0x00f0ff, emissive: 0x00d9ff, emissiveIntensity: 0.8 }});
                const goldMat = new THREE.MeshStandardMaterial({{ color: 0xf59e0b, metalness: 0.9, roughness: 0.2 }});
                const visorScreenMat = new THREE.MeshStandardMaterial({{ color: 0x030712, roughness: 0.1 }});
                const eyeMat = new THREE.MeshBasicMaterial({{ color: 0x38bdf8 }});

                // Torso & Reactor Core
                const torso = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.32, 0.75, 20), chassisMat);
                torso.position.y = 0.95;
                auraRoot.add(torso);

                const coreReactor = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.04, 16), glowCyanMat);
                coreReactor.rotation.x = Math.PI / 2;
                coreReactor.position.set(0, 0.98, 0.33);
                auraRoot.add(coreReactor);

                // Head with Digital Visor Screen
                const headGroup = new THREE.Group();
                headGroup.position.set(0, 1.55, 0);

                const headChassis = new THREE.Mesh(new THREE.SphereGeometry(0.32, 24, 20), chassisMat);
                headGroup.add(headChassis);

                const visorScreen = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.20, 0.15), visorScreenMat);
                visorScreen.position.set(0, 0.02, 0.26);
                headGroup.add(visorScreen);

                // Glowing Digital Eyes
                const eyeL = new THREE.Mesh(new THREE.SphereGeometry(0.042, 12, 12), eyeMat);
                eyeL.position.set(-0.11, 0.04, 0.34);
                headGroup.add(eyeL);

                const eyeR = new THREE.Mesh(new THREE.SphereGeometry(0.042, 12, 12), eyeMat);
                eyeR.position.set(0.11, 0.04, 0.34);
                headGroup.add(eyeR);

                // Digital Smile
                const smile = new THREE.Mesh(new THREE.TorusGeometry(0.05, 0.012, 8, 16, Math.PI * 0.75), glowCyanMat);
                smile.rotation.x = Math.PI;
                smile.position.set(0, -0.04, 0.34);
                headGroup.add(smile);

                // Cute Antenna with glowing beacon tip
                const antennaStem = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.18, 8), goldMat);
                antennaStem.position.set(0, 0.38, 0);
                headGroup.add(antennaStem);

                const antennaOrb = new THREE.Mesh(new THREE.SphereGeometry(0.05, 12, 12), glowCyanMat);
                antennaOrb.position.set(0, 0.48, 0);
                headGroup.add(antennaOrb);

                auraRoot.add(headGroup);

                // Articulated Arms
                // Left Arm
                const armLGroup = new THREE.Group();
                armLGroup.position.set(-0.46, 1.15, 0);
                const armLMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.04, 0.48, 12), chassisMat);
                armLMesh.position.y = -0.22;
                armLGroup.add(armLMesh);
                auraRoot.add(armLGroup);

                // Right Arm (Holding Glowing Navigation Stick)
                const armRGroup = new THREE.Group();
                armRGroup.position.set(0.46, 1.15, 0);
                const armRMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.04, 0.48, 12), chassisMat);
                armRMesh.position.y = -0.22;
                armRGroup.add(armRMesh);

                // GLOWING NAVIGATION STICK (Aura's signature tool)
                const navStickGroup = new THREE.Group();
                navStickGroup.position.set(0, -0.42, 0.15);

                const stickShaft = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.85, 12), goldMat);
                navStickGroup.add(stickShaft);

                const stickCrystal = new THREE.Mesh(new THREE.SphereGeometry(0.09, 16, 16), glowCyanMat);
                stickCrystal.position.set(0, 0.45, 0);
                navStickGroup.add(stickCrystal);

                // PointLight emitted directly from the navigation stick
                const stickLight = new THREE.PointLight(0x00f0ff, 1.5, 4.0);
                stickLight.position.set(0, 0.45, 0);
                navStickGroup.add(stickLight);

                armRGroup.add(navStickGroup);
                auraRoot.add(armRGroup);

                // Articulated Legs & Magnetic Boots
                const legLGroup = new THREE.Group();
                legLGroup.position.set(-0.20, 0.58, 0);
                const legLMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.06, 0.52, 12), chassisMat);
                legLMesh.position.y = -0.25;
                legLGroup.add(legLMesh);
                const bootL = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.09, 0.22), glowCyanMat);
                bootL.position.set(0, -0.52, 0.04);
                legLGroup.add(bootL);
                auraRoot.add(legLGroup);

                const legRGroup = new THREE.Group();
                legRGroup.position.set(0.20, 0.58, 0);
                const legRMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.06, 0.52, 12), chassisMat);
                legRMesh.position.y = -0.25;
                legRGroup.add(legRMesh);
                const bootR = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.09, 0.22), glowCyanMat);
                bootR.position.set(0, -0.52, 0.04);
                legRGroup.add(bootR);
                auraRoot.add(legRGroup);

                // Glowing Aura Celebration Ring on Ground
                const ringGeo = new THREE.RingGeometry(0.4, 0.65, 24);
                const ringMat = new THREE.MeshBasicMaterial({{ color: 0x00f0ff, side: THREE.DoubleSide, transparent: true, opacity: 0.7 }});
                const auraRing = new THREE.Mesh(ringGeo, ringMat);
                auraRing.rotation.x = -Math.PI / 2;
                auraRing.position.y = 0.05;
                auraRoot.add(auraRing);

                scene.add(auraRoot);

                // Connect Dynamic Vehicle Controller
                const auraLimbs = {{
                    head: headGroup,
                    torso: torso,
                    armL: armLGroup,
                    armR: armRGroup,
                    legL: legLGroup,
                    legR: legRGroup,
                    stick: navStickGroup,
                    ring: auraRing
                }};
                window.activeVehicleController = new VehicleController(scene, auraRoot, auraLimbs);
                window.activeVehicleController.setMode('{norm_travel_mode}');

                // Animation Clock
                let clock = new THREE.Clock();

                function renderLoop() {{
                    threeAnimId = requestAnimationFrame(renderLoop);
                    try {{
                        const elapsed = clock.getElapsedTime();

                        // Dynamic Vehicle Kinematics and Movement
                        if (window.activeVehicleController) {{
                            const turnAngle = (currentAnimState === 'turn_left') ? 0.35 : ((currentAnimState === 'turn_right') ? -0.35 : 0.0);
                            const isArr = (currentAnimState === 'arrive');
                            window.activeVehicleController.updateKinematics(elapsed, userSpeedKmh, turnAngle, isArr);
                        }}

                        // Procedural Skeletal Animations (Separated by Pedestrian vs Seated Vehicle)
                        const isWalkingMode = (!window.activeVehicleController || window.activeVehicleController.currentMode === 'WALK');
                        if (isWalkingMode) {{
                            if (currentAnimState === 'arrive') {{
                                // Celebratory Jumping & Dual Arm Waves
                                const hop = Math.abs(Math.sin(elapsed * 7.5)) * 0.45;
                                auraRoot.position.y = hop;
                                armRGroup.rotation.z = 0.8 + Math.sin(elapsed * 9) * 0.3;
                                armRGroup.rotation.x = -1.2;
                                armLGroup.rotation.z = -0.8 - Math.sin(elapsed * 9) * 0.3;
                                armLGroup.rotation.x = -1.2;
                                legLGroup.rotation.x = -hop * 0.5;
                                legRGroup.rotation.x = -hop * 0.5;
                                headGroup.rotation.y = Math.sin(elapsed * 4) * 0.25;
                                auraRing.scale.setScalar(1.0 + Math.sin(elapsed * 6) * 0.4);
                                auraRing.material.opacity = 0.9;
                            }} else if (currentAnimState === 'turn_left') {{
                                // Smoothly point stick to the left
                                auraRoot.position.y = 0;
                                auraRoot.rotation.y = safeLerp(auraRoot.rotation.y, 0.65, 0.1);
                                headGroup.rotation.y = 0.35;
                                armRGroup.rotation.z = -1.1; // Raise and point left
                                armRGroup.rotation.x = 0.6;
                                navStickGroup.rotation.z = -0.5;
                                armLGroup.rotation.x = 0.2;
                                legLGroup.rotation.x = Math.sin(elapsed * 3) * 0.2;
                                legRGroup.rotation.x = -Math.sin(elapsed * 3) * 0.2;
                                auraRing.material.opacity = 0.3;
                            }} else if (currentAnimState === 'turn_right') {{
                                // Smoothly point stick to the right
                                auraRoot.position.y = 0;
                                auraRoot.rotation.y = safeLerp(auraRoot.rotation.y, -0.65, 0.1);
                                headGroup.rotation.y = -0.35;
                                armRGroup.rotation.z = 1.2; // Raise and point right
                                armRGroup.rotation.x = 0.6;
                                navStickGroup.rotation.z = 0.5;
                                armLGroup.rotation.x = 0.2;
                                legLGroup.rotation.x = Math.sin(elapsed * 3) * 0.2;
                                legRGroup.rotation.x = -Math.sin(elapsed * 3) * 0.2;
                                auraRing.material.opacity = 0.3;
                            }} else if (currentAnimState === 'wave') {{
                                // Waving hello
                                auraRoot.position.y = 0;
                                auraRoot.rotation.y = safeLerp(auraRoot.rotation.y, 0, 0.1);
                                headGroup.rotation.y = Math.sin(elapsed * 3) * 0.15;
                                armRGroup.rotation.z = 1.3 + Math.sin(elapsed * 10) * 0.35;
                                armRGroup.rotation.x = 0.2;
                                armLGroup.rotation.x = 0.1;
                                legLGroup.rotation.x = 0;
                                legRGroup.rotation.x = 0;
                            }} else if (currentAnimState === 'run') {{
                                // High-speed Stride
                                const stride = Math.sin(elapsed * 10) * 0.85;
                                legLGroup.rotation.x = stride;
                                legRGroup.rotation.x = -stride;
                                armLGroup.rotation.x = -stride * 0.7;
                                armRGroup.rotation.x = stride * 0.7;
                                armRGroup.rotation.z = 0.2;
                                auraRoot.position.y = Math.abs(Math.sin(elapsed * 10)) * 0.12;
                                headGroup.rotation.y = 0;
                            }} else {{
                                // Natural Walking Stride
                                const stride = Math.sin(elapsed * 5.5) * 0.52;
                                legLGroup.rotation.x = stride;
                                legRGroup.rotation.x = -stride;
                                armLGroup.rotation.x = -stride * 0.6;
                                armRGroup.rotation.x = stride * 0.6;
                                armRGroup.rotation.z = 0.15;
                                auraRoot.position.y = Math.abs(Math.sin(elapsed * 5.5)) * 0.06;
                                headGroup.rotation.y = Math.sin(elapsed * 2.5) * 0.1;
                                auraRoot.rotation.y = safeLerp(auraRoot.rotation.y, 0, 0.1);
                                auraRing.material.opacity = 0.4;
                            }}
                        }} else {{
                            // Dynamic Vehicle Seated / Riding Mode
                            // VirtualGuidePoseController applies the sitting/riding posture on wheels/handlebars
                            if (currentAnimState === 'arrive') {{
                                armRGroup.rotation.z = 1.0 + Math.sin(elapsed * 9) * 0.25;
                                armRGroup.rotation.x = -0.6;
                                headGroup.rotation.y = Math.sin(elapsed * 4) * 0.2;
                            }} else if (currentAnimState === 'wave') {{
                                armRGroup.rotation.z = 1.2 + Math.sin(elapsed * 10) * 0.3;
                                armRGroup.rotation.x = -0.3;
                            }}
                        }}

                        // Blinking Visor Eyes
                        const blinkScale = Math.sin(elapsed * 2.5) > 0.96 ? 0.1 : 1.0;
                        eyeL.scale.y = blinkScale;
                        eyeR.scale.y = blinkScale;

                        // Procedural Cloud Drifting
                        cloudList.forEach(c => {{
                            c.obj.position.x += c.speed;
                            if (c.obj.position.x > 85) c.obj.position.x = -85;
                        }});

                        // Gentle Foliage Wind Sway
                        treeSwayList.forEach(t => {{
                            t.group.rotation.z = Math.sin(elapsed * 1.8 + t.phase) * 0.024;
                        }});

                        // Camera Modes
                        if (activeCam === 'pov') {{
                            camera.position.set(0, 1.45, -1.8);
                            camera.lookAt(0, 1.3, 15);
                        }} else if (activeCam === 'iso') {{
                            camera.position.set(4.5, 5.2, -4.5);
                            camera.lookAt(0, 0.9, 2.0);
                        }} else {{
                            // 3D Follow Drone
                            camera.position.set(0, 2.3, -4.2);
                            camera.lookAt(0, 1.1, 3.0);
                        }}

                        renderer.render(scene, camera);
                    }} catch(loopErr) {{
                        console.warn("Three.js renderLoop caught error, gracefully reverting to 2.5D scenic companion:", loopErr);
                        if (threeAnimId) cancelAnimationFrame(threeAnimId);
                        threeSceneStarted = false;
                        canvas.style.display = 'none';
                        if (scenicCanvas) scenicCanvas.style.display = 'block';
                        startScenicFallback2D();
                    }}
                }}

                // Test initial render to verify WebGL execution before hiding 2.5D companion
                camera.position.set(0, 2.3, -4.2);
                camera.lookAt(0, 1.1, 3.0);
                renderer.render(scene, camera);

                // Verification successful: promote to full 3D companion
                canvas.style.display = 'block';
                if (scenicCanvas) scenicCanvas.style.display = 'none';
                if (fallback2DAnimId) {{
                    cancelAnimationFrame(fallback2DAnimId);
                    fallback2DAnimId = null;
                }}
                threeSceneStarted = true;

                renderLoop();

                // Environment Lighting Controller
                threeEnv = {{
                    updateLighting: function(env) {{
                        if (env === 'sunset') {{
                            scene.background = new THREE.Color(0xf97316);
                            scene.fog.color = new THREE.Color(0x6b21a8);
                            scene.fog.density = 0.009;
                            skyMesh.material.map = makeSkyTexture('#311042', '#ea580c', '#fde047');
                            hemiLight.color.setHex(0xfb923c);
                            hemiLight.groundColor.setHex(0x78350f);
                            hemiLight.intensity = 0.85;
                            ambientLight.color.setHex(0xfbbf24);
                            ambientLight.intensity = 0.45;
                            dirLight.color.setHex(0xf97316);
                            dirLight.intensity = 1.4;
                            dirLight.position.set(40, 22, 10);
                            sunMesh.material.opacity = 1.0;
                            sunGlowMesh.material.opacity = 0.55;
                            moonMesh.material.opacity = 0.2;
                            starMat.opacity = 0.15;
                            cloudMat.color.setHex(0xfca5a5);
                            lampLights.forEach(l => {{
                                l.light.intensity = 0.75;
                                l.glass.material.color.setHex(0xfde047);
                            }});
                            windowMats.forEach(m => {{ m.map = makeBuildingWindowTexture(true); }});
                        }} else if (env === 'night') {{
                            scene.background = new THREE.Color(0x020617);
                            scene.fog.color = new THREE.Color(0x030712);
                            scene.fog.density = 0.012;
                            skyMesh.material.map = makeSkyTexture('#020617', '#091124', '#0f172a');
                            hemiLight.color.setHex(0x0f172a);
                            hemiLight.groundColor.setHex(0x020617);
                            hemiLight.intensity = 0.35;
                            ambientLight.color.setHex(0x1e293b);
                            ambientLight.intensity = 0.25;
                            dirLight.color.setHex(0x38bdf8);
                            dirLight.intensity = 0.55;
                            dirLight.position.set(-25, 45, 20);
                            sunMesh.material.opacity = 0;
                            sunGlowMesh.material.opacity = 0;
                            moonMesh.material.opacity = 0.95;
                            starMat.opacity = 0.95;
                            cloudMat.color.setHex(0x334155);
                            lampLights.forEach(l => {{
                                l.light.intensity = 1.8;
                                l.glass.material.color.setHex(0xfef08a);
                            }});
                            windowMats.forEach(m => {{ m.map = makeBuildingWindowTexture(true); }});
                        }} else {{
                            // Day
                            scene.background = new THREE.Color(0x38bdf8);
                            scene.fog.color = new THREE.Color(0xc7d2fe);
                            scene.fog.density = 0.0075;
                            skyMesh.material.map = makeSkyTexture('#1d4ed8', '#38bdf8', '#e0f2fe');
                            hemiLight.color.setHex(0x7dd3fc);
                            hemiLight.groundColor.setHex(0x15803d);
                            hemiLight.intensity = 0.85;
                            ambientLight.color.setHex(0xffffff);
                            ambientLight.intensity = 0.35;
                            dirLight.color.setHex(0xfffaed);
                            dirLight.intensity = 1.35;
                            dirLight.position.set(28, 52, 28);
                            sunMesh.material.opacity = 1.0;
                            sunGlowMesh.material.opacity = 0.35;
                            moonMesh.material.opacity = 0;
                            starMat.opacity = 0;
                            cloudMat.color.setHex(0xffffff);
                            lampLights.forEach(l => {{
                                l.light.intensity = 0.0;
                                l.glass.material.color.setHex(0xffffff);
                            }});
                            windowMats.forEach(m => {{ m.map = makeBuildingWindowTexture(false); }});
                        }}
                    }}
                }};

                // Immediately sync active environment lighting
                threeEnv.updateLighting(activeEnv);

                // Update HUD runtime badge to active 3D
                const hudBadge = document.getElementById('hud-runtime-badge');
                const hudDot = document.getElementById('hud-pulse-dot');
                const hudText = document.getElementById('hud-runtime-text');
                if (hudText) hudText.innerText = '✦ 3D COMPANION ACTIVE';
                if (hudBadge) {{
                    hudBadge.style.borderColor = 'rgba(16, 185, 129, 0.5)';
                    hudBadge.style.color = '#34d399';
                }}
                if (hudDot) {{
                    hudDot.style.background = '#34d399';
                    hudDot.style.boxShadow = '0 0 8px #34d399';
                }}

                if (window.ResizeObserver && container) {{
                    const ro = new ResizeObserver(entries => {{
                        for (let entry of entries) {{
                            const cr = entry.contentRect;
                            if (cr.width > 0 && cr.height > 0) {{
                                camera.aspect = cr.width / cr.height;
                                camera.updateProjectionMatrix();
                                renderer.setSize(cr.width, cr.height);
                            }}
                        }}
                    }});
                    ro.observe(container);
                }}

                window.addEventListener('resize', () => {{
                    const w = container.clientWidth;
                    const h = container.clientHeight;
                    if (w && h) {{
                        camera.aspect = w / h;
                        camera.updateProjectionMatrix();
                        renderer.setSize(w, h);
                    }}
                }});

                return true;
            }} catch(e) {{
                console.warn("Three.js init error, falling back to 2.5D scenic companion:", e);
                threeSceneStarted = false;
                if (scenicCanvas) scenicCanvas.style.display = 'block';
                canvas.style.display = 'none';
                startScenicFallback2D();
                return false;
            }}
        }}

        // =========================================================================
        // RESILIENT 2.5D ANIMATED SCENIC COMPANION ENGINE (ZERO-BLANK-SCREEN GUARANTEE)
        // =========================================================================
        function startScenicFallback2D() {{
            const canvas = document.getElementById('aura-scenic-canvas');
            const container = document.getElementById('aura-3d-scene-box');
            if (!canvas || !container) return;
            const ctx = canvas.getContext('2d');
            if (!ctx) return;

            const hudBadge = document.getElementById('hud-runtime-badge');
            const hudDot = document.getElementById('hud-pulse-dot');
            const hudText = document.getElementById('hud-runtime-text');
            if (hudText && !threeSceneStarted) hudText.innerText = '✦ 2.5D SCENIC RUNTIME ACTIVE';
            if (hudBadge && !threeSceneStarted) {{
                hudBadge.style.borderColor = 'rgba(56, 189, 248, 0.6)';
                hudBadge.style.color = '#38bdf8';
            }}
            if (hudDot && !threeSceneStarted) {{
                hudDot.style.background = '#38bdf8';
                hudDot.style.boxShadow = '0 0 8px #38bdf8';
            }}

            // Fallback environment lighting controller
            if (!threeEnv) {{
                threeEnv = {{
                    updateLighting: function(env) {{
                        activeEnv = env;
                    }}
                }};
            }}

            function drawRoundedRect(c, x, y, w, h, r) {{
                if (typeof c.roundRect === 'function') {{
                    c.roundRect(x, y, w, h, r);
                }} else {{
                    c.rect(x, y, w, h);
                }}
            }}

            let tStart = Date.now();
            const stars = [];
            for (let i = 0; i < 50; i++) {{
                stars.push({{
                    x: Math.random(),
                    y: Math.random() * 0.52,
                    r: 0.7 + Math.random() * 1.6,
                    phase: Math.random() * Math.PI * 2
                }});
            }}

            const clouds = [
                {{ x: 30, y: 45, scale: 1.1, speed: 0.16 }},
                {{ x: 240, y: 70, scale: 0.85, speed: 0.11 }},
                {{ x: 490, y: 35, scale: 1.35, speed: 0.20 }},
                {{ x: 710, y: 60, scale: 0.95, speed: 0.14 }}
            ];

            function drawCloud(cx, cy, s, color) {{
                ctx.fillStyle = color;
                ctx.beginPath();
                ctx.arc(cx, cy, 18 * s, 0, Math.PI * 2);
                ctx.arc(cx + 16 * s, cy - 8 * s, 22 * s, 0, Math.PI * 2);
                ctx.arc(cx + 36 * s, cy, 17 * s, 0, Math.PI * 2);
                ctx.arc(cx + 20 * s, cy + 6 * s, 14 * s, 0, Math.PI * 2);
                ctx.fill();
            }}

            function render() {{
                if (threeSceneStarted) {{
                    if (fallback2DAnimId) cancelAnimationFrame(fallback2DAnimId);
                    return;
                }}

                const w = container.clientWidth || 800;
                const h = container.clientHeight || 360;
                const dpr = Math.min(window.devicePixelRatio || 1, 2);

                if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {{
                    canvas.width = Math.round(w * dpr);
                    canvas.height = Math.round(h * dpr);
                }}

                ctx.save();
                ctx.scale(dpr, dpr);

                const elapsed = (Date.now() - tStart) / 1000;
                const isSunset = (activeEnv === 'sunset');
                const isNight = (activeEnv === 'night');

                // 1. SKY BACKGROUND GRADIENT
                let skyGrad = ctx.createLinearGradient(0, 0, 0, h * 0.58);
                if (isSunset) {{
                    skyGrad.addColorStop(0, '#2e1065');
                    skyGrad.addColorStop(0.45, '#c2410c');
                    skyGrad.addColorStop(0.85, '#ea580c');
                    skyGrad.addColorStop(1, '#fde047');
                }} else if (isNight) {{
                    skyGrad.addColorStop(0, '#020617');
                    skyGrad.addColorStop(0.5, '#091124');
                    skyGrad.addColorStop(1, '#1e1b4b');
                }} else {{
                    skyGrad.addColorStop(0, '#1d4ed8');
                    skyGrad.addColorStop(0.5, '#38bdf8');
                    skyGrad.addColorStop(1, '#e0f2fe');
                }}
                ctx.fillStyle = skyGrad;
                ctx.fillRect(0, 0, w, h);

                // 2. CELESTIAL BODIES (SUN / MOON & STARS)
                if (isNight) {{
                    // Stars
                    for (let s of stars) {{
                        const alpha = 0.3 + 0.65 * Math.abs(Math.sin(elapsed * 1.8 + s.phase));
                        ctx.fillStyle = 'rgba(255, 255, 255, ' + alpha.toFixed(2) + ')';
                        ctx.beginPath();
                        ctx.arc(s.x * w, s.y * h, s.r, 0, Math.PI * 2);
                        ctx.fill();
                    }}
                    // Crescent Moon with Halo
                    const mx = w * 0.82, my = h * 0.22;
                    let moonHalo = ctx.createRadialGradient(mx, my, 8, mx, my, 45);
                    moonHalo.addColorStop(0, 'rgba(224, 231, 255, 0.35)');
                    moonHalo.addColorStop(1, 'rgba(224, 231, 255, 0)');
                    ctx.fillStyle = moonHalo;
                    ctx.beginPath();
                    ctx.arc(mx, my, 45, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.fillStyle = '#f8fafc';
                    ctx.beginPath();
                    ctx.arc(mx, my, 18, 0, Math.PI * 2);
                    ctx.fill();
                    // Shadow arc for crescent
                    ctx.fillStyle = '#091124';
                    ctx.beginPath();
                    ctx.arc(mx - 7, my - 4, 16, 0, Math.PI * 2);
                    ctx.fill();
                }} else if (isSunset) {{
                    const sx = w * 0.72, sy = h * 0.42;
                    let sunGlow = ctx.createRadialGradient(sx, sy, 10, sx, sy, 65);
                    sunGlow.addColorStop(0, 'rgba(254, 240, 138, 0.9)');
                    sunGlow.addColorStop(0.4, 'rgba(249, 115, 22, 0.45)');
                    sunGlow.addColorStop(1, 'rgba(234, 88, 12, 0)');
                    ctx.fillStyle = sunGlow;
                    ctx.beginPath();
                    ctx.arc(sx, sy, 65, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = '#fef08a';
                    ctx.beginPath();
                    ctx.arc(sx, sy, 20, 0, Math.PI * 2);
                    ctx.fill();
                }} else {{
                    // Day Sun
                    const sx = w * 0.76, sy = h * 0.20;
                    let sunGlow = ctx.createRadialGradient(sx, sy, 12, sx, sy, 70);
                    sunGlow.addColorStop(0, 'rgba(255, 253, 235, 0.95)');
                    sunGlow.addColorStop(0.35, 'rgba(254, 240, 138, 0.5)');
                    sunGlow.addColorStop(1, 'rgba(56, 189, 248, 0)');
                    ctx.fillStyle = sunGlow;
                    ctx.beginPath();
                    ctx.arc(sx, sy, 70, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = '#fffae0';
                    ctx.beginPath();
                    ctx.arc(sx, sy, 22, 0, Math.PI * 2);
                    ctx.fill();
                }}

                // 3. DRIFTING CLOUDS
                const cloudCol = isSunset ? 'rgba(254, 202, 202, 0.65)' : (isNight ? 'rgba(51, 65, 85, 0.55)' : 'rgba(255, 255, 255, 0.75)');
                clouds.forEach(c => {{
                    c.x += c.speed;
                    if (c.x > w + 60) c.x = -60;
                    drawCloud(c.x, c.y, c.scale, cloudCol);
                }});

                // 4. DISTANT CITY SKYLINE & CAMPUS TOWERS
                const horizonY = h * 0.52;
                const bldgList = [
                    {{ x: 0.05, w: 45, bh: 70, col: isNight ? '#0f172a' : (isSunset ? '#311042' : '#334155') }},
                    {{ x: 0.12, w: 55, bh: 95, col: isNight ? '#1e293b' : (isSunset ? '#4a154b' : '#1e293b') }},
                    {{ x: 0.20, w: 40, bh: 65, col: isNight ? '#0f172a' : (isSunset ? '#311042' : '#475569') }},
                    {{ x: 0.74, w: 48, bh: 85, col: isNight ? '#1e293b' : (isSunset ? '#4a154b' : '#1e293b') }},
                    {{ x: 0.82, w: 60, bh: 110, col: isNight ? '#0f172a' : (isSunset ? '#311042' : '#334155') }},
                    {{ x: 0.91, w: 42, bh: 75, col: isNight ? '#1e293b' : (isSunset ? '#4a154b' : '#475569') }}
                ];
                bldgList.forEach(b => {{
                    const bx = b.x * w;
                    const by = horizonY - b.bh;
                    ctx.fillStyle = b.col;
                    ctx.fillRect(bx, by, b.w, b.bh);

                    // Rooftop beacon
                    if (b.bh > 80) {{
                        ctx.fillStyle = '#94a3b8';
                        ctx.fillRect(bx + b.w * 0.5 - 1, by - 16, 2, 16);
                        const beaconAlpha = Math.sin(elapsed * 4) > 0 ? 1 : 0.2;
                        ctx.fillStyle = 'rgba(239, 68, 68, ' + beaconAlpha + ')';
                        ctx.beginPath();
                        ctx.arc(bx + b.w * 0.5, by - 16, 2.5, 0, Math.PI * 2);
                        ctx.fill();
                    }}

                    // Window grid
                    const litCol = isNight ? '#fef08a' : (isSunset ? '#fed7aa' : '#93c5fd');
                    const rows = 4, cols = 3;
                    for (let r = 0; r < rows; r++) {{
                        for (let c = 0; c < cols; c++) {{
                            if ((r + c + Math.floor(b.x * 10)) % 2 === 0) {{
                                ctx.fillStyle = isNight ? litCol : 'rgba(147, 197, 253, 0.45)';
                                ctx.fillRect(bx + 6 + c * 12, by + 10 + r * 14, 6, 8);
                            }}
                        }}
                    }}
                }});

                // 5. GROUND / GRASS TERRAIN
                let groundGrad = ctx.createLinearGradient(0, horizonY, 0, h);
                if (isNight) {{
                    groundGrad.addColorStop(0, '#064e3b');
                    groundGrad.addColorStop(1, '#022c22');
                }} else if (isSunset) {{
                    groundGrad.addColorStop(0, '#78350f');
                    groundGrad.addColorStop(1, '#1c1917');
                }} else {{
                    groundGrad.addColorStop(0, '#16a34a');
                    groundGrad.addColorStop(1, '#14532d');
                }}
                ctx.fillStyle = groundGrad;
                ctx.fillRect(0, horizonY, w, h - horizonY);

                // 6. CURVING 3D PERSPECTIVE ROADWAY
                const camXOffset = (activeCam === 'iso') ? w * 0.12 : ((activeCam === 'pov') ? -w * 0.05 : 0);
                const roadCenterX = w * 0.5 + camXOffset;
                const roadHorizonW = w * 0.08;
                const roadBottomW = w * 0.65;
                const roadCurve = Math.sin(elapsed * 0.35) * 16;

                // Asphalt road surface
                ctx.fillStyle = isNight ? '#0b1120' : (isSunset ? '#18181b' : '#1e293b');
                ctx.beginPath();
                ctx.moveTo(roadCenterX - roadHorizonW * 0.5 + roadCurve * 0.2, horizonY);
                ctx.lineTo(roadCenterX + roadHorizonW * 0.5 + roadCurve * 0.2, horizonY);
                ctx.quadraticCurveTo(roadCenterX + roadBottomW * 0.35 + roadCurve, (horizonY + h) * 0.5, roadCenterX + roadBottomW * 0.5, h);
                ctx.lineTo(roadCenterX - roadBottomW * 0.5, h);
                ctx.quadraticCurveTo(roadCenterX - roadBottomW * 0.35 + roadCurve, (horizonY + h) * 0.5, roadCenterX - roadHorizonW * 0.5 + roadCurve * 0.2, horizonY);
                ctx.closePath();
                ctx.fill();

                // Left & Right Curbs
                ctx.strokeStyle = '#94a3b8';
                ctx.lineWidth = 3;
                ctx.stroke();

                // Road Sidewalk Borders
                ctx.fillStyle = isNight ? '#1e293b' : '#475569';
                // Left sidewalk strip
                ctx.beginPath();
                ctx.moveTo(roadCenterX - roadHorizonW * 0.5 + roadCurve * 0.2, horizonY);
                ctx.lineTo(roadCenterX - roadHorizonW * 0.7 + roadCurve * 0.2, horizonY);
                ctx.lineTo(roadCenterX - roadBottomW * 0.58, h);
                ctx.lineTo(roadCenterX - roadBottomW * 0.5, h);
                ctx.closePath();
                ctx.fill();

                // Right sidewalk strip
                ctx.beginPath();
                ctx.moveTo(roadCenterX + roadHorizonW * 0.5 + roadCurve * 0.2, horizonY);
                ctx.lineTo(roadCenterX + roadHorizonW * 0.7 + roadCurve * 0.2, horizonY);
                ctx.lineTo(roadCenterX + roadBottomW * 0.58, h);
                ctx.lineTo(roadCenterX + roadBottomW * 0.5, h);
                ctx.closePath();
                ctx.fill();

                // Dashed Centerline (animated perspective movement)
                const dashSpeed = (motionState === 'MOVING' || isLiveMoving) ? (Math.max(currentSpeedKmh, 5.0) * 12) : 24;
                const dashOffset = (elapsed * dashSpeed) % 40;
                ctx.strokeStyle = '#facc15';
                ctx.lineWidth = 2.5;
                ctx.setLineDash([12, 10]);
                ctx.lineDashOffset = -dashOffset;
                ctx.beginPath();
                ctx.moveTo(roadCenterX + roadCurve * 0.2, horizonY);
                ctx.quadraticCurveTo(roadCenterX + roadCurve, (horizonY + h) * 0.5, roadCenterX, h);
                ctx.stroke();
                ctx.setLineDash([]); // reset dash

                // GLOWING CYAN AR TRAJECTORY RIBBON
                ctx.strokeStyle = 'rgba(0, 240, 255, 0.75)';
                ctx.lineWidth = 4;
                ctx.shadowColor = '#00f0ff';
                ctx.shadowBlur = 14;
                ctx.beginPath();
                ctx.moveTo(roadCenterX + roadCurve * 0.2, horizonY + 4);
                ctx.quadraticCurveTo(roadCenterX + roadCurve + 3, (horizonY + h) * 0.5, roadCenterX + 5, h);
                ctx.stroke();
                ctx.shadowBlur = 0; // reset shadow

                // 7. ROADSIDE STREET LAMPS (animated perspective movement)
                const lampPositions = [
                    {{ baseT: 0.15, side: -1 }},
                    {{ baseT: 0.40, side: 1 }},
                    {{ baseT: 0.65, side: -1 }},
                    {{ baseT: 0.90, side: 1 }}
                ];
                const lampScrollSpeed = (motionState === 'MOVING' || isLiveMoving) ? (Math.max(currentSpeedKmh, 15.0) * 0.006) : 0.035;
                lampPositions.forEach(lp => {{
                    const t = (lp.baseT + (elapsed * lampScrollSpeed)) % 1.0;
                    const ly = horizonY + (h - horizonY) * t;
                    const rWAtY = roadHorizonW + (roadBottomW - roadHorizonW) * t;
                    const lx = roadCenterX + lp.side * (rWAtY * 0.5 + 16 * (0.3 + t * 0.7));
                    const lampHeight = 18 + t * 36;

                    // Pole
                    ctx.strokeStyle = '#334155';
                    ctx.lineWidth = 1.5 + t * 1.5;
                    ctx.beginPath();
                    ctx.moveTo(lx, ly);
                    ctx.lineTo(lx, ly - lampHeight);
                    ctx.lineTo(lx - lp.side * (6 + t * 6), ly - lampHeight - 4);
                    ctx.stroke();

                    // Lamp head & glow
                    if (isNight || isSunset) {{
                        const glowR = 15 + t * 30;
                        const lampGrad = ctx.createRadialGradient(lx - lp.side * (6 + t * 6), ly - lampHeight - 4, 2, lx - lp.side * (6 + t * 6), ly, glowR);
                        lampGrad.addColorStop(0, 'rgba(254, 240, 138, 0.85)');
                        lampGrad.addColorStop(1, 'rgba(254, 240, 138, 0)');
                        ctx.fillStyle = lampGrad;
                        ctx.beginPath();
                        ctx.arc(lx - lp.side * (6 + t * 6), ly - lampHeight - 4, glowR, 0, Math.PI * 2);
                        ctx.fill();
                    }}
                }});

                // 8. ROADSIDE TREES WITH PERSPECTIVE STREAMING
                const treeSway = Math.sin(elapsed * 2.2) * 4;
                const baseTrees = [
                    {{ slot: 0.08, side: -1, type: 'canopy', baseH: 52 }},
                    {{ slot: 0.25, side: 1, type: 'pine', baseH: 58 }},
                    {{ slot: 0.42, side: -1, type: 'pine', baseH: 48 }},
                    {{ slot: 0.58, side: 1, type: 'canopy', baseH: 54 }},
                    {{ slot: 0.75, side: -1, type: 'canopy', baseH: 56 }},
                    {{ slot: 0.92, side: 1, type: 'pine', baseH: 50 }}
                ];
                const treeScrollSpeed = (motionState === 'MOVING' || isLiveMoving) ? (Math.max(currentSpeedKmh, 15.0) * 0.006) : 0.035;
                baseTrees.forEach(tr => {{
                    const t = (tr.slot + (elapsed * treeScrollSpeed)) % 1.0;
                    const ty = horizonY + (h - horizonY) * t;
                    const scale = 0.2 + t * 0.85;
                    const halfW = (roadHorizonW * 0.5 + (roadBottomW * 0.5 - roadHorizonW * 0.5) * t);
                    const tx = roadCenterX + tr.side * (halfW + 32 * scale);
                    const th = tr.baseH * scale;

                    // Trunk
                    ctx.fillStyle = '#4a2e18';
                    ctx.fillRect(tx - 2 * scale, ty - th * 0.35, 4 * scale, th * 0.35);

                    // Crown
                    ctx.fillStyle = isNight ? '#064e3b' : (isSunset ? '#14532d' : '#15803d');
                    ctx.beginPath();
                    if (tr.type === 'pine') {{
                        ctx.moveTo(tx + treeSway * 0.5 * scale, ty - th);
                        ctx.lineTo(tx + th * 0.35, ty - th * 0.35);
                        ctx.lineTo(tx - th * 0.35, ty - th * 0.35);
                    }} else {{
                        ctx.arc(tx + treeSway * 0.6 * scale, ty - th * 0.65, th * 0.38, 0, Math.PI * 2);
                    }}
                    ctx.fill();
                }});

                // 9. DYNAMIC VEHICLE & VIRTUAL GUIDE (AURA) SUITE
                const curMode = (window.activeVehicleMode || '{norm_travel_mode}').toUpperCase();
                const isMoving = (motionState === 'MOVING' || isLiveMoving);
                const spd = isMoving ? Math.max(currentSpeedKmh, 35.0) : 20.0;
                const turnTilt = (currentAnimState === 'turn_left') ? -0.22 : ((currentAnimState === 'turn_right') ? 0.22 : (roadCurve * 0.006));
                const chassisRoll = (currentAnimState === 'turn_left') ? -0.12 : ((currentAnimState === 'turn_right') ? 0.12 : (roadCurve * 0.004));
                const suspensionBob = Math.sin(elapsed * 18) * 1.5;
                const wheelAngle = elapsed * (spd * 0.5);

                let auraBaseX = roadCenterX;
                let auraBaseY = h * 0.78;
                if (activeCam === 'pov') {{
                    auraBaseX = w * 0.5;
                    auraBaseY = h * 0.84;
                }} else if (activeCam === 'iso') {{
                    auraBaseX = roadCenterX + 35;
                    auraBaseY = h * 0.75;
                }}

                // Helper: Draw cute Aura Avatar seated or in cockpit
                function drawCuteAuraDriver(cx, cy, scale, isSeated, handsOnWheel, wheelRadius) {{
                    ctx.save();
                    ctx.translate(cx, cy);

                    // Visor blink
                    const isBlink = Math.sin(elapsed * 2.5) > 0.96;

                    // Torso / Chassis
                    ctx.fillStyle = '#0f2b48';
                    drawRoundedRect(ctx, -14 * scale, -10 * scale, 28 * scale, 22 * scale, 6 * scale);
                    ctx.fill();
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 1.2 * scale;
                    ctx.stroke();

                    // Glowing Core Reactor
                    ctx.save();
                    ctx.shadowColor = '#00f0ff';
                    ctx.shadowBlur = 8;
                    ctx.fillStyle = '#00f0ff';
                    ctx.beginPath();
                    ctx.arc(0, 0, 4.5 * scale, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();

                    // Head
                    const headY = -24 * scale;
                    ctx.fillStyle = '#0f2b48';
                    drawRoundedRect(ctx, -15 * scale, headY, 30 * scale, 20 * scale, 7 * scale);
                    ctx.fill();
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 1.2 * scale;
                    ctx.stroke();

                    // Visor Screen
                    ctx.fillStyle = '#030712';
                    drawRoundedRect(ctx, -12 * scale, headY + 4 * scale, 24 * scale, 12 * scale, 4 * scale);
                    ctx.fill();

                    // Visor Eyes
                    ctx.fillStyle = '#38bdf8';
                    ctx.shadowColor = '#38bdf8';
                    ctx.shadowBlur = 6;
                    if (isBlink) {{
                        ctx.fillRect(-8 * scale, headY + 9 * scale, 5 * scale, 1.2 * scale);
                        ctx.fillRect(3 * scale, headY + 9 * scale, 5 * scale, 1.2 * scale);
                    }} else {{
                        ctx.beginPath();
                        ctx.arc(-5.5 * scale, headY + 9.5 * scale, 2.2 * scale, 0, Math.PI * 2);
                        ctx.arc(5.5 * scale, headY + 9.5 * scale, 2.2 * scale, 0, Math.PI * 2);
                        ctx.fill();
                    }}

                    // Smile
                    ctx.strokeStyle = '#00f0ff';
                    ctx.lineWidth = 1.2 * scale;
                    ctx.beginPath();
                    ctx.arc(0, headY + 12 * scale, 3 * scale, 0.1 * Math.PI, 0.9 * Math.PI, false);
                    ctx.stroke();
                    ctx.shadowBlur = 0;

                    // Antenna
                    ctx.fillStyle = '#f59e0b';
                    ctx.fillRect(-1 * scale, headY - 6 * scale, 2 * scale, 6 * scale);
                    ctx.shadowColor = '#00f0ff';
                    ctx.shadowBlur = 8;
                    ctx.fillStyle = '#00f0ff';
                    ctx.beginPath();
                    ctx.arc(0, headY - 7 * scale, 3 * scale, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.shadowBlur = 0;

                    // Hands & Steering Wheel
                    if (handsOnWheel) {{
                        const wr = wheelRadius || (13 * scale);
                        ctx.save();
                        ctx.strokeStyle = '#1e293b';
                        ctx.lineWidth = 3 * scale;
                        ctx.beginPath();
                        ctx.arc(0, 9 * scale, wr, 0, Math.PI * 2);
                        ctx.stroke();
                        // Steering Spokes
                        ctx.strokeStyle = '#64748b';
                        ctx.lineWidth = 1.5 * scale;
                        ctx.beginPath();
                        ctx.moveTo(-wr, 9 * scale); ctx.lineTo(wr, 9 * scale);
                        ctx.moveTo(0, 9 * scale); ctx.lineTo(0, 9 * scale + wr);
                        ctx.stroke();
                        // Hands gripping wheel
                        ctx.fillStyle = '#00f0ff';
                        ctx.beginPath();
                        ctx.arc(-wr * 0.85, 9 * scale - 2 * scale, 3.2 * scale, 0, Math.PI * 2);
                        ctx.arc(wr * 0.85, 9 * scale - 2 * scale, 3.2 * scale, 0, Math.PI * 2);
                        ctx.fill();
                        ctx.restore();
                    }}

                    ctx.restore();
                }}

                // Helper: Draw spinning wheel from rear perspective
                function drawSpinningWheel(wx, wy, radX, radY, angle, isDeepTread) {{
                    ctx.save();
                    ctx.translate(wx, wy);

                    // Tire Shadow
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.45)';
                    ctx.beginPath();
                    ctx.ellipse(0, radY * 0.9, radX * 1.1, radY * 0.35, 0, 0, Math.PI * 2);
                    ctx.fill();

                    // Rubber Tire
                    ctx.fillStyle = '#111827';
                    ctx.strokeStyle = '#374151';
                    ctx.lineWidth = 1.5;
                    ctx.beginPath();
                    ctx.ellipse(0, 0, radX, radY, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.stroke();

                    // Rim
                    ctx.fillStyle = '#475569';
                    ctx.beginPath();
                    ctx.ellipse(0, 0, radX * 0.65, radY * 0.65, 0, 0, Math.PI * 2);
                    ctx.fill();

                    // Rotating rim spokes
                    ctx.strokeStyle = '#94a3b8';
                    ctx.lineWidth = 1.2;
                    const spokeCount = isDeepTread ? 8 : 5;
                    for (let i = 0; i < spokeCount; i++) {{
                        const th = angle + (i * Math.PI * 2 / spokeCount);
                        ctx.beginPath();
                        ctx.moveTo(0, 0);
                        ctx.lineTo(Math.cos(th) * radX * 0.6, Math.sin(th) * radY * 0.6);
                        ctx.stroke();
                    }}

                    // Center Nut
                    ctx.fillStyle = '#00f0ff';
                    ctx.beginPath();
                    ctx.arc(0, 0, 2.5, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.restore();
                }}

                // Helper: Dynamic Forward Headlight Beam Cones
                function drawHeadlightBeams(lx, rx, by, reachY, beamColor) {{
                    if (!isNight && !isSunset) return;
                    ctx.save();
                    const bGrad = ctx.createLinearGradient(0, by, 0, by - reachY);
                    bGrad.addColorStop(0, beamColor || 'rgba(254, 240, 138, 0.42)');
                    bGrad.addColorStop(0.35, 'rgba(254, 240, 138, 0.22)');
                    bGrad.addColorStop(1, 'rgba(254, 240, 138, 0.0)');
                    ctx.fillStyle = bGrad;

                    // Left Beam
                    ctx.beginPath();
                    ctx.moveTo(lx, by);
                    ctx.lineTo(lx - 55, by - reachY);
                    ctx.lineTo(lx - 8, by - reachY);
                    ctx.closePath();
                    ctx.fill();

                    // Right Beam
                    ctx.beginPath();
                    ctx.moveTo(rx, by);
                    ctx.lineTo(rx + 8, by - reachY);
                    ctx.lineTo(rx + 55, by - reachY);
                    ctx.closePath();
                    ctx.fill();

                    ctx.restore();
                }}

                if (curMode === 'WALK') {{
                    // =========================================================================
                    // 1. PEDESTRIAN WALK MODE (Original Aura Mascot with Nav Stick)
                    // =========================================================================
                    let walkBob = 0;
                    let legLRot = 0;
                    let legRRot = 0;
                    let armLRot = 0;
                    let armRRot = 0;
                    let stickRot = 0;
                    let auraScale = (activeCam === 'pov') ? 0.95 : 1.15;

                    if (currentAnimState === 'arrive') {{
                        walkBob = Math.abs(Math.sin(elapsed * 7)) * 22;
                        armLRot = -1.2 + Math.sin(elapsed * 9) * 0.3;
                        armRRot = 1.2 + Math.sin(elapsed * 9) * 0.3;
                    }} else if (currentAnimState === 'wave') {{
                        armRRot = 1.4 + Math.sin(elapsed * 8) * 0.45;
                        armLRot = 0.1;
                    }} else if (currentAnimState === 'run') {{
                        walkBob = Math.abs(Math.sin(elapsed * 10)) * 7;
                        legLRot = Math.sin(elapsed * 10) * 26;
                        legRRot = -legLRot;
                        armLRot = -legLRot * 0.6;
                        armRRot = legLRot * 0.6;
                    }} else if (currentAnimState === 'turn_left') {{
                        armRRot = -0.9;
                        stickRot = -0.6;
                    }} else if (currentAnimState === 'turn_right') {{
                        armRRot = 0.9;
                        stickRot = 0.6;
                    }} else {{
                        walkBob = Math.abs(Math.sin(elapsed * 5.5)) * 4.5;
                        legLRot = Math.sin(elapsed * 5.5) * 16;
                        legRRot = -legLRot;
                        armLRot = -legLRot * 0.5;
                        armRRot = legLRot * 0.5;
                    }}

                    const ax = auraBaseX;
                    const ay = auraBaseY - walkBob;

                    // Holographic Ring on ground
                    ctx.save();
                    ctx.shadowColor = '#00f0ff';
                    ctx.shadowBlur = 12;
                    ctx.strokeStyle = 'rgba(0, 240, 255, 0.85)';
                    ctx.lineWidth = 2.5;
                    ctx.beginPath();
                    ctx.ellipse(ax, auraBaseY + 18 * auraScale, 26 * auraScale, 10 * auraScale, 0, 0, Math.PI * 2);
                    ctx.stroke();
                    ctx.restore();

                    // Left Leg
                    ctx.save();
                    ctx.translate(ax - 10 * auraScale, ay + 6 * auraScale);
                    ctx.rotate(legLRot * Math.PI / 180);
                    ctx.fillStyle = '#0f2b48';
                    ctx.fillRect(-4 * auraScale, 0, 8 * auraScale, 18 * auraScale);
                    ctx.fillStyle = '#00f0ff';
                    ctx.fillRect(-5 * auraScale, 16 * auraScale, 11 * auraScale, 6 * auraScale);
                    ctx.restore();

                    // Right Leg
                    ctx.save();
                    ctx.translate(ax + 10 * auraScale, ay + 6 * auraScale);
                    ctx.rotate(legRRot * Math.PI / 180);
                    ctx.fillStyle = '#0f2b48';
                    ctx.fillRect(-4 * auraScale, 0, 8 * auraScale, 18 * auraScale);
                    ctx.fillStyle = '#00f0ff';
                    ctx.fillRect(-5 * auraScale, 16 * auraScale, 11 * auraScale, 6 * auraScale);
                    ctx.restore();

                    // Torso
                    ctx.fillStyle = '#0f2b48';
                    drawRoundedRect(ctx, ax - 17 * auraScale, ay - 16 * auraScale, 34 * auraScale, 26 * auraScale, 8 * auraScale);
                    ctx.fill();
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 1.5;
                    ctx.stroke();

                    // Core Reactor
                    ctx.save();
                    ctx.shadowColor = '#00f0ff';
                    ctx.shadowBlur = 10;
                    ctx.fillStyle = '#00f0ff';
                    ctx.beginPath();
                    ctx.arc(ax, ay - 3 * auraScale, 6 * auraScale, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();

                    // Left Arm
                    ctx.save();
                    ctx.translate(ax - 20 * auraScale, ay - 10 * auraScale);
                    ctx.rotate(armLRot * Math.PI / 180);
                    ctx.fillStyle = '#0f2b48';
                    ctx.fillRect(-3 * auraScale, 0, 6 * auraScale, 18 * auraScale);
                    ctx.fillStyle = '#00f0ff';
                    ctx.beginPath();
                    ctx.arc(0, 18 * auraScale, 3.5 * auraScale, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();

                    // Right Arm & Stick
                    ctx.save();
                    ctx.translate(ax + 20 * auraScale, ay - 10 * auraScale);
                    ctx.rotate(-armRRot * Math.PI / 180);
                    ctx.fillStyle = '#0f2b48';
                    ctx.fillRect(-3 * auraScale, 0, 6 * auraScale, 18 * auraScale);
                    ctx.translate(0, 18 * auraScale);
                    ctx.rotate(stickRot);
                    ctx.fillStyle = '#f59e0b';
                    ctx.fillRect(-1.5 * auraScale, -24 * auraScale, 3 * auraScale, 32 * auraScale);
                    ctx.shadowColor = '#00f0ff';
                    ctx.shadowBlur = 16;
                    ctx.fillStyle = '#00f0ff';
                    ctx.beginPath();
                    ctx.arc(0, -25 * auraScale, 6.5 * auraScale, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.fillStyle = '#ffffff';
                    ctx.beginPath();
                    ctx.arc(0, -25 * auraScale, 2.5 * auraScale, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();

                    // Head
                    const headY = ay - 32 * auraScale;
                    ctx.fillStyle = '#0f2b48';
                    drawRoundedRect(ctx, ax - 18 * auraScale, headY, 36 * auraScale, 26 * auraScale, 10 * auraScale);
                    ctx.fill();
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 1.5;
                    ctx.stroke();

                    // Visor
                    ctx.fillStyle = '#030712';
                    drawRoundedRect(ctx, ax - 14 * auraScale, headY + 5 * auraScale, 28 * auraScale, 16 * auraScale, 6 * auraScale);
                    ctx.fill();

                    // Eyes
                    const isBlink = Math.sin(elapsed * 2.5) > 0.96;
                    ctx.fillStyle = '#38bdf8';
                    ctx.shadowColor = '#38bdf8';
                    ctx.shadowBlur = 8;
                    if (isBlink) {{
                        ctx.fillRect(ax - 9 * auraScale, headY + 12 * auraScale, 6 * auraScale, 1.5 * auraScale);
                        ctx.fillRect(ax + 3 * auraScale, headY + 12 * auraScale, 6 * auraScale, 1.5 * auraScale);
                    }} else {{
                        ctx.beginPath();
                        ctx.arc(ax - 6 * auraScale, headY + 12 * auraScale, 2.8 * auraScale, 0, Math.PI * 2);
                        ctx.arc(ax + 6 * auraScale, headY + 12 * auraScale, 2.8 * auraScale, 0, Math.PI * 2);
                        ctx.fill();
                    }}

                    // Smile
                    ctx.strokeStyle = '#00f0ff';
                    ctx.lineWidth = 1.5 * auraScale;
                    ctx.beginPath();
                    ctx.arc(ax, headY + 15 * auraScale, 3.5 * auraScale, 0.1 * Math.PI, 0.9 * Math.PI, false);
                    ctx.stroke();
                    ctx.shadowBlur = 0;

                    // Antenna
                    ctx.fillStyle = '#f59e0b';
                    ctx.fillRect(ax - 1 * auraScale, headY - 8 * auraScale, 2 * auraScale, 8 * auraScale);
                    ctx.shadowColor = '#00f0ff';
                    ctx.shadowBlur = 10;
                    ctx.fillStyle = '#00f0ff';
                    ctx.beginPath();
                    ctx.arc(ax, headY - 10 * auraScale, 3.5 * auraScale, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.shadowBlur = 0;

                }} else if (curMode === 'BIKE') {{
                    // =========================================================================
                    // 2. MOTORCYCLE (SPORT BIKE)
                    // =========================================================================
                    drawHeadlightBeams(auraBaseX, auraBaseX, auraBaseY + 6, 120, 'rgba(254, 240, 138, 0.5)');

                    ctx.save();
                    ctx.translate(auraBaseX, auraBaseY + suspensionBob * 1.3);
                    ctx.rotate(turnTilt * 1.8);

                    drawSpinningWheel(0, 18, 15, 20, wheelAngle);

                    ctx.fillStyle = '#0f172a';
                    ctx.fillRect(-8, -4, 16, 22);

                    ctx.fillStyle = '#00f0ff';
                    ctx.beginPath();
                    ctx.moveTo(0, -32);
                    ctx.lineTo(16, -10);
                    ctx.lineTo(12, 10);
                    ctx.lineTo(-12, 10);
                    ctx.lineTo(-16, -10);
                    ctx.closePath();
                    ctx.fill();
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 2;
                    ctx.stroke();

                    ctx.fillStyle = '#1e293b';
                    drawRoundedRect(ctx, -14, -14, 28, 12, 4);
                    ctx.fill();

                    ctx.fillStyle = '#94a3b8';
                    ctx.fillRect(14, 2, 8, 16);

                    ctx.strokeStyle = '#cbd5e1';
                    ctx.lineWidth = 3;
                    ctx.beginPath();
                    ctx.moveTo(-24, -28); ctx.lineTo(24, -28);
                    ctx.stroke();
                    ctx.fillStyle = '#38bdf8';
                    ctx.fillRect(-26, -34, 5, 6);
                    ctx.fillRect(21, -34, 5, 6);

                    drawCuteAuraDriver(0, -22, 0.78, true, false, 0);

                    ctx.strokeStyle = '#00f0ff';
                    ctx.lineWidth = 3;
                    ctx.beginPath();
                    ctx.moveTo(-10, -22); ctx.lineTo(-20, -28);
                    ctx.moveTo(10, -22); ctx.lineTo(20, -28);
                    ctx.stroke();

                    ctx.save();
                    ctx.shadowColor = '#ef4444';
                    ctx.shadowBlur = 12;
                    ctx.fillStyle = '#ef4444';
                    ctx.fillRect(-10, 4, 20, 5);
                    ctx.restore();

                    ctx.restore();

                }} else if (curMode === 'BUS') {{
                    // =========================================================================
                    // 3. TRANSIT COACH BUS
                    // =========================================================================
                    drawHeadlightBeams(auraBaseX - 45, auraBaseX + 45, auraBaseY + 6, 150, 'rgba(254, 240, 138, 0.45)');

                    ctx.save();
                    ctx.translate(auraBaseX, auraBaseY + suspensionBob * 0.7);
                    ctx.rotate(chassisRoll * 0.6);

                    drawSpinningWheel(-56, 20, 14, 18, wheelAngle, true);
                    drawSpinningWheel(56, 20, 14, 18, wheelAngle, true);

                    const busGrad = ctx.createLinearGradient(-65, -50, 65, 30);
                    busGrad.addColorStop(0, '#1e3a8a');
                    busGrad.addColorStop(0.7, '#1d4ed8');
                    busGrad.addColorStop(1, '#0f172a');
                    ctx.fillStyle = busGrad;
                    drawRoundedRect(ctx, -68, -62, 136, 80, 12);
                    ctx.fill();
                    ctx.strokeStyle = 'rgba(56, 189, 248, 0.7)';
                    ctx.lineWidth = 2;
                    ctx.stroke();

                    ctx.fillStyle = '#020617';
                    drawRoundedRect(ctx, -56, -56, 112, 14, 4);
                    ctx.fill();
                    ctx.fillStyle = '#f59e0b';
                    ctx.font = 'bold 9px monospace';
                    ctx.textAlign = 'center';
                    ctx.fillText('✦ NEXTROUTE EXPRESS ✦', 0, -46);

                    ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
                    drawRoundedRect(ctx, -58, -38, 116, 32, 6);
                    ctx.fill();
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 1;
                    ctx.stroke();

                    drawCuteAuraDriver(0, -22, 0.82, true, true, 16);

                    ctx.save();
                    ctx.shadowColor = '#ef4444';
                    ctx.shadowBlur = 10;
                    ctx.fillStyle = '#ef4444';
                    ctx.fillRect(-64, -2, 6, 16);
                    ctx.fillRect(58, -2, 6, 16);
                    ctx.restore();

                    ctx.restore();

                }} else if (curMode === 'BICYCLE') {{
                    // =========================================================================
                    // 4. BICYCLE (ROAD CYCLE)
                    // =========================================================================
                    ctx.save();
                    ctx.translate(auraBaseX, auraBaseY + suspensionBob);
                    ctx.rotate(turnTilt * 1.5);

                    drawSpinningWheel(0, 18, 14, 18, wheelAngle);

                    ctx.strokeStyle = '#10b981';
                    ctx.lineWidth = 3.5;
                    ctx.beginPath();
                    ctx.moveTo(0, 18); ctx.lineTo(-12, -8);
                    ctx.lineTo(0, -24);
                    ctx.lineTo(0, 18);
                    ctx.moveTo(0, -24); ctx.lineTo(16, -10);
                    ctx.lineTo(-12, -8);
                    ctx.stroke();

                    ctx.fillStyle = '#1e293b';
                    drawRoundedRect(ctx, -10, -27, 20, 5, 2);
                    ctx.fill();

                    const crankR = 9;
                    const crankX = Math.cos(wheelAngle * 0.7) * crankR;
                    const crankY = Math.sin(wheelAngle * 0.7) * crankR;
                    ctx.strokeStyle = '#94a3b8';
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(-12 - crankX, -8 - crankY);
                    ctx.lineTo(-12 + crankX, -8 + crankY);
                    ctx.stroke();

                    ctx.strokeStyle = '#cbd5e1';
                    ctx.lineWidth = 2.5;
                    ctx.beginPath();
                    ctx.moveTo(-16, -28); ctx.lineTo(16, -28);
                    ctx.stroke();

                    drawCuteAuraDriver(0, -32, 0.75, true, false, 0);

                    ctx.strokeStyle = '#00f0ff';
                    ctx.lineWidth = 3;
                    ctx.beginPath();
                    ctx.moveTo(-6, -24); ctx.lineTo(-12 - crankX, -8 - crankY);
                    ctx.moveTo(6, -24); ctx.lineTo(-12 + crankX, -8 + crankY);
                    ctx.stroke();

                    ctx.beginPath();
                    ctx.moveTo(-8, -32); ctx.lineTo(-14, -28);
                    ctx.moveTo(8, -32); ctx.lineTo(14, -28);
                    ctx.stroke();

                    ctx.fillStyle = '#ef4444';
                    ctx.shadowColor = '#ef4444';
                    ctx.shadowBlur = 8;
                    ctx.beginPath();
                    ctx.arc(0, -21, 3, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.shadowBlur = 0;

                    ctx.restore();

                }} else if (curMode === 'TRUCK') {{
                    // =========================================================================
                    // 5. HEAVY CARGO TRUCK / SEMI
                    // =========================================================================
                    drawHeadlightBeams(auraBaseX - 48, auraBaseX + 48, auraBaseY + 6, 160, 'rgba(254, 240, 138, 0.45)');

                    ctx.save();
                    ctx.translate(auraBaseX, auraBaseY + suspensionBob * 1.1);
                    ctx.rotate(chassisRoll * 0.7);

                    drawSpinningWheel(-60, 24, 15, 20, wheelAngle, true);
                    drawSpinningWheel(-45, 24, 15, 20, wheelAngle, true);
                    drawSpinningWheel(45, 24, 15, 20, wheelAngle, true);
                    drawSpinningWheel(60, 24, 15, 20, wheelAngle, true);

                    const truckGrad = ctx.createLinearGradient(-65, -70, 65, 30);
                    truckGrad.addColorStop(0, '#9a3412');
                    truckGrad.addColorStop(0.6, '#c2410c');
                    truckGrad.addColorStop(1, '#431407');
                    ctx.fillStyle = truckGrad;
                    drawRoundedRect(ctx, -68, -75, 136, 95, 10);
                    ctx.fill();
                    ctx.strokeStyle = '#ea580c';
                    ctx.lineWidth = 2;
                    ctx.stroke();

                    ctx.fillStyle = '#cbd5e1';
                    ctx.fillRect(-74, -85, 6, 50);
                    ctx.fillRect(68, -85, 6, 50);

                    ctx.save();
                    ctx.fillStyle = '#f59e0b';
                    ctx.shadowColor = '#f59e0b';
                    ctx.shadowBlur = 6;
                    for (let i = -2; i <= 2; i++) {{
                        ctx.beginPath();
                        ctx.arc(i * 18, -72, 3, 0, Math.PI * 2);
                        ctx.fill();
                    }}
                    ctx.restore();

                    ctx.fillStyle = 'rgba(15, 23, 42, 0.88)';
                    drawRoundedRect(ctx, -56, -58, 112, 34, 6);
                    ctx.fill();
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 1;
                    ctx.stroke();

                    drawCuteAuraDriver(0, -40, 0.84, true, true, 18);

                    ctx.fillStyle = '#facc15';
                    ctx.fillRect(-64, 4, 128, 12);
                    ctx.fillStyle = '#1e293b';
                    for (let k = -5; k <= 5; k++) {{
                        ctx.beginPath();
                        ctx.moveTo(k * 12 - 4, 16);
                        ctx.lineTo(k * 12 + 4, 4);
                        ctx.lineTo(k * 12 + 8, 4);
                        ctx.lineTo(k * 12, 16);
                        ctx.fill();
                    }}

                    ctx.restore();

                }} else if (curMode === 'TRACTOR') {{
                    // =========================================================================
                    // 6. AGRICULTURAL TRACTOR
                    // =========================================================================
                    drawHeadlightBeams(auraBaseX - 35, auraBaseX + 35, auraBaseY + 4, 120, 'rgba(254, 240, 138, 0.4)');

                    ctx.save();
                    ctx.translate(auraBaseX, auraBaseY + Math.sin(elapsed * 22) * 2.5);
                    ctx.rotate(chassisRoll);

                    drawSpinningWheel(-52, 12, 18, 24, wheelAngle, true);
                    drawSpinningWheel(52, 12, 18, 24, wheelAngle, true);

                    ctx.fillStyle = '#15803d';
                    drawRoundedRect(ctx, -38, -25, 76, 40, 6);
                    ctx.fill();
                    ctx.strokeStyle = '#22c55e';
                    ctx.lineWidth = 2;
                    ctx.stroke();

                    ctx.fillStyle = '#1e293b';
                    ctx.fillRect(-28, -52, 4, 30);
                    ctx.fillStyle = 'rgba(203, 213, 225, 0.4)';
                    ctx.beginPath();
                    ctx.arc(-26 + Math.sin(elapsed * 10) * 3, -56 - (elapsed * 15 % 15), 4, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.fillStyle = '#166534';
                    drawRoundedRect(ctx, -56, -14, 18, 24, 4);
                    drawRoundedRect(ctx, 38, -14, 18, 24, 4);
                    ctx.fill();

                    ctx.strokeStyle = '#eab308';
                    ctx.lineWidth = 4;
                    ctx.beginPath();
                    ctx.moveTo(-28, 0); ctx.lineTo(-28, -48);
                    ctx.lineTo(28, -48); ctx.lineTo(28, 0);
                    ctx.stroke();

                    drawCuteAuraDriver(0, -22, 0.85, true, true, 16);

                    ctx.restore();

                }} else if (curMode === 'FLIGHT') {{
                    // =========================================================================
                    // 7. SUPERSONIC FLIGHT / AIR JET
                    // =========================================================================
                    const flightAlt = Math.sin(elapsed * 2.0) * 8.0;
                    ctx.save();
                    ctx.translate(auraBaseX, auraBaseY - 52 + flightAlt);
                    ctx.rotate(turnTilt * 2.2);

                    const thrustLen = 35 + Math.sin(elapsed * 25) * 8;
                    const pGradL = ctx.createLinearGradient(-35, 10, -35, 10 + thrustLen);
                    pGradL.addColorStop(0, '#00f0ff');
                    pGradL.addColorStop(0.4, 'rgba(56, 189, 248, 0.8)');
                    pGradL.addColorStop(1, 'rgba(56, 189, 248, 0)');
                    ctx.fillStyle = pGradL;
                    ctx.beginPath();
                    ctx.moveTo(-42, 10); ctx.lineTo(-28, 10); ctx.lineTo(-35, 10 + thrustLen);
                    ctx.closePath();
                    ctx.fill();

                    const pGradR = ctx.createLinearGradient(35, 10, 35, 10 + thrustLen);
                    pGradR.addColorStop(0, '#00f0ff');
                    pGradR.addColorStop(0.4, 'rgba(56, 189, 248, 0.8)');
                    pGradR.addColorStop(1, 'rgba(56, 189, 248, 0)');
                    ctx.fillStyle = pGradR;
                    ctx.beginPath();
                    ctx.moveTo(28, 10); ctx.lineTo(42, 10); ctx.lineTo(35, 10 + thrustLen);
                    ctx.closePath();
                    ctx.fill();

                    ctx.fillStyle = '#f8fafc';
                    ctx.beginPath();
                    ctx.moveTo(0, -25);
                    ctx.lineTo(75, 4);
                    ctx.lineTo(60, 14);
                    ctx.lineTo(0, 5);
                    ctx.lineTo(-60, 14);
                    ctx.lineTo(-75, 4);
                    ctx.closePath();
                    ctx.fill();
                    ctx.strokeStyle = '#94a3b8';
                    ctx.lineWidth = 1.5;
                    ctx.stroke();

                    ctx.fillStyle = '#ef4444';
                    ctx.shadowColor = '#ef4444'; ctx.shadowBlur = 8;
                    ctx.beginPath(); ctx.arc(-74, 5, 3.5, 0, Math.PI * 2); ctx.fill();
                    ctx.fillStyle = '#22c55e';
                    ctx.shadowColor = '#22c55e'; ctx.shadowBlur = 8;
                    ctx.beginPath(); ctx.arc(74, 5, 3.5, 0, Math.PI * 2); ctx.fill();
                    ctx.shadowBlur = 0;

                    ctx.fillStyle = '#e2e8f0';
                    drawRoundedRect(ctx, -20, -38, 40, 50, 14);
                    ctx.fill();
                    ctx.strokeStyle = '#0284c7';
                    ctx.lineWidth = 2;
                    ctx.stroke();

                    ctx.fillStyle = 'rgba(6, 182, 212, 0.55)';
                    drawRoundedRect(ctx, -14, -32, 28, 22, 7);
                    ctx.fill();

                    drawCuteAuraDriver(0, -20, 0.72, true, false, 0);

                    ctx.restore();

                }} else if (curMode === 'WATERWAY') {{
                    // =========================================================================
                    // 8. WATERWAY CRUISE / FAST FERRY
                    // =========================================================================
                    const waveRoll = Math.sin(elapsed * 2.8) * 0.05;
                    const waveBob = Math.sin(elapsed * 3.2) * 3.5;

                    ctx.save();
                    ctx.translate(auraBaseX, auraBaseY + waveBob);
                    ctx.rotate(waveRoll);

                    ctx.fillStyle = 'rgba(14, 165, 233, 0.45)';
                    ctx.beginPath();
                    ctx.ellipse(0, 16, 75, 12, 0, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)';
                    ctx.lineWidth = 1.5;
                    ctx.beginPath();
                    ctx.arc(-55, 16, 12, 0, Math.PI);
                    ctx.arc(55, 16, 12, 0, Math.PI);
                    ctx.stroke();

                    const hullGrad = ctx.createLinearGradient(-60, 0, 60, 20);
                    hullGrad.addColorStop(0, '#0369a1');
                    hullGrad.addColorStop(0.5, '#0284c7');
                    hullGrad.addColorStop(1, '#075985');
                    ctx.fillStyle = hullGrad;
                    ctx.beginPath();
                    ctx.moveTo(-65, -4);
                    ctx.lineTo(65, -4);
                    ctx.lineTo(50, 18);
                    ctx.lineTo(-50, 18);
                    ctx.closePath();
                    ctx.fill();
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 1.5;
                    ctx.stroke();

                    ctx.fillStyle = '#f8fafc';
                    drawRoundedRect(ctx, -42, -26, 84, 24, 5);
                    ctx.fill();
                    ctx.strokeStyle = '#cbd5e1';
                    ctx.stroke();

                    ctx.fillStyle = '#fef08a';
                    for (let p = -3; p <= 3; p++) {{
                        ctx.beginPath();
                        ctx.arc(p * 11, -14, 2.5, 0, Math.PI * 2);
                        ctx.fill();
                    }}

                    ctx.fillStyle = '#0f172a';
                    ctx.fillRect(-2, -42, 4, 16);
                    const radarW = Math.cos(elapsed * 4) * 16;
                    ctx.strokeStyle = '#00f0ff';
                    ctx.lineWidth = 2.5;
                    ctx.beginPath();
                    ctx.moveTo(-radarW, -42); ctx.lineTo(radarW, -42);
                    ctx.stroke();

                    drawCuteAuraDriver(0, -22, 0.76, true, true, 12);

                    ctx.fillStyle = '#ef4444';
                    ctx.fillRect(-62, -6, 5, 4);
                    ctx.fillStyle = '#22c55e';
                    ctx.fillRect(57, -6, 5, 4);

                    ctx.restore();

                }} else if (curMode === 'TRAIN') {{
                    // =========================================================================
                    // 9. HIGH-SPEED EXPRESS BULLET TRAIN
                    // =========================================================================
                    ctx.save();
                    ctx.strokeStyle = '#cbd5e1';
                    ctx.lineWidth = 3;
                    ctx.beginPath();
                    ctx.moveTo(auraBaseX - 45, auraBaseY + 26); ctx.lineTo(auraBaseX - 18, auraBaseY - 60);
                    ctx.moveTo(auraBaseX + 45, auraBaseY + 26); ctx.lineTo(auraBaseX + 18, auraBaseY - 60);
                    ctx.stroke();
                    ctx.strokeStyle = '#78350f';
                    ctx.lineWidth = 2;
                    for (let r = 0; r < 5; r++) {{
                        const ry = auraBaseY + 22 - (r * 16);
                        const rw = 45 - (r * 5);
                        ctx.beginPath();
                        ctx.moveTo(auraBaseX - rw, ry); ctx.lineTo(auraBaseX + rw, ry);
                        ctx.stroke();
                    }}
                    ctx.restore();

                    drawHeadlightBeams(auraBaseX - 35, auraBaseX + 35, auraBaseY + 6, 170, 'rgba(254, 240, 138, 0.55)');

                    ctx.save();
                    ctx.translate(auraBaseX, auraBaseY + suspensionBob * 0.6);
                    ctx.rotate(chassisRoll * 0.5);

                    const trainGrad = ctx.createLinearGradient(-50, -50, 50, 30);
                    trainGrad.addColorStop(0, '#6366f1');
                    trainGrad.addColorStop(0.6, '#4f46e5');
                    trainGrad.addColorStop(1, '#312e81');
                    ctx.fillStyle = trainGrad;
                    drawRoundedRect(ctx, -52, -64, 104, 84, 16);
                    ctx.fill();
                    ctx.strokeStyle = '#818cf8';
                    ctx.lineWidth = 2;
                    ctx.stroke();

                    ctx.strokeStyle = '#94a3b8';
                    ctx.lineWidth = 2.5;
                    ctx.beginPath();
                    ctx.moveTo(-16, -64); ctx.lineTo(-8, -82); ctx.lineTo(8, -82); ctx.lineTo(16, -64);
                    ctx.moveTo(-20, -82); ctx.lineTo(20, -82);
                    ctx.stroke();

                    if (Math.sin(elapsed * 18) > 0.85) {{
                        ctx.fillStyle = '#00f0ff';
                        ctx.shadowColor = '#00f0ff'; ctx.shadowBlur = 10;
                        ctx.beginPath(); ctx.arc(0, -82, 3.5, 0, Math.PI * 2); ctx.fill();
                        ctx.shadowBlur = 0;
                    }}

                    ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
                    drawRoundedRect(ctx, -42, -45, 84, 28, 8);
                    ctx.fill();
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 1;
                    ctx.stroke();

                    drawCuteAuraDriver(0, -32, 0.8, true, true, 16);

                    ctx.save();
                    ctx.shadowColor = '#fef08a';
                    ctx.shadowBlur = 14;
                    ctx.fillStyle = '#fef08a';
                    ctx.beginPath();
                    ctx.arc(-34, 4, 6, 0, Math.PI * 2);
                    ctx.arc(34, 4, 6, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();

                    ctx.restore();

                }} else {{
                    // =========================================================================
                    // 10. DEFAULT CAR / AUTOMOBILE (SPORT SEDAN)
                    // =========================================================================
                    drawHeadlightBeams(auraBaseX - 32, auraBaseX + 32, auraBaseY, 130, 'rgba(224, 242, 254, 0.45)');

                    ctx.save();
                    ctx.translate(auraBaseX, auraBaseY + suspensionBob);
                    ctx.rotate(chassisRoll);

                    drawSpinningWheel(-44, 14, 12, 16, wheelAngle);
                    drawSpinningWheel(44, 14, 12, 16, wheelAngle);

                    const carGrad = ctx.createLinearGradient(-50, -10, 50, 20);
                    carGrad.addColorStop(0, '#0369a1');
                    carGrad.addColorStop(0.5, '#0284c7');
                    carGrad.addColorStop(1, '#0c4a6e');
                    ctx.fillStyle = carGrad;
                    drawRoundedRect(ctx, -52, -4, 104, 22, 7);
                    ctx.fill();
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 1.5;
                    ctx.stroke();

                    ctx.fillStyle = '#0f172a';
                    drawRoundedRect(ctx, -38, -32, 76, 30, 8);
                    ctx.fill();
                    ctx.strokeStyle = 'rgba(56, 189, 248, 0.6)';
                    ctx.stroke();

                    ctx.fillStyle = 'rgba(14, 116, 144, 0.65)';
                    drawRoundedRect(ctx, -34, -28, 68, 22, 5);
                    ctx.fill();

                    drawCuteAuraDriver(0, -12, 0.72, true, true, 12);

                    ctx.save();
                    ctx.shadowColor = '#ef4444';
                    ctx.shadowBlur = 12;
                    ctx.fillStyle = '#ef4444';
                    ctx.fillRect(-50, 0, 16, 6);
                    ctx.fillRect(34, 0, 16, 6);
                    ctx.restore();

                    const isBlinkOn = Math.sin(elapsed * 12) > 0;
                    if (currentAnimState === 'turn_left' && isBlinkOn) {{
                        ctx.fillStyle = '#f59e0b';
                        ctx.fillRect(-52, -3, 8, 5);
                    }} else if (currentAnimState === 'turn_right' && isBlinkOn) {{
                        ctx.fillStyle = '#f59e0b';
                        ctx.fillRect(44, -3, 8, 5);
                    }}

                    ctx.fillStyle = '#cbd5e1';
                    ctx.fillRect(-28, 14, 8, 4);
                    ctx.fillRect(20, 14, 8, 4);

                    ctx.restore();
                }}

                ctx.restore();

                fallback2DAnimId = requestAnimationFrame(render);
            }}

            render();
        }}

        function launchThreeSceneWithRetry() {{
            let attempts = 0;
            const maxAttempts = 50;

            function checkThree() {{
                attempts++;
                const canvas = document.getElementById('aura-threejs-canvas');
                const container = document.getElementById('aura-3d-scene-box');

                if (typeof THREE !== 'undefined' && canvas && container) {{
                    try {{
                        const ok = initAuraThreeScene();
                        if (ok) {{
                            threeSceneStarted = true;
                            return;
                        }}
                    }} catch(e) {{
                        console.warn("Three.js init attempt error:", e);
                    }}
                }}

                if (attempts < maxAttempts && !threeSceneStarted) {{
                    setTimeout(checkThree, 100);
                }}
            }}

            setTimeout(checkThree, 60);
        }}

        window.toggleEngineCompanion = function() {{
            const canvas = document.getElementById('aura-threejs-canvas');
            const scenicCanvas = document.getElementById('aura-scenic-canvas');
            const hudText = document.getElementById('hud-runtime-text');
            const hudBadge = document.getElementById('hud-runtime-badge');
            const hudDot = document.getElementById('hud-pulse-dot');

            if (threeSceneStarted) {{
                threeSceneStarted = false;
                if (threeAnimId) cancelAnimationFrame(threeAnimId);
                if (canvas) canvas.style.display = 'none';
                if (scenicCanvas) scenicCanvas.style.display = 'block';
                if (hudText) hudText.innerText = '✦ 2.5D SCENIC RUNTIME ACTIVE';
                if (hudBadge) {{
                    hudBadge.style.borderColor = 'rgba(56, 189, 248, 0.6)';
                    hudBadge.style.color = '#38bdf8';
                }}
                if (hudDot) {{
                    hudDot.style.background = '#38bdf8';
                    hudDot.style.boxShadow = '0 0 8px #38bdf8';
                }}
                startScenicFallback2D();
            }} else {{
                if (typeof THREE !== 'undefined') {{
                    if (fallback2DAnimId) cancelAnimationFrame(fallback2DAnimId);
                    if (scenicCanvas) scenicCanvas.style.display = 'none';
                    if (canvas) canvas.style.display = 'block';
                    initAuraThreeScene();
                }} else {{
                    console.warn("Three.js library is loading; scenic engine active.");
                }}
            }}
        }};

        function syncIframeHeight() {{
            try {{
                const root = document.getElementById('aura-journey-root');
                if (root) {{
                    const h = Math.ceil(root.getBoundingClientRect().height + 25);
                    if (window.frameElement) {{
                        window.frameElement.style.height = h + 'px';
                        window.frameElement.height = h;
                    }}
                    if (window.parent && window.parent !== window) {{
                        window.parent.postMessage({{ type: 'streamlit:setFrameHeight', height: h }}, '*');
                    }}
                }}
            }} catch(e) {{}}
        }}
        window.addEventListener('load', syncIframeHeight);
        window.addEventListener('resize', syncIframeHeight);
        setTimeout(syncIframeHeight, 100);
        setTimeout(syncIframeHeight, 400);
        setTimeout(syncIframeHeight, 1200);

        // Initialize
        renderPipeline();
        initSensorWatchers();
        startStepProgressionLoop();
        updateMotionUI(isLiveMoving ? currentSpeedKmh : 0.0, motionState, isLiveMoving ? '🛰️ Parallel Sensor GPS' : 'Sensor Ready');
        // Auto-synchronize real-time device clock and lighting immediately and keep continuous live sync
        syncRealTimeAutoEnvironment();
        setTimeout(syncRealTimeAutoEnvironment, 100);
        setTimeout(syncRealTimeAutoEnvironment, 600);
        setInterval(syncRealTimeAutoEnvironment, 3000);
        // Immediately engage 2.5D scenic companion engine for instant visual rendering,
        // and actively poll in background to promote to full 3D WebGL as soon as Three.js CDN loads!
        startScenicFallback2D();
        launchThreeSceneWithRetry();
    }})();
    </script>
    """
