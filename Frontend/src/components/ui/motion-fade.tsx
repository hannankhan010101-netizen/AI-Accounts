"use client";

import { m } from "framer-motion";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { appPresets } from "@/lib/motion/app-presets";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { cn } from "@/lib/utils";

/** Route content enter — fade + subtle slide; does not block navigation. */
export function MotionFade({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const pathname = usePathname();
  const reduced = useReducedMotion();
  const [key, setKey] = useState(pathname);
  const preset = appPresets.pageEnter;

  useEffect(() => {
    setKey(pathname);
  }, [pathname]);

  return (
    <m.div
      key={key}
      initial={reduced ? false : "hidden"}
      animate={reduced ? undefined : "visible"}
      variants={preset.variants}
      transition={preset.transition}
      className={cn(className)}
    >
      {children}
    </m.div>
  );
}
