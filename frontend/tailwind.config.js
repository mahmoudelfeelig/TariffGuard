/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#060913",
        sidebar: "#090e19",
        panel: "#111827",
        panelSoft: "#172033",
        line: "#273247",
        mint: "#31d0aa",
        amber: "#f4b740",
        danger: "#f87171",
        sky: "#5aa7ff"
      },
      boxShadow: {
        panel: "0 18px 60px rgb(0 0 0 / 25%)"
      }
    }
  },
  plugins: []
};
