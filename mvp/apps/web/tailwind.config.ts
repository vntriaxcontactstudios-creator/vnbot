import type { Config } from 'tailwindcss';

// VNBOT canonical palette — from docs/05-DISENO-UI-UX §4.1
// Source of truth: do not edit these values without updating the design doc.
const VNBOT_TOKENS = {
  void: '#070A12', // deepest background
  bg: {
    0: '#0A1020',
    1: '#101B2E',
  },
  panel: {
    0: '#12243A',
    1: '#173653',
    2: '#1C4664',
  },
  line: {
    DEFAULT: '#2A6F8E',
    soft: '#1D465E',
  },
  text: {
    DEFAULT: '#ECF6FF',
    muted: '#91A9BE',
  },
  // Semantic accents (per VNBOT color meaning §4.2)
  cyan: '#20DCE8', // normal / memory / active
  blue: '#4D9DFF', // info / nav / query
  magenta: '#D94BE3', // creativity / specialized agent
  violet: '#8A6CFF', // graph / relations / knowledge
  amber: '#FFC83D', // attention / waiting / next task
  green: '#5BDF82', // completed / safe
  red: '#FF5C6D', // error / blocked / risk
  white: '#FFFFFF',
} as const;

export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
    '../../packages/{ui,pixelart}/src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        vnbot: VNBOT_TOKENS,
      },
      fontFamily: {
        pixel: ['"Press Start 2P"', 'monospace'], // titles pixel art
        display: ['"Space Grotesk"', 'sans-serif'], // navigation
        body: ['Inter', 'sans-serif'], // messages
        mono: ['"JetBrains Mono"', 'monospace'], // logs / JSON
      },
      clipPath: {
        // Angular clip-path pixel-perfect for PixelPanel/HudFrame (per UI §18)
        'pixel-panel':
          'polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px))',
        'hud-frame':
          'polygon(12px 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%, 0 12px)',
        'corner-cut': 'polygon(8px 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%, 0 8px)',
      },
      animation: {
        'visor-pulse': 'visor-pulse 2s ease-in-out infinite',
        bob: 'bob 3s ease-in-out infinite',
        'scan-line': 'scan-line 8s linear infinite',
      },
      keyframes: {
        'visor-pulse': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
        bob: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-1px)' }, // integer pixel movement (per UI §19.6)
        },
        'scan-line': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
      },
      boxShadow: {
        'glow-cyan': '0 0 24px rgba(32, 220, 232, 0.4)',
        'glow-amber': '0 0 24px rgba(255, 200, 61, 0.4)',
        'glow-violet': '0 0 24px rgba(138, 108, 255, 0.4)',
        'panel-inset': 'inset 0 0 16px rgba(32, 220, 232, 0.15)',
      },
    },
  },
  plugins: [],
} satisfies Config;
