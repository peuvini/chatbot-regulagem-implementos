import type { Config } from "tailwindcss";
import daisyui from "daisyui";

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
  plugins: [daisyui],
  daisyui: {
    themes: [
      {
        arips: {
          primary: "#59651f",
          "primary-content": "#ffffff",
          secondary: "#d4aa55",
          "secondary-content": "#201b12",
          accent: "#b9bd45",
          "accent-content": "#15170c",
          neutral: "#595954",
          "neutral-content": "#ffffff",
          "base-100": "#f4f2e9",
          "base-200": "#e8e4d8",
          "base-300": "#d4cec0",
          "base-content": "#22241d",
          info: "#58758a",
          success: "#587629",
          warning: "#c68b37",
          error: "#a8463d"
        }
      }
    ]
  }
} satisfies Config;
