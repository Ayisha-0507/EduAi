/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#0d1117",
          secondary: "#161b22",
          tertiary: "#21262d",
        },
        border: {
          default: "#30363d",
          muted: "#21262d",
        },
        text: {
          primary: "#c9d1d9",
          secondary: "#8b949e",
          link: "#58a6ff",
        },
        accent: {
          green: "#238636",
          greenHover: "#2ea043",
          blue: "#58a6ff",
          purple: "#a371f7",
          red: "#da3633",
          yellow: "#d29922",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
      },
    },
  },
  plugins: [],
};
