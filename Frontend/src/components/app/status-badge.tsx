import { Badge } from "@/components/ui/badge";

interface StatusBadgeProps {
  status: string;
}

const TONE: Record<string, "default" | "success" | "danger" | "brand"> = {
  draft: "default",
  in_progress: "default",
  approved: "success",
  accepted: "success",
  rejected: "danger",
  invoiced: "brand",
  billed: "brand",
  converted: "brand",
  posted: "success",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const variant = TONE[status] ?? "default";
  return (
    <Badge variant={variant}>
      {status.replace(/_/g, " ")}
    </Badge>
  );
}
