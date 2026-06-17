"use client";

import Link from "next/link";
import { Construction } from "lucide-react";

import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { MotionFade } from "@/components/ui/motion-fade";

type ComingSoonContentProps = {
  slug: string[];
  title: string;
};

export function ComingSoonContent({ slug, title }: ComingSoonContentProps) {
  const path = `/${slug.join("/")}`;

  return (
    <MotionFade>
      <div className="max-w-2xl space-y-4">
        <h1 className="text-page-title font-semibold text-fg">{title}</h1>
        <div className="surface-elevated rounded-xl bg-surface dark:border-0">
          <EmptyState
            icon={Construction}
            title="Not yet implemented"
            description={`${path} is reserved for an upcoming milestone. The sidebar route stays in place so navigation remains consistent during the build-out.`}
            action={
              <div className="flex flex-wrap justify-center gap-2">
                <Button asChild variant="outline" size="sm">
                  <Link href="/">Dashboard</Link>
                </Button>
                <Button asChild variant="outline" size="sm">
                  <Link href="/admin">Admin settings</Link>
                </Button>
              </div>
            }
          />
        </div>
      </div>
    </MotionFade>
  );
}
