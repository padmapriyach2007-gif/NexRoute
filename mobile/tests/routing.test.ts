import { RoutesApi } from '../src/services/api/routesApi';
import { RouteCalculationParams } from '../src/types/routing';

describe('Mobile Routes API & Multi-Objective Engine', () => {
  const api = new RoutesApi();

  const testParams: RouteCalculationParams = {
    origin: { latitude: 17.3850, longitude: 78.4867 },
    destination: { latitude: 17.4350, longitude: 78.5200 },
    objective: 'FASTEST',
    travelMode: 'driving'
  };

  test('generates valid multi-objective route alternatives when server is in fallback mode', async () => {
    const routes = await api.calculateRoutes(testParams);

    expect(routes.length).toBeGreaterThanOrEqual(3);

    const objectives = routes.map((r) => r.objective);
    expect(objectives).toContain('FASTEST');
    expect(objectives).toContain('SHORTEST');
    expect(objectives).toContain('ACCESSIBLE');
  });

  test('ensures each alternative has valid non-negative distances and durations', async () => {
    const routes = await api.calculateRoutes(testParams);

    routes.forEach((r) => {
      expect(r.distanceMeters).toBeGreaterThan(0);
      expect(r.durationSeconds).toBeGreaterThan(0);
      expect(r.polyline.length).toBeGreaterThanOrEqual(2);
      expect(r.maneuvers.length).toBeGreaterThanOrEqual(1);
    });
  });

  test('validates accessible route includes accessibility confidence', async () => {
    const routes = await api.calculateRoutes(testParams);
    const accessibleRoute = routes.find((r) => r.objective === 'ACCESSIBLE');

    expect(accessibleRoute).toBeDefined();
    expect(accessibleRoute?.accessibilityLevel).toBe('VERIFIED_ACCESSIBLE');
    expect(accessibleRoute?.confidenceScore).toBeGreaterThanOrEqual(0.9);
  });
});
