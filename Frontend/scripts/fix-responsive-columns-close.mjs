import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function walk(dir, out = []) {
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, ent.name);
    if (ent.isDirectory() && ent.name !== "node_modules") walk(p, out);
    else if (ent.isFile() && ent.name.endsWith(".tsx")) out.push(p);
  }
  return out;
}

for (const f of walk(path.join(root, "src"))) {
  let s = fs.readFileSync(f, "utf8");
  if (!s.includes("responsiveListColumns")) continue;
  const fixed = s.replace(
    /(const columns = responsiveListColumns<[^>]+>\(\[[\s\S]*?)\n  \];/g,
    "$1\n  ]);",
  );
  if (fixed !== s) {
    fs.writeFileSync(f, fixed);
    console.log("fixed", path.relative(root, f));
  }
}
