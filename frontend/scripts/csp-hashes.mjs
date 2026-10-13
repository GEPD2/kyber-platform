// Computes a SHA-256 hash for every inline <script> in the static export and
// writes an nginx `map` that sets $csp_script, so the CSP can allow exactly
// these scripts instead of 'unsafe-inline'. Node standard library only.
//
// Usage: node scripts/csp-hashes.mjs <out dir> <output .conf>
import { createHash } from "node:crypto";
import { readdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const [outDir = "out", target = "csp_script.conf"] = process.argv.slice(2);

function htmlFiles(dir) {
  return readdirSync(dir).flatMap((name) => {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) return htmlFiles(p);
    return name.endsWith(".html") ? [p] : [];
  });
}

// Inline scripts only: a <script> with a src attribute is covered by 'self'.
const INLINE = /<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g;
const hashes = new Set();
const files = htmlFiles(outDir);
for (const file of files) {
  for (const m of readFileSync(file, "utf8").matchAll(INLINE)) {
    if (m[1].length === 0) continue;
    hashes.add(`'sha256-${createHash("sha256").update(m[1], "utf8").digest("base64")}'`);
  }
}
if (files.length === 0) throw new Error(`no HTML files under ${outDir}`);

const value = ["'self'", ...[...hashes].sort()].join(" ");
writeFileSync(
  target,
  "# Generated at build time by frontend/scripts/csp-hashes.mjs. Do not edit.\n" +
    `map "" $csp_script {\n    default "${value}";\n}\n`,
);
console.log(`csp-hashes: ${hashes.size} inline script hashes from ${files.length} pages -> ${target}`);
