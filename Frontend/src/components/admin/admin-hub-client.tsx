"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import type { LucideIcon } from "lucide-react";
import { Search } from "lucide-react";

import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { MotionFade } from "@/components/ui/motion-fade";
import { cn } from "@/lib/utils";

export type AdminHubSection = {
  title: string;
  description: string;
  icon: LucideIcon;
  links: { label: string; href: string }[];
};

type AdminHubClientProps = {
  sections: AdminHubSection[];
};

export function AdminHubClient({ sections }: AdminHubClientProps) {
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return sections;
    return sections
      .map((section) => ({
        ...section,
        links: section.links.filter(
          (link) =>
            link.label.toLowerCase().includes(q) ||
            link.href.toLowerCase().includes(q) ||
            section.title.toLowerCase().includes(q),
        ),
      }))
      .filter((section) => section.links.length > 0);
  }, [sections, search]);

  return (
    <MotionFade>
      <div className="mb-4 max-w-md">
        <div className="relative">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-fg-muted"
            aria-hidden
          />
          <Input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search admin settings…"
            className="pl-9"
            aria-label="Search admin settings"
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <p className="text-sm text-fg-muted">No settings match &ldquo;{search}&rdquo;.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((section) => {
            const Icon = section.icon;
            return (
              <Card
                key={section.title}
                variant="glass"
                className="p-4 motion-safe-transition hover:elevation-md dark:border-0"
              >
                <div className="mb-3 flex items-start gap-3">
                  <div className="rounded-md p-2 surface-brand-soft">
                    <Icon className="h-5 w-5 text-brand" aria-hidden />
                  </div>
                  <div>
                    <h2 className="text-label font-semibold text-fg">{section.title}</h2>
                    <p className="mt-0.5 text-caption text-fg-muted">{section.description}</p>
                  </div>
                </div>
                <ul className="space-y-0.5">
                  {section.links.map((link) => (
                    <li key={link.href + link.label}>
                      <Link
                        href={link.href}
                        className={cn(
                          "block rounded-md px-2 py-1.5 text-sm text-fg",
                          "hover:bg-canvas motion-safe-transition",
                        )}
                      >
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </Card>
            );
          })}
        </div>
      )}
    </MotionFade>
  );
}
