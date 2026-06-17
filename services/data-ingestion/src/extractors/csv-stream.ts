import { createReadStream } from "node:fs";
import { parse } from "csv-parse";
import type { Readable } from "node:stream";

export interface StreamRow {
  rowIndex: number;
  data: Record<string, unknown>;
}

export async function* streamCsv(
  filePath: string,
  options: { headers?: boolean; delimiter?: string } = {},
): AsyncGenerator<StreamRow> {
  const parser = createReadStream(filePath).pipe(
    parse({
      columns: options.headers !== false,
      skip_empty_lines: true,
      trim: true,
      delimiter: options.delimiter ?? ",",
      relax_column_count: true,
    }),
  );

  let rowIndex = 0;
  for await (const record of parser) {
    rowIndex++;
    yield {
      rowIndex,
      data: record as Record<string, unknown>,
    };
  }
}

export async function* streamCsvFromReadable(
  stream: Readable,
): AsyncGenerator<StreamRow> {
  const parser = stream.pipe(
    parse({
      columns: true,
      skip_empty_lines: true,
      trim: true,
      relax_column_count: true,
    }),
  );

  let rowIndex = 0;
  for await (const record of parser) {
    rowIndex++;
    yield { rowIndex, data: record as Record<string, unknown> };
  }
}

export async function collectRows(
  generator: AsyncGenerator<StreamRow>,
  maxRows?: number,
): Promise<StreamRow[]> {
  const rows: StreamRow[] = [];
  for await (const row of generator) {
    rows.push(row);
    if (maxRows && rows.length >= maxRows) break;
  }
  return rows;
}
