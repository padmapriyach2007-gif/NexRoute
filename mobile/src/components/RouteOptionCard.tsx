import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { RouteAlternative } from '../types/routing';
import { colors } from '../theme/colors';
import { tokens } from '../theme/tokens';

export interface RouteOptionCardProps {
  route: RouteAlternative;
  isSelected: boolean;
  onSelect: () => void;
}

export const RouteOptionCard: React.FC<RouteOptionCardProps> = ({
  route,
  isSelected,
  onSelect
}) => {
  const getObjectiveColor = () => {
    switch (route.objective) {
      case 'FASTEST':
        return colors.routeFastest;
      case 'SHORTEST':
        return colors.routeShortest;
      case 'BALANCED':
        return colors.routeBalanced;
      case 'ACCESSIBLE':
        return colors.routeAccessible;
      default:
        return colors.cyan;
    }
  };

  const formatDuration = (sec: number) => {
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

  const objColor = getObjectiveColor();

  return (
    <TouchableOpacity
      activeOpacity={0.85}
      onPress={onSelect}
      style={[
        styles.card,
        {
          borderColor: isSelected ? objColor : colors.borderSubtle,
          backgroundColor: isSelected ? 'rgba(15, 23, 42, 0.95)' : 'rgba(15, 23, 42, 0.65)'
        }
      ]}
    >
      <View style={styles.headerRow}>
        <View style={styles.badgeRow}>
          <View style={[styles.objectiveDot, { backgroundColor: objColor }]} />
          <Text style={[styles.objectiveText, { color: objColor }]}>
            {route.objective}
          </Text>
          {route.isRecommended && (
            <View style={styles.recBadge}>
              <Text style={styles.recBadgeText}>★ Best</Text>
            </View>
          )}
        </View>

        <Text style={styles.sourceText}>{route.source}</Text>
      </View>

      <View style={styles.metricsRow}>
        <Text style={styles.durationText}>{formatDuration(route.durationSeconds)}</Text>
        <Text style={styles.distanceText}>• {formatDistance(route.distanceMeters)}</Text>
      </View>

      <Text style={styles.summaryText} numberOfLines={1}>
        {route.summary}
      </Text>

      <View style={styles.footerRow}>
        {route.accessibilityLevel === 'VERIFIED_ACCESSIBLE' && (
          <View style={styles.tagPill}>
            <Text style={styles.tagText}>♿ Step-Free</Text>
          </View>
        )}
        {route.tollCostInr !== undefined && (
          <View style={styles.tagPill}>
            <Text style={styles.tagText}>
              {route.tollCostInr === 0 ? '₹0 Tolls' : `₹${route.tollCostInr} Toll`}
            </Text>
          </View>
        )}
        {route.hazardCount !== undefined && (
          <View style={styles.tagPill}>
            <Text style={styles.tagText}>
              {route.hazardCount === 0 ? '🛡️ Clear Path' : `⚠️ ${route.hazardCount} Hazards`}
            </Text>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    borderRadius: tokens.radii.md,
    borderWidth: 2,
    padding: tokens.spacing.md,
    marginBottom: tokens.spacing.sm,
    ...tokens.elevation.card
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6
  },
  objectiveDot: {
    width: 8,
    height: 8,
    borderRadius: 4
  },
  objectiveText: {
    fontSize: 12,
    fontWeight: '800',
    letterSpacing: 0.5,
    textTransform: 'uppercase'
  },
  recBadge: {
    backgroundColor: 'rgba(16, 185, 129, 0.25)',
    borderWidth: 1,
    borderColor: colors.emerald,
    borderRadius: 4,
    paddingHorizontal: 4,
    paddingVertical: 1
  },
  recBadgeText: {
    fontSize: 10,
    color: colors.emerald,
    fontWeight: '800'
  },
  sourceText: {
    fontSize: 11,
    color: colors.textMuted
  },
  metricsRow: {
    flexDirection: 'row',
    alignItems: 'baseline',
    gap: 6,
    marginVertical: 2
  },
  durationText: {
    fontSize: 20,
    fontWeight: '900',
    color: colors.textPrimary
  },
  distanceText: {
    fontSize: 15,
    fontWeight: '700',
    color: colors.textSecondary
  },
  summaryText: {
    fontSize: 13,
    color: colors.textMuted,
    marginBottom: 6
  },
  footerRow: {
    flexDirection: 'row',
    gap: 6,
    flexWrap: 'wrap'
  },
  tagPill: {
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 6,
    paddingHorizontal: 6,
    paddingVertical: 2
  },
  tagText: {
    fontSize: 11,
    color: colors.textSecondary,
    fontWeight: '600'
  }
});
