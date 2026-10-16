# Auto-generated comprehensive Vignan University 3D campus graph containing ALL 97 tour dropdown locations
import math
from typing import Dict, List, Tuple, Optional

class CampusNode:
    def __init__(self, node_id: str, name: str, section: str, block: str, floor: int, x: float, y: float, z: float, node_type: str, capacity: int = 50, nav_id: str = "", pano_id: str = "", is_accessible: Optional[bool] = None, is_elevator: bool = False):
        self.node_id = node_id
        self.name = name
        self.section = section
        self.block = block
        self.floor = floor
        self.x = x
        self.y = y
        self.z = z
        self.node_type = node_type
        self.capacity = capacity
        self.nav_id = nav_id
        self.pano_id = pano_id
        self.is_elevator = is_elevator
        
        # Stair detection
        self.is_stair = (node_type == "stair" or "STAIR" in node_id or "Stair" in name)
        
        # Accessibility flag (wheelchair accessible): Stairs are NOT accessible
        if is_accessible is not None:
            self.is_accessible = is_accessible
        else:
            self.is_accessible = not self.is_stair

        # Average movement speed (m/s): 1.2 on flat, 0.7 on stairs
        self.base_speed_mps = 0.7 if self.is_stair else 1.2

    def __getattr__(self, name):
        if name == 'section':
            return getattr(self, 'block', 'Vignan Campus')
        if name == 'block':
            return getattr(self, 'section', 'Vignan Campus')
        raise AttributeError(f"'CampusNode' object has no attribute '{name}'")

    def distance_to(self, other: "CampusNode") -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        dz = (self.z - other.z) * 1.5
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def travel_time_to(self, other: "CampusNode") -> float:
        """Estimated transit duration in seconds between two nodes."""
        dist = self.distance_to(other)
        avg_speed = (self.base_speed_mps + other.base_speed_mps) / 2.0
        return dist / max(avg_speed, 0.1)

    def to_dict(self):
        return {
            "node_id": self.node_id,
            "name": self.name,
            "section": self.section,
            "block": self.block,
            "floor": self.floor,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "type": self.node_type,
            "capacity": self.capacity,
            "nav_id": self.nav_id,
            "pano_id": self.pano_id,
            "is_accessible": self.is_accessible,
            "is_stair": self.is_stair,
            "is_elevator": self.is_elevator
        }

def build_campus_building() -> Tuple[Dict[str, CampusNode], List[Tuple[str, str, float]]]:
    nodes: Dict[str, CampusNode] = {}

    nodes["VIG_FOUN_VIGNAN_CAMPUS_VIEW"] = CampusNode("VIG_FOUN_VIGNAN_CAMPUS_VIEW", "Vignan Campus view", "About Vignan Foundation", "Vignan Foundation Admin Block", 0, 23.0, 35.0, 0.0, "exit", nav_id="SEID00000002887")
    nodes["VIG_FOUN_CHAIRMAN_S_ROOM"] = CampusNode("VIG_FOUN_CHAIRMAN_S_ROOM", "Chairman's Room", "About Vignan Foundation", "Vignan Foundation Admin Block", 0, 23.5, 38.5, 0.0, "room", nav_id="SEID00000002777")
    nodes["VIG_FOUN_VICE_CHAIRMAN_S_ROOM"] = CampusNode("VIG_FOUN_VICE_CHAIRMAN_S_ROOM", "Vice Chairman's Room", "About Vignan Foundation", "Vignan Foundation Admin Block", 0, 20.0, 42.0, 0.0, "room", nav_id="SEID00000002778")
    nodes["VIG_FOUN_CHANCELLOR_S_ROOM"] = CampusNode("VIG_FOUN_CHANCELLOR_S_ROOM", "Chancellor's Room", "About Vignan Foundation", "Vignan Foundation Admin Block", 0, 17.9, 37.1, 0.0, "room", nav_id="SEID00000002779")
    nodes["VIG_FOUN_VICE_CHANCELLOR_S_ROOM"] = CampusNode("VIG_FOUN_VICE_CHANCELLOR_S_ROOM", "Vice Chancellor's Room", "About Vignan Foundation", "Vignan Foundation Admin Block", 0, 15.0, 35.0, 0.0, "room", nav_id="SEID00000002780")
    nodes["VIG_FOUN_REGISTRAR_S_ROOM"] = CampusNode("VIG_FOUN_REGISTRAR_S_ROOM", "Registrar's Room", "About Vignan Foundation", "Vignan Foundation Admin Block", 0, 15.1, 30.1, 0.0, "room", nav_id="SEID00000002781")
    nodes["VIG_FOUN_DEAN_S_ROOM"] = CampusNode("VIG_FOUN_DEAN_S_ROOM", "Dean's Room", "About Vignan Foundation", "Vignan Foundation Admin Block", 0, 20.0, 32.0, 0.0, "room", nav_id="SEID00000002782")
    nodes["VIG_FOUN_BOARD_ROOM"] = CampusNode("VIG_FOUN_BOARD_ROOM", "Board Room", "About Vignan Foundation", "Vignan Foundation Admin Block", 0, 23.5, 31.5, 0.0, "room", nav_id="SEID00000002866")
    nodes["VIG_LIBR_LIBRARY_BLOCK"] = CampusNode("VIG_LIBR_LIBRARY_BLOCK", "Library Block", "NTR Vignan Library", "NTR Vignan Library Block", 0, 23.0, 78.0, 0.0, "room", nav_id="SEID00000002784")
    nodes["VIG_LIBR_LIBRARY_GROUND_FLOOR"] = CampusNode("VIG_LIBR_LIBRARY_GROUND_FLOOR", "Library Ground Floor", "NTR Vignan Library", "NTR Vignan Library Block", 0, 23.5, 81.5, 0.0, "room", nav_id="SEID00000002785")
    nodes["VIG_LIBR_LIBRARY_FIRST_FLOOR"] = CampusNode("VIG_LIBR_LIBRARY_FIRST_FLOOR", "Library First Floor", "NTR Vignan Library", "NTR Vignan Library Block", 1, 20.0, 85.0, 4.0, "room", nav_id="SEID00000002786")
    nodes["VIG_LIBR_GENERAL_REFERENCE_SECTI"] = CampusNode("VIG_LIBR_GENERAL_REFERENCE_SECTI", "General Reference Section", "NTR Vignan Library", "NTR Vignan Library Block", 0, 17.9, 80.1, 0.0, "room", nav_id="SEID00000002910")
    nodes["VIG_LIBR_CIVIL_SERVICES_ASPIRANT"] = CampusNode("VIG_LIBR_CIVIL_SERVICES_ASPIRANT", "Civil Services Aspirants", "NTR Vignan Library", "NTR Vignan Library Block", 1, 15.0, 78.0, 4.0, "room", nav_id="SEID00000002911")
    nodes["VIG_LIBR_VIDEO_CONFERENCE_HALL"] = CampusNode("VIG_LIBR_VIDEO_CONFERENCE_HALL", "Video Conference Hall", "NTR Vignan Library", "NTR Vignan Library Block", 1, 15.1, 73.1, 4.0, "room", nav_id="SEID00000002912")
    nodes["VIG_LIBR_RESEARCH_CARRELS"] = CampusNode("VIG_LIBR_RESEARCH_CARRELS", "Research Carrels", "NTR Vignan Library", "NTR Vignan Library Block", 1, 20.0, 75.0, 4.0, "room", nav_id="SEID00000002943")
    nodes["VIG_LIBR_DIGITAL_LIBRARY"] = CampusNode("VIG_LIBR_DIGITAL_LIBRARY", "Digital Library", "NTR Vignan Library", "NTR Vignan Library Block", 0, 23.5, 74.5, 0.0, "room", nav_id="SEID00000002944")
    nodes["VIG_TRAI_ADMISSION_DEPARTMENT"] = CampusNode("VIG_TRAI_ADMISSION_DEPARTMENT", "Admission Department", "Dept of Admission / Training", "Admission & Training Block", 0, 33.0, 35.0, 0.0, "room", nav_id="SEID00000002791")
    nodes["VIG_TRAI_TRAINING_AND_PLACEMENT"] = CampusNode("VIG_TRAI_TRAINING_AND_PLACEMENT", "Training and Placement", "Dept of Admission / Training", "Admission & Training Block", 0, 30.0, 40.0, 0.0, "room", nav_id="SEID00000002792")
    nodes["VIG_TRAI_INTERVIEW_PANELS"] = CampusNode("VIG_TRAI_INTERVIEW_PANELS", "Interview Panels", "Dept of Admission / Training", "Admission & Training Block", 0, 23.0, 35.0, 0.0, "room", nav_id="SEID00000002793")
    nodes["VIG_TRAI_DEAN_ADMISSIONS"] = CampusNode("VIG_TRAI_DEAN_ADMISSIONS", "Dean Admissions", "Dept of Admission / Training", "Admission & Training Block", 0, 30.0, 32.0, 0.0, "room", nav_id="SEID00000002794")
    nodes["VIG_LABO_ENGLISH_LANGUAGE_LAB"] = CampusNode("VIG_LABO_ENGLISH_LANGUAGE_LAB", "English Language Lab", "Laboratories", "Central Academic Labs", 0, 38.0, 70.0, 0.0, "lab", nav_id="SEID00000002858")
    nodes["VIG_LABO_SCIENCE_HUMANITIES_RESE"] = CampusNode("VIG_LABO_SCIENCE_HUMANITIES_RESE", "Science & Humanities Research Lab", "Laboratories", "Central Academic Labs", 0, 32.5, 74.3, 0.0, "lab", nav_id="SEID00000002856")
    nodes["VIG_LABO_MAT_LAB"] = CampusNode("VIG_LABO_MAT_LAB", "MAT Lab", "Laboratories", "Central Academic Labs", 0, 31.5, 63.9, 0.0, "lab", nav_id="SEID00000002859")
    nodes["VIG_ENGI_ADVANCED_PROGRAMMING_NE"] = CampusNode("VIG_ENGI_ADVANCED_PROGRAMMING_NE", "Advanced Programming & Networking Lab", "Dept of Computer Science Engineering", "CSE Department Block", 0, 83.0, 60.0, 0.0, "lab", nav_id="SEID00000002796")
    nodes["VIG_ENGI_OPEN_SOURCE_DEVELOPMENT"] = CampusNode("VIG_ENGI_OPEN_SOURCE_DEVELOPMENT", "Open Source Development Lab", "Dept of Computer Science Engineering", "CSE Department Block", 0, 80.0, 65.0, 0.0, "lab", nav_id="SEID00000002797")
    nodes["VIG_ENGI_INFORMATION_TECHNOLOGY_"] = CampusNode("VIG_ENGI_INFORMATION_TECHNOLOGY_", "Information Technology Lab", "Dept of Computer Science Engineering", "CSE Department Block", 0, 73.0, 60.0, 0.0, "lab", nav_id="SEID00000002798")
    nodes["VIG_ENGI_CSE_DEPT_LIBRARY"] = CampusNode("VIG_ENGI_CSE_DEPT_LIBRARY", "CSE Dept Library", "Dept of Computer Science Engineering", "CSE Department Block", 0, 80.0, 57.0, 0.0, "lab", nav_id="SEID00000002799")
    nodes["VIG_ENGI_ELECTRICAL_MACHINES_LAB"] = CampusNode("VIG_ENGI_ELECTRICAL_MACHINES_LAB", "Electrical Machines Lab", "Dept of Electrical & Electronics Engineering", "EEE Department Block", 0, 83.0, 42.0, 0.0, "lab", nav_id="SEID00000002801")
    nodes["VIG_ENGI_POWER_SYSTEMS_LAB"] = CampusNode("VIG_ENGI_POWER_SYSTEMS_LAB", "Power Systems lab", "Dept of Electrical & Electronics Engineering", "EEE Department Block", 0, 81.5, 46.8, 0.0, "lab", nav_id="SEID00000002802")
    nodes["VIG_ENGI_POWER_ELECTRONICS_LAB"] = CampusNode("VIG_ENGI_POWER_ELECTRONICS_LAB", "Power Electronics Lab", "Dept of Electrical & Electronics Engineering", "EEE Department Block", 0, 74.3, 46.1, 0.0, "lab", nav_id="SEID00000002803")
    nodes["VIG_ENGI_SIMULATION_LAB"] = CampusNode("VIG_ENGI_SIMULATION_LAB", "Simulation Lab", "Dept of Electrical & Electronics Engineering", "EEE Department Block", 0, 77.6, 40.2, 0.0, "lab", nav_id="SEID00000002804")
    nodes["VIG_ENGI_EEE_DEPT_LIBRARY"] = CampusNode("VIG_ENGI_EEE_DEPT_LIBRARY", "EEE Dept Library", "Dept of Electrical & Electronics Engineering", "EEE Department Block", 0, 81.5, 37.2, 0.0, "lab", nav_id="SEID00000002805")
    nodes["VIG_ENGI_COMMUNICATION_LAB_1"] = CampusNode("VIG_ENGI_COMMUNICATION_LAB_1", "Communication Lab 1", "Dept of Electronics & Communication Engineering", "ECE Department Block", 0, 88.0, 35.0, 0.0, "lab", nav_id="SEID00000002807")
    nodes["VIG_ENGI_COMMUNICATION_LAB_2"] = CampusNode("VIG_ENGI_COMMUNICATION_LAB_2", "Communication Lab 2", "Dept of Electronics & Communication Engineering", "ECE Department Block", 0, 88.8, 38.2, 0.0, "lab", nav_id="SEID00000002808")
    nodes["VIG_ENGI_INSTRUMENTATION_LAB"] = CampusNode("VIG_ENGI_INSTRUMENTATION_LAB", "Instrumentation Lab", "Dept of Electronics & Communication Engineering", "ECE Department Block", 0, 86.2, 41.9, 0.0, "lab", nav_id="SEID00000002809")
    nodes["VIG_ENGI_EMBEDDED_SYSTEMS_LAB"] = CampusNode("VIG_ENGI_EMBEDDED_SYSTEMS_LAB", "Embedded Systems Lab", "Dept of Electronics & Communication Engineering", "ECE Department Block", 0, 83.5, 37.6, 0.0, "lab", nav_id="SEID00000002810")
    nodes["VIG_ENGI_VLSI_DESIGN_RESEARCH_LA"] = CampusNode("VIG_ENGI_VLSI_DESIGN_RESEARCH_LA", "VLSI Design Research Lab", "Dept of Electronics & Communication Engineering", "ECE Department Block", 0, 80.3, 36.7, 0.0, "lab", nav_id="SEID00000002811")
    nodes["VIG_ENGI_IC_APPLICATIONS_LAB"] = CampusNode("VIG_ENGI_IC_APPLICATIONS_LAB", "IC Applications Lab", "Dept of Electronics & Communication Engineering", "ECE Department Block", 0, 78.4, 32.6, 0.0, "lab", nav_id="SEID00000002812")
    nodes["VIG_ENGI_MICROPROCESSOR_LAB"] = CampusNode("VIG_ENGI_MICROPROCESSOR_LAB", "Microprocessor Lab", "Dept of Electronics & Communication Engineering", "ECE Department Block", 0, 83.5, 32.4, 0.0, "lab", nav_id="SEID00000002813")
    nodes["VIG_ENGI_CAD_LAB"] = CampusNode("VIG_ENGI_CAD_LAB", "CAD Lab", "Dept of Electronics & Communication Engineering", "ECE Department Block", 0, 85.9, 30.1, 0.0, "lab", nav_id="SEID00000002814")
    nodes["VIG_ENGI_ECE_DEPT_LIBRARY"] = CampusNode("VIG_ENGI_ECE_DEPT_LIBRARY", "ECE Dept Library", "Dept of Electronics & Communication Engineering", "ECE Department Block", 0, 90.4, 30.5, 0.0, "lab", nav_id="SEID00000002815")
    nodes["VIG_ENGI_COE_LAB"] = CampusNode("VIG_ENGI_COE_LAB", "COE Lab", "Dept of Mechanical Engineering", "Mechanical Engineering Block", 0, 28.0, 55.0, 0.0, "lab", nav_id="SEID00000002817")
    nodes["VIG_ENGI_FLUID_MECHANICS_HYDRAUL"] = CampusNode("VIG_ENGI_FLUID_MECHANICS_HYDRAUL", "Fluid Mechanics & Hydraulic Machines lab", "Dept of Mechanical Engineering", "Mechanical Engineering Block", 0, 28.5, 58.5, 0.0, "lab", nav_id="SEID00000002822")
    nodes["VIG_ENGI_POLYMER_COMPOSITE_LAB"] = CampusNode("VIG_ENGI_POLYMER_COMPOSITE_LAB", "Polymer Composite Lab", "Dept of Mechanical Engineering", "Mechanical Engineering Block", 0, 25.0, 62.0, 0.0, "lab", nav_id="SEID00000002823")
    nodes["VIG_ENGI_MANUFACTURING_PROCESS_L"] = CampusNode("VIG_ENGI_MANUFACTURING_PROCESS_L", "Manufacturing Process Lab", "Dept of Mechanical Engineering", "Mechanical Engineering Block", 0, 22.9, 57.1, 0.0, "lab", nav_id="SEID00000002818")
    nodes["VIG_ENGI_IC_ENGINES_LAB"] = CampusNode("VIG_ENGI_IC_ENGINES_LAB", "IC Engines Lab", "Dept of Mechanical Engineering", "Mechanical Engineering Block", 0, 20.0, 55.0, 0.0, "lab", nav_id="SEID00000002819")
    nodes["VIG_ENGI_MACHINE_TOOLS_LAB"] = CampusNode("VIG_ENGI_MACHINE_TOOLS_LAB", "Machine Tools Lab", "Dept of Mechanical Engineering", "Mechanical Engineering Block", 0, 20.1, 50.1, 0.0, "lab", nav_id="SEID00000002820")
    nodes["VIG_ENGI_MACHINE_DYNAMICS_LAB"] = CampusNode("VIG_ENGI_MACHINE_DYNAMICS_LAB", "Machine Dynamics Lab", "Dept of Mechanical Engineering", "Mechanical Engineering Block", 0, 25.0, 52.0, 0.0, "lab", nav_id="SEID00000002821")
    nodes["VIG_ENGI_MECHANICAL_DEPT_LIBRARY"] = CampusNode("VIG_ENGI_MECHANICAL_DEPT_LIBRARY", "Mechanical Dept Library", "Dept of Mechanical Engineering", "Mechanical Engineering Block", 0, 28.5, 51.5, 0.0, "lab", nav_id="SEID00000002824")
    nodes["VIG_ENGI_CONCRETE_LAB"] = CampusNode("VIG_ENGI_CONCRETE_LAB", "Concrete Lab", "Dept of Civil Engineering", "Civil Engineering Block", 0, 18.0, 55.0, 0.0, "lab", nav_id="SEID00000002826")
    nodes["VIG_ENGI_GEO_TECHNICAL_LAB"] = CampusNode("VIG_ENGI_GEO_TECHNICAL_LAB", "Geo Technical Lab", "Dept of Civil Engineering", "Civil Engineering Block", 0, 18.1, 58.9, 0.0, "lab", nav_id="SEID00000002827")
    nodes["VIG_ENGI_GEOLOGY_LAB"] = CampusNode("VIG_ENGI_GEOLOGY_LAB", "Geology Lab", "Dept of Civil Engineering", "Civil Engineering Block", 0, 13.4, 61.8, 0.0, "lab", nav_id="SEID00000002828")
    nodes["VIG_ENGI_SURVEYING_LAB"] = CampusNode("VIG_ENGI_SURVEYING_LAB", "Surveying Lab", "Dept of Civil Engineering", "Civil Engineering Block", 0, 12.3, 56.3, 0.0, "lab", nav_id="SEID00000002829")
    nodes["VIG_ENGI_ENVIRONMENTAL_ENGINEERI"] = CampusNode("VIG_ENGI_ENVIRONMENTAL_ENGINEERI", "Environmental Engineering Lab", "Dept of Civil Engineering", "Civil Engineering Block", 0, 10.5, 52.8, 0.0, "lab", nav_id="SEID00000002830")
    nodes["VIG_ENGI_COMPUTER_LAB"] = CampusNode("VIG_ENGI_COMPUTER_LAB", "Computer Lab", "Dept of Civil Engineering", "Civil Engineering Block", 0, 13.4, 48.2, 0.0, "lab", nav_id="SEID00000002831")
    nodes["VIG_ENGI_CIVIL_DEPT_LIBRARY"] = CampusNode("VIG_ENGI_CIVIL_DEPT_LIBRARY", "Civil Dept Library", "Dept of Civil Engineering", "Civil Engineering Block", 0, 16.9, 52.7, 0.0, "lab", nav_id="SEID00000002832")
    nodes["VIG_TECH_COE_LAB"] = CampusNode("VIG_TECH_COE_LAB", "COE Lab", "Dept of Bio Technology", "Biotechnology Block", 0, 43.0, 65.0, 0.0, "lab", nav_id="SEID00000002834")
    nodes["VIG_TECH_BIO_CHEMISTRY_LAB"] = CampusNode("VIG_TECH_BIO_CHEMISTRY_LAB", "Bio Chemistry Lab", "Dept of Bio Technology", "Biotechnology Block", 2, 41.5, 69.8, 8.0, "lab", nav_id="SEID00000002835")
    nodes["VIG_TECH_BIO_RESEARCH_LAB"] = CampusNode("VIG_TECH_BIO_RESEARCH_LAB", "Bio Research Lab", "Dept of Bio Technology", "Biotechnology Block", 0, 34.3, 69.1, 0.0, "lab", nav_id="SEID00000002836")
    nodes["VIG_TECH_PLANT_TISSUE_CULTIVATE_"] = CampusNode("VIG_TECH_PLANT_TISSUE_CULTIVATE_", "Plant Tissue Cultivate Lab", "Dept of Bio Technology", "Biotechnology Block", 0, 37.6, 63.2, 0.0, "lab", nav_id="SEID00000002837")
    nodes["VIG_TECH_BIO_PROCESS_LAB"] = CampusNode("VIG_TECH_BIO_PROCESS_LAB", "Bio Process Lab", "Dept of Bio Technology", "Biotechnology Block", 0, 41.5, 60.2, 0.0, "lab", nav_id="SEID00000002838")
    nodes["VIG_ENGI_PROCESS_DYNAMICS_AND_CO"] = CampusNode("VIG_ENGI_PROCESS_DYNAMICS_AND_CO", "Process Dynamics and Control Lab", "Dept of Chemical Engineering", "Chemical Engineering Block", 2, 53.0, 88.0, 8.0, "lab", nav_id="SEID00000002840")
    nodes["VIG_ENGI_CHEMICAL_REACTION_ENGG_"] = CampusNode("VIG_ENGI_CHEMICAL_REACTION_ENGG_", "Chemical Reaction Engg Lab", "Dept of Chemical Engineering", "Chemical Engineering Block", 2, 53.1, 91.9, 8.0, "lab", nav_id="SEID00000002841")
    nodes["VIG_ENGI_MECHANICAL_UNIT_OPERATI"] = CampusNode("VIG_ENGI_MECHANICAL_UNIT_OPERATI", "Mechanical Unit Operation lab", "Dept of Chemical Engineering", "Chemical Engineering Block", 2, 48.4, 94.8, 8.0, "lab", nav_id="SEID00000002842")
    nodes["VIG_ENGI_TEXTILE_TESTING_LAB"] = CampusNode("VIG_ENGI_TEXTILE_TESTING_LAB", "Textile Testing Lab", "Dept of Chemical Engineering", "Chemical Engineering Block", 2, 47.3, 89.3, 8.0, "lab", nav_id="SEID00000002843")
    nodes["VIG_ENGI_HEAT_TRANSFER_LAB"] = CampusNode("VIG_ENGI_HEAT_TRANSFER_LAB", "Heat Transfer Lab", "Dept of Chemical Engineering", "Chemical Engineering Block", 2, 45.5, 85.8, 8.0, "lab", nav_id="SEID00000002844")
    nodes["VIG_ENGI_BIO_CHEMISTRY_LAB"] = CampusNode("VIG_ENGI_BIO_CHEMISTRY_LAB", "Bio Chemistry Lab", "Dept of Chemical Engineering", "Chemical Engineering Block", 2, 48.4, 81.2, 8.0, "lab", nav_id="SEID00000002845")
    nodes["VIG_ENGI_FOOD_MICRO_BIOLOGY_LAB"] = CampusNode("VIG_ENGI_FOOD_MICRO_BIOLOGY_LAB", "Food Micro Biology Lab", "Dept of Chemical Engineering", "Chemical Engineering Block", 2, 51.9, 85.7, 8.0, "lab", nav_id="SEID00000002846")
    nodes["VIG_ENGI_DRILLING_FLUIDS_LAB"] = CampusNode("VIG_ENGI_DRILLING_FLUIDS_LAB", "Drilling Fluids Lab", "Dept of Petroleum Engineering", "Chemical & Petroleum Block", 1, 58.0, 88.0, 4.0, "lab", nav_id="SEID00000002848")
    nodes["VIG_TECH_TEXTILE_FASHION_TECHNOL"] = CampusNode("VIG_TECH_TEXTILE_FASHION_TECHNOL", "Textile & Fashion Technology", "Dept of Textile Technology", "Textile & Fashion Block", 1, 63.0, 88.0, 4.0, "lab", nav_id="SEID00000002851")
    nodes["VIG_HUMA_CHEMISTRY_LAB"] = CampusNode("VIG_HUMA_CHEMISTRY_LAB", "Chemistry Lab", "Dept of Science and Humanities", "Science & Humanities Block", 0, 35.0, 75.0, 0.0, "lab", nav_id="SEID00000002853")
    nodes["VIG_HUMA_PHYSICS_LAB"] = CampusNode("VIG_HUMA_PHYSICS_LAB", "Physics Lab", "Dept of Science and Humanities", "Science & Humanities Block", 0, 29.5, 79.3, 0.0, "lab", nav_id="SEID00000002854")
    nodes["VIG_HUMA_PHYSICS_LAB_1"] = CampusNode("VIG_HUMA_PHYSICS_LAB_1", "Physics Lab 1", "Dept of Science and Humanities", "Science & Humanities Block", 0, 28.5, 68.9, 0.0, "lab", nav_id="SEID00000002855")
    nodes["VIG_DEVE_OFFICE_ICT_ELECTRONICS"] = CampusNode("VIG_DEVE_OFFICE_ICT_ELECTRONICS", "Office & ICT Electronics", "Dept of Skill Development", "Skill Development Block", 0, 51.0, 38.0, 0.0, "lab", nav_id="SEID00000002861")
    nodes["VIG_DEVE_HOME_ELECTRONICS"] = CampusNode("VIG_DEVE_HOME_ELECTRONICS", "Home Electronics", "Dept of Skill Development", "Skill Development Block", 0, 49.5, 42.8, 0.0, "lab", nav_id="SEID00000002862")
    nodes["VIG_DEVE_REFREGIRATION_AIR_CONDI"] = CampusNode("VIG_DEVE_REFREGIRATION_AIR_CONDI", "Refregiration & Air Conditioning", "Dept of Skill Development", "Skill Development Block", 0, 42.3, 42.1, 0.0, "lab", nav_id="SEID00000002863")
    nodes["VIG_DEVE_WELDING"] = CampusNode("VIG_DEVE_WELDING", "Welding", "Dept of Skill Development", "Skill Development Block", 0, 45.6, 36.2, 0.0, "lab", nav_id="SEID00000002864")
    nodes["VIG_DEVE_COMPUTER_NUMERICAL_CONT"] = CampusNode("VIG_DEVE_COMPUTER_NUMERICAL_CONT", "Computer & Numerical Control Lab", "Dept of Skill Development", "Skill Development Block", 0, 49.5, 33.2, 0.0, "lab", nav_id="SEID00000002865")
    nodes["VIG_FACI_SANGAM_SEMINAR_HALL"] = CampusNode("VIG_FACI_SANGAM_SEMINAR_HALL", "Sangam Seminar Hall", "University Facilities", "University Facilities & Hostels", 0, 53.0, 18.0, 0.0, "facility", nav_id="SEID00000002868")
    nodes["VIG_FACI_GALLERY_HALL"] = CampusNode("VIG_FACI_GALLERY_HALL", "Gallery Hall", "University Facilities", "University Facilities & Hostels", 0, 54.7, 19.6, 0.0, "facility", nav_id="SEID00000002871")
    nodes["VIG_FACI_SPOORTHY_SEMINAR_HALL"] = CampusNode("VIG_FACI_SPOORTHY_SEMINAR_HALL", "Spoorthy Seminar Hall", "University Facilities", "University Facilities & Hostels", 0, 55.5, 22.3, 0.0, "facility", nav_id="SEID00000002869")
    nodes["VIG_FACI_CONVOCATION_HALL"] = CampusNode("VIG_FACI_CONVOCATION_HALL", "Convocation Hall", "University Facilities", "University Facilities & Hostels", 0, 51.6, 20.5, 0.0, "facility", nav_id="SEID00000002870")
    nodes["VIG_FACI_GUEST_HOUSE_OUTER_VIEW"] = CampusNode("VIG_FACI_GUEST_HOUSE_OUTER_VIEW", "Guest House Outer View", "University Facilities", "University Facilities & Hostels", 0, 51.2, 22.8, 0.0, "facility", nav_id="SEID00000002883")
    nodes["VIG_FACI_GUEST_ROOM"] = CampusNode("VIG_FACI_GUEST_ROOM", "Guest Room", "University Facilities", "University Facilities & Hostels", 0, 49.4, 25.0, 0.0, "facility", nav_id="SEID00000002884")
    nodes["VIG_FACI_GUEST_ROOM_1"] = CampusNode("VIG_FACI_GUEST_ROOM_1", "Guest Room 1", "University Facilities", "University Facilities & Hostels", 0, 48.8, 20.7, 0.0, "facility", nav_id="SEID00000002885")
    nodes["VIG_FACI_BOYS_HOSTEL_ROOM"] = CampusNode("VIG_FACI_BOYS_HOSTEL_ROOM", "Boys Hostel Room", "University Facilities", "University Facilities & Hostels", 0, 46.6, 21.7, 0.0, "facility", nav_id="SEID00000002872")
    nodes["VIG_FACI_BOYS_MESS"] = CampusNode("VIG_FACI_BOYS_MESS", "Boys Mess", "University Facilities", "University Facilities & Hostels", 0, 43.8, 21.3, 0.0, "facility", nav_id="SEID00000002873")
    nodes["VIG_FACI_GYM"] = CampusNode("VIG_FACI_GYM", "Gym", "University Facilities", "University Facilities & Hostels", 0, 47.0, 18.5, 0.0, "facility", nav_id="SEID00000002874")
    nodes["VIG_FACI_PRIYADARSHINI_GIRLS_HOS"] = CampusNode("VIG_FACI_PRIYADARSHINI_GIRLS_HOS", "Priyadarshini Girls Hostel View", "University Facilities", "University Facilities & Hostels", 0, 45.1, 17.2, 0.0, "facility", nav_id="SEID00000002886")
    nodes["VIG_FACI_GIRLS_HOSTEL_ROOM"] = CampusNode("VIG_FACI_GIRLS_HOSTEL_ROOM", "Girls Hostel Room", "University Facilities", "University Facilities & Hostels", 0, 43.8, 14.7, 0.0, "facility", nav_id="SEID00000002875")
    nodes["VIG_FACI_GIRLS_HOSTEL_ROOM_1"] = CampusNode("VIG_FACI_GIRLS_HOSTEL_ROOM_1", "Girls Hostel Room 1", "University Facilities", "University Facilities & Hostels", 0, 48.0, 15.8, 0.0, "facility", nav_id="SEID00000002876")
    nodes["VIG_FACI_GIRLS_MESS"] = CampusNode("VIG_FACI_GIRLS_MESS", "Girls Mess", "University Facilities", "University Facilities & Hostels", 0, 48.0, 13.4, 0.0, "facility", nav_id="SEID00000002877")
    nodes["VIG_FACI_CANTEEN"] = CampusNode("VIG_FACI_CANTEEN", "Canteen", "University Facilities", "University Facilities & Hostels", 0, 49.4, 11.0, 0.0, "facility", nav_id="SEID00000002878")
    nodes["VIG_FACI_HEALTH_CENTRE"] = CampusNode("VIG_FACI_HEALTH_CENTRE", "Health Centre", "University Facilities", "University Facilities & Hostels", 0, 50.7, 15.1, 0.0, "facility", nav_id="SEID00000002879")
    nodes["VIG_FACI_MEDIA_CENTRE"] = CampusNode("VIG_FACI_MEDIA_CENTRE", "Media Centre", "University Facilities", "University Facilities & Hostels", 0, 52.7, 13.8, 0.0, "facility", nav_id="SEID00000002880")
    nodes["VIG_FACI_PLAY_GROUNDS"] = CampusNode("VIG_FACI_PLAY_GROUNDS", "Play Grounds", "University Facilities", "University Facilities & Hostels", 0, 55.5, 13.7, 0.0, "assembly", nav_id="SEID00000002881")
    nodes["VIG_FACI_TRANSPORT_BUSES"] = CampusNode("VIG_FACI_TRANSPORT_BUSES", "Transport Buses", "University Facilities", "University Facilities & Hostels", 0, 52.8, 17.0, 0.0, "exit", nav_id="SEID00000002882")

    # --- Campus Arterial Hubs, Corridors & Stairwells ---
    nodes["HUB_CENTRAL_PLAZA"] = CampusNode("HUB_CENTRAL_PLAZA", "Vignan Central Quadrangle Plaza", "Campus Core", "Central Plaza", 0, 50.0, 50.0, 0.0, "corridor")
    nodes["HUB_NORTH_AVENUE"] = CampusNode("HUB_NORTH_AVENUE", "Campus North Arterial Avenue", "Campus Core", "North Avenue", 0, 50.0, 75.0, 0.0, "corridor")
    nodes["HUB_SOUTH_AVENUE"] = CampusNode("HUB_SOUTH_AVENUE", "Campus South Arterial Avenue", "Campus Core", "South Avenue", 0, 50.0, 25.0, 0.0, "corridor")
    nodes["HUB_WEST_AVENUE"] = CampusNode("HUB_WEST_AVENUE", "West Admin Arterial Pathway", "Campus Core", "West Avenue", 0, 20.0, 50.0, 0.0, "corridor")
    nodes["HUB_EAST_AVENUE"] = CampusNode("HUB_EAST_AVENUE", "East Engineering Quad Avenue", "Campus Core", "East Avenue", 0, 80.0, 50.0, 0.0, "corridor")

    # Vertical Stairwells for Multi-Story Chemical & Library Blocks
    nodes["CHEM_STAIR_A_F0"] = CampusNode("CHEM_STAIR_A_F0", "Chem Block Stairwell A (Ground Landing)", "Stairwells", "Chemical Engg Block", 0, 42.0, 88.0, 0.0, "stairwell")
    nodes["CHEM_STAIR_A_F1"] = CampusNode("CHEM_STAIR_A_F1", "Chem Block Stairwell A (Floor 1)", "Stairwells", "Chemical Engg Block", 1, 42.0, 88.0, 4.0, "stairwell")
    nodes["CHEM_STAIR_A_F2"] = CampusNode("CHEM_STAIR_A_F2", "Chem Block Stairwell A (Floor 2 Landing)", "Stairwells", "Chemical Engg Block", 2, 42.0, 88.0, 8.0, "stairwell")
    nodes["CHEM_STAIR_B_F0"] = CampusNode("CHEM_STAIR_B_F0", "Chem Block Stairwell B (Ground Landing)", "Stairwells", "Chemical Engg Block", 0, 58.0, 88.0, 0.0, "stairwell")
    nodes["CHEM_STAIR_B_F1"] = CampusNode("CHEM_STAIR_B_F1", "Chem Block Stairwell B (Floor 1)", "Stairwells", "Chemical Engg Block", 1, 58.0, 88.0, 4.0, "stairwell")
    nodes["CHEM_STAIR_B_F2"] = CampusNode("CHEM_STAIR_B_F2", "Chem Block Stairwell B (Floor 2 Landing)", "Stairwells", "Chemical Engg Block", 2, 58.0, 88.0, 8.0, "stairwell")
    nodes["LIB_STAIR_F0"] = CampusNode("LIB_STAIR_F0", "NTR Library Stairwell (Ground)", "Stairwells", "NTR Library", 0, 20.0, 82.0, 0.0, "stairwell")
    nodes["LIB_STAIR_F1"] = CampusNode("LIB_STAIR_F1", "NTR Library Stairwell (Floor 1)", "Stairwells", "NTR Library", 1, 20.0, 82.0, 4.0, "stairwell")

    # Connecting Edges Network
    raw_edges = [
        # Arterial Spine
        ("HUB_CENTRAL_PLAZA", "HUB_NORTH_AVENUE"),
        ("HUB_CENTRAL_PLAZA", "HUB_SOUTH_AVENUE"),
        ("HUB_CENTRAL_PLAZA", "HUB_WEST_AVENUE"),
        ("HUB_CENTRAL_PLAZA", "HUB_EAST_AVENUE"),
        ("HUB_NORTH_AVENUE", "HUB_WEST_AVENUE"),
        ("HUB_NORTH_AVENUE", "HUB_EAST_AVENUE"),
        ("HUB_SOUTH_AVENUE", "HUB_WEST_AVENUE"),
        ("HUB_SOUTH_AVENUE", "HUB_EAST_AVENUE"),

        # Chemical Block Stair Vertical Connections
        ("CHEM_STAIR_A_F0", "CHEM_STAIR_A_F1"),
        ("CHEM_STAIR_A_F1", "CHEM_STAIR_A_F2"),
        ("CHEM_STAIR_B_F0", "CHEM_STAIR_B_F1"),
        ("CHEM_STAIR_B_F1", "CHEM_STAIR_B_F2"),
        ("CHEM_STAIR_A_F0", "HUB_NORTH_AVENUE"),
        ("CHEM_STAIR_B_F0", "HUB_NORTH_AVENUE"),
        ("LIB_STAIR_F0", "LIB_STAIR_F1"),
        ("LIB_STAIR_F0", "HUB_WEST_AVENUE"),

        # Direct Arterial Safe Exit & Assembly Connections
        ("HUB_SOUTH_AVENUE", "VIG_FACI_PLAY_GROUNDS"),
        ("HUB_SOUTH_AVENUE", "VIG_FACI_CANTEEN"),
        ("HUB_SOUTH_AVENUE", "VIG_FACI_HEALTH_CENTRE"),
        ("HUB_SOUTH_AVENUE", "VIG_ADMI_MAIN_ENTRANCE_SECURIT"),
        ("HUB_WEST_AVENUE", "VIG_FACI_PLAY_GROUNDS"),
    ]
    # Connect each room/lab in each section to its hub & daisy chain
    raw_edges.append(("VIG_FOUN_VIGNAN_CAMPUS_VIEW", "HUB_WEST_AVENUE"))
    raw_edges.append(("VIG_FOUN_VIGNAN_CAMPUS_VIEW", "VIG_FOUN_CHAIRMAN_S_ROOM"))
    raw_edges.append(("VIG_FOUN_CHAIRMAN_S_ROOM", "VIG_FOUN_VICE_CHAIRMAN_S_ROOM"))
    raw_edges.append(("VIG_FOUN_VICE_CHAIRMAN_S_ROOM", "VIG_FOUN_CHANCELLOR_S_ROOM"))
    raw_edges.append(("VIG_FOUN_CHANCELLOR_S_ROOM", "VIG_FOUN_VICE_CHANCELLOR_S_ROOM"))
    raw_edges.append(("VIG_FOUN_VICE_CHANCELLOR_S_ROOM", "VIG_FOUN_REGISTRAR_S_ROOM"))
    raw_edges.append(("VIG_FOUN_REGISTRAR_S_ROOM", "VIG_FOUN_DEAN_S_ROOM"))
    raw_edges.append(("VIG_FOUN_DEAN_S_ROOM", "VIG_FOUN_BOARD_ROOM"))
    raw_edges.append(("VIG_LIBR_LIBRARY_BLOCK", "LIB_STAIR_F0"))
    raw_edges.append(("VIG_LIBR_LIBRARY_BLOCK", "VIG_LIBR_LIBRARY_GROUND_FLOOR"))
    raw_edges.append(("VIG_LIBR_LIBRARY_GROUND_FLOOR", "VIG_LIBR_LIBRARY_FIRST_FLOOR"))
    raw_edges.append(("VIG_LIBR_LIBRARY_FIRST_FLOOR", "VIG_LIBR_GENERAL_REFERENCE_SECTI"))
    raw_edges.append(("VIG_LIBR_GENERAL_REFERENCE_SECTI", "VIG_LIBR_CIVIL_SERVICES_ASPIRANT"))
    raw_edges.append(("VIG_LIBR_CIVIL_SERVICES_ASPIRANT", "VIG_LIBR_VIDEO_CONFERENCE_HALL"))
    raw_edges.append(("VIG_LIBR_VIDEO_CONFERENCE_HALL", "VIG_LIBR_RESEARCH_CARRELS"))
    raw_edges.append(("VIG_LIBR_RESEARCH_CARRELS", "VIG_LIBR_DIGITAL_LIBRARY"))
    raw_edges.append(("VIG_LIBR_DIGITAL_LIBRARY", "LIB_STAIR_F1"))
    raw_edges.append(("VIG_TRAI_ADMISSION_DEPARTMENT", "HUB_WEST_AVENUE"))
    raw_edges.append(("VIG_TRAI_ADMISSION_DEPARTMENT", "VIG_TRAI_TRAINING_AND_PLACEMENT"))
    raw_edges.append(("VIG_TRAI_TRAINING_AND_PLACEMENT", "VIG_TRAI_INTERVIEW_PANELS"))
    raw_edges.append(("VIG_TRAI_INTERVIEW_PANELS", "VIG_TRAI_DEAN_ADMISSIONS"))
    raw_edges.append(("VIG_LABO_ENGLISH_LANGUAGE_LAB", "HUB_NORTH_AVENUE"))
    raw_edges.append(("VIG_LABO_ENGLISH_LANGUAGE_LAB", "VIG_LABO_SCIENCE_HUMANITIES_RESE"))
    raw_edges.append(("VIG_LABO_SCIENCE_HUMANITIES_RESE", "VIG_LABO_MAT_LAB"))
    raw_edges.append(("VIG_ENGI_ADVANCED_PROGRAMMING_NE", "HUB_EAST_AVENUE"))
    raw_edges.append(("VIG_ENGI_ADVANCED_PROGRAMMING_NE", "VIG_ENGI_OPEN_SOURCE_DEVELOPMENT"))
    raw_edges.append(("VIG_ENGI_OPEN_SOURCE_DEVELOPMENT", "VIG_ENGI_INFORMATION_TECHNOLOGY_"))
    raw_edges.append(("VIG_ENGI_INFORMATION_TECHNOLOGY_", "VIG_ENGI_CSE_DEPT_LIBRARY"))
    raw_edges.append(("VIG_ENGI_ELECTRICAL_MACHINES_LAB", "HUB_EAST_AVENUE"))
    raw_edges.append(("VIG_ENGI_ELECTRICAL_MACHINES_LAB", "VIG_ENGI_POWER_SYSTEMS_LAB"))
    raw_edges.append(("VIG_ENGI_POWER_SYSTEMS_LAB", "VIG_ENGI_POWER_ELECTRONICS_LAB"))
    raw_edges.append(("VIG_ENGI_POWER_ELECTRONICS_LAB", "VIG_ENGI_SIMULATION_LAB"))
    raw_edges.append(("VIG_ENGI_SIMULATION_LAB", "VIG_ENGI_EEE_DEPT_LIBRARY"))
    raw_edges.append(("VIG_ENGI_COMMUNICATION_LAB_1", "HUB_EAST_AVENUE"))
    raw_edges.append(("VIG_ENGI_COMMUNICATION_LAB_1", "VIG_ENGI_COMMUNICATION_LAB_2"))
    raw_edges.append(("VIG_ENGI_COMMUNICATION_LAB_2", "VIG_ENGI_INSTRUMENTATION_LAB"))
    raw_edges.append(("VIG_ENGI_INSTRUMENTATION_LAB", "VIG_ENGI_EMBEDDED_SYSTEMS_LAB"))
    raw_edges.append(("VIG_ENGI_EMBEDDED_SYSTEMS_LAB", "VIG_ENGI_VLSI_DESIGN_RESEARCH_LA"))
    raw_edges.append(("VIG_ENGI_VLSI_DESIGN_RESEARCH_LA", "VIG_ENGI_IC_APPLICATIONS_LAB"))
    raw_edges.append(("VIG_ENGI_IC_APPLICATIONS_LAB", "VIG_ENGI_MICROPROCESSOR_LAB"))
    raw_edges.append(("VIG_ENGI_MICROPROCESSOR_LAB", "VIG_ENGI_CAD_LAB"))
    raw_edges.append(("VIG_ENGI_CAD_LAB", "VIG_ENGI_ECE_DEPT_LIBRARY"))
    raw_edges.append(("VIG_ENGI_COE_LAB", "HUB_WEST_AVENUE"))
    raw_edges.append(("VIG_ENGI_COE_LAB", "VIG_ENGI_FLUID_MECHANICS_HYDRAUL"))
    raw_edges.append(("VIG_ENGI_FLUID_MECHANICS_HYDRAUL", "VIG_ENGI_POLYMER_COMPOSITE_LAB"))
    raw_edges.append(("VIG_ENGI_POLYMER_COMPOSITE_LAB", "VIG_ENGI_MANUFACTURING_PROCESS_L"))
    raw_edges.append(("VIG_ENGI_MANUFACTURING_PROCESS_L", "VIG_ENGI_IC_ENGINES_LAB"))
    raw_edges.append(("VIG_ENGI_IC_ENGINES_LAB", "VIG_ENGI_MACHINE_TOOLS_LAB"))
    raw_edges.append(("VIG_ENGI_MACHINE_TOOLS_LAB", "VIG_ENGI_MACHINE_DYNAMICS_LAB"))
    raw_edges.append(("VIG_ENGI_MACHINE_DYNAMICS_LAB", "VIG_ENGI_MECHANICAL_DEPT_LIBRARY"))
    raw_edges.append(("VIG_ENGI_CONCRETE_LAB", "HUB_WEST_AVENUE"))
    raw_edges.append(("VIG_ENGI_CONCRETE_LAB", "VIG_ENGI_GEO_TECHNICAL_LAB"))
    raw_edges.append(("VIG_ENGI_GEO_TECHNICAL_LAB", "VIG_ENGI_GEOLOGY_LAB"))
    raw_edges.append(("VIG_ENGI_GEOLOGY_LAB", "VIG_ENGI_SURVEYING_LAB"))
    raw_edges.append(("VIG_ENGI_SURVEYING_LAB", "VIG_ENGI_ENVIRONMENTAL_ENGINEERI"))
    raw_edges.append(("VIG_ENGI_ENVIRONMENTAL_ENGINEERI", "VIG_ENGI_COMPUTER_LAB"))
    raw_edges.append(("VIG_ENGI_COMPUTER_LAB", "VIG_ENGI_CIVIL_DEPT_LIBRARY"))
    raw_edges.append(("VIG_TECH_COE_LAB", "HUB_NORTH_AVENUE"))
    raw_edges.append(("VIG_TECH_COE_LAB", "VIG_TECH_BIO_CHEMISTRY_LAB"))
    raw_edges.append(("VIG_TECH_BIO_CHEMISTRY_LAB", "VIG_TECH_BIO_RESEARCH_LAB"))
    raw_edges.append(("VIG_TECH_BIO_RESEARCH_LAB", "VIG_TECH_PLANT_TISSUE_CULTIVATE_"))
    raw_edges.append(("VIG_TECH_PLANT_TISSUE_CULTIVATE_", "VIG_TECH_BIO_PROCESS_LAB"))
    raw_edges.append(("VIG_ENGI_PROCESS_DYNAMICS_AND_CO", "CHEM_STAIR_A_F2"))
    raw_edges.append(("VIG_ENGI_PROCESS_DYNAMICS_AND_CO", "VIG_ENGI_CHEMICAL_REACTION_ENGG_"))
    raw_edges.append(("VIG_ENGI_CHEMICAL_REACTION_ENGG_", "VIG_ENGI_MECHANICAL_UNIT_OPERATI"))
    raw_edges.append(("VIG_ENGI_MECHANICAL_UNIT_OPERATI", "VIG_ENGI_TEXTILE_TESTING_LAB"))
    raw_edges.append(("VIG_ENGI_TEXTILE_TESTING_LAB", "VIG_ENGI_HEAT_TRANSFER_LAB"))
    raw_edges.append(("VIG_ENGI_HEAT_TRANSFER_LAB", "VIG_ENGI_BIO_CHEMISTRY_LAB"))
    raw_edges.append(("VIG_ENGI_BIO_CHEMISTRY_LAB", "VIG_ENGI_FOOD_MICRO_BIOLOGY_LAB"))
    raw_edges.append(("VIG_ENGI_FOOD_MICRO_BIOLOGY_LAB", "CHEM_STAIR_B_F2"))
    raw_edges.append(("VIG_ENGI_DRILLING_FLUIDS_LAB", "CHEM_STAIR_A_F1"))
    raw_edges.append(("VIG_TECH_TEXTILE_FASHION_TECHNOL", "CHEM_STAIR_B_F1"))
    raw_edges.append(("VIG_HUMA_CHEMISTRY_LAB", "HUB_NORTH_AVENUE"))
    raw_edges.append(("VIG_HUMA_CHEMISTRY_LAB", "VIG_HUMA_PHYSICS_LAB"))
    raw_edges.append(("VIG_HUMA_PHYSICS_LAB", "VIG_HUMA_PHYSICS_LAB_1"))
    raw_edges.append(("VIG_DEVE_OFFICE_ICT_ELECTRONICS", "HUB_CENTRAL_PLAZA"))
    raw_edges.append(("VIG_DEVE_OFFICE_ICT_ELECTRONICS", "VIG_DEVE_HOME_ELECTRONICS"))
    raw_edges.append(("VIG_DEVE_HOME_ELECTRONICS", "VIG_DEVE_REFREGIRATION_AIR_CONDI"))
    raw_edges.append(("VIG_DEVE_REFREGIRATION_AIR_CONDI", "VIG_DEVE_WELDING"))
    raw_edges.append(("VIG_DEVE_WELDING", "VIG_DEVE_COMPUTER_NUMERICAL_CONT"))
    raw_edges.append(("VIG_FACI_SANGAM_SEMINAR_HALL", "HUB_SOUTH_AVENUE"))
    raw_edges.append(("VIG_FACI_SANGAM_SEMINAR_HALL", "VIG_FACI_GALLERY_HALL"))
    raw_edges.append(("VIG_FACI_GALLERY_HALL", "VIG_FACI_SPOORTHY_SEMINAR_HALL"))
    raw_edges.append(("VIG_FACI_SPOORTHY_SEMINAR_HALL", "VIG_FACI_CONVOCATION_HALL"))
    raw_edges.append(("VIG_FACI_CONVOCATION_HALL", "VIG_FACI_GUEST_HOUSE_OUTER_VIEW"))
    raw_edges.append(("VIG_FACI_GUEST_HOUSE_OUTER_VIEW", "VIG_FACI_GUEST_ROOM"))
    raw_edges.append(("VIG_FACI_GUEST_ROOM", "VIG_FACI_GUEST_ROOM_1"))
    raw_edges.append(("VIG_FACI_GUEST_ROOM_1", "VIG_FACI_BOYS_HOSTEL_ROOM"))
    raw_edges.append(("VIG_FACI_BOYS_HOSTEL_ROOM", "VIG_FACI_BOYS_MESS"))
    raw_edges.append(("VIG_FACI_BOYS_MESS", "VIG_FACI_GYM"))
    raw_edges.append(("VIG_FACI_GYM", "VIG_FACI_PRIYADARSHINI_GIRLS_HOS"))
    raw_edges.append(("VIG_FACI_PRIYADARSHINI_GIRLS_HOS", "VIG_FACI_GIRLS_HOSTEL_ROOM"))
    raw_edges.append(("VIG_FACI_GIRLS_HOSTEL_ROOM", "VIG_FACI_GIRLS_HOSTEL_ROOM_1"))
    raw_edges.append(("VIG_FACI_GIRLS_HOSTEL_ROOM_1", "VIG_FACI_GIRLS_MESS"))
    raw_edges.append(("VIG_FACI_GIRLS_MESS", "VIG_FACI_CANTEEN"))
    raw_edges.append(("VIG_FACI_CANTEEN", "VIG_FACI_HEALTH_CENTRE"))
    raw_edges.append(("VIG_FACI_HEALTH_CENTRE", "VIG_FACI_MEDIA_CENTRE"))
    raw_edges.append(("VIG_FACI_MEDIA_CENTRE", "VIG_FACI_PLAY_GROUNDS"))
    raw_edges.append(("VIG_FACI_PLAY_GROUNDS", "VIG_FACI_TRANSPORT_BUSES"))

    edges = []
    for u, v in raw_edges:
        if u in nodes and v in nodes:
            dist = nodes[u].distance_to(nodes[v])
            edges.append((u, v, round(dist, 2)))

    # Automatically map authentic Virtual Tour Panorama IDs
    try:
        import json, os
        tour_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'vignan_tour_locations.json')
        if not os.path.exists(tour_file):
            tour_file = 'vignan_tour_locations.json'
        if os.path.exists(tour_file):
            with open(tour_file, 'r', encoding='utf-8') as f:
                tdata = json.load(f)
                nav_to_pano = {item['nav_id']: item.get('pano_id', '') for item in tdata.get('all_items', [])}
                for nid, node in nodes.items():
                    if node.nav_id in nav_to_pano:
                        node.pano_id = nav_to_pano[node.nav_id]
    except Exception:
        pass

    return nodes, edges
