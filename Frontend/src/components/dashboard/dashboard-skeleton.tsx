import { CommandCenterSkeleton } from "@/components/dashboard/command-center/command-center-skeleton";
import { cn } from "@/lib/utils";

export function DashboardSkeleton({ className }: { className?: string }) {
  return <CommandCenterSkeleton className={cn("w-full", className)} />;
}
