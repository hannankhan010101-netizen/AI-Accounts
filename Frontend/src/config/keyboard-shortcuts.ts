export interface KeyboardShortcut {
  id: string;
  keys: string[];
  description: string;
  /** When true, only shown in shortcuts help (handled elsewhere) */
  global?: boolean;
}

export const keyboardShortcuts: KeyboardShortcut[] = [
  { id: "palette", keys: ["Ctrl", "K"], description: "Open command palette", global: true },
  { id: "copilot", keys: ["Ctrl", "."], description: "Open AI-Assistant", global: true },
  { id: "help", keys: ["?"], description: "Show keyboard shortcuts", global: true },
  { id: "grid-up", keys: ["↑"], description: "Previous row in focused grid" },
  { id: "grid-down", keys: ["↓"], description: "Next row in focused grid" },
  { id: "grid-enter", keys: ["Enter"], description: "Open selected grid row" },
  { id: "grid-home", keys: ["Home"], description: "First row in grid" },
  { id: "grid-end", keys: ["End"], description: "Last row in grid" },
  { id: "palette-nav", keys: ["↑", "↓"], description: "Navigate command palette results" },
  { id: "palette-enter", keys: ["Enter"], description: "Run selected command" },
  { id: "escape", keys: ["Esc"], description: "Close dialog, palette, or mobile nav" },
];

export const shortcutGroups: { title: string; ids: string[] }[] = [
  { title: "Global", ids: ["palette", "copilot", "help", "escape"] },
  { title: "Data tables", ids: ["grid-up", "grid-down", "grid-enter", "grid-home", "grid-end"] },
  { title: "Command palette", ids: ["palette-nav", "palette-enter"] },
];
