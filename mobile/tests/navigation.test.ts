import { NavigationEngine } from '../src/features/navigation/NavigationEngine';
import { RouteAlternative } from '../src/types/routing';

describe('Turn-by-turn Navigation Engine', () => {
  let engine: NavigationEngine;

  const mockRoute: RouteAlternative = {
    id: 'test_route',
    objective: 'FASTEST',
    title: 'Test Corridor',
    summary: 'Direct arterial path',
    distanceMeters: 5000,
    durationSeconds: 600,
    polyline: [
      { latitude: 17.3850, longitude: 78.4867 },
      { latitude: 17.3950, longitude: 78.4967 },
      { latitude: 17.4050, longitude: 78.5067 }
    ],
    maneuvers: [
      {
        id: 'm1',
        instruction: 'Head North on Main Ave',
        type: 'depart',
        distanceMeters: 2000,
        durationSeconds: 240,
        coordinates: { latitude: 17.3850, longitude: 78.4867 }
      },
      {
        id: 'm2',
        instruction: 'Turn right onto Grand Expressway',
        type: 'turn',
        distanceMeters: 3000,
        durationSeconds: 360,
        coordinates: { latitude: 17.3950, longitude: 78.4967 }
      },
      {
        id: 'm3',
        instruction: 'Arrive at destination',
        type: 'arrive',
        distanceMeters: 0,
        durationSeconds: 0,
        coordinates: { latitude: 17.4050, longitude: 78.5067 }
      }
    ],
    source: 'Test Provider',
    accessibilityLevel: 'VERIFIED_ACCESSIBLE',
    confidenceScore: 0.95
  };

  beforeEach(() => {
    engine = new NavigationEngine();
  });

  test('initializes navigation with first maneuver and calculating status', () => {
    engine.startNavigation(mockRoute);
    const state = engine.getState();

    expect(state.status).toBe('NAVIGATING');
    expect(state.currentManeuverIndex).toBe(0);
    expect(state.currentManeuver?.id).toBe('m1');
    expect(state.nextManeuver?.id).toBe('m2');
  });

  test('progresses to next maneuver when approaching waypoint within 20m', () => {
    engine.startNavigation(mockRoute);

    // Simulate location arrival right near second maneuver waypoint
    engine.onLocationUpdate({ latitude: 17.395001, longitude: 78.496701 });
    const state = engine.getState();

    expect(state.currentManeuverIndex).toBe(1);
    expect(state.currentManeuver?.id).toBe('m2');
  });

  test('detects arrival with consecutive confirmation', () => {
    engine.startNavigation(mockRoute);

    // 1st reading near destination: arrival countdown starts
    engine.onLocationUpdate({ latitude: 17.405001, longitude: 78.506701 });
    expect(engine.getState().status).toBe('NAVIGATING');

    // 2nd consecutive reading near destination: ARRIVED confirmed
    engine.onLocationUpdate({ latitude: 17.405002, longitude: 78.506702 });
    expect(engine.getState().status).toBe('ARRIVED');
  });
});
