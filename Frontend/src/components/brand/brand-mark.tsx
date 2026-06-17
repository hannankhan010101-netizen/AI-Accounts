import Image from "next/image";

import { BRAND } from "@/lib/brand";
import { cn } from "@/lib/utils";

interface BrandMarkProps {
  size?: number;
  className?: string;
  priority?: boolean;
}

/** Brand symbol only (no wordmark plate) — `/public/brand/symbol.png`. */
export function BrandMark({ size = 32, className, priority = false }: BrandMarkProps) {
  return (
    <Image
      src={BRAND.symbol}
      alt=""
      width={size}
      height={size}
      priority={priority}
      aria-hidden
      className={cn(
        "object-contain object-center",
        "dark:brightness-0 dark:invert",
        className,
      )}
    />
  );
}
