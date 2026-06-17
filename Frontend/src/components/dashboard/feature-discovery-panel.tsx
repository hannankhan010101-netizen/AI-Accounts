"use client";

import { m } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Compass, Megaphone, Sparkles, X } from "lucide-react";

import { FeatureHintCard } from "@/components/guidance/feature-hint-card";
import { Button } from "@/components/ui/button";
import { useFeatureDiscovery } from "@/features/onboarding/hooks/use-feature-discovery";
import { useCompany } from "@/lib/auth/company-context";
import { staggerContainer } from "@/lib/motion/variants";
import { useReducedMotion } from "@/lib/motion/use-reduced-motion";
import { isReleaseUnread } from "@/lib/tour/release-feed";
import { useTour } from "@/lib/tour/tour-context";
import { cn } from "@/lib/utils";

export function FeatureDiscoveryPanel() {
  const router = useRouter();
  const { companyId } = useCompany();
  const reduced = useReducedMotion();
  const { hints, dismiss, pathname } = useFeatureDiscovery(6);
  const {
    releases,
    dismissRelease,
    startTour,
    progress,
  } = useTour();

  const unreadReleases = releases.filter((r) => isReleaseUnread(r, progress));
  const readReleases = releases.filter((r) => !isReleaseUnread(r, progress));

  const completedCount = Object.values(progress.tours).filter(
    (e) => e.status === "completed",
  ).length;

  const hasContent =
    unreadReleases.length > 0 || readReleases.length > 0 || hints.length > 0;

  return (
    <m.section
      initial={reduced ? false : { opacity: 0, y: 8 }}
      animate={reduced ? undefined : { opacity: 1, y: 0 }}
      transition={{ duration: reduced ? 0.01 : 0.22 }}
      className="surface-elevated space-y-6 rounded-lg p-6"
      data-tour="dashboard-whats-new"
    >
      <div>
        <h2 className="flex items-center gap-2 text-base font-semibold text-fg">
          <Sparkles className="h-4 w-4 text-brand dark:text-brand-400" aria-hidden />
          Learning &amp; updates
        </h2>
        <p className="mt-1 text-sm text-fg-muted">
          Release notes and tips tailored to your role.
          {completedCount > 0 && (
            <span className="ml-1 tabular-nums">
              · {completedCount} tour{completedCount === 1 ? "" : "s"} completed
            </span>
          )}
        </p>
      </div>

      {unreadReleases.length > 0 && (
        <div className="space-y-3">
          <h3 className="flex items-center gap-2 text-sm font-semibold text-fg">
            <Megaphone className="h-4 w-4" aria-hidden />
            What&apos;s new
            <span className="rounded-full bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700 dark:bg-brand-100/12 dark:text-brand-300">
              {unreadReleases.length}
            </span>
          </h3>
          <ul className="space-y-3">
            {unreadReleases.map((release) => (
              <ReleaseCard
                key={release.id}
                release={release}
                isNew
                onDismiss={() => dismissRelease(release.id)}
                onTour={() => {
                  if (release.href) router.push(release.href);
                  if (release.tourId) startTour(release.tourId);
                }}
              />
            ))}
          </ul>
        </div>
      )}

      {hints.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-fg">Recommended for you</h3>
          <m.ul
            className="space-y-3"
            variants={reduced ? undefined : staggerContainer}
            initial={reduced ? false : "hidden"}
            animate={reduced ? undefined : "visible"}
          >
            {hints.map((hint) => (
              <FeatureHintCard
                key={hint.id}
                hint={hint}
                pathname={pathname}
                companyId={companyId}
                onDismiss={dismiss}
                onStartTour={(tourId, href) => {
                  if (href) router.push(href);
                  startTour(tourId);
                }}
              />
            ))}
          </m.ul>
        </div>
      )}

      {readReleases.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs font-medium uppercase tracking-wide text-fg-muted">
            Earlier updates
          </h3>
          <ul className="space-y-2">
            {readReleases.map((release) => (
              <li
                key={release.id}
                className="rounded-md border border-border/60 px-3 py-2 text-sm text-fg-muted"
              >
                {release.title}
                <span className="mx-1.5">·</span>
                {release.publishedAt}
              </li>
            ))}
          </ul>
        </div>
      )}

      {!hasContent && (
        <p className="rounded-md border border-dashed border-border bg-canvas/50 px-4 py-6 text-center text-sm text-fg-muted">
          You&apos;re up to speed. Open the compass button anytime for tours and shortcuts.
        </p>
      )}

      <div className="flex flex-wrap gap-2 border-t border-border pt-4">
        <Link href="/settings/learning">
          <Button type="button" variant="outline" size="sm">
            Learning preferences
          </Button>
        </Link>
      </div>
    </m.section>
  );
}

function ReleaseCard({
  release,
  isNew,
  onDismiss,
  onTour,
}: {
  release: {
    id: string;
    title: string;
    summary: string;
    publishedAt: string;
    tourId?: string | null;
  };
  isNew?: boolean;
  onDismiss: () => void;
  onTour: () => void;
}) {
  return (
    <li
      className={cn(
        "flex flex-col gap-3 rounded-md border p-4 sm:flex-row sm:items-center sm:justify-between",
        isNew
          ? "border-brand/25 bg-brand/5 dark:border-brand-400/20 dark:bg-brand-400/5"
          : "border-border bg-canvas/40",
      )}
    >
      <div className="min-w-0">
        <p className="font-medium text-fg">{release.title}</p>
        <p className="mt-0.5 text-sm text-fg-muted">{release.summary}</p>
        <p className="mt-1 text-xs text-fg-muted">{release.publishedAt}</p>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        {release.tourId && (
          <Button type="button" variant="primary" size="sm" onClick={onTour}>
            <Compass className="mr-1.5 h-3.5 w-3.5" aria-hidden />
            See how it works
          </Button>
        )}
        <button
          type="button"
          onClick={onDismiss}
          className="rounded-md p-1.5 text-fg-muted hover:bg-surface focus-ring"
          aria-label={`Dismiss: ${release.title}`}
        >
          <X className="h-4 w-4" aria-hidden />
        </button>
      </div>
    </li>
  );
}
