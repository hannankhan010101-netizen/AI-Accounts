import { z } from "zod";

const decimalString = z
  .string()
  .regex(/^\d+(\.\d+)?$/u, "Enter a valid number")
  .or(z.literal(""));

export const productFormSchema = z
  .object({
    code: z.string().optional(),
    name: z.string().min(1, "Name is required"),
    isStock: z.boolean().default(true),
    unit: z.string().min(1, "Unit is required").default("EA"),
    category: z.string().optional(),
    salePrice: decimalString,
    cost: decimalString,
    lowStockLevel: decimalString,
    binLocation: z.string().optional(),
    openingQty: decimalString,
    openingRate: decimalString,
  })
  .superRefine((data, ctx) => {
    if (data.isStock && !data.salePrice) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Sale price is required for stock products",
        path: ["salePrice"],
      });
    }
    if (data.openingQty && data.openingQty !== "0" && !data.isStock) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Opening stock applies to stock products only",
        path: ["openingQty"],
      });
    }
  });

export type ProductFormValues = z.infer<typeof productFormSchema>;

export const productFormDefaults: ProductFormValues = {
  code: "",
  name: "",
  isStock: true,
  unit: "EA",
  category: "",
  salePrice: "",
  cost: "",
  lowStockLevel: "",
  binLocation: "",
  openingQty: "",
  openingRate: "",
};
