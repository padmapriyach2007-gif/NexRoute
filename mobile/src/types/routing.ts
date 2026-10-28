import { GeoCoordinates } from './location';

export type OptimizationObjective =
  | 'FASTEST'
  | 'SHORTEST'
  | 'BALANCED'
  | 'ACCESSIBLE';

export type AccessibilityLevel =
  | 'VERIFIED_ACCESSIBLE'
  | 'VERIFIED_INACCESSIBLE'
  | 'UNKNOWN';

export interface RouteManeuver {
  id: string;
  instruction: string;
  type: string;
  modifier?: string;
  distanceMeters: number;
  durationSeconds: number;
  coordinates: GeoCoordinates;
  spokenInstruction?: string;
}

export interface RouteAlternative {
  id: string;
  objective: OptimizationObjective;
  title: string;
  summary: string;
  distanceMeters: number;
  durationSeconds: number;
  polyline: GeoCoordinates[];
  maneuvers: RouteManeuver[];
  source: string;
  tollCostInr?: number;
  hazardCount?: number;
  accessibilityLevel: AccessibilityLevel;
  confidenceScore: number;
  restrictions?: string[];
  isRecommended?: boolean;
}

export interface RouteCalculationParams {
  origin: GeoCoordinates;
  destination: GeoCoordinates;
  objective?: OptimizationObjective;
  travelMode?: 'driving' | 'walking' | 'bicycling' | 'transit';
  avoidTolls?: boolean;
  avoidHighways?: boolean;
  requireAccessible?: boolean;
}
