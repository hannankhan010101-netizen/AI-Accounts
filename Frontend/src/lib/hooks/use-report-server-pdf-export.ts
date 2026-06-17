"use client";

import { useCallback, useState } from "react";

import { downloadReportServerExport } from "@/lib/export/report-server-export";
import { reportsApi } from "@/lib/api/tenant";

/** Server-side PDF export via POST /reports/export. */
export function useReportServerPdfExport(reportId: string, filenameBase: string) {
  const [exportingPdf, setExportingPdf] = useState(false);

  const exportPdf = useCallback(
    async (criteria: Record<string, unknown>) => {
      setExportingPdf(true);
      try {
        const res = await reportsApi.exportReportSync({
          reportId,
          criteria,
          format: "pdf",
        });
        downloadReportServerExport(filenameBase, res.result);
      } finally {
        setExportingPdf(false);
      }
    },
    [reportId, filenameBase],
  );

  return { exportPdf, exportingPdf };
}
