"use client";

import { useReducedMotion as useFramerReducedMotion } from "framer-motion";
import { useEffect, useState } from "react";

/** SSR-safe reduced-motion detection (Framer + media query). */
export function useReducedMotion(): boolean {
  const framer = useFramerReducedMotion();
  const [mq, setMq] = useState(false);

  useEffect(() => {
    const q = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setMq(q.matches);
    update();
    q.addEventListener("change", update);
    return () => q.removeEventListener("change", update);
  }, []);

  return Boolean(framer ?? mq);
}
