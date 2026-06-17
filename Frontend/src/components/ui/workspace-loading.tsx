import { cn } from "@/lib/utils";

import { Skeleton } from "@/components/ui/skeleton";

interface WorkspaceLoadingProps {
  title?: string;
  className?: string;
  variant?: "default" | "dashboard";
}

export function WorkspaceLoading({ title, className, variant = "default" }: WorkspaceLoadingProps) {
  if (variant === "dashboard") {
    return (
      <div className={cn("space-y-6", className)} aria-busy="true" aria-label={title ?? "Loading dashboard"}>
        <div className="flex flex-wrap gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} variant="block" className="h-28 flex-1 min-w-[12rem] rounded-xl" />
          ))}
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <Skeleton variant="chart" />
          <Skeleton variant="chart" />
        </div>
      </div>
    );
  }

  return (
    <div className={cn("space-y-6", className)} aria-busy="true" aria-label={title ?? "Loading"}>
      <div className="space-y-2">
        <Skeleton variant="text" className="h-7 w-56" />
        <Skeleton variant="text" className="h-4 w-72" />
      </div>
      <div className="flex flex-wrap gap-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-9 w-24" />
        ))}
      </div>
      <div className="rounded-xl border border-border bg-surface p-4">
        <Skeleton variant="text" className="mb-3 max-w-md" />
        {Array.from({ length: 10 }).map((_, i) => (
          <Skeleton key={i} className="mb-2 h-8" style={{ width: `${55 + (i % 4) * 10}%` }} />
        ))}
      </div>
    </div>
  );
}
