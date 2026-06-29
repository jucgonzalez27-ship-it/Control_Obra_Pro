/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#101418",
          900: "#151b22",
          800: "#1e2630"
        },
        site: {
          50: "#f7f8fa",
          100: "#edf0f4",
          200: "#d8dee8"
        }
      },
      boxShadow: {
        soft: "0 12px 30px rgba(15, 23, 42, 0.08)"
      }
    }
  },
  plugins: []
};
