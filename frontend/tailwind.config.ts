import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0A0D1C",
        "background-secondary": "#0F152F",
        card: "#FFFFFF",
        "card-gradient-top": "#121834",
        "card-gradient-bottom": "#090D20",
        "text-primary": "#FFFFFF",
        "text-secondary": "rgba(255, 255, 255, 0.62)",
        "accent-pink": "#FC2BA3",
        "accent-orange": "#FC6D35",
        "accent-yellow": "#F9C83D",
        "accent-light-blue": "#C2D6E1",
        "accent-blue": "#144EC5",
        "accent-sky": "#0ea5e9",
      },
      boxShadow: {
        soft: "0 10px 20px -6px rgba(0, 0, 0, 0.3)",
        medium: "0 10px 20px -6px rgba(0, 0, 0, 0.5)",
      },
      borderRadius: {
        card: "20px",
        button: "14px",
      },
      fontFamily: {
        sans: ['"Helvetica Neue"', 'Helvetica', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
export default config;
