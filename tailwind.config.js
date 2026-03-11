/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/**/*.py"
  ],
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'sans-serif'], },
      colors: { brand: { 50: '#eff6ff', 100: '#dbeafe', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8' } },
      boxShadow: { 'glass': '0 10px 40px -10px rgba(0,0,0,0.08)' }
    }
  },
  plugins: [],
}
