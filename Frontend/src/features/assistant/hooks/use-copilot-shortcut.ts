"use client";

import { useEffect } from "react";

import { useCopilotStore } from "@/stores/assistant/copilot-store";

/** Global Ctrl/Cmd+. opens AI copilot. */
export function useCopilotShortcut() {
  const setOpen = useCopilotStore((s) => s.setOpen);
  const setMode = useCopilotStore((s) => s.setMode);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === ".") {
        e.preventDefault();
        setMode("erp");
        setOpen(true);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [setMode, setOpen]);
}
