import { createHash } from "node:crypto";
import type { MappingRule } from "../types/pipeline.js";
import type { EntityModule } from "../types/pipeline.js";
import { FASTACCOUNTS_PRESETS, getTargetSchema } from "../domain/target-schemas.js";

export interface MappingSuggestion {
  sourceField: string;
  targetField: string;
  confidence: number;
  reason: string;
}

function normalizeKey(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]/g, "");
}

function similarity(a: string, b: string): number {
  const na = normalizeKey(a);
  const nb = normalizeKey(b);
  if (na === nb) return 1;
  if (na.includes(nb) || nb.includes(na)) return 0.85;
  const longer = na.length > nb.length ? na : nb;
  const shorter = na.length > nb.length ? nb : na;
  let matches = 0;
  for (const ch of shorter) {
    if (longer.includes(ch)) matches++;
  }
  return matches / longer.length;
}

/** Rule-based + preset field matching (AI hook optional). */
export function suggestMappings(
  module: EntityModule,
  sourceFields: string[],
  sourceSystem = "generic",
): MappingSuggestion[] {
  const targetFields = getTargetSchema(module);
  const preset =
    sourceSystem === "fastaccounts" ? FASTACCOUNTS_PRESETS[module] ?? {} : {};
  const suggestions: MappingSuggestion[] = [];
  const usedTargets = new Set<string>();

  for (const sourceField of sourceFields) {
    if (preset[sourceField]) {
      suggestions.push({
        sourceField,
        targetField: preset[sourceField],
        confidence: 0.98,
        reason: "FastAccounts preset",
      });
      usedTargets.add(preset[sourceField]);
      continue;
    }

    let best: MappingSuggestion | null = null;
    for (const target of targetFields) {
      if (usedTargets.has(target.field)) continue;
      const score = Math.max(
        similarity(sourceField, target.field),
        similarity(sourceField, target.label),
      );
      if (score >= 0.6 && (!best || score > best.confidence)) {
        best = {
          sourceField,
          targetField: target.field,
          confidence: score,
          reason: score >= 0.95 ? "Exact match" : "Fuzzy match",
        };
      }
    }
    if (best) {
      suggestions.push(best);
      usedTargets.add(best.targetField);
    }
  }

  return suggestions.sort((a, b) => b.confidence - a.confidence);
}

export function applyMapping(
  sourceRow: Record<string, unknown>,
  rules: MappingRule[],
): Record<string, unknown> {
  const out: Record<string, unknown> = {};

  for (const rule of rules) {
    let value: unknown = sourceRow[rule.sourceField];

    if ((value === undefined || value === null || value === "") && rule.defaultValue !== undefined) {
      value = rule.defaultValue;
    }

    if (rule.transform) {
      value = applyTransform(value, rule.transform, sourceRow);
    }

    if (value !== undefined && value !== null && value !== "") {
      out[rule.targetField] = value;
    }
  }

  return out;
}

function applyTransform(
  value: unknown,
  transform: string,
  row: Record<string, unknown>,
): unknown {
  switch (transform) {
    case "trim":
      return String(value ?? "").trim();
    case "uppercase":
      return String(value ?? "").toUpperCase();
    case "lowercase":
      return String(value ?? "").toLowerCase();
    case "stripCommas":
      return String(value ?? "").replace(/,/g, "");
    case "coalesceContactName": {
      const business = row["Business Name"] ?? row["businessName"];
      return business || value;
    }
    case "entitySideTag":
      return value;
    default:
      return value;
  }
}

export function rulesFromSuggestions(
  suggestions: MappingSuggestion[],
  requiredTargets: string[],
): MappingRule[] {
  const rules: MappingRule[] = suggestions.map((s) => ({
    sourceField: s.sourceField,
    targetField: s.targetField,
    isRequired: requiredTargets.includes(s.targetField),
  }));

  for (const field of requiredTargets) {
    if (!rules.some((r) => r.targetField === field)) {
      rules.push({ sourceField: "", targetField: field, isRequired: true });
    }
  }

  return rules;
}

export function mappingFingerprint(rules: MappingRule[]): string {
  const payload = rules
    .map((r) => `${r.sourceField}->${r.targetField}:${r.transform ?? ""}`)
    .sort()
    .join("|");
  return createHash("sha256").update(payload).digest("hex").slice(0, 16);
}
