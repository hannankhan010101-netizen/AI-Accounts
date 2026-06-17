import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    screens: {
      xs: "375px",
      sm: "640px",
      md: "768px",
      lg: "1024px",
      xl: "1280px",
      "2xl": "1536px",
      "max-h-sm": { raw: "(max-height: 500px) and (orientation: landscape)" },
    },
    extend: {
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "Segoe UI", "sans-serif"],
      },
      colors: {
        brand: {
          DEFAULT: "var(--brand-600)",
          foreground: "var(--brand-foreground)",
          50: "var(--brand-50)",
          100: "var(--brand-100)",
          200: "var(--brand-200)",
          300: "var(--brand-300)",
          400: "var(--brand-400)",
          500: "var(--brand-500)",
          600: "var(--brand-600)",
          700: "var(--brand-700)",
          800: "var(--brand-800)",
          900: "var(--brand-900)",
        },
        accent: {
          DEFAULT: "var(--accent-sage)",
          sage: "var(--accent-sage)",
        },
        canvas: "var(--bg-canvas)",
        surface: {
          DEFAULT: "var(--bg-surface)",
          elevated: "var(--bg-surface-elevated)",
          muted: "var(--bg-surface-muted)",
          accent: "var(--bg-surface-accent)",
        },
        elevated: "var(--bg-surface-elevated)",
        fg: {
          DEFAULT: "var(--fg-default)",
          muted: "var(--fg-muted)",
          onBrand: "var(--fg-on-brand)",
        },
        border: {
          DEFAULT: "var(--border-default)",
          subtle: "var(--border-subtle)",
          strong: "var(--border-strong)",
        },
        status: {
          success: "var(--status-success)",
          warning: "var(--status-warning)",
          danger: "var(--status-danger)",
          info: "var(--status-info)",
        },
        chart: {
          1: "var(--chart-1)",
          2: "var(--chart-2)",
          3: "var(--chart-3)",
          4: "var(--chart-4)",
          5: "var(--chart-5)",
        },
        overlay: {
          scrim: "var(--overlay-scrim)",
        },
      },
      backgroundImage: {
        "gradient-brand": "var(--gradient-brand-subtle)",
        "gradient-mesh": "var(--gradient-surface-mesh)",
      },
      boxShadow: {
        xs: "var(--shadow-xs)",
        sm: "var(--shadow-sm)",
        md: "var(--shadow-md)",
        lg: "var(--shadow-lg)",
        xl: "var(--shadow-xl)",
        premium: "var(--shadow-premium)",
        "brand-glow": "0 0 0 1px color-mix(in srgb, var(--brand-600) 12%, transparent), 0 4px 20px var(--glow-brand)",
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        xl: "var(--radius-xl)",
        "2xl": "var(--radius-2xl)",
      },
      spacing: {
        section: "var(--space-section)",
        card: "var(--space-card)",
        inline: "var(--space-inline)",
      },
      fontSize: {
        display: "var(--text-display)",
        section: "var(--text-section)",
        label: "var(--text-label)",
        caption: "var(--text-caption)",
      },
      ringColor: {
        DEFAULT: "var(--focus-ring)",
        brand: "var(--brand-600)",
      },
      zIndex: {
        drawer: "var(--z-drawer)",
        modal: "var(--z-modal)",
        command: "var(--z-command)",
        tour: "var(--z-tour)",
      },
      transitionDuration: {
        instant: "var(--motion-instant)",
        fast: "var(--motion-fast)",
        base: "var(--motion-base)",
        slow: "var(--motion-slow)",
        enter: "var(--motion-enter)",
        stagger: "var(--motion-stagger)",
      },
      transitionTimingFunction: {
        out: "var(--ease-out)",
        "in-out": "var(--ease-in-out)",
      },
      width: {
        "sidebar-expanded": "var(--sidebar-width-expanded)",
        "sidebar-compact": "var(--sidebar-width-compact)",
      },
    },
  },
  plugins: [],
};
export default config;
