import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

export function CommandCenterSkeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn("space-y-4", className)}
      aria-busy="true"
      aria-label="Loading command center"
    >
      <div className="space-y-2">
        <Skeleton variant="text" className="h-7 w-48" />
        <Skeleton variant="text" className="h-4 w-64" />
      </div>

      <Skeleton variant="block" className="h-12 w-full rounded-xl" />

      <div className="flex snap-x gap-3 overflow-hidden pb-1">
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton key={i} variant="block" className="h-24 w-36 shrink-0 rounded-xl" />
        ))}
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <Skeleton variant="chart" />
        <Skeleton variant="chart" />
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} variant="block" className="h-32 rounded-xl" />
        ))}
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} variant="block" className="h-28 rounded-xl" />
        ))}
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} variant="block" className="h-36 rounded-xl" />
        ))}
      </div>

      <Skeleton variant="block" className="h-40 w-full rounded-xl" />
    </div>
  );
}
