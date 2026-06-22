import { redirect } from "next/navigation";

export default function LegacyNewProductPage() {
  redirect("/inventory/add");
}
