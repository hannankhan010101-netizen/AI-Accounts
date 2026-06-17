import type { GridLayoutItem } from "@/components/dashboard/command-center/types/command-center";

function collides(a: GridLayoutItem, b: GridLayoutItem): boolean {
  if (a.i === b.i) return false;
  return (
    a.x < b.x + b.w &&
    a.x + a.w > b.x &&
    a.y < b.y + b.h &&
    a.y + a.h > b.y
  );
}

/** Remove empty vertical gaps when widgets are hidden or filtered out. */
export function compactGridLayout(items: GridLayoutItem[]): GridLayoutItem[] {
  if (items.length === 0) return items;

  const sorted = [...items].sort((a, b) => a.y - b.y || a.x - b.x);
  const placed: GridLayoutItem[] = [];

  for (const item of sorted) {
    let y = 0;
    while (true) {
      const candidate = { ...item, y };
      const hit = placed.some((p) => collides(candidate, p));
      if (!hit) {
        placed.push(candidate);
        break;
      }
      y += 1;
    }
  }

  return placed;
}
