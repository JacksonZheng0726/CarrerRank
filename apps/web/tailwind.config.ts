import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#16231d",
        cream: "#f5f1e8",
        moss: "#325e4b",
        fern: "#6f927d",
        amber: "#db9b43",
      },
      boxShadow: {
        card: "0 22px 55px -32px rgba(22, 35, 29, 0.45)",
      },
    },
  },
  plugins: [],
};

export default config;
