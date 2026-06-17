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
  let src = fs.readFileSync(file, "utf8");
  const orig = src;
  src = src.replace(/\(\),\s*\{\s*\)\s*=>/g, "() =>");
  src = src.replace(/,\s*\],\s*\(\),\s*\{\s*\)\s*=>/g, "], () =>");
  if (src !== orig) {
    fs.writeFileSync(file, src);
    console.log("fixed:", path.relative(SRC, file));
  }
}
