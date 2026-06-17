"use client";

import Decimal from "decimal.js";

import { BRAND } from "@/lib/brand";
import type { PrintTemplateSettings } from "@/lib/api/tenant";
import {
  resolvePrintPaperClass,
  resolvePrintTitle,
} from "@/lib/hooks/use-print-template";
import { useESignatures, type ESignatureRow } from "@/lib/hooks/use-e-signatures";

interface PartyBlock {
  label: string;
  name?: string | null;
  code?: string | null;
  addressLines?: string[];
}

interface PrintLine {
  productCode?: string | null;
  description?: string | null;
  quantity?: string | number | null;
  rate?: string | number | null;
  gstCode?: string | null;
  taxAmount?: string | number | null;
  lineTotal: string | number;
}

interface DocumentPrintProps {
  title: string;
  documentNumber: string;
  documentDate: string;
  businessName?: string | null;
  businessAddress?: string | null;
  businessLogoUrl?: string | null;
  party: PartyBlock;
  lines: PrintLine[];
  total: string | number;
  notes?: string | null;
  footer?: React.ReactNode;
  template?: PrintTemplateSettings | null;
}

function fmt(v: string | number | null | undefined): string {
  if (v === null || v === undefined || v === "") return "";
  try {
    return new Decimal(typeof v === "string" ? v : v.toString()).toFixed(2);
  } catch {
    return String(v);
  }
}

function DefaultPrintFooter({ eSignatures }: { eSignatures: ESignatureRow[] }) {
  if (eSignatures.length > 0) {
    return (
      <div className="flex flex-wrap justify-between gap-8">
        {eSignatures.map((sig) => (
          <div key={sig.name} className="min-w-[140px]">
            {sig.signatureUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={sig.signatureUrl}
                alt={sig.name}
                className="mb-2 h-12 max-w-[180px] object-contain"
              />
            ) : (
              <div className="mb-2 h-12" />
            )}
            <div className="border-t border-neutral-400 pt-1 font-semibold print:border-black">
              {sig.name}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="flex justify-between">
      <div>
        <div className="font-semibold">Prepared by</div>
        <div className="mt-8 border-t border-neutral-400 pt-1 print:border-black">
          Signature
        </div>
      </div>
      <div>
        <div className="font-semibold">Received by</div>
        <div className="mt-8 border-t border-neutral-400 pt-1 print:border-black">
          Signature
        </div>
      </div>
    </div>
  );
}

function DocumentPrintBody({
  displayTitle,
  documentNumber,
  documentDate,
  businessName,
  businessAddress,
  businessLogoUrl,
  party,
  lines,
  total,
  notes,
  footer,
  eSignatures,
  showLogo,
  showBusiness,
  showGst,
  headerNote,
  footerNote,
}: {
  displayTitle: string;
  documentNumber: string;
  documentDate: string;
  businessName?: string | null;
  businessAddress?: string | null;
  businessLogoUrl?: string | null;
  party: PartyBlock;
  lines: PrintLine[];
  total: string | number;
  notes?: string | null;
  footer?: React.ReactNode;
  eSignatures: ESignatureRow[];
  showLogo: boolean;
  showBusiness: boolean;
  showGst: boolean;
  headerNote?: string;
  footerNote?: string;
}) {
  const totalColSpan = showGst ? 7 : 5;

  return (
    <>
      <header className="mb-6 flex items-start justify-between border-b border-neutral-300 pb-4 print:border-black">
        <div>
          {(showLogo || showBusiness) && (
            <div className="flex flex-col gap-2">
              {showLogo ? (
                /* eslint-disable-next-line @next/next/no-img-element */
                <img
                  src={businessLogoUrl || BRAND.logo}
                  alt={businessName ?? BRAND.name}
                  className="h-12 w-auto max-w-[180px] object-contain object-left"
                />
              ) : null}
              {showBusiness ? (
                <div className="text-lg font-bold uppercase tracking-wide">
                  {businessName ?? BRAND.name}
                </div>
              ) : null}
            </div>
          )}
          {showBusiness && businessAddress ? (
            <div className="mt-1 whitespace-pre-line text-xs text-neutral-600">{businessAddress}</div>
          ) : null}
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold uppercase tracking-wide">{displayTitle}</div>
          <div className="mt-1 text-sm">No. {documentNumber}</div>
          <div className="text-sm">Date: {new Date(documentDate).toLocaleDateString()}</div>
        </div>
      </header>

      {headerNote ? <p className="mb-4 text-xs text-neutral-600">{headerNote}</p> : null}

      <section className="mb-4">
        <div className="text-xs font-semibold uppercase tracking-wide text-neutral-500">
          {party.label}
        </div>
        <div className="mt-1 text-sm font-medium">{party.name ?? party.code ?? "—"}</div>
        {party.code && party.name ? (
          <div className="text-xs text-neutral-500">{party.code}</div>
        ) : null}
        {party.addressLines?.map((line, i) => (
          <div key={i} className="text-xs text-neutral-600">
            {line}
          </div>
        ))}
      </section>

      <table className="mb-6 w-full border-collapse text-sm">
        <thead>
          <tr className="border-y border-neutral-300 bg-neutral-100 print:border-black print:bg-neutral-100">
            <th className="px-2 py-2 text-left">#</th>
            <th className="px-2 py-2 text-left">Product</th>
            <th className="px-2 py-2 text-left">Description</th>
            <th className="px-2 py-2 text-right">Qty</th>
            <th className="px-2 py-2 text-right">Rate</th>
            {showGst ? (
              <>
                <th className="px-2 py-2 text-left">GST</th>
                <th className="px-2 py-2 text-right">Tax</th>
              </>
            ) : null}
            <th className="px-2 py-2 text-right">Line total</th>
          </tr>
        </thead>
        <tbody>
          {lines.map((line, i) => (
            <tr key={i} className="border-b border-neutral-200">
              <td className="px-2 py-1.5">{i + 1}</td>
              <td className="px-2 py-1.5 font-mono">{line.productCode ?? "—"}</td>
              <td className="px-2 py-1.5">{line.description ?? ""}</td>
              <td className="px-2 py-1.5 text-right tabular-nums">{fmt(line.quantity)}</td>
              <td className="px-2 py-1.5 text-right tabular-nums">{fmt(line.rate)}</td>
              {showGst ? (
                <>
                  <td className="px-2 py-1.5">{line.gstCode ?? "—"}</td>
                  <td className="px-2 py-1.5 text-right tabular-nums">
                    {line.taxAmount !== undefined ? fmt(line.taxAmount) : "—"}
                  </td>
                </>
              ) : null}
              <td className="px-2 py-1.5 text-right tabular-nums">{fmt(line.lineTotal)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="border-y-2 border-neutral-400 bg-neutral-50 font-semibold print:border-black">
            <td colSpan={totalColSpan} className="px-2 py-2 text-right">
              Total
            </td>
            <td className="px-2 py-2 text-right tabular-nums">{fmt(total)}</td>
          </tr>
        </tfoot>
      </table>

      {notes ? (
        <div className="mb-6 border border-neutral-200 bg-neutral-50 p-3 text-xs">
          <div className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-neutral-500">
            Notes
          </div>
          {notes}
        </div>
      ) : null}

      {footerNote ? <p className="mb-4 text-xs text-neutral-600">{footerNote}</p> : null}

      <footer className="mt-12 border-t border-neutral-300 pt-6 text-xs text-neutral-500 print:border-black">
        {footer ?? <DefaultPrintFooter eSignatures={eSignatures} />}
      </footer>
    </>
  );
}

export function DocumentPrint(props: DocumentPrintProps) {
  const {
    title,
    documentNumber,
    documentDate,
    businessName,
    businessAddress,
    businessLogoUrl,
    party,
    lines,
    total,
    notes,
    footer,
    template,
  } = props;

  const displayTitle = resolvePrintTitle(title, template ?? undefined);
  const showLogo = template?.showLogo !== false;
  const showBusiness = template?.showBusinessBlock !== false;
  const showGst =
    template?.showTaxColumns === false
      ? false
      : lines.some(
          (l) => l.gstCode || (l.taxAmount !== undefined && Number(l.taxAmount) > 0),
        );
  const paperClass = resolvePrintPaperClass(template ?? undefined);
  const headerNote = template?.headerNote?.trim() || undefined;
  const footerNote = template?.footerNote?.trim() || undefined;
  const twoCopies = Boolean(template?.twoCopies);
  const { eSignatures } = useESignatures();

  const bodyProps = {
    displayTitle,
    documentNumber,
    documentDate,
    businessName,
    businessAddress,
    businessLogoUrl,
    party,
    lines,
    total,
    notes,
    footer,
    eSignatures,
    showLogo,
    showBusiness,
    showGst,
    headerNote,
    footerNote,
  };

  return (
    <div
      className={`mx-auto bg-white p-8 text-neutral-900 print:bg-white print:text-black ${paperClass}`}
    >
      <div className="no-print mb-4 flex gap-2">
        <button
          type="button"
          onClick={() => window.print()}
          className="btn-brand rounded-md px-4 py-2 text-sm font-medium"
        >
          Print / Save as PDF
        </button>
        <button
          type="button"
          onClick={() => window.history.back()}
          className="rounded-md border border-border bg-surface px-4 py-2 text-sm text-fg hover:bg-canvas"
        >
          Back
        </button>
      </div>

      <div className={twoCopies ? "print:grid print:grid-cols-2 print:gap-6" : undefined}>
        <DocumentPrintBody {...bodyProps} />
        {twoCopies ? <DocumentPrintBody {...bodyProps} /> : null}
      </div>
    </div>
  );
}
