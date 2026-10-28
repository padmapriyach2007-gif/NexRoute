import { GeoCoordinates } from './location';
import { RouteAlternative, RouteManeuver } from './routing';

export type NavigationStatus =
  | 'IDLE'
  | 'PLANNING'
  | 'NAVIGATING'
  | 'REROUTING'
  | 'ARRIVED'
  | 'PAUSED';

export interface NavigationSessionState {
  status: NavigationStatus;
  selectedRoute: RouteAlternative | null;
  currentLocation: GeoCoordinates | null;
  currentManeuverIndex: number;
  currentManeuver: RouteManeuver | null;
  nextManeuver: RouteManeuver | null;
  distanceToNextManeuverMeters: number;
  remainingDistanceMeters: number;
  remainingDurationSeconds: number;
  isMuted: boolean;
  isFollowMode: boolean;
  offRouteCount: number;
  lastAnnouncementId: string | null;
}
