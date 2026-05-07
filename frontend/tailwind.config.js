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
          white: '#FFFFFF',
          success: '#2E7D32',
          error: '#D32F2F',
          textDark: '#1E1E1E',
          textLight: '#F5F5F5',
          accentBlue: '#1A1F71',    /* Visa Blue */
          accentGold: '#F9A825',    /* Visa Gold */
        },
        /* ── Brand palette (legacy) ── */
        brand: {
          50: '#ecfdee',
          100: '#D1FAE5',
          200: '#A7F3D0',
          300: '#6EE7B7',
          400: '#34D399',
          500: '#2E7D32',   /* Updated to new green */
          600: '#059669',
          700: '#0A2540',   /* Updated to navy */
          800: '#065F46',
          900: '#064E3B',
        },
        /* ── Surface palette ── */
        surface: {
          900: '#F5F5F5',   /* Light Gray Background */
          800: '#FFFFFF',   /* White */
          700: '#0A2540',   /* Navy Card Background */
          600: '#161E2A',
          500: '#F5F5F5',   /* Light Gray Border */
          400: '#243347',
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
