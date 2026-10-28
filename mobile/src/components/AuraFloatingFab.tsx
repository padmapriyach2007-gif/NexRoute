import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';
import { colors } from '../theme/colors';
import { tokens } from '../theme/tokens';

export interface AuraFloatingFabProps {
  onPress: () => void;
}

export const AuraFloatingFab: React.FC<AuraFloatingFabProps> = ({ onPress }) => {
  return (
    <TouchableOpacity
      activeOpacity={0.8}
      onPress={onPress}
      style={styles.fab}
    >
      <Text style={styles.icon}>✨</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  fab: {
    position: 'absolute',
    bottom: 24,
    right: 20,
    width: 54,
    height: 54,
    borderRadius: 27,
    backgroundColor: colors.violetDark,
    borderWidth: 2,
    borderColor: colors.violet,
    alignItems: 'center',
    justifyContent: 'center',
    ...tokens.elevation.fab,
    zIndex: 9999
  },
  icon: {
    fontSize: 24
  }
});
