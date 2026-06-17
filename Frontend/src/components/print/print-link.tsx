import Link from "next/link";

interface PrintLinkProps {
  href: string;
  className?: string;
  label?: string;
}

/** Opens the dedicated print layout in a new tab. */
export function PrintLink({ href, className, label = "Print" }: PrintLinkProps) {
  return (
    <Link
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={
        className ??
        "inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-brand hover:bg-canvas"
      }
    >
      {label}
    </Link>
  );
}
