/**
 * Wave 1 parity wiring — FastAccounts module keys → UI route → tenant API.
 * Keep in sync with scripts/fastaccounts_export/modules_manifest.py and navigation.ts.
 */

export interface Wave1Connection {
  /** Key in modules_manifest.py */
  moduleKey: string;
  catalogLabel: string;
  href: string;
  apiPath: string;
  apiMethod: "GET" | "POST";
}

export const WAVE1_CONNECTIONS: Wave1Connection[] = [
  {
    moduleKey: "sales_all",
    catalogLabel: "Sales All",
    href: "/sales/all",
    apiPath: "/sales-activity",
    apiMethod: "GET",
  },
  {
    moduleKey: "purchases_all",
    catalogLabel: "Purchases All",
    href: "/purchases/all",
    apiPath: "/purchases-activity",
    apiMethod: "GET",
  },
  {
    moduleKey: "bank_import_statement",
    catalogLabel: "Import Statement",
    href: "/bank/import-statement",
    apiPath: "/bank-statement-import",
    apiMethod: "POST",
  },
  {
    moduleKey: "analytical_reports",
    catalogLabel: "Analytical Reports",
    href: "/reports/analytical",
    apiPath: "/reports/definitions",
    apiMethod: "GET",
  },
];

export const WAVE1_HREFS = WAVE1_CONNECTIONS.map((c) => c.href);
