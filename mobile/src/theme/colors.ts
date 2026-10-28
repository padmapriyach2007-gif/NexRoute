/**
 * NexRoute Quantum Realm Design System Color Palette
 * Deep Space Void #030712 • Electric Cyan #00f0ff • Quantum Violet #a855f7
 */

export const colors = {
  // Backgrounds
  background: '#030712',
  backgroundCard: '#0f172a',
  backgroundGlass: 'rgba(15, 23, 42, 0.75)',
  backgroundGlassLight: 'rgba(30, 41, 59, 0.60)',
  backgroundOverlay: 'rgba(3, 7, 18, 0.92)',

  // Brand Accents
  cyan: '#00f0ff',
  cyanGlow: 'rgba(0, 240, 255, 0.40)',
  cyanMuted: '#0284c7',
  cyanBorder: 'rgba(56, 189, 248, 0.35)',

  violet: '#a855f7',
  violetGlow: 'rgba(168, 85, 247, 0.40)',
  violetDark: '#3b0764',

  emerald: '#10b981',
  emeraldGlow: 'rgba(16, 185, 129, 0.35)',
  emeraldDark: '#064e3b',

  amber: '#f59e0b',
  amberDark: '#78350f',

  rose: '#ef4444',
  roseDark: '#7f1d1d',

  // Neutral Scales
  textPrimary: '#f8fafc',
  textSecondary: '#cbd5e1',
  textMuted: '#94a3b8',
  textDark: '#475569',

  // Borders
  borderSubtle: 'rgba(255, 255, 255, 0.08)',
  borderCyan: 'rgba(0, 217, 255, 0.35)',
  borderEmerald: 'rgba(16, 185, 129, 0.35)',
  borderRose: 'rgba(239, 68, 68, 0.35)',

  // Route Objective Palette (Color-vision safe)
  routeFastest: '#00f0ff',    // Cyan
  routeShortest: '#a855f7',   // Purple
  routeBalanced: '#10b981',   // Emerald
  routeAccessible: '#fbbf24', // Amber
  routeBlocked: '#ef4444'     // Rose
} as const;

export type ThemeColors = typeof colors;
