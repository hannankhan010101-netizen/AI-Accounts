/**
 * Olive enterprise palette — canonical hex values.
 * CSS variables in globals.css are the runtime source of truth for theming.
 */

export const brandScale = {
  50: "#f4f7f0",
  100: "#e4ebe0",
  200: "#c9d4bc",
  300: "#a8b89a",
  400: "#8fa67a",
  500: "#6d8560",
  600: "#556b47",
  700: "#465a3b",
  800: "#384830",
  900: "#2a3624",
} as const;

export const lightPalette = {
  canvas: "#f4f6f0",
  surface: "#fafbf7",
  surfaceElevated: "#ffffff",
  foreground: "#1a1f16",
  foregroundMuted: "#5c6654",
  border: "#dfe3d6",
  borderSubtle: "#e8ebe3",
  borderStrong: "#c5cbb8",
  accentSage: "#7d8f6e",
  brand: brandScale[600],
  brandHover: brandScale[700],
  brandForeground: "#ffffff",
  statusSuccess: "#3d7a4a",
  statusWarning: "#b8860b",
  statusDanger: "#c44d4d",
  statusInfo: brandScale[600],
  chart: ["#556b47", "#7d8f6e", "#5a8a7a", "#a8a090", "#6d8560"] as const,
} as const;

export const darkPalette = {
  canvas: "#0c0f0a",
  surface: "#141812",
  surfaceElevated: "#1a1f17",
  foreground: "#ecefe6",
  foregroundMuted: "#9aa392",
  border: "#2d3328",
  borderSubtle: "#252a21",
  borderStrong: "#3d4536",
  accentSage: "#b5c4a8",
  brand: "#8fa67a",
  brandHover: "#a3b890",
  brandForeground: "#1a1f16",
  statusSuccess: "#5cb86a",
  statusWarning: "#d4a84b",
  statusDanger: "#e07a7a",
  statusInfo: "#8fa67a",
  chart: ["#8fa67a", "#b5c4a8", "#6a9a8a", "#c4b8a8", "#7d8f6e"] as const,
} as const;

export type BrandScale = keyof typeof brandScale;
