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
        /* ── Brand palette ── */
        brand: {
          50: '#ecfdee',
          100: '#D1FAE5',
          200: '#A7F3D0',
          300: '#6EE7B7',
          400: '#34D399',
          500: '#10B981',   /* Emerald Accent */
          600: '#059669',
          700: '#0F6B4F',   /* Deep Green */
          800: '#065F46',
          900: '#064E3B',
        },
        /* ── Surface palette ── */
        surface: {
          900: '#0B0F14',   /* Dark Background */
          800: '#0D1117',
          700: '#121821',   /* Card Background */
          600: '#161E2A',
          500: '#1A2535',   /* Border */
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
