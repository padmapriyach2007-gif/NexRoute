"""
CampusAegis Real-World Map & Geocoding Service
Provides place-name geocoding, reverse geocoding, and interactive Folium/Leaflet map generation.
Uses OpenStreetMap Nominatim API with an integrated offline cache and fallback directory.

Safety & Licensing Notice:
Uses OpenStreetMap data under the Open Database License (ODbL).
Nominatim requests include standard User-Agent headers and rate-limiting safeguards.
"""

import os
import requests
import json
import time
from typing import Dict, List, Tuple, Optional, Any
import folium
from folium import plugins
from concurrent.futures import ThreadPoolExecutor
import re

# Pre-cached regional landmarks, micro-areas, wards, colonies, and campus blocks
OFFLINE_GEOCODE_CACHE = {
    # Darsi Regional Town & Hub
    "darsi": {"lat": 15.7688, "lon": 79.6792, "name": "Darsi Town, Prakasam, Andhra Pradesh, India"},
    "darsi town": {"lat": 15.7688, "lon": 79.6792, "name": "Darsi Town, Prakasam, Andhra Pradesh, India"},
    "darsi town, andhra pradesh, india": {"lat": 15.7688, "lon": 79.6792, "name": "Darsi Town, Prakasam, Andhra Pradesh, India"},

    # Baseline Universities & Campus Micro-Locations
    "vignan university": {"lat": 16.2335, "lon": 80.5505, "name": "Vignan's Foundation for Science, Technology & Research, Vadlamudi"},
    "vignan campus": {"lat": 16.2335, "lon": 80.5505, "name": "Vignan University Main Campus"},
    "vignan main gate": {"lat": 16.2325, "lon": 80.5490, "name": "Vignan University Main Entrance Arch, Vadlamudi Road"},
    "vignan library": {"lat": 16.2338, "lon": 80.5512, "name": "NTR Vignan Central Library Block"},
    "ntr library": {"lat": 16.2338, "lon": 80.5512, "name": "NTR Vignan Central Library Block"},
    "chemical engineering": {"lat": 16.2340, "lon": 80.5498, "name": "Chemical Reaction Engineering Department Block"},
    "chemical reaction": {"lat": 16.2340, "lon": 80.5498, "name": "Chemical Reaction Engineering Department Block"},
    "cse block": {"lat": 16.2348, "lon": 80.5515, "name": "Computer Science & Engineering Academic Block"},
    "computer science": {"lat": 16.2348, "lon": 80.5515, "name": "Computer Science & Engineering Department"},
    "it block": {"lat": 16.2346, "lon": 80.5518, "name": "Information Technology Department & Lab Block"},
    "a-block": {"lat": 16.2330, "lon": 80.5500, "name": "A-Block Administrative Complex"},
    "admin block": {"lat": 16.2330, "lon": 80.5500, "name": "Vignan Foundation Administrative Block"},
    "h-block": {"lat": 16.2342, "lon": 80.5522, "name": "H-Block Academic Complex"},
    "u-block": {"lat": 16.2352, "lon": 80.5508, "name": "U-Block Technology & Science Center"},
    "lara college": {"lat": 16.2375, "lon": 80.5480, "name": "Lara Institute of Technology & Sciences"},
    "lara engineering": {"lat": 16.2375, "lon": 80.5480, "name": "Lara Institute of Technology & Sciences"},
    "pharmacy block": {"lat": 16.2365, "lon": 80.5490, "name": "Vignan Institute of Pharmaceutical Sciences"},
    "boys hostel": {"lat": 16.2315, "lon": 80.5535, "name": "Vignan Boys Hostel Complex (Priyamvada)"},
    "girls hostel": {"lat": 16.2355, "lon": 80.5540, "name": "Vignan Girls Hostel Complex"},
    "open air theatre": {"lat": 16.2332, "lon": 80.5518, "name": "Vignan Open Air Theatre (OAT)"},
    "sports complex": {"lat": 16.2310, "lon": 80.5485, "name": "Vignan University Sports Complex & Athletic Grounds"},
    "play grounds": {"lat": 16.2310, "lon": 80.5485, "name": "Vignan University Sports Ground"},
    "food court": {"lat": 16.2336, "lon": 80.5525, "name": "Vignan Central Food Court & Student Cafeteria"},
    "convocation hall": {"lat": 16.2328, "lon": 80.5508, "name": "Mahathi Convocation Auditorium"},

    # Guntur Colonies, Small Areas & Neighborhood Wards
    "arundelpet": {"lat": 16.3075, "lon": 80.4350, "name": "Arundelpet, Guntur"},
    "brodipet": {"lat": 16.3015, "lon": 80.4420, "name": "Brodipet Commercial Center, Guntur"},
    "kothapet": {"lat": 16.3120, "lon": 80.4480, "name": "Kothapet, Guntur"},
    "lalapet": {"lat": 16.3080, "lon": 80.4520, "name": "Lalapet, Guntur"},
    "pattabhipuram": {"lat": 16.2950, "lon": 80.4280, "name": "Pattabhipuram Residential Area, Guntur"},
    "gorantla": {"lat": 16.3250, "lon": 80.4180, "name": "Gorantla, Guntur"},
    "vidya nagar": {"lat": 16.2880, "lon": 80.4220, "name": "Vidya Nagar, Guntur"},
    "syamala nagar": {"lat": 16.2920, "lon": 80.4310, "name": "Syamala Nagar, Guntur"},
    "old guntur": {"lat": 16.3150, "lon": 80.4600, "name": "Old Guntur Historic Center"},
    "autonagar": {"lat": 16.2890, "lon": 80.4550, "name": "Auto Nagar Industrial Hub, Guntur"},
    "auto nagar": {"lat": 16.2890, "lon": 80.4550, "name": "Auto Nagar Industrial Hub, Guntur"},
    "etukuru": {"lat": 16.2750, "lon": 80.4720, "name": "Etukuru Bypass Junction, Guntur"},
    "pedakakani": {"lat": 16.3420, "lon": 80.5050, "name": "Pedakakani Temple Center, Guntur District"},
    "kaza": {"lat": 16.3750, "lon": 80.5580, "name": "Kaza Toll Plaza, NH-16"},
    "mangalagiri": {"lat": 16.4350, "lon": 80.5680, "name": "Mangalagiri Town & AIIMS, Guntur District"},
    "gaddipadu": {"lat": 16.3210, "lon": 80.4780, "name": "Gaddipadu Village Area, Guntur"},
    "takkellapadu": {"lat": 16.3350, "lon": 80.4650, "name": "Takkellapadu, Guntur"},
    "uppalapadu": {"lat": 16.2780, "lon": 80.5280, "name": "Uppalapadu Bird Sanctuary, Guntur District"},
    "koritepadu": {"lat": 16.3120, "lon": 80.4280, "name": "Koritepadu, Guntur"},
    "lakshmipuram": {"lat": 16.3010, "lon": 80.4310, "name": "Lakshmipuram Main Road, Guntur"},
    "gujjanagundla": {"lat": 16.2920, "lon": 80.4180, "name": "Gujjanagundla Ring Road, Guntur"},
    "guntur railway station": {"lat": 16.3045, "lon": 80.4445, "name": "Guntur Junction Railway Station"},
    "guntur bus stand": {"lat": 16.3080, "lon": 80.4420, "name": "NTR RTC Bus Stand, Guntur"},
    "guntur": {"lat": 16.3067, "lon": 80.4365, "name": "Guntur City Center, Andhra Pradesh"},

    # Intermediate Villages, Mandals & Rural Corridors
    "budampadu": {"lat": 16.2620, "lon": 80.4680, "name": "Budampadu Village Cross, Guntur District"},
    "selapadu": {"lat": 16.2480, "lon": 80.5220, "name": "Selapadu Village, Guntur District"},
    "sangam jagarlamudi": {"lat": 16.2350, "lon": 80.5050, "name": "Sangam Jagarlamudi Junction"},
    "sangam": {"lat": 16.2350, "lon": 80.5050, "name": "Sangam Jagarlamudi Junction"},
    "sitarampuram": {"lat": 16.2410, "lon": 80.5180, "name": "Sitarampuram Rural Colony"},
    "kothareddypalem": {"lat": 16.2180, "lon": 80.4850, "name": "Kothareddypalem Village"},
    "pathareddypalem": {"lat": 16.2120, "lon": 80.4890, "name": "Pathareddypalem, Chebrolu Mandal"},
    "gundavaram": {"lat": 16.2380, "lon": 80.4780, "name": "Gundavaram Rural Junction"},
    "godavarru": {"lat": 16.2450, "lon": 80.4720, "name": "Godavarru Village, Guntur District"},
    "lemallepadu": {"lat": 16.2220, "lon": 80.4550, "name": "Lemallepadu Village"},
    "vatticherukuru": {"lat": 16.1980, "lon": 80.4450, "name": "Vatticherukuru Mandal Headquarters"},
    "kovelamudi": {"lat": 16.2050, "lon": 80.4680, "name": "Kovelamudi Village"},
    "narakodur": {"lat": 16.2650, "lon": 80.4980, "name": "Narakodur Center Cross, Guntur District"},
    "vadlamudi": {"lat": 16.2319, "lon": 80.5539, "name": "Vadlamudi Center & Municipal Hub"},
    "chebrolu": {"lat": 16.2010, "lon": 80.5280, "name": "Chebrolu Heritage Center & Historical Temples"},
    "sekuru": {"lat": 16.2550, "lon": 80.5150, "name": "Sekuru Village"},
    "duggirala": {"lat": 16.3280, "lon": 80.6280, "name": "Duggirala Agricultural Market Yard"},
    "pedavadlapudi": {"lat": 16.4150, "lon": 80.6050, "name": "Pedavadlapudi Rural Junction"},
    "kolakaluru": {"lat": 16.2950, "lon": 80.6150, "name": "Kolakaluru Village, Tenali Mandal"},
    "koppuravuru": {"lat": 16.2820, "lon": 80.4880, "name": "Koppuravuru Village, Pedakakani"},
    "namburu": {"lat": 16.3610, "lon": 80.4980, "name": "Namburu Village Center, Guntur District", "display_name": "Namburu, Pedakakani Mandal, Guntur District, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Namburu", "type": "village"},
    "namburu, guntur district": {"lat": 16.3610, "lon": 80.4980, "name": "Namburu Village Center, Guntur District", "display_name": "Namburu, Pedakakani Mandal, Guntur District, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Namburu", "type": "village"},

    # Tenali Town Wards, Landmarks, Small Areas & Environs
    "morrispet": {"lat": 16.2380, "lon": 80.6450, "name": "Morrispet, Tenali"},
    "chenchupet": {"lat": 16.2450, "lon": 80.6350, "name": "Chenchupet, Tenali"},
    "angalakuduru": {"lat": 16.2280, "lon": 80.6220, "name": "Angalakuduru Village, Tenali"},
    "nazerpet": {"lat": 16.2410, "lon": 80.6480, "name": "Nazerpet, Tenali"},
    "chinaravuru": {"lat": 16.2520, "lon": 80.6550, "name": "Chinaravuru, Tenali"},
    "pinapadu": {"lat": 16.2490, "lon": 80.6290, "name": "Pinapadu, Tenali"},
    "tenali railway station": {"lat": 16.2395, "lon": 80.6465, "name": "Tenali Junction Railway Station", "display_name": "Tenali Junction Railway Station, Station Road, Tenali, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Tenali", "type": "station"},
    "tenali": {"lat": 16.2430, "lon": 80.6400, "name": "Tenali Town, Guntur District", "display_name": "Tenali, Guntur District, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Tenali", "type": "town"},
    "tenali, andhra pradesh": {"lat": 16.2430, "lon": 80.6400, "name": "Tenali, Andhra Pradesh", "display_name": "Tenali, Guntur District, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Tenali", "type": "town"},
    "asta lakshmi temple, tenali": {"lat": 16.2385, "lon": 80.6420, "name": "Sri Asta Lakshmi Temple, Tenali", "display_name": "Sri Asta Lakshmi Temple, Tenali, Guntur District, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Tenali", "type": "place_of_worship"},
    "asta lakshmi temple": {"lat": 16.2385, "lon": 80.6420, "name": "Sri Asta Lakshmi Temple, Tenali", "display_name": "Sri Asta Lakshmi Temple, Tenali, Guntur District, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Tenali", "type": "place_of_worship"},
    "astalakshmi temple, tenali": {"lat": 16.2385, "lon": 80.6420, "name": "Sri Asta Lakshmi Temple, Tenali", "display_name": "Sri Asta Lakshmi Temple, Tenali, Guntur District, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Tenali", "type": "place_of_worship"},
    "astalakshmi temple": {"lat": 16.2385, "lon": 80.6420, "name": "Sri Asta Lakshmi Temple, Tenali", "display_name": "Sri Asta Lakshmi Temple, Tenali, Guntur District, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Tenali", "type": "place_of_worship"},
    "bsr enclave": {"lat": 16.23454, "lon": 80.65197, "name": "BSR Enclave, Sarojini Naidu Street, Tenali", "display_name": "BSR Enclave, Sarojini Naidu Street, Tenali, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Tenali"},
    "sarojini naidu street": {"lat": 16.23454, "lon": 80.65180, "name": "Sarojini Naidu Street, Tenali", "display_name": "Sarojini Naidu Street, Tenali, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Tenali"},
    "amaravati": {"lat": 16.5417, "lon": 80.5150, "name": "Amaravati Capital City, Andhra Pradesh", "display_name": "AP State Secretariat, Velagapudi, Amaravati Capital City, Guntur District, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Amaravati", "type": "city"},
    "amaravathi": {"lat": 16.5417, "lon": 80.5150, "name": "Amaravati Capital City, Andhra Pradesh", "display_name": "AP State Secretariat, Velagapudi, Amaravati Capital City, Guntur District, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Amaravati", "type": "city"},
    "amaravati capital": {"lat": 16.5417, "lon": 80.5150, "name": "Amaravati Capital City, Andhra Pradesh", "display_name": "AP State Secretariat, Velagapudi, Amaravati Capital City, Guntur District, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Amaravati", "type": "city"},

    # Campus Specific Locations & Internal POIs with Entrance Reference
    "the cafeteria, vignan university, vadlamudi": {"lat": 16.2336, "lon": 80.5525, "name": "Vignan Central Cafeteria & Food Court", "display_name": "The Cafeteria, Vignan University, Vadlamudi (Campus Internal POI - nearest road entrance: Main Entrance Arch)", "state": "Andhra Pradesh", "country": "India", "city": "Vadlamudi", "is_campus_internal": True, "campus_entrance": "Vignan University Main Entrance Arch, Vadlamudi Road", "entrance_lat": 16.2325, "entrance_lon": 80.5490, "type": "amenity"},
    "the cafeteria": {"lat": 16.2336, "lon": 80.5525, "name": "Vignan Central Cafeteria & Food Court", "display_name": "The Cafeteria, Vignan University, Vadlamudi (Campus Internal POI - nearest road entrance: Main Entrance Arch)", "state": "Andhra Pradesh", "country": "India", "city": "Vadlamudi", "is_campus_internal": True, "campus_entrance": "Vignan University Main Entrance Arch, Vadlamudi Road", "entrance_lat": 16.2325, "entrance_lon": 80.5490, "type": "amenity"},
    "cafeteria": {"lat": 16.2336, "lon": 80.5525, "name": "Vignan Central Cafeteria & Food Court", "display_name": "Vignan Central Cafeteria & Food Court, Vadlamudi (Campus Internal POI - nearest road entrance: Main Entrance Arch)", "state": "Andhra Pradesh", "country": "India", "city": "Vadlamudi", "is_campus_internal": True, "campus_entrance": "Vignan University Main Entrance Arch, Vadlamudi Road", "entrance_lat": 16.2325, "entrance_lon": 80.5490, "type": "amenity"},
    "canteen": {"lat": 16.2336, "lon": 80.5525, "name": "Vignan Central Canteen & Food Court", "display_name": "Vignan Central Canteen, Vadlamudi (Campus Internal POI - nearest road entrance: Main Entrance Arch)", "state": "Andhra Pradesh", "country": "India", "city": "Vadlamudi", "is_campus_internal": True, "campus_entrance": "Vignan University Main Entrance Arch, Vadlamudi Road", "entrance_lat": 16.2325, "entrance_lon": 80.5490, "type": "amenity"},

    # Regional Towns & Mandals
    "bapatla": {"lat": 15.9042, "lon": 80.4674, "name": "Bapatla Town & Coastal Beach Center", "display_name": "Bapatla, Bapatla District, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Bapatla"},
    "ponnur": {"lat": 16.0667, "lon": 80.5667, "name": "Ponnur Town & Sakshi Bhavan", "display_name": "Ponnur, Guntur District, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Ponnur"},
    "chirala": {"lat": 15.8246, "lon": 80.3522, "name": "Chirala Textile Hub", "display_name": "Chirala, Bapatla District, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Chirala"},
    "repalle": {"lat": 16.0200, "lon": 80.8500, "name": "Repalle Port Town", "display_name": "Repalle, Bapatla District, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Repalle"},
    "narasaraopet": {"lat": 16.2360, "lon": 80.0499, "name": "Narasaraopet Commercial Center", "display_name": "Narasaraopet, Palnadu District, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Narasaraopet"},
    "sattenapalle": {"lat": 16.3950, "lon": 80.1550, "name": "Sattenapalle Center", "display_name": "Sattenapalle, Palnadu District, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Sattenapalle"},
    "chilakaluripet": {"lat": 16.0892, "lon": 80.1672, "name": "Chilakaluripet NH-16 Hub", "display_name": "Chilakaluripet, Palnadu District, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Chilakaluripet"},

    # Major Regional Transit Hubs & Capital Centers
    "vijayawada": {"lat": 16.5062, "lon": 80.6480, "name": "Vijayawada Junction, Andhra Pradesh", "display_name": "Vijayawada, NTR District, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Vijayawada"},
    "amaravati": {"lat": 16.5417, "lon": 80.5150, "name": "Amaravati Capital City, Andhra Pradesh", "display_name": "Amaravati Capital City, Guntur District, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Amaravati"},
    "hyderabad": {"lat": 17.3850, "lon": 78.4867, "name": "Hyderabad, Telangana", "display_name": "Hyderabad, Telangana, India", "state": "Telangana", "country": "India", "city": "Hyderabad"},
    "hyderabad pakistan": {"lat": 25.3960, "lon": 68.3578, "name": "Hyderabad, Sindh", "display_name": "Hyderabad, Sindh, Pakistan", "state": "Sindh", "country": "Pakistan", "city": "Hyderabad"},
    "visakhapatnam": {"lat": 17.6868, "lon": 83.2185, "name": "Visakhapatnam Port City", "display_name": "Visakhapatnam, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Visakhapatnam"},
    "tirupati": {"lat": 13.6288, "lon": 79.4192, "name": "Tirupati Pilgrim City", "display_name": "Tirupati, Tirupati District, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Tirupati"},
    "vignan": {"lat": 16.2335, "lon": 80.5505, "name": "Vignan University (VFSTR), Vadlamudi", "display_name": "Vignan University, Vadlamudi, Guntur District, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Vadlamudi"},
    "aiims mangalagiri": {"lat": 16.4385, "lon": 80.5750, "name": "AIIMS Mangalagiri Hospital", "display_name": "All India Institute of Medical Sciences (AIIMS), Mangalagiri, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Mangalagiri"},
    "guntur medical college": {"lat": 16.2980, "lon": 80.4430, "name": "Guntur Medical College & Hospital", "display_name": "Guntur Medical College (GMC), Guntur, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Guntur"},
    "kanaka durga temple": {"lat": 16.5160, "lon": 80.6055, "name": "Sri Durga Malleswara Swamy Varla Devasthanam", "display_name": "Kanaka Durga Temple, Indrakeeladri, Vijayawada, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Vijayawada"},
    "prakasam barrage": {"lat": 16.5075, "lon": 80.6080, "name": "Prakasam Barrage Krishna River", "display_name": "Prakasam Barrage, Krishna River, Vijayawada, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Vijayawada"},
    "gannavaram airport": {"lat": 16.5280, "lon": 80.7980, "name": "Vijayawada International Airport (Gannavaram)", "display_name": "Vijayawada International Airport, Gannavaram, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Gannavaram"},
    "vijayawada railway station": {"lat": 16.5180, "lon": 80.6200, "name": "Vijayawada Junction Railway Station", "display_name": "Vijayawada Junction Railway Station, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Vijayawada"},
    "vijayawada bus stand": {"lat": 16.5110, "lon": 80.6280, "name": "Pandit Nehru Bus Station (PNBS), Vijayawada", "display_name": "Pandit Nehru Bus Station, Vijayawada, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Vijayawada"},
    "undavalli caves": {"lat": 16.4975, "lon": 80.5815, "name": "Undavalli Rock Cut Caves", "display_name": "Undavalli Caves, Guntur District, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Undavalli"},
    "kotappakonda": {"lat": 16.1420, "lon": 80.0380, "name": "Kotappakonda Temple", "display_name": "Kotappakonda Temple, Palnadu District, Andhra Pradesh", "state": "Andhra Pradesh", "country": "India", "city": "Narasaraopet"},
    "ongole": {"lat": 15.5057, "lon": 80.0499, "name": "Ongole Town Center", "display_name": "Ongole, Prakasam District, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Ongole"},
    "nellore": {"lat": 14.4426, "lon": 79.9865, "name": "Nellore City Center", "display_name": "Nellore, SPSR Nellore District, Andhra Pradesh, India", "state": "Andhra Pradesh", "country": "India", "city": "Nellore"},
}

# Curated prominent sub-areas, transit hubs, IT corridors & neighborhoods for multi-area selection
CITY_AREAS_DIRECTORY: Dict[str, List[Dict[str, Any]]] = {
    "hyderabad": [
        {"name": "Hyderabad City Center (Nampally / Abids)", "display_name": "Hyderabad City Center, Nampally / Abids, Hyderabad, Telangana", "city": "Hyderabad", "state": "Telangana", "country": "India", "lat": 17.3850, "lon": 78.4867, "category_icon": "🏛️", "category_name": "City Center", "area_badge": "Downtown Hub", "provider": "Verified Regional Gazetteer", "provider_id": "area_hyd_center"},
        {"name": "Rajiv Gandhi Int'l Airport (RGIA)", "display_name": "Rajiv Gandhi International Airport (RGIA), Shamshabad, Hyderabad, Telangana", "city": "Shamshabad", "state": "Telangana", "country": "India", "lat": 17.2403, "lon": 78.4294, "category_icon": "✈️", "category_name": "Airport", "area_badge": "Shamshabad Hub", "provider": "Verified Regional Gazetteer", "provider_id": "area_hyd_rgia"},
        {"name": "HITEC City / Madhapur (Cyber Towers)", "display_name": "HITEC City / Madhapur, Cyberabad IT Zone, Hyderabad, Telangana", "city": "Hyderabad", "state": "Telangana", "country": "India", "lat": 17.4485, "lon": 78.3772, "category_icon": "💻", "category_name": "Tech Corridor", "area_badge": "Cyberabad IT Zone", "provider": "Verified Regional Gazetteer", "provider_id": "area_hyd_hitec"},
        {"name": "Gachibowli Financial District", "display_name": "Gachibowli Financial District & ISB, Hyderabad, Telangana", "city": "Hyderabad", "state": "Telangana", "country": "India", "lat": 17.4401, "lon": 78.3489, "category_icon": "🏢", "category_name": "Financial District", "area_badge": "Corporate Hub", "provider": "Verified Regional Gazetteer", "provider_id": "area_hyd_gachibowli"},
        {"name": "Secunderabad Junction Railway Station", "display_name": "Secunderabad Junction Railway Station, Secunderabad, Telangana", "city": "Secunderabad", "state": "Telangana", "country": "India", "lat": 17.4334, "lon": 78.5015, "category_icon": "🚆", "category_name": "Railway Station", "area_badge": "Main Transit Junction", "provider": "Verified Regional Gazetteer", "provider_id": "area_hyd_sc_station"},
        {"name": "Charminar & Historic Old City", "display_name": "Charminar & Historic Old City, Hyderabad, Telangana", "city": "Hyderabad", "state": "Telangana", "country": "India", "lat": 17.3616, "lon": 78.4747, "category_icon": "🏰", "category_name": "Heritage & Culture", "area_badge": "Historic Center", "provider": "Verified Regional Gazetteer", "provider_id": "area_hyd_charminar"},
        {"name": "Banjara Hills / Jubilee Hills", "display_name": "Banjara Hills & Jubilee Hills Commercial Hub, Hyderabad, Telangana", "city": "Hyderabad", "state": "Telangana", "country": "India", "lat": 17.4319, "lon": 78.4073, "category_icon": "🛍️", "category_name": "Commercial & Lifestyle", "area_badge": "Metro Sector", "provider": "Verified Regional Gazetteer", "provider_id": "area_hyd_banjara"}
    ],
    "guntur": [
        {"name": "Guntur City Center (Old Club Road / Market)", "display_name": "Guntur City Center, Old Club Road, Guntur, Andhra Pradesh", "city": "Guntur", "state": "Andhra Pradesh", "country": "India", "lat": 16.3067, "lon": 80.4365, "category_icon": "🏛️", "category_name": "City Center", "area_badge": "Downtown Hub", "provider": "Verified Regional Gazetteer", "provider_id": "area_gnt_center"},
        {"name": "Guntur Junction Railway Station", "display_name": "Guntur Junction Railway Station, Station Road, Guntur, Andhra Pradesh", "city": "Guntur", "state": "Andhra Pradesh", "country": "India", "lat": 16.3045, "lon": 80.4445, "category_icon": "🚆", "category_name": "Railway Station", "area_badge": "Main Transit Hub", "provider": "Verified Regional Gazetteer", "provider_id": "area_gnt_station"},
        {"name": "Brodipet Commercial Center", "display_name": "Brodipet Commercial Center, Guntur, Andhra Pradesh", "city": "Guntur", "state": "Andhra Pradesh", "country": "India", "lat": 16.3015, "lon": 80.4420, "category_icon": "🛍️", "category_name": "Commercial", "area_badge": "Market Hub", "provider": "Verified Regional Gazetteer", "provider_id": "area_gnt_brodipet"},
        {"name": "Arundelpet Main Area", "display_name": "Arundelpet Commercial & Residential Sector, Guntur, Andhra Pradesh", "city": "Guntur", "state": "Andhra Pradesh", "country": "India", "lat": 16.3075, "lon": 80.4350, "category_icon": "📍", "category_name": "Commercial Sector", "area_badge": "Central Sector", "provider": "Verified Regional Gazetteer", "provider_id": "area_gnt_arundelpet"},
        {"name": "NTR RTC Central Bus Stand", "display_name": "NTR RTC Central Bus Stand, Guntur, Andhra Pradesh", "city": "Guntur", "state": "Andhra Pradesh", "country": "India", "lat": 16.3080, "lon": 80.4420, "category_icon": "🚌", "category_name": "Bus Terminal", "area_badge": "RTC Hub", "provider": "Verified Regional Gazetteer", "provider_id": "area_gnt_busstand"},
        {"name": "Vignan University (VFSTR Vadlamudi)", "display_name": "Vignan's Foundation for Science, Technology & Research (VFSTR), Vadlamudi, Guntur District", "city": "Vadlamudi", "state": "Andhra Pradesh", "country": "India", "lat": 16.2335, "lon": 80.5505, "category_icon": "🎓", "category_name": "University Campus", "area_badge": "VFSTR Campus", "provider": "Verified Regional Gazetteer", "provider_id": "area_gnt_vignan"},
        {"name": "AIIMS Mangalagiri", "display_name": "All India Institute of Medical Sciences (AIIMS), Mangalagiri, Guntur District", "city": "Mangalagiri", "state": "Andhra Pradesh", "country": "India", "lat": 16.4385, "lon": 80.5750, "category_icon": "🏥", "category_name": "Healthcare & Hospital", "area_badge": "AIIMS Campus", "provider": "Verified Regional Gazetteer", "provider_id": "area_gnt_aiims"}
    ],
    "tenali": [
        {"name": "Tenali Town Center", "display_name": "Tenali Town Center, Guntur District, Andhra Pradesh", "city": "Tenali", "state": "Andhra Pradesh", "country": "India", "lat": 16.2430, "lon": 80.6400, "category_icon": "🏛️", "category_name": "Town Center", "area_badge": "Municipal Hub", "provider": "Verified Regional Gazetteer", "provider_id": "area_tnl_center"},
        {"name": "Tenali Junction Railway Station", "display_name": "Tenali Junction Railway Station, Station Road, Tenali, Andhra Pradesh", "city": "Tenali", "state": "Andhra Pradesh", "country": "India", "lat": 16.2395, "lon": 80.6465, "category_icon": "🚆", "category_name": "Railway Station", "area_badge": "Main Station", "provider": "Verified Regional Gazetteer", "provider_id": "area_tnl_station"},
        {"name": "Morrispet Commercial Area", "display_name": "Morrispet Commercial Area, Tenali, Andhra Pradesh", "city": "Tenali", "state": "Andhra Pradesh", "country": "India", "lat": 16.2380, "lon": 80.6450, "category_icon": "🛍️", "category_name": "Commercial", "area_badge": "Market Hub", "provider": "Verified Regional Gazetteer", "provider_id": "area_tnl_morrispet"},
        {"name": "Chenchupet Area", "display_name": "Chenchupet Residential Sector, Tenali, Andhra Pradesh", "city": "Tenali", "state": "Andhra Pradesh", "country": "India", "lat": 16.2450, "lon": 80.6350, "category_icon": "📍", "category_name": "Residential Sector", "area_badge": "Town Sector", "provider": "Verified Regional Gazetteer", "provider_id": "area_tnl_chenchupet"},
        {"name": "Sri Asta Lakshmi Temple", "display_name": "Sri Asta Lakshmi Temple, Tenali, Guntur District, Andhra Pradesh", "city": "Tenali", "state": "Andhra Pradesh", "country": "India", "lat": 16.2385, "lon": 80.6420, "category_icon": "🛕", "category_name": "Temple & Pilgrim", "area_badge": "Cultural Landmark", "provider": "Verified Regional Gazetteer", "provider_id": "area_tnl_temple"},
        {"name": "BSR Enclave (Sarojini Naidu St)", "display_name": "BSR Enclave, Sarojini Naidu Street, Tenali, Andhra Pradesh", "city": "Tenali", "state": "Andhra Pradesh", "country": "India", "lat": 16.23454, "lon": 80.65197, "category_icon": "📍", "category_name": "Residential Enclave", "area_badge": "Enclave", "provider": "Verified Regional Gazetteer", "provider_id": "area_tnl_bsr"},
        {"name": "Angalakuduru Village", "display_name": "Angalakuduru Village, Tenali Mandal, Andhra Pradesh", "city": "Tenali Mandal", "state": "Andhra Pradesh", "country": "India", "lat": 16.2280, "lon": 80.6220, "category_icon": "🏡", "category_name": "Mandal Outskirts", "area_badge": "Rural Hub", "provider": "Verified Regional Gazetteer", "provider_id": "area_tnl_angalakuduru"}
    ],
    "vijayawada": [
        {"name": "Vijayawada City Center / Benz Circle", "display_name": "Benz Circle, Vijayawada, NTR District, Andhra Pradesh", "city": "Vijayawada", "state": "Andhra Pradesh", "country": "India", "lat": 16.5062, "lon": 80.6480, "category_icon": "🏛️", "category_name": "City Center", "area_badge": "Benz Circle Hub", "provider": "Verified Regional Gazetteer", "provider_id": "area_vja_center"},
        {"name": "Vijayawada Junction Railway Station", "display_name": "Vijayawada Junction Railway Station, Vijayawada, Andhra Pradesh", "city": "Vijayawada", "state": "Andhra Pradesh", "country": "India", "lat": 16.5180, "lon": 80.6200, "category_icon": "🚆", "category_name": "Railway Station", "area_badge": "Transit Junction", "provider": "Verified Regional Gazetteer", "provider_id": "area_vja_station"},
        {"name": "Pandit Nehru Bus Station (PNBS)", "display_name": "Pandit Nehru Bus Station (PNBS), Vijayawada, Andhra Pradesh", "city": "Vijayawada", "state": "Andhra Pradesh", "country": "India", "lat": 16.5110, "lon": 80.6280, "category_icon": "🚌", "category_name": "Bus Terminal", "area_badge": "Central RTC", "provider": "Verified Regional Gazetteer", "provider_id": "area_vja_pnbs"},
        {"name": "Vijayawada Int'l Airport (Gannavaram)", "display_name": "Vijayawada International Airport (Gannavaram), Gannavaram, Andhra Pradesh", "city": "Gannavaram", "state": "Andhra Pradesh", "country": "India", "lat": 16.5280, "lon": 80.7980, "category_icon": "✈️", "category_name": "Airport", "area_badge": "Airport Terminal", "provider": "Verified Regional Gazetteer", "provider_id": "area_vja_airport"},
        {"name": "Kanaka Durga Temple (Indrakeeladri)", "display_name": "Kanaka Durga Temple, Indrakeeladri, Vijayawada, Andhra Pradesh", "city": "Vijayawada", "state": "Andhra Pradesh", "country": "India", "lat": 16.5160, "lon": 80.6055, "category_icon": "🛕", "category_name": "Pilgrim Site", "area_badge": "Temple Shrine", "provider": "Verified Regional Gazetteer", "provider_id": "area_vja_temple"},
        {"name": "Prakasam Barrage", "display_name": "Prakasam Barrage, Krishna River, Vijayawada, Andhra Pradesh", "city": "Vijayawada", "state": "Andhra Pradesh", "country": "India", "lat": 16.5075, "lon": 80.6080, "category_icon": "🌊", "category_name": "River Landmark", "area_badge": "Krishna River", "provider": "Verified Regional Gazetteer", "provider_id": "area_vja_barrage"}
    ],
    "bangalore": [
        {"name": "MG Road / Vidhana Soudha (City Center)", "display_name": "MG Road / Vidhana Soudha, Bengaluru, Karnataka", "city": "Bengaluru", "state": "Karnataka", "country": "India", "lat": 12.9716, "lon": 77.5946, "category_icon": "🏛️", "category_name": "City Center", "area_badge": "Central District", "provider": "Verified Regional Gazetteer", "provider_id": "area_blr_center"},
        {"name": "Kempegowda Int'l Airport (BLR)", "display_name": "Kempegowda International Airport (BLR), Devanahalli, Bengaluru, Karnataka", "city": "Devanahalli", "state": "Karnataka", "country": "India", "lat": 13.1986, "lon": 77.7066, "category_icon": "✈️", "category_name": "Airport", "area_badge": "Airport Terminal", "provider": "Verified Regional Gazetteer", "provider_id": "area_blr_airport"},
        {"name": "Whitefield IT Corridor", "display_name": "Whitefield IT Corridor & Tech Parks, Bengaluru, Karnataka", "city": "Bengaluru", "state": "Karnataka", "country": "India", "lat": 12.9698, "lon": 77.7500, "category_icon": "💻", "category_name": "Tech Corridor", "area_badge": "IT Park Hub", "provider": "Verified Regional Gazetteer", "provider_id": "area_blr_whitefield"},
        {"name": "Electronic City Hub", "display_name": "Electronic City Phase 1 & 2, Bengaluru, Karnataka", "city": "Bengaluru", "state": "Karnataka", "country": "India", "lat": 12.8452, "lon": 77.6602, "category_icon": "💻", "category_name": "Tech Corridor", "area_badge": "Electronic City", "provider": "Verified Regional Gazetteer", "provider_id": "area_blr_ecity"},
        {"name": "KSR Bengaluru Railway Station (Majestic)", "display_name": "KSR Bengaluru City Railway Station (Majestic), Bengaluru, Karnataka", "city": "Bengaluru", "state": "Karnataka", "country": "India", "lat": 12.9774, "lon": 77.5713, "category_icon": "🚆", "category_name": "Railway Station", "area_badge": "Majestic Hub", "provider": "Verified Regional Gazetteer", "provider_id": "area_blr_station"}
    ],
    "amaravati": [
        {"name": "Amaravati Capital City (Secretariat)", "display_name": "AP State Secretariat, Velagapudi, Amaravati, Guntur District, Andhra Pradesh", "city": "Velagapudi", "state": "Andhra Pradesh", "country": "India", "lat": 16.5417, "lon": 80.5150, "category_icon": "🏛️", "category_name": "Capital City", "area_badge": "Secretariat Hub", "provider": "Verified Regional Gazetteer", "provider_id": "area_amr_secretariat"},
        {"name": "Amaravati High Court", "display_name": "Andhra Pradesh High Court, Nelapadu, Amaravati, Andhra Pradesh", "city": "Nelapadu", "state": "Andhra Pradesh", "country": "India", "lat": 16.5135, "lon": 80.4985, "category_icon": "⚖️", "category_name": "Judicial Complex", "area_badge": "High Court", "provider": "Verified Regional Gazetteer", "provider_id": "area_amr_highcourt"},
        {"name": "Amaravati Heritage Town & Mahastupa", "display_name": "Amaravati Buddhist Stupa & Dhyana Buddha, Amaravati Town, Andhra Pradesh", "city": "Amaravati", "state": "Andhra Pradesh", "country": "India", "lat": 16.5746, "lon": 80.3572, "category_icon": "🛕", "category_name": "Heritage Monument", "area_badge": "Buddhist Stupa", "provider": "Verified Regional Gazetteer", "provider_id": "area_amr_stupa"},
        {"name": "SRM University AP (Amaravati)", "display_name": "SRM University AP, Neerukonda, Amaravati, Andhra Pradesh", "city": "Neerukonda", "state": "Andhra Pradesh", "country": "India", "lat": 16.4678, "lon": 80.5054, "category_icon": "🎓", "category_name": "University Campus", "area_badge": "SRM Campus", "provider": "Verified Regional Gazetteer", "provider_id": "area_amr_srm"},
        {"name": "VIT-AP University", "display_name": "VIT-AP University, Inavolu, Beside AP Secretariat, Amaravati, Andhra Pradesh", "city": "Inavolu", "state": "Andhra Pradesh", "country": "India", "lat": 16.4975, "lon": 80.4990, "category_icon": "🎓", "category_name": "University Campus", "area_badge": "VIT Campus", "provider": "Verified Regional Gazetteer", "provider_id": "area_amr_vit"}
    ]
}
CITY_AREAS_DIRECTORY["bengaluru"] = CITY_AREAS_DIRECTORY["bangalore"]
CITY_AREAS_DIRECTORY["amaravathi"] = CITY_AREAS_DIRECTORY["amaravati"]


class MapService:
    def __init__(
        self,
        user_agent: str = "PATHFINDER-Global-Nav/2.0 (predictive.adaptive.transit@navigation.org)",
        base_url: Optional[str] = None,
        timeout_sec: float = 2.5
    ):
        self.user_agent = user_agent
        self.base_url = (base_url or os.environ.get("NOMINATIM_BASE_URL", "https://nominatim.openstreetmap.org")).rstrip("/")
        self.timeout_sec = timeout_sec
        self.cache: Dict[str, Dict[str, Any]] = dict(OFFLINE_GEOCODE_CACHE)
        self._query_candidates_cache: Dict[str, List[Dict[str, Any]]] = {}
        try:
            from src.google_maps_platform import load_and_georeference_saved_locations
            for loc in load_and_georeference_saved_locations():
                name_k = loc["name"].lower().strip()
                self.cache[name_k] = {
                    "lat": loc["latitude"],
                    "lon": loc["longitude"],
                    "name": loc["name"],
                    "display_name": f"{loc['name']}, {loc.get('section', 'Campus')}, Vignan University",
                    "country": "India",
                    "state": "Andhra Pradesh"
                }
        except Exception:
            pass

        # Ingest all regional emergency and civic facilities into geocoder
        try:
            from src.facilities_service import CATEGORY_CONFIG
            for cat_id, cat_info in CATEGORY_CONFIG.items():
                for fac in cat_info.get("facilities", []):
                    fac_k = fac["name"].lower().strip()
                    self.cache[fac_k] = {
                        "lat": fac["lat"],
                        "lon": fac["lon"],
                        "name": fac["name"],
                        "display_name": f"{fac['name']} ({cat_info.get('label', 'Facility')}), {fac.get('address', 'Regional Sector')}",
                        "country": "India",
                        "state": "Andhra Pradesh",
                        "type": cat_id.lower()
                    }
        except Exception:
            pass

        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self._last_request_time = 0.0
        self._min_request_interval = 0.20

    def _respect_rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    def geocode(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Geocodes any global address, city, country, landmark, postal code,
        or GPS coordinate pair to (latitude, longitude, display_name).

        Resolution pipeline:
        1. Direct Coordinate Detection with strict WGS84 range validation (-90 to +90, -180 to +180)
        2. Exact Offline Local Alias Match (Vignan, Guntur, Tenali local wards/landmarks)
        3. Global Provider Search (OpenStreetMap Nominatim worldwide query)
        4. Curated Fuzzy Token Match for regional campus/corridor aliases
        5. Return None if unresolved — NEVER silently substitute an incorrect regional anchor
        """
        candidates = self.geocode_candidates(query, limit=1)
        return candidates[0] if candidates else None

    def geocode_candidates(
        self,
        query: str,
        limit: int = 5,
        origin_coords: Optional[Tuple[float, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Disambiguates queries by returning candidate worldwide matches with
        country, region/state, locality/city, coordinates, campus-internal metadata, and relevance score.

        Resolution Pipeline:
        1. Direct Coordinate Detection with strict WGS-84 range validation (-90 to +90, -180 to +180).
        2. Verified Local Gazetteer & Curated POIs with token-overlap matching and internal campus boundary flags.
        3. Configured Google Maps Geocoding API (when GOOGLE_MAPS_API_KEY is active).
        4. Worldwide Geocoding Provider (OpenStreetMap Nominatim with respectful rate-limiting).
        5. High-Precision Small-Place Geocoder (Photon by Komoot with dynamic, non-coercive biasing).
        6. Locality-Aware Cross-Provider Candidate Ranking & Spatial Deduplication.
        """
        q_raw = query.strip()
        if not q_raw:
            return []

        # ---------------------------------------------------------
        # TIER 1: Direct Coordinate Detection & Strict Range Validation
        # ---------------------------------------------------------
        coord_pattern = r"^\s*\(?\s*([+-]?\d{1,2}(?:\.\d+)?)\s*[,\s]\s*([+-]?\d{1,3}(?:\.\d+)?)\s*\)?\s*$"
        coord_match = re.match(coord_pattern, q_raw)
        if coord_match:
            try:
                c_lat = float(coord_match.group(1))
                c_lon = float(coord_match.group(2))
                # Validate physical latitude (-90 to 90) and longitude (-180 to 180)
                if -90.0 <= c_lat <= 90.0 and -180.0 <= c_lon <= 180.0:
                    return [{
                        "lat": c_lat,
                        "lon": c_lon,
                        "name": f"Pinpoint ({c_lat:.4f}, {c_lon:.4f})",
                        "display_name": f"Pinpoint Coordinate ({c_lat:.5f}, {c_lon:.5f})",
                        "address": f"Pinpoint Coordinate ({c_lat:.5f}, {c_lon:.5f})",
                        "country": "Global Coordinates",
                        "state": "",
                        "city": "",
                        "type": "coordinate",
                        "importance": 1.0,
                        "relevance_score": 1.0,
                        "provider": "Direct Coordinates",
                        "provider_id": f"coord_{c_lat:.4f}_{c_lon:.4f}",
                        "source": "COORDINATE_INPUT",
                        "is_campus_internal": False
                    }]
                else:
                    # Out of bounds coordinates: do not fabricate or search text
                    return []
            except Exception:
                return []

        # Clean query normalization & common transliteration standardization
        q_clean = re.sub(r"\s+", " ", q_raw).strip()
        q_norm = q_clean.lower()
        q_norm_std = q_norm.replace("astalakshmi", "asta lakshmi").replace("ashtalakshmi", "asta lakshmi").replace("ashta lakshmi", "asta lakshmi")

        # Instant Query Cache Check
        if q_norm in self._query_candidates_cache:
            return self._query_candidates_cache[q_norm][:limit]
        if q_norm_std in self._query_candidates_cache:
            return self._query_candidates_cache[q_norm_std][:limit]

        # Handle 'current location' keyword
        if "current" in q_norm or "my location" in q_norm or "live location" in q_norm:
            c_lat = origin_coords[0] if origin_coords else 17.3850
            c_lon = origin_coords[1] if origin_coords else 78.4867
            cur_loc_res = [{
                "lat": c_lat,
                "lon": c_lon,
                "display_name": "📍 Current Location",
                "country": "India",
                "state": "",
                "city": "Current Location",
                "type": "current_location",
                "importance": 1.0,
                "relevance_score": 1.0,
                "source": "CURRENT_LOCATION",
                "is_campus_internal": False
            }]
            return cur_loc_res

        # ---------------------------------------------------------
        # TIER 1.5: Airport IATA & Global Airway Hub Detection
        # ---------------------------------------------------------
        q_clean_up = q_clean.upper()
        try:
            from src.backend.routing.flight_provider import AIRPORT_DATABASE
            matched_airports = []
            for apt in AIRPORT_DATABASE:
                has_airport_kw = any(w in q_norm for w in ["airport", "aerodrome", "terminal", "intl", "airway"])
                is_exact_code = (q_clean_up == apt["iata"] or q_clean_up == apt["icao"])
                is_airport_name_query = has_airport_kw and (
                    apt["name"].lower() in q_norm or
                    q_norm.startswith(apt["name"].lower()) or
                    apt["name"].lower().startswith(q_norm) or
                    f"{apt['city'].lower()} airport" in q_norm or 
                    f"{apt['city'].lower()} intl" in q_norm
                )
                if is_exact_code or is_airport_name_query:
                    matched_airports.append({
                        "lat": apt["lat"],
                        "lon": apt["lon"],
                        "name": f"✈️ {apt['name']} ({apt['iata']})",
                        "display_name": f"✈️ {apt['name']} ({apt['iata']}), {apt['city']}, {apt['country']}",
                        "address": f"{apt['name']}, {apt['city']}, {apt['country']}",
                        "country": apt["country"],
                        "state": apt["city"],
                        "city": apt["city"],
                        "type": "airport",
                        "importance": 1.0,
                        "relevance_score": 1.0,
                        "provider": "Global Aviation Database",
                        "provider_id": f"airport_{apt['iata']}",
                        "source": "AIRPORT_REGISTRY",
                        "is_campus_internal": False
                    })
            if matched_airports:
                return matched_airports[:limit]
        except Exception:
            pass

        q_tokens = set(re.findall(r"\b[a-zA-Z0-9]{2,}\b", q_norm_std))
        # Known regional and major global localities for locality-consistency ranking
        LOCALITY_KEYWORDS = {
            "tenali", "guntur", "vadlamudi", "vijayawada", "amaravati", "khammam",
            "hyderabad", "bangalore", "bengaluru", "chennai", "mumbai", "delhi",
            "kolkata", "bapatla", "chirala", "ponnur", "repalle", "narasaraopet",
            "sattenapalle", "pedakakani", "namburu", "chebrolu", "cambridge", "london", "tokyo", "paris"
        }
        query_explicit_locs = q_tokens.intersection(LOCALITY_KEYWORDS)

        collected_candidates: List[Dict[str, Any]] = []

        # ---------------------------------------------------------
        # TIER 2: Verified Local Gazetteer & Campus POI Directory
        # ---------------------------------------------------------
        gazetteer_matches = []
        for k, v in self.cache.items():
            k_clean = k.lower().strip()
            name_clean = v.get("name", "").lower().strip()
            disp_clean = v.get("display_name", "").lower().strip()

            target_tokens = set(re.findall(r"\b[a-zA-Z0-9]{2,}\b", f"{k_clean} {name_clean} {disp_clean}"))
            token_overlap = len(q_tokens.intersection(target_tokens))

            # Generic stopwords that should not trigger false gazetteer matches on their own
            GENERIC_STOPWORDS = {
                "town", "city", "center", "centre", "andhra", "pradesh", "district", "india",
                "near", "junction", "road", "street", "main", "gate", "station", "building",
                "telangana", "state", "point", "location", "place", "hub"
            }
            distinctive_q_tokens = {t for t in q_tokens if t not in GENERIC_STOPWORDS and len(t) >= 3}
            distinctive_overlap = len(distinctive_q_tokens.intersection(target_tokens))

            # Match criteria: exact key, exact name, startswith, or distinctive token overlap
            is_exact = (k_clean == q_norm or k_clean == q_norm_std or name_clean == q_norm or name_clean == q_norm_std)
            is_substring = (len(q_norm_std) >= 3 and (k_clean.startswith(q_norm_std) or q_norm_std in k_clean or q_norm_std in name_clean))

            has_valid_overlap = False
            if distinctive_q_tokens:
                has_valid_overlap = (distinctive_overlap >= 1 and token_overlap >= 2)
            else:
                has_valid_overlap = (token_overlap >= max(1, min(len(q_tokens), 2)))

            if is_exact or is_substring or has_valid_overlap:
                # Calculate match score (verified gazetteer has highest confidence)
                match_score = 1.60 if is_exact else (1.30 if is_substring else 0.85)
                match_score += 0.08 * token_overlap

                # Locality alignment check
                if query_explicit_locs:
                    if query_explicit_locs.intersection(target_tokens):
                        match_score += 0.25
                    else:
                        match_score -= 0.30

                c_item = {
                    "lat": float(v["lat"]),
                    "lon": float(v["lon"]),
                    "name": v.get("name", k.title()),
                    "display_name": v.get("display_name", v.get("name", k.title())),
                    "address": v.get("display_name", v.get("name", k.title())),
                    "country": v.get("country", "India"),
                    "state": v.get("state", "Andhra Pradesh"),
                    "city": v.get("city", ""),
                    "type": v.get("type", "verified_poi"),
                    "importance": match_score,
                    "relevance_score": match_score,
                    "provider": "Verified Local Gazetteer",
                    "provider_id": f"gazetteer_{k_clean}",
                    "source": "VERIFIED_GAZETTEER",
                    "is_campus_internal": bool(v.get("is_campus_internal", False)),
                    "campus_entrance": v.get("campus_entrance", ""),
                    "limitation_note": v.get("limitation_note", "")
                }
                gazetteer_matches.append((match_score, c_item))

        gazetteer_matches.sort(key=lambda x: x[0], reverse=True)

        # High-confidence local gazetteer or campus internal short-circuit:
        # If there is an exact or very high-confidence gazetteer match (e.g. Tenali, Guntur, Vignan, Bapatla, CSE block),
        # return immediately without waiting for slow external network APIs!
        is_high_conf_gazetteer = gazetteer_matches and (gazetteer_matches[0][0] >= 1.50 or gazetteer_matches[0][1].get("is_campus_internal", False))
        if is_high_conf_gazetteer:
            final_res = [m[1] for m in gazetteer_matches[:limit]]
            self._query_candidates_cache[q_norm] = final_res
            self._query_candidates_cache[q_norm_std] = final_res
            return final_res

        for _, g_cand in gazetteer_matches[:limit]:
            collected_candidates.append(g_cand)

        # ---------------------------------------------------------
        # TIER 2.5: Official Google Maps Geocoding API (when key is active)
        # ---------------------------------------------------------
        try:
            from src.google_maps_platform import geocode_with_google_api, is_google_maps_key_configured
            if is_google_maps_key_configured():
                g_res = geocode_with_google_api(q_clean)
                if g_res:
                    collected_candidates.append({
                        "lat": float(g_res["lat"]),
                        "lon": float(g_res["lon"]),
                        "name": g_res.get("formatted_address", q_clean).split(",")[0].strip(),
                        "display_name": g_res.get("formatted_address", q_clean),
                        "country": "",
                        "state": "",
                        "city": "",
                        "address": g_res.get("formatted_address", q_clean),
                        "type": "google_geocoded",
                        "importance": 0.95,
                        "relevance_score": 0.95,
                        "provider": "Google Maps Platform",
                        "provider_id": f"google_{g_res['lat']:.4f}_{g_res['lon']:.4f}",
                        "source": "GOOGLE_MAPS_PLATFORM",
                        "is_campus_internal": False
                    })
        except Exception:
            pass

        # ---------------------------------------------------------
        # TIER 3 & 3.5: Fast Parallel Worldwide Geocoding (Nominatim + Photon)
        # ---------------------------------------------------------
        def _fetch_nominatim() -> List[Dict[str, Any]]:
            nom_results = []
            try:
                self._respect_rate_limit()
                url = f"{self.base_url}/search"
                params = {
                    "q": q_clean,
                    "format": "jsonv2",
                    "limit": limit,
                    "addressdetails": 1
                }
                headers = {"User-Agent": self.user_agent}
                resp = self.session.get(url, params=params, headers=headers, timeout=1.2)
                if resp.status_code == 200:
                    for item in resp.json():
                        addr = item.get("address", {})
                        country = addr.get("country", "")
                        state = addr.get("state", addr.get("region", addr.get("province", "")))
                        city = addr.get("city", addr.get("town", addr.get("village", addr.get("county", addr.get("municipality", "")))))
                        c_lat = float(item["lat"])
                        c_lon = float(item["lon"])

                        osm_id_str = str(item.get("osm_id") or item.get("place_id") or "")
                        osm_type_str = str(item.get("osm_type") or "place")
                        prov_id = f"osm_{osm_type_str}_{osm_id_str}" if osm_id_str else f"osm_{c_lat:.4f}_{c_lon:.4f}"

                        raw_name = item.get("name")
                        disp_name = item.get("display_name", q_clean)
                        if not raw_name:
                            raw_name = disp_name.split(",")[0].strip() if disp_name else q_clean

                        text_for_eval = (disp_name + " " + city + " " + state + " " + country).lower()
                        eval_tokens = set(re.findall(r"\b[a-zA-Z0-9]{2,}\b", text_for_eval))
                        tok_overlap = len(q_tokens.intersection(eval_tokens))

                        rel_score = float(item.get("importance", 0.5)) + 0.1 * tok_overlap
                        if query_explicit_locs:
                            if query_explicit_locs.intersection(eval_tokens):
                                rel_score += 0.35
                            else:
                                other_locs = eval_tokens.intersection(LOCALITY_KEYWORDS)
                                if other_locs and not (query_explicit_locs.intersection(other_locs)):
                                    rel_score -= 0.60

                        if origin_coords:
                            dist_deg = ((c_lat - origin_coords[0])**2 + (c_lon - origin_coords[1])**2)**0.5
                            if dist_deg < 0.5:
                                rel_score += 0.20
                            elif dist_deg < 2.5:
                                rel_score += 0.10

                        nom_results.append({
                            "lat": c_lat,
                            "lon": c_lon,
                            "name": raw_name,
                            "display_name": disp_name,
                            "country": country,
                            "state": state,
                            "city": city,
                            "address": disp_name,
                            "type": item.get("type", item.get("category", "place")),
                            "importance": float(item.get("importance", 0.5)),
                            "relevance_score": rel_score,
                            "provider": "OpenStreetMap Nominatim",
                            "provider_id": prov_id,
                            "osm_id": osm_id_str,
                            "osm_type": osm_type_str,
                            "source": "GLOBAL_OSM_NOMINATIM",
                            "is_campus_internal": False
                        })
            except Exception:
                pass
            return nom_results

        def _fetch_photon() -> List[Dict[str, Any]]:
            pho_results = []
            try:
                photon_url = "https://photon.komoot.io/api/"
                photon_params: Dict[str, Any] = {
                    "q": q_clean,
                    "limit": limit,
                    "lang": "en"
                }
                if origin_coords:
                    photon_params["lat"] = origin_coords[0]
                    photon_params["lon"] = origin_coords[1]

                headers = {"User-Agent": self.user_agent}
                p_resp = self.session.get(photon_url, params=photon_params, headers=headers, timeout=1.2)
                if p_resp.status_code == 200:
                    p_data = p_resp.json()
                    features = p_data.get("features", [])
                    for f in features:
                        geom = f.get("geometry", {})
                        props = f.get("properties", {})
                        coords = geom.get("coordinates", [])
                        if len(coords) >= 2:
                            p_lon = float(coords[0])
                            p_lat = float(coords[1])
                            p_name = props.get("name") or q_clean
                            parts = [p_name]
                            if props.get("street"):
                                parts.append(props["street"])
                            c_city = props.get("city") or props.get("town") or props.get("village") or props.get("county", "")
                            if c_city and c_city not in parts:
                                parts.append(c_city)
                            c_state = props.get("state") or props.get("region", "")
                            if c_state and c_state not in parts:
                                parts.append(c_state)
                            c_country = props.get("country", "")
                            if c_country and c_country not in parts:
                                parts.append(c_country)
                            disp = ", ".join([p for p in parts if p])

                            osm_id_str = str(props.get("osm_id") or "")
                            osm_type_str = str(props.get("osm_type") or "place")
                            prov_id = f"photon_{osm_type_str}_{osm_id_str}" if osm_id_str else f"photon_{p_lat:.4f}_{p_lon:.4f}"

                            text_eval = disp.lower()
                            eval_tokens = set(re.findall(r"\b[a-zA-Z0-9]{2,}\b", text_eval))
                            tok_overlap = len(q_tokens.intersection(eval_tokens))

                            rel_score = 0.65 + 0.1 * tok_overlap
                            if query_explicit_locs:
                                if query_explicit_locs.intersection(eval_tokens):
                                    rel_score += 0.35
                                else:
                                    other_locs = eval_tokens.intersection(LOCALITY_KEYWORDS)
                                    if other_locs and not (query_explicit_locs.intersection(other_locs)):
                                        rel_score -= 0.60

                            if origin_coords:
                                dist_deg = ((p_lat - origin_coords[0])**2 + (p_lon - origin_coords[1])**2)**0.5
                                if dist_deg < 0.5:
                                    rel_score += 0.20
                                elif dist_deg < 2.5:
                                    rel_score += 0.10

                            pho_results.append({
                                "lat": p_lat,
                                "lon": p_lon,
                                "name": p_name,
                                "display_name": disp,
                                "country": c_country,
                                "state": c_state,
                                "city": c_city,
                                "address": disp,
                                "type": props.get("osm_value", props.get("type", "poi")),
                                "importance": 0.75,
                                "relevance_score": rel_score,
                                "provider": "Photon (Komoot/OSM)",
                                "provider_id": prov_id,
                                "osm_id": osm_id_str,
                                "osm_type": osm_type_str,
                                "source": "PHOTON_KOMOOT_OSM",
                                "is_campus_internal": False
                            })
            except Exception:
                pass
            return pho_results

        # Execute network geocoders in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            fut_nom = executor.submit(_fetch_nominatim)
            fut_pho = executor.submit(_fetch_photon)
            try:
                nom_cands = fut_nom.result(timeout=2.4)
                collected_candidates.extend(nom_cands)
            except Exception:
                pass
            try:
                pho_cands = fut_pho.result(timeout=2.4)
                collected_candidates.extend(pho_cands)
            except Exception:
                pass

        if not collected_candidates:
            return []

        # ---------------------------------------------------------
        # TIER 4: Geographic Diversification & Deduplication
        # ---------------------------------------------------------
        # Sort by relevance score descending
        collected_candidates.sort(key=lambda c: c.get("relevance_score", 0.0), reverse=True)

        # Pass 1: Eliminate micro-spatial duplicates (< 500m)
        spatially_distinct: List[Dict[str, Any]] = []
        for cand in collected_candidates:
            is_micro_dup = False
            for accepted in spatially_distinct:
                d_lat = abs(cand["lat"] - accepted["lat"])
                d_lon = abs(cand["lon"] - accepted["lon"])
                if d_lat < 0.005 and d_lon < 0.005:  # ~500 meters
                    is_micro_dup = True
                    if not accepted.get("state") and cand.get("state"):
                        accepted["state"] = cand["state"]
                    if not accepted.get("country") and cand.get("country"):
                        accepted["country"] = cand["country"]
                    if not accepted.get("city") and cand.get("city"):
                        accepted["city"] = cand["city"]
                    break
            if not is_micro_dup:
                spatially_distinct.append(cand)

        # Pass 2: Geographic & Administrative Region Diversification
        # Ensure distinct countries and states/provinces are prioritized so ambiguous queries
        # (e.g. Hyderabad, India vs. Hyderabad, Pakistan) are both surfaced prominently.
        region_buckets: Dict[str, List[Dict[str, Any]]] = {}
        for cand in spatially_distinct:
            country = (cand.get("country") or "").strip().lower()
            state = (cand.get("state") or "").strip().lower()
            region_key = f"{country}_{state}" if state else country
            if not region_key:
                region_key = f"{cand['lat']:.1f}_{cand['lon']:.1f}"
            region_buckets.setdefault(region_key, []).append(cand)

        final_candidates: List[Dict[str, Any]] = []
        # Round-robin pick from each geographically distinct region first
        bucket_keys = list(region_buckets.keys())
        max_depth = max(len(items) for items in region_buckets.values()) if region_buckets else 0
        for depth in range(max_depth):
            for rk in bucket_keys:
                if depth < len(region_buckets[rk]):
                    cand = region_buckets[rk][depth]
                    if cand not in final_candidates:
                        final_candidates.append(cand)
                    if len(final_candidates) >= limit:
                        break
            if len(final_candidates) >= limit:
                break

        # Final pass: Ensure every candidate has consistent fields & unique stable ID
        for idx, cand in enumerate(final_candidates):
            c_name = cand.get("name") or cand.get("display_name", "").split(",")[0].strip()
            c_name_primary = c_name.split(",")[0].strip()
            c_city = cand.get("city") or ""
            c_state = cand.get("state") or ""
            c_country = cand.get("country") or ""
            
            parts = [c_name_primary]
            if c_city and c_city.lower() != c_name_primary.lower() and c_city.lower() not in [p.lower() for p in parts]:
                parts.append(c_city)
            if c_state and c_state.lower() not in [p.lower() for p in parts]:
                parts.append(c_state)
            if c_country and c_country.lower() not in [p.lower() for p in parts]:
                parts.append(c_country)
            
            cand["clean_label"] = ", ".join(parts)
            if not cand.get("provider_id"):
                cand["provider_id"] = f"cand_{cand['lat']:.4f}_{cand['lon']:.4f}_{idx}"

        # Populate memory cache for future lookups
        if final_candidates:
            self.cache[q_norm] = final_candidates[0]
            self._query_candidates_cache[q_norm] = final_candidates
            self._query_candidates_cache[q_norm_std] = final_candidates

        return final_candidates

    def get_disambiguation_candidates(
        self,
        query: str,
        limit: int = 8,
        origin_coords: Optional[Tuple[float, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Returns rich multi-area disambiguation candidates for any query.
        If a recognized metropolitan hub or city is queried, provides prominent
        neighborhoods, airports, IT corridors, transit stations, and city center areas.
        Also preserves international and statewide candidates returned by geocode_candidates.
        """
        q_raw = (query or "").strip()
        if not q_raw:
            return []

        q_norm = q_raw.lower()
        base_cands = self.geocode_candidates(q_raw, limit=max(limit, 5), origin_coords=origin_coords)

        # Check for matching city in directory
        matched_city_key = None
        for k in CITY_AREAS_DIRECTORY.keys():
            if k == q_norm or k in q_norm.split() or q_norm.startswith(k):
                matched_city_key = k
                break

        res: List[Dict[str, Any]] = []
        if matched_city_key:
            for item in CITY_AREAS_DIRECTORY[matched_city_key]:
                cand_copy = dict(item)
                cand_copy.setdefault("source", "CITY_AREAS_DIRECTORY")
                cand_copy.setdefault("importance", 1.5)
                cand_copy.setdefault("relevance_score", 1.5)
                cand_copy.setdefault("is_campus_internal", False)
                res.append(cand_copy)

            # Preserve any international or cross-state matches from base_cands (e.g. Hyderabad, Sindh, Pakistan)
            for bc in base_cands:
                is_unique_region = True
                for r_item in res:
                    if abs(bc["lat"] - r_item["lat"]) < 0.05 and abs(bc["lon"] - r_item["lon"]) < 0.05:
                        is_unique_region = False
                        break
                if is_unique_region:
                    res.append(bc)
        else:
            res = list(base_cands)

        # Ensure all candidates have rich display metadata & category badges
        for idx, c in enumerate(res):
            c_name = c.get("name") or c.get("display_name", "").split(",")[0].strip()
            c.setdefault("name", c_name)
            if not c.get("category_icon"):
                t_low = (str(c.get("type", "")) + " " + c_name.lower() + " " + str(c.get("display_name", "")).lower())
                if any(w in t_low for w in ["airport", "aerodrome", "terminal"]):
                    c["category_icon"] = "✈️"
                    c["category_name"] = "Airport"
                    c["area_badge"] = "Aviation Hub"
                elif any(w in t_low for w in ["railway", "station", "train", "junction"]):
                    c["category_icon"] = "🚆"
                    c["category_name"] = "Railway Station"
                    c["area_badge"] = "Transit Hub"
                elif any(w in t_low for w in ["bus", "pnbs", "rtc"]):
                    c["category_icon"] = "🚌"
                    c["category_name"] = "Bus Terminal"
                    c["area_badge"] = "Bus Hub"
                elif any(w in t_low for w in ["temple", "church", "mosque", "worship", "devasthanam"]):
                    c["category_icon"] = "🛕"
                    c["category_name"] = "Place of Worship"
                    c["area_badge"] = "Landmark"
                elif any(w in t_low for w in ["hospital", "medical", "clinic", "health"]):
                    c["category_icon"] = "🏥"
                    c["category_name"] = "Healthcare"
                    c["area_badge"] = "Medical"
                elif any(w in t_low for w in ["university", "college", "school", "campus"]):
                    c["category_icon"] = "🎓"
                    c["category_name"] = "University"
                    c["area_badge"] = "Academic"
                elif any(w in t_low for w in ["mall", "market", "commercial", "shopping"]):
                    c["category_icon"] = "🛍️"
                    c["category_name"] = "Commercial"
                    c["area_badge"] = "Market"
                elif any(w in t_low for w in ["city", "town", "center"]):
                    c["category_icon"] = "🏛️"
                    c["category_name"] = "City Center"
                    c["area_badge"] = "Downtown"
                elif any(w in t_low for w in ["village", "rural"]):
                    c["category_icon"] = "🏡"
                    c["category_name"] = "Village"
                    c["area_badge"] = "Mandal"
                else:
                    c["category_icon"] = "📍"
                    c["category_name"] = "Area / Landmark"
                    c["area_badge"] = c.get("city") or c.get("state") or "Locality"

            if not c.get("provider_id"):
                c["provider_id"] = f"area_{c['lat']:.4f}_{c['lon']:.4f}_{idx}"

            # Calculate distance if origin_coords is available
            if origin_coords:
                import math
                lat1, lon1 = math.radians(origin_coords[0]), math.radians(origin_coords[1])
                lat2, lon2 = math.radians(c["lat"]), math.radians(c["lon"])
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
                dist_km = 6371.0 * 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
                c["distance_km"] = round(dist_km, 1)

        return res[:limit]

    def reverse_geocode(self, lat: float, lon: float) -> str:
        """Translates lat/lon into human-readable landmark or address worldwide."""
        # Check proximity to known cached landmarks (< 350 meters) - find closest
        best_match = None
        min_dist_sq = 0.0035 ** 2
        for k, v in self.cache.items():
            dist_sq = (v["lat"] - lat) ** 2 + (v["lon"] - lon) ** 2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                best_match = v.get("display_name", v.get("name", "Known Landmark"))
        if best_match:
            return best_match

        try:
            self._respect_rate_limit()
            url = f"{self.base_url}/reverse"
            params = {
                "lat": lat,
                "lon": lon,
                "format": "jsonv2",
                "addressdetails": 1
            }
            resp = self.session.get(url, params=params, timeout=self.timeout_sec)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("display_name", f"{lat:.4f}, {lon:.4f}")
        except Exception:
            pass

        return f"Geographic Point ({lat:.4f}° N, {lon:.4f}° E)"

    def create_interactive_map(
        self,
        center_lat: float,
        center_lon: float,
        zoom: int = 14,
        origin_coords: Optional[Tuple[float, float]] = None,
        destination_coords: Optional[Tuple[float, float]] = None,
        routes: Optional[List[Dict[str, Any]]] = None,
        hazards: Optional[List[Dict[str, Any]]] = None,
        road_closures: Optional[List[Dict[str, Any]]] = None,
        breadcrumb_trail: Optional[List[Tuple[float, float]]] = None,
        map_style: str = "satellite_hybrid",
        auto_fit_bounds: bool = False,
        traveler_avatar: str = "boy",
        emergency_facilities: Optional[List[Dict[str, Any]]] = None,
        is_custom_origin: bool = False,
        fleet_members: Optional[List[Dict[str, Any]]] = None
    ) -> folium.Map:
        """
        Creates a rich, multi-layered interactive Folium Leaflet Map with:
        - Photorealistic Satellite imagery (Google Satellite Hybrid & Esri World Imagery)
        - Origin marker (Blue pulse)
        - Destination marker (Green shield)
        - Multi-route polylines (Primary green, Alternatives dashed/purple, Hazardous red)
        - Active hazard zones (Amber/Red transparent circular buffer zones)
        - Road closure barricade markers
        - Real-time GPS Tracker & Live Location Lock
        """
        # Create base Folium Map without default single tile layer so selectable layers can be layered cleanly
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom,
            tiles=None,
            control_scale=True,
            attribution_control=False,
            zoom_control=True,
            scrollWheelZoom=False
        )

        # Real Google Maps Roadmap, Satellite Hybrid, Terrain, and Live Traffic
        # Official Google Maps tile streams matching Google Maps @16.2463744,80.6617088,14z
        is_satellite = str(map_style).lower() in ("satellite_hybrid", "satellite", "google_satellite", "tactical_satellite")
        is_terrain = "terrain" in str(map_style).lower()

        # 1. Google Maps Roadmap (Clean, high-contrast city & highway view)
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
            attr="Google Maps",
            name="🗺️ Google Maps Roadmap",
            overlay=False,
            control=True,
            show=(not is_satellite and not is_terrain)
        ).add_to(m)

        # 2. Google Satellite Hybrid (High-resolution aerial satellite with road overlays & place labels)
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
            attr="Google Satellite",
            name="🛰️ Google Satellite Hybrid",
            overlay=False,
            control=True,
            show=is_satellite
        ).add_to(m)

        # 3. Google Terrain (Physical contours, elevation and regional topography)
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
            attr="Google Terrain",
            name="🏔️ Google Terrain",
            overlay=False,
            control=True,
            show=is_terrain
        ).add_to(m)

        # 4. Live Real-Time Traffic Congestion Layer (Official Google traffic stream: Green/Orange/Red)
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=h,traffic&x={x}&y={y}&z={z}",
            attr="Google Traffic",
            name="🚦 Live Traffic Congestion",
            overlay=True,
            control=True,
            show=True
        ).add_to(m)

        # Interactive Google Maps Layer Switcher
        folium.LayerControl(position="topright", collapsed=True).add_to(m)

        # High-Accuracy Real-Time GPS Tracking Plugin (Google Maps style)
        try:
            import folium.plugins as plugins
            plugins.LocateControl(
                auto_start=True,
                flyTo=True,
                keepCurrentZoomLevel=True,
                drawCircle=True,
                drawMarker=True,
                showPopup=True,
                strings={
                    "title": "🎯 Locate Me on Satellite View",
                    "popup": "📍 Live Satellite GPS Position (Accurate within {distance} {unit})"
                },
                locateOptions={
                    "enableHighAccuracy": True,
                    "watch": True,
                    "maxZoom": 18
                }
            ).add_to(m)
        except Exception:
            pass

        # Real-time bridge: When map detects the start location (blue circle),
        # take that blue circle as the start location until user enters custom start location
        map_var_name = m.get_name()
        gps_bridge_html = f"""
        <script>
        (function() {{
            var isCustomOrigin = {json.dumps(bool(is_custom_origin))};

            function syncDetectedStartLocation(lat, lon, acc) {{
                if (isCustomOrigin) {{
                    console.log("[PATHFINDER] Custom start location is active; preserving custom origin.");
                    return;
                }}
                try {{
                    if (window.parent && window.parent !== window) {{
                        window.parent.postMessage({{
                            type: 'PATHFINDER_GPS_DETECTED',
                            lat: lat,
                            lon: lon,
                            acc: (acc || 6.0)
                        }}, '*');
                    }}
                }} catch(e) {{}}
                try {{
                    var targetWin = window.parent || window;
                    var url;
                    try {{
                        url = new URL(targetWin.location.href);
                    }} catch(e) {{
                        url = new URL(window.location.href);
                        targetWin = window;
                    }}

                    var curLat = url.searchParams.get("gps_lat");
                    var curLon = url.searchParams.get("gps_lon");

                    var shouldUpdate = false;
                    if (!curLat || !curLon) {{
                        shouldUpdate = true;
                    }} else {{
                        var dLat = Math.abs(parseFloat(curLat) - lat);
                        var dLon = Math.abs(parseFloat(curLon) - lon);
                        if (dLat > 0.0003 || dLon > 0.0003) {{
                            shouldUpdate = true;
                        }}
                    }}

                    if (shouldUpdate) {{
                        console.log("[PATHFINDER] Map detected blue circle GPS at:", lat, lon, "Taking as start location.");
                        url.searchParams.set("gps_lat", lat.toFixed(6));
                        url.searchParams.set("gps_lon", lon.toFixed(6));
                        url.searchParams.set("gps_acc", (acc || 6.0).toFixed(1));
                        if (targetWin.history && targetWin.history.replaceState) {{
                            targetWin.history.replaceState(null, '', url.toString());
                        }}
                    }}
                }} catch(err) {{
                    console.warn("[PATHFINDER] Could not sync detected start location to parent window:", err);
                }}
            }}

            function initMapLocationBridge() {{
                var leafletMap = window["{map_var_name}"];
                if (!leafletMap) {{
                    var mapEls = document.querySelectorAll('.folium-map');
                    if (mapEls && mapEls.length > 0 && window[mapEls[0].id]) {{
                        leafletMap = window[mapEls[0].id];
                    }}
                }}

                if (leafletMap) {{
                    leafletMap.on('locationfound', function(e) {{
                        var lat = e.latlng.lat;
                        var lon = e.latlng.lng;
                        var acc = e.accuracy || 6.0;
                        syncDetectedStartLocation(lat, lon, acc);
                    }});
                }} else {{
                    setTimeout(initMapLocationBridge, 120);
                }}
            }}

            var movingRunnerMarker = null;

            function updateMovingRunnerPosition(lat, lon, label, avatarIcon, avatarLabel, speedKmh, isReturning) {{
                var leafletMap = window["{map_var_name}"];
                if (!leafletMap) {{
                    var mapEls = document.querySelectorAll('.folium-map');
                    if (mapEls && mapEls.length > 0 && window[mapEls[0].id]) {{
                        leafletMap = window[mapEls[0].id];
                    }}
                }}
                if (!leafletMap) return;

                var iconSym = avatarIcon || "🏃‍♂️";
                var speedText = (speedKmh ? (" • " + speedKmh + " km/h") : "");
                var badgeText = isReturning ? ("🔄 Returning: " + (label || "Start")) : (iconSym + " " + (avatarLabel || "Virtual Companion") + speedText);
                var badgeBg = isReturning ? "#0284c7" : "#059669";

                var runnerHtml = '<div style="position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 56px; height: 56px;">' +
                      '<div id="folium-runner-label" style="position: absolute; top: -20px; background: ' + badgeBg + '; color: #ffffff; font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 999px; white-space: nowrap; box-shadow: 0 0 10px #38bdf8; border: 1.5px solid #38bdf8; z-index: 10;">' + badgeText + '</div>' +
                      '<div style="position: absolute; width: 46px; height: 46px; border-radius: 50%; background: rgba(56, 189, 248, 0.4); border: 2.5px solid #38bdf8; box-shadow: 0 0 20px #38bdf8; animation: foliumRadar 1.4s infinite ease-out;"></div>' +
                      '<div style="font-size: 30px; z-index: 5; filter: drop-shadow(0 3px 6px rgba(0,0,0,0.8));">' + iconSym + '</div>' +
                      '</div>';

                if (!movingRunnerMarker) {{
                    var runnerIcon = L.divIcon({{
                        className: 'live-virtual-runner-boy-icon',
                        html: runnerHtml,
                        iconSize: [56, 56],
                        iconAnchor: [28, 28]
                    }});
                    movingRunnerMarker = L.marker([lat, lon], {{ icon: runnerIcon, zIndexOffset: 9999 }}).addTo(leafletMap);
                }} else {{
                    movingRunnerMarker.setLatLng([lat, lon]);
                    var iconEl = movingRunnerMarker.getElement();
                    if (iconEl) {{
                        var lbl = iconEl.querySelector('#folium-runner-label');
                        if (lbl) {{
                            lbl.innerText = badgeText;
                            lbl.style.background = badgeBg;
                        }}
                    }}
                }}
                leafletMap.panTo([lat, lon], {{ animate: true, duration: 0.8 }});
            }}

            window.updateMovingCarPosition = updateMovingRunnerPosition;

            window.addEventListener('storage', function(e) {{
                if (e.key === 'pathfinder_vehicle_state' && e.newValue) {{
                    try {{
                        var data = JSON.parse(e.newValue);
                        if (data.lat && data.lon) {{
                            updateMovingRunnerPosition(data.lat, data.lon, data.label, data.avatarIcon, data.avatarLabel, data.speedKmh, data.isReturning);
                        }}
                    }} catch(err) {{}}
                }}
            }});

            window.addEventListener('message', function(e) {{
                if (e.data && e.data.type === 'PATHFINDER_VEHICLE_UPDATE') {{
                    var data = e.data;
                    if (data.lat && data.lon) {{
                        updateMovingRunnerPosition(data.lat, data.lon, data.label, data.avatarIcon, data.avatarLabel, data.speedKmh, data.isReturning);
                    }}
                }}
            }});

            if (document.readyState === "complete" || document.readyState === "interactive") {{
                setTimeout(initMapLocationBridge, 150);
            }} else {{
                document.addEventListener("DOMContentLoaded", initMapLocationBridge);
            }}
        }})();
        </script>
        """
        m.get_root().html.add_child(folium.Element(gps_bridge_html))

        # 1. Add Origin Marker with Small Boy / Driving Car Avatar & Pulsing Radar Wave
        if origin_coords:
            # Snap start vehicle marker directly to the first drivable road waypoint of the route when routes exist
            effective_origin = origin_coords
            if routes and len(routes) > 0:
                first_r = next((r for r in routes if r.get("rank") == 1 or r.get("is_eligible")), routes[0])
                first_pts = first_r.get("polyline", [])
                if first_pts and len(first_pts) > 0:
                    effective_origin = (float(first_pts[0][0]), float(first_pts[0][1]))

            avatar_key = str(traveler_avatar).lower()
            if "tractor" in avatar_key:
                avatar_sym = "🚜"
                avatar_title = "🚜 Virtual Tractor (Standing at Start Point)"
                badge_title = "🚜 Virtual Tractor (Start Point)"
                halo_border = "#16a34a"
                halo_bg = "rgba(22, 163, 74, 0.35)"
            elif "bike" in avatar_key or "motorcycle" in avatar_key:
                avatar_sym = "🏍️"
                avatar_title = "🏍️ Virtual Motorcyclist (Standing at Start Point)"
                badge_title = "🏍️ Virtual Motorcyclist (Start Point)"
                halo_border = "#0284c7"
                halo_bg = "rgba(2, 132, 199, 0.35)"
            elif "truck" in avatar_key:
                avatar_sym = "🚚"
                avatar_title = "🚚 Virtual Truck (Standing at Start Point)"
                badge_title = "🚚 Virtual Truck (Start Point)"
                halo_border = "#f59e0b"
                halo_bg = "rgba(245, 158, 11, 0.35)"
            elif "bicycle" in avatar_key:
                avatar_sym = "🚴"
                avatar_title = "🚴 Virtual Cyclist (Standing at Start Point)"
                badge_title = "🚴 Virtual Cyclist (Start Point)"
                halo_border = "#10b981"
                halo_bg = "rgba(16, 185, 129, 0.35)"
            elif "walk" in avatar_key or avatar_key == "boy":
                avatar_sym = "🚶‍♂️"
                avatar_title = "🚶‍♂️ Virtual Boy Walking (Standing at Start Point)"
                badge_title = "🚶‍♂️ Virtual Boy Walking (Start Point)"
                halo_border = "#38bdf8"
                halo_bg = "rgba(56, 189, 248, 0.35)"
            elif "runner" in avatar_key or "run" in avatar_key:
                avatar_sym = "🏃‍♂️"
                avatar_title = "🏃‍♂️ Virtual Runner (Standing at Start Point)"
                badge_title = "🏃‍♂️ Virtual Runner (Start Point)"
                halo_border = "#38bdf8"
                halo_bg = "rgba(56, 189, 248, 0.35)"
            else:
                avatar_sym = "🚗"
                avatar_title = "🚗 Virtual Car Companion (Standing at Start Point)"
                badge_title = "🚗 Virtual Car (Start Point)"
                halo_border = "#0284c7"
                halo_bg = "rgba(2, 132, 199, 0.35)"

            # Inject CSS animation styles into Folium map
            folium_css = """
            <style>
            @keyframes foliumRadar {
                0% { transform: scale(0.5); opacity: 1; }
                60% { transform: scale(1.6); opacity: 0.4; }
                100% { transform: scale(2.2); opacity: 0; }
            }
            @keyframes foliumLegLeft {
                0% { transform: rotate(-24deg); transform-origin: 28px 42px; }
                100% { transform: rotate(24deg); transform-origin: 28px 42px; }
            }
            @keyframes foliumLegRight {
                0% { transform: rotate(24deg); transform-origin: 38px 42px; }
                100% { transform: rotate(-24deg); transform-origin: 38px 42px; }
            }
            @keyframes foliumArmLeft {
                0% { transform: rotate(24deg); transform-origin: 22px 28px; }
                100% { transform: rotate(-24deg); transform-origin: 22px 28px; }
            }
            @keyframes foliumArmRight {
                0% { transform: rotate(-24deg); transform-origin: 42px 28px; }
                100% { transform: rotate(24deg); transform-origin: 42px 28px; }
            }
            .folium-walking-leg-left { animation: foliumLegLeft 0.5s infinite alternate ease-in-out; }
            .folium-walking-leg-right { animation: foliumLegRight 0.5s infinite alternate ease-in-out; }
            .folium-walking-arm-left { animation: foliumArmLeft 0.5s infinite alternate ease-in-out; }
            .folium-walking-arm-right { animation: foliumArmRight 0.5s infinite alternate ease-in-out; }
            </style>
            """
            m.get_root().header.add_child(folium.Element(folium_css))

            if "walk" in avatar_key or avatar_key == "boy":
                avatar_html = f"""
                <div style="position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 60px; height: 60px; cursor: pointer;">
                    <div style="position: absolute; bottom: 58px; background: #0284c7; color: #ffffff; font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 999px; white-space: nowrap; box-shadow: 0 0 10px #38bdf8; border: 1.5px solid #38bdf8; z-index: 20; pointer-events: none;">{badge_title}</div>
                    <div style="position: absolute; width: 48px; height: 48px; border-radius: 50%; background: {halo_bg}; border: 2.5px solid {halo_border}; box-shadow: 0 0 16px {halo_border}; animation: foliumRadar 1.6s infinite ease-out;"></div>
                    <div style="position: relative; z-index: 10; filter: drop-shadow(0 3px 6px rgba(0,0,0,0.8));">
                        <svg width="44" height="44" viewBox="0 0 64 64" fill="none">
                            <rect x="12" y="24" width="12" height="18" rx="4" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
                            <g class="folium-walking-leg-left">
                                <line x1="28" y1="42" x2="24" y2="58" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round"/>
                                <ellipse cx="23" cy="58" rx="4.5" ry="3" fill="#ef4444"/>
                            </g>
                            <g class="folium-walking-leg-right">
                                <line x1="38" y1="42" x2="42" y2="58" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round"/>
                                <ellipse cx="43" cy="58" rx="4.5" ry="3" fill="#ef4444"/>
                            </g>
                            <g class="folium-walking-arm-left">
                                <line x1="22" y1="28" x2="16" y2="38" stroke="#fde047" stroke-width="3" stroke-linecap="round"/>
                            </g>
                            <rect x="22" y="24" width="20" height="20" rx="5" fill="#10b981" stroke="#059669" stroke-width="2"/>
                            <rect x="29" y="28" width="6" height="5" rx="1.5" fill="#ffffff" opacity="0.85"/>
                            <g class="folium-walking-arm-right">
                                <line x1="42" y1="28" x2="48" y2="38" stroke="#fde047" stroke-width="3.5" stroke-linecap="round"/>
                            </g>
                            <circle cx="32" cy="15" r="9" fill="#fde047" stroke="#ca8a04" stroke-width="1.5"/>
                            <path d="M22 13 C22 7, 42 7, 42 13 L47 14 L22 14 Z" fill="#ef4444"/>
                            <circle cx="30" cy="14" r="1.5" fill="#0f172a"/>
                            <circle cx="36" cy="14" r="1.5" fill="#0f172a"/>
                            <path d="M30 18 Q33 21 36 18" stroke="#0f172a" stroke-width="1.5" fill="none" stroke-linecap="round"/>
                            <circle cx="23" cy="15" r="2" fill="#38bdf8"/>
                        </svg>
                    </div>
                </div>
                """
            else:
                avatar_html = f"""
                <div style="position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 60px; height: 60px; cursor: pointer;">
                    <div style="position: absolute; bottom: 58px; background: #0284c7; color: #ffffff; font-size: 10px; font-weight: 800; padding: 2px 8px; border-radius: 999px; white-space: nowrap; box-shadow: 0 0 10px #38bdf8; border: 1.5px solid #38bdf8; z-index: 20; pointer-events: none;">{badge_title}</div>
                    <div style="position: absolute; width: 48px; height: 48px; border-radius: 50%; background: {halo_bg}; border: 2.5px solid {halo_border}; box-shadow: 0 0 16px {halo_border}; animation: foliumRadar 1.6s infinite ease-out;"></div>
                    <div style="position: relative; z-index: 10; font-size: 30px; line-height: 1; filter: drop-shadow(0 3px 6px rgba(0,0,0,0.8));">{avatar_sym}</div>
                </div>
                """

            folium.Marker(
                location=effective_origin,
                popup=folium.Popup(f"<b>{avatar_title}</b><br>Coords: {effective_origin[0]:.5f}, {effective_origin[1]:.5f}", max_width=260),
                tooltip=avatar_title,
                icon=folium.DivIcon(html=avatar_html, icon_size=(60, 60), icon_anchor=(30, 30))
            ).add_to(m)

            folium.Circle(
                location=effective_origin,
                radius=35.0,
                color=halo_border,
                weight=2,
                fill=True,
                fill_color=halo_border,
                fill_opacity=0.3
            ).add_to(m)

        # Breadcrumb Movement History Trail
        if breadcrumb_trail and len(breadcrumb_trail) > 1:
            folium.PolyLine(
                locations=breadcrumb_trail,
                color="#0284c7",
                weight=3,
                opacity=0.75,
                dash_array="6, 8",
                tooltip="Live Movement Trail"
            ).add_to(m)

        # 2. Add Destination Marker
        if destination_coords:
            folium.Marker(
                location=destination_coords,
                popup=folium.Popup("<b>🏁 Safe Destination</b><br>Designated assembly or target", max_width=250),
                tooltip="Safe Destination",
                icon=folium.Icon(color="green", icon="flag-checkered", prefix="fa")
            ).add_to(m)

        # 3. Add Verified Road Restrictions & Blockages with Caution Symbols
        if road_closures:
            for rc in road_closures:
                c_lat = rc.get("lat")
                c_lon = rc.get("lon")
                road_name = rc.get("road_name", "Arterial Road")
                r_type = rc.get("type", "ROAD_BLOCKAGE")
                desc = rc.get("description", "Road Blockage / Scheduled Maintenance")
                is_hard = rc.get("is_hard_closure", True)
                radius = float(rc.get("radius_meters", 120.0))

                if c_lat and c_lon:
                    # Caution Zone Buffer Circle
                    folium.Circle(
                        location=[c_lat, c_lon],
                        radius=max(60.0, radius),
                        color="#ef4444" if is_hard else "#f59e0b",
                        weight=3,
                        dash_array="6, 6",
                        fill=True,
                        fill_color="#ef4444" if is_hard else "#f59e0b",
                        fill_opacity=0.35,
                        tooltip=f"⚠️ CAUTION: {'Road Blockage / Closure' if is_hard else 'Road Work'} - {road_name}"
                    ).add_to(m)

                    # Prominent Floating Caution Badge on Map
                    badge_html = f"""
                    <div style="
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        cursor: pointer;
                        filter: drop-shadow(0 4px 10px rgba(0,0,0,0.6));
                    ">
                        <div style="
                            display: flex;
                            align-items: center;
                            gap: 6px;
                            background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
                            color: #ffffff;
                            border: 2px solid #ffffff;
                            border-radius: 20px;
                            padding: 5px 12px;
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                            font-weight: 800;
                            font-size: 12px;
                            letter-spacing: 0.5px;
                            white-space: nowrap;
                            box-shadow: 0 0 15px rgba(239, 68, 68, 0.9);
                        ">
                            <span style="font-size: 16px;">⚠️</span>
                            <span>ROAD BLOCKED</span>
                        </div>
                        <div style="
                            width: 0;
                            height: 0;
                            border-left: 7px solid transparent;
                            border-right: 7px solid transparent;
                            border-top: 8px solid #b91c1c;
                            margin-top: -1px;
                        "></div>
                    </div>
                    """
                    folium.Marker(
                        location=[c_lat, c_lon],
                        icon=folium.DivIcon(
                            html=badge_html,
                            icon_size=(160, 40),
                            icon_anchor=(80, 40)
                        ),
                        popup=folium.Popup(
                            f"""
                            <div style='font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; min-width: 220px; padding: 4px;'>
                                <div style='background: #dc2626; color: #ffffff; padding: 5px 8px; border-radius: 5px; font-weight: 800; font-size: 0.84rem; display: flex; align-items: center; gap: 6px;'>
                                    <span>⚠️</span> <span>CAUTION: ROAD BLOCKAGE</span>
                                </div>
                                <div style='margin-top: 8px; font-size: 0.80rem; color: #1e293b; line-height: 1.45;'>
                                    <b>Location:</b> {road_name}<br>
                                    <b>Condition:</b> {r_type}<br>
                                    <b>Details:</b> {desc}<br>
                                    <span style='display: inline-block; margin-top: 4px; color: #b91c1c; font-weight: 700;'>
                                        ⛔ Corridor Impassable — Detour Applied
                                    </span>
                                </div>
                            </div>
                            """,
                            max_width=300
                        ),
                        tooltip=f"⚠️ CAUTION: Road Blockage on {road_name}"
                    ).add_to(m)

        # 4. Add Active Geographic Hazards with Caution Highlight
        if hazards:
            for hz in hazards:
                h_lat = hz.get("lat") or hz.get("latitude")
                h_lon = hz.get("lon") or hz.get("longitude")
                h_type = hz.get("incident_type") or hz.get("type", "HAZARD")
                h_desc = hz.get("description", "Active Incident Reported")
                h_radius = float(hz.get("radius_meters", 150.0))
                h_road = hz.get("affected_road_name", "Local Corridor")
                h_sev = hz.get("severity", "HIGH")
                hazard_emoji = "🔥" if "FIRE" in str(h_type).upper() else ("🌊" if "FLOOD" in str(h_type).upper() else "⚠️")
                badge_title = f"{h_type}".replace("_", " ")

                if h_lat and h_lon:
                    # Caution Hazard Circle Buffer
                    folium.Circle(
                        location=[h_lat, h_lon],
                        radius=max(80.0, h_radius),
                        color="#dc2626",
                        weight=3,
                        dash_array="5, 5",
                        fill=True,
                        fill_color="#dc2626",
                        fill_opacity=0.38,
                        tooltip=f"⚠️ CAUTION: {h_type} Hazard Zone ({h_radius:.0f}m buffer)"
                    ).add_to(m)

                    # Prominent Floating Hazardous Symbol Badge
                    hazard_badge_html = f"""
                    <div style="
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        cursor: pointer;
                        filter: drop-shadow(0 4px 10px rgba(0,0,0,0.6));
                    ">
                        <div style="
                            display: flex;
                            align-items: center;
                            gap: 6px;
                            background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%);
                            color: #ffffff;
                            border: 2px solid #fecaca;
                            border-radius: 20px;
                            padding: 5px 12px;
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                            font-weight: 800;
                            font-size: 12px;
                            letter-spacing: 0.5px;
                            white-space: nowrap;
                            box-shadow: 0 0 18px rgba(220, 38, 38, 0.95);
                        ">
                            <span style="font-size: 16px;">{hazard_emoji} ⚠️</span>
                            <span>{badge_title}</span>
                        </div>
                        <div style="
                            width: 0;
                            height: 0;
                            border-left: 7px solid transparent;
                            border-right: 7px solid transparent;
                            border-top: 8px solid #7f1d1d;
                            margin-top: -1px;
                        "></div>
                    </div>
                    """
                    folium.Marker(
                        location=[h_lat, h_lon],
                        icon=folium.DivIcon(
                            html=hazard_badge_html,
                            icon_size=(180, 40),
                            icon_anchor=(90, 40)
                        ),
                        popup=folium.Popup(
                            f"""
                            <div style='font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; min-width: 220px; padding: 4px;'>
                                <div style='background: #b91c1c; color: #ffffff; padding: 5px 8px; border-radius: 5px; font-weight: 800; font-size: 0.84rem; display: flex; align-items: center; gap: 6px;'>
                                    <span>⚠️</span> <span>CAUTION: {h_type} HAZARD</span>
                                </div>
                                <div style='margin-top: 8px; font-size: 0.80rem; color: #1e293b; line-height: 1.45;'>
                                    <b>Location:</b> {h_road}<br>
                                    <b>Severity:</b> <span style='color: #dc2626; font-weight: 800;'>{h_sev}</span><br>
                                    <b>Buffer Radius:</b> {h_radius:.0f} meters<br>
                                    <b>Report:</b> {h_desc}<br>
                                    <span style='display: inline-block; margin-top: 4px; color: #b91c1c; font-weight: 700;'>
                                        ⚠️ Hazard Zone Excluded from Route
                                    </span>
                                </div>
                            </div>
                            """,
                            max_width=300
                        ),
                        tooltip=f"⚠️ CAUTION: {h_type} Hazard ({h_road})"
                    ).add_to(m)

        # 4b. Add Real-World Emergency Services & Safety Facilities
        if emergency_facilities:
            for fac in emergency_facilities:
                f_lat = fac.get("latitude") or fac.get("lat")
                f_lon = fac.get("longitude") or fac.get("lon")
                if not f_lat or not f_lon:
                    continue
                f_name = fac.get("name", "Emergency Facility")
                f_type = fac.get("facility_type", "Emergency Service")
                f_icon = fac.get("amenity_icon", "🏥")
                f_dist = fac.get("road_distance_km", fac.get("distance_from_route_km", 0.0))
                f_hours = fac.get("operating_hours", "Hours not published")
                f_source = fac.get("data_source", "OpenStreetMap Contributors")
                f_phone = fac.get("contact_phone")
                f_has_ed = fac.get("has_emergency_department")
                f_is_shelter = fac.get("is_officially_designated_shelter")

                if f_icon == "🍽️":
                    badge_border = "#f97316"
                elif f_icon == "⛽":
                    badge_border = "#38bdf8"
                elif f_icon == "🏨":
                    badge_border = "#a855f7"
                elif f_icon in ["🚨", "🏥", "🩺"]:
                    badge_border = "#ef4444"
                elif f_icon == "🏧":
                    badge_border = "#10b981"
                elif f_icon == "🛍️":
                    badge_border = "#ec4899"
                elif f_icon == "🔍":
                    badge_border = "#06b6d4"
                elif f_icon == "⛺":
                    badge_border = "#f59e0b"
                elif f_icon in ["👮", "🚒"]:
                    badge_border = "#0284c7"
                else:
                    badge_border = "#10b981"
                badge_bg = "rgba(15, 23, 42, 0.92)"

                fac_html = f"""
                <div style="
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 32px;
                    height: 32px;
                    background: {badge_bg};
                    border: 2px solid {badge_border};
                    border-radius: 50%;
                    box-shadow: 0 0 10px {badge_border};
                    font-size: 16px;
                    cursor: pointer;
                " title="{f_name}">
                    {f_icon}
                </div>
                """
                ed_badge = "<span style='color:#ef4444; font-weight:700;'>● 24/7 Verified Emergency Dept</span><br>" if f_has_ed else ("<span style='color:#f59e0b; font-weight:700;'>● Primary Clinic (No Dedicated Trauma Unit)</span><br>" if f_has_ed is False else "")
                shelter_badge = "<span style='color:#10b981; font-weight:700;'>● Officially Designated Evacuation Safe Haven</span><br>" if f_is_shelter else ""
                phone_line = f"<b>Contact:</b> {f_phone}<br>" if f_phone else ""

                folium.Marker(
                    location=[f_lat, f_lon],
                    icon=folium.DivIcon(
                        html=fac_html,
                        icon_size=(32, 32),
                        icon_anchor=(16, 16)
                    ),
                    tooltip=f"{f_icon} {f_name} (~{f_dist:.1f} km)",
                    popup=folium.Popup(
                        f"""
                        <div style='font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; min-width: 230px; padding: 4px;'>
                            <div style='background: {badge_border}; color: #ffffff; padding: 4px 8px; border-radius: 4px; font-weight: 800; font-size: 0.82rem;'>
                                {f_icon} {f_type}
                            </div>
                            <div style='margin-top: 6px; font-size: 0.78rem; color: #1e293b; line-height: 1.4;'>
                                <b>{f_name}</b><br>
                                {ed_badge}{shelter_badge}
                                <b>Distance:</b> ~{f_dist:.1f} km from position<br>
                                <b>Operating:</b> {f_hours}<br>
                                {phone_line}
                                <span style='font-size: 0.70rem; color: #64748b;'>Source: {f_source}</span>
                            </div>
                        </div>
                        """,
                        max_width=290
                    )
                ).add_to(m)

        # 4c. Add Multi-User Live Fleet / Convoy Peer Markers
        if fleet_members:
            for member in fleet_members:
                m_lat = member.get("latitude")
                m_lon = member.get("longitude")
                if not m_lat or not m_lon:
                    continue
                m_name = member.get("display_name", "Convoy Member")
                m_avatar = member.get("avatar", "🚗")
                m_role = member.get("role", "traveler").capitalize()
                m_speed = member.get("speed_kmh", 0.0)
                m_dist_lbl = member.get("relative_location_str", member.get("distance_label", ""))
                m_status = member.get("status_msg", "Active")
                m_seen = member.get("last_seen_str", "Just now")

                member_html = f"""
                <div style="position: relative; display: flex; flex-direction: column; align-items: center; cursor: pointer;">
                    <div style="
                        width: 36px; height: 36px; border-radius: 50%;
                        background: rgba(15, 23, 42, 0.95);
                        border: 2px solid #38bdf8;
                        box-shadow: 0 0 14px rgba(56, 189, 248, 0.75), inset 0 0 6px rgba(56, 189, 248, 0.3);
                        display: flex; align-items: center; justify-content: center;
                        font-size: 18px;
                    ">
                        {m_avatar}
                    </div>
                    <div style="
                        background: rgba(15, 23, 42, 0.92);
                        color: #38bdf8;
                        font-weight: 700;
                        font-size: 10px;
                        padding: 1px 5px;
                        border-radius: 4px;
                        border: 1px solid rgba(56, 189, 248, 0.5);
                        margin-top: 2px;
                        white-space: nowrap;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.5);
                    ">
                        {m_name}
                    </div>
                </div>
                """

                popup_html = f"""
                <div style='font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; min-width: 210px; padding: 4px;'>
                    <div style='background: linear-gradient(135deg, #0284c7, #0369a1); color: #ffffff; padding: 4px 8px; border-radius: 5px; font-weight: 800; font-size: 0.82rem; display: flex; align-items: center; justify-content: space-between;'>
                        <span>{m_avatar} {m_name}</span>
                        <span style='font-size: 0.65rem; background: rgba(0,0,0,0.25); padding: 2px 5px; border-radius: 4px;'>{m_role}</span>
                    </div>
                    <div style='margin-top: 6px; font-size: 0.76rem; color: #1e293b; line-height: 1.45;'>
                        <b>Status:</b> <span style='color: #0284c7;'>{m_status}</span><br>
                        <b>Distance:</b> {m_dist_lbl}<br>
                        <b>Live Speed:</b> {m_speed:.1f} km/h<br>
                        <span style='font-size: 0.68rem; color: #64748b;'>Updated: {m_seen}</span>
                    </div>
                </div>
                """

                folium.Marker(
                    location=[m_lat, m_lon],
                    icon=folium.DivIcon(
                        html=member_html,
                        icon_size=(90, 52),
                        icon_anchor=(45, 18)
                    ),
                    tooltip=f"{m_avatar} {m_name} ({m_dist_lbl})",
                    popup=folium.Popup(popup_html, max_width=260)
                ).add_to(m)

        # 5. Add Route Polylines with Multi-Objective Visual Hierarchy
        if routes:
            for idx, r in enumerate(routes):
                coords = r.get("polyline", [])
                if not coords or len(coords) < 2:
                    continue

                status = r.get("safety_status", r.get("status", "ROUTE_ELIGIBLE"))
                rank = r.get("rank", idx + 1)
                is_eligible = r.get("is_eligible", "ELIGIBLE" in str(status).upper())
                is_selected = r.get("is_selected", False)
                has_selection = any(rt.get("is_selected") for rt in routes)

                if not is_eligible or "RESTRICT" in str(status).upper() or "INACCESSIBLE" in str(status).upper():
                    line_color = "#ef4444"  # Muted red for closed routes
                    dash_array = "5, 10"
                    opacity = 0.85 if is_selected else (0.35 if has_selection else 0.55)
                    weight = 6 if is_selected else 3.5
                elif is_selected:
                    line_color = r.get("color") or ("#38bdf8" if rank > 1 else "#10b981")  # Vibrant luminous highlight
                    dash_array = None
                    opacity = 1.0
                    weight = 8.5
                elif has_selection:
                    # Visible distinct alternative when another route is selected
                    line_color = r.get("color") or ("#64748b" if rank != 1 else "#059669")
                    dash_array = None
                    opacity = 0.70
                    weight = 5.0
                else:
                    line_color = r.get("color") or ("#10b981" if rank == 1 else ("#38bdf8" if rank == 2 else "#a855f7"))
                    dash_array = None
                    opacity = 0.95 if rank == 1 else 0.90
                    weight = 6.5 if rank == 1 else 5.5

                route_label = r.get("name", f"Route {idx+1}")
                dist_km = r.get("distance_km", 0.0)
                dur_min = r.get("duration_minutes", 0.0)

                folium.PolyLine(
                    locations=coords,
                    color=line_color,
                    weight=weight,
                    opacity=opacity,
                    dash_array=dash_array,
                    tooltip=f"{route_label} ({dist_km:.1f} km, ~{dur_min:.0f} min) - {status}",
                    popup=folium.Popup(
                        f"<b>{route_label}</b><br>Distance: {dist_km:.2f} km<br>Est. Time: {dur_min:.1f} min<br>Status: <code>{status}</code>",
                        max_width=300
                    )
                ).add_to(m)


        # Dynamic Auto Fit-Bounds: Frame map automatically across global routes & waypoints when explicitly enabled
        if auto_fit_bounds:
            all_pts: List[Tuple[float, float]] = []
            selected_route = next((r for r in routes if r.get("is_selected")), None) if routes else None
            if selected_route and selected_route.get("polyline"):
                all_pts = list(selected_route.get("polyline", []))
            else:
                if origin_coords:
                    all_pts.append(origin_coords)
                if destination_coords:
                    all_pts.append(destination_coords)
                if routes:
                    for r in routes:
                        for pt in r.get("polyline", []):
                            all_pts.append(pt)

            if all_pts and len(all_pts) >= 2:
                lats = [p[0] for p in all_pts]
                lons = [p[1] for p in all_pts]
                min_lat, max_lat = min(lats), max(lats)
                min_lon, max_lon = min(lons), max(lons)
                if (max_lat - min_lat) > 0.003 or (max_lon - min_lon) > 0.003:
                    try:
                        m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]], padding=[35, 35])
                    except Exception:
                        pass

        # 6. Live Google Maps In-Dash Vehicle Navigation Engine directly on Satellite Map (2nd Picture Map)
        if routes:
            active_r = next((r for r in routes if r.get("is_selected")), None) or next((r for r in routes if r.get("rank") == 1 or r.get("is_eligible")), routes[0])
            active_coords = active_r.get("polyline", [])
            route_title = active_r.get("name", "Safe Corridor").split("(")[0].strip()
            avatar_key = str(traveler_avatar).lower()

            if active_coords and len(active_coords) >= 2:
                coords_json = json.dumps(active_coords)
                in_map_script = f"""
                <script>
                (function() {{
                    function setupLiveNavigationEngine() {{
                        let leafletMap = null;
                        for (let k in window) {{
                            if (k.startsWith('map_') && window[k] && typeof window[k].addLayer === 'function') {{
                                leafletMap = window[k];
                                break;
                            }}
                        }}
                        if (!leafletMap) {{
                            const mapDiv = document.querySelector('.folium-map');
                            if (mapDiv && mapDiv.id && window[mapDiv.id]) {{
                                leafletMap = window[mapDiv.id];
                            }}
                        }}
                        if (!leafletMap) {{
                            setTimeout(setupLiveNavigationEngine, 150);
                            return;
                        }}

                        const routePts = {coords_json};
                        if (!routePts || routePts.length < 2) return;

                        // Calculate cumulative distances along route
                        const cumDists = [0];
                        function calcDistM(p1, p2) {{
                            const R = 6371000;
                            const dLat = (p2[0] - p1[0]) * Math.PI / 180;
                            const dLon = (p2[1] - p1[1]) * Math.PI / 180;
                            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                                      Math.cos(p1[0] * Math.PI / 180) * Math.cos(p2[0] * Math.PI / 180) *
                                      Math.sin(dLon/2) * Math.sin(dLon/2);
                            return 2 * R * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
                        }}
                        for (let i = 1; i < routePts.length; i++) {{
                            cumDists.push(cumDists[cumDists.length - 1] + calcDistM(routePts[i-1], routePts[i]));
                        }}
                        const totalDistM = cumDists[cumDists.length - 1] || 1.0;

                        function calcBearing(p0, p1) {{
                            const dLon = (p1[1] - p0[1]) * Math.PI / 180;
                            const lat1 = p0[0] * Math.PI / 180;
                            const lat2 = p1[0] * Math.PI / 180;
                            const y = Math.sin(dLon) * Math.cos(lat2);
                            const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
                            return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
                        }}

                        // Moving Vehicle DivIcon (Car with headlights or selected vehicle)
                        const avatarType = "{avatar_key}";
                        let iconSvg = '';
                        if (avatarType.indexOf('boy') !== -1 || avatarType.indexOf('walk') !== -1) {{
                            iconSvg = `
                            <div style="position:relative; width:48px; height:48px; display:flex; align-items:center; justify-content:center;">
                                <div style="position:absolute; width:44px; height:44px; border-radius:50%; background:rgba(56,189,248,0.35); border:2.5px solid #38bdf8; box-shadow:0 0 16px #38bdf8; animation:foliumRadar 1.6s infinite ease-out;"></div>
                                <div id="satVehicleRotator" style="position:relative; z-index:2; transition:transform 0.2s linear;">
                                    <svg width="44" height="44" viewBox="0 0 64 64" fill="none">
                                        <rect x="12" y="24" width="12" height="18" rx="4" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
                                        <g class="folium-walking-leg-left"><line x1="28" y1="42" x2="24" y2="58" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round"/><ellipse cx="23" cy="58" rx="4.5" ry="3" fill="#ef4444"/></g>
                                        <g class="folium-walking-leg-right"><line x1="38" y1="42" x2="42" y2="58" stroke="#1e293b" stroke-width="4.5" stroke-linecap="round"/><ellipse cx="43" cy="58" rx="4.5" ry="3" fill="#ef4444"/></g>
                                        <rect x="22" y="24" width="20" height="20" rx="5" fill="#10b981" stroke="#059669" stroke-width="2"/>
                                        <circle cx="32" cy="15" r="9" fill="#fde047" stroke="#ca8a04" stroke-width="1.5"/>
                                        <path d="M22 13 C22 7, 42 7, 42 13 L47 14 L22 14 Z" fill="#ef4444"/>
                                    </svg>
                                </div>
                            </div>`;
                        }} else if (avatarType.indexOf('tractor') !== -1) {{
                            iconSvg = `
                            <div style="position:relative; width:48px; height:48px; display:flex; align-items:center; justify-content:center;">
                                <div style="position:absolute; width:44px; height:44px; border-radius:50%; background:rgba(22,163,74,0.35); border:2.5px solid #16a34a; box-shadow:0 0 16px #16a34a; animation:foliumRadar 1.6s infinite ease-out;"></div>
                                <div id="satVehicleRotator" style="position:relative; z-index:2; transition:transform 0.2s linear;">
                                    <svg width="46" height="46" viewBox="0 0 64 64" fill="none">
                                        <line x1="22" y1="20" x2="22" y2="8" stroke="#475569" stroke-width="3" stroke-linecap="round"/>
                                        <rect x="16" y="20" width="22" height="18" rx="4" fill="#15803d" stroke="#166534" stroke-width="2"/>
                                        <circle cx="18" cy="46" r="8" fill="#1e293b" stroke="#eab308" stroke-width="3"/>
                                        <circle cx="48" cy="42" r="14" fill="#0f172a" stroke="#eab308" stroke-width="4"/>
                                    </svg>
                                </div>
                            </div>`;
                        }} else if (avatarType.indexOf('bike') !== -1 || avatarType.indexOf('motorcycle') !== -1) {{
                            iconSvg = `
                            <div style="position:relative; width:48px; height:48px; display:flex; align-items:center; justify-content:center;">
                                <div style="position:absolute; width:44px; height:44px; border-radius:50%; background:rgba(2,132,199,0.35); border:2.5px solid #0284c7; box-shadow:0 0 16px #0284c7; animation:foliumRadar 1.6s infinite ease-out;"></div>
                                <div id="satVehicleRotator" style="position:relative; z-index:2; transition:transform 0.2s linear;">
                                    <svg width="46" height="46" viewBox="0 0 64 64" fill="none">
                                        <circle cx="16" cy="44" r="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2.5"/>
                                        <circle cx="48" cy="44" r="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2.5"/>
                                        <path d="M16 44 L30 32 L40 32 L48 44" stroke="#e11d48" stroke-width="4" stroke-linecap="round"/>
                                    </svg>
                                </div>
                            </div>`;
                        }} else {{
                            // Google Maps GPS Car Arrow with Headlight Beam
                            iconSvg = `
                            <div style="position:relative; width:48px; height:48px; display:flex; align-items:center; justify-content:center;">
                                <div style="position:absolute; width:44px; height:44px; border-radius:50%; background:rgba(16,185,129,0.35); border:2.5px solid #10b981; box-shadow:0 0 18px #10b981; animation:foliumRadar 1.6s infinite ease-out;"></div>
                                <div id="satVehicleRotator" style="position:relative; z-index:2; transition:transform 0.2s linear;">
                                    <svg width="44" height="44" viewBox="0 0 64 64" fill="none">
                                        <path d="M32 4 L14 56 L32 46 L50 56 Z" fill="rgba(56,189,248,0.35)"/>
                                        <rect x="20" y="20" width="24" height="34" rx="7" fill="#0284c7" stroke="#38bdf8" stroke-width="2"/>
                                        <rect x="24" y="26" width="16" height="9" rx="3" fill="#0f172a"/>
                                        <rect x="24" y="42" width="16" height="5" rx="2" fill="#0f172a"/>
                                        <rect x="25" y="32" width="14" height="12" rx="3" fill="#0369a1"/>
                                        <circle cx="23" cy="22" r="2.5" fill="#fef08a"/>
                                        <circle cx="41" cy="22" r="2.5" fill="#fef08a"/>
                                    </svg>
                                </div>
                            </div>`;
                        }}

                        const initialBrng = calcBearing(routePts[0], routePts[1]);
                        const vehicleMarker = L.marker(routePts[0], {{
                            icon: L.divIcon({{
                                html: iconSvg,
                                iconSize: [48, 48],
                                iconAnchor: [24, 24]
                            }}),
                            zIndexOffset: 3000
                        }}).addTo(leafletMap);

                        setTimeout(() => {{
                            const rot = document.getElementById('satVehicleRotator');
                            if (rot) rot.style.transform = `rotate(${{initialBrng}}deg)`;
                        }}, 100);

                        // Floating In-Dash Google Maps HUD atop the Satellite Map
                        const hud = document.createElement('div');
                        hud.style.cssText = 'position:absolute; top:12px; left:12px; right:12px; z-index:1000; background:linear-gradient(135deg,#065f46 0%,#047857 70%,#0f766e 100%); border:2px solid #10b981; border-radius:12px; padding:10px 14px; box-shadow:0 8px 24px rgba(0,0,0,0.6); display:flex; align-items:center; justify-content:space-between; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; color:#ffffff; user-select:none;';
                        const hasHazardsOrClosures = Boolean({json.dumps(bool(hazards or road_closures))});
                        const satHudDesc = hasHazardsOrClosures ? "Evading Verified Road Obstacles on Corridor" : "Satellite Verified: 100% Open Corridor • No Road Blockages";
                        hud.innerHTML = `
                            <div style="display:flex; align-items:center; gap:12px;">
                                <div id="satTurnIcon" style="width:42px; height:42px; background:rgba(255,255,255,0.2); border:2px solid #ffffff; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:24px; box-shadow:0 0 10px rgba(255,255,255,0.3);">🟢</div>
                                <div>
                                    <div id="satTurnDist" style="font-size:1.15rem; font-weight:900; line-height:1.1;">{route_title}</div>
                                    <div id="satTurnRoad" style="font-size:0.76rem; font-weight:700; color:#d1fae5;">Safe Corridor Navigation Active</div>
                                    <div id="satTurnDesc" style="font-size:0.70rem; color:#a7f3d0; opacity:0.9;">${{satHudDesc}}</div>
                                </div>
                            </div>
                            <div style="display:flex; flex-direction:column; align-items:flex-end; gap:6px;">
                                <div style="display:flex; gap:6px;">
                                    <button id="satPlayBtn" style="background:#10b981; color:#ffffff; border:none; padding:6px 12px; border-radius:6px; font-weight:800; font-size:0.75rem; cursor:pointer; box-shadow:0 2px 8px rgba(16,185,129,0.5);">▶️ Move Along Route</button>
                                    <button id="satGpsBtn" style="background:rgba(255,255,255,0.15); color:#ffffff; border:1px solid rgba(255,255,255,0.3); padding:6px 10px; border-radius:6px; font-weight:700; font-size:0.75rem; cursor:pointer;">📡 GPS Sync</button>
                                </div>
                                <div id="satEtaBadge" style="font-size:0.70rem; background:rgba(0,0,0,0.35); padding:2px 8px; border-radius:4px; color:#cbd5e1; border:1px solid rgba(255,255,255,0.15);">● Google Maps Live Guidance</div>
                            </div>
                        `;
                        leafletMap.getContainer().appendChild(hud);

                        // Spoken Voice Helper (Silenced: AI voice assistant removed per user request)
                        let voiceMuted = true;
                        function speak(txt) {{
                            if ('speechSynthesis' in window) {{
                                try {{ window.speechSynthesis.cancel(); }} catch(e) {{}}
                            }}
                            return;
                        }}

                        const satVoiceBtnEl = document.getElementById('satVoiceBtn');
                        if (satVoiceBtnEl) {{
                            satVoiceBtnEl.onclick = function() {{
                                if ('speechSynthesis' in window) window.speechSynthesis.cancel();
                            }};
                        }}

                        // Navigation State
                        let isNavigating = false;
                        let progress = 0.0;
                        let animId = null;
                        let lastT = 0;
                        let gpsWatch = null;

                        function updateVehicle(latLon, brng) {{
                            vehicleMarker.setLatLng(latLon);
                            const r = document.getElementById('satVehicleRotator');
                            if (r && brng !== undefined) {{
                                if (avatarType.indexOf('boy') !== -1) {{
                                    r.style.transform = (brng > 180 && brng < 360) ? 'scaleX(-1)' : 'scaleX(1)';
                                }} else {{
                                    r.style.transform = `rotate(${{brng}}deg)`;
                                }}
                            }}
                        }}

                        function stepAnim(t) {{
                            if (!isNavigating) return;
                            if (!lastT) lastT = t;
                            const dt = (t - lastT) / 1000.0;
                            lastT = t;

                            const speedMps = (avatarType.indexOf('boy') !== -1) ? 3.0 : 18.0;
                            const dTraveled = speedMps * dt;
                            progress += (dTraveled / totalDistM);

                            if (progress >= 1.0) {{
                                progress = 1.0;
                                isNavigating = false;
                                document.getElementById('satPlayBtn').innerText = '▶️ Restart';
                                document.getElementById('satTurnDesc').innerText = 'Arrived at destination safe terminal';
                                updateVehicle(routePts[routePts.length - 1], calcBearing(routePts[routePts.length - 2], routePts[routePts.length - 1]));
                                speak('You have arrived at your destination: Guntur City Center. Navigation complete.');
                                return;
                            }}

                            const curTargetM = progress * totalDistM;
                            let idx = 0;
                            while (idx < cumDists.length - 1 && cumDists[idx + 1] < curTargetM) {{
                                idx++;
                            }}
                            const segStart = cumDists[idx];
                            const segEnd = cumDists[idx + 1] || (segStart + 0.001);
                            const segT = Math.max(0, Math.min(1, (curTargetM - segStart) / (segEnd - segStart)));

                            const p0 = routePts[idx];
                            const p1 = routePts[Math.min(idx + 1, routePts.length - 1)];
                            const cLat = p0[0] + (p1[0] - p0[0]) * segT;
                            const cLon = p0[1] + (p1[1] - p0[1]) * segT;
                            const brng = calcBearing(p0, p1);

                            updateVehicle([cLat, cLon], brng);

                            if (idx % 4 === 0) {{
                                leafletMap.panTo([cLat, cLon], {{ animate: true, duration: 0.25 }});
                            }}

                            const remM = Math.max(0, totalDistM - curTargetM);
                            document.getElementById('satTurnDist').innerText = remM > 1000 ? `${{(remM/1000).toFixed(1)}} km remaining` : `${{Math.round(remM)}} m remaining`;

                            animId = requestAnimationFrame(stepAnim);
                        }}

                        document.getElementById('satPlayBtn').onclick = function() {{
                            if (isNavigating) {{
                                isNavigating = false;
                                this.innerText = '▶️ Resume';
                                if (animId) cancelAnimationFrame(animId);
                            }} else {{
                                if (progress >= 1.0) progress = 0.0;
                                isNavigating = true;
                                this.innerText = '⏸️ Pause';
                                lastT = performance.now();
                                speak('Starting live navigation along {route_title}.');
                                animId = requestAnimationFrame(stepAnim);
                            }}
                        }};

                        // Automatic Live Satellite GPS Tracking & Movement Detection Engine
                        let isGps = true;
                        let liveSatMarker = null;
                        let liveSatCircle = null;
                        let liveTrailPoly = L.polyline([], {{
                            color: '#06b6d4',
                            weight: 3.5,
                            opacity: 0.8,
                            dashArray: '5, 8'
                        }}).addTo(leafletMap);
                        let prevGpsLat = null, prevGpsLon = null, prevGpsTime = 0;

                        function handleGpsPosition(pos) {{
                            const uLat = pos.coords.latitude;
                            const uLon = pos.coords.longitude;
                            const acc = pos.coords.accuracy || 8.0;
                            const now = Date.now();

                            // Instantaneous speed calculation (km/h)
                            let speedKmh = 0.0;
                            if (pos.coords.speed !== null && !isNaN(pos.coords.speed) && pos.coords.speed > 0) {{
                                speedKmh = pos.coords.speed * 3.6;
                            }} else if (prevGpsLat !== null && prevGpsTime > 0) {{
                                const dt = (now - prevGpsTime) / 1000.0;
                                if (dt > 0.4) {{
                                    const dm = calcDistM([prevGpsLat, prevGpsLon], [uLat, uLon]);
                                    speedKmh = (dm / dt) * 3.6;
                                }}
                            }}

                            // Heading / Bearing calculation
                            let liveBrng = pos.coords.heading;
                            if (liveBrng === null || isNaN(liveBrng) || liveBrng === 0) {{
                                if (prevGpsLat !== null) {{
                                    liveBrng = calcBearing([prevGpsLat, prevGpsLon], [uLat, uLon]);
                                }} else {{
                                    liveBrng = 0.0;
                                }}
                            }}

                            prevGpsLat = uLat;
                            prevGpsLon = uLon;
                            prevGpsTime = now;

                            // Update live movement trail on map
                            liveTrailPoly.addLatLng([uLat, uLon]);

                            // Satellite GPS pulsating pin & accuracy halo
                            const satPinHtml = `
                                <div style="position:relative; width:34px; height:34px; display:flex; align-items:center; justify-content:center;">
                                    <div style="position:absolute; width:32px; height:32px; border-radius:50%; background:rgba(6,182,212,0.45); animation:foliumRadar 1.5s infinite ease-out;"></div>
                                    <div style="width:14px; height:14px; border-radius:50%; background:#06b6d4; border:2.5px solid #ffffff; box-shadow:0 0 12px #06b6d4;"></div>
                                </div>
                            `;

                            if (!liveSatMarker) {{
                                liveSatMarker = L.marker([uLat, uLon], {{
                                    icon: L.divIcon({{ html: satPinHtml, iconSize: [34, 34], iconAnchor: [17, 17] }}),
                                    zIndexOffset: 3500
                                }}).addTo(leafletMap);

                                liveSatCircle = L.circle([uLat, uLon], {{
                                    radius: acc,
                                    color: '#06b6d4',
                                    fillColor: '#06b6d4',
                                    fillOpacity: 0.12,
                                    weight: 1.5
                                }}).addTo(leafletMap);
                            }} else {{
                                liveSatMarker.setLatLng([uLat, uLon]);
                                liveSatCircle.setLatLng([uLat, uLon]);
                                liveSatCircle.setRadius(acc);
                            }}

                            // Nearest corridor snapping & off-corridor detection
                            let minD = Infinity;
                            let snapPt = routePts[0];
                            let bestSeg = 0;
                            for (let i = 0; i < routePts.length - 1; i++) {{
                                const d = calcDistM([uLat, uLon], routePts[i]);
                                if (d < minD) {{
                                    minD = d;
                                    snapPt = routePts[i];
                                    bestSeg = i;
                                }}
                            }}

                            const routeSegBrng = calcBearing(routePts[bestSeg], routePts[Math.min(bestSeg + 1, routePts.length - 1)]);
                            const effectiveBrng = (speedKmh > 1.2 && liveBrng) ? liveBrng : routeSegBrng;

                            // Update moving avatar position & bearing
                            updateVehicle(minD < 50 ? snapPt : [uLat, uLon], effectiveBrng);

                            // Sync detected satellite GPS location back to application start location unless custom origin is active
                            const isCustomStart = {json.dumps(bool(is_custom_origin))};
                            if (!isCustomStart) {{
                                try {{
                                    var targetWin = window.parent || window;
                                    var pUrl;
                                    try {{
                                        pUrl = new URL(targetWin.location.href);
                                    }} catch(e) {{
                                        pUrl = new URL(window.location.href);
                                        targetWin = window;
                                    }}
                                    var curLat = pUrl.searchParams.get("gps_lat");
                                    var curLon = pUrl.searchParams.get("gps_lon");
                                    var dLat = curLat ? Math.abs(parseFloat(curLat) - uLat) : 999;
                                    var dLon = curLon ? Math.abs(parseFloat(curLon) - uLon) : 999;
                                    if (!curLat || !curLon || dLat > 0.0003 || dLon > 0.0003) {{
                                        pUrl.searchParams.set("gps_lat", uLat.toFixed(6));
                                        pUrl.searchParams.set("gps_lon", uLon.toFixed(6));
                                        pUrl.searchParams.set("gps_acc", acc.toFixed(1));
                                        try {{
                                            if (targetWin.history && targetWin.history.replaceState) {{
                                                targetWin.history.replaceState(null, '', pUrl.toString());
                                            }}
                                        }} catch(e) {{}}
                                    }}
                                }} catch(e) {{}}
                            }}

                            // Smooth satellite map auto-panning to follow user
                            leafletMap.panTo([uLat, uLon], {{ animate: true, duration: 0.6 }});

                            // Real-time Motion Detection
                            const isMoving = speedKmh > 1.2;
                            const turnDesc = document.getElementById('satTurnDesc');
                            const turnRoad = document.getElementById('satTurnRoad');
                            const etaBadge = document.getElementById('satEtaBadge');
                            const gpsBtn = document.getElementById('satGpsBtn');

                            if (gpsBtn) {{
                                gpsBtn.innerHTML = isMoving ? '🟢 Moving (Live)' : '🛰️ Satellite Active';
                                gpsBtn.style.background = isMoving ? '#059669' : '#0284c7';
                                gpsBtn.style.borderColor = isMoving ? '#10b981' : '#38bdf8';
                            }}

                            if (turnDesc) {{
                                if (isMoving) {{
                                    turnDesc.innerHTML = `<span style="color:#34d399; font-weight:800;">🟢 LIVE MOVEMENT DETECTED</span> • Speed: <b>${{speedKmh.toFixed(1)}} km/h</b> • Bearing: <b>${{Math.round(effectiveBrng)}}°</b>`;
                                }} else {{
                                    turnDesc.innerHTML = `<span style="color:#60a5fa; font-weight:700;">📡 SATELLITE LOCKED</span> • Stationary • Precision: <b>±${{Math.round(acc)}}m</b>`;
                                }}
                            }}

                            if (turnRoad) {{
                                turnRoad.innerText = minD < 45 ? 'On Recommended Safe Corridor' : `Corridor Distance: ${{Math.round(minD)}}m`;
                            }}

                            if (etaBadge) {{
                                etaBadge.innerHTML = isMoving ? `● Moving at ${{speedKmh.toFixed(1)}} km/h` : `● Live Satellite Tracking`;
                                etaBadge.style.color = isMoving ? '#34d399' : '#38bdf8';
                            }}
                        }}

                        function startLiveSatelliteGps() {{
                            if (!navigator.geolocation) {{
                                console.warn('Satellite GPS: Geolocation not supported in browser');
                                const turnDesc = document.getElementById('satTurnDesc');
                                if (turnDesc) turnDesc.innerText = 'GPS not supported in browser';
                                return;
                            }}

                            // Automatic initial fix
                            navigator.geolocation.getCurrentPosition(handleGpsPosition, function(err) {{
                                console.warn('Satellite initial fix warning:', err.message);
                            }}, {{ enableHighAccuracy: true, timeout: 8000, maximumAge: 2000 }});

                            // Continuous live position & movement watcher
                            gpsWatch = navigator.geolocation.watchPosition(handleGpsPosition, function(err) {{
                                console.warn('Satellite live watch warning:', err.message);
                            }}, {{ enableHighAccuracy: true, maximumAge: 1000, timeout: 12000 }});
                        }}

                        // Connect to Satellite Location automatically on startup
                        startLiveSatelliteGps();

                        // Interactive Satellite GPS button toggles or re-centers
                        document.getElementById('satGpsBtn').onclick = function() {{
                            if (prevGpsLat !== null && prevGpsLon !== null) {{
                                leafletMap.panTo([prevGpsLat, prevGpsLon], {{ animate: true, duration: 0.5 }});
                                leafletMap.setZoom(16);
                            }} else {{
                                startLiveSatelliteGps();
                            }}
                        }};
                    }}

                    if (document.readyState === 'complete' || document.readyState === 'interactive') {{
                        setupLiveNavigationEngine();
                    }} else {{
                        window.addEventListener('DOMContentLoaded', setupLiveNavigationEngine);
                    }}
                }})();
                </script>
                """
                m.get_root().html.add_child(folium.Element(in_map_script))

        return m

    def build_interactive_map(
        self,
        center_lat: float,
        center_lon: float,
        zoom_start: int = 13,
        origin_coords: Optional[Tuple[float, float]] = None,
        dest_coords: Optional[Tuple[float, float]] = None,
        route_polylines: Optional[List[Dict[str, Any]]] = None,
        hazards: Optional[List[Dict[str, Any]]] = None,
        road_closures: Optional[List[Dict[str, Any]]] = None,
        breadcrumb_trail: Optional[List[Tuple[float, float]]] = None,
        map_style: str = "satellite_hybrid",
        auto_fit_bounds: bool = False,
        traveler_avatar: str = "boy",
        emergency_facilities: Optional[List[Dict[str, Any]]] = None,
        is_custom_origin: bool = False,
        fleet_members: Optional[List[Dict[str, Any]]] = None
    ) -> folium.Map:
        """Adapts route polylines, road restrictions, and breadcrumb trails for Folium map rendering."""
        routes_adapted = []
        if route_polylines:
            for idx, r in enumerate(route_polylines, start=1):
                routes_adapted.append({
                    "name": r.get("name", f"Route {idx}"),
                    "polyline": r.get("coordinates", []),
                    "rank": r.get("rank", idx),
                    "color": r.get("color"),
                    "is_eligible": r.get("is_eligible", True),
                    "is_selected": r.get("is_selected", False),
                    "safety_status": r.get("status", "ROUTE_ELIGIBLE")
                })

        return self.create_interactive_map(
            center_lat=center_lat,
            center_lon=center_lon,
            zoom=zoom_start,
            origin_coords=origin_coords,
            destination_coords=dest_coords,
            routes=routes_adapted,
            hazards=hazards,
            road_closures=road_closures,
            breadcrumb_trail=breadcrumb_trail,
            map_style=map_style,
            auto_fit_bounds=auto_fit_bounds,
            traveler_avatar=traveler_avatar,
            emergency_facilities=emergency_facilities,
            is_custom_origin=is_custom_origin,
            fleet_members=fleet_members
        )

    def render_hazard_map(
        self,
        center_lat: float,
        center_lon: float,
        zoom: int = 14,
        hazards: Optional[List[Dict[str, Any]]] = None,
        road_closures: Optional[List[Dict[str, Any]]] = None,
        map_style: str = "satellite_hybrid"
    ) -> folium.Map:
        """Renders tactical satellite hazard cartography with spatial buffers and road closures."""
        return self.create_interactive_map(
            center_lat=center_lat,
            center_lon=center_lon,
            zoom=zoom,
            hazards=hazards,
            road_closures=road_closures,
            map_style=map_style
        )

