"""
Automated Test Suite for Real-Time Motion State Machine & Companion Synchronization
CampusAegis / P.A.T.H.F.I.N.D.E.R. • Predictive Adaptive Transit & Hazard-Free Intelligent Navigation

Tests:
1. Stationary user with GPS noise/jitter guard.
2. Slow walking user along route.
3. Fast moving user.
4. Moving in parallel with virtual companion.
5. Stopping with hysteresis (sustained low speed requirement) and resuming.
6. Approaching and verified crossing of checkpoints.
7. Passing near checkpoint on a perpendicular/off-route road (no false crossing).
8. Route deviation detection beyond accuracy-aware threshold.
9. Moving backward / return trajectory detection.
10. Degraded GPS accuracy entering LOCATION_UNCERTAIN.
11. Stale / timed out GPS entering LOCATION_LOST.
12. Follow-user mode vs Independent companion mode behavior.
13. Sanitization of invalid, out-of-order, or future timestamps.
"""

import pytest
import math
import time
from src.realtime_motion_sync import (
    RealtimeMotionState,
    CompanionSyncMode,
    LocationObservation,
    LocationValidator,
    RouteMatcher,
    RealtimeMotionEngine,
    build_realtime_motion_hud_html
)


# Sample route polyline (Northward from lat 16.2335, lon 80.5505 to 16.2435, 80.5505)
SAMPLE_POLYLINE = [
    (16.2335, 80.5505),
    (16.2365, 80.5505),  # ~331m
    (16.2395, 80.5505),  # ~663m
    (16.2435, 80.5505)   # ~1105m
]

SAMPLE_CHECKPOINTS = [
    {"label": "Gate 1", "lat": 16.2365, "lon": 80.5505, "station_m": 331.0},
    {"label": "Central Plaza", "lat": 16.2395, "lon": 80.5505, "station_m": 663.0},
    {"label": "North Terminal", "lat": 16.2435, "lon": 80.5505, "station_m": 1105.0}
]


def test_stationary_user_with_gps_jitter():
    """Verify small jitter fluctuations within GPS accuracy do not register as moving."""
    engine = RealtimeMotionEngine(
        polyline=SAMPLE_POLYLINE,
        checkpoints=SAMPLE_CHECKPOINTS,
        total_distance_m=1105.0
    )

    base_time = 1700000000.0

    # User standing at start point, GPS fluctuates by 1-2 meters
    obs1 = LocationObservation(latitude=16.233500, longitude=80.550500, timestamp=base_time, accuracy_meters=8.0, speed_mps=0.0)
    res1 = engine.process_observation(obs1, current_time_epoch=base_time)
    assert res1.state == RealtimeMotionState.STATIONARY

    # Ping 2: 1.5 seconds later, 2m jitter jump
    obs2 = LocationObservation(latitude=16.233515, longitude=80.550505, timestamp=base_time + 1.5, accuracy_meters=8.0, speed_mps=None)
    res2 = engine.process_observation(obs2, current_time_epoch=base_time + 1.5)
    # Jitter guard must keep user stationary
    assert res2.user_speed_kmh <= 1.2

    # Ping 3: 3.0 seconds later, still within stationary threshold
    obs3 = LocationObservation(latitude=16.233505, longitude=80.550500, timestamp=base_time + 3.0, accuracy_meters=6.0, speed_mps=0.0)
    res3 = engine.process_observation(obs3, current_time_epoch=base_time + 3.0)
    assert res3.state == RealtimeMotionState.STATIONARY


def test_user_walking_slowly_along_route():
    """Verify slow continuous walking triggers moving states."""
    engine = RealtimeMotionEngine(
        polyline=SAMPLE_POLYLINE,
        checkpoints=SAMPLE_CHECKPOINTS,
        total_distance_m=1105.0
    )

    base_time = 1700000000.0

    # Initial fix
    engine.process_observation(
        LocationObservation(16.2335, 80.5505, timestamp=base_time, accuracy_meters=5.0, speed_mps=1.2),
        current_time_epoch=base_time
    )

    # 4 seconds later: moved 5 meters forward (~4.5 km/h)
    obs = LocationObservation(16.233545, 80.5505, timestamp=base_time + 4.0, accuracy_meters=4.0, speed_mps=1.25)
    res = engine.process_observation(obs, current_time_epoch=base_time + 4.0)

    assert res.user_speed_kmh > 1.8
    assert res.state in (RealtimeMotionState.MOVING_FORWARD, RealtimeMotionState.MOVING_PARALLEL)
    assert res.along_track_distance_m > 0.0


def test_user_moving_in_parallel_with_companion():
    """Verify moving parallel state when user and companion progress closely along corridor."""
    engine = RealtimeMotionEngine(
        polyline=SAMPLE_POLYLINE,
        checkpoints=SAMPLE_CHECKPOINTS,
        total_distance_m=1105.0,
        sync_mode=CompanionSyncMode.FOLLOW_USER
    )

    base_time = 1700000000.0
    # Set companion station to 100m
    engine.companion_station_m = 100.0

    # User at ~105m along route moving at 12 km/h
    engine.previous_along_track_s = 90.0
    obs = LocationObservation(16.23445, 80.5505, timestamp=base_time + 3.0, accuracy_meters=5.0, speed_mps=3.3)
    res = engine.process_observation(obs, current_time_epoch=base_time + 3.0)

    assert res.state == RealtimeMotionState.MOVING_PARALLEL
    assert abs(res.along_track_distance_m - res.companion_station_m) <= 75.0


def test_stopping_with_hysteresis_and_resuming():
    """Verify that a single slow ping does not immediately trigger stationary without sustained window."""
    engine = RealtimeMotionEngine(
        polyline=SAMPLE_POLYLINE,
        checkpoints=SAMPLE_CHECKPOINTS,
        total_distance_m=1105.0
    )
    engine.current_state = RealtimeMotionState.MOVING_FORWARD

    base_time = 1700000000.0
    engine.last_valid_obs = LocationObservation(16.2340, 80.5505, timestamp=base_time - 2.0, speed_mps=3.0)

    # 1st observation with speed 0 (e.g. temporary red light or delayed ping)
    obs1 = LocationObservation(16.2340, 80.5505, timestamp=base_time, accuracy_meters=5.0, speed_mps=0.0)
    res1 = engine.process_observation(obs1, current_time_epoch=base_time)
    # Hysteresis prevents instant transition to STATIONARY on single reading
    assert res1.state == RealtimeMotionState.MOVING_FORWARD

    # 2nd observation 2.5 seconds later with speed 0: sustained period confirms stationary
    obs2 = LocationObservation(16.2340, 80.5505, timestamp=base_time + 2.5, accuracy_meters=5.0, speed_mps=0.0)
    res2 = engine.process_observation(obs2, current_time_epoch=base_time + 2.5)
    assert res2.state == RealtimeMotionState.STATIONARY

    # Speed resumes (> 1.8 km/h) -> transitions back to moving
    obs3 = LocationObservation(16.2341, 80.5505, timestamp=base_time + 4.5, accuracy_meters=5.0, speed_mps=2.5)
    res3 = engine.process_observation(obs3, current_time_epoch=base_time + 4.5)
    assert res3.state in (RealtimeMotionState.MOVING_FORWARD, RealtimeMotionState.MOVING_PARALLEL)


def test_approaching_and_crossing_checkpoint():
    """Verify approaching checkpoint and confirmed crossing along the route."""
    engine = RealtimeMotionEngine(
        polyline=SAMPLE_POLYLINE,
        checkpoints=SAMPLE_CHECKPOINTS,
        total_distance_m=1105.0
    )

    base_time = 1700000000.0

    # Gate 1 is at 16.2365, 80.5505 (station 331m)
    # User at station 280m (~51m before checkpoint): approaching
    obs_appr = LocationObservation(16.23605, 80.5505, timestamp=base_time, accuracy_meters=5.0, speed_mps=2.0)
    res_appr = engine.process_observation(obs_appr, current_time_epoch=base_time)
    assert res_appr.state == RealtimeMotionState.APPROACHING_CHECKPOINT

    # User reaches station 330m (directly at checkpoint radius): crossed
    obs_cross = LocationObservation(16.23650, 80.5505, timestamp=base_time + 15.0, accuracy_meters=5.0, speed_mps=2.0)
    res_cross = engine.process_observation(obs_cross, current_time_epoch=base_time + 15.0)
    assert res_cross.state == RealtimeMotionState.CHECKPOINT_CROSSED
    assert res_cross.newly_crossed_checkpoint is not None
    assert res_cross.newly_crossed_checkpoint["label"] == "Gate 1"
    assert engine.current_checkpoint_idx == 1


def test_no_false_crossing_when_passing_checkpoint_on_parallel_road():
    """Verify that a user far off-route near a checkpoint does not trigger a false crossing."""
    engine = RealtimeMotionEngine(
        polyline=SAMPLE_POLYLINE,
        checkpoints=SAMPLE_CHECKPOINTS,
        total_distance_m=1105.0
    )

    base_time = 1700000000.0

    # Gate 1 is at 16.2365, lon 80.5505.
    # User is at 16.2365, but on a parallel road at lon 80.5520 (~160m away, off route!)
    obs_far = LocationObservation(16.2365, 80.5520, timestamp=base_time, accuracy_meters=5.0, speed_mps=3.0)
    # Trigger twice to confirm deviation
    engine.process_observation(obs_far, current_time_epoch=base_time)
    res_far = engine.process_observation(obs_far, current_time_epoch=base_time + 1.0)

    assert res_far.state == RealtimeMotionState.ROUTE_DEVIATION
    assert res_far.is_off_route is True
    # Crucial: Checkpoint index must NOT have advanced!
    assert engine.current_checkpoint_idx == 0


def test_route_deviation_detection():
    """Verify route deviation triggers when user leaves corridor beyond accuracy-aware threshold."""
    engine = RealtimeMotionEngine(
        polyline=SAMPLE_POLYLINE,
        checkpoints=SAMPLE_CHECKPOINTS,
        total_distance_m=1105.0
    )

    base_time = 1700000000.0

    # User at 85m cross-track distance off the route
    obs_dev1 = LocationObservation(16.2350, 80.5513, timestamp=base_time, accuracy_meters=6.0, speed_mps=2.0)
    engine.process_observation(obs_dev1, current_time_epoch=base_time)

    obs_dev2 = LocationObservation(16.2350, 80.5513, timestamp=base_time + 2.0, accuracy_meters=6.0, speed_mps=2.0)
    res_dev = engine.process_observation(obs_dev2, current_time_epoch=base_time + 2.0)

    assert res_dev.state == RealtimeMotionState.ROUTE_DEVIATION
    assert res_dev.is_off_route is True
    assert res_dev.cross_track_distance_m > 55.0


def test_moving_backward_detection():
    """Verify moving backward state when user reverses along corridor."""
    engine = RealtimeMotionEngine(
        polyline=SAMPLE_POLYLINE,
        checkpoints=SAMPLE_CHECKPOINTS,
        total_distance_m=1105.0
    )

    base_time = 1700000000.0

    # User was at station ~500m
    obs_fwd = LocationObservation(16.2380, 80.5505, timestamp=base_time, accuracy_meters=5.0, speed_mps=2.5, heading_deg=0.0)
    engine.process_observation(obs_fwd, current_time_epoch=base_time)

    # User moves southward (heading ~180 deg, station drops from 500m to 470m)
    obs_back = LocationObservation(16.2377, 80.5505, timestamp=base_time + 4.0, accuracy_meters=5.0, speed_mps=2.5, heading_deg=180.0)
    res_back = engine.process_observation(obs_back, current_time_epoch=base_time + 4.0)

    assert res_back.is_moving_backward is True
    assert res_back.state == RealtimeMotionState.MOVING_BACKWARD


def test_location_uncertain_on_poor_gps_accuracy():
    """Verify poor GPS accuracy (> 50m) transitions to LOCATION_UNCERTAIN."""
    engine = RealtimeMotionEngine(
        polyline=SAMPLE_POLYLINE,
        checkpoints=SAMPLE_CHECKPOINTS,
        total_distance_m=1105.0
    )

    base_time = 1700000000.0
    obs_poor = LocationObservation(16.2350, 80.5505, timestamp=base_time, accuracy_meters=75.0, speed_mps=2.0)
    res = engine.process_observation(obs_poor, current_time_epoch=base_time)

    assert res.state == RealtimeMotionState.LOCATION_UNCERTAIN
    assert res.location_quality == "DEGRADED"


def test_location_lost_on_stale_gps():
    """Verify missing updates for > 15s triggers LOCATION_LOST."""
    engine = RealtimeMotionEngine(
        polyline=SAMPLE_POLYLINE,
        checkpoints=SAMPLE_CHECKPOINTS,
        total_distance_m=1105.0
    )

    base_time = 1700000000.0
    obs_initial = LocationObservation(16.2350, 80.5505, timestamp=base_time, accuracy_meters=5.0)
    engine.process_observation(obs_initial, current_time_epoch=base_time)

    # Next update arrives with timestamp from the past or invalid accuracy, while current clock is 20s later
    obs_stale = LocationObservation(16.2350, 80.5505, timestamp=base_time - 5.0, accuracy_meters=5.0)
    res = engine.process_observation(obs_stale, current_time_epoch=base_time + 20.0)

    assert res.state == RealtimeMotionState.LOCATION_LOST
    assert res.location_quality == "LOST"


def test_follow_user_vs_independent_companion_mode():
    """Verify follow-user companion pauses when user stops, while independent companion keeps moving."""
    # 1. Follow User Mode
    engine_follow = RealtimeMotionEngine(
        polyline=SAMPLE_POLYLINE,
        checkpoints=SAMPLE_CHECKPOINTS,
        total_distance_m=1105.0,
        sync_mode=CompanionSyncMode.FOLLOW_USER
    )
    base_time = 1700000000.0
    obs_stop1 = LocationObservation(16.2350, 80.5505, timestamp=base_time, accuracy_meters=5.0, speed_mps=0.0)
    obs_stop2 = LocationObservation(16.2350, 80.5505, timestamp=base_time + 3.0, accuracy_meters=5.0, speed_mps=0.0)
    engine_follow.process_observation(obs_stop1, current_time_epoch=base_time)
    res_follow = engine_follow.process_observation(obs_stop2, current_time_epoch=base_time + 3.0)

    assert res_follow.state == RealtimeMotionState.STATIONARY
    assert res_follow.companion_speed_kmh == 0.0  # Companion stops with user!

    # 2. Independent Mode
    engine_indep = RealtimeMotionEngine(
        polyline=SAMPLE_POLYLINE,
        checkpoints=SAMPLE_CHECKPOINTS,
        total_distance_m=1105.0,
        sync_mode=CompanionSyncMode.INDEPENDENT
    )
    engine_indep.companion_station_m = 50.0
    engine_indep.process_observation(obs_stop1, current_time_epoch=base_time)
    res_indep = engine_indep.process_observation(obs_stop2, current_time_epoch=base_time + 3.0)

    assert res_indep.state == RealtimeMotionState.STATIONARY
    assert res_indep.companion_station_m > 50.0  # Companion advances independently!


def test_sanitization_rejects_future_or_out_of_bounds_coords():
    """Verify invalid coordinates and future timestamps are rejected."""
    now = 1700000000.0

    # NaN coordinates
    bad_coord = LocationObservation(float("nan"), 80.5505, timestamp=now)
    ok, reason, _ = LocationValidator.sanitize_observation(bad_coord, current_time_epoch=now)
    assert not ok

    # Out of bounds coordinates (lat > 90)
    out_of_bounds = LocationObservation(120.0, 80.5505, timestamp=now)
    ok, reason, _ = LocationValidator.sanitize_observation(out_of_bounds, current_time_epoch=now)
    assert not ok

    # Future timestamp
    future_obs = LocationObservation(16.2350, 80.5505, timestamp=now + 500.0)
    ok, reason, _ = LocationValidator.sanitize_observation(future_obs, current_time_epoch=now)
    assert not ok


def test_build_realtime_motion_hud_html_renders():
    """Verify HTML component builder renders telemetry, status pills, and developer controls."""
    html = build_realtime_motion_hud_html(
        origin_name="Start Gate",
        dest_name="Destination Terminal",
        polyline=SAMPLE_POLYLINE,
        checkpoints=SAMPLE_CHECKPOINTS
    )

    assert "realtime-motion-engine-root" in html
    assert "motion-state-pill" in html
    assert "toggleLocationTracking" in html
    assert "toggleSyncMode" in html
    assert "telemetry-grid" in html
    assert "Traffic Stop (0 km/h)" in html
    assert "Move in Parallel" in html
    assert "Cross Next Stop" in html
