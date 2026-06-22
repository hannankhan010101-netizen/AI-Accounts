import { BrandMarkIcon } from "@/components/brand/brand-mark-icon";
import { cn } from "@/lib/utils";

interface BrandMarkProps {
  size?: number;
  className?: string;
  priority?: boolean;
}

/** Brand symbol — ledger + AI mark for shell UI. */
export function BrandMark({ size = 32, className }: BrandMarkProps) {
  return (
    <BrandMarkIcon
      size={size}
      className={cn("text-brand-600 dark:text-brand-300", className)}
    />
  );
}
