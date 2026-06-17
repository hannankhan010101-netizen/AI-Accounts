"use client";



import { autoUpdate, flip, offset, shift, useFloating } from "@floating-ui/react";

import { AnimatePresence, m } from "framer-motion";

import { MoreHorizontal } from "lucide-react";

import { useEffect, useId, useRef, useState } from "react";



import { appPresets } from "@/lib/motion/app-presets";

import { useReducedMotion } from "@/lib/motion/use-reduced-motion";

import { Button } from "@/components/ui/button";

import { BodyPortal } from "@/lib/ui/portal";

import { cn } from "@/lib/utils";



export interface ActionMenuItem {

  id: string;

  label: string;

  onClick: () => void;

  variant?: "default" | "danger";

  disabled?: boolean;

}



interface ActionMenuProps {

  items: ActionMenuItem[];

  /** Accessible label for the trigger */

  triggerLabel?: string;

  align?: "left" | "right";

  className?: string;

}



export function ActionMenu({

  items,

  triggerLabel = "Actions",

  align = "right",

  className,

}: ActionMenuProps) {

  const [open, setOpen] = useState(false);

  const menuId = useId();

  const rootRef = useRef<HTMLDivElement>(null);

  const reduced = useReducedMotion();

  const preset = appPresets.modalEnter;



  const { refs, floatingStyles } = useFloating({

    open,

    onOpenChange: setOpen,

    placement: align === "right" ? "bottom-end" : "bottom-start",

    middleware: [offset(4), flip({ padding: 8 }), shift({ padding: 8 })],

    whileElementsMounted: autoUpdate,

  });



  useEffect(() => {

    if (!open) return;

    function onKey(e: KeyboardEvent) {

      if (e.key === "Escape") setOpen(false);

    }

    window.addEventListener("keydown", onKey);

    return () => window.removeEventListener("keydown", onKey);

  }, [open]);



  if (items.length === 0) return null;



  return (

    <div ref={rootRef} className={cn("relative inline-block", className)}>

      <Button

        ref={refs.setReference}

        type="button"

        variant="ghost"

        size="icon"

        className="touch-target"

        aria-label={triggerLabel}

        aria-haspopup="menu"

        aria-expanded={open}

        aria-controls={menuId}

        onClick={() => setOpen((o) => !o)}

      >

        <MoreHorizontal className="h-5 w-5" aria-hidden />

      </Button>

      <BodyPortal>

        <AnimatePresence>

          {open && (

            <>

              <button

                type="button"

                className="fixed inset-0 z-[calc(var(--z-modal)-1)] cursor-default bg-transparent"

                aria-label="Close menu"

                onClick={() => setOpen(false)}

              />

              <m.ul

                ref={refs.setFloating}

                id={menuId}

                role="menu"

                style={floatingStyles}

                initial={reduced ? false : "hidden"}

                animate={reduced ? undefined : "visible"}

                exit={reduced ? undefined : "exit"}

                variants={preset.variants}

                transition={preset.transition}

                className="z-modal min-w-[10rem] overflow-hidden rounded-xl border border-border-subtle bg-surface-elevated py-1 shadow-lg"

              >

                {items.map((item) => (

                  <li key={item.id} role="none">

                    <button

                      type="button"

                      role="menuitem"

                      disabled={item.disabled}

                      className={cn(

                        "block w-full px-3 py-2.5 text-left text-sm motion-safe-transition hover:bg-surface-muted focus-ring disabled:opacity-50",

                        item.variant === "danger" && "text-status-danger",

                      )}

                      onClick={() => {

                        setOpen(false);

                        item.onClick();

                      }}

                    >

                      {item.label}

                    </button>

                  </li>

                ))}

              </m.ul>

            </>

          )}

        </AnimatePresence>

      </BodyPortal>

    </div>

  );

}



/** Collapses children into a menu below `sm`; shows inline from `sm` up. */

export function ResponsiveActionCluster({

  children,

  menuLabel = "More actions",

  className,

}: {

  children: React.ReactNode;

  menuLabel?: string;

  className?: string;

}) {

  const [open, setOpen] = useState(false);

  const menuId = useId();

  const rootRef = useRef<HTMLDivElement>(null);



  const { refs, floatingStyles } = useFloating({

    open,

    onOpenChange: setOpen,

    placement: "bottom-end",

    middleware: [offset(4), flip({ padding: 8 }), shift({ padding: 8 })],

    whileElementsMounted: autoUpdate,

  });



  useEffect(() => {

    if (!open) return;

    function onKey(e: KeyboardEvent) {

      if (e.key === "Escape") setOpen(false);

    }

    window.addEventListener("keydown", onKey);

    return () => window.removeEventListener("keydown", onKey);

  }, [open]);



  return (

    <div ref={rootRef} className={cn("relative", className)}>

      <div className="hidden flex-wrap gap-2 sm:flex">{children}</div>

      <div className="sm:hidden">

        <Button

          ref={refs.setReference}

          type="button"

          variant="outline"

          size="md"

          className="w-full touch-target"

          aria-expanded={open}

          aria-controls={menuId}

          onClick={() => setOpen((o) => !o)}

        >

          {menuLabel}

        </Button>

        <BodyPortal>

          {open && (

            <>

              <button

                type="button"

                className="fixed inset-0 z-[calc(var(--z-modal)-1)] cursor-default bg-transparent"

                aria-label="Close menu"

                onClick={() => setOpen(false)}

              />

              <div

                ref={refs.setFloating}

                id={menuId}

                style={floatingStyles}

                className="z-modal flex w-full min-w-[12rem] max-w-[min(100vw-2rem,20rem)] flex-col gap-2 rounded-md border border-border bg-surface-elevated p-2 shadow-lg"

              >

                <div className="flex flex-col gap-2 [&_a]:w-full [&_button]:w-full">{children}</div>

              </div>

            </>

          )}

        </BodyPortal>

      </div>

    </div>

  );

}

