"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { LayoutDashboard } from "lucide-react";
import type { Layout, LayoutItem } from "react-grid-layout";

import { CommandCenterWidget } from "@/components/dashboard/command-center/widget-registry";
import type { CommandCenterPayload, GridLayoutItem } from "@/components/dashboard/command-center/types/command-center";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { cn } from "@/lib/utils";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";

const ResponsiveGridLayout = dynamic(
  () => import("react-grid-layout/legacy").then((m) => m.ResponsiveReactGridLayout),
  { ssr: false },
);

const BREAKPOINTS = { lg: 1200, md: 996, sm: 768, xs: 480 };
const COLS = { lg: 12, md: 12, sm: 6, xs: 1 };

function toLayoutItems(items: GridLayoutItem[], editMode: boolean): Layout {
  return items.map((item) => ({
    i: item.i,
    x: item.x,
    y: item.y,
    w: item.w,
    h: item.h,
    minW: item.minW ?? 2,
    minH: item.minH ?? 2,
    static: !editMode,
  }));
}

function singleColumnLayout(items: GridLayoutItem[], editMode: boolean): Layout {
  let y = 0;
  return items.map((item) => {
    const next: LayoutItem = {
      i: item.i,
      x: 0,
      y,
      w: 1,
      h: item.h,
      minW: 1,
      minH: item.minH ?? 2,
      static: !editMode,
    };
    y += item.h;
    return next;
  });
}

function fromLayoutItems(next: Layout): GridLayoutItem[] {
  return next.map((item) => ({
    i: item.i,
    x: item.x,
    y: item.y,
    w: item.w,
    h: item.h,
    minW: item.minW,
    minH: item.minH,
  }));
}

export function WidgetGrid({
  layout,
  data,
  editMode,
  onLayoutChange,
}: {
  layout: GridLayoutItem[];
  data: CommandCenterPayload;
  editMode: boolean;
  onLayoutChange: (next: GridLayoutItem[]) => void;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(1200);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      const w = entries[0]?.contentRect.width;
      if (w && w > 0) setWidth(w);
    });
    ro.observe(el);
    setWidth(el.offsetWidth || 1200);
    return () => ro.disconnect();
  }, []);

  const layouts = useMemo(
    () => ({
      lg: toLayoutItems(layout, editMode),
      md: toLayoutItems(layout, editMode),
      sm: toLayoutItems(
        layout.map((item) => ({ ...item, w: Math.min(item.w, 6) })),
        editMode,
      ),
      xs: singleColumnLayout(layout, editMode),
    }),
    [editMode, layout],
  );

  const handleChange = useCallback(
    (next: Layout) => {
      onLayoutChange(fromLayoutItems(next));
    },
    [onLayoutChange],
  );

  if (!layout.length) {
    return (
      <EmptyState
        icon={LayoutDashboard}
        title="No widgets visible"
        description="Enable widgets in Settings → Dashboard management, or check module access for your role."
        action={
          <Button asChild size="sm" variant="outline">
            <Link href="/settings/dashboards">Manage dashboard</Link>
          </Button>
        }
      />
    );
  }

  return (
    <div ref={containerRef} className={cn("command-center-grid w-full", editMode && "command-center-grid--edit")}>
      <ResponsiveGridLayout
        className="layout"
        layouts={layouts}
        breakpoints={BREAKPOINTS}
        cols={COLS}
        rowHeight={48}
        width={width}
        margin={[12, 12]}
        containerPadding={[0, 0]}
        isDraggable={editMode}
        isResizable={editMode}
        compactType="vertical"
        onLayoutChange={handleChange}
      >
        {layout.map((item) => (
          <div key={item.i} className="h-full">
            <CommandCenterWidget id={item.i} data={data} editMode={editMode} />
          </div>
        ))}
      </ResponsiveGridLayout>
    </div>
  );
}
