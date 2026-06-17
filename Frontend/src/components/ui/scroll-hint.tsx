"use client";

export function ScrollHint() {
  return (
    <p className="pointer-events-none absolute bottom-1 right-2 z-10 rounded-md border border-border-subtle bg-surface-elevated px-2 py-0.5 text-[10px] text-fg-muted shadow-sm md:hidden">
      Swipe for more →
    </p>
  );
}
