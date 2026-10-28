import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { colors } from '../src/theme/colors';
import { tokens } from '../src/theme/tokens';

interface ItineraryLeg {
  id: string;
  time: string;
  title: string;
  mode: string;
  durationMins: number;
  distanceKm: number;
  notes: string;
}

const SAMPLE_LEGS: ItineraryLeg[] = [
  {
    id: 'leg_1',
    time: '09:00 AM',
    title: 'Depart from Starting Residence',
    mode: '🚗 Electric Car',
    durationMins: 22,
    distanceKm: 14.5,
    notes: 'Fastest highway corridor avoiding reported bottleneck.'
  },
  {
    id: 'leg_2',
    time: '10:00 AM',
    title: 'Visit Undavalli Historic Caves',
    mode: '🚶 Walking Tour',
    durationMins: 45,
    distanceKm: 1.2,
    notes: 'AURA guide step-by-step commentary enabled.'
  },
  {
    id: 'leg_3',
    time: '12:30 PM',
    title: 'Transit to Riverwalk Dining Hub',
    mode: '🚗 Electric Car',
    durationMins: 18,
    distanceKm: 8.4,
    notes: 'Scenic bridge crossing with zero FASTag tolls.'
  }
];

export default function ItineraryScreen() {
  const router = useRouter();
  const [legs] = useState<ItineraryLeg[]>(SAMPLE_LEGS);

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.heading}>Multi-Stop Smart Journey</Text>
        <Text style={styles.subtitle}>Generated with AI travel pacing & energy optimization</Text>

        <View style={styles.timeline}>
          {legs.map((leg, index) => (
            <View key={leg.id} style={styles.legCard}>
              <View style={styles.timeTag}>
                <Text style={styles.timeText}>{leg.time}</Text>
                <Text style={styles.modeText}>{leg.mode}</Text>
              </View>

              <Text style={styles.legTitle}>{leg.title}</Text>
              <Text style={styles.legMetrics}>
                ⏱️ {leg.durationMins} mins • 📏 {leg.distanceKm} km
              </Text>
              <Text style={styles.legNotes}>{leg.notes}</Text>
            </View>
          ))}
        </View>

        <TouchableOpacity
          activeOpacity={0.85}
          onPress={() => router.push('/navigation')}
          style={styles.startBtn}
        >
          <Text style={styles.startBtnText}>🚀 Start Full Itinerary Journey</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.background
  },
  container: {
    padding: tokens.spacing.md,
    gap: 12
  },
  heading: {
    fontSize: 20,
    fontWeight: '900',
    color: '#ffffff'
  },
  subtitle: {
    fontSize: 13,
    color: colors.textMuted
  },
  timeline: {
    gap: 12,
    marginVertical: 8
  },
  legCard: {
    backgroundColor: colors.backgroundGlass,
    borderWidth: 1.5,
    borderColor: colors.borderCyan,
    borderRadius: tokens.radii.lg,
    padding: tokens.spacing.md,
    ...tokens.elevation.card
  },
  timeTag: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6
  },
  timeText: {
    color: colors.cyan,
    fontSize: 13,
    fontWeight: '800'
  },
  modeText: {
    color: colors.textSecondary,
    fontSize: 12,
    fontWeight: '600'
  },
  legTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#ffffff',
    marginBottom: 4
  },
  legMetrics: {
    fontSize: 13,
    color: colors.emerald,
    fontWeight: '700',
    marginBottom: 6
  },
  legNotes: {
    fontSize: 12,
    color: colors.textMuted,
    lineHeight: 17
  },
  startBtn: {
    minHeight: 48,
    backgroundColor: colors.emeraldDark,
    borderWidth: 2,
    borderColor: colors.emerald,
    borderRadius: tokens.radii.md,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8
  },
  startBtnText: {
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '900'
  }
});
