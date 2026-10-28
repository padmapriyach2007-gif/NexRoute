import React from 'react';
import { View, StyleSheet, Text, TouchableOpacity } from 'react-native';
import { GeoCoordinates } from '../../types/location';
import { RouteAlternative } from '../../types/routing';
import { colors } from '../../theme/colors';
import { tokens } from '../../theme/tokens';

export interface MapScreenProps {
  userLocation: GeoCoordinates | null;
  routes: RouteAlternative[];
  selectedRouteIndex: number;
  isFollowMode: boolean;
  onRecenter: () => void;
  onToggleFollow: () => void;
  destinationCoords?: GeoCoordinates | null;
}

export const MapScreen: React.FC<MapScreenProps> = ({
  userLocation,
  routes,
  selectedRouteIndex,
  isFollowMode,
  onRecenter,
  onToggleFollow,
  destinationCoords
}) => {
  const activeRoute = routes[selectedRouteIndex];

  return (
    <View style={styles.mapContainer}>
      {/* Background Interactive Map Grid & Coordinate Display */}
      <View style={styles.mapCanvas}>
        <View style={styles.mapGridPattern} />

        {/* Route Geometry Vector Representation */}
        {activeRoute && (
          <View style={styles.routeOverlayContainer}>
            <View style={styles.routeHeaderInfo}>
              <Text style={styles.routeBadgeText}>
                🛰️ {activeRoute.objective} • {(activeRoute.distanceMeters / 1000).toFixed(1)} km
              </Text>
            </View>
          </View>
        )}

        {/* User Location Pulsing Puck */}
        {userLocation && (
          <View style={styles.userPuckContainer}>
            <View style={styles.userPuckPulse} />
            <View style={styles.userPuckCore} />
            <Text style={styles.userPuckLabel}>📍 You</Text>
          </View>
        )}

        {/* Destination Pin */}
        {destinationCoords && (
          <View style={styles.destPinContainer}>
            <Text style={styles.destPinIcon}>🏁</Text>
            <Text style={styles.destPinLabel}>Destination</Text>
          </View>
        )}
      </View>

      {/* Camera and Mode Controls Floating Bar */}
      <View style={styles.controlsBar}>
        <TouchableOpacity
          activeOpacity={0.8}
          onPress={onRecenter}
          style={styles.controlButton}
        >
          <Text style={styles.controlIcon}>🎯</Text>
        </TouchableOpacity>

        <TouchableOpacity
          activeOpacity={0.8}
          onPress={onToggleFollow}
          style={[
            styles.controlButton,
            isFollowMode && styles.controlButtonActive
          ]}
        >
          <Text style={styles.controlIcon}>{isFollowMode ? '🔒' : '🔓'}</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  mapContainer: {
    flex: 1,
    backgroundColor: '#030712',
    position: 'relative'
  },
  mapCanvas: {
    flex: 1,
    backgroundColor: '#050c1a',
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center'
  },
  mapGridPattern: {
    ...StyleSheet.absoluteFillObject,
    opacity: 0.12,
    borderWidth: 1,
    borderColor: '#00f0ff'
  },
  routeOverlayContainer: {
    position: 'absolute',
    top: 16,
    left: 16,
    right: 16,
    alignItems: 'center'
  },
  routeHeaderInfo: {
    backgroundColor: 'rgba(15, 23, 42, 0.88)',
    borderWidth: 1,
    borderColor: colors.borderCyan,
    borderRadius: tokens.radii.full,
    paddingHorizontal: 12,
    paddingVertical: 5
  },
  routeBadgeText: {
    color: colors.cyan,
    fontSize: 12,
    fontWeight: '800'
  },
  userPuckContainer: {
    position: 'absolute',
    alignItems: 'center',
    justifyContent: 'center'
  },
  userPuckPulse: {
    position: 'absolute',
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(0, 240, 255, 0.25)'
  },
  userPuckCore: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: colors.cyan,
    borderWidth: 2,
    borderColor: '#ffffff'
  },
  userPuckLabel: {
    color: '#e0f2fe',
    fontSize: 10,
    fontWeight: '700',
    marginTop: 4
  },
  destPinContainer: {
    position: 'absolute',
    top: '30%',
    right: '25%',
    alignItems: 'center'
  },
  destPinIcon: {
    fontSize: 26
  },
  destPinLabel: {
    color: colors.rose,
    fontSize: 10,
    fontWeight: '800',
    marginTop: 2
  },
  controlsBar: {
    position: 'absolute',
    right: 16,
    bottom: 24,
    gap: 10
  },
  controlButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(15, 23, 42, 0.90)',
    borderWidth: 1.5,
    borderColor: colors.borderCyan,
    alignItems: 'center',
    justifyContent: 'center',
    ...tokens.elevation.card
  },
  controlButtonActive: {
    borderColor: colors.emerald,
    backgroundColor: 'rgba(6, 78, 59, 0.80)'
  },
  controlIcon: {
    fontSize: 18
  }
});
