"use client";

import { useEffect } from "react";

/** Warn before leaving when a document form has unsaved local changes. */
export function useDocumentFormGuard(active: boolean) {
  useEffect(() => {
    if (!active) return;
    function onBeforeUnload(e: BeforeUnloadEvent) {
      e.preventDefault();
    }
    window.addEventListener("beforeunload", onBeforeUnload);
    return () => window.removeEventListener("beforeunload", onBeforeUnload);
  }, [active]);
}
