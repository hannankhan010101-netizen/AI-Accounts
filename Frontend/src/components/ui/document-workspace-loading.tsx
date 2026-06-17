import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { cn } from "@/lib/utils";

/** Loading skeleton for document list/detail/new routes (sales, purchases, bank, …). */
export function DocumentWorkspaceLoading({ className }: { className?: string }) {
  return (
    <div className={cn("space-y-6", className)}>
      <WorkspaceLoading />
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-3 rounded-lg border border-border bg-surface p-4 lg:col-span-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-9 rounded bg-canvas" />
          ))}
        </div>
        <div className="space-y-3 rounded-lg border border-border bg-surface p-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-6 rounded bg-canvas" />
          ))}
        </div>
      </div>
    </div>
  );
}
