"use client";



import { BRAND } from "@/lib/brand";

import type { PrintTemplateSettings } from "@/lib/api/tenant";

import {

  resolvePrintPaperClass,

  resolvePrintTitle,

} from "@/lib/hooks/use-print-template";



export interface VoucherPrintField {

  label: string;

  value: string;

}



interface VoucherPrintProps {

  title: string;

  documentNumber: string;

  documentDate?: string;

  businessName?: string | null;

  businessAddress?: string | null;

  businessLogoUrl?: string | null;

  fields: VoucherPrintField[];

  tableHeaders?: string[];

  tableRows?: string[][];

  notes?: string | null;

  template?: Partial<PrintTemplateSettings> | null;

}



function VoucherPrintBody({

  displayTitle,

  documentNumber,

  documentDate,

  businessName,

  businessAddress,

  businessLogoUrl,

  fields,

  tableHeaders,

  tableRows,

  notes,

  showLogo,

  showBusiness,

  headerNote,

  footerNote,

}: {

  displayTitle: string;

  documentNumber: string;

  documentDate?: string;

  businessName?: string | null;

  businessAddress?: string | null;

  businessLogoUrl?: string | null;

  fields: VoucherPrintField[];

  tableHeaders?: string[];

  tableRows?: string[][];

  notes?: string | null;

  showLogo: boolean;

  showBusiness: boolean;

  headerNote?: string;

  footerNote?: string;

}) {

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

          {documentDate ? (

            <div className="text-sm">Date: {new Date(documentDate).toLocaleDateString()}</div>

          ) : null}

        </div>

      </header>



      {headerNote ? <p className="mb-4 text-xs text-neutral-600">{headerNote}</p> : null}



      <section className="mb-6 grid grid-cols-2 gap-x-6 gap-y-3 text-sm md:grid-cols-3">

        {fields.map((f) => (

          <div key={f.label}>

            <div className="text-[10px] font-semibold uppercase tracking-wide text-neutral-500">

              {f.label}

            </div>

            <div className="mt-0.5 font-medium">{f.value}</div>

          </div>

        ))}

      </section>



      {tableHeaders && tableRows && tableRows.length > 0 ? (

        <table className="mb-6 w-full border-collapse text-sm">

          <thead>

            <tr className="border-y border-neutral-300 bg-neutral-100 print:border-black">

              {tableHeaders.map((h) => (

                <th key={h} className="px-2 py-2 text-left first:text-left last:text-right">

                  {h}

                </th>

              ))}

            </tr>

          </thead>

          <tbody>

            {tableRows.map((row, i) => (

              <tr key={i} className="border-b border-neutral-200">

                {row.map((cell, j) => (

                  <td

                    key={j}

                    className={`px-2 py-1.5 ${j === row.length - 1 ? "text-right tabular-nums" : ""}`}

                  >

                    {cell}

                  </td>

                ))}

              </tr>

            ))}

          </tbody>

        </table>

      ) : null}



      {notes ? (

        <div className="mb-6 border border-neutral-200 bg-neutral-50 p-3 text-xs">

          <div className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-neutral-500">

            Notes

          </div>

          {notes}

        </div>

      ) : null}



      {footerNote ? <p className="text-xs text-neutral-600">{footerNote}</p> : null}

    </>

  );

}



export function VoucherPrint({

  title,

  documentNumber,

  documentDate,

  businessName,

  businessAddress,

  businessLogoUrl,

  fields,

  tableHeaders,

  tableRows,

  notes,

  template,

}: VoucherPrintProps) {

  const displayTitle = resolvePrintTitle(title, template ?? undefined);

  const showLogo = template?.showLogo !== false;

  const showBusiness = template?.showBusinessBlock !== false;

  const paperClass = resolvePrintPaperClass(template ?? undefined);

  const headerNote = template?.headerNote?.trim() || undefined;

  const footerNote = template?.footerNote?.trim() || undefined;

  const twoCopies = Boolean(template?.twoCopies);



  const bodyProps = {

    displayTitle,

    documentNumber,

    documentDate,

    businessName,

    businessAddress,

    fields,

    tableHeaders,

    tableRows,

    notes,

    showLogo,

    showBusiness,

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

        <VoucherPrintBody {...bodyProps} />

        {twoCopies ? <VoucherPrintBody {...bodyProps} /> : null}

      </div>

    </div>

  );

}


