import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        soil: {
          50: "#f4f6f3",
          100: "#e5ece4",
          600: "#2f6b4f",
          800: "#1b3f30",
          950: "#14221c"
        },
        field: {
          500: "#315d86",
          700: "#22415f"
        },
        harvest: {
          500: "#a56321"
        }
      },
      boxShadow: {
        panel: "0 16px 40px rgba(31, 44, 36, 0.08)"
      }
    }
  },
  plugins: []
} satisfies Config;

