import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { colors } from '../src/theme/colors';
import { tokens } from '../src/theme/tokens';

interface DestinationItem {
  id: string;
  name: string;
  category: string;
  distanceKm: number;
  icon: string;
  description: string;
  isAccessible: boolean;
  coordinates: { latitude: number; longitude: number };
}

const SAMPLE_DESTINATIONS: DestinationItem[] = [
  {
    id: 'dest_1',
    name: 'Vignan University Campus',
    category: 'Education & Innovation',
    distanceKm: 2.4,
    icon: '🏛️',
    description: 'Main academic hub with pedestrian pathways and EV charging.',
    isAccessible: true,
    coordinates: { latitude: 16.2335, longitude: 80.5505 }
  },
  {
    id: 'dest_2',
    name: 'Prakasam Barrage & Krishna Riverwalk',
    category: 'Scenic & Landmarks',
    distanceKm: 18.2,
    icon: '🌉',
    description: 'Historic architectural landmark spanning the Krishna river with cycling paths.',
    isAccessible: true,
    coordinates: { latitude: 16.5062, longitude: 80.6050 }
  },
  {
    id: 'dest_3',
    name: 'Undavalli Caves & Heritage Monument',
    category: 'Historical Heritage',
    distanceKm: 14.8,
    icon: '🗿',
    description: 'Ancient rock-cut monolithic caves from the 4th-5th centuries.',
    isAccessible: false,
    coordinates: { latitude: 16.4965, longitude: 80.5815 }
  },
  {
    id: 'dest_4',
    name: 'Bhavani Island Adventure Park',
    category: 'Outdoor & Nature',
    distanceKm: 21.0,
    icon: '🏝️',
    description: 'River island retreat featuring walking trails, boating, and gardens.',
    isAccessible: true,
    coordinates: { latitude: 16.5180, longitude: 80.5900 }
  }
];

export default function DestinationsScreen() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');

  const filtered = SAMPLE_DESTINATIONS.filter((item) => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <View style={styles.searchBar}>
          <Text style={styles.searchIcon}>🔍</Text>
          <TextInput
            style={styles.searchInput}
            placeholder="Search attractions, landmarks, nature..."
            placeholderTextColor={colors.textMuted}
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </View>

        <FlatList
          data={filtered}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <View style={styles.placeCard}>
              <View style={styles.placeHeader}>
                <View style={styles.iconCircle}>
                  <Text style={styles.placeIcon}>{item.icon}</Text>
                </View>
                <View style={styles.placeTitleWrap}>
                  <Text style={styles.placeName}>{item.name}</Text>
                  <Text style={styles.placeCategory}>{item.category} • {item.distanceKm} km</Text>
                </View>
              </View>

              <Text style={styles.placeDescription}>{item.description}</Text>

              <View style={styles.placeActions}>
                {item.isAccessible && (
                  <View style={styles.accessBadge}>
                    <Text style={styles.accessText}>♿ Step-Free</Text>
                  </View>
                )}

                <TouchableOpacity
                  activeOpacity={0.8}
                  onPress={() => router.push('/')}
                  style={styles.routeBtn}
                >
                  <Text style={styles.routeBtnText}>🧭 Route Here</Text>
                </TouchableOpacity>
              </View>
            </View>
          )}
          contentContainerStyle={styles.listContent}
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
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.backgroundCard,
    borderWidth: 1.5,
    borderColor: colors.borderCyan,
    borderRadius: tokens.radii.md,
    paddingHorizontal: 12,
    height: 44,
    marginBottom: 12,
    gap: 8
  },
  searchIcon: {
    fontSize: 16
  },
  searchInput: {
    flex: 1,
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600'
  },
  listContent: {
    gap: 12
  },
  placeCard: {
    backgroundColor: colors.backgroundGlass,
    borderWidth: 1,
    borderColor: colors.borderSubtle,
    borderRadius: tokens.radii.lg,
    padding: tokens.spacing.md,
    ...tokens.elevation.card
  },
  placeHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 8
  },
  iconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(6, 182, 212, 0.15)',
    borderWidth: 1,
    borderColor: colors.cyan,
    alignItems: 'center',
    justifyContent: 'center'
  },
  placeIcon: {
    fontSize: 20
  },
  placeTitleWrap: {
    flex: 1
  },
  placeName: {
    fontSize: 16,
    fontWeight: '800',
    color: '#ffffff'
  },
  placeCategory: {
    fontSize: 12,
    color: colors.textMuted,
    marginTop: 2
  },
  placeDescription: {
    fontSize: 13,
    color: colors.textSecondary,
    lineHeight: 18,
    marginBottom: 10
  },
  placeActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  accessBadge: {
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
    borderWidth: 1,
    borderColor: colors.emerald,
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 3
  },
  accessText: {
    color: colors.emerald,
    fontSize: 11,
    fontWeight: '700'
  },
  routeBtn: {
    backgroundColor: colors.cyanMuted,
    borderWidth: 1,
    borderColor: colors.cyan,
    borderRadius: tokens.radii.sm,
    paddingHorizontal: 14,
    paddingVertical: 6
  },
  routeBtnText: {
    color: '#ffffff',
    fontSize: 13,
    fontWeight: '700'
  }
});
