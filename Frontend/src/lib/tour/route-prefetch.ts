/**
 * Prefetch Next.js routes referenced by tour navigate steps.
 */
export function prefetchTourRoute(href: string): void {
  if (typeof window === "undefined" || !href.startsWith("/")) return;
  try {
    const link = document.createElement("link");
    link.rel = "prefetch";
    link.href = href;
    document.head.appendChild(link);
  } catch {
    /* ignore */
  }
}

export function prefetchTourRoutes(hrefs: string[]): void {
  for (const href of hrefs) prefetchTourRoute(href);
}
