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
