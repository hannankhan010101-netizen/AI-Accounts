import { cn } from "@/lib/utils";

interface BrandMarkIconProps {
  size?: number;
  className?: string;
}

/**
 * AI-Accounts symbol — ledger sheet, growth bars, and AI sparkle.
 * Sized for sidebar (36px) and favicon; stays legible at small sizes.
 */
export function BrandMarkIcon({ size = 32, className }: BrandMarkIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="AI-Accounts"
      className={cn("shrink-0", className)}
    >
      <rect x="1" y="1" width="30" height="30" rx="8" fill="url(#aa-mark-bg)" />
      <rect
        x="1"
        y="1"
        width="30"
        height="30"
        rx="8"
        stroke="currentColor"
        strokeOpacity="0.22"
        strokeWidth="1"
      />
      <rect
        x="7"
        y="6"
        width="13"
        height="18"
        rx="2"
        fill="currentColor"
        fillOpacity="0.12"
        stroke="currentColor"
        strokeWidth="1.75"
      />
      <path
        d="M10 10.5h7M10 13.5h5"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
        opacity="0.55"
      />
      <rect x="10" y="17.5" width="2.4" height="4" rx="0.6" fill="currentColor" />
      <rect x="13.2" y="15.5" width="2.4" height="6" rx="0.6" fill="currentColor" />
      <rect x="16.4" y="13.5" width="2.4" height="8" rx="0.6" fill="currentColor" />
      <path
        d="M21.5 8.2l.75 1.5 1.5.75-1.5.75-.75 1.5-.75-1.5-1.5-.75 1.5-.75z"
        fill="currentColor"
      />
      <circle cx="23.8" cy="12.2" r="1.35" fill="currentColor" />
      <path
        d="M22.2 11c1.2-.45 2.1.35 2.55 1.55"
        stroke="currentColor"
        strokeWidth="1.35"
        strokeLinecap="round"
      />
      <defs>
        <linearGradient id="aa-mark-bg" x1="4" y1="3" x2="28" y2="29" gradientUnits="userSpaceOnUse">
          <stop stopColor="currentColor" stopOpacity="0.14" />
          <stop offset="1" stopColor="currentColor" stopOpacity="0.06" />
        </linearGradient>
      </defs>
    </svg>
  );
}
