import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { RouteManeuver } from '../types/routing';
import { colors } from '../theme/colors';
import { tokens } from '../theme/tokens';

export interface TurnInstructionCardProps {
  currentManeuver: RouteManeuver | null;
  nextManeuver: RouteManeuver | null;
  distanceMeters: number;
}

export const TurnInstructionCard: React.FC<TurnInstructionCardProps> = ({
  currentManeuver,
  nextManeuver,
  distanceMeters
}) => {
  if (!currentManeuver) {
    return (
      <View style={styles.container}>
        <Text style={styles.standbyText}>Proceeding on route...</Text>
      </View>
    );
  }

  const formatDistance = (m: number) => {
    if (m >= 1000) {
      return `${(m / 1000).toFixed(1)} km`;
    }
    return `${Math.round(m)} m`;
  };

  const getManeuverIcon = (type?: string, mod?: string) => {
    const text = `${type || ''} ${mod || ''}`.toLowerCase();
    if (text.includes('left')) return '↰';
    if (text.includes('right')) return '↱';
    if (text.includes('uturn')) return '↶';
    if (text.includes('arrive')) return '🏁';
    if (text.includes('depart')) return '🚗';
    return '↑';
  };

  return (
    <View style={styles.container}>
      <View style={styles.topRow}>
        <View style={styles.iconCircle}>
          <Text style={styles.iconText}>
            {getManeuverIcon(currentManeuver.type, currentManeuver.modifier)}
          </Text>
        </View>

        <View style={styles.instructionWrap}>
          <Text style={styles.distanceText}>{formatDistance(distanceMeters)}</Text>
          <Text style={styles.instructionText} numberOfLines={2}>
            {currentManeuver.instruction}
          </Text>
        </View>
      </View>

      {nextManeuver && (
        <View style={styles.subsequentRow}>
          <Text style={styles.thenText}>Then:</Text>
          <Text style={styles.nextText} numberOfLines={1}>
            {getManeuverIcon(nextManeuver.type, nextManeuver.modifier)} {nextManeuver.instruction}
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#0a192f',
    borderRadius: tokens.radii.lg,
    borderWidth: 1.5,
    borderColor: colors.cyan,
    padding: tokens.spacing.md,
    ...tokens.elevation.card
  },
  topRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: tokens.spacing.md
  },
  iconCircle: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: colors.cyanMuted,
    borderWidth: 2,
    borderColor: colors.cyan,
    alignItems: 'center',
    justifyContent: 'center'
  },
  iconText: {
    fontSize: 26,
    color: '#ffffff',
    fontWeight: '900'
  },
  instructionWrap: {
    flex: 1
  },
  distanceText: {
    fontSize: 22,
    fontWeight: '900',
    color: colors.cyan,
    letterSpacing: 0.5
  },
  instructionText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#ffffff',
    marginTop: 2
  },
  subsequentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: tokens.spacing.sm,
    marginTop: tokens.spacing.sm,
    paddingTop: tokens.spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.borderSubtle
  },
  thenText: {
    fontSize: 12,
    color: colors.textMuted,
    fontWeight: '700',
    textTransform: 'uppercase'
  },
  nextText: {
    fontSize: 13,
    color: colors.textSecondary,
    flex: 1
  },
  standbyText: {
    fontSize: 16,
    color: colors.textSecondary,
    textAlign: 'center',
    fontWeight: '600'
  }
});
