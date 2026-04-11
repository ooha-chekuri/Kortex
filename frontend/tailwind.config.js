/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111827",
        mist: "#f3f7f5",
        pine: "#14342b",
        pixel: {
          dark: "#0d0d0d",
          green: "#00ff41",
          cyan: "#00d4ff",
          magenta: "#ff00ff",
          yellow: "#ffff00",
          orange: "#ff6b00",
          purple: "#9d00ff",
          bg: "#1a1a2e",
          card: "#16213e",
          border: "#0f3460"
        }
      },
      boxShadow: {
        card: "0 18px 50px rgba(20, 52, 43, 0.12)",
        pixel: "4px 4px 0px 0px #00ff41",
        "pixel-cyan": "4px 4px 0px 0px #00d4ff",
        "pixel-magenta": "4px 4px 0px 0px #ff00ff"
      },
      fontFamily: {
        display: ["Georgia", "serif"],
        body: ["Segoe UI", "sans-serif"],
        pixel: ["Departure Mono", "monospace", "Courier New"],
        mono: ["Departure Mono", "monospace", "Courier New"]
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" }
        },
        blink: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0" }
        },
        pulse: {
          "0%, 100%": { transform: "scale(1)" },
          "50%": { transform: "scale(1.05)" }
        },
        scanline: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" }
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" }
        },
        typing: {
          "0%": { width: "0" },
          "100%": { width: "100%" }
        },
        glow: {
          "0%, 100%": { boxShadow: "0 0 5px #00ff41, 0 0 10px #00ff41" },
          "50%": { boxShadow: "0 0 10px #00ff41, 0 0 20px #00ff41" }
        },
        shake: {
          "0%, 100%": { transform: "translateX(0)" },
          "10%, 30%, 50%, 70%, 90%": { transform: "translateX(-2px)" },
          "20%, 40%, 60%, 80%": { transform: "translateX(2px)" }
        }
      },
      animation: {
        fadeIn: "fadeIn 0.35s ease-out",
        blink: "blink 1s infinite",
        pulse: "pulse 2s infinite",
        scanline: "scanline 3s linear infinite",
        float: "float 3s ease-in-out infinite",
        typing: "typing 2s steps(30, end) forwards",
        glow: "glow 2s ease-in-out infinite",
        shake: "shake 0.5s ease-in-out"
      }
    },
  },
  plugins: [],
};
