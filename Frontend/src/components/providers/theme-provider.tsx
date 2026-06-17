"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import {
  applyThemeClass,
  readThemeMode,
  writeThemeMode,
  type ThemeMode,
} from "@/lib/theme/storage";

interface ThemeContextValue {
  mode: ThemeMode;
  resolvedDark: boolean;
  setMode: (mode: ThemeMode) => void;
  cycleMode: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

const CYCLE: ThemeMode[] = ["light", "dark", "system"];

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setModeState] = useState<ThemeMode>("system");
  const [resolvedDark, setResolvedDark] = useState(false);

  useEffect(() => {
    const stored = readThemeMode();
    setModeState(stored);
    applyThemeClass(stored);
  }, []);

  useEffect(() => {
    const sync = () => {
      setResolvedDark(document.documentElement.classList.contains("dark"));
    };
    sync();
    const observer = new MutationObserver(sync);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
    return () => observer.disconnect();
  }, [mode]);

  useEffect(() => {
    if (mode !== "system") return;
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => applyThemeClass("system");
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, [mode]);

  const setMode = useCallback((next: ThemeMode) => {
    setModeState(next);
    writeThemeMode(next);
    applyThemeClass(next);
  }, []);

  const cycleMode = useCallback(() => {
    setModeState((current) => {
      const idx = CYCLE.indexOf(current);
      const next = CYCLE[(idx + 1) % CYCLE.length] ?? "system";
      writeThemeMode(next);
      applyThemeClass(next);
      return next;
    });
  }, []);

  const value = useMemo(
    () => ({ mode, resolvedDark, setMode, cycleMode }),
    [mode, resolvedDark, setMode, cycleMode],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider");
  return ctx;
}
