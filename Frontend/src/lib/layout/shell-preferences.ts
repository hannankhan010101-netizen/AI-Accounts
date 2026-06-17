/** Persisted shell UI preferences (localStorage). */

export type SidebarMode = "expanded" | "compact";

const SIDEBAR_MODE_KEY = "layout:sidebar-mode";
const OPEN_GROUPS_KEY = "layout:nav-open-groups";

export function readSidebarMode(): SidebarMode {
  if (typeof window === "undefined") return "expanded";
  const raw = localStorage.getItem(SIDEBAR_MODE_KEY);
  return raw === "compact" ? "compact" : "expanded";
}

export function writeSidebarMode(mode: SidebarMode): void {
  localStorage.setItem(SIDEBAR_MODE_KEY, mode);
}

export function readOpenGroups(): Record<string, boolean> {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(OPEN_GROUPS_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as unknown;
    return typeof parsed === "object" && parsed !== null ? (parsed as Record<string, boolean>) : {};
  } catch {
    return {};
  }
}

export function writeOpenGroups(groups: Record<string, boolean>): void {
  localStorage.setItem(OPEN_GROUPS_KEY, JSON.stringify(groups));
}
