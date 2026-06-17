/** Tour accessibility helpers — WCAG 2.2 AA patterns. */

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

export function getFocusableElements(root: HTMLElement): HTMLElement[] {
  return Array.from(root.querySelectorAll<HTMLElement>(FOCUSABLE)).filter(
    (el) => !el.hasAttribute("disabled") && el.offsetParent !== null,
  );
}

/** Trap Tab within container; returns cleanup. */
export function trapFocus(container: HTMLElement): () => void {
  function onKeyDown(e: KeyboardEvent) {
    if (e.key !== "Tab") return;
    const nodes = getFocusableElements(container);
    if (nodes.length === 0) return;
    const first = nodes[0];
    const last = nodes[nodes.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
  container.addEventListener("keydown", onKeyDown);
  const nodes = getFocusableElements(container);
  nodes[0]?.focus();
  return () => container.removeEventListener("keydown", onKeyDown);
}

export function announceToScreenReader(message: string): void {
  const el = document.createElement("div");
  el.setAttribute("role", "status");
  el.setAttribute("aria-live", "polite");
  el.setAttribute("aria-atomic", "true");
  el.className = "sr-only";
  el.textContent = message;
  document.body.appendChild(el);
  window.setTimeout(() => el.remove(), 1200);
}
