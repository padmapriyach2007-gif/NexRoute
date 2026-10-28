import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, ViewStyle, TextStyle } from 'react-native';
import { colors } from '../theme/colors';
import { tokens } from '../theme/tokens';

export interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'danger' | 'outline';
  disabled?: boolean;
  loading?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  disabled = false,
  loading = false,
  style,
  textStyle,
  icon
}) => {
  const getBackgroundColor = () => {
    if (disabled) return colors.textDark;
    switch (variant) {
      case 'primary':
        return colors.cyanMuted;
      case 'secondary':
        return colors.backgroundCard;
      case 'danger':
        return colors.roseDark;
      case 'outline':
        return 'transparent';
      default:
        return colors.cyanMuted;
    }
  };

  const getBorderColor = () => {
    if (disabled) return 'transparent';
    switch (variant) {
      case 'primary':
        return colors.cyan;
      case 'secondary':
        return colors.borderCyan;
      case 'danger':
        return colors.rose;
      case 'outline':
        return colors.cyan;
      default:
        return colors.cyan;
    }
  };

  const getTextColor = () => {
    if (disabled) return colors.textMuted;
    switch (variant) {
      case 'outline':
        return colors.cyan;
      case 'secondary':
        return colors.textSecondary;
      default:
        return colors.textPrimary;
    }
  };

  return (
    <TouchableOpacity
      activeOpacity={0.8}
      onPress={onPress}
      disabled={disabled || loading}
      style={[
        styles.button,
        {
          backgroundColor: getBackgroundColor(),
          borderColor: getBorderColor()
        },
        style
      ]}
    >
      {loading ? (
        <ActivityIndicator color={getTextColor()} size="small" />
      ) : (
        <>
          {icon}
          <Text style={[styles.text, { color: getTextColor() }, textStyle]}>
            {title}
          </Text>
        </>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    minHeight: tokens.touchTargetMin,
    borderRadius: tokens.radii.md,
    borderWidth: 1.5,
    paddingHorizontal: tokens.spacing.lg,
    paddingVertical: tokens.spacing.sm,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: tokens.spacing.sm
  },
  text: {
    fontSize: 15,
    fontWeight: '700',
    letterSpacing: 0.3
  }
});
