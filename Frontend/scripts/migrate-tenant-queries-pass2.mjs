/**
 * Pass 2: migrate remaining useQuery + *QueryOptions patterns.
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SRC = path.join(__dirname, "..", "src");

const OPT_TO_HOOK = {
  referenceQueryOptions: "useTenantReferenceQuery",
  listQueryOptions: "useTenantListQuery",
  detailQueryOptions: "useTenantDetailQuery",
  reportQueryOptions: "useTenantReportQuery",
  paginatedListQueryOptions: "useTenantListQuery",
};

function walk(dir, out = []) {
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name);
    if (fs.statSync(p).isDirectory()) {
      if (name !== "node_modules") walk(p, out);
    } else if (/\.(tsx|ts)$/.test(name) && !name.endsWith(".test.ts")) {
      out.push(p);
    }
  }
  return out;
}

function extractBalanced(source, startIdx, open, close) {
  let depth = 0;
  for (let i = startIdx; i < source.length; i++) {
    if (source[i] === open) depth++;
    else if (source[i] === close) {
      depth--;
      if (depth === 0) return source.slice(startIdx, i + 1);
    }
  }
  return null;
}

function migrateOptionsBlock(src, optName, hookName) {
  let changed = false;
  let idx = 0;
  const token = `${optName}(`;
  while ((idx = src.indexOf(token, idx)) !== -1) {
    const before = src.slice(Math.max(0, idx - 30), idx);
    if (!before.includes("useQuery")) {
      idx += token.length;
      continue;
    }
    const useQueryIdx = src.lastIndexOf("useQuery", idx);
    const parenOpen = src.indexOf("(", useQueryIdx);
    const optOpen = src.indexOf("(", idx);
    const innerObj = extractBalanced(src, src.indexOf("{", optOpen), "{", "}");
    if (!innerObj) {
      idx += token.length;
      continue;
    }
    const inner = innerObj.slice(1, -1);
    const qk = inner.match(/queryKey:\s*(\[[\s\S]*?\])\s*,/);
    const qfStart = inner.indexOf("queryFn:");
    if (!qk || qfStart === -1) {
      idx += token.length;
      continue;
    }
    let qfEnd = qfStart + "queryFn:".length;
    while (qfEnd < inner.length && /\s/.test(inner[qfEnd])) qfEnd++;
    if (inner[qfEnd] === "(") {
      const fnBody = extractBalanced(inner, qfEnd, "(", ")");
      if (!fnBody) {
        idx += token.length;
        continue;
      }
      var queryFn = inner.slice(qfStart + "queryFn:".length).trim();
      if (queryFn.endsWith(",")) queryFn = queryFn.slice(0, -1).trim();
    } else {
      idx += token.length;
      continue;
    }
    const afterFn = inner.slice(qfStart + queryFn.length + "queryFn:".length).replace(/^,\s*/, "");
    const rest = afterFn.replace(/,\s*$/, "").trim();
    const keyParts = qk[1].slice(1, -1).trim();
    const restOpt = rest ? `, { ${rest} }` : "";
    const replacement = `${hookName}([${keyParts}], ${queryFn}${restOpt})`;
    const endOpt = optOpen + 1 + innerObj.length + 1; // close opt paren
    const endUse = endOpt + 1; // close useQuery paren
    if (src[endOpt] !== ")" || src[endUse] !== ")") {
      idx += token.length;
      continue;
    }
    src = src.slice(0, useQueryIdx) + replacement + src.slice(endUse + 1);
    changed = true;
    idx = useQueryIdx + replacement.length;
  }
  return { src, changed };
}

function ensureImports(src) {
  const hooks = [];
  for (const h of [
    "useTenantReferenceQuery",
    "useTenantListQuery",
    "useTenantDetailQuery",
    "useTenantReportQuery",
    "invalidateTenantQueries",
  ]) {
    if (src.includes(h)) hooks.push(h);
  }
  if (hooks.length === 0) return src;

  const importLine = `import { ${hooks.join(", ")} } from "@/lib/api/tenant-query";`;
  if (src.includes('from "@/lib/api/tenant-query"')) {
    src = src.replace(
      /import \{([^}]+)\} from "@\/lib\/api\/tenant-query";/,
      (_, imps) => {
        const set = new Set(imps.split(",").map((s) => s.trim()).filter(Boolean));
        hooks.forEach((h) => set.add(h));
        return `import { ${[...set].join(", ")} } from "@/lib/api/tenant-query";`;
      },
    );
  } else {
    const uc = src.indexOf('"use client"');
    if (uc !== -1) {
      const le = src.indexOf("\n", uc) + 1;
      src = src.slice(0, le) + importLine + "\n\n" + src.slice(le);
    } else {
      src = importLine + "\n" + src;
    }
  }

  for (const opt of Object.keys(OPT_TO_HOOK)) {
    if (!src.includes(opt)) {
      src = src.replace(new RegExp(`\\s*${opt},?`, "g"), (m, off, s) => {
        const lineStart = s.lastIndexOf("\n", off);
        const line = s.slice(lineStart, off + m.length);
        return line.includes("import") ? "" : m;
      });
      src = src.replace(/import \{\s*,\s*/g, "import { ");
      src = src.replace(/,\s*\} from "@\/lib\/query\/options"/g, " } from \"@/lib/query/options\"");
      src = src.replace(/import \{\s*\} from "@\/lib\/query\/options";\n/g, "");
    }
  }

  if (!/\buseQuery\b/.test(src)) {
    src = src.replace(/import \{([^}]+)\} from "@tanstack\/react-query";/g, (m, imps) => {
      const kept = imps.split(",").map((s) => s.trim()).filter((s) => s && s !== "useQuery");
      return kept.length ? `import { ${kept.join(", ")} } from "@tanstack/react-query";` : "";
    });
  }
  return src;
}

function migrateRawUseQuery(src, filePath) {
  const isReport = filePath.includes(`${path.sep}reports${path.sep}`);
  const hook = isReport ? "useTenantReportQuery" : "useTenantListQuery";
  let changed = false;
  let idx = 0;
  while ((idx = src.indexOf("useQuery({", idx)) !== -1) {
    if (src.slice(idx - 20, idx).includes("useTenant")) {
      idx += 10;
      continue;
    }
    const objStart = idx + "useQuery(".length;
    const obj = extractBalanced(src, objStart, "{", "}");
    if (!obj) break;
    const inner = obj.slice(1, -1);
    const qk = inner.match(/queryKey:\s*(\[[\s\S]*?\])\s*,/);
    const qfStart = inner.indexOf("queryFn:");
    if (!qk || qfStart === -1) {
      idx += 10;
      continue;
    }
    const fnPart = inner.slice(qfStart + "queryFn:".length);
    let queryFn;
    const trimmed = fnPart.trimStart();
    if (trimmed.startsWith("(")) {
      const fnBody = extractBalanced(fnPart, fnPart.indexOf("("), "(", ")");
      queryFn = fnPart.slice(0, fnPart.indexOf("(") + fnBody.length).trim();
    } else if (trimmed.startsWith("async")) {
      const asyncIdx = fnPart.indexOf("async");
      const p = fnPart.indexOf("(", asyncIdx);
      const fnBody = extractBalanced(fnPart, p, "(", ")");
      queryFn = fnPart.slice(0, p + fnBody.length).trim();
    } else {
      idx += 10;
      continue;
    }
    const afterFn = inner.slice(qfStart + "queryFn:".length + queryFn.length).replace(/^,\s*/, "");
    const rest = afterFn.replace(/,\s*$/, "").trim();
    const keyParts = qk[1].slice(1, -1).trim();
    const restOpt = rest ? `, { ${rest} }` : "";
    const replacement = `${hook}([${keyParts}], ${queryFn}${restOpt})`;
    const end = objStart + obj.length + 1;
    src = src.slice(0, idx) + replacement + src.slice(end);
    changed = true;
    idx += replacement.length;
  }
  return { src, changed };
}

let count = 0;
for (const file of walk(SRC)) {
  if (file.endsWith("tenant-query.ts")) continue;
  let src = fs.readFileSync(file, "utf8");
  if (!src.includes("useQuery")) continue;
  let changed = false;
  for (const [opt, hook] of Object.entries(OPT_TO_HOOK)) {
    const r = migrateOptionsBlock(src, opt, hook);
    src = r.src;
    changed = changed || r.changed;
  }
  const r2 = migrateRawUseQuery(src, file);
  src = r2.src;
  changed = changed || r2.changed;
  if (changed) {
    src = ensureImports(src);
    fs.writeFileSync(file, src);
    console.log("migrated:", path.relative(SRC, file));
    count++;
  }
}
console.log(`Pass 2 done: ${count} files`);
