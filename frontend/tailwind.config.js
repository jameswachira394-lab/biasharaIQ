/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        white: 'var(--text-white)',
        /* ── Cream Palette ── */
        cream: {
          50: '#FFFDF8',
          100: '#FDF6EC',
          200: '#FAF3E0',
          300: '#F5EFE6',
          400: '#EDE3D8',
          500: '#E0D0BC',
        },
        /* ── Brown Palette ── */
        brown: {
          900: '#2C1810',
          800: '#3C2A1E',
          700: '#5C4033',
          600: '#6F4A2D',
          500: '#8B5E3C',
          400: '#A67B5B',
          300: '#C4A484',
          200: '#DCC9B0',
        },
        /* ── Semantic Colors ── */
        semantic: {
          white: 'var(--text-white)',
          success: 'var(--success-green)',
          error: 'var(--error-red)',
          textDark: '#2C1810',
          textSecondary: 'var(--text-secondary)',
          textMuted: 'var(--text-muted)',
          textLight: 'var(--text-light)',
          accentBlue: 'var(--accent-primary)',
          accentPurple: 'var(--accent-secondary)',
          accentGold: 'var(--accent-yellow)',
          bgMain: 'var(--bg-main)',
          bgSidebar: 'var(--bg-sidebar)',
        },
        /* ── Chart Palette (warm tones) ── */
        chart: {
          brown: '#8B5E3C',
          mocha: '#A67B5B',
          teal: '#14B8A6',
          amber: '#D97706',
          rose: '#E11D48',
          forest: '#4A7C59',
        },
        /* ── Text Colors ── */
        text: {
          white: 'var(--text-white)',
          dark: '#2C1810',
          secondary: 'var(--text-secondary)',
          muted: 'var(--text-muted)',
          light: 'var(--text-light)',
        },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        display: ['var(--font-syne)', 'sans-serif'],
        mono: ['var(--font-jetbrains)', 'monospace'],
      },
    },
  },
  plugins: [],
}
