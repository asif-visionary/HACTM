/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        hactm: {
          bg: '#070B12',
          surface: '#0B111A',
          card: '#101923',
          panel: '#131E2A',
          border: '#1E2D3D',
          hover: '#192837',
          accent: '#00B8FF',
          secondary: '#6366F1',
          muted: '#8A99AD',
          text: '#E2E8F0',
          heading: '#FFFFFF',
        },
        risk: {
          low: '#10B981',
          medium: '#F59E0B',
          high: '#F97316',
          critical: '#EF4444',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        'panel': '0 4px 20px -2px rgba(0, 0, 0, 0.5)',
        'accent-subtle': '0 0 15px -3px rgba(0, 184, 255, 0.15)',
      }
    },
  },
  plugins: [],
}
