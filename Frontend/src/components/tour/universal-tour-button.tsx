"use client";

import { AnimatePresence } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { GripVertical } from "lucide-react";

import { HelpFab } from "@/components/onboarding/help-fab";
import { TourMenu } from "@/components/tour/tour-menu";
import { useTour } from "@/lib/tour/tour-context";
import { useTourUIStore } from "@/stores/onboarding/tour-ui-store";
import { cn } from "@/lib/utils";

export function UniversalTourButton() {
  const {
    menuOpen,
    setMenuOpen,
    unreadReleaseCount,
    machine,
    running,
    currentStep,
    dismissTour,
  } = useTour();
  const fabDraggable = useTourUIStore((s) => s.fabDraggable);
  const setFabDraggable = useTourUIStore((s) => s.setFabDraggable);
  const fabAnchor = useTourUIStore((s) => s.fabAnchor);
  const setFabAnchor = useTourUIStore((s) => s.setFabAnchor);
  const resetFabPosition = useTourUIStore((s) => s.resetFabPosition);

  const onHelpTargetStep = currentStep?.id === "help";
  const wrapRef = useRef<HTMLDivElement>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const isActive =
    machine === "running" || machine === "waiting_target" || machine === "paused";

  useEffect(() => {
    if (fabAnchor) setDragOffset(fabAnchor);
  }, [fabAnchor]);

  useEffect(() => {
    if (!menuOpen) return;
    function onPointer(e: MouseEvent) {
      if (wrapRef.current?.contains(e.target as Node)) return;
      setMenuOpen(false);
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setMenuOpen(false);
    }
    window.addEventListener("mousedown", onPointer);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("mousedown", onPointer);
      window.removeEventListener("keydown", onKey);
    };
  }, [menuOpen, setMenuOpen]);

  return (
    <div
      ref={wrapRef}
      className={cn(
        "fixed z-tour flex flex-col items-end",
        !fabDraggable && "bottom-5 right-5 md:bottom-7 md:right-7",
      )}
      style={
        fabDraggable
          ? { bottom: 24, right: 24, transform: `translate(${dragOffset.x}px, ${dragOffset.y}px)` }
          : undefined
      }
      data-tour="tour-button"
    >
      <AnimatePresence>
        {menuOpen && !isActive && (
          <TourMenu onClose={() => setMenuOpen(false)} />
        )}
      </AnimatePresence>

      <div className="flex items-center gap-1.5">
        <button
          type="button"
          onClick={() => setFabDraggable(!fabDraggable)}
          className={cn(
            "hidden rounded-lg border border-border/70 bg-surface/80 p-1.5 text-fg-muted shadow-sm backdrop-blur-sm hover:bg-canvas focus-ring md:flex",
            fabDraggable && "text-brand-600 dark:text-brand-100",
          )}
          aria-label={fabDraggable ? "Lock position" : "Reposition learning button"}
          aria-pressed={fabDraggable}
        >
          <GripVertical className="h-3.5 w-3.5" aria-hidden />
        </button>

        <HelpFab
          active={isActive}
          expanded={menuOpen}
          stepBadge={isActive && running ? running.stepIndex + 1 : undefined}
          unreadCount={!isActive ? unreadReleaseCount : undefined}
          onClick={() => {
            if (isActive && !onHelpTargetStep) {
              dismissTour();
              return;
            }
            if (!isActive) setMenuOpen(!menuOpen);
          }}
        />
      </div>

      {fabDraggable && (
        <button
          type="button"
          className="mt-1 text-[10px] text-fg-muted underline-offset-2 hover:underline"
          onClick={() => {
            resetFabPosition();
            setDragOffset({ x: 0, y: 0 });
          }}
        >
          Reset position
        </button>
      )}
    </div>
  );
}
