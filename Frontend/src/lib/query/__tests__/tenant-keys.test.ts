import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { describe, expect, it } from "vitest";

const SRC_ROOT = join(process.cwd(), "src");
const ALLOWED_USE_QUERY = new Set(["lib/api/tenant-query.ts"]);

function tenantQueryKey(companyId: string | null | undefined, ...parts: unknown[]) {
  return ["tenant", companyId ?? "", ...parts];
}

function walkTsFiles(dir: string, out: string[] = []): string[] {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    const stat = statSync(full);
    if (stat.isDirectory()) {
      if (entry === "node_modules" || entry === "__tests__") continue;
      walkTsFiles(full, out);
    } else if (/\.(ts|tsx)$/.test(entry)) {
      out.push(full);
    }
  }
  return out;
}

describe("tenant query keys", () => {
  it("tenantQueryKey prefixes tenant and company id", () => {
    expect(tenantQueryKey("co-1", "coa-tree")).toEqual(["tenant", "co-1", "coa-tree"]);
    expect(tenantQueryKey(null, "coa-tree")).toEqual(["tenant", "", "coa-tree"]);
  });

  it("only tenant-query.ts uses raw useQuery", () => {
    const offenders: string[] = [];
    for (const file of walkTsFiles(SRC_ROOT)) {
      const rel = relative(SRC_ROOT, file).replace(/\\/g, "/");
      const content = readFileSync(file, "utf8");
      if (/\buseQuery\s*\(/.test(content) && !ALLOWED_USE_QUERY.has(rel)) {
        offenders.push(rel);
      }
    }
    expect(offenders).toEqual([]);
  });

  it("no flat queryKey arrays without tenant prefix in app code", () => {
    const offenders: string[] = [];
    const flatKeyPattern = /queryKey:\s*\[\s*["'](?!tenant)[^"']+["']/;

    for (const file of walkTsFiles(SRC_ROOT)) {
      const rel = relative(SRC_ROOT, file).replace(/\\/g, "/");
      if (rel === "lib/api/tenant-query.ts") continue;
      const content = readFileSync(file, "utf8");
      if (flatKeyPattern.test(content)) {
        offenders.push(rel);
      }
    }
    expect(offenders).toEqual([]);
  });
});
