"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  readOpenGroups,
  readSidebarMode,
  writeOpenGroups,
  writeSidebarMode,
  type SidebarMode,
} from "@/lib/layout/shell-preferences";

interface ShellContextValue {
  sidebarMode: SidebarMode;
  setSidebarMode: (mode: SidebarMode) => void;
  toggleSidebarMode: () => void;
  mobileNavOpen: boolean;
  setMobileNavOpen: (open: boolean) => void;
  openGroups: Record<string, boolean>;
  setGroupOpen: (label: string, open: boolean) => void;
}

const ShellContext = createContext<ShellContextValue | null>(null);

export function ShellProvider({ children }: { children: ReactNode }) {
  const [sidebarMode, setSidebarModeState] = useState<SidebarMode>("expanded");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [openGroups, setOpenGroupsState] = useState<Record<string, boolean>>({});

  useEffect(() => {
    setSidebarModeState(readSidebarMode());
    setOpenGroupsState(readOpenGroups());
  }, []);

  const setSidebarMode = useCallback((mode: SidebarMode) => {
    setSidebarModeState(mode);
    writeSidebarMode(mode);
  }, []);

  const toggleSidebarMode = useCallback(() => {
    setSidebarModeState((prev) => {
      const next = prev === "expanded" ? "compact" : "expanded";
      writeSidebarMode(next);
      return next;
    });
  }, []);

  const setGroupOpen = useCallback((label: string, open: boolean) => {
    setOpenGroupsState((prev) => {
      const next = { ...prev, [label]: open };
      writeOpenGroups(next);
      return next;
    });
  }, []);

  const value = useMemo(
    () => ({
      sidebarMode,
      setSidebarMode,
      toggleSidebarMode,
      mobileNavOpen,
      setMobileNavOpen,
      openGroups,
      setGroupOpen,
    }),
    [sidebarMode, setSidebarMode, toggleSidebarMode, mobileNavOpen, openGroups, setGroupOpen],
  );

  return <ShellContext.Provider value={value}>{children}</ShellContext.Provider>;
}

export function useShell() {
  const ctx = useContext(ShellContext);
  if (!ctx) throw new Error("useShell must be used within ShellProvider");
  return ctx;
}
