#!/usr/bin/env npx tsx
/**
 * CLI: bulk-import FastAccounts labeled JSON into AI-Accounts via ingestion pipeline.
 *
 * Usage:
 *   npx tsx src/cli/fastaccounts-import.ts \
 *     --company-id <id> \
 *     --token <jwt> \
 *     --file ../../scripts/fastaccounts_export/output/fastaccounts_labeled_data.json \
 *     --modules customers,suppliers,products
 */
import { parseArgs } from "node:util";
import { streamFastAccountsLabeled, listFastAccountsSections } from "../extractors/fastaccounts-adapter.js";
import type { EntityModule } from "../types/pipeline.js";
import { config } from "../config.js";

const { values } = parseArgs({
  options: {
    "company-id": { type: "string" },
    token: { type: "string" },
    file: { type: "string" },
    modules: { type: "string", default: "customers,suppliers,products" },
    "api-url": { type: "string" },
  },
});

async function main() {
  const companyId = values["company-id"];
  const token = values.token;
  const file = values.file;
  if (!companyId || !token || !file) {
    console.error("Required: --company-id, --token, --file");
    process.exit(1);
  }

  const base = values["api-url"] ?? `http://127.0.0.1:${config.PORT}`;
  const modules = (values.modules ?? "").split(",").filter(Boolean) as EntityModule[];

  const sections = await listFastAccountsSections(file);
  console.log("Available sections:");
  for (const s of sections) {
    console.log(`  ${s.moduleKey} → ${s.module ?? "?"} (${s.recordCount} rows)`);
  }

  for (const module of modules) {
    console.log(`\n=== Starting ${module} ===`);
    const runRes = await fetch(`${base}/api/v1/companies/${companyId}/migrations/runs`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        name: `FastAccounts ${module}`,
        module,
        sourceType: "fastaccounts",
        sourceSystem: "fastaccounts",
        sourceKey: file,
      }),
    });
    if (!runRes.ok) {
      console.error(await runRes.text());
      continue;
    }
    const { result: run } = (await runRes.json()) as { result: { id: string } };

    const startRes = await fetch(
      `${base}/api/v1/companies/${companyId}/migrations/runs/${run.id}/start`,
      { method: "POST", headers: { Authorization: `Bearer ${token}` } },
    );
  console.log(await startRes.json());
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
