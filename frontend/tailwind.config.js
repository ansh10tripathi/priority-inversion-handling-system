/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "Segoe UI", "sans-serif"],
        mono: ["Consolas", "Menlo", "monospace"],
      },
      colors: {
        base:  "#0f1117",
        surface: "#161b27",
        border: "#2d3748",
        muted:  "#475569",
      },
    },
  },
  plugins: [],
};
