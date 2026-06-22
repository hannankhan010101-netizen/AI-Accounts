"use client";

import { useEffect, useState } from "react";

/** True only after the client has mounted — use to gate browser-only UI. */
export function useHydrated(): boolean {
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setHydrated(true);
  }, []);

  return hydrated;
}
