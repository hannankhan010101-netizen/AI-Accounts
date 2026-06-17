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

  src = src.replace(/\}\)\s*\}\);/g, "}));");
  src = src.replace(/\(\)\s*\}\);/g, "());");

  // enabled:/staleTime: without wrapping braces after useTenant*Query
  src = src.replace(
    /(useTenant(?:Reference|List|Detail|Report)Query\([\s\S]*?,\s*\(\)\s*=>\s*[\s\S]*?),\s*\n\s*(enabled:|staleTime:)/g,
    "$1,\n    { $2",
  );
  src = src.replace(
    /(useTenant(?:Reference|List|Detail|Report)Query\([\s\S]*?,\s*\(\)\s*=>\s*[^,\n]+),\s*(enabled:|staleTime:)/g,
    "$1, { $2",
  );
  // close options object when line ends with `});` after enabled expression
  src = src.replace(
    /(\{\s*enabled:[^}]+\})\s*\);/g,
    "$1);",
  );

  if (src !== orig) {
    fs.writeFileSync(file, src);
    console.log("fixed:", path.relative(SRC, file));
  }
}
