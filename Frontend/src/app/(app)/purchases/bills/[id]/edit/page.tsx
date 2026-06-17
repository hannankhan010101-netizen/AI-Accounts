/** Edit draft supplier bill — catalog §6.3 */

"use client";
import { useTenantListQuery, invalidateTenantQueries, useTenantDetailQuery } from "@/lib/api/tenant-query";




import { useEffect, useMemo, useState } from "react";

import { useParams, useRouter } from "next/navigation";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { useFieldArray, useForm } from "react-hook-form";

import { z } from "zod";

import { zodResolver } from "@hookform/resolvers/zod";

import Decimal from "decimal.js";



import { DocumentWorkspace } from "@/components/patterns/document-workspace";

import { GstLineGrid, type GstLineRow } from "@/components/patterns/gst-line-grid";

import { FormField } from "@/components/ui/form-field";

import { Input } from "@/components/ui/input";

import { Select } from "@/components/ui/select";

import { DetailPageLoading } from "@/components/ui/detail-page-loading";

import {

  inventoryApi,

  partiesApi,

  purchasesApi,

  settingsApi,

  type SupplierBillCreateInput,

} from "@/lib/api/tenant";

import { ApiError } from "@/lib/api/client";

import { useCompany } from "@/lib/auth/company-context";

import { supplierBillToFormValues } from "@/lib/document-form-mappers";

import { applyLastRateToLine } from "@/lib/document/apply-last-rate";

import { hasMeaningfulLineGridDraft } from "@/lib/hooks/document-draft-helpers";

import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";

import { useLastRateSettings } from "@/lib/hooks/use-last-rate-settings";

import { useProductDescriptionColumns } from "@/lib/hooks/use-product-description-columns";

import { descriptionFieldsFromLine } from "@/lib/hooks/product-description-columns";





const lineSchema = z.object({

  productCode: z.string().optional(),

  quantity: z.string().regex(/^\d+(\.\d+)?$/u, "Positive number"),

  rate: z.string().regex(/^\d+(\.\d+)?$/u, "Positive number"),

  gstCode: z.string().optional(),

  gstRate: z.string().optional(),

  description: z.string().optional(),

  text1: z.string().optional(),

  text2: z.string().optional(),

  text3: z.string().optional(),

  text4: z.string().optional(),

  text5: z.string().optional(),

  text6: z.string().optional(),

  batchNumber: z.string().optional(),

  expiryDate: z.string().optional(),

});



const schema = z.object({

  billDate: z.string().min(1, "Required"),

  supplierId: z.string().min(1, "Required"),

  lines: z.array(lineSchema).min(1, "At least one line"),

});

type FormValues = z.infer<typeof schema>;



function emptyLine(): GstLineRow {

  return {

    productCode: "",

    quantity: "1",

    rate: "0",

    gstCode: "",

    gstRate: "",

    batchNumber: "",

    expiryDate: "",

  };

}



function dec(v: string): Decimal {

  if (!v) return new Decimal(0);

  try {

    return new Decimal(v);

  } catch {

    return new Decimal(0);

  }

}



export default function EditSupplierBillPage() {

  const router = useRouter();

  const params = useParams<{ id: string }>();

  const billId = params.id;

  const queryClient = useQueryClient();

  const { companyId } = useCompany();

  const [submitError, setSubmitError] = useState<string | null>(null);

  const [hydrated, setHydrated] = useState(false);



  const billQuery = useTenantDetailQuery(["supplier-bill", billId], () => purchasesApi.getSupplierBill(billId), { enabled: Boolean(billId) });



  const suppliersQuery = useTenantListQuery(["suppliers"], () => partiesApi.listSuppliers());

  const productsQuery = useTenantListQuery(["products"], () => inventoryApi.listProducts());

  const taxesQuery = useTenantListQuery(["taxes-year-end"], () => settingsApi.getTaxesYearEnd());

  const gstRates = taxesQuery.data?.result?.gstRates ?? [];

  const { columns: descriptionColumns } = useProductDescriptionColumns("VI");

  const { addEditEnabled: lastRateEnabled } = useLastRateSettings("VI");



  const form = useForm<FormValues>({

    resolver: zodResolver(schema),

    defaultValues: {

      billDate: new Date().toISOString().slice(0, 10),

      supplierId: "",

      lines: [emptyLine()],

    },

  });



  const lines = useFieldArray({ control: form.control, name: "lines" });

  const watched = form.watch();

  const watchedLines = watched.lines ?? [];

  const supplierId = watched.supplierId;



  useEffect(() => {

    const bill = billQuery.data?.result;

    if (!bill || hydrated) return;

    if (bill.status !== "draft") {

      router.replace(`/purchases/bills/${billId}`);

      return;

    }

    form.reset(supplierBillToFormValues(bill));

    setHydrated(true);

  }, [billQuery.data, form, hydrated, billId, router]);



  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({

    scope: `supplier-bill-edit:${billId}`,

    companyId,

    form,

    values: watched,
    enabled: hydrated,
    shouldPersist: hasMeaningfulLineGridDraft,
  });



  const supplierName = useMemo(() => {

    const s = suppliersQuery.data?.result.find((x) => x.id === supplierId);

    return s?.name ?? "—";

  }, [suppliersQuery.data, supplierId]);



  const lineTotals = useMemo(

    () =>

      watchedLines.map((l) => {

        const sub = dec(l.quantity).times(dec(l.rate));

        const ratePct = l.gstRate ? dec(l.gstRate) : new Decimal(0);

        const tax = ratePct.gt(0) ? sub.times(ratePct).div(100) : new Decimal(0);

        return sub.plus(tax);

      }),

    [watchedLines],

  );

  const subtotal = useMemo(

    () =>

      watchedLines.reduce((acc, l) => acc.plus(dec(l.quantity).times(dec(l.rate))), new Decimal(0)),

    [watchedLines],

  );

  const grandTotal = useMemo(

    () => lineTotals.reduce((acc, v) => acc.plus(v), new Decimal(0)),

    [lineTotals],

  );



  const mutation = useMutation({

    mutationFn: (input: SupplierBillCreateInput) =>

      purchasesApi.updateSupplierBill(billId, input),

    onSuccess: async () => {

      clearDraftOnSuccess();

      await invalidateTenantQueries(queryClient, "supplier-bills");

      await invalidateTenantQueries(queryClient, "supplier-bill", billId);

      router.push(`/purchases/bills/${billId}`);

    },

    onError: (err) =>

      setSubmitError(err instanceof ApiError ? err.message : "Could not update bill"),

  });



  const onSubmit = form.handleSubmit((values) => {

    setSubmitError(null);

    mutation.mutate({

      billDate: new Date(values.billDate).toISOString(),

      supplierId: values.supplierId,

      lines: values.lines.map((l) => {

        const row: SupplierBillCreateInput["lines"][number] = {

          productCode: l.productCode || null,

          quantity: l.quantity,

          rate: l.rate,

          gstCode: l.gstCode || null,

          gstRate: l.gstRate || null,

        };

        if (l.description?.trim()) row.description = l.description.trim();

        const extra = descriptionFieldsFromLine(l as Record<string, unknown>, descriptionColumns);

        if (extra) row.descriptionFields = extra;

        if (l.batchNumber?.trim()) row.batchNumber = l.batchNumber.trim();

        if (l.expiryDate?.trim()) row.expiryDate = new Date(l.expiryDate).toISOString();

        return row;

      }),

    });

  });



  if (billQuery.isLoading || !hydrated) {

    return <DetailPageLoading />;

  }

  if (billQuery.error instanceof Error) {

    return (

      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">

        {billQuery.error.message}

      </div>

    );

  }



  const bill = billQuery.data?.result;

  const docNo = bill?.documentNumber ?? billId;



  return (

    <DocumentWorkspace

      title={`Edit bill ${docNo}`}

      breadcrumb={`Buy / Bills / ${docNo} / Edit`}

      formId="vi-edit-form"

      onSubmit={onSubmit}

      topBanner={topBanner}

      isSaving={mutation.isPending}

      saveLabel="Save changes"

      onCancel={() => router.push(`/purchases/bills/${billId}`)}

      grandTotal={grandTotal.toFixed(2)}

      grandTotalLabel="Total incl. tax"

      error={submitError}

      summaryLines={[

        { label: "Supplier", value: supplierName, emphasis: true },

        { label: "Lines", value: String(watchedLines.length) },

        { label: "Subtotal", value: subtotal.toFixed(2) },

        { label: "Tax", value: grandTotal.minus(subtotal).toFixed(2) },

      ]}

      header={

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">

          <FormField label="Bill date" required error={form.formState.errors.billDate?.message}>

            <Input type="date" {...form.register("billDate")} />

          </FormField>

          <FormField label="Supplier" required error={form.formState.errors.supplierId?.message}>

            <Select {...form.register("supplierId")}>

              <option value="">Select supplier…</option>

              {suppliersQuery.data?.result.map((s) => (

                <option key={s.id} value={s.id}>

                  {s.name}

                  {s.code ? ` (${s.code})` : ""}

                </option>

              ))}

            </Select>

          </FormField>

        </div>

      }

    >

      <GstLineGrid

        form={form}

        lines={lines}

        lineTotals={lineTotals}

        products={productsQuery.data?.result}

        gstRates={gstRates}

        showProject={false}

        emptyLine={emptyLine}

        showBatchExpiry

        descriptionColumns={descriptionColumns}

        onProductSelect={

          lastRateEnabled && supplierId

            ? async (lineIndex, productCode) => {

                await applyLastRateToLine(

                  (field, value) => form.setValue(`lines.${lineIndex}.${field}`, value),

                  productCode,

                  { partyKind: "supplier", partyId: supplierId, docType: "VI" },

                );

              }

            : undefined

        }

      />

    </DocumentWorkspace>

  );

}


