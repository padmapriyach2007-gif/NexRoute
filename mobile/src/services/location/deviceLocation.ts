import * as Location from 'expo-location';
import { GeoCoordinates, LocationStatus, LocationPermissionState } from '../../types/location';

export type LocationUpdateCallback = (location: GeoCoordinates) => void;

export class DeviceLocationService {
  private subscription: Location.LocationSubscription | null = null;
  private lastLocation: GeoCoordinates | null = null;
  private listeners: Set<LocationUpdateCallback> = new Set();
  private isStale: boolean = false;
  private staleTimer: ReturnType<typeof setTimeout> | null = null;

  public async requestPermissions(): Promise<LocationPermissionState> {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') return 'granted';
      if (status === 'denied') return 'denied';
      return 'undetermined';
    } catch {
      return 'denied';
    }
  }

  public async checkPermissions(): Promise<LocationPermissionState> {
    try {
      const { status } = await Location.getForegroundPermissionsAsync();
      if (status === 'granted') return 'granted';
      if (status === 'denied') return 'denied';
      return 'undetermined';
    } catch {
      return 'denied';
    }
  }

  public async getCurrentPosition(): Promise<GeoCoordinates | null> {
    try {
      const permission = await this.checkPermissions();
      if (permission !== 'granted') {
        const req = await this.requestPermissions();
        if (req !== 'granted') return null;
      }

      const loc = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced
      });

      const coords: GeoCoordinates = {
        latitude: loc.coords.latitude,
        longitude: loc.coords.longitude,
        altitude: loc.coords.altitude,
        accuracy: loc.coords.accuracy,
        heading: loc.coords.heading,
        speed: loc.coords.speed,
        timestamp: loc.timestamp
      };

      this.lastLocation = coords;
      this.resetStaleTimer();
      return coords;
    } catch {
      return this.lastLocation;
    }
  }

  public async startTracking(callback: LocationUpdateCallback): Promise<boolean> {
    this.listeners.add(callback);

    if (this.subscription) {
      if (this.lastLocation) callback(this.lastLocation);
      return true;
    }

    try {
      const permission = await this.checkPermissions();
      if (permission !== 'granted') {
        const req = await this.requestPermissions();
        if (req !== 'granted') return false;
      }

      this.subscription = await Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.High,
          distanceInterval: 5, // Update every 5 meters
          timeInterval: 1000   // Or at least once per second
        },
        (loc) => {
          const coords: GeoCoordinates = {
            latitude: loc.coords.latitude,
            longitude: loc.coords.longitude,
            altitude: loc.coords.altitude,
            accuracy: loc.coords.accuracy,
            heading: loc.coords.heading,
            speed: loc.coords.speed,
            timestamp: loc.timestamp
          };

          this.lastLocation = coords;
          this.isStale = false;
          this.resetStaleTimer();

          this.listeners.forEach((listener) => {
            try {
              listener(coords);
            } catch {}
          });
        }
      );

      return true;
    } catch {
      return false;
    }
  }

  public stopTracking(callback?: LocationUpdateCallback): void {
    if (callback) {
      this.listeners.delete(callback);
    }
    if (this.listeners.size === 0 && this.subscription) {
      this.subscription.remove();
      this.subscription = null;
    }
  }

  private resetStaleTimer(): void {
    if (this.staleTimer) clearTimeout(this.staleTimer);
    // Mark location stale if no update arrives within 15 seconds
    this.staleTimer = setTimeout(() => {
      this.isStale = true;
    }, 15000);
  }

  public getStatus(): LocationStatus {
    return {
      permission: this.subscription ? 'granted' : 'undetermined',
      servicesEnabled: true,
      isStale: this.isStale,
      lastUpdated: this.lastLocation?.timestamp || null,
      currentCoords: this.lastLocation
    };
  }
}

export const deviceLocation = new DeviceLocationService();
