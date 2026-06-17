import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { cn } from "@/lib/utils";

/** Client + route loading skeleton for document / voucher detail pages. */
export function DetailPageLoading({ className }: { className?: string }) {
  return (
    <WorkspaceLoading
      className={cn(className)}
      title="Loading document"
    />
  );
}
