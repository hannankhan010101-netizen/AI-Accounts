"use client";

import { createPortal } from "react-dom";
import { useEffect, useState } from "react";

/** Renders children into `document.body` after mount (SSR-safe). */
export function BodyPortal({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return null;
  return createPortal(children, document.body);
}
