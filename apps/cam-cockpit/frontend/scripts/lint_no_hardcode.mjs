#!/usr/bin/env node
/**
 * Lint no-hardcode — TASK-U012 (BL-UI-1).
 *
 * Falha se algum componente/hook tiver cor hex hardcoded. O DS é SSoT: cores
 * vêm do theme (palette/camTokens). Único arquivo autorizado a conter hex é
 * `src/app/theme.ts` (a fonte dos tokens).
 *
 * Uso: node scripts/lint_no_hardcode.mjs   (exit 1 em violação)
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import { dirname } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SRC = join(__dirname, "..", "src");

// Arquivos autorizados a conter hex (fonte dos tokens).
const ALLOWLIST = [join("app", "theme.ts")];

const HEX = /#[0-9A-Fa-f]{3,8}\b/;

function walk(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    const st = statSync(full);
    if (st.isDirectory()) {
      out.push(...walk(full));
    } else if (/\.(ts|tsx)$/.test(name)) {
      out.push(full);
    }
  }
  return out;
}

function isAllowed(rel) {
  if (ALLOWLIST.some((a) => rel.endsWith(a))) return true;
  // Testes podem usar hex para asserções de cor do DS.
  if (rel.includes("__tests__") || rel.includes(`${"/"}test${"/"}`)) return true;
  return false;
}

const violations = [];
for (const file of walk(SRC)) {
  const rel = relative(join(__dirname, ".."), file);
  if (isAllowed(rel)) continue;
  const lines = readFileSync(file, "utf-8").split("\n");
  lines.forEach((line, i) => {
    if (HEX.test(line)) {
      violations.push(`${rel}:${i + 1}  ${line.trim()}`);
    }
  });
}

if (violations.length > 0) {
  console.error("✗ no-hardcode: cores hex fora do theme detectadas:\n");
  for (const v of violations) console.error("  " + v);
  console.error(`\n${violations.length} violação(ões). Use tokens do theme (palette/camTokens).`);
  process.exit(1);
}

console.log("✓ no-hardcode: nenhuma cor hex hardcoded fora do theme.");
