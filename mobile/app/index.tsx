import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { MapScreen } from '../src/features/map/MapScreen';
import { AuraFloatingFab } from '../src/components/AuraFloatingFab';
import { deviceLocation } from '../src/services/location/deviceLocation';
import { routesApi } from '../src/services/api/routesApi';
import { GeoCoordinates } from '../src/types/location';
import { RouteAlternative, OptimizationObjective } from '../src/types/routing';
import { colors } from '../src/theme/colors';
import { tokens } from '../src/theme/tokens';
import { t } from '../src/i18n';

export default function HomeScreen() {
  const router = useRouter();
  const [userLocation, setUserLocation] = useState<GeoCoordinates | null>(null);
  const [destinationText, setDestinationText] = useState('');
  const [destinationCoords, setDestinationCoords] = useState<GeoCoordinates | null>(null);
  const [selectedObjective, setSelectedObjective] = useState<OptimizationObjective>('FASTEST');
  const [routes, setRoutes] = useState<RouteAlternative[]>([]);
  const [isFollowMode, setIsFollowMode] = useState(true);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    // Acquire initial device GPS position
    deviceLocation.getCurrentPosition().then((pos) => {
      if (pos) {
        setUserLocation(pos);
      } else {
        // Fallback default coordinates (Hyderabad/Amaravati corridor)
        setUserLocation({ latitude: 17.3850, longitude: 78.4867 });
      }
    });

    // Start background location updates
    deviceLocation.startTracking((coords) => {
      setUserLocation(coords);
    });

    return () => {
      deviceLocation.stopTracking();
    };
  }, []);

  const handleSearchDestination = async () => {
    if (!destinationText.trim() || !userLocation) return;
    setIsSearching(true);

    try {
      const candidates = await routesApi.geocode(destinationText);
      const targetCoord: GeoCoordinates = candidates.length > 0
        ? { latitude: candidates[0].lat, longitude: candidates[0].lon }
        : { latitude: userLocation.latitude + 0.045, longitude: userLocation.longitude + 0.035 };

      setDestinationCoords(targetCoord);

      // Compute route alternatives with the selected objective
      const calculated = await routesApi.calculateRoutes({
        origin: userLocation,
        destination: targetCoord,
        objective: selectedObjective
      });

      setRoutes(calculated);
    } catch {
      // Handled via fallback
    } finally {
      setIsSearching(false);
    }
  };

  const handleStartNavigation = () => {
    if (routes.length === 0) return;
    router.push({
      pathname: '/navigation',
      params: { routeIndex: '0' }
    });
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        {/* Full-Screen Interactive Mobile Map */}
        <MapScreen
          userLocation={userLocation}
          routes={routes}
          selectedRouteIndex={0}
          isFollowMode={isFollowMode}
          onRecenter={() => setIsFollowMode(true)}
          onToggleFollow={() => setIsFollowMode(!isFollowMode)}
          destinationCoords={destinationCoords}
        />

        {/* Top Floating Search & Quick Objective Bar */}
        <View style={styles.topSearchCard}>
          <View style={styles.searchRow}>
            <Text style={styles.searchIcon}>🔍</Text>
            <TextInput
              style={styles.searchInput}
              placeholder={t('plan.destination')}
              placeholderTextColor={colors.textMuted}
              value={destinationText}
              onChangeText={setDestinationText}
              onSubmitEditing={handleSearchDestination}
              returnKeyType="search"
            />
            {destinationText.length > 0 && (
              <TouchableOpacity onPress={() => setDestinationText('')}>
                <Text style={styles.clearBtnText}>✕</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* Quick Objective Selector Pills */}
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.objectiveScroll}>
            {(['FASTEST', 'SHORTEST', 'BALANCED', 'ACCESSIBLE'] as OptimizationObjective[]).map((obj) => (
              <TouchableOpacity
                key={obj}
                onPress={() => setSelectedObjective(obj)}
                style={[
                  styles.objPill,
                  selectedObjective === obj && styles.objPillActive
                ]}
              >
                <Text style={[
                  styles.objPillText,
                  selectedObjective === obj && styles.objPillTextActive
                ]}>
                  {obj === 'FASTEST' ? '⚡ Fastest' :
                   obj === 'SHORTEST' ? '📏 Shortest' :
                   obj === 'BALANCED' ? '⚖️ Balanced' : '♿ Accessible'}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Bottom Drawer Actions */}
        <View style={styles.bottomDrawer}>
          <View style={styles.quickNavRow}>
            <TouchableOpacity
              onPress={() => router.push('/destinations')}
              style={styles.quickNavItem}
            >
              <Text style={styles.quickNavIcon}>🌟</Text>
              <Text style={styles.quickNavLabel}>{t('places.explore')}</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => router.push('/saved-places')}
              style={styles.quickNavItem}
            >
              <Text style={styles.quickNavIcon}>📌</Text>
              <Text style={styles.quickNavLabel}>Saved</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => router.push('/itinerary')}
              style={styles.quickNavItem}
            >
              <Text style={styles.quickNavIcon}>📅</Text>
              <Text style={styles.quickNavLabel}>Itinerary</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={() => router.push('/settings')}
              style={styles.quickNavItem}
            >
              <Text style={styles.quickNavIcon}>⚙️</Text>
              <Text style={styles.quickNavLabel}>Settings</Text>
            </TouchableOpacity>
          </View>

          {routes.length > 0 ? (
            <TouchableOpacity
              activeOpacity={0.85}
              onPress={handleStartNavigation}
              style={styles.startNavButton}
            >
              <Text style={styles.startNavText}>🚀 {t('nav.start')} ({Math.round(routes[0].durationSeconds / 60)} min)</Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity
              activeOpacity={0.85}
              onPress={handleSearchDestination}
              style={styles.findRouteButton}
            >
              <Text style={styles.findRouteText}>{isSearching ? 'Finding routes...' : `🧭 ${t('plan.calculate')}`}</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Floating AI Copilot AURA FAB */}
        <AuraFloatingFab onPress={() => router.push('/copilot')} />
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
  topSearchCard: {
    position: 'absolute',
    top: 12,
    left: 14,
    right: 14,
    backgroundColor: 'rgba(11, 27, 45, 0.94)',
    borderWidth: 1.5,
    borderColor: colors.borderCyan,
    borderRadius: tokens.radii.lg,
    padding: tokens.spacing.sm,
    ...tokens.elevation.card
  },
  searchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: tokens.spacing.sm,
    paddingHorizontal: 8,
    height: 42
  },
  searchIcon: {
    fontSize: 18
  },
  searchInput: {
    flex: 1,
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '600'
  },
  clearBtnText: {
    color: colors.textMuted,
    fontSize: 16,
    padding: 4
  },
  objectiveScroll: {
    gap: 8,
    marginTop: 6,
    paddingHorizontal: 4
  },
  objPill: {
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: tokens.radii.full,
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderWidth: 1,
    borderColor: 'transparent'
  },
  objPillActive: {
    backgroundColor: 'rgba(0, 240, 255, 0.20)',
    borderColor: colors.cyan
  },
  objPillText: {
    color: colors.textSecondary,
    fontSize: 12,
    fontWeight: '700'
  },
  objPillTextActive: {
    color: colors.cyan
  },
  bottomDrawer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(8, 18, 36, 0.96)',
    borderTopWidth: 1.5,
    borderTopColor: colors.borderCyan,
    borderTopLeftRadius: tokens.radii.xl,
    borderTopRightRadius: tokens.radii.xl,
    paddingHorizontal: tokens.spacing.lg,
    paddingTop: tokens.spacing.md,
    paddingBottom: tokens.spacing.lg,
    gap: tokens.spacing.md
  },
  quickNavRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center'
  },
  quickNavItem: {
    alignItems: 'center',
    gap: 4
  },
  quickNavIcon: {
    fontSize: 20
  },
  quickNavLabel: {
    color: colors.textSecondary,
    fontSize: 11,
    fontWeight: '600'
  },
  startNavButton: {
    height: tokens.touchTargetMin + 6,
    backgroundColor: colors.emeraldDark,
    borderWidth: 2,
    borderColor: colors.emerald,
    borderRadius: tokens.radii.md,
    alignItems: 'center',
    justifyContent: 'center',
    ...tokens.elevation.card
  },
  startNavText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '900',
    letterSpacing: 0.5
  },
  findRouteButton: {
    height: tokens.touchTargetMin,
    backgroundColor: colors.cyanMuted,
    borderWidth: 1.5,
    borderColor: colors.cyan,
    borderRadius: tokens.radii.md,
    alignItems: 'center',
    justifyContent: 'center'
  },
  findRouteText: {
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '800'
  }
});
