"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/** Nominals — alias to Chart of Accounts grid (catalog §9.1.3). */
export default function NominalsPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/settings/coa");
  }, [router]);
  return null;
}
