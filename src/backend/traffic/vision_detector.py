"""
Pathfinder AI Traffic & Human Movement Vision Detector Engine
Provides real-time camera-based detection, multi-object tracking,
virtual line-crossing, entry/exit counting, queue estimation, and telemetry overlays.

Supports:
- Webcams (cv2.VideoCapture)
- Uploaded video files
- RTSP / IP Camera streams
- Built-in Synthetic/Simulated video generator for zero-hardware instant testing
"""

import time
import math
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    CV2_AVAILABLE = False
    np = None
    cv2 = None


SUPPORTED_CLASSES = ["person", "car", "motorcycle", "bicycle", "bus", "truck"]

CLASS_COLORS = {
    "person": (0, 240, 181),       # Emerald Cyan
    "car": (248, 189, 56),         # Sky Blue (BGR: 56, 189, 248) -> in BGR: (248, 189, 56)
    "motorcycle": (68, 150, 244),   # Orange / Coral
    "bicycle": (192, 132, 252),    # Violet / Purple
    "bus": (245, 158, 11),         # Amber
    "truck": (244, 63, 94)         # Crimson Rose
}


@dataclass
class TrackedObject:
    """Represents an anonymously tracked person or vehicle across frames."""
    track_id: int
    cls_name: str
    bbox: Tuple[int, int, int, int]  # (x, y, w, h)
    centroid: Tuple[int, int]         # (cx, cy)
    confidence: float
    first_seen: float
    last_seen: float
    trajectory: List[Tuple[int, int]] = field(default_factory=list)
    crossed_tripwire: bool = False
    crossing_direction: Optional[str] = None  # "INBOUND", "OUTBOUND", or None
    estimated_speed_px_per_s: float = 0.0
    is_queued: bool = False
    disappeared_frames: int = 0


@dataclass
class VisionDetectionMetrics:
    """Telemetry metrics emitted by the vision detector for analytics."""
    timestamp: str
    fps: float
    latency_ms: float
    active_tracks: int
    pedestrian_count: int
    vehicle_count: int
    counts_by_class: Dict[str, int]
    inbound_count: int
    outbound_count: int
    people_per_min: float
    vehicles_per_min: float
    queue_length: int
    environment_type: str  # "INDOOR" or "OUTDOOR"
    connection_status: str  # "CONNECTED", "RECONNECTING", "STANDBY", "OFFLINE"
    source_type: str       # "WEBCAM", "VIDEO_FILE", "RTSP", "SYNTHETIC"
    camera_id: str


class VisionDetectorEngine:
    """
    Core Computer Vision & Object Tracking Engine for Pathfinder.
    Adheres strictly to privacy guidelines (zero facial recognition, ephemeral IDs).
    """

    def __init__(
        self,
        camera_id: str = "CAM_MAIN_01",
        environment_type: str = "OUTDOOR",
        tripwire_y_ratio: float = 0.55,
        tripwire_orientation: str = "HORIZONTAL"
    ):
        self.camera_id = camera_id
        self.environment_type = environment_type.upper()
        self.tripwire_y_ratio = tripwire_y_ratio
        self.tripwire_orientation = tripwire_orientation

        self.source_type: str = "SYNTHETIC"
        self.source_path: Optional[str] = None
        self.cap: Optional[Any] = None
        self.connection_status: str = "STANDBY"

        self.next_track_id: int = 100
        self.tracks: Dict[int, TrackedObject] = {}
        self.max_disappeared_frames: int = 15
        self.max_distance_threshold: float = 85.0

        # Cumulative event counters
        self.total_inbound: int = 0
        self.total_outbound: int = 0
        self.counts_by_class: Dict[str, int] = {c: 0 for c in SUPPORTED_CLASSES}

        # Rate calculations (timestamps of events)
        self.recent_pedestrian_crossings: List[float] = []
        self.recent_vehicle_crossings: List[float] = []

        # Synthetic generator state
        self._synthetic_objects: List[Dict[str, Any]] = []
        self._last_frame_time: float = time.time()
        self._init_synthetic_scenario()

    def _init_synthetic_scenario(self):
        """Initializes realistic objects for synthetic video generation."""
        self._synthetic_objects.clear()
        if self.environment_type == "INDOOR":
            # Indoor scenario: People walking in an entrance/corridor
            for i in range(5):
                direction = 1 if i % 2 == 0 else -1
                y_pos = random.randint(60, 400)
                x_pos = 50 + i * 110
                self._synthetic_objects.append({
                    "id_seed": i,
                    "cls": "person",
                    "x": float(x_pos),
                    "y": float(y_pos),
                    "w": 38,
                    "h": 82,
                    "vx": random.uniform(-0.5, 0.5),
                    "vy": direction * random.uniform(2.2, 4.5),
                    "color": (0, 240, 181)
                })
        else:
            # Outdoor scenario: Vehicles and pedestrians at an intersection/corridor
            mix = [
                ("car", 58, 105, 5.5, 1),
                ("car", 60, 110, 4.8, -1),
                ("motorcycle", 32, 60, 6.2, 1),
                ("bus", 75, 175, 3.8, -1),
                ("truck", 72, 160, 3.4, 1),
                ("bicycle", 30, 52, 3.0, 1),
                ("person", 28, 65, 1.8, -1),
                ("person", 26, 62, 1.6, 1)
            ]
            for i, (cls_name, w, h, speed, direction) in enumerate(mix):
                lane_x = 70 + (i % 4) * 135 + random.randint(-15, 15)
                start_y = random.randint(40, 420)
                self._synthetic_objects.append({
                    "id_seed": i,
                    "cls": cls_name,
                    "x": float(lane_x),
                    "y": float(start_y),
                    "w": w,
                    "h": h,
                    "vx": random.uniform(-0.2, 0.2),
                    "vy": direction * (speed + random.uniform(-0.4, 0.4)),
                    "color": CLASS_COLORS.get(cls_name, (200, 200, 200))
                })

    def open_source(self, source_type: str = "SYNTHETIC", source_path: Optional[str] = None) -> bool:
        """Opens camera, uploaded video file, or initializes synthetic engine."""
        self.source_type = source_type.upper()
        self.source_path = source_path

        if self.cap is not None and hasattr(self.cap, "release"):
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

        if self.source_type == "SYNTHETIC":
            self.connection_status = "CONNECTED"
            self._init_synthetic_scenario()
            return True

        if not CV2_AVAILABLE:
            self.connection_status = "OFFLINE"
            return False

        try:
            if self.source_type == "WEBCAM":
                cam_idx = int(source_path) if (source_path and source_path.isdigit()) else 0
                self.cap = cv2.VideoCapture(cam_idx)
            elif self.source_type in ["VIDEO_FILE", "RTSP"]:
                if not source_path:
                    self.connection_status = "OFFLINE"
                    return False
                self.cap = cv2.VideoCapture(source_path)

            if self.cap and self.cap.isOpened():
                self.connection_status = "CONNECTED"
                return True
            else:
                self.connection_status = "OFFLINE"
                return False
        except Exception:
            self.connection_status = "OFFLINE"
            return False

    def close_source(self):
        """Closes camera device and releases memory."""
        if self.cap is not None and hasattr(self.cap, "release"):
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
        self.connection_status = "STANDBY"

    def process_frame(self) -> Tuple[Optional[np.ndarray], VisionDetectionMetrics]:
        """
        Reads one frame, runs object detection, tracks objects, evaluates virtual tripwires,
        draws HUD overlays, and returns (annotated_frame, telemetry_metrics).
        """
        start_time = time.time()
        frame = None

        # 1. Acquire raw frame
        if self.source_type == "SYNTHETIC" or not CV2_AVAILABLE or self.cap is None or not self.cap.isOpened():
            frame = self._generate_synthetic_frame()
        else:
            ret, raw_frame = self.cap.read()
            if not ret or raw_frame is None:
                # Video ended or camera disconnected: rewind or fallback to synthetic
                if self.source_type == "VIDEO_FILE" and self.cap:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, raw_frame = self.cap.read()
                if not ret or raw_frame is None:
                    frame = self._generate_synthetic_frame()
                else:
                    frame = raw_frame
            else:
                frame = raw_frame

        if frame is None:
            # Fallback black canvas
            frame = np.zeros((480, 640, 3), dtype=np.uint8) if CV2_AVAILABLE else None

        frame_h, frame_w = frame.shape[:2] if frame is not None else (480, 640)

        # 2. Extract Detections
        detections = self._detect_objects(frame)

        # 3. Update Multi-Object Tracker (Centroid / IoU association)
        self._update_tracks(detections, frame_w, frame_h)

        # 4. Tripwire & Queue Analysis
        queue_count = self._evaluate_tripwire_and_queue(frame_w, frame_h)

        # 5. Calculate Rates (People per minute, Vehicles per minute)
        now_ts = time.time()
        one_min_ago = now_ts - 60.0
        self.recent_pedestrian_crossings = [t for t in self.recent_pedestrian_crossings if t >= one_min_ago]
        self.recent_vehicle_crossings = [t for t in self.recent_vehicle_crossings if t >= one_min_ago]

        ppm = float(len(self.recent_pedestrian_crossings))
        vpm = float(len(self.recent_vehicle_crossings))

        latency_ms = (time.time() - start_time) * 1000.0
        fps = 1000.0 / max(1.0, latency_ms)

        # Count active tracks
        pedestrian_active = sum(1 for t in self.tracks.values() if t.cls_name == "person")
        vehicle_active = sum(1 for t in self.tracks.values() if t.cls_name != "person")

        metrics = VisionDetectionMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            fps=round(fps, 1),
            latency_ms=round(latency_ms, 1),
            active_tracks=len(self.tracks),
            pedestrian_count=pedestrian_active,
            vehicle_count=vehicle_active,
            counts_by_class=dict(self.counts_by_class),
            inbound_count=self.total_inbound,
            outbound_count=self.total_outbound,
            people_per_min=ppm,
            vehicles_per_min=vpm,
            queue_length=queue_count,
            environment_type=self.environment_type,
            connection_status=self.connection_status,
            source_type=self.source_type,
            camera_id=self.camera_id
        )

        # 6. Render HUD Overlays onto Frame
        annotated_frame = self._render_hud_overlay(frame, metrics, frame_w, frame_h)

        return annotated_frame, metrics

    def _generate_synthetic_frame(self) -> np.ndarray:
        """Generates realistic synthetic video frames with smooth animations."""
        if not CV2_AVAILABLE:
            return None

        width, height = 640, 420
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Draw realistic background environment
        if self.environment_type == "INDOOR":
            # Glass corridor / building entrance floor
            frame[:] = (22, 27, 34)  # Dark slate
            # Floor tile perspective grid
            for x in range(0, width, 60):
                cv2.line(frame, (x, 0), (x, height), (35, 43, 56), 1)
            for y in range(0, height, 45):
                cv2.line(frame, (0, y), (width, y), (35, 43, 56), 1)
            # Doorway boundary pillars
            cv2.rectangle(frame, (0, 0), (45, height), (15, 23, 42), -1)
            cv2.rectangle(frame, (width - 45, 0), (width, height), (15, 23, 42), -1)
            cv2.putText(frame, "INDOOR ZONE: ENTRANCE CONCOURSE 4", (55, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (148, 163, 184), 1, cv2.LINE_AA)
        else:
            # Asphalt multi-lane road
            frame[:] = (20, 24, 33)
            # Curbs
            cv2.rectangle(frame, (0, 0), (35, height), (30, 41, 59), -1)
            cv2.rectangle(frame, (width - 35, 0), (width, height), (30, 41, 59), -1)
            # Dashed lane markings
            for lane_x in [180, 320, 460]:
                for seg_y in range(0, height, 40):
                    cv2.line(frame, (lane_x, seg_y), (lane_x, seg_y + 20), (255, 255, 255), 2)
            cv2.putText(frame, "OUTDOOR CORRIDOR: NH-16 ARTERIAL INTERSECTION", (45, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, (148, 163, 184), 1, cv2.LINE_AA)

        # Animate synthetic objects
        for obj in self._synthetic_objects:
            obj["x"] += obj["vx"]
            obj["y"] += obj["vy"]

            # Wrap around boundaries
            if obj["y"] > height + 80:
                obj["y"] = -80
                obj["x"] = random.uniform(60, width - 80)
            elif obj["y"] < -80:
                obj["y"] = height + 80
                obj["x"] = random.uniform(60, width - 80)

            ox, oy = int(obj["x"]), int(obj["y"])
            ow, oh = int(obj["w"]), int(obj["h"])
            col = obj["color"]

            # Draw body silhouette
            cv2.rectangle(frame, (ox, oy), (ox + ow, oy + oh), col, -1)
            # Highlight border
            cv2.rectangle(frame, (ox, oy), (ox + ow, oy + oh), (255, 255, 255), 1)

            # Details
            if obj["cls"] == "person":
                # Head circle
                cv2.circle(frame, (ox + ow // 2, oy + 10), 8, (255, 255, 255), -1)
            elif obj["cls"] in ["car", "bus", "truck"]:
                # Windshield strip
                cv2.rectangle(frame, (ox + 4, oy + 8), (ox + ow - 4, oy + 22), (20, 20, 20), -1)

        return frame

    def _detect_objects(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detects objects in frame. When using synthetic stream or OpenCV standard pipeline,
        converts active entities into normalized detections.
        """
        detections = []
        if frame is None:
            return detections

        if self.source_type == "SYNTHETIC":
            # Direct mapping from synthetic engine with realistic confidence noise
            for obj in self._synthetic_objects:
                x, y, w, h = int(obj["x"]), int(obj["y"]), int(obj["w"]), int(obj["h"])
                if 0 <= y <= frame.shape[0] and 0 <= x <= frame.shape[1]:
                    detections.append({
                        "cls": obj["cls"],
                        "bbox": (x, y, w, h),
                        "centroid": (x + w // 2, y + h // 2),
                        "confidence": round(random.uniform(0.85, 0.98), 2)
                    })
        elif CV2_AVAILABLE:
            # Color & contour motion analysis for real webcam / video inputs
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (15, 15), 0)
                edged = cv2.Canny(blurred, 30, 150)
                contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if 450 < area < 40000:
                        x, y, w, h = cv2.boundingRect(cnt)
                        aspect_ratio = float(h) / max(1.0, float(w))
                        cls_name = "person" if aspect_ratio > 1.3 else "car"
                        if w > 120 and h > 80:
                            cls_name = "bus" if aspect_ratio < 1.0 else "truck"

                        detections.append({
                            "cls": cls_name,
                            "bbox": (x, y, w, h),
                            "centroid": (x + w // 2, y + h // 2),
                            "confidence": 0.88
                        })
            except Exception:
                pass

        return detections

    def _update_tracks(self, detections: List[Dict[str, Any]], frame_w: int, frame_h: int):
        """ByteTrack-style centroid association and track management."""
        now_ts = time.time()

        if len(self.tracks) == 0:
            for d in detections:
                self._register_track(d, now_ts)
            return

        track_ids = list(self.tracks.keys())
        track_centroids = [self.tracks[tid].centroid for tid in track_ids]

        if len(detections) == 0:
            for tid in track_ids:
                self.tracks[tid].disappeared_frames += 1
                if self.tracks[tid].disappeared_frames > self.max_disappeared_frames:
                    self._deregister_track(tid)
            return

        # Compute pairwise Euclidean distance matrix
        det_centroids = [d["centroid"] for d in detections]
        used_tracks = set()
        used_detections = set()

        # Greedy nearest-centroid matching
        matches = []
        for d_idx, (dcx, dcy) in enumerate(det_centroids):
            for t_idx, tid in enumerate(track_ids):
                if tid in used_tracks:
                    continue
                tcx, tcy = track_centroids[t_idx]
                dist = math.hypot(dcx - tcx, dcy - tcy)
                if dist < self.max_distance_threshold:
                    matches.append((dist, tid, d_idx))

        matches.sort(key=lambda m: m[0])

        for dist, tid, d_idx in matches:
            if tid in used_tracks or d_idx in used_detections:
                continue
            used_tracks.add(tid)
            used_detections.add(d_idx)

            d = detections[d_idx]
            trk = self.tracks[tid]
            prev_cx, prev_cy = trk.centroid
            trk.bbox = d["bbox"]
            trk.centroid = d["centroid"]
            trk.confidence = d["confidence"]
            trk.cls_name = d["cls"]
            trk.last_seen = now_ts
            trk.disappeared_frames = 0
            trk.trajectory.append(d["centroid"])
            if len(trk.trajectory) > 25:
                trk.trajectory.pop(0)

            # Speed px/s estimate
            dt = max(0.01, now_ts - trk.first_seen)
            dx = d["centroid"][0] - prev_cx
            dy = d["centroid"][1] - prev_cy
            trk.estimated_speed_px_per_s = math.hypot(dx, dy) / 0.05

        # Handle unmatched existing tracks
        for tid in track_ids:
            if tid not in used_tracks:
                self.tracks[tid].disappeared_frames += 1
                if self.tracks[tid].disappeared_frames > self.max_disappeared_frames:
                    self._deregister_track(tid)

        # Handle new unmatched detections
        for d_idx, d in enumerate(detections):
            if d_idx not in used_detections:
                self._register_track(d, now_ts)

    def _register_track(self, detection: Dict[str, Any], timestamp: float):
        """Registers a new tracked entity."""
        tid = self.next_track_id
        self.next_track_id += 1
        trk = TrackedObject(
            track_id=tid,
            cls_name=detection["cls"],
            bbox=detection["bbox"],
            centroid=detection["centroid"],
            confidence=detection["confidence"],
            first_seen=timestamp,
            last_seen=timestamp,
            trajectory=[detection["centroid"]],
            crossed_tripwire=False
        )
        self.tracks[tid] = trk

    def _deregister_track(self, track_id: int):
        """Removes an expired track."""
        if track_id in self.tracks:
            del self.tracks[track_id]

    def _evaluate_tripwire_and_queue(self, frame_w: int, frame_h: int) -> int:
        """Evaluates virtual tripwire line crossings and estimates queue length."""
        now_ts = time.time()
        tripwire_y = int(frame_h * self.tripwire_y_ratio)
        queue_count = 0

        for trk in self.tracks.values():
            # Check for vehicle queue: stopped/slow vehicles near intersection
            if trk.cls_name in ["car", "bus", "truck", "motorcycle"]:
                if trk.estimated_speed_px_per_s < 20.0 and (0.35 * frame_h <= trk.centroid[1] <= 0.85 * frame_h):
                    trk.is_queued = True
                    queue_count += 1
                else:
                    trk.is_queued = False

            # Check line-crossing
            if not trk.crossed_tripwire and len(trk.trajectory) >= 2:
                prev_y = trk.trajectory[-2][1]
                curr_y = trk.trajectory[-1][1]

                # Crossed from above to below (Downwards / INBOUND)
                if prev_y < tripwire_y <= curr_y:
                    trk.crossed_tripwire = True
                    trk.crossing_direction = "INBOUND"
                    self.total_inbound += 1
                    self.counts_by_class[trk.cls_name] = self.counts_by_class.get(trk.cls_name, 0) + 1
                    if trk.cls_name == "person":
                        self.recent_pedestrian_crossings.append(now_ts)
                    else:
                        self.recent_vehicle_crossings.append(now_ts)

                # Crossed from below to above (Upwards / OUTBOUND)
                elif prev_y > tripwire_y >= curr_y:
                    trk.crossed_tripwire = True
                    trk.crossing_direction = "OUTBOUND"
                    self.total_outbound += 1
                    self.counts_by_class[trk.cls_name] = self.counts_by_class.get(trk.cls_name, 0) + 1
                    if trk.cls_name == "person":
                        self.recent_pedestrian_crossings.append(now_ts)
                    else:
                        self.recent_vehicle_crossings.append(now_ts)

        return queue_count

    def _render_hud_overlay(
        self,
        frame: np.ndarray,
        metrics: VisionDetectionMetrics,
        frame_w: int,
        frame_h: int
    ) -> np.ndarray:
        """Renders glassmorphic HUD overlays, bounding boxes, labels, and statistics."""
        if not CV2_AVAILABLE or frame is None:
            return frame

        out = frame.copy()
        tripwire_y = int(frame_h * self.tripwire_y_ratio)

        # 1. Virtual Tripwire Line with Glow
        cv2.line(out, (0, tripwire_y), (frame_w, tripwire_y), (56, 189, 248), 2)
        cv2.line(out, (0, tripwire_y - 1), (frame_w, tripwire_y - 1), (0, 240, 181), 1)

        # Direction indicator labels on tripwire
        cv2.putText(out, "▼ INBOUND", (20, tripwire_y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 240, 181), 1, cv2.LINE_AA)
        cv2.putText(out, "▲ OUTBOUND", (frame_w - 110, tripwire_y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (56, 189, 248), 1, cv2.LINE_AA)

        # 2. Draw Object Bounding Boxes, Temporary IDs, and Trajectories
        for trk in self.tracks.values():
            x, y, w, h = trk.bbox
            col = CLASS_COLORS.get(trk.cls_name, (255, 255, 255))

            # Bounding box
            cv2.rectangle(out, (x, y), (x + w, y + h), col, 2)

            # Trajectory polyline
            if len(trk.trajectory) > 1:
                pts = np.array(trk.trajectory, np.int32).reshape((-1, 1, 2))
                cv2.polylines(out, [pts], False, col, 1)

            # Badge pill
            label = f"#{trk.track_id} {trk.cls_name.upper()} {int(trk.confidence*100)}%"
            if trk.is_queued:
                label += " [QUEUED]"

            (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.40, 1)
            cv2.rectangle(out, (x, max(0, y - lh - 6)), (x + lw + 6, max(lh + 6, y)), col, -1)
            cv2.putText(out, label, (x + 3, max(lh, y - 4)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, (15, 23, 42), 1, cv2.LINE_AA)

        # 3. Top Glassmorphic Telemetry HUD
        hud_h = 36
        sub_img = out[0:hud_h, 0:frame_w]
        dark_rect = np.zeros(sub_img.shape, dtype=np.uint8)
        dark_rect[:] = (15, 23, 42)
        res = cv2.addWeighted(sub_img, 0.25, dark_rect, 0.75, 1.0)
        out[0:hud_h, 0:frame_w] = res
        cv2.line(out, (0, hud_h), (frame_w, hud_h), (56, 189, 248), 1)

        # Telemetry text
        hud_text = (
            f"FPS: {metrics.fps} | LAT: {metrics.latency_ms}ms | "
            f"IN: {metrics.inbound_count} | OUT: {metrics.outbound_count} | "
            f"PED: {metrics.pedestrian_count} ({metrics.people_per_min}/m) | "
            f"VEH: {metrics.vehicle_count} ({metrics.vehicles_per_min}/m)"
        )
        if metrics.queue_length > 0:
            hud_text += f" | QUEUE: {metrics.queue_length}"

        cv2.putText(out, hud_text, (10, 23),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (248, 250, 252), 1, cv2.LINE_AA)

        return out
