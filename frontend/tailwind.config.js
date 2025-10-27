/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#00C853',
        accent: '#69F0AE',
        'primary-dark': '#00A043',
        'sidebar-bg': '#0a1410',
        'sidebar-hover': '#0f1f18',
        'chat-bg': '#0d1912',
        'input-bg': '#0a1410',
        'user-bubble': '#00803D',
        'ai-bubble': '#0d1912',
      },
      fontFamily: {
        orbitron: ['Orbitron', 'sans-serif'],
        inter: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'glow-green': '0 0 20px rgba(0, 200, 83, 0.3)',
        'glow-green-lg': '0 0 40px rgba(0, 200, 83, 0.5)',
        'glow-intense': '0 0 50px rgba(0, 200, 83, 0.6)',
      },
    },
  },
  plugins: [],
}
