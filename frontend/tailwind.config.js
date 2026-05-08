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
          white: 'var(--text-light)',
          success: 'var(--success-green)',
          error: 'var(--error-red)',
          textDark: 'var(--text-dark)',
          textSecondary: 'var(--text-secondary)',
          textMuted: 'var(--text-muted)',
          textLight: 'var(--text-light)',
          accentBlue: 'var(--visa-blue)',
          accentGold: 'var(--visa-gold)',
        },
        /* ── Text Colors ── */
        text: {
          white: 'var(--text-light)',
          dark: 'var(--text-dark)',
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
