import ExcelJS from "exceljs";
import type { StreamRow } from "./csv-stream.js";

export async function* streamXlsx(
  filePath: string,
  sheetName?: string,
): AsyncGenerator<StreamRow> {
  const workbook = new ExcelJS.Workbook();
  await workbook.xlsx.readFile(filePath);

  const sheet =
    sheetName !== undefined
      ? workbook.getWorksheet(sheetName)
      : workbook.worksheets[0];

  if (!sheet) return;

  const headers: string[] = [];
  const pending: StreamRow[] = [];
  let rowIndex = 0;

  sheet.eachRow((row, rowNumber) => {
    if (rowNumber === 1) {
      row.eachCell((cell, col) => {
        headers[col - 1] = String(cell.value ?? `col_${col}`);
      });
      return;
    }

    rowIndex++;
    const data: Record<string, unknown> = {};
    row.eachCell((cell, col) => {
      const header = headers[col - 1] ?? `col_${col}`;
      data[header] = cellValue(cell.value);
    });
    pending.push({ rowIndex, data });
  });

  for (const row of pending) {
    yield row;
  }
}

/** Chunked XLSX read for large files (row-by-row after header). */
export async function* streamXlsxChunked(
  filePath: string,
  chunkStartRow = 2,
): AsyncGenerator<StreamRow> {
  const workbook = new ExcelJS.stream.xlsx.WorkbookReader(filePath, {
    sharedStrings: "cache",
    hyperlinks: "ignore",
    styles: "ignore",
  });

  let headers: string[] = [];
  let rowIndex = 0;

  for await (const worksheet of workbook) {
    for await (const row of worksheet) {
      if (row.number === 1) {
        headers = [];
        row.eachCell((cell, col) => {
          headers[col - 1] = String(cell.value ?? `col_${col}`);
        });
        continue;
      }
      if (row.number < chunkStartRow) continue;

      rowIndex++;
      const data: Record<string, unknown> = {};
      row.eachCell({ includeEmpty: true }, (cell, col) => {
        const header = headers[col - 1] ?? `col_${col}`;
        data[header] = cellValue(cell.value);
      });
      yield { rowIndex, data };
    }
    break; // first sheet only
  }
}

function cellValue(value: ExcelJS.CellValue): unknown {
  if (value === null || value === undefined) return "";
  if (typeof value === "object" && "result" in value) {
    return (value as { result: unknown }).result;
  }
  if (value instanceof Date) return value.toISOString();
  return value;
}
