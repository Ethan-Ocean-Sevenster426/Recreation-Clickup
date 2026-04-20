/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./home/templates/**/*.html",
    "./main/templates/**/*.html",
    "./static/**/*.js",
    "./static/**/*.css",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'accent': '#ef4444',
        'accent-dark': '#dc2626',
        'eclick-600': '#dc2626',
        'eclick-700': '#b91c1c',
        slate: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
      },
      fontFamily: {
        'inter': ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
