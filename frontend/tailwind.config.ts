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
        background: "#F5F6F6",
        card: "#FFFFFF",
        secondary: "#f5f4f3",
        "text-secondary": "#6b7280",
        "accent-pink": "#FC2BA3",
        "accent-orange": "#FC6D35",
        "accent-yellow": "#F9C83D",
        "accent-light-blue": "#C2D6E1",
        "accent-blue": "#144EC5",
        "accent-sky": "#0ea5e9",
      },
      boxShadow: {
        soft: "0 10px 20px -6px rgba(0, 0, 0, 0.1)",
        medium: "0 10px 20px -6px rgba(0, 0, 0, 0.2)",
      },
      borderRadius: {
        chat: "14px",
      },
    },
  },
  plugins: [],
};
export default config;
