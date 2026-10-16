import json
import re
import math

with open('vignan_tour_locations.json', 'r', encoding='utf-8') as f:
    tour_data = json.load(f)

# Define block center coordinates and floor levels
# Each section gets a designated zone in the campus layout
section_meta = {
    "About Vignan Foundation": {
        "block": "Vignan Foundation Admin Block",
        "cx": 20.0, "cy": 35.0, "z": 0.0, "floor": 0, "node_type": "room"
    },
    "NTR Vignan Library": {
        "block": "NTR Vignan Library Block",
        "cx": 20.0, "cy": 78.0, "z": 0.0, "floor": 0, "node_type": "room"
    },
    "Dept of Admission / Training": {
        "block": "Admission & Training Block",
        "cx": 30.0, "cy": 35.0, "z": 0.0, "floor": 0, "node_type": "room"
    },
    "Laboratories": {
        "block": "Central Academic Labs",
        "cx": 35.0, "cy": 70.0, "z": 0.0, "floor": 0, "node_type": "lab"
    },
    "Dept of Computer Science Engineering": {
        "block": "CSE Department Block",
        "cx": 80.0, "cy": 60.0, "z": 0.0, "floor": 0, "node_type": "lab"
    },
    "Dept of Electrical & Electronics Engineering": {
        "block": "EEE Department Block",
        "cx": 80.0, "cy": 42.0, "z": 0.0, "floor": 0, "node_type": "lab"
    },
    "Dept of Electronics & Communication Engineering": {
        "block": "ECE Department Block",
        "cx": 85.0, "cy": 35.0, "z": 0.0, "floor": 0, "node_type": "lab"
    },
    "Dept of Mechanical Engineering": {
        "block": "Mechanical Engineering Block",
        "cx": 25.0, "cy": 55.0, "z": 0.0, "floor": 0, "node_type": "lab"
    },
    "Dept of Civil Engineering": {
        "block": "Civil Engineering Block",
        "cx": 15.0, "cy": 55.0, "z": 0.0, "floor": 0, "node_type": "lab"
    },
    "Dept of Bio Technology": {
        "block": "Biotechnology Block",
        "cx": 40.0, "cy": 65.0, "z": 0.0, "floor": 0, "node_type": "lab"
    },
    "Dept of Chemical Engineering": {
        "block": "Chemical Engineering Block",
        "cx": 50.0, "cy": 88.0, "z": 8.0, "floor": 2, "node_type": "lab"
    },
    "Dept of Petroleum Engineering": {
        "block": "Chemical & Petroleum Block",
        "cx": 55.0, "cy": 88.0, "z": 4.0, "floor": 1, "node_type": "lab"
    },
    "Dept of Textile Technology": {
        "block": "Textile & Fashion Block",
        "cx": 60.0, "cy": 88.0, "z": 4.0, "floor": 1, "node_type": "lab"
    },
    "Dept of Science and Humanities": {
        "block": "Science & Humanities Block",
        "cx": 32.0, "cy": 75.0, "z": 0.0, "floor": 0, "node_type": "lab"
    },
    "Dept of Skill Development": {
        "block": "Skill Development Block",
        "cx": 48.0, "cy": 38.0, "z": 0.0, "floor": 0, "node_type": "lab"
    },
    "University Facilities": {
        "block": "University Facilities & Hostels",
        "cx": 50.0, "cy": 18.0, "z": 0.0, "floor": 0, "node_type": "facility"
    }
}

code_lines = [
    '# Auto-generated comprehensive Vignan University 3D campus graph containing ALL 97 tour dropdown locations',
    'import math',
    'from typing import Dict, List, Tuple',
    '',
    'class CampusNode:',
    '    def __init__(self, node_id: str, name: str, section: str, block: str, floor: int, x: float, y: float, z: float, node_type: str, capacity: int = 50, nav_id: str = ""):',
    '        self.node_id = node_id',
    '        self.name = name',
    '        self.section = section',
    '        self.block = block',
    '        self.floor = floor',
    '        self.x = x',
    '        self.y = y',
    '        self.z = z',
    '        self.node_type = node_type',
    '        self.capacity = capacity',
    '        self.nav_id = nav_id',
    '',
    '    def distance_to(self, other: "CampusNode") -> float:',
    '        dx = self.x - other.x',
    '        dy = self.y - other.y',
    '        dz = (self.z - other.z) * 1.5',
    '        return math.sqrt(dx * dx + dy * dy + dz * dz)',
    '',
    '    def to_dict(self):',
    '        return {',
    '            "node_id": self.node_id,',
    '            "name": self.name,',
    '            "section": self.section,',
    '            "block": self.block,',
    '            "floor": self.floor,',
    '            "x": self.x,',
    '            "y": self.y,',
    '            "z": self.z,',
    '            "type": self.node_type,',
    '            "capacity": self.capacity,',
    '            "nav_id": self.nav_id',
    '        }',
    '',
    'def build_campus_building() -> Tuple[Dict[str, CampusNode], List[Tuple[str, str, float]]]:',
    '    nodes: Dict[str, CampusNode] = {}',
    ''
]

# Generate nodes
seen_ids = set()
nodes_by_section = {}

for sec_name, items in tour_data['sections'].items():
    meta = section_meta.get(sec_name, {
        "block": sec_name, "cx": 50.0, "cy": 50.0, "z": 0.0, "floor": 0, "node_type": "room"
    })
    nodes_by_section[sec_name] = []
    
    for idx, item in enumerate(items):
        raw_name = item['name']
        nav_id = item['nav_id']
        
        # Determine ID
        clean_name = re.sub(r'[^a-zA-Z0-9]+', '_', raw_name).strip('_').upper()
        sec_slug = re.sub(r'[^a-zA-Z0-9]+', '_', sec_name.split()[-1]).strip('_').upper()[:4]
        nid = f"VIG_{sec_slug}_{clean_name}"[:32]
        if nid in seen_ids:
            nid = f"{nid}_{idx}"
        seen_ids.add(nid)
        
        # Spatial offset around section center
        angle = (idx / max(len(items), 1)) * 2 * math.pi
        rad = 3.0 + (idx % 3) * 2.0
        x = round(meta['cx'] + rad * math.cos(angle), 1)
        y = round(meta['cy'] + rad * math.sin(angle), 1)
        z = meta['z']
        floor = meta['floor']
        
        # Specific overrides for prominent items
        node_type = meta['node_type']
        if "Play Grounds" in raw_name or "Lawn" in raw_name:
            node_type = "assembly"
        elif "Transport Buses" in raw_name or "Campus view" in raw_name:
            node_type = "exit"
        elif "Health Centre" in raw_name:
            node_type = "facility"
        elif "First Floor" in raw_name or "Civil Services" in raw_name or "Video Conference" in raw_name or "Research Carrels" in raw_name:
            z = 4.0
            floor = 1
        elif "Floor 2" in raw_name or "Reaction" in raw_name or "Bio Chemistry Lab" in raw_name:
            z = 8.0
            floor = 2
            
        nodes_by_section[sec_name].append(nid)
        code_lines.append(f'    nodes["{nid}"] = CampusNode("{nid}", "{raw_name}", "{sec_name}", "{meta["block"]}", {floor}, {x}, {y}, {z}, "{node_type}", nav_id="{nav_id}")')

# Add Hubs, Stairwells, and Corridors
code_lines.extend([
    '',
    '    # --- Campus Arterial Hubs, Corridors & Stairwells ---',
    '    nodes["HUB_CENTRAL_PLAZA"] = CampusNode("HUB_CENTRAL_PLAZA", "Vignan Central Quadrangle Plaza", "Campus Core", "Central Plaza", 0, 50.0, 50.0, 0.0, "corridor")',
    '    nodes["HUB_NORTH_AVENUE"] = CampusNode("HUB_NORTH_AVENUE", "Campus North Arterial Avenue", "Campus Core", "North Avenue", 0, 50.0, 75.0, 0.0, "corridor")',
    '    nodes["HUB_SOUTH_AVENUE"] = CampusNode("HUB_SOUTH_AVENUE", "Campus South Arterial Avenue", "Campus Core", "South Avenue", 0, 50.0, 25.0, 0.0, "corridor")',
    '    nodes["HUB_WEST_AVENUE"] = CampusNode("HUB_WEST_AVENUE", "West Admin Arterial Pathway", "Campus Core", "West Avenue", 0, 20.0, 50.0, 0.0, "corridor")',
    '    nodes["HUB_EAST_AVENUE"] = CampusNode("HUB_EAST_AVENUE", "East Engineering Quad Avenue", "Campus Core", "East Avenue", 0, 80.0, 50.0, 0.0, "corridor")',
    '',
    '    # Vertical Stairwells for Multi-Story Chemical & Library Blocks',
    '    nodes["CHEM_STAIR_A_F0"] = CampusNode("CHEM_STAIR_A_F0", "Chem Block Stairwell A (Ground Landing)", "Stairwells", "Chemical Engg Block", 0, 42.0, 88.0, 0.0, "stairwell")',
    '    nodes["CHEM_STAIR_A_F1"] = CampusNode("CHEM_STAIR_A_F1", "Chem Block Stairwell A (Floor 1)", "Stairwells", "Chemical Engg Block", 1, 42.0, 88.0, 4.0, "stairwell")',
    '    nodes["CHEM_STAIR_A_F2"] = CampusNode("CHEM_STAIR_A_F2", "Chem Block Stairwell A (Floor 2 Landing)", "Stairwells", "Chemical Engg Block", 2, 42.0, 88.0, 8.0, "stairwell")',
    '    nodes["CHEM_STAIR_B_F0"] = CampusNode("CHEM_STAIR_B_F0", "Chem Block Stairwell B (Ground Landing)", "Stairwells", "Chemical Engg Block", 0, 58.0, 88.0, 0.0, "stairwell")',
    '    nodes["CHEM_STAIR_B_F1"] = CampusNode("CHEM_STAIR_B_F1", "Chem Block Stairwell B (Floor 1)", "Stairwells", "Chemical Engg Block", 1, 58.0, 88.0, 4.0, "stairwell")',
    '    nodes["CHEM_STAIR_B_F2"] = CampusNode("CHEM_STAIR_B_F2", "Chem Block Stairwell B (Floor 2 Landing)", "Stairwells", "Chemical Engg Block", 2, 58.0, 88.0, 8.0, "stairwell")',
    '    nodes["LIB_STAIR_F0"] = CampusNode("LIB_STAIR_F0", "NTR Library Stairwell (Ground)", "Stairwells", "NTR Library", 0, 20.0, 82.0, 0.0, "stairwell")',
    '    nodes["LIB_STAIR_F1"] = CampusNode("LIB_STAIR_F1", "NTR Library Stairwell (Floor 1)", "Stairwells", "NTR Library", 1, 20.0, 82.0, 4.0, "stairwell")',
    '',
    '    # Connecting Edges Network',
    '    raw_edges = [',
    '        # Arterial Spine',
    '        ("HUB_CENTRAL_PLAZA", "HUB_NORTH_AVENUE"),',
    '        ("HUB_CENTRAL_PLAZA", "HUB_SOUTH_AVENUE"),',
    '        ("HUB_CENTRAL_PLAZA", "HUB_WEST_AVENUE"),',
    '        ("HUB_CENTRAL_PLAZA", "HUB_EAST_AVENUE"),',
    '        ("HUB_NORTH_AVENUE", "HUB_WEST_AVENUE"),',
    '        ("HUB_NORTH_AVENUE", "HUB_EAST_AVENUE"),',
    '        ("HUB_SOUTH_AVENUE", "HUB_WEST_AVENUE"),',
    '        ("HUB_SOUTH_AVENUE", "HUB_EAST_AVENUE"),',
    '',
    '        # Chemical Block Stair Vertical Connections',
    '        ("CHEM_STAIR_A_F0", "CHEM_STAIR_A_F1"),',
    '        ("CHEM_STAIR_A_F1", "CHEM_STAIR_A_F2"),',
    '        ("CHEM_STAIR_B_F0", "CHEM_STAIR_B_F1"),',
    '        ("CHEM_STAIR_B_F1", "CHEM_STAIR_B_F2"),',
    '        ("CHEM_STAIR_A_F0", "HUB_NORTH_AVENUE"),',
    '        ("CHEM_STAIR_B_F0", "HUB_NORTH_AVENUE"),',
    '        ("LIB_STAIR_F0", "LIB_STAIR_F1"),',
    '        ("LIB_STAIR_F0", "HUB_WEST_AVENUE"),',
    '    ]'
])

# Connect section nodes to closest hubs or section peers
section_hub_mapping = {
    "About Vignan Foundation": "HUB_WEST_AVENUE",
    "NTR Vignan Library": "LIB_STAIR_F0",
    "Dept of Admission / Training": "HUB_WEST_AVENUE",
    "Laboratories": "HUB_NORTH_AVENUE",
    "Dept of Computer Science Engineering": "HUB_EAST_AVENUE",
    "Dept of Electrical & Electronics Engineering": "HUB_EAST_AVENUE",
    "Dept of Electronics & Communication Engineering": "HUB_EAST_AVENUE",
    "Dept of Mechanical Engineering": "HUB_WEST_AVENUE",
    "Dept of Civil Engineering": "HUB_WEST_AVENUE",
    "Dept of Bio Technology": "HUB_NORTH_AVENUE",
    "Dept of Chemical Engineering": "CHEM_STAIR_A_F2",
    "Dept of Petroleum Engineering": "CHEM_STAIR_A_F1",
    "Dept of Textile Technology": "CHEM_STAIR_B_F1",
    "Dept of Science and Humanities": "HUB_NORTH_AVENUE",
    "Dept of Skill Development": "HUB_CENTRAL_PLAZA",
    "University Facilities": "HUB_SOUTH_AVENUE"
}

code_lines.append('    # Connect each room/lab in each section to its hub & daisy chain')
for sec_name, nids in nodes_by_section.items():
    hub = section_hub_mapping.get(sec_name, "HUB_CENTRAL_PLAZA")
    if nids:
        # First node connects to hub
        code_lines.append(f'    raw_edges.append(("{nids[0]}", "{hub}"))')
        # Daisy chain within section
        for i in range(len(nids) - 1):
            code_lines.append(f'    raw_edges.append(("{nids[i]}", "{nids[i+1]}"))')
        # Secondary cross-connections for Chem block to Stair B
        if "Chemical" in sec_name:
            code_lines.append(f'    raw_edges.append(("{nids[-1]}", "CHEM_STAIR_B_F2"))')
        elif "Library" in sec_name:
            code_lines.append(f'    raw_edges.append(("{nids[-1]}", "LIB_STAIR_F1"))')

code_lines.extend([
    '',
    '    edges = []',
    '    for u, v in raw_edges:',
    '        if u in nodes and v in nodes:',
    '            dist = nodes[u].distance_to(nodes[v])',
    '            edges.append((u, v, round(dist, 2)))',
    '',
    '    return nodes, edges',
    ''
])

with open('src/campus_graph.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(code_lines))

print(f"Generated src/campus_graph.py successfully with {len(seen_ids)} tour locations + hubs!")
