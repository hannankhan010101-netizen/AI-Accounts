/** Lets tour UI open shell features without prop-drilling through TopBar / Sidebar. */



import { tourNavTargetId } from "@/lib/tour/sidebar-navigation";



export type TourShellActions = {

  openCommandPalette?: () => void;

  closeCommandPalette?: () => void;

  openShortcutsHelp?: () => void;

  openMobileNav?: () => void;

  closeMobileNav?: () => void;

  closeCompanyMenu?: () => void;

  /** Expand pinned-compact sidebar for demos. */

  ensureSidebarExpanded?: () => void;

  expandNavGroup?: (groupLabel: string) => void;

  /** Programmatically activate a sidebar link; returns false if not found. */

  clickNavLink?: (href: string) => boolean;

  navigateToHref?: (href: string) => void;

};



let registered: TourShellActions = {};



export function registerTourShellActions(actions: TourShellActions): void {

  registered = { ...registered, ...actions };

}



export function unregisterTourShellActions(): void {

  registered = {};

}



export function getTourShellActions(): TourShellActions {

  return registered;

}



function isNavLinkVisible(el: HTMLElement): boolean {

  const rect = el.getBoundingClientRect();

  if (rect.width < 2 || rect.height < 2) return false;

  const style = window.getComputedStyle(el);

  return style.display !== "none" && style.visibility !== "hidden" && style.opacity !== "0";

}



export function clickNavLinkInDom(href: string): boolean {

  const id = tourNavTargetId(href);

  const el = document.querySelector<HTMLElement>(`[data-tour="${id}"]`);

  if (!el || !isNavLinkVisible(el)) return false;

  el.scrollIntoView({ block: "nearest", inline: "nearest", behavior: "auto" });

  el.click();

  return true;

}


