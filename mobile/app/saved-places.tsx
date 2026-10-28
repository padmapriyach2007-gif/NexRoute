import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { colors } from '../src/theme/colors';
import { tokens } from '../src/theme/tokens';

interface SavedPlace {
  id: string;
  label: string;
  address: string;
  icon: string;
  lat: number;
  lon: number;
}

const DEFAULT_SAVED: SavedPlace[] = [
  { id: '1', label: 'Home', address: 'Amaravati Central Residence', icon: '🏠', lat: 16.5140, lon: 80.5230 },
  { id: '2', label: 'Work', address: 'Vignan Innovation & Research Park', icon: '💼', lat: 16.2335, lon: 80.5505 },
  { id: '3', label: 'Gym', address: 'Guntur City Fitness Hub', icon: '🏋️', lat: 16.3067, lon: 80.4365 }
];

export default function SavedPlacesScreen() {
  const router = useRouter();
  const [places, setPlaces] = useState<SavedPlace[]>(DEFAULT_SAVED);

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <FlatList
          data={places}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <TouchableOpacity
              activeOpacity={0.8}
              onPress={() => router.push('/')}
              style={styles.card}
            >
              <View style={styles.iconCircle}>
                <Text style={styles.icon}>{item.icon}</Text>
              </View>
              <View style={styles.info}>
                <Text style={styles.label}>{item.label}</Text>
                <Text style={styles.address}>{item.address}</Text>
              </View>
              <Text style={styles.routeArrow}>➔</Text>
            </TouchableOpacity>
          )}
          contentContainerStyle={styles.list}
        />
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
  list: {
    gap: 10
  },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.backgroundGlass,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    borderRadius: tokens.radii.lg,
    padding: tokens.spacing.md,
    gap: 12,
    ...tokens.elevation.card
  },
  iconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(0, 240, 255, 0.15)',
    borderWidth: 1,
    borderColor: colors.cyan,
    alignItems: 'center',
    justifyContent: 'center'
  },
  icon: {
    fontSize: 20
  },
  info: {
    flex: 1
  },
  label: {
    fontSize: 16,
    fontWeight: '800',
    color: '#ffffff'
  },
  address: {
    fontSize: 12,
    color: colors.textMuted,
    marginTop: 2
  },
  routeArrow: {
    fontSize: 18,
    color: colors.cyan,
    fontWeight: '900'
  }
});
