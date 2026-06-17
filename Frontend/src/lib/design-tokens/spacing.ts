/** Spacing rhythm — mirrors CSS variables in globals.css */
export const spacing = {
  section: "var(--space-section)",
  card: "var(--space-card)",
  inline: "var(--space-inline)",
} as const;

export const typography = {
  display: "var(--text-display)",
  section: "var(--text-section)",
  pageTitle: "var(--text-page-title)",
  body: "var(--text-body)",
  label: "var(--text-label)",
  caption: "var(--text-caption)",
} as const;
