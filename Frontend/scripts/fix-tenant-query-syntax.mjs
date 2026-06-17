/**
 * Fix orphaned closing parens left by migrate-tenant-queries.mjs
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SRC = path.join(__dirname, "..", "src");

function walk(dir, out = []) {
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name);
    const st = fs.statSync(p);
    if (st.isDirectory()) {
      if (name === "node_modules") continue;
      walk(p, out);
    } else if (/\.(tsx|ts)$/.test(name)) {
      out.push(p);
    }
  }
  return out;
}

for (const file of walk(SRC)) {
  let src = fs.readFileSync(file, "utf8");
  const orig = src;

  // useTenantXQuery(...)\n  );  -> useTenantXQuery(...);
  src = src.replace(
    /(useTenant(?:Reference|List|Detail|Report)Query\([\s\S]*?\))\s*\n\s*\);/g,
    "$1;",
  );

  // Fix double-brace corruption: { page: 1, { pageSize: N } -> { page: 1, pageSize: N }
  src = src.replace(/\{\s*page:\s*(\d+),\s*\{\s*pageSize:/g, "{ page: $1, pageSize:");
  src = src.replace(/listUsers\(\{\s*userId:\s*([^,]+),\s*\{\s*page:/g, "listUsers({ userId: $1, page:");

  if (src !== orig) {
    fs.writeFileSync(file, src);
    console.log("fixed:", path.relative(SRC, file));
  }
}
