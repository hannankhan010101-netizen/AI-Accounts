export type ThemeMode = "light" | "dark" | "system";

const THEME_KEY = "theme:mode";

export function readThemeMode(): ThemeMode {
  if (typeof window === "undefined") return "system";
  const raw = localStorage.getItem(THEME_KEY);
  if (raw === "light" || raw === "dark" || raw === "system") return raw;
  return "system";
}

export function writeThemeMode(mode: ThemeMode): void {
  localStorage.setItem(THEME_KEY, mode);
}

export function resolveThemeClass(mode: ThemeMode): "light" | "dark" {
  if (mode === "dark") return "dark";
  if (mode === "light") return "light";
  if (typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    return "dark";
  }
  return "light";
}

export function applyThemeClass(mode: ThemeMode): void {
  const resolved = resolveThemeClass(mode);
  document.documentElement.classList.remove("light", "dark");
  document.documentElement.classList.add(resolved);
}
