#!/usr/bin/env node
/**
 * Flags design-system drift in app routes (alert(), raw Tailwind colors).
 * Exit code 1 when violations are found.
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(fileURLToPath(new URL(".", import.meta.url)), "..", "src", "app");

const RULES = [
  { id: "alert()", pattern: /\balert\s*\(/g },
  { id: "bg-brand-600 text-white", pattern: /bg-brand-600\s+text-white/g },
  { id: "text-red-*", pattern: /text-red-\d+/g },
];

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    const st = statSync(full);
    if (st.isDirectory()) walk(full, out);
    else if (/\.(tsx|ts|jsx|js)$/.test(name)) out.push(full);
  }
  return out;
}

const violations = [];

for (const file of walk(ROOT)) {
  const text = readFileSync(file, "utf8");
  const lines = text.split(/\r?\n/);
  for (const rule of RULES) {
    rule.pattern.lastIndex = 0;
    for (let i = 0; i < lines.length; i++) {
      if (rule.pattern.test(lines[i])) {
        violations.push({
          file: relative(join(fileURLToPath(new URL(".", import.meta.url)), ".."), file),
          line: i + 1,
          rule: rule.id,
          snippet: lines[i].trim().slice(0, 120),
        });
      }
      rule.pattern.lastIndex = 0;
    }
  }
}

if (violations.length === 0) {
  console.log("check-design: no violations in src/app");
  process.exit(0);
}

console.error(`check-design: ${violations.length} violation(s):\n`);
for (const v of violations) {
  console.error(`  ${v.file}:${v.line} [${v.rule}] ${v.snippet}`);
}
process.exit(1);
