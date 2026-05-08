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
        white: 'var(--text-light)',
        /* ── Primary Navy (cards/headers) ── */
        navy: {
          950: '#0A2540',
          900: '#0D2E52',
          800: '#10366A',
          700: '#134282',
          600: '#164E9A',
        },
        /* ── Semantic Colors ── */
        semantic: {
          white: 'var(--text-white)',
          success: 'var(--success-green)',
          error: 'var(--error-red)',
          textDark: '#0F172A',
          textSecondary: 'var(--text-secondary)',
          textMuted: 'var(--text-muted)',
          textLight: 'var(--text-light)',
          accentBlue: 'var(--accent-primary)',
          accentPurple: 'var(--accent-secondary)',
          accentGold: 'var(--accent-yellow)',
          bgMain: 'var(--bg-main)',
          bgSidebar: 'var(--bg-sidebar)',
        },
        /* ── Chart Palette ── */
        chart: {
          pink: '#EC4899',
          purple: '#A855F7',
          blue: '#6366F1',
          teal: '#14B8A6',
          yellow: '#EAB308',
          magenta: '#D946EF',
        },
        /* ── Text Colors ── */
        text: {
          white: 'var(--text-white)',
          dark: '#0F172A',
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
