/** Imperative scroll-to-row for virtualized grids during tours (P2). */

type GridScrollHandler = (rowIndex: number) => void;

const handlers = new Map<string, GridScrollHandler>();

export function registerGridTourScroll(
  gridId: string,
  handler: GridScrollHandler,
): () => void {
  handlers.set(gridId, handler);
  return () => {
    handlers.delete(gridId);
  };
}

export function scrollGridTourRow(gridId: string, rowIndex: number): void {
  handlers.get(gridId)?.(rowIndex);
}
