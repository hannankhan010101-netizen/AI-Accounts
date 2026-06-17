/**
 * One-time codemod: migrate useQuery + *QueryOptions to useTenant*Query hooks.
 * Run: node scripts/migrate-tenant-queries.mjs
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SRC = path.join(__dirname, "..", "src");

const TIER_MAP = {
  referenceQueryOptions: "useTenantReferenceQuery",
  listQueryOptions: "useTenantListQuery",
  detailQueryOptions: "useTenantDetailQuery",
  reportQueryOptions: "useTenantReportQuery",
  paginatedListQueryOptions: "useTenantListQuery",
};

function walk(dir, out = []) {
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name);
    const st = fs.statSync(p);
    if (st.isDirectory()) {
      if (name === "node_modules") continue;
      walk(p, out);
    } else if (/\.(tsx|ts)$/.test(name) && !name.endsWith(".test.ts")) {
      out.push(p);
    }
  }
  return out;
}

function extractBalanced(source, startIdx, openChar, closeChar) {
  let depth = 0;
  let i = startIdx;
  for (; i < source.length; i++) {
    const ch = source[i];
    if (ch === openChar) depth++;
    else if (ch === closeChar) {
      depth--;
      if (depth === 0) return source.slice(startIdx, i + 1);
    }
  }
  return null;
}

function parseOptionsObject(inner) {
  const queryKeyMatch = inner.match(/queryKey:\s*(\[[\s\S]*?\])\s*,/);
  const queryFnMatch = inner.match(/queryFn:\s*((?:\(\)\s*=>\s*[^,]+|\([^)]*\)\s*=>\s*[^,]+|async\s*\([^)]*\)\s*=>\s*[^,]+))/);
  if (!queryKeyMatch || !queryFnMatch) return null;

  const queryKey = queryKeyMatch[1].trim();
  let queryFn = queryFnMatch[1].trim();
  // extend queryFn if it ends early (multiline)
  const fnStart = inner.indexOf(queryFnMatch[0]);
  const afterFn = inner.slice(fnStart + queryFnMatch[0].length);
  if (afterFn.startsWith(",")) {
    // ok
  }

  const restStart = inner.indexOf(queryFnMatch[0]) + queryFnMatch[0].length;
  let rest = inner.slice(restStart).replace(/^,\s*/, "").replace(/,\s*$/, "").trim();
  if (rest === "") rest = null;

  // unwrap queryKey array to key parts string
  let keyParts = queryKey.slice(1, -1).trim();
  if (!keyParts) keyParts = "";

  return { keyParts, queryFn, rest };
}

function migrateFile(filePath) {
  let src = fs.readFileSync(filePath, "utf8");
  if (!src.includes("useQuery")) return false;
  if (filePath.endsWith("tenant-query.ts")) return false;

  let changed = false;
  const rel = path.relative(SRC, filePath).replace(/\\/g, "/");

  for (const [optName, hookName] of Object.entries(TIER_MAP)) {
    const needle = `useQuery(\n    ${optName}(`;
    let idx = 0;
    while ((idx = src.indexOf(needle, idx)) !== -1) {
      const parenStart = idx + "useQuery(".length;
      const objStart = src.indexOf("{", parenStart);
      const obj = extractBalanced(src, objStart, "{", "}");
      if (!obj) break;
      const parsed = parseOptionsObject(obj.slice(1, -1));
      if (!parsed) {
        idx += needle.length;
        continue;
      }
      const closeParen = objStart + obj.length;
      if (src[closeParen] !== ")") {
        idx += needle.length;
        continue;
      }
      const end = closeParen + 2; // )
      const restOpt = parsed.rest ? `, { ${parsed.rest} }` : "";
      const replacement = `${hookName}([${parsed.keyParts}], ${parsed.queryFn}${restOpt})`;
      src = src.slice(0, idx) + replacement + src.slice(end);
      changed = true;
      idx += replacement.length;
    }

    // single-line variant: useQuery(referenceQueryOptions({ queryKey: [...], queryFn: ... }))
    const re = new RegExp(
      `useQuery\\(\\s*${optName}\\(\\{\\s*queryKey:\\s*(\\[[^\\]]+\\]),\\s*queryFn:\\s*([^,}]+(?:\\([^)]*\\))?[^,}]*)(?:,\\s*([^}]+))?\\s*\\}\\)\\s*\\)`,
      "g",
    );
    src = src.replace(re, (_, key, fn, extra) => {
      changed = true;
      const keyInner = key.slice(1, -1).trim();
      const extraPart = extra ? `, { ${extra.trim()} }` : "";
      return `${hookName}([${keyInner}], ${fn.trim()}${extraPart})`;
    });
  }

  // invalidateQueries migration
  src = src.replace(
    /(\w+)\.invalidateQueries\(\{\s*queryKey:\s*\[([^\]]+)\]\s*\}\)/g,
    (_, client, keys) => {
      changed = true;
      const parts = keys
        .split(",")
        .map((k) => k.trim())
        .filter(Boolean)
        .join(", ");
      return `invalidateTenantQueries(${client}, ${parts})`;
    },
  );

  if (changed) {
    // fix imports
    if (
      src.includes("useTenantReferenceQuery") ||
      src.includes("useTenantListQuery") ||
      src.includes("useTenantDetailQuery") ||
      src.includes("useTenantReportQuery")
    ) {
      if (src.includes('from "@/lib/api/tenant-query"')) {
        src = src.replace(
          /from "@\/lib\/api\/tenant-query"/,
          'from "@/lib/api/tenant-query"',
        );
        const hooks = [
          src.includes("useTenantReferenceQuery") ? "useTenantReferenceQuery" : "",
          src.includes("useTenantListQuery") ? "useTenantListQuery" : "",
          src.includes("useTenantDetailQuery") ? "useTenantDetailQuery" : "",
          src.includes("useTenantReportQuery") ? "useTenantReportQuery" : "",
          src.includes("invalidateTenantQueries") ? "invalidateTenantQueries" : "",
        ].filter(Boolean);
        if (!src.match(/import\s*\{[^}]*useTenantReferenceQuery/)) {
          src = src.replace(
            /import \{([^}]+)\} from "@\/lib\/api\/tenant-query";/,
            (m, existing) => {
              const set = new Set(
                existing.split(",").map((s) => s.trim()).filter(Boolean),
              );
              for (const h of hooks) set.add(h);
              return `import { ${[...set].join(", ")} } from "@/lib/api/tenant-query";`;
            },
          );
          if (!src.includes('from "@/lib/api/tenant-query"')) {
            const hookImport = `import { ${hooks.join(", ")} } from "@/lib/api/tenant-query";\n`;
            const useClientIdx = src.indexOf('"use client"');
            if (useClientIdx !== -1) {
              const lineEnd = src.indexOf("\n", useClientIdx) + 1;
              src = src.slice(0, lineEnd) + hookImport + src.slice(lineEnd);
            } else {
              src = hookImport + src;
            }
          }
        }
      } else {
        const hooks = [
          src.includes("useTenantReferenceQuery") ? "useTenantReferenceQuery" : "",
          src.includes("useTenantListQuery") ? "useTenantListQuery" : "",
          src.includes("useTenantDetailQuery") ? "useTenantDetailQuery" : "",
          src.includes("useTenantReportQuery") ? "useTenantReportQuery" : "",
          src.includes("invalidateTenantQueries") ? "invalidateTenantQueries" : "",
        ].filter(Boolean);
        const hookImport = `import { ${hooks.join(", ")} } from "@/lib/api/tenant-query";\n`;
        const useClientIdx = src.indexOf('"use client"');
        if (useClientIdx !== -1) {
          const lineEnd = src.indexOf("\n", useClientIdx) + 1;
          src = src.slice(0, lineEnd) + hookImport + src.slice(lineEnd);
        } else {
          src = hookImport + src;
        }
      }
    }

    if (src.includes("invalidateTenantQueries") && !src.includes('invalidateTenantQueries')) {
      // already handled
    }

    // Remove unused query option imports if no longer referenced
    for (const opt of Object.keys(TIER_MAP)) {
      if (!src.includes(opt)) {
        src = src.replace(new RegExp(`\\s*${opt},?`, "g"), (m, offset, str) => {
          const line = str.slice(str.lastIndexOf("\n", offset), str.indexOf("\n", offset));
          if (line.includes("import")) return "";
          return m;
        });
        src = src.replace(/import \{\s*,\s*/g, "import { ");
        src = src.replace(/,\s*\} from "@\/lib\/query\/options"/g, ' } from "@/lib/query/options"');
        src = src.replace(/import \{\s*\} from "@\/lib\/query\/options";\n/g, "");
      }
    }

    // Remove useQuery import if unused
    if (!src.match(/\buseQuery\b/) || src.match(/\buseQuery\b/g)?.length === 0) {
      src = src.replace(/import \{([^}]+)\} from "@tanstack\/react-query";/g, (m, imps) => {
        const kept = imps
          .split(",")
          .map((s) => s.trim())
          .filter((s) => s && s !== "useQuery");
        if (kept.length === 0) return "";
        return `import { ${kept.join(", ")} } from "@tanstack/react-query";`;
      });
    } else {
      // still uses useQuery - keep import
    }

    fs.writeFileSync(filePath, src);
    console.log("migrated:", rel);
    return true;
  }
  return false;
}

let count = 0;
for (const f of walk(SRC)) {
  if (migrateFile(f)) count++;
}
console.log(`Done. ${count} files updated.`);
