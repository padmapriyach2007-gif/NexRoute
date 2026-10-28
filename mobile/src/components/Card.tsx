import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { colors } from '../theme/colors';
import { tokens } from '../theme/tokens';

export interface CardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  variant?: 'glass' | 'panel' | 'highlight';
}

export const Card: React.FC<CardProps> = ({ children, style, variant = 'glass' }) => {
  const getBackground = () => {
    switch (variant) {
      case 'highlight':
        return colors.violetDark;
      case 'panel':
        return colors.backgroundCard;
      default:
        return colors.backgroundGlass;
    }
  };

  const getBorder = () => {
    switch (variant) {
      case 'highlight':
        return colors.violet;
      default:
        return colors.borderCyan;
    }
  };

  return (
    <View
      style={[
        styles.card,
        {
          backgroundColor: getBackground(),
          borderColor: getBorder()
        },
        style
      ]}
    >
      {children}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    borderRadius: tokens.radii.lg,
    borderWidth: 1,
    padding: tokens.spacing.md,
    ...tokens.elevation.card
  }
});
