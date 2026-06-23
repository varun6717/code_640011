#!/usr/bin/env node
/* emit_cli.mjs — print the §3.1 config the SPA would POST, from a form-state JSON file.
 *
 * A thin bridge so the offline proof (fixtures/frontend/verify_frontend.py) exercises the
 * REAL emit code (src/emit.js) — the same buildConfig the browser uses — instead of a
 * hand-copied duplicate. Usage:  node scripts/emit_cli.mjs <form.json>  →  config JSON on stdout.
 */
import { readFileSync } from "node:fs";
import { buildConfig } from "../src/emit.js";

const path = process.argv[2];
if (!path) {
  console.error("usage: node scripts/emit_cli.mjs <form-state.json>");
  process.exit(2);
}
const form = JSON.parse(readFileSync(path, "utf8"));
process.stdout.write(JSON.stringify(buildConfig(form), null, 2) + "\n");
