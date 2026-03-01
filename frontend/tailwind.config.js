/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Outfit', 'system-ui', 'sans-serif'],
      },
      colors: {
        ink: {
          950: '#0a0f1a',
          900: '#0f172a',
          800: '#151c2c',
          700: '#1e293b',
          600: '#334155',
          400: '#94a3b8',
          300: '#cbd5e1',
        },
        accent: {
          amber: '#f59e0b',
          cyan: '#06b6d4',
        },
      },
    },
  },
  plugins: [],
}
