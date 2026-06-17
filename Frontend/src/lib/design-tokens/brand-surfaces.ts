import { cn } from "@/lib/utils";

/**
 * Solid brand fill + guaranteed readable label via `--fg-on-brand` (not palette step 900).
 */
export const brandSolidClasses = cn(
  "bg-brand-solid text-on-brand shadow-sm",
  "hover:bg-brand-700 active:bg-brand-800",
  "dark:hover:bg-brand-400 dark:active:bg-brand-300",
  "[&_svg]:text-current [&_*]:text-inherit",
);

export const brandSolidBgClasses = "bg-brand-solid";

export const brandSolidTextClasses = "text-on-brand";

export const brandSolidPillClasses = cn(
  "absolute inset-0 rounded bg-brand-solid shadow-sm",
);

export const brandSolidLabelClasses = cn("relative z-[1]", brandSolidTextClasses);

/** Light brand wash — selected filters, badges, command palette row. */
export const brandSoftClasses = cn(
  "bg-brand-50 text-brand-700",
  "dark:bg-brand-100/12 dark:text-brand-300",
);

/** Accent text links and nav labels on dark canvas. */
export const brandLinkClasses = cn(
  "text-brand-700 dark:text-brand-300",
  "hover:text-brand-800 dark:hover:text-brand-200",
);

/** Warning / draft banners — token-based, readable in both themes. */
export const warningSurfaceClasses = cn(
  "border border-status-warning/35 bg-status-warning/10 text-fg",
  "dark:border-status-warning/40 dark:bg-status-warning/15",
);

/** Keyboard / search focus ring on list rows. */
export const brandFocusedRowClasses = cn(
  "bg-brand-50/70 ring-1 ring-inset ring-brand-200/60",
  "dark:bg-brand-400/10 dark:ring-brand-400/25",
);

/** Highlight a row from deep-link or selection. */
export const brandRowHighlightClasses = cn(
  brandSoftClasses,
  "ring-1 ring-brand/30 dark:ring-brand-400/25",
);
