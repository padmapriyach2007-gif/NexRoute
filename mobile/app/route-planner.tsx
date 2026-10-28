import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, SafeAreaView, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { RouteOptionCard } from '../src/components/RouteOptionCard';
import { routesApi } from '../src/services/api/routesApi';
import { navigationEngine } from '../src/features/navigation/NavigationEngine';
import { deviceLocation } from '../src/services/location/deviceLocation';
import { RouteAlternative } from '../src/types/routing';
import { colors } from '../src/theme/colors';
import { tokens } from '../src/theme/tokens';
import { t } from '../src/i18n';

export default function RoutePlannerScreen() {
  const router = useRouter();
  const [routes, setRoutes] = useState<RouteAlternative[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    deviceLocation.getCurrentPosition().then(async (pos) => {
      const start = pos || { latitude: 17.3850, longitude: 78.4867 };
      const dest = { latitude: start.latitude + 0.045, longitude: start.longitude + 0.035 };
      const fetched = await routesApi.calculateRoutes({ origin: start, destination: dest });
      setRoutes(fetched);
      setIsLoading(false);
    });
  }, []);

  const handleStartNavigation = () => {
    if (routes.length === 0) return;
    const selected = routes[selectedIndex];
    navigationEngine.startNavigation(selected);
    router.push('/navigation');
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <Text style={styles.title}>Available Route Alternatives</Text>
        <Text style={styles.subtitle}>Select preferred route optimization before driving</Text>

        {isLoading ? (
          <View style={styles.loadingBox}>
            <Text style={styles.loadingText}>Calculating multi-objective corridors...</Text>
          </View>
        ) : (
          <FlatList
            data={routes}
            keyExtractor={(item) => item.id}
            renderItem={({ item, index }) => (
              <RouteOptionCard
                route={item}
                isSelected={index === selectedIndex}
                onSelect={() => setSelectedIndex(index)}
              />
            )}
            contentContainerStyle={styles.listContent}
          />
        )}

        <View style={styles.footer}>
          <TouchableOpacity
            activeOpacity={0.85}
            onPress={handleStartNavigation}
            disabled={routes.length === 0}
            style={styles.startButton}
          >
            <Text style={styles.startText}>🚀 {t('nav.start')} ({routes[selectedIndex]?.title || 'Selected Route'})</Text>
          </TouchableOpacity>
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
    padding: tokens.spacing.md
  },
  title: {
    fontSize: 20,
    fontWeight: '900',
    color: '#ffffff',
    marginBottom: 2
  },
  subtitle: {
    fontSize: 13,
    color: colors.textMuted,
    marginBottom: 14
  },
  listContent: {
    paddingBottom: 80
  },
  loadingBox: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center'
  },
  loadingText: {
    color: colors.cyan,
    fontSize: 15,
    fontWeight: '600'
  },
  footer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(8, 18, 36, 0.96)',
    borderTopWidth: 1.5,
    borderTopColor: colors.borderCyan,
    padding: tokens.spacing.md
  },
  startButton: {
    height: tokens.touchTargetMin + 6,
    backgroundColor: colors.emeraldDark,
    borderWidth: 2,
    borderColor: colors.emerald,
    borderRadius: tokens.radii.md,
    alignItems: 'center',
    justifyContent: 'center'
  },
  startText: {
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '900'
  }
});
