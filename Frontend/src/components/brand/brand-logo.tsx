import Link from "next/link";

import { BRAND } from "@/lib/brand";
import { BrandMark } from "@/components/brand/brand-mark";
import { cn } from "@/lib/utils";

type BrandLogoVariant = "sidebar" | "sidebarCompact" | "auth";

interface BrandLogoProps {
  variant?: BrandLogoVariant;
  href?: string;
  className?: string;
  priority?: boolean;
}

function BrandWordmark({ layout }: { layout: "inline" | "auth" }) {
  if (layout === "auth") {
    return (
      <span className="text-center">
        <span className="block text-lg font-semibold tracking-tight text-fg">{BRAND.name}</span>
        <span className="mt-1 block text-xs font-medium text-fg-muted">{BRAND.tagline}</span>
      </span>
    );
  }
  return (
    <span className="min-w-0 leading-tight">
      <span className="block truncate text-sm font-semibold tracking-tight text-fg">
        {BRAND.name}
      </span>
      <span className="block truncate text-[10px] font-medium text-fg-muted">
        {BRAND.tagline}
      </span>
    </span>
  );
}

function MarkFrame({
  children,
  size = "md",
}: {
  children: React.ReactNode;
  size?: "md" | "lg";
}) {
  return (
    <span
      className={cn(
        "flex shrink-0 items-center justify-center rounded-lg",
        "bg-brand-600/8 ring-1 ring-brand-600/15 dark:bg-brand-100/10 dark:ring-brand-100/20",
        size === "lg" ? "h-12 w-12" : "h-9 w-9",
      )}
    >
      {children}
    </span>
  );
}

/** Sidebar / auth branding — symbol mark + optional wordmark (no full logo plate). */
export function BrandLogo({
  variant = "sidebar",
  href = "/dashboard",
  className,
  priority = false,
}: BrandLogoProps) {
  const isCompact = variant === "sidebarCompact";
  const isAuth = variant === "auth";

  const content = (
    <span
      className={cn(
        "inline-flex min-w-0 items-center",
        isAuth ? "flex-col gap-3 text-center" : "gap-2.5",
        isCompact && "justify-center",
        className,
      )}
    >
      <MarkFrame size={isAuth ? "lg" : "md"}>
        <BrandMark
          size={isAuth ? 28 : isCompact ? 22 : 24}
          priority={priority}
          className={isAuth ? "h-7 w-7" : isCompact ? "h-[22px] w-[22px]" : "h-6 w-6"}
        />
      </MarkFrame>
      {!isCompact && <BrandWordmark layout={isAuth ? "auth" : "inline"} />}
    </span>
  );

  if (!href) {
    return content;
  }

  return (
    <Link
      href={href}
      className={cn(
        "rounded-md motion-safe-transition hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-brand/40",
        isCompact ? "inline-flex" : "inline-flex min-w-0 flex-1",
      )}
      aria-label={`${BRAND.name} home`}
    >
      {content}
    </Link>
  );
}
