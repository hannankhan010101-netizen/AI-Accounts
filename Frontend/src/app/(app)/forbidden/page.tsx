"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";

export default function ForbiddenPage() {
  const searchParams = useSearchParams();
  const from = searchParams.get("from");

  return (
    <div>
      <PageHeader
        title="Access denied"
        breadcrumb="Forbidden"
        description={
          from
            ? `You cannot open ${from}. The module may be disabled or you lack permission.`
            : "You do not have permission to view this page."
        }
      />
      <Button asChild>
        <Link href="/">Return home</Link>
      </Button>
    </div>
  );
}
