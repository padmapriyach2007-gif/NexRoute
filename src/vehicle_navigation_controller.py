"""
Vehicle Navigation & Multi-Modal Transportation Controller
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Dynamic Virtual Guide Fleet Architecture

Provides centralized mapping, model loading, posture configuration, kinematics,
and route-following synchronization for ALL transportation modes supported across
the NexRoute / Pathfinder platform.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
import json
from typing import Any, Dict, List, Optional, Tuple, Union


class TransportationMode(str, Enum):
    CAR = "CAR"
    BIKE = "BIKE"
    BUS = "BUS"
    BICYCLE = "BICYCLE"
    WALK = "WALK"
    TRUCK = "TRUCK"
    TRACTOR = "TRACTOR"
    FLIGHT = "FLIGHT"
    WATERWAY = "WATERWAY"
    TAXI = "TAXI"
    TRAIN = "TRAIN"
    METRO = "METRO"


@dataclass
class VehicleModeConfig:
    mode_id: str
    display_name: str
    icon: str
    vehicle_type: str            # "pedestrian", "vehicle", "aircraft", "vessel", "rail"
    movement_type: str           # "ground_walk", "ground_road", "ground_rail", "air", "water"
    model_name: str
    default_speed_kmh: float
    speed_factor: float
    guide_pose: str              # "walking", "seated_car", "riding_moto", "cycling", "elevated_cab", "pilot", "captain"
    seat_offset: List[float]     # [x, y, z] relative to vehicle root
    guide_scale: float
    camera_offset: List[float]   # [x, y, z] camera follow position
    camera_look_at: List[float]  # [x, y, z] camera target point
    wheel_count: int = 0
    wheel_radius: float = 0.35
    flight_altitude: float = 0.0
    is_open_air: bool = False
    has_steering_wheel: bool = False
    has_headlights: bool = True
    tail_lights_color: str = "#ef4444"
    accent_color: str = "#00f0ff"
    sound_fx: str = "motor_hum"


class VehicleModeManager:
    """
    Central registry and configuration manager for all transportation modes.
    Ensures that any mode selected in the UI automatically resolves to its exact
    3D vehicle model, kinematics, speed limits, and guide posture.
    """

    CONFIGS: Dict[str, VehicleModeConfig] = {
        "CAR": VehicleModeConfig(
            mode_id="CAR",
            display_name="Car",
            icon="🚗",
            vehicle_type="vehicle",
            movement_type="ground_road",
            model_name="car",
            default_speed_kmh=65.0,
            speed_factor=1.0,
            guide_pose="seated_car",
            seat_offset=[-0.32, 0.30, -0.15],
            guide_scale=0.68,
            camera_offset=[0, 2.4, -4.8],
            camera_look_at=[0, 1.2, 3.5],
            wheel_count=4,
            wheel_radius=0.38,
            has_steering_wheel=True,
            accent_color="#38bdf8"
        ),
        "BIKE": VehicleModeConfig(
            mode_id="BIKE",
            display_name="Motorcycle",
            icon="🏍️",
            vehicle_type="vehicle",
            movement_type="ground_road",
            model_name="motorcycle",
            default_speed_kmh=50.0,
            speed_factor=0.90,
            guide_pose="riding_moto",
            seat_offset=[0, 0.48, -0.14],
            guide_scale=0.72,
            camera_offset=[0, 2.2, -4.2],
            camera_look_at=[0, 1.1, 3.0],
            wheel_count=2,
            wheel_radius=0.42,
            is_open_air=True,
            accent_color="#00f0ff"
        ),
        "BUS": VehicleModeConfig(
            mode_id="BUS",
            display_name="Transit Bus",
            icon="🚌",
            vehicle_type="vehicle",
            movement_type="ground_road",
            model_name="bus",
            default_speed_kmh=45.0,
            speed_factor=0.75,
            guide_pose="elevated_cab",
            seat_offset=[-0.46, 0.85, 1.45],
            guide_scale=0.62,
            camera_offset=[0, 3.8, -7.8],
            camera_look_at=[0, 1.8, 4.0],
            wheel_count=6,
            wheel_radius=0.48,
            has_steering_wheel=True,
            accent_color="#f59e0b"
        ),
        "BICYCLE": VehicleModeConfig(
            mode_id="BICYCLE",
            display_name="Bicycle",
            icon="🚴",
            vehicle_type="vehicle",
            movement_type="ground_road",
            model_name="bicycle",
            default_speed_kmh=18.0,
            speed_factor=0.35,
            guide_pose="cycling",
            seat_offset=[0, 0.60, -0.16],
            guide_scale=0.75,
            camera_offset=[0, 2.0, -3.8],
            camera_look_at=[0, 1.0, 3.0],
            wheel_count=2,
            wheel_radius=0.45,
            is_open_air=True,
            accent_color="#10b981"
        ),
        "WALK": VehicleModeConfig(
            mode_id="WALK",
            display_name="Walk",
            icon="🚶",
            vehicle_type="pedestrian",
            movement_type="ground_walk",
            model_name="walking-guide",
            default_speed_kmh=4.8,
            speed_factor=0.12,
            guide_pose="walking",
            seat_offset=[0, 0, 0],
            guide_scale=1.0,
            camera_offset=[0, 2.3, -4.2],
            camera_look_at=[0, 1.1, 3.0],
            wheel_count=0,
            is_open_air=True,
            accent_color="#00f0ff"
        ),
        "TRUCK": VehicleModeConfig(
            mode_id="TRUCK",
            display_name="Truck",
            icon="🚚",
            vehicle_type="vehicle",
            movement_type="ground_road",
            model_name="truck",
            default_speed_kmh=55.0,
            speed_factor=0.82,
            guide_pose="elevated_cab",
            seat_offset=[-0.48, 1.15, 1.25],
            guide_scale=0.62,
            camera_offset=[0, 4.2, -8.5],
            camera_look_at=[0, 2.0, 4.0],
            wheel_count=6,
            wheel_radius=0.52,
            has_steering_wheel=True,
            accent_color="#fb923c"
        ),
        "TRACTOR": VehicleModeConfig(
            mode_id="TRACTOR",
            display_name="Tractor",
            icon="🚜",
            vehicle_type="vehicle",
            movement_type="ground_road",
            model_name="tractor",
            default_speed_kmh=25.0,
            speed_factor=0.45,
            guide_pose="elevated_cab",
            seat_offset=[0, 0.98, -0.32],
            guide_scale=0.68,
            camera_offset=[0, 2.8, -5.2],
            camera_look_at=[0, 1.3, 3.0],
            wheel_count=4,
            wheel_radius=0.92,
            is_open_air=True,
            has_steering_wheel=True,
            accent_color="#84cc16"
        ),
        "FLIGHT": VehicleModeConfig(
            mode_id="FLIGHT",
            display_name="Airway",
            icon="✈️",
            vehicle_type="aircraft",
            movement_type="air",
            model_name="airplane",
            default_speed_kmh=280.0,
            speed_factor=3.5,
            guide_pose="pilot",
            seat_offset=[0, 0.28, 0.55],
            guide_scale=0.58,
            camera_offset=[0, 5.8, -11.5],
            camera_look_at=[0, 3.5, 6.0],
            flight_altitude=7.5,
            wheel_count=3,
            accent_color="#38bdf8"
        ),
        "WATERWAY": VehicleModeConfig(
            mode_id="WATERWAY",
            display_name="Waterway",
            icon="🚢",
            vehicle_type="vessel",
            movement_type="water",
            model_name="ferry",
            default_speed_kmh=35.0,
            speed_factor=0.60,
            guide_pose="captain",
            seat_offset=[0, 0.88, 0.35],
            guide_scale=0.62,
            camera_offset=[0, 3.6, -7.2],
            camera_look_at=[0, 1.6, 4.0],
            is_open_air=True,
            accent_color="#06b6d4"
        ),
        "TAXI": VehicleModeConfig(
            mode_id="TAXI",
            display_name="Taxi",
            icon="🚕",
            vehicle_type="vehicle",
            movement_type="ground_road",
            model_name="taxi",
            default_speed_kmh=65.0,
            speed_factor=1.0,
            guide_pose="seated_car",
            seat_offset=[-0.32, 0.30, -0.15],
            guide_scale=0.68,
            camera_offset=[0, 2.4, -4.8],
            camera_look_at=[0, 1.2, 3.5],
            wheel_count=4,
            wheel_radius=0.38,
            has_steering_wheel=True,
            accent_color="#eab308"
        ),
        "TRAIN": VehicleModeConfig(
            mode_id="TRAIN",
            display_name="Train",
            icon="🚆",
            vehicle_type="rail",
            movement_type="ground_rail",
            model_name="train",
            default_speed_kmh=90.0,
            speed_factor=1.5,
            guide_pose="pilot",
            seat_offset=[0, 0.72, 2.2],
            guide_scale=0.62,
            camera_offset=[0, 3.6, -8.2],
            camera_look_at=[0, 1.6, 5.0],
            wheel_count=8,
            accent_color="#a855f7"
        ),
        "METRO": VehicleModeConfig(
            mode_id="METRO",
            display_name="Metro",
            icon="🚇",
            vehicle_type="rail",
            movement_type="ground_rail",
            model_name="train",
            default_speed_kmh=80.0,
            speed_factor=1.35,
            guide_pose="pilot",
            seat_offset=[0, 0.72, 2.2],
            guide_scale=0.62,
            camera_offset=[0, 3.6, -8.2],
            camera_look_at=[0, 1.6, 5.0],
            wheel_count=8,
            accent_color="#ec4899"
        ),
    }

    # Common aliases and synonyms mapping to canonical mode_ids
    ALIASES = {
        "driving": "CAR",
        "automobile": "CAR",
        "motorcar": "CAR",
        "cab": "TAXI",
        "taxi": "TAXI",
        "motorcycle": "BIKE",
        "motorbike": "BIKE",
        "scooter": "BIKE",
        "bicycling": "BICYCLE",
        "cycle": "BICYCLE",
        "cycling": "BICYCLE",
        "bike_cycle": "BICYCLE",
        "walking": "WALK",
        "pedestrian": "WALK",
        "transit": "BUS",
        "public": "BUS",
        "air": "FLIGHT",
        "airplane": "FLIGHT",
        "plane": "FLIGHT",
        "aviation": "FLIGHT",
        "water": "WATERWAY",
        "boat": "WATERWAY",
        "ferry": "WATERWAY",
        "ship": "WATERWAY",
        "maritime": "WATERWAY",
        "rail": "TRAIN",
        "railway": "TRAIN",
        "metro": "METRO",
        "subway": "METRO",
        "semi": "TRUCK",
        "heavy": "TRUCK",
        "lorry": "TRUCK",
        "agro": "TRACTOR",
        "farm": "TRACTOR"
    }

    @classmethod
    def normalize_mode(cls, raw_mode: Optional[str]) -> str:
        """Converts any input string or TravelMode enum to a canonical mode_id."""
        if not raw_mode:
            return "CAR"
        m_str = str(raw_mode).upper().strip()
        # Direct key match
        if m_str in cls.CONFIGS:
            return m_str
        # Lowercase alias match
        lower = m_str.lower()
        if lower in cls.ALIASES:
            return cls.ALIASES[lower]
        # Partial substring match
        for k, target in cls.ALIASES.items():
            if k in lower:
                return target
        for k in cls.CONFIGS:
            if k.lower() in lower:
                return k
        return "CAR"

    @classmethod
    def get_config(cls, mode: Optional[str]) -> VehicleModeConfig:
        """Retrieve full vehicle mode configuration for any mode."""
        canonical = cls.normalize_mode(mode)
        return cls.CONFIGS.get(canonical, cls.CONFIGS["CAR"])

    @classmethod
    def get_all_configs(cls) -> Dict[str, VehicleModeConfig]:
        """Returns the full dictionary of all supported configurations."""
        return cls.CONFIGS.copy()

    @classmethod
    def to_json_dict(cls) -> Dict[str, Any]:
        """Serializes all configs to a dictionary suitable for client JSON injection."""
        return {k: asdict(v) for k, v in cls.CONFIGS.items()}

    @classmethod
    def generate_threejs_vehicle_suite_js(cls) -> str:
        """
        Generates the complete Three.js client-side vehicle controller, model loader,
        skeletal pose adapter, and route-following engine.
        """
        configs_json = json.dumps(cls.to_json_dict())
        return f"""
        // =========================================================================
        // DYNAMIC VEHICLE MODE-BASED VIRTUAL GUIDE NAVIGATION SUITE
        // Modular Architecture: ModeManager, ModelLoader, PoseController, MovementController
        // =========================================================================

        const VEHICLE_CONFIGS = {configs_json};

        // 1. VEHICLE MODE MANAGER
        const VehicleModeManager = {{
            configs: VEHICLE_CONFIGS,
            activeMode: 'CAR',

            normalizeMode: function(rawMode) {{
                if (!rawMode) return 'CAR';
                const s = String(rawMode).toUpperCase().trim();
                if (this.configs[s]) return s;
                const lower = s.toLowerCase();
                const aliases = {{
                    'driving': 'CAR', 'automobile': 'CAR', 'motorcar': 'CAR',
                    'cab': 'TAXI', 'taxi': 'TAXI',
                    'motorcycle': 'BIKE', 'motorbike': 'BIKE', 'scooter': 'BIKE',
                    'bicycling': 'BICYCLE', 'cycle': 'BICYCLE', 'cycling': 'BICYCLE',
                    'walking': 'WALK', 'pedestrian': 'WALK',
                    'transit': 'BUS', 'public': 'BUS',
                    'air': 'FLIGHT', 'airplane': 'FLIGHT', 'plane': 'FLIGHT', 'aviation': 'FLIGHT',
                    'water': 'WATERWAY', 'boat': 'WATERWAY', 'ferry': 'WATERWAY', 'ship': 'WATERWAY',
                    'rail': 'TRAIN', 'railway': 'TRAIN', 'metro': 'METRO', 'subway': 'METRO',
                    'semi': 'TRUCK', 'heavy': 'TRUCK', 'lorry': 'TRUCK',
                    'agro': 'TRACTOR', 'farm': 'TRACTOR'
                }};
                if (aliases[lower]) return aliases[lower];
                for (let k in aliases) {{
                    if (lower.indexOf(k) !== -1) return aliases[k];
                }}
                for (let k in this.configs) {{
                    if (k.toLowerCase().indexOf(lower) !== -1) return k;
                }}
                return 'CAR';
            }},

            getConfig: function(mode) {{
                const norm = this.normalizeMode(mode);
                return this.configs[norm] || this.configs['CAR'];
            }}
        }};

        // 2. PROCEDURAL 3D VEHICLE MODEL LOADER (Three.js Low-Poly Optimized)
        const VehicleModelLoader = {{
            materials: null,

            initMaterials: function() {{
                if (this.materials) return;
                this.materials = {{
                    carChassis: new THREE.MeshStandardMaterial({{ color: 0x0f3460, metalness: 0.82, roughness: 0.22 }}),
                    taxiChassis: new THREE.MeshStandardMaterial({{ color: 0xf59e0b, metalness: 0.75, roughness: 0.25 }}),
                    bikeChassis: new THREE.MeshStandardMaterial({{ color: 0x00f0ff, metalness: 0.88, roughness: 0.18 }}),
                    busChassis: new THREE.MeshStandardMaterial({{ color: 0x1e3a8a, metalness: 0.70, roughness: 0.30 }}),
                    truckChassis: new THREE.MeshStandardMaterial({{ color: 0x9a3412, metalness: 0.75, roughness: 0.35 }}),
                    tractorChassis: new THREE.MeshStandardMaterial({{ color: 0x16a34a, metalness: 0.65, roughness: 0.40 }}),
                    planeChassis: new THREE.MeshStandardMaterial({{ color: 0xf8fafc, metalness: 0.85, roughness: 0.15 }}),
                    boatChassis: new THREE.MeshStandardMaterial({{ color: 0x0284c7, metalness: 0.72, roughness: 0.28 }}),
                    trainChassis: new THREE.MeshStandardMaterial({{ color: 0x7c3aed, metalness: 0.80, roughness: 0.20 }}),
                    bicycleFrame: new THREE.MeshStandardMaterial({{ color: 0x10b981, metalness: 0.85, roughness: 0.20 }}),

                    rubberTire: new THREE.MeshStandardMaterial({{ color: 0x111827, roughness: 0.92 }}),
                    wheelRim: new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, metalness: 0.95, roughness: 0.15 }}),
                    chrome: new THREE.MeshStandardMaterial({{ color: 0xf8fafc, metalness: 0.98, roughness: 0.10 }}),
                    glassDark: new THREE.MeshStandardMaterial({{ color: 0x030712, roughness: 0.08, transparent: true, opacity: 0.82 }}),
                    glassCyan: new THREE.MeshStandardMaterial({{ color: 0x38bdf8, roughness: 0.05, transparent: true, opacity: 0.75 }}),
                    headlightGlow: new THREE.MeshBasicMaterial({{ color: 0x00f0ff }}),
                    taillightGlow: new THREE.MeshBasicMaterial({{ color: 0xef4444 }}),
                    indicatorAmber: new THREE.MeshBasicMaterial({{ color: 0xfbbf24 }}),
                    interiorWarm: new THREE.MeshBasicMaterial({{ color: 0xfef08a, transparent: true, opacity: 0.85 }}),
                    thrusterCyan: new THREE.MeshBasicMaterial({{ color: 0x00f0ff, transparent: true, opacity: 0.90 }})
                }};
            }},

            buildVehicle: function(mode, config) {{
                this.initMaterials();
                const norm = VehicleModeManager.normalizeMode(mode);
                if (norm === 'WALK') return null; // Pedestrian walk mode (no vehicle object)

                const root = new THREE.Group();
                root.name = 'vehicle_' + norm;
                const wheels = [];
                let steeringWheel = null;
                let driverSeat = null;
                const dynamicParts = {{}};

                const m = this.materials;

                if (norm === 'CAR' || norm === 'TAXI') {{
                    const isTaxi = (norm === 'TAXI');
                    const cMat = isTaxi ? m.taxiChassis : m.carChassis;

                    // Main Lower Chassis
                    const bodyGeo = new THREE.BoxGeometry(1.68, 0.48, 3.5);
                    const bodyMesh = new THREE.Mesh(bodyGeo, cMat);
                    bodyMesh.position.y = 0.38;
                    bodyMesh.castShadow = true;
                    root.add(bodyMesh);

                    // Front Bumper / Radiator Grill
                    const grill = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.28, 0.18), m.chrome);
                    grill.position.set(0, 0.32, 1.76);
                    root.add(grill);

                    // Aerodynamic Cabin / Greenhouse
                    const cabinGeo = new THREE.BoxGeometry(1.42, 0.52, 1.85);
                    const cabinMesh = new THREE.Mesh(cabinGeo, cMat);
                    cabinMesh.position.set(0, 0.82, -0.18);
                    cabinMesh.castShadow = true;
                    root.add(cabinMesh);

                    // Windshields (Front & Rear angled glass)
                    const frontWindshield = new THREE.Mesh(new THREE.PlaneGeometry(1.35, 0.58), m.glassDark);
                    frontWindshield.rotation.x = -Math.PI / 3.4;
                    frontWindshield.position.set(0, 0.82, 0.82);
                    root.add(frontWindshield);

                    const rearWindshield = new THREE.Mesh(new THREE.PlaneGeometry(1.35, 0.50), m.glassDark);
                    rearWindshield.rotation.x = Math.PI / 3.2;
                    rearWindshield.rotation.y = Math.PI;
                    rearWindshield.position.set(0, 0.82, -1.15);
                    root.add(rearWindshield);

                    // Driver's Seat
                    driverSeat = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.38, 0.44), m.rubberTire);
                    driverSeat.position.set(-0.32, 0.55, -0.15);
                    root.add(driverSeat);

                    // Steering Wheel
                    const swGroup = new THREE.Group();
                    swGroup.position.set(-0.32, 0.78, 0.24);
                    swGroup.rotation.x = -0.42;
                    const swRing = new THREE.Mesh(new THREE.TorusGeometry(0.14, 0.022, 8, 16), m.rubberTire);
                    swGroup.add(swRing);
                    root.add(swGroup);
                    steeringWheel = swGroup;

                    // Xenon Headlights & Taillights
                    const hlL = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.12, 0.08), m.headlightGlow);
                    hlL.position.set(-0.58, 0.42, 1.76);
                    const hlR = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.12, 0.08), m.headlightGlow);
                    hlR.position.set(0.58, 0.42, 1.76);
                    root.add(hlL); root.add(hlR);

                    const tlL = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.12, 0.08), m.taillightGlow);
                    tlL.position.set(-0.58, 0.44, -1.76);
                    const tlR = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.12, 0.08), m.taillightGlow);
                    tlR.position.set(0.58, 0.44, -1.76);
                    root.add(tlL); root.add(tlR);

                    // Headlight Forward Beam Illuminator
                    const carLight = new THREE.SpotLight(0x00f0ff, 1.8, 22, Math.PI / 6, 0.35);
                    carLight.position.set(0, 0.5, 1.8);
                    carLight.target.position.set(0, 0.2, 12);
                    root.add(carLight);
                    root.add(carLight.target);

                    // 4 Wheels (Tire + Chrome Rim)
                    const wheelPositions = [
                        [-0.88, 0.34, 1.15],
                        [0.88, 0.34, 1.15],
                        [-0.88, 0.34, -1.15],
                        [0.88, 0.34, -1.15]
                    ];
                    wheelPositions.forEach((pos, idx) => {{
                        const wGrp = new THREE.Group();
                        wGrp.position.set(pos[0], pos[1], pos[2]);
                        const tire = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 0.22, 18), m.rubberTire);
                        tire.rotation.z = Math.PI / 2;
                        const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.23, 12), m.wheelRim);
                        rim.rotation.z = Math.PI / 2;
                        wGrp.add(tire);
                        wGrp.add(rim);
                        root.add(wGrp);
                        wheels.push(wGrp);
                    }});

                    // For Taxi: Illuminated Rooftop Sign
                    if (isTaxi) {{
                        const taxiSign = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.14, 0.18), m.indicatorAmber);
                        taxiSign.position.set(0, 1.15, -0.15);
                        root.add(taxiSign);
                    }}

                }} else if (norm === 'BIKE') {{
                    // Motorcycle / Scooter
                    const cMat = m.bikeChassis;

                    // Sloped Main Chassis / Tank
                    const tankGeo = new THREE.BoxGeometry(0.36, 0.42, 1.6);
                    const tankMesh = new THREE.Mesh(tankGeo, cMat);
                    tankMesh.position.y = 0.58;
                    tankMesh.castShadow = true;
                    root.add(tankMesh);

                    // Engine Block & Chrome Exhaust Pipe
                    const engine = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.38, 0.55), m.chrome);
                    engine.position.set(0, 0.35, 0.05);
                    root.add(engine);

                    const exhaust = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.055, 1.35, 12), m.chrome);
                    exhaust.rotation.x = Math.PI / 2;
                    exhaust.position.set(0.24, 0.25, -0.45);
                    root.add(exhaust);

                    // Front Fork & Handlebars
                    const fork = new THREE.Group();
                    fork.position.set(0, 0.55, 0.75);
                    fork.rotation.x = -0.25;

                    const forkLegL = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.85, 8), m.chrome);
                    forkLegL.position.set(-0.12, -0.15, 0);
                    const forkLegR = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.85, 8), m.chrome);
                    forkLegR.position.set(0.12, -0.15, 0);
                    fork.add(forkLegL); fork.add(forkLegR);

                    const handlebars = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.72, 8), m.rubberTire);
                    handlebars.rotation.z = Math.PI / 2;
                    handlebars.position.set(0, 0.32, 0);
                    fork.add(handlebars);

                    const headlight = new THREE.Mesh(new THREE.SphereGeometry(0.11, 12, 12), m.headlightGlow);
                    headlight.position.set(0, 0.18, 0.15);
                    fork.add(headlight);

                    root.add(fork);
                    dynamicParts.fork = fork;
                    steeringWheel = fork;

                    // Ergonomic Saddle Seat
                    driverSeat = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.12, 0.52), m.rubberTire);
                    driverSeat.position.set(0, 0.65, -0.15);
                    root.add(driverSeat);

                    // Front & Rear Wheels
                    const fWheel = new THREE.Group();
                    fWheel.position.set(0, 0.38, 0.95);
                    const fTire = new THREE.Mesh(new THREE.CylinderGeometry(0.40, 0.40, 0.14, 18), m.rubberTire);
                    fTire.rotation.z = Math.PI / 2;
                    const fRim = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.26, 0.15, 12), m.wheelRim);
                    fRim.rotation.z = Math.PI / 2;
                    fWheel.add(fTire); fWheel.add(fRim);
                    root.add(fWheel);
                    wheels.push(fWheel);

                    const rWheel = new THREE.Group();
                    rWheel.position.set(0, 0.38, -0.85);
                    const rTire = new THREE.Mesh(new THREE.CylinderGeometry(0.40, 0.40, 0.18, 18), m.rubberTire);
                    rTire.rotation.z = Math.PI / 2;
                    const rRim = new THREE.Mesh(new THREE.CylinderGeometry(0.26, 0.26, 0.19, 12), m.wheelRim);
                    rRim.rotation.z = Math.PI / 2;
                    rWheel.add(rTire); rWheel.add(rRim);
                    root.add(rWheel);
                    wheels.push(rWheel);

                }} else if (norm === 'BICYCLE') {{
                    // Bicycle
                    const cMat = m.bicycleFrame;

                    // Diamond Frame Tubes
                    const frame = new THREE.Group();
                    const topTube = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.95, 8), cMat);
                    topTube.rotation.x = Math.PI / 2;
                    topTube.position.set(0, 0.72, 0);
                    frame.add(topTube);

                    const downTube = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.98, 8), cMat);
                    downTube.rotation.x = 0.75;
                    downTube.position.set(0, 0.52, 0.25);
                    frame.add(downTube);

                    const seatTube = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.65, 8), cMat);
                    seatTube.position.set(0, 0.55, -0.25);
                    frame.add(seatTube);
                    root.add(frame);

                    // Handlebars & Stem
                    const hbGroup = new THREE.Group();
                    hbGroup.position.set(0, 0.88, 0.45);
                    const hbBar = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.58, 8), m.chrome);
                    hbBar.rotation.z = Math.PI / 2;
                    hbGroup.add(hbBar);
                    root.add(hbGroup);
                    steeringWheel = hbGroup;

                    // Saddle
                    driverSeat = new THREE.Mesh(new THREE.BoxGeometry(0.20, 0.08, 0.32), m.rubberTire);
                    driverSeat.position.set(0, 0.82, -0.26);
                    root.add(driverSeat);

                    // Rotating Pedals & Crank
                    const crankGroup = new THREE.Group();
                    crankGroup.position.set(0, 0.28, -0.15);
                    const crankAxle = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.32, 8), m.chrome);
                    crankAxle.rotation.z = Math.PI / 2;
                    crankGroup.add(crankAxle);
                    root.add(crankGroup);
                    dynamicParts.crank = crankGroup;

                    // Spoked Thin Wheels
                    const wheelPositions = [[0, 0.42, 0.75], [0, 0.42, -0.75]];
                    wheelPositions.forEach(pos => {{
                        const wGrp = new THREE.Group();
                        wGrp.position.set(pos[0], pos[1], pos[2]);
                        const tire = new THREE.Mesh(new THREE.TorusGeometry(0.42, 0.035, 8, 24), m.rubberTire);
                        const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.12, 10), m.chrome);
                        hub.rotation.z = Math.PI / 2;
                        wGrp.add(tire); wGrp.add(hub);
                        root.add(wGrp);
                        wheels.push(wGrp);
                    }});

                }} else if (norm === 'BUS') {{
                    // Transit City Bus
                    const cMat = m.busChassis;

                    // Main Box Chassis
                    const bodyGeo = new THREE.BoxGeometry(2.35, 2.15, 7.8);
                    const bodyMesh = new THREE.Mesh(bodyGeo, cMat);
                    bodyMesh.position.y = 1.35;
                    bodyMesh.castShadow = true;
                    root.add(bodyMesh);

                    // Panoramic Front Windshield
                    const windshield = new THREE.Mesh(new THREE.PlaneGeometry(2.1, 1.15), m.glassDark);
                    windshield.position.set(0, 1.75, 3.91);
                    root.add(windshield);

                    // Glowing Route Marquee ("NEXROUTE EXPRESS")
                    const marquee = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.26, 0.08), m.headlightGlow);
                    marquee.position.set(0, 2.32, 3.92);
                    root.add(marquee);

                    // Side Passenger Windows (Strip)
                    const sideL = new THREE.Mesh(new THREE.PlaneGeometry(6.5, 0.85), m.glassDark);
                    sideL.rotation.y = -Math.PI / 2;
                    sideL.position.set(-1.18, 1.65, -0.2);
                    const sideR = new THREE.Mesh(new THREE.PlaneGeometry(6.5, 0.85), m.glassDark);
                    sideR.rotation.y = Math.PI / 2;
                    sideR.position.set(1.18, 1.65, -0.2);
                    root.add(sideL); root.add(sideR);

                    // Interior Passenger Lighting
                    const busLight = new THREE.PointLight(0xfef08a, 0.9, 10.0);
                    busLight.position.set(0, 2.0, 0);
                    root.add(busLight);

                    // Elevated Driver Seat & Steering Wheel
                    driverSeat = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.4, 0.5), m.rubberTire);
                    driverSeat.position.set(-0.46, 1.05, 2.4);
                    root.add(driverSeat);

                    const busSW = new THREE.Group();
                    busSW.position.set(-0.46, 1.45, 3.1);
                    busSW.rotation.x = -0.55;
                    const swRing = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.028, 8, 16), m.rubberTire);
                    busSW.add(swRing);
                    root.add(busSW);
                    steeringWheel = busSW;

                    // 6 Heavy-duty Wheels
                    const wheelZList = [2.2, -1.6, -2.8];
                    wheelZList.forEach(z => {{
                        [-1.15, 1.15].forEach(x => {{
                            const wGrp = new THREE.Group();
                            wGrp.position.set(x, 0.45, z);
                            const tire = new THREE.Mesh(new THREE.CylinderGeometry(0.46, 0.46, 0.32, 18), m.rubberTire);
                            tire.rotation.z = Math.PI / 2;
                            const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.28, 0.33, 12), m.wheelRim);
                            rim.rotation.z = Math.PI / 2;
                            wGrp.add(tire); wGrp.add(rim);
                            root.add(wGrp);
                            wheels.push(wGrp);
                        }});
                    }});

                }} else if (norm === 'TRUCK') {{
                    // Semi-Truck & Cargo Container
                    const cMat = m.truckChassis;

                    // Heavy Cab
                    const cab = new THREE.Mesh(new THREE.BoxGeometry(2.25, 2.25, 2.4), cMat);
                    cab.position.set(0, 1.45, 1.6);
                    cab.castShadow = true;
                    root.add(cab);

                    // Giant Chrome Front Grill
                    const grill = new THREE.Mesh(new THREE.BoxGeometry(1.8, 1.15, 0.22), m.chrome);
                    grill.position.set(0, 0.95, 2.82);
                    root.add(grill);

                    // Vertical Chrome Twin Exhaust Stacks
                    [-1.12, 1.12].forEach(x => {{
                        const stack = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.075, 2.8, 12), m.chrome);
                        stack.position.set(x, 2.4, 0.45);
                        root.add(stack);
                    }});

                    // Cargo Trailer Box
                    const trailer = new THREE.Mesh(new THREE.BoxGeometry(2.35, 2.45, 5.2), m.materials?.busChassis || cMat);
                    trailer.position.set(0, 1.65, -2.4);
                    trailer.castShadow = true;
                    root.add(trailer);

                    driverSeat = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.4, 0.5), m.rubberTire);
                    driverSeat.position.set(-0.48, 1.35, 1.4);
                    root.add(driverSeat);

                    // 6 Truck Wheels
                    [2.1, -1.8, -3.4].forEach(z => {{
                        [-1.15, 1.15].forEach(x => {{
                            const wGrp = new THREE.Group();
                            wGrp.position.set(x, 0.50, z);
                            const tire = new THREE.Mesh(new THREE.CylinderGeometry(0.50, 0.50, 0.35, 18), m.rubberTire);
                            tire.rotation.z = Math.PI / 2;
                            const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.30, 0.30, 0.36, 12), m.wheelRim);
                            rim.rotation.z = Math.PI / 2;
                            wGrp.add(tire); wGrp.add(rim);
                            root.add(wGrp);
                            wheels.push(wGrp);
                        }});
                    }});

                }} else if (norm === 'TRACTOR') {{
                    // Agricultural Tractor
                    const cMat = m.tractorChassis;

                    // Engine Hood
                    const hood = new THREE.Mesh(new THREE.BoxGeometry(1.15, 0.85, 1.8), cMat);
                    hood.position.set(0, 0.95, 0.45);
                    hood.castShadow = true;
                    root.add(hood);

                    // Vertical Exhaust Pipe
                    const exhaust = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.055, 1.4, 8), m.chrome);
                    exhaust.position.set(0.35, 1.85, 0.85);
                    root.add(exhaust);

                    // Open Driver Platform & Seat
                    driverSeat = new THREE.Mesh(new THREE.BoxGeometry(0.48, 0.15, 0.48), m.rubberTire);
                    driverSeat.position.set(0, 1.15, -0.45);
                    root.add(driverSeat);

                    const trSW = new THREE.Group();
                    trSW.position.set(0, 1.45, 0.05);
                    trSW.rotation.x = -0.65;
                    const swRing = new THREE.Mesh(new THREE.TorusGeometry(0.18, 0.024, 8, 16), m.rubberTire);
                    trSW.add(swRing);
                    root.add(trSW);
                    steeringWheel = trSW;

                    // Big Rear Lug Tires
                    [-0.82, 0.82].forEach(x => {{
                        const wGrp = new THREE.Group();
                        wGrp.position.set(x, 0.85, -0.65);
                        const tire = new THREE.Mesh(new THREE.CylinderGeometry(0.88, 0.88, 0.44, 18), m.rubberTire);
                        tire.rotation.z = Math.PI / 2;
                        const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.50, 0.50, 0.45, 12), m.indicatorAmber);
                        rim.rotation.z = Math.PI / 2;
                        wGrp.add(tire); wGrp.add(rim);
                        root.add(wGrp);
                        wheels.push(wGrp);
                    }});

                    // Smaller Front Wheels
                    [-0.65, 0.65].forEach(x => {{
                        const wGrp = new THREE.Group();
                        wGrp.position.set(x, 0.46, 1.05);
                        const tire = new THREE.Mesh(new THREE.CylinderGeometry(0.46, 0.46, 0.25, 16), m.rubberTire);
                        tire.rotation.z = Math.PI / 2;
                        const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.28, 0.26, 12), m.indicatorAmber);
                        rim.rotation.z = Math.PI / 2;
                        wGrp.add(tire); wGrp.add(rim);
                        root.add(wGrp);
                        wheels.push(wGrp);
                    }});

                }} else if (norm === 'FLIGHT') {{
                    // Jet Airplane
                    const cMat = m.planeChassis;

                    // Fuselage
                    const fuselage = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.72, 4.8, 16), cMat);
                    fuselage.rotation.x = Math.PI / 2;
                    fuselage.position.y = 0.55;
                    fuselage.castShadow = true;
                    root.add(fuselage);

                    // Swept Main Wings
                    const wings = new THREE.Mesh(new THREE.BoxGeometry(6.6, 0.08, 1.25), cMat);
                    wings.position.set(0, 0.55, 0.15);
                    root.add(wings);

                    // Winglets & Strobes
                    const strobL = new THREE.Mesh(new THREE.SphereGeometry(0.08, 8, 8), m.taillightGlow);
                    strobL.position.set(-3.3, 0.65, 0.15);
                    const strobR = new THREE.Mesh(new THREE.SphereGeometry(0.08, 8, 8), m.headlightGlow);
                    strobR.position.set(3.3, 0.65, 0.15);
                    root.add(strobL); root.add(strobR);

                    // T-Tail Fin
                    const tailFin = new THREE.Mesh(new THREE.BoxGeometry(0.08, 1.15, 0.85), cMat);
                    tailFin.position.set(0, 1.35, -2.1);
                    root.add(tailFin);

                    // Dual Jet Turbofans with Cyan Thrust Glow
                    const jetL = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.95, 12), m.chrome);
                    jetL.rotation.x = Math.PI / 2;
                    jetL.position.set(-1.25, 0.28, -0.15);
                    const thrusterL = new THREE.Mesh(new THREE.ConeGeometry(0.20, 0.65, 12), m.thrusterCyan);
                    thrusterL.rotation.x = -Math.PI / 2;
                    thrusterL.position.set(0, -0.55, 0);
                    jetL.add(thrusterL);

                    const jetR = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.95, 12), m.chrome);
                    jetR.rotation.x = Math.PI / 2;
                    jetR.position.set(1.25, 0.28, -0.15);
                    const thrusterR = new THREE.Mesh(new THREE.ConeGeometry(0.20, 0.65, 12), m.thrusterCyan);
                    thrusterR.rotation.x = -Math.PI / 2;
                    thrusterR.position.set(0, -0.55, 0);
                    jetR.add(thrusterR);

                    root.add(jetL); root.add(jetR);
                    dynamicParts.thrusters = [thrusterL, thrusterR];

                    // Cockpit Canopy
                    const canopy = new THREE.Mesh(new THREE.SphereGeometry(0.45, 16, 12), m.glassCyan);
                    canopy.scale.set(1, 0.6, 1.6);
                    canopy.position.set(0, 0.95, 1.1);
                    root.add(canopy);

                    driverSeat = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.3, 0.4), m.rubberTire);
                    driverSeat.position.set(0, 0.58, 0.95);
                    root.add(driverSeat);

                }} else if (norm === 'WATERWAY') {{
                    // Cruise / Ferry Boat
                    const cMat = m.boatChassis;

                    // Pointed Hull
                    const hull = new THREE.Mesh(new THREE.BoxGeometry(2.1, 0.85, 4.8), cMat);
                    hull.position.y = 0.42;
                    hull.castShadow = true;
                    root.add(hull);

                    const bow = new THREE.Mesh(new THREE.ConeGeometry(1.05, 1.25, 12), cMat);
                    bow.rotation.x = Math.PI / 2;
                    bow.position.set(0, 0.42, 2.7);
                    root.add(bow);

                    // Upper Bridge Deck & Wheelhouse
                    const bridge = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.85, 1.9), m.planeChassis);
                    bridge.position.set(0, 1.15, 0.35);
                    root.add(bridge);

                    // Radar Scanner
                    const radarMast = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.75, 8), m.chrome);
                    radarMast.position.set(0, 1.85, 0.35);
                    const radarBar = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.08, 0.08), m.indicatorAmber);
                    radarBar.position.y = 0.35;
                    radarMast.add(radarBar);
                    root.add(radarMast);
                    dynamicParts.radar = radarBar;

                    driverSeat = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.3, 0.4), m.rubberTire);
                    driverSeat.position.set(0, 1.25, 0.85);
                    root.add(driverSeat);

                }} else if (norm === 'TRAIN' || norm === 'METRO') {{
                    // High-speed Train / Metro Car
                    const cMat = (norm === 'METRO') ? m.trainChassis : m.trainChassis;

                    // Streamlined Car
                    const trainCar = new THREE.Mesh(new THREE.BoxGeometry(2.1, 2.0, 8.2), cMat);
                    trainCar.position.y = 1.35;
                    trainCar.castShadow = true;
                    root.add(trainCar);

                    // Aerodynamic Sloped Nose
                    const nose = new THREE.Mesh(new THREE.ConeGeometry(1.05, 1.6, 16), cMat);
                    nose.rotation.x = Math.PI / 2;
                    nose.position.set(0, 1.1, 4.6);
                    root.add(nose);

                    // Roof Diamond Pantograph
                    const pantograph = new THREE.Mesh(new THREE.TorusGeometry(0.45, 0.03, 6, 4), m.chrome);
                    pantograph.rotation.x = Math.PI / 2;
                    pantograph.position.set(0, 2.55, -1.8);
                    root.add(pantograph);

                    driverSeat = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.35, 0.45), m.rubberTire);
                    driverSeat.position.set(0, 1.15, 3.4);
                    root.add(driverSeat);

                    // 8 Bogie Wheels
                    [2.6, 1.6, -2.2, -3.2].forEach(z => {{
                        [-0.98, 0.98].forEach(x => {{
                            const wGrp = new THREE.Group();
                            wGrp.position.set(x, 0.35, z);
                            const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 0.16, 16), m.wheelRim);
                            wheel.rotation.z = Math.PI / 2;
                            wGrp.add(wheel);
                            root.add(wGrp);
                            wheels.push(wGrp);
                        }});
                    }});
                }}

                return {{
                    group: root,
                    wheels: wheels,
                    steeringWheel: steeringWheel,
                    driverSeat: driverSeat,
                    dynamicParts: dynamicParts,
                    mode: norm,
                    config: config
                }};
            }}
        }};

        // 3. VIRTUAL GUIDE SKELETAL POSE CONTROLLER
        const VirtualGuidePoseController = {{
            applyPose: function(auraRoot, limbs, mode, elapsed, turnAngle, speedKmh) {{
                if (!auraRoot || !limbs) return;
                const norm = VehicleModeManager.normalizeMode(mode);
                const cfg = VehicleModeManager.getConfig(norm);

                const {{ head, torso, armL, armR, legL, legR, stick, ring }} = limbs;
                const spd = Math.max(0.1, (speedKmh || cfg.default_speed_kmh) / 10.0);

                if (norm === 'WALK') {{
                    // Natural Bipedal Walking Stride
                    auraRoot.scale.setScalar(1.0);
                    torso.rotation.x = 0;
                    if (ring) ring.visible = true;
                    if (stick) stick.visible = true;

                    const stride = Math.sin(elapsed * 5.5 * spd) * 0.52;
                    legL.rotation.x = stride;
                    legR.rotation.x = -stride;
                    armL.rotation.x = -stride * 0.6;
                    armR.rotation.x = stride * 0.6;
                    armR.rotation.z = 0.15;
                    auraRoot.position.y = Math.abs(Math.sin(elapsed * 5.5 * spd)) * 0.06;
                    head.rotation.y = Math.sin(elapsed * 2.5) * 0.1;

                }} else if (norm === 'CAR' || norm === 'TAXI') {{
                    // Seated in Driver's Seat
                    auraRoot.scale.setScalar(cfg.guide_scale || 0.68);
                    if (ring) ring.visible = false;
                    if (stick) stick.visible = false;

                    // Sitting posture
                    torso.rotation.x = 0.08;
                    legL.rotation.x = -1.25; // Knees bent forward
                    legR.rotation.x = -1.25;
                    legL.rotation.z = -0.15;
                    legR.rotation.z = 0.15;

                    // Hands holding steering wheel
                    armL.rotation.x = -0.85;
                    armR.rotation.x = -0.85;
                    armL.rotation.z = 0.35;
                    armR.rotation.z = -0.35;

                    // Head tracking turn angle
                    head.rotation.y = turnAngle * 0.6;
                    auraRoot.position.y = (cfg.seat_offset ? cfg.seat_offset[1] : 0.30) + Math.sin(elapsed * 8) * 0.015;

                }} else if (norm === 'BIKE') {{
                    // Motorcycle Riding Posture (Aggressive aerodynamic forward lean)
                    auraRoot.scale.setScalar(cfg.guide_scale || 0.72);
                    if (ring) ring.visible = false;
                    if (stick) stick.visible = false;

                    torso.rotation.x = 0.32; // Lean forward over tank
                    legL.rotation.x = -1.15;
                    legR.rotation.x = -1.15;
                    legL.rotation.z = -0.22;
                    legR.rotation.z = 0.22;

                    // Arms extended to clip-on handlebars
                    armL.rotation.x = -0.92;
                    armR.rotation.x = -0.92;
                    armL.rotation.z = 0.25;
                    armR.rotation.z = -0.25;

                    head.rotation.x = -0.25; // Look up toward road
                    head.rotation.y = turnAngle * 0.8;
                    auraRoot.position.y = (cfg.seat_offset ? cfg.seat_offset[1] : 0.48) + Math.sin(elapsed * 12) * 0.012;

                }} else if (norm === 'BICYCLE') {{
                    // Cycling Posture with Alternate Pedaling Action
                    auraRoot.scale.setScalar(cfg.guide_scale || 0.75);
                    if (ring) ring.visible = false;
                    if (stick) stick.visible = false;

                    torso.rotation.x = 0.22;
                    const pedalPhase = elapsed * 6.5 * spd;
                    legL.rotation.x = Math.sin(pedalPhase) * 0.55 - 0.75;
                    legR.rotation.x = -Math.sin(pedalPhase) * 0.55 - 0.75;

                    armL.rotation.x = -0.78;
                    armR.rotation.x = -0.78;
                    armL.rotation.z = 0.20;
                    armR.rotation.z = -0.20;

                    head.rotation.y = turnAngle * 0.5;
                    auraRoot.position.y = (cfg.seat_offset ? cfg.seat_offset[1] : 0.60) + Math.abs(Math.sin(pedalPhase)) * 0.025;

                }} else if (norm === 'BUS' || norm === 'TRUCK' || norm === 'TRACTOR') {{
                    // Elevated Commercial Driver Posture
                    auraRoot.scale.setScalar(cfg.guide_scale || 0.62);
                    if (ring) ring.visible = false;
                    if (stick) stick.visible = false;

                    torso.rotation.x = 0.05;
                    legL.rotation.x = -1.35;
                    legR.rotation.x = -1.35;

                    armL.rotation.x = -0.90;
                    armR.rotation.x = -0.90;
                    head.rotation.y = turnAngle * 0.45;
                    auraRoot.position.y = (cfg.seat_offset ? cfg.seat_offset[1] : 0.85) + Math.sin(elapsed * 7) * 0.018;

                }} else if (norm === 'FLIGHT') {{
                    // Aircraft Pilot Posture
                    auraRoot.scale.setScalar(cfg.guide_scale || 0.58);
                    if (ring) ring.visible = false;
                    if (stick) stick.visible = false;

                    torso.rotation.x = 0.12;
                    legL.rotation.x = -1.2;
                    legR.rotation.x = -1.2;

                    armL.rotation.x = -0.75;
                    armR.rotation.x = -0.75;
                    head.rotation.y = turnAngle * 0.5;
                    auraRoot.position.y = (cfg.seat_offset ? cfg.seat_offset[1] : 0.28);

                }} else if (norm === 'WATERWAY') {{
                    // Marine Vessel Captain Posture
                    auraRoot.scale.setScalar(cfg.guide_scale || 0.62);
                    if (ring) ring.visible = false;
                    if (stick) stick.visible = true; // Guide holds nautical beacon

                    torso.rotation.x = 0;
                    legL.rotation.x = 0;
                    legR.rotation.x = 0;

                    armL.rotation.x = 0.1;
                    armR.rotation.x = -0.65;
                    head.rotation.y = turnAngle * 0.35;
                    auraRoot.position.y = (cfg.seat_offset ? cfg.seat_offset[1] : 0.88);

                }} else {{
                    // Train / Rail Operator Posture
                    auraRoot.scale.setScalar(cfg.guide_scale || 0.62);
                    if (ring) ring.visible = false;
                    if (stick) stick.visible = false;

                    torso.rotation.x = 0.08;
                    legL.rotation.x = -1.25;
                    legR.rotation.x = -1.25;

                    armL.rotation.x = -0.80;
                    armR.rotation.x = -0.80;
                    head.rotation.y = turnAngle * 0.4;
                    auraRoot.position.y = (cfg.seat_offset ? cfg.seat_offset[1] : 0.72);
                }}
            }}
        }};

        // 4. VEHICLE CONTROLLER & KINEMATICS SYNCHRONIZATION
        function VehicleController(scene, auraRoot, limbs) {{
            this.scene = scene;
            this.auraRoot = auraRoot;
            this.limbs = limbs;
            this.currentMode = null;
            this.activeVehicle = null;
            this.wheelSpinAngle = 0;

            this.setMode = function(newMode) {{
                const norm = VehicleModeManager.normalizeMode(newMode);
                if (this.currentMode === norm && this.activeVehicle) return;

                // 1. Remove previous vehicle from scene
                if (this.activeVehicle && this.activeVehicle.group) {{
                    this.scene.remove(this.activeVehicle.group);
                    this.activeVehicle = null;
                }}

                this.currentMode = norm;
                const config = VehicleModeManager.getConfig(norm);

                // 2. Build and attach new vehicle
                const vObj = VehicleModelLoader.buildVehicle(norm, config);
                if (vObj) {{
                    this.activeVehicle = vObj;
                    this.scene.add(vObj.group);

                    // Position guide relative to vehicle seat
                    const seat = config.seat_offset || [0, 0, 0];
                    this.auraRoot.position.set(seat[0], seat[1], seat[2]);
                    vObj.group.add(this.auraRoot);
                }} else {{
                    // Pedestrian mode: guide attached directly to scene root
                    this.auraRoot.position.set(0, 0, 0);
                    this.scene.add(this.auraRoot);
                }}
            }};

            this.updateKinematics = function(elapsed, speedKmh, turnAngle, isArrived) {{
                const norm = this.currentMode || 'CAR';
                const config = VehicleModeManager.getConfig(norm);
                const spd = (speedKmh !== undefined && speedKmh !== null) ? speedKmh : config.default_speed_kmh;

                // 1. Update Guide Skeletal Pose
                VirtualGuidePoseController.applyPose(this.auraRoot, this.limbs, norm, elapsed, turnAngle, spd);

                if (!this.activeVehicle) return;

                const v = this.activeVehicle;
                const rad = config.wheel_radius || 0.35;
                const angularSpeed = (spd / 3.6) / rad;
                this.wheelSpinAngle += angularSpeed * 0.016;

                // 2. Spin Wheels
                if (v.wheels && v.wheels.length > 0) {{
                    v.wheels.forEach(w => {{
                        w.rotation.x = this.wheelSpinAngle;
                    }});
                }}

                // 3. Turn Steering Wheel / Front Fork
                if (v.steeringWheel) {{
                    if (norm === 'BIKE' || norm === 'BICYCLE') {{
                        v.steeringWheel.rotation.y = turnAngle * 0.45;
                    }} else {{
                        v.steeringWheel.rotation.z = -turnAngle * 1.8;
                    }}
                }}

                // 4. Vehicle Body Banking & Tilt into Curves
                if (norm === 'BIKE' || norm === 'BICYCLE') {{
                    v.group.rotation.z = -turnAngle * 0.35; // Bank into turn
                    v.group.rotation.y = turnAngle * 0.25;
                }} else if (norm === 'FLIGHT') {{
                    v.group.rotation.z = -turnAngle * 0.55; // Wing bank
                    v.group.rotation.x = (spd > 150 ? -0.12 : 0); // Slight pitch up
                    v.group.position.y = config.flight_altitude || 7.5;
                }} else if (norm === 'WATERWAY') {{
                    v.group.rotation.z = Math.sin(elapsed * 2.5) * 0.035; // Ship roll
                    v.group.rotation.x = Math.sin(elapsed * 1.8) * 0.025; // Ship pitch
                }} else {{
                    v.group.rotation.z = -turnAngle * 0.08; // Subtle chassis roll
                    v.group.rotation.y = turnAngle * 0.15;
                }}

                // 5. Dynamic Parts (Crank, Radar, Thrusters)
                if (v.dynamicParts) {{
                    if (v.dynamicParts.crank) {{
                        v.dynamicParts.crank.rotation.x = this.wheelSpinAngle * 0.6;
                    }}
                    if (v.dynamicParts.radar) {{
                        v.dynamicParts.radar.rotation.y = elapsed * 3.5;
                    }}
                    if (v.dynamicParts.thrusters) {{
                        v.dynamicParts.thrusters.forEach(th => {{
                            th.scale.y = 0.85 + Math.sin(elapsed * 20) * 0.25;
                        }});
                    }}
                }}
            }};
        }}
        """

