export const tokens = {
  spacing: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 20,
    xxl: 24,
    hero: 32
  },
  radii: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 20,
    full: 9999
  },
  touchTargetMin: 44,
  elevation: {
    card: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 6 },
      shadowOpacity: 0.45,
      shadowRadius: 10,
      elevation: 6
    },
    fab: {
      shadowColor: '#00f0ff',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.55,
      shadowRadius: 14,
      elevation: 8
    }
  }
} as const;
