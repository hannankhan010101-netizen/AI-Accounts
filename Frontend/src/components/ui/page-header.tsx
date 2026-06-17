"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";

import {
  resetStickyPageHeaderHeight,
  setStickyPageHeaderHeight,
} from "@/lib/layout/sticky-stack";
import { cn } from "@/lib/utils";

interface PageHeaderProps {
  title: string;
  breadcrumb?: string;
  description?: string;
  actions?: React.ReactNode;
  sticky?: boolean;
  /** `data-tour` on the page header block (module tours). */
  tourRoot?: string;
  /** `data-tour` on the actions slot (e.g. primary create button). */
  tourActions?: string;
}

export function PageHeader({
  title,
  breadcrumb,
  description,
  actions,
  sticky = false,
  tourRoot,
  tourActions,
}: PageHeaderProps) {
  const pathname = usePathname();
  const titleRef = useRef<HTMLHeadingElement>(null);
  const stickyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    titleRef.current?.focus({ preventScroll: true });
  }, [pathname]);

  useEffect(() => {
    if (!sticky) {
      resetStickyPageHeaderHeight();
      return;
    }

    const node = stickyRef.current;
    if (!node) return;

    const publish = () => setStickyPageHeaderHeight(node.offsetHeight);

    publish();
    const observer = new ResizeObserver(publish);
    observer.observe(node);

    return () => {
      observer.disconnect();
      resetStickyPageHeaderHeight();
    };
  }, [sticky, pathname]);

  return (
    <div
      ref={sticky ? stickyRef : undefined}
      className={cn(
        "mb-4 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between sm:gap-3",
        sticky &&
          "sticky-page-header -mx-[var(--app-gutter)] mb-3 border-b border-border-subtle bg-surface/95 px-[var(--app-gutter)] py-3 shadow-sm backdrop-blur-md",
      )}
      {...(tourRoot ? { "data-tour": tourRoot } : {})}
    >
      <div className="min-w-0">
        {breadcrumb && <div className="text-xs text-fg-muted">{breadcrumb}</div>}
        <h1
          id="page-title"
          ref={titleRef}
          tabIndex={-1}
          className="text-page-title font-semibold text-fg outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)] focus-visible:ring-offset-2"
        >
          {title}
        </h1>
        {description && <p className="mt-1 text-sm text-fg-muted">{description}</p>}
      </div>
      {actions && (
        <div
          className="flex w-full shrink-0 flex-wrap gap-2 sm:w-auto sm:justify-end [&>a]:max-xs:w-full [&>button]:max-xs:w-full"
          {...(tourActions ? { "data-tour": tourActions } : {})}
        >
          {actions}
        </div>
      )}
    </div>
  );
}
