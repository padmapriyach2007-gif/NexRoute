import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.facilities_service import get_facilities_around_journey, FacilityCategory

cities = [
    ("Paris (Eiffel Tower -> Louvre)", (48.8584, 2.2945), (48.8606, 2.3376)),
    ("New York (Times Square -> Central Park)", (40.7580, -73.9855), (40.7851, -73.9683)),
    ("Tokyo (Shinjuku -> Shibuya)", (35.6938, 139.7034), (35.6595, 139.7005)),
    ("London (Big Ben -> Tower Bridge)", (51.5007, -0.1246), (51.5055, -0.0754)),
    ("Tenali (Current Location -> Tenali)", (16.2410, 80.5840), (16.2428, 80.6360))
]

for name, orig, dest in cities:
    facs = get_facilities_around_journey("🌐 All Facilities", origin_coords=orig, dest_coords=dest, radius_km=5.0)
    cats = {str(f.get("category")) for f in facs}
    names = [f["name"] for f in facs[:5]]
    print(f"\n==========================================")
    print(f"City: {name}")
    print(f"Total Detected Places: {len(facs)}")
    print(f"Distinct Categories: {len(cats)}")
    print(f"Sample Detected Places:")
    for n in names:
        print(f"  • {n}")
    assert len(facs) >= 5, f"Insufficient facilities for {name}"

print("\n>>> ALL WORLDWIDE HUBS VERIFIED SUCCESSFULLY! <<<")
