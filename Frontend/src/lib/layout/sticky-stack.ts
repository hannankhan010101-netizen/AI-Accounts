/** Publishes measured sticky page header height for stacked sticky layers (toolbar, filters). */
export function setStickyPageHeaderHeight(px: number) {
  if (typeof document === "undefined") return;
  document.documentElement.style.setProperty(
    "--sticky-page-header-height",
    px > 0 ? `${px}px` : "0px",
  );
}

export function resetStickyPageHeaderHeight() {
  setStickyPageHeaderHeight(0);
}
