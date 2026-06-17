import { redirect } from "next/navigation";

/** Analytical reports ship inside Insights — avoid dead-end coming-soon. */
export default function AnalyticalReportsRedirect() {
  redirect("/reports");
}
