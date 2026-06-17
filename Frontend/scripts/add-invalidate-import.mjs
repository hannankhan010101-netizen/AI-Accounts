import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SRC = path.join(__dirname, "..", "src");

function walk(dir, out = []) {
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name);
    if (fs.statSync(p).isDirectory()) {
      if (name !== "node_modules") walk(p, out);
    } else if (/\.(tsx|ts)$/.test(name)) out.push(p);
  }
  return out;
}

for (const file of walk(SRC)) {
  if (file.endsWith("tenant-query.ts")) continue;
  let src = fs.readFileSync(file, "utf8");
  if (!src.includes("invalidateTenantQueries")) continue;
  if (src.includes('from "@/lib/api/tenant-query"')) {
    if (!src.match(/import \{[^}]*invalidateTenantQueries/)) {
      src = src.replace(
        /import \{([^}]+)\} from "@\/lib\/api\/tenant-query";/,
        (_, imps) => {
          const set = new Set(imps.split(",").map((s) => s.trim()).filter(Boolean));
          set.add("invalidateTenantQueries");
          return `import { ${[...set].join(", ")} } from "@/lib/api/tenant-query";`;
        },
      );
    }
  } else {
    const line = 'import { invalidateTenantQueries } from "@/lib/api/tenant-query";\n';
    const uc = src.indexOf('"use client"');
    if (uc !== -1) {
      const le = src.indexOf("\n", uc) + 1;
      src = src.slice(0, le) + line + src.slice(le);
    } else {
      src = line + src;
    }
  }
  fs.writeFileSync(file, src);
  console.log("import:", path.relative(SRC, file));
}
