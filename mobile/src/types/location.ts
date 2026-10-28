export interface GeoCoordinates {
  latitude: number;
  longitude: number;
  altitude?: number | null;
  accuracy?: number | null;
  heading?: number | null;
  speed?: number | null;
  timestamp?: number;
}

export type LocationPermissionState =
  | 'undetermined'
  | 'granted'
  | 'denied'
  | 'restricted';

export interface LocationStatus {
  permission: LocationPermissionState;
  servicesEnabled: boolean;
  isStale: boolean;
  lastUpdated: number | null;
  currentCoords: GeoCoordinates | null;
  error?: string | null;
}
