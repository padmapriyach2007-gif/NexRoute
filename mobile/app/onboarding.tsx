import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { deviceLocation } from '../src/services/location/deviceLocation';
import { SUPPORTED_LANGUAGES, SupportedLanguage, setLanguage, getLanguage } from '../src/i18n';
import { colors } from '../src/theme/colors';
import { tokens } from '../src/theme/tokens';

export default function OnboardingScreen() {
  const router = useRouter();
  const [selectedLang, setSelectedLang] = useState<SupportedLanguage>(getLanguage());

  const handleGrantLocation = async () => {
    await deviceLocation.requestPermissions();
    router.replace('/');
  };

  const handleSkipLocation = () => {
    router.replace('/');
  };

  const handleChooseLanguage = (lang: SupportedLanguage) => {
    setLanguage(lang);
    setSelectedLang(lang);
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.heroSection}>
          <View style={styles.emblemCircle}>
            <Text style={styles.emblemIcon}>🧭</Text>
          </View>
          <Text style={styles.title}>Welcome to NexRoute</Text>
          <Text style={styles.subtitle}>
            Next-Generation Adaptive AI Navigation & Multi-Objective Journey Optimization
          </Text>
        </View>

        {/* Language Selection Grid */}
        <Text style={styles.sectionLabel}>Select Your Language / మీ భాషను ఎంచుకోండి</Text>
        <View style={styles.langGrid}>
          {(Object.keys(SUPPORTED_LANGUAGES) as SupportedLanguage[]).map((code) => {
            const meta = SUPPORTED_LANGUAGES[code];
            const isActive = code === selectedLang;
            return (
              <TouchableOpacity
                key={code}
                onPress={() => handleChooseLanguage(code)}
                style={[styles.langChip, isActive && styles.langChipActive]}
              >
                <Text style={[styles.langText, isActive && styles.langTextActive]}>
                  {meta.native}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Permission Explanation Box */}
        <View style={styles.permissionCard}>
          <Text style={styles.cardHeader}>📍 Accurate Location Awareness</Text>
          <Text style={styles.cardBody}>
            NexRoute uses your device GPS to provide turn-by-turn spoken guidance, live speed alerts, and automatic off-route replanning.
            {'\n\n'}
            Your location data is processed locally and never sold. You may also skip and use manual search at any time.
          </Text>
        </View>

        {/* Actions */}
        <View style={styles.actions}>
          <TouchableOpacity
            activeOpacity={0.85}
            onPress={handleGrantLocation}
            style={styles.primaryBtn}
          >
            <Text style={styles.primaryBtnText}>Enable Location & Continue</Text>
          </TouchableOpacity>

          <TouchableOpacity
            activeOpacity={0.8}
            onPress={handleSkipLocation}
            style={styles.skipBtn}
          >
            <Text style={styles.skipBtnText}>Skip for Now (Manual Search)</Text>
          </TouchableOpacity>
        </View>
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
    padding: tokens.spacing.xl,
    gap: 16
  },
  heroSection: {
    alignItems: 'center',
    marginVertical: tokens.spacing.md
  },
  emblemCircle: {
    width: 68,
    height: 68,
    borderRadius: 34,
    backgroundColor: 'rgba(0, 240, 255, 0.15)',
    borderWidth: 2,
    borderColor: colors.cyan,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12
  },
  emblemIcon: {
    fontSize: 32
  },
  title: {
    fontSize: 24,
    fontWeight: '900',
    color: '#ffffff',
    textAlign: 'center'
  },
  subtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: 6,
    lineHeight: 20
  },
  sectionLabel: {
    fontSize: 13,
    fontWeight: '800',
    color: colors.cyan,
    textTransform: 'uppercase',
    marginTop: 4
  },
  langGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8
  },
  langChip: {
    backgroundColor: colors.backgroundCard,
    borderWidth: 1.5,
    borderColor: colors.borderSubtle,
    borderRadius: tokens.radii.sm,
    paddingHorizontal: 12,
    paddingVertical: 8
  },
  langChipActive: {
    borderColor: colors.cyan,
    backgroundColor: 'rgba(0, 240, 255, 0.20)'
  },
  langText: {
    color: colors.textSecondary,
    fontSize: 13,
    fontWeight: '700'
  },
  langTextActive: {
    color: '#ffffff'
  },
  permissionCard: {
    backgroundColor: colors.backgroundGlass,
    borderWidth: 1,
    borderColor: colors.borderCyan,
    borderRadius: tokens.radii.lg,
    padding: tokens.spacing.md
  },
  cardHeader: {
    fontSize: 15,
    fontWeight: '800',
    color: '#ffffff',
    marginBottom: 6
  },
  cardBody: {
    fontSize: 13,
    color: colors.textMuted,
    lineHeight: 19
  },
  actions: {
    marginTop: 10,
    gap: 10
  },
  primaryBtn: {
    minHeight: 48,
    backgroundColor: colors.cyanMuted,
    borderWidth: 1.5,
    borderColor: colors.cyan,
    borderRadius: tokens.radii.md,
    alignItems: 'center',
    justifyContent: 'center'
  },
  primaryBtnText: {
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '800'
  },
  skipBtn: {
    minHeight: 42,
    alignItems: 'center',
    justifyContent: 'center'
  },
  skipBtnText: {
    color: colors.textMuted,
    fontSize: 13,
    fontWeight: '600'
  }
});
