import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ["var(--font-syne)", "sans-serif"],
        sans: ["var(--font-jakarta)", "sans-serif"],
        mono: ["var(--font-dm-mono)", "monospace"],
      },
      colors: {
        base: {
          "950": "#080910",
          "900": "#0C0D12",
          "800": "#12141C",
          "700": "#191C28",
          "600": "#212436",
          "500": "#2C3045",
        },
        border: "#252838",
        amber: {
          DEFAULT: "#FFC533",
          dim: "#9A6E00",
          glow: "rgba(255,197,51,0.15)",
        },
        purple: {
          DEFAULT: "#6010C6",
          dim: "#3B0875",
          glow: "rgba(96,16,198,0.15)",
        },
        emerald: {
          DEFAULT: "#10B981",
          dim: "#065F46",
          glow: "rgba(16,185,129,0.15)",
        },
        crimson: "#EF4444",
        text: {
          primary: "#EDEEF2",
          secondary: "#8B8FA8",
          muted: "#555870",
        },
      },
      animation: {
        "fade-up": "fadeUp 0.3s ease forwards",
        "slide-in": "slideIn 0.25s ease forwards",
        "pulse-dot": "pulseDot 2s infinite",
        shimmer: "shimmer 1.5s infinite",
      },
      keyframes: {
        fadeUp: {
          from: { opacity: "0", transform: "translateY(6px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        slideIn: {
          from: { opacity: "0", transform: "translateX(-8px)" },
          to: { opacity: "1", transform: "translateX(0)" },
        },
        pulseDot: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.4" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
  plugins: [],
};
export default config;
