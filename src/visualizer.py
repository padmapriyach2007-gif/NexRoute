import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Set, Tuple, Optional
from src.campus_graph import CampusNode

def create_3d_building_figure(
    nodes: Dict[str, CampusNode],
    edges: List[Tuple[str, str, float]],
    evacuation_path: List[str] = None,
    blocked_nodes: Set[str] = None,
    start_node: str = None,
    goal_node: str = None,
    route_focus_only: bool = False,
    filter_section: str = "All Campus"
) -> go.Figure:
    """
    Renders an ultra-clean, high-clarity 3D digital-twin of Vignan University.
    Clutter eliminated:
      - Zero text overlapping: background nodes render as clean color-coded markers.
      - Full room details appear neatly on hover cards.
      - Numbered waypoint badges (Step 1, Step 2...) along the evacuation route.
      - Elevated isometric view with clearly labeled floor planes.
    """
    if evacuation_path is None:
        evacuation_path = []
    if blocked_nodes is None:
        blocked_nodes = set()

    path_node_set = set(evacuation_path)
    
    # Filter nodes
    active_nodes = {}
    for nid, n in nodes.items():
        if route_focus_only:
            # Show only path nodes, blocked nodes, and immediately connected neighbors
            if nid in path_node_set or nid in blocked_nodes:
                active_nodes[nid] = n
        elif filter_section != "All Campus":
            if getattr(n, 'section', '') == filter_section or nid in path_node_set or nid in blocked_nodes:
                active_nodes[nid] = n
        else:
            active_nodes[nid] = n

    path_edges = set()
    for i in range(len(evacuation_path) - 1):
        path_edges.add(tuple(sorted([evacuation_path[i], evacuation_path[i+1]])))

    fig = go.Figure()

    # 1. Semi-Transparent Architectural Floor Plates
    # Ground Floor
    fig.add_trace(go.Mesh3d(
        x=[5, 95, 95, 5],
        y=[5, 5, 95, 95],
        z=[0.0, 0.0, 0.0, 0.0],
        i=[0, 0], j=[1, 2], k=[2, 3],
        opacity=0.04,
        color='#38bdf8',
        name='Floor 0: Ground Campus (0m)',
        hoverinfo='none'
    ))

    # 1st Floor (CSE & Library)
    fig.add_trace(go.Mesh3d(
        x=[10, 95, 95, 10],
        y=[45, 45, 95, 95],
        z=[4.0, 4.0, 4.0, 4.0],
        i=[0, 0], j=[1, 2], k=[2, 3],
        opacity=0.08,
        color='#8b5cf6',
        name='Floor 1: CSE & Library (4m)',
        hoverinfo='none'
    ))

    # 2nd Floor (Chemical Block)
    fig.add_trace(go.Mesh3d(
        x=[38, 65, 65, 38],
        y=[80, 80, 95, 95],
        z=[8.0, 8.0, 8.0, 8.0],
        i=[0, 0], j=[1, 2], k=[2, 3],
        opacity=0.10,
        color='#ec4899',
        name='Floor 2: Chemical & Petroleum (8m)',
        hoverinfo='none'
    ))

    # Floor Level Reference Labels at the boundary
    fig.add_trace(go.Scatter3d(
        x=[8, 8, 38],
        y=[95, 95, 95],
        z=[0.2, 4.2, 8.2],
        mode='text',
        text=[
            "<b>🏢 Floor 0: Ground Level (0m)</b>",
            "<b>🏢 Floor 1: First Floor (4m)</b>",
            "<b>🏢 Floor 2: Second Floor (8m)</b>"
        ],
        textposition="top right",
        textfont=dict(size=10, color=['#38bdf8', '#c084fc', '#f472b6']),
        hoverinfo='none',
        showlegend=False
    ))

    # 2. Corridors & Pathways (Subtle Background Lines)
    edge_x, edge_y, edge_z = [], [], []
    for u, v, _ in edges:
        if u in active_nodes and v in active_nodes:
            edge_key = tuple(sorted([u, v]))
            if edge_key not in path_edges:
                edge_x.extend([nodes[u].x, nodes[v].x, None])
                edge_y.extend([nodes[u].y, nodes[v].y, None])
                edge_z.extend([nodes[u].z, nodes[v].z, None])

    fig.add_trace(go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(color='#334155', width=2),
        hoverinfo='none',
        name='Campus Avenues & Corridors'
    ))

    # 3. Active Evacuation Path (High-Contrast Glowing Neon Green)
    if evacuation_path and len(evacuation_path) > 1:
        path_x, path_y, path_z = [], [], []
        for i in range(len(evacuation_path) - 1):
            u, v = evacuation_path[i], evacuation_path[i+1]
            if u in nodes and v in nodes:
                path_x.extend([nodes[u].x, nodes[v].x, None])
                path_y.extend([nodes[u].y, nodes[v].y, None])
                path_z.extend([nodes[u].z, nodes[v].z, None])

        fig.add_trace(go.Scatter3d(
            x=path_x, y=path_y, z=path_z,
            mode='lines',
            line=dict(color='#10b981', width=10),
            name='🛡️ Active Evacuation Path (A*)',
            hoverinfo='name'
        ))

        # Add Waypoint Markers along the path (Hover info for steps to avoid 3D collisions)
        wp_x, wp_y, wp_z, wp_hover = [], [], [], []
        for idx, nid in enumerate(evacuation_path):
            if nid in nodes and nid != start_node and nid != goal_node:
                n = nodes[nid]
                wp_x.append(n.x)
                wp_y.append(n.y)
                wp_z.append(n.z)
                wp_hover.append(f"<b>Checkpoint {idx+1}:</b> {n.name}<br>Floor: {n.floor}<br>Block: {n.block}")

        if wp_x:
            fig.add_trace(go.Scatter3d(
                x=wp_x, y=wp_y, z=wp_z,
                mode='markers',
                marker=dict(size=8, color='#34d399', line=dict(color='#ffffff', width=1.5)),
                name='🚶 Escape Route Checkpoints',
                hovertext=wp_hover,
                hoverinfo='text'
            ))

    # 4. Clean Background Nodes (Hover-only cards to eliminate text clutter)
    categories = {
        'room': {'color': '#38bdf8', 'size': 5, 'name': 'Offices & Rooms', 'nodes': []},
        'lab': {'color': '#f59e0b', 'size': 6, 'name': 'University Laboratories', 'nodes': []},
        'stairwell': {'color': '#a855f7', 'size': 7, 'name': 'Vertical Stairwells', 'nodes': []},
        'facility': {'color': '#c084fc', 'size': 6, 'name': 'Facilities & Hostels', 'nodes': []},
        'corridor': {'color': '#64748b', 'size': 4, 'name': 'Avenues & Hubs', 'nodes': []},
        'exit': {'color': '#22c55e', 'size': 8, 'name': 'Security Gates', 'nodes': []},
        'assembly': {'color': '#06b6d4', 'size': 10, 'name': 'Safe Assembly Zones', 'nodes': []},
    }

    for nid, node in active_nodes.items():
        if nid not in blocked_nodes and nid != start_node and nid != goal_node and nid not in path_node_set:
            cat = categories.get(node.node_type, categories['room'])
            cat['nodes'].append(node)

    for cat_key, cat in categories.items():
        if cat['nodes']:
            fig.add_trace(go.Scatter3d(
                x=[n.x for n in cat['nodes']],
                y=[n.y for n in cat['nodes']],
                z=[n.z for n in cat['nodes']],
                mode='markers',  # strictly markers to prevent label collisions
                marker=dict(size=cat['size'], color=cat['color'], opacity=0.8),
                name=cat['name'],
                hovertext=[
                    f"<b>{n.name}</b><br>Section: {getattr(n, 'section', n.block)}<br>Block: {n.block}<br>Floor: {n.floor}"
                    for n in cat['nodes']
                ],
                hoverinfo='text'
            ))

    # 5. Blocked / Hazard Nodes (Bold Red Diamond)
    if blocked_nodes:
        b_nodes = [nodes[nid] for nid in blocked_nodes if nid in nodes]
        fig.add_trace(go.Scatter3d(
            x=[n.x for n in b_nodes],
            y=[n.y for n in b_nodes],
            z=[n.z for n in b_nodes],
            mode='markers+text',
            marker=dict(size=14, color='#ef4444', symbol='diamond', line=dict(color='#ffffff', width=2)),
            text=[f"🚨 HAZARD: {n.name.split('(')[0]}" for n in b_nodes],
            textposition='top center',
            textfont=dict(size=11, color='#ef4444'),
            name='🚨 Active Hazard Blockage',
            hovertext=[f"<b>🚨 HAZARD BLOCKED</b><br>{n.name}<br>Status: Non-Traversable" for n in b_nodes],
            hoverinfo='text'
        ))

    # 6. Occupant Start Node (Bright Yellow Circle + Distinct Label)
    if start_node and start_node in nodes:
        sn = nodes[start_node]
        fig.add_trace(go.Scatter3d(
            x=[sn.x], y=[sn.y], z=[sn.z],
            mode='markers+text',
            marker=dict(size=14, color='#eab308', symbol='circle', line=dict(color='#ffffff', width=2)),
            text=["📍 YOU ARE HERE: " + sn.name.split('(')[0]],
            textposition='top center',
            textfont=dict(size=11, color='#fef08a'),
            name='📍 Occupant Starting Position',
            hovertext=f"<b>Current Location</b><br>{sn.name}<br>Block: {sn.block}<br>Floor: {sn.floor}",
            hoverinfo='text'
        ))

    # 7. Safe Assembly Goal Node (Emerald Green Square + Distinct Label)
    if goal_node and goal_node in nodes:
        gn = nodes[goal_node]
        fig.add_trace(go.Scatter3d(
            x=[gn.x], y=[gn.y], z=[gn.z],
            mode='markers+text',
            marker=dict(size=16, color='#10b981', symbol='square', line=dict(color='#ffffff', width=2)),
            text=["🛡️ SAFE ASSEMBLY: " + gn.name.split('(')[0]],
            textposition='top center',
            textfont=dict(size=11, color='#a7f3d0'),
            name='🛡️ Assembly Target',
            hovertext=f"<b>Evacuation Destination</b><br>{gn.name}<br>Block: {gn.block}<br>Floor: {gn.floor}",
            hoverinfo='text'
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='West ← X (m) → East', backgroundcolor="#070b14", gridcolor="#1e293b", showbackground=True),
            yaxis=dict(title='South ← Y (m) → North', backgroundcolor="#070b14", gridcolor="#1e293b", showbackground=True),
            zaxis=dict(title='Floor Elevation (m)', backgroundcolor="#070b14", gridcolor="#1e293b", showbackground=True, range=[-1, 10]),
            camera=dict(
                eye=dict(x=1.35, y=-1.55, z=1.35),
                up=dict(x=0, y=0, z=1)
            )
        ),
        paper_bgcolor="#070b14",
        plot_bgcolor="#070b14",
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="#38bdf8",
            font=dict(family="sans-serif", size=12, color="#f8fafc")
        ),
        margin=dict(l=0, r=0, b=0, t=10),
        showlegend=False
    )

    return fig


def create_2d_campus_map(
    nodes: Dict[str, CampusNode],
    edges: List[Tuple[str, str, float]],
    evacuation_path: List[str] = None,
    blocked_nodes: Set[str] = None,
    start_node: str = None,
    goal_node: str = None,
    route_focus_only: bool = True
) -> go.Figure:
    """
    Renders an ultra-clean, architectural 2D Campus Blueprint.
    Clean aesthetics:
    - Structured building footprints with crisp solid borders & department styling.
    - Clean arterial walkways & promenades (zero messy spiderweb clutter).
    - Luminous multi-layer emerald escape trail with start/goal pins.
    - Minimalist border without distracting numerical axis clutter.
    """
    if evacuation_path is None:
        evacuation_path = []
    if blocked_nodes is None:
        blocked_nodes = set()

    path_edges = set()
    for i in range(len(evacuation_path) - 1):
        path_edges.add(tuple(sorted([evacuation_path[i], evacuation_path[i+1]])))

    path_node_set = set(evacuation_path)

    fig = go.Figure()

    # 1. Campus Perimeter Wall & Masterplan Ground
    fig.add_shape(
        type="rect",
        x0=3, x1=97, y0=3, y1=97,
        fillcolor="rgba(11, 15, 25, 1.0)",
        line=dict(color="#1e293b", width=2),
    )

    # 2. Main Campus Arterial Walkways & Road Network (Clean avenues, not spiderwebs)
    # North-South Central Spine (X: 47 to 53, Y: 18 to 82)
    fig.add_shape(type="rect", x0=47, x1=53, y0=18, y1=82, fillcolor="rgba(30, 41, 59, 0.45)", line=dict(color="rgba(51, 65, 85, 0.4)", width=1))
    # East-West Arterial Promenade (X: 18 to 82, Y: 47 to 53)
    fig.add_shape(type="rect", x0=18, x1=82, y0=47, y1=53, fillcolor="rgba(30, 41, 59, 0.45)", line=dict(color="rgba(51, 65, 85, 0.4)", width=1))
    # West Access Corridor (X: 18 to 24, Y: 30 to 75)
    fig.add_shape(type="rect", x0=18, x1=24, y0=30, y1=75, fillcolor="rgba(30, 41, 59, 0.35)", line=dict(color="rgba(51, 65, 85, 0.3)", width=1))
    # East Engineering Promenade (X: 76 to 82, Y: 30 to 75)
    fig.add_shape(type="rect", x0=76, x1=82, y0=30, y1=75, fillcolor="rgba(30, 41, 59, 0.35)", line=dict(color="rgba(51, 65, 85, 0.3)", width=1))

    # Avenues Roadway Centerlines
    fig.add_trace(go.Scatter(
        x=[50, 50, None, 20, 80, None, 20, 20, None, 79, 79],
        y=[18, 82, None, 50, 50, None, 30, 75, None, 30, 75],
        mode='lines',
        line=dict(color='rgba(71, 85, 105, 0.35)', width=1.5, dash='dash'),
        hoverinfo='none',
        showlegend=False
    ))

    # 3. Clean Building Footprints (Architectural Zoning)
    block_zones = [
        {"name": "🛡️ Open Play Grounds<br><b>(Safe Assembly Area)</b>", "x0": 40, "x1": 70, "y0": 6, "y1": 19, "color": "rgba(6, 182, 212, 0.15)", "border": "#06b6d4"},
        {"name": "🏨 Hostels & Living Quarters", "x0": 38, "x1": 66, "y0": 21, "y1": 31, "color": "rgba(192, 132, 252, 0.12)", "border": "#a855f7"},
        {"name": "🏛️ Admin & Foundation Block", "x0": 8, "x1": 35, "y0": 25, "y1": 43, "color": "rgba(14, 165, 233, 0.14)", "border": "#0ea5e9"},
        {"name": "🏗️ Civil & Mechanical Block", "x0": 8, "x1": 35, "y0": 45, "y1": 62, "color": "rgba(16, 185, 129, 0.14)", "border": "#10b981"},
        {"name": "📚 NTR Central Library Block", "x0": 8, "x1": 35, "y0": 65, "y1": 92, "color": "rgba(59, 130, 246, 0.14)", "border": "#3b82f6"},
        {"name": "⚗️ Chemical & Petroleum Block", "x0": 38, "x1": 66, "y0": 80, "y1": 95, "color": "rgba(244, 63, 94, 0.16)", "border": "#f43f5e"},
        {"name": "💻 Computer Science (CSE) Block", "x0": 68, "x1": 95, "y0": 50, "y1": 72, "color": "rgba(139, 92, 246, 0.14)", "border": "#8b5cf6"},
        {"name": "⚡ ECE / EEE Engineering Block", "x0": 68, "x1": 95, "y0": 25, "y1": 48, "color": "rgba(245, 158, 11, 0.14)", "border": "#f59e0b"},
        {"name": "🌿 Central Quadrangle & Lawn", "x0": 38, "x1": 66, "y0": 45, "y1": 65, "color": "rgba(34, 197, 94, 0.08)", "border": "#22c55e"}
    ]

    for bz in block_zones:
        fig.add_shape(
            type="rect",
            x0=bz["x0"], x1=bz["x1"], y0=bz["y0"], y1=bz["y1"],
            fillcolor=bz["color"],
            line=dict(color=bz["border"], width=1.5, dash="solid"),
        )
        fig.add_annotation(
            x=(bz["x0"] + bz["x1"]) / 2,
            y=(bz["y0"] + bz["y1"]) / 2,
            text=f"<b>{bz['name']}</b>",
            showarrow=False,
            font=dict(size=10, color=bz["border"]),
            opacity=0.92
        )

    # Compass Indicator (Top-Right)
    fig.add_annotation(
        x=93, y=94,
        text="<b>🧭 NORTH (N ↑)</b>",
        showarrow=False,
        font=dict(size=10, color="#38bdf8"),
        bgcolor="rgba(15, 23, 42, 0.9)",
        bordercolor="#0284c7",
        borderwidth=1,
        borderpad=4
    )

    # 4. Background Secondary Connectors (Only shown if exploring full campus, subtle & clean)
    if not route_focus_only:
        edge_x, edge_y = [], []
        for u, v, _ in edges:
            edge_key = tuple(sorted([u, v]))
            if edge_key not in path_edges:
                edge_x.extend([nodes[u].x, nodes[v].x, None])
                edge_y.extend([nodes[u].y, nodes[v].y, None])

        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(color='rgba(51, 65, 85, 0.35)', width=1),
            hoverinfo='none',
            showlegend=False
        ))

        room_nodes = [
            n for nid, n in nodes.items()
            if nid not in blocked_nodes and nid != start_node and nid != goal_node and nid not in path_node_set
        ]
        fig.add_trace(go.Scatter(
            x=[n.x for n in room_nodes],
            y=[n.y for n in room_nodes],
            mode='markers',
            marker=dict(size=5, color='#475569', opacity=0.7),
            name='Campus Locations',
            hovertext=[
                f"<b>{n.name}</b><br>Block: {n.block}<br>Floor: {n.floor}"
                for n in room_nodes
            ],
            hoverinfo='text'
        ))

    # 5. Active Evacuation Path (High-Visibility Dual-Layer Emerald Laser Route)
    if evacuation_path and len(evacuation_path) > 1:
        path_x, path_y = [], []
        for i in range(len(evacuation_path) - 1):
            u, v = evacuation_path[i], evacuation_path[i+1]
            if u in nodes and v in nodes:
                path_x.extend([nodes[u].x, nodes[v].x, None])
                path_y.extend([nodes[u].y, nodes[v].y, None])

        # Layer 1: Emerald Neon Glow
        fig.add_trace(go.Scatter(
            x=path_x, y=path_y,
            mode='lines',
            line=dict(color='rgba(16, 185, 129, 0.30)', width=14),
            hoverinfo='none',
            showlegend=False
        ))

        # Layer 2: Core Laser Line
        fig.add_trace(go.Scatter(
            x=path_x, y=path_y,
            mode='lines',
            line=dict(color='#10b981', width=5),
            name='🛡️ Active Evacuation Path (A*)',
            hoverinfo='name'
        ))

        # Waypoint Markers along the path
        wp_nodes = [nodes[nid] for nid in evacuation_path if nid in nodes and nid != start_node and nid != goal_node]
        if wp_nodes:
            fig.add_trace(go.Scatter(
                x=[n.x for n in wp_nodes],
                y=[n.y for n in wp_nodes],
                mode='markers',
                marker=dict(size=8, color='#34d399', line=dict(color='#ffffff', width=1.5)),
                name='🚶 Escape Route Checkpoints',
                hovertext=[f"<b>Checkpoint:</b> {n.name}<br>Floor: {n.floor}<br>Block: {n.block}" for n in wp_nodes],
                hoverinfo='text'
            ))

    # 6. Active Hazard Blockage (Glowing Red Diamond)
    if blocked_nodes:
        b_nodes = [nodes[nid] for nid in blocked_nodes if nid in nodes]
        fig.add_trace(go.Scatter(
            x=[n.x for n in b_nodes],
            y=[n.y for n in b_nodes],
            mode='markers+text',
            marker=dict(size=15, color='#ef4444', symbol='diamond', line=dict(color='#ffffff', width=2)),
            text=[f"🚨 HAZARD: {n.name.split('(')[0]}" for n in b_nodes],
            textposition='top center',
            textfont=dict(size=10, color='#ef4444'),
            name='🚨 Active Hazard Blockage',
            hovertext=[f"<b>🚨 HAZARD BLOCKED</b><br>{n.name}<br>Status: Non-Traversable" for n in b_nodes],
            hoverinfo='text'
        ))

    # 7. Start Point (Luminous Yellow Marker)
    if start_node and start_node in nodes:
        sn = nodes[start_node]
        fig.add_trace(go.Scatter(
            x=[sn.x], y=[sn.y],
            mode='markers+text',
            marker=dict(size=16, color='#eab308', symbol='circle', line=dict(color='#ffffff', width=2)),
            text=["📍 YOU ARE HERE: " + sn.name.split('(')[0]],
            textposition='bottom center',
            textfont=dict(size=11, color='#fef08a'),
            name='📍 Occupant Starting Point',
            hovertext=f"<b>Current Location</b><br>{sn.name}<br>Floor: {sn.floor}<br>Block: {sn.block}",
            hoverinfo='text'
        ))

    # 8. Safe Assembly Goal Point (Emerald Green Target)
    if goal_node and goal_node in nodes:
        gn = nodes[goal_node]
        fig.add_trace(go.Scatter(
            x=[gn.x], y=[gn.y],
            mode='markers+text',
            marker=dict(size=18, color='#06b6d4', symbol='square', line=dict(color='#ffffff', width=2)),
            text=["🛡️ SAFE ASSEMBLY: " + gn.name.split('(')[0]],
            textposition='bottom center',
            textfont=dict(size=11, color='#a7f3d0'),
            name='🛡️ Safe Assembly Target',
            hovertext=f"<b>Evacuation Destination</b><br>{gn.name}<br>Block: {gn.block}",
            hoverinfo='text'
        ))

    # Minimalist, Clean Architectural Layout
    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[0, 100]
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[0, 100]
        ),
        paper_bgcolor="#070b14",
        plot_bgcolor="#070b14",
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="#38bdf8",
            font=dict(family="sans-serif", size=12, color="#f8fafc")
        ),
        margin=dict(l=10, r=10, b=10, t=10),
        showlegend=False
    )

    return fig
