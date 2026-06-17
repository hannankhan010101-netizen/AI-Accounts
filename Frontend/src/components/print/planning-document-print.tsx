"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { DocumentPrint } from "@/components/print/document-print";
import { PrintQueryShell } from "@/components/print/print-query-shell";
import type { DocumentLine } from "@/lib/api/tenant";
import { partiesApi, settingsApi } from "@/lib/api/tenant";
import { usePrintTemplate } from "@/lib/hooks/use-print-template";

export interface PlanningPrintDoc {
  documentNumber: string;
  documentDate: string;
  partyId: string;
  lines: DocumentLine[];
  totalAmount: string | number;
  notes?: string | null;
}

interface PlanningDocumentPrintProps<T> {
  title: string;
  partyLabel: string;
  templateCode: string;
  queryKey: string;
  fetchDetail: (id: string) => Promise<{ result: T }>;
  mapDoc: (detail: T) => PlanningPrintDoc;
  partyMode: "customer" | "supplier";
}

export function PlanningDocumentPrint<T>({
  title,
  partyLabel,
  templateCode,
  queryKey,
  fetchDetail,
  mapDoc,
  partyMode,
}: PlanningDocumentPrintProps<T>) {
  const params = useParams<{ id: string }>();

  const templateQuery = usePrintTemplate(templateCode);

  const docQuery = useTenantListQuery([queryKey, params.id], () => fetchDetail(params.id),
    { enabled: !!params.id,
    retry: false });
  const businessQuery = useTenantListQuery(["business-information"], () => settingsApi.getBusinessInformation());
  const partiesQuery = useTenantListQuery([partyMode === "customer" ? "customers" : "suppliers"], () =>
      partyMode === "customer"
        ? partiesApi.listCustomers()
        : partiesApi.listSuppliers());

  const raw = docQuery.data?.result;
  const doc = raw ? mapDoc(raw) : null;

  const business = businessQuery.data?.result;
  const partyId = doc?.partyId;
  const party = partyId
    ? partiesQuery.data?.result.find((p) => p.id === partyId)
    : undefined;

  const businessAddress = business
    ? [
        business.addressLine1,
        business.addressLine2,
        business.addressLine3,
        business.addressLine4,
        business.addressLine5,
      ]
        .filter(Boolean)
        .join("\n")
    : null;

  return (
    <PrintQueryShell
      isLoading={docQuery.isLoading || businessQuery.isLoading || partiesQuery.isLoading || templateQuery.isLoading}
      error={docQuery.error}
      ready={Boolean(doc)}
    >
      {doc ? (
        <DocumentPrint
          title={title}
          documentNumber={String(doc.documentNumber)}
          documentDate={doc.documentDate}
          businessName={business?.businessName ?? null}
          businessAddress={businessAddress}
          businessLogoUrl={business?.logoUrl ?? null}
          party={{
            label: partyLabel,
            name: party?.name ?? null,
            code: party?.code ?? null,
          }}
          lines={doc.lines.map((l) => ({
            productCode: l.productCode,
            description: null,
            quantity: l.quantity,
            rate: l.rate,
            gstCode: l.gstCode,
            taxAmount: l.taxAmount,
            lineTotal: l.lineTotal,
          }))}
          total={doc.totalAmount}
          notes={doc.notes ?? undefined}
          template={templateQuery.data?.result}
        />
      ) : null}
    </PrintQueryShell>
  );
}
