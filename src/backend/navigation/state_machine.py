"""
Navigation State Machine for Live Virtual Travel Companion
Defines the authoritative state graph, valid transitions, noise filtering,
and hysteresis rules.
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class NavigationState(str, Enum):
    IDLE = "IDLE"
    ROUTE_READY = "ROUTE_READY"
    STARTING = "STARTING"
    MOVING = "MOVING"
    APPROACHING_TURN = "APPROACHING_TURN"
    TURNING = "TURNING"
    TEMPORARILY_STOPPED = "TEMPORARILY_STOPPED"
    TRAFFIC_DELAY = "TRAFFIC_DELAY"
    OFF_ROUTE = "OFF_ROUTE"
    REROUTING = "REROUTING"
    GPS_UNCERTAIN = "GPS_UNCERTAIN"
    RESUMING = "RESUMING"
    ARRIVED = "ARRIVED"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"


# Valid State Transition Graph
VALID_TRANSITIONS: Dict[NavigationState, Set[NavigationState]] = {
    NavigationState.IDLE: {
        NavigationState.ROUTE_READY,
        NavigationState.STARTING,
        NavigationState.CANCELLED
    },
    NavigationState.ROUTE_READY: {
        NavigationState.STARTING,
        NavigationState.MOVING,
        NavigationState.PAUSED,
        NavigationState.CANCELLED
    },
    NavigationState.STARTING: {
        NavigationState.MOVING,
        NavigationState.TEMPORARILY_STOPPED,
        NavigationState.GPS_UNCERTAIN,
        NavigationState.PAUSED,
        NavigationState.CANCELLED
    },
    NavigationState.MOVING: {
        NavigationState.APPROACHING_TURN,
        NavigationState.TURNING,
        NavigationState.TEMPORARILY_STOPPED,
        NavigationState.TRAFFIC_DELAY,
        NavigationState.OFF_ROUTE,
        NavigationState.GPS_UNCERTAIN,
        NavigationState.ARRIVED,
        NavigationState.PAUSED,
        NavigationState.CANCELLED
    },
    NavigationState.APPROACHING_TURN: {
        NavigationState.TURNING,
        NavigationState.MOVING,
        NavigationState.TEMPORARILY_STOPPED,
        NavigationState.OFF_ROUTE,
        NavigationState.GPS_UNCERTAIN,
        NavigationState.ARRIVED,
        NavigationState.PAUSED,
        NavigationState.CANCELLED
    },
    NavigationState.TURNING: {
        NavigationState.MOVING,
        NavigationState.APPROACHING_TURN,
        NavigationState.TEMPORARILY_STOPPED,
        NavigationState.OFF_ROUTE,
        NavigationState.GPS_UNCERTAIN,
        NavigationState.ARRIVED,
        NavigationState.PAUSED,
        NavigationState.CANCELLED
    },
    NavigationState.TEMPORARILY_STOPPED: {
        NavigationState.RESUMING,
        NavigationState.MOVING,
        NavigationState.TRAFFIC_DELAY,
        NavigationState.GPS_UNCERTAIN,
        NavigationState.PAUSED,
        NavigationState.CANCELLED
    },
    NavigationState.TRAFFIC_DELAY: {
        NavigationState.RESUMING,
        NavigationState.MOVING,
        NavigationState.TEMPORARILY_STOPPED,
        NavigationState.GPS_UNCERTAIN,
        NavigationState.PAUSED,
        NavigationState.CANCELLED
    },
    NavigationState.OFF_ROUTE: {
        NavigationState.REROUTING,
        NavigationState.MOVING,
        NavigationState.PAUSED,
        NavigationState.CANCELLED
    },
    NavigationState.REROUTING: {
        NavigationState.MOVING,
        NavigationState.OFF_ROUTE,
        NavigationState.PAUSED,
        NavigationState.CANCELLED
    },
    NavigationState.GPS_UNCERTAIN: {
        NavigationState.MOVING,
        NavigationState.TEMPORARILY_STOPPED,
        NavigationState.APPROACHING_TURN,
        NavigationState.TURNING,
        NavigationState.TRAFFIC_DELAY,
        NavigationState.PAUSED,
        NavigationState.CANCELLED
    },
    NavigationState.RESUMING: {
        NavigationState.MOVING,
        NavigationState.TEMPORARILY_STOPPED,
        NavigationState.APPROACHING_TURN,
        NavigationState.ARRIVED,
        NavigationState.PAUSED,
        NavigationState.CANCELLED
    },
    NavigationState.PAUSED: {
        NavigationState.RESUMING,
        NavigationState.MOVING,
        NavigationState.STARTING,
        NavigationState.CANCELLED
    },
    NavigationState.ARRIVED: {
        NavigationState.IDLE,
        NavigationState.ROUTE_READY
    },
    NavigationState.CANCELLED: {
        NavigationState.IDLE,
        NavigationState.ROUTE_READY
    }
}


class NavigationStateMachine:
    """
    Manages navigation state transitions, hysteresis filtering, and speed thresholds.
    """

    ACCURACY_THRESHOLD_METERS = 45.0  # If accuracy > 45m, enter GPS_UNCERTAIN
    STOPPED_SPEED_THRESHOLD_KMH = 1.2
    MOVING_SPEED_THRESHOLD_KMH = 1.8
    CONSECUTIVE_OBSERVATIONS_FOR_STOP = 2
    CONSECUTIVE_OBSERVATIONS_FOR_MOVE = 1

    def __init__(self, initial_state: NavigationState = NavigationState.IDLE):
        self.current_state = initial_state
        self.previous_reliable_state = initial_state
        self.consecutive_stops = 0
        self.consecutive_moving = 0

    def can_transition_to(self, new_state: NavigationState) -> bool:
        """Checks if a transition from current_state to new_state is legally allowed."""
        if self.current_state == new_state:
            return True
        allowed = VALID_TRANSITIONS.get(self.current_state, set())
        return new_state in allowed

    def transition_to(self, new_state: NavigationState, reason: str = "") -> Tuple[bool, NavigationState]:
        """
        Attempts a transition to new_state. Returns (success, active_state).
        """
        if self.current_state == new_state:
            return True, self.current_state

        if not self.can_transition_to(new_state):
            return False, self.current_state

        if self.current_state != NavigationState.GPS_UNCERTAIN:
            self.previous_reliable_state = self.current_state

        self.current_state = new_state
        return True, self.current_state

    def evaluate_observation(
        self,
        speed_kmh: float,
        accuracy_meters: float,
        dist_to_turn_meters: Optional[float] = None,
        is_at_turn: bool = False,
        is_off_route: bool = False,
        is_arrived: bool = False,
        is_known_traffic_zone: bool = False,
        is_manual_paused: bool = False
    ) -> NavigationState:
        """
        Evaluates real-time sensor observation with hysteresis to determine the target state.
        """
        if is_manual_paused:
            self.transition_to(NavigationState.PAUSED, "Manual pause")
            return self.current_state

        if self.current_state in (NavigationState.ARRIVED, NavigationState.CANCELLED):
            return self.current_state

        # 1. Arrival Check
        if is_arrived:
            self.transition_to(NavigationState.ARRIVED, "Arrived at destination")
            return self.current_state

        # 2. GPS Accuracy Filtering
        if accuracy_meters > self.ACCURACY_THRESHOLD_METERS:
            if self.current_state != NavigationState.GPS_UNCERTAIN:
                self.transition_to(NavigationState.GPS_UNCERTAIN, f"GPS accuracy deteriorated: {accuracy_meters:.1f}m")
            return self.current_state
        elif self.current_state == NavigationState.GPS_UNCERTAIN:
            # Recover from GPS_UNCERTAIN back to previous reliable state or evaluated state
            self.current_state = self.previous_reliable_state

        # 3. Off-Route Check
        if is_off_route:
            if self.current_state != NavigationState.OFF_ROUTE and self.current_state != NavigationState.REROUTING:
                self.transition_to(NavigationState.OFF_ROUTE, "Deviated from planned route")
            return self.current_state
        elif self.current_state == NavigationState.OFF_ROUTE:
            # If back on route
            self.transition_to(NavigationState.MOVING, "Re-joined route")

        # 4. Speed & Stop Hysteresis
        if speed_kmh <= self.STOPPED_SPEED_THRESHOLD_KMH:
            self.consecutive_stops += 1
            self.consecutive_moving = 0

            if self.consecutive_stops >= self.CONSECUTIVE_OBSERVATIONS_FOR_STOP:
                target_state = NavigationState.TRAFFIC_DELAY if is_known_traffic_zone else NavigationState.TEMPORARILY_STOPPED
                self.transition_to(target_state, "User stationary")
                return self.current_state
        else:
            self.consecutive_moving += 1
            self.consecutive_stops = 0

            # Transition out of stop
            if self.current_state in (NavigationState.TEMPORARILY_STOPPED, NavigationState.TRAFFIC_DELAY):
                self.transition_to(NavigationState.RESUMING, "Speed increased, resuming")
                return self.current_state
            elif self.current_state == NavigationState.RESUMING:
                self.transition_to(NavigationState.MOVING, "Consistent movement verified")

        # 5. Maneuver & Turning Detection (if moving)
        if self.current_state in (NavigationState.MOVING, NavigationState.APPROACHING_TURN, NavigationState.TURNING, NavigationState.STARTING):
            if is_at_turn:
                self.transition_to(NavigationState.TURNING, "Executing turn at intersection")
                return self.current_state
            elif dist_to_turn_meters is not None and dist_to_turn_meters <= 60.0:
                self.transition_to(NavigationState.APPROACHING_TURN, f"Approaching turn ({dist_to_turn_meters:.0f}m)")
                return self.current_state
            else:
                self.transition_to(NavigationState.MOVING, "Moving along corridor")
                return self.current_state

        return self.current_state
