"use client";

import { Filter } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sheet } from "@/components/ui/sheet";
import { useIsMobile } from "@/lib/responsive";
import { cn } from "@/lib/utils";

interface ListToolbarProps {
  search?: string;
  onSearchChange?: (value: string) => void;
  searchPlaceholder?: string;
  searchDisabled?: boolean;
  className?: string;
  children?: React.ReactNode;
  filterCount?: number;
}

export function ListToolbar({
  search,
  onSearchChange,
  searchPlaceholder = "Search…",
  searchDisabled = false,
  className,
  children,
  filterCount,
}: ListToolbarProps) {
  const isMobile = useIsMobile();
  const [filtersOpen, setFiltersOpen] = useState(false);
  const hasFilters = Boolean(children);
  const count = filterCount ?? (hasFilters ? 1 : 0);

  return (
    <div
      className={cn(
        "mb-3 flex flex-col gap-2 rounded-lg border border-border/60 bg-surface px-3 py-2 sm:flex-row sm:flex-wrap sm:items-center",
        className,
      )}
    >
      {onSearchChange !== undefined && (
        <div className="min-w-0 flex-1 sm:max-w-xs">
          <Input
            type="search"
            value={search ?? ""}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder={searchPlaceholder}
            aria-label="Search list"
            disabled={searchDisabled}
          />
        </div>
      )}
      {hasFilters && isMobile ? (
        <>
          <Button
            type="button"
            variant="outline"
            size="md"
            className="w-full sm:w-auto"
            onClick={() => setFiltersOpen(true)}
          >
            <Filter className="mr-2 h-4 w-4" aria-hidden />
            Filters{count > 0 ? ` (${count})` : ""}
          </Button>
          <Sheet open={filtersOpen} onClose={() => setFiltersOpen(false)} title="Filters" position="bottom">
            <div className="flex flex-col gap-3">{children}</div>
          </Sheet>
        </>
      ) : (
        children && <div className="flex flex-wrap items-center gap-3">{children}</div>
      )}
    </div>
  );
}
