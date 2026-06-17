/**
 * Catch-all placeholder for routes that don't have a real page yet.
 * Real pages at /sales/invoices, /settings/smart, etc. override this segment.
 */

import { ComingSoonContent } from "@/components/app/coming-soon-content";

interface ComingSoonProps {
  params: { slug: string[] };
}

function titleize(slug: string[]): string {
  return slug
    .map((s) =>
      s
        .replace(/-/g, " ")
        .replace(/\b\w/g, (c) => c.toUpperCase()),
    )
    .join(" / ");
}

export default function ComingSoon({ params }: ComingSoonProps) {
  return <ComingSoonContent slug={params.slug} title={titleize(params.slug)} />;
}
