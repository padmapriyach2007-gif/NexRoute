import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { navigationEngine } from '../src/features/navigation/NavigationEngine';
import { deviceLocation } from '../src/services/location/deviceLocation';
import { routesApi } from '../src/services/api/routesApi';
import { TurnInstructionCard } from '../src/components/TurnInstructionCard';
import { MapScreen } from '../src/features/map/MapScreen';
import { NavigationSessionState } from '../src/types/navigation';
import { colors } from '../src/theme/colors';
import { tokens } from '../src/theme/tokens';
import { t } from '../src/i18n';

export default function NavigationScreen() {
  const router = useRouter();
  const [navState, setNavState] = useState<NavigationSessionState>(navigationEngine.getState());

  useEffect(() => {
    // Subscribe to navigation engine state transitions
    const unsubscribe = navigationEngine.subscribe((state) => {
      setNavState(state);
    });

    // Start GPS position streaming into navigation engine
    deviceLocation.startTracking((coords) => {
      navigationEngine.onLocationUpdate(coords);
    });

    // If no active route in navigation engine, initialize fallback demo route
    if (!navigationEngine.getState().selectedRoute) {
      deviceLocation.getCurrentPosition().then(async (pos) => {
        const start = pos || { latitude: 17.3850, longitude: 78.4867 };
        const dest = { latitude: start.latitude + 0.045, longitude: start.longitude + 0.035 };
        const routes = await routesApi.calculateRoutes({ origin: start, destination: dest });
        if (routes.length > 0) {
          navigationEngine.startNavigation(routes[0], start);
        }
      });
    }

    return () => {
      unsubscribe();
    };
  }, []);

  const handleExit = () => {
    navigationEngine.stopNavigation();
    router.replace('/');
  };

  const handleToggleMute = () => {
    navigationEngine.toggleMute();
  };

  const formatRemainingTime = (sec: number) => {
    const mins = Math.round(sec / 60);
    if (mins >= 60) {
      const hrs = Math.floor(mins / 60);
      const rem = mins % 60;
      return `${hrs}h ${rem}m`;
    }
    return `${mins} min`;
  };

  const formatDistance = (m: number) => {
    return `${(m / 1000).toFixed(1)} km`;
  };

  const route = navState.selectedRoute;

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        {/* Full-Screen Map with Navigation Puck & Polyline */}
        <MapScreen
          userLocation={navState.currentLocation}
          routes={route ? [route] : []}
          selectedRouteIndex={0}
          isFollowMode={navState.isFollowMode}
          onRecenter={() => navigationEngine.setFollowMode(true)}
          onToggleFollow={() => navigationEngine.setFollowMode(!navState.isFollowMode)}
        />

        {/* Top Active Turn Instruction HUD */}
        <View style={styles.topHud}>
          <TurnInstructionCard
            currentManeuver={navState.currentManeuver}
            nextManeuver={navState.nextManeuver}
            distanceMeters={navState.distanceToNextManeuverMeters}
          />
        </View>

        {/* Bottom Navigation Status Bar */}
        <View style={styles.bottomBar}>
          <View style={styles.metricsCol}>
            <Text style={styles.remainingTime}>
              {formatRemainingTime(navState.remainingDurationSeconds)}
            </Text>
            <Text style={styles.remainingDistance}>
              {formatDistance(navState.remainingDistanceMeters)} remaining
            </Text>
          </View>

          <View style={styles.actionButtonsRow}>
            {/* Voice Mute Toggle */}
            <TouchableOpacity
              activeOpacity={0.8}
              onPress={handleToggleMute}
              style={[
                styles.iconButton,
                navState.isMuted && styles.iconButtonMuted
              ]}
            >
              <Text style={styles.btnIcon}>{navState.isMuted ? '🔇' : '🔊'}</Text>
            </TouchableOpacity>

            {/* Exit Navigation */}
            <TouchableOpacity
              activeOpacity={0.8}
              onPress={handleExit}
              style={styles.exitButton}
            >
              <Text style={styles.exitText}>✕ {t('nav.stop')}</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.background
  },
  container: {
    flex: 1,
    position: 'relative'
  },
  topHud: {
    position: 'absolute',
    top: 14,
    left: 14,
    right: 14
  },
  bottomBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(8, 18, 36, 0.96)',
    borderTopWidth: 1.5,
    borderTopColor: colors.borderCyan,
    paddingHorizontal: tokens.spacing.lg,
    paddingVertical: tokens.spacing.md,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  metricsCol: {
    flex: 1
  },
  remainingTime: {
    fontSize: 24,
    fontWeight: '900',
    color: colors.cyan,
    letterSpacing: 0.5
  },
  remainingDistance: {
    fontSize: 13,
    color: colors.textSecondary,
    fontWeight: '600'
  },
  actionButtonsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12
  },
  iconButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(15, 23, 42, 0.90)',
    borderWidth: 1.5,
    borderColor: colors.borderCyan,
    alignItems: 'center',
    justifyContent: 'center'
  },
  iconButtonMuted: {
    borderColor: colors.rose,
    backgroundColor: 'rgba(127, 29, 29, 0.4)'
  },
  btnIcon: {
    fontSize: 18
  },
  exitButton: {
    minHeight: 44,
    backgroundColor: colors.roseDark,
    borderWidth: 1.5,
    borderColor: colors.rose,
    borderRadius: tokens.radii.md,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center'
  },
  exitText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '800'
  }
});
