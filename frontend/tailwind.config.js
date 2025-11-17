/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Toyota GR Brand Colors
        'gr-black': '#000000',
        'gr-red': '#E60012',
        'gr-grey': '#2C2C2C',
        'gr-neon': '#00FF88',
        'gr-asphalt': '#1A1A1A',
        // Professional gradients
        'gr-red-dark': '#B3000E',
        'gr-neon-dark': '#00CC6A',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Inter', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'gr-gradient': 'linear-gradient(135deg, #000000 0%, #1A1A1A 50%, #000000 100%)',
        'gr-red-gradient': 'linear-gradient(135deg, #E60012 0%, #FF3366 100%)',
        'gr-neon-gradient': 'linear-gradient(135deg, #00FF88 0%, #00CC6A 100%)',
      },
      boxShadow: {
        'gr': '0 4px 20px rgba(0, 0, 0, 0.5)',
        'gr-red': '0 4px 20px rgba(230, 0, 18, 0.3)',
        'gr-neon': '0 4px 20px rgba(0, 255, 136, 0.3)',
        'gr-lg': '0 10px 40px rgba(0, 0, 0, 0.6)',
        'gr-inner': 'inset 0 2px 4px rgba(0, 0, 0, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(0, 255, 136, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(0, 255, 136, 0.8)' },
        },
      },
    },
  },
  plugins: [],
}

