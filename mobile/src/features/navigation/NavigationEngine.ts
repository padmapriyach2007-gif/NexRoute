import { GeoCoordinates } from '../../types/location';
import { RouteAlternative, RouteManeuver } from '../../types/routing';
import { NavigationSessionState } from '../../types/navigation';
import { routesApi } from '../../services/api/routesApi';
import { ttsService } from '../../services/speech/ttsService';

// Off-route threshold in meters before triggering adaptive recalculation
const OFF_ROUTE_THRESHOLD_METERS = 45;
// Arrival radius in meters
const ARRIVAL_THRESHOLD_METERS = 25;

export type NavigationListener = (state: NavigationSessionState) => void;

export class NavigationEngine {
  private state: NavigationSessionState = {
    status: 'IDLE',
    selectedRoute: null,
    currentLocation: null,
    currentManeuverIndex: 0,
    currentManeuver: null,
    nextManeuver: null,
    distanceToNextManeuverMeters: 0,
    remainingDistanceMeters: 0,
    remainingDurationSeconds: 0,
    isMuted: false,
    isFollowMode: true,
    offRouteCount: 0,
    lastAnnouncementId: null
  };

  private listeners: Set<NavigationListener> = new Set();
  private isRecalculating: boolean = false;
  private consecutiveArrivalHits: number = 0;

  public subscribe(listener: NavigationListener): () => void {
    this.listeners.add(listener);
    listener(this.state);
    return () => this.listeners.delete(listener);
  }

  public getState(): NavigationSessionState {
    return { ...this.state };
  }

  public startNavigation(route: RouteAlternative, startLocation?: GeoCoordinates): void {
    const firstManeuver = route.maneuvers[0] || null;
    const secondManeuver = route.maneuvers[1] || null;

    this.state = {
      status: 'NAVIGATING',
      selectedRoute: route,
      currentLocation: startLocation || route.polyline[0] || null,
      currentManeuverIndex: 0,
      currentManeuver: firstManeuver,
      nextManeuver: secondManeuver,
      distanceToNextManeuverMeters: firstManeuver?.distanceMeters || 0,
      remainingDistanceMeters: route.distanceMeters,
      remainingDurationSeconds: route.durationSeconds,
      isMuted: ttsService.getMuted(),
      isFollowMode: true,
      offRouteCount: 0,
      lastAnnouncementId: null
    };

    this.consecutiveArrivalHits = 0;
    this.notify();

    if (firstManeuver) {
      ttsService.announceManeuver(firstManeuver.id, firstManeuver.spokenInstruction || firstManeuver.instruction);
    }
  }

  public stopNavigation(): void {
    ttsService.stop();
    this.state = {
      ...this.state,
      status: 'IDLE',
      selectedRoute: null,
      currentManeuver: null,
      nextManeuver: null
    };
    this.notify();
  }

  public toggleMute(): boolean {
    const newMuted = !this.state.isMuted;
    ttsService.setMuted(newMuted);
    this.state.isMuted = newMuted;
    this.notify();
    return newMuted;
  }

  public setFollowMode(follow: boolean): void {
    this.state.isFollowMode = follow;
    this.notify();
  }

  public onLocationUpdate(location: GeoCoordinates): void {
    if (this.state.status !== 'NAVIGATING' || !this.state.selectedRoute) {
      this.state.currentLocation = location;
      return;
    }

    this.state.currentLocation = location;

    // 1. Check Arrival
    const destination = this.state.selectedRoute.polyline[this.state.selectedRoute.polyline.length - 1];
    if (destination) {
      const distToDest = this.calculateDistanceMeters(location, destination);
      if (distToDest <= ARRIVAL_THRESHOLD_METERS) {
        this.consecutiveArrivalHits += 1;
        // Require 2 consecutive GPS readings within threshold to prevent false positives from noisy spikes
        if (this.consecutiveArrivalHits >= 2) {
          this.state.status = 'ARRIVED';
          ttsService.announceArrival();
          this.notify();
          return;
        }
      } else {
        this.consecutiveArrivalHits = 0;
      }
    }

    // 2. Maneuver Progression
    const maneuvers = this.state.selectedRoute.maneuvers;
    const curIdx = this.state.currentManeuverIndex;
    if (curIdx < maneuvers.length) {
      const curMan = maneuvers[curIdx];
      const distToManeuver = this.calculateDistanceMeters(location, curMan.coordinates);
      this.state.distanceToNextManeuverMeters = Math.round(distToManeuver);

      // Transition to next maneuver when within 20m of waypoint
      if (distToManeuver <= 20 && curIdx < maneuvers.length - 1) {
        const nextIdx = curIdx + 1;
        this.state.currentManeuverIndex = nextIdx;
        this.state.currentManeuver = maneuvers[nextIdx];
        this.state.nextManeuver = maneuvers[nextIdx + 1] || null;

        const nextMan = maneuvers[nextIdx];
        ttsService.announceManeuver(
          nextMan.id,
          nextMan.spokenInstruction || nextMan.instruction,
          nextMan.distanceMeters
        );
      }
    }

    // 3. Off-Route Detection & Adaptive Rerouting
    const minDistanceToPolyline = this.findDistanceToPolyline(location, this.state.selectedRoute.polyline);
    if (minDistanceToPolyline > OFF_ROUTE_THRESHOLD_METERS) {
      this.state.offRouteCount += 1;
      // Trigger reroute if user is off-route across 3 consecutive updates (debouncing noise)
      if (this.state.offRouteCount >= 3 && !this.isRecalculating) {
        this.triggerAdaptiveRerouting(location);
      }
    } else {
      this.state.offRouteCount = 0;
    }

    this.notify();
  }

  private async triggerAdaptiveRerouting(currentLocation: GeoCoordinates): Promise<void> {
    if (!this.state.selectedRoute || this.isRecalculating) return;

    this.isRecalculating = true;
    this.state.status = 'REROUTING';
    this.notify();

    const destination = this.state.selectedRoute.polyline[this.state.selectedRoute.polyline.length - 1];

    try {
      const newRoute = await routesApi.requestReroute(currentLocation, destination);
      if (newRoute && newRoute.polyline.length > 0) {
        this.state.selectedRoute = newRoute;
        this.state.currentManeuverIndex = 0;
        this.state.currentManeuver = newRoute.maneuvers[0] || null;
        this.state.nextManeuver = newRoute.maneuvers[1] || null;
        this.state.remainingDistanceMeters = newRoute.distanceMeters;
        this.state.remainingDurationSeconds = newRoute.durationSeconds;
        this.state.status = 'NAVIGATING';
        this.state.offRouteCount = 0;

        if (newRoute.maneuvers[0]) {
          ttsService.announceManeuver(
            newRoute.maneuvers[0].id,
            `Rerouting: ${newRoute.maneuvers[0].spokenInstruction || newRoute.maneuvers[0].instruction}`
          );
        }
      } else {
        this.state.status = 'NAVIGATING';
      }
    } catch {
      this.state.status = 'NAVIGATING';
    } finally {
      this.isRecalculating = false;
      this.notify();
    }
  }

  private calculateDistanceMeters(p1: GeoCoordinates, p2: GeoCoordinates): number {
    const R = 6371000;
    const dLat = (p2.latitude - p1.latitude) * Math.PI / 180;
    const dLon = (p2.longitude - p1.longitude) * Math.PI / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(p1.latitude * Math.PI / 180) *
      Math.cos(p2.latitude * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  private findDistanceToPolyline(point: GeoCoordinates, polyline: GeoCoordinates[]): number {
    if (!polyline || polyline.length === 0) return 0;
    let minDistance = Infinity;
    for (let i = 0; i < polyline.length - 1; i++) {
      const p1 = polyline[i];
      const p2 = polyline[i + 1];
      const d = this.distanceToSegmentMeters(point, p1, p2);
      if (d < minDistance) minDistance = d;
    }
    return minDistance === Infinity ? 0 : minDistance;
  }

  private distanceToSegmentMeters(p: GeoCoordinates, a: GeoCoordinates, b: GeoCoordinates): number {
    const lat1 = a.latitude;
    const lon1 = a.longitude;
    const lat2 = b.latitude;
    const lon2 = b.longitude;
    const x = p.latitude;
    const y = p.longitude;

    const dx = lat2 - lat1;
    const dy = lon2 - lon1;

    if (dx === 0 && dy === 0) {
      return this.calculateDistanceMeters(p, a);
    }

    const t = Math.max(0, Math.min(1, ((x - lat1) * dx + (y - lon1) * dy) / (dx * dx + dy * dy)));
    const proj: GeoCoordinates = {
      latitude: lat1 + t * dx,
      longitude: lon1 + t * dy
    };
    return this.calculateDistanceMeters(p, proj);
  }

  private notify(): void {
    const snap = this.getState();
    this.listeners.forEach((listener) => {
      try {
        listener(snap);
      } catch {}
    });
  }
}

export const navigationEngine = new NavigationEngine();
