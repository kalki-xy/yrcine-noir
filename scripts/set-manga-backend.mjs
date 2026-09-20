#!/usr/bin/env node
// Rewrites the built-in default manga backend URL inside a YRcine Noir release HTML file.
//
// The manga section is a thin client that defaults to a hardcoded backend origin
// (https://yra45417.workers.dev). This script swaps that default for your own deployed
// backend so a fresh install works with no in-app configuration.
//
// Usage:
//   node scripts/set-manga-backend.mjs <input.html> <new-backend-url> [output.html]
//
// Example:
//   node scripts/set-manga-backend.mjs YRcine_Noir_VoidVerse-508.html https://yrcine-noir.vercel.app patched.html
//
// Notes:
//   - <new-backend-url> must be an https origin with no trailing slash and no path.
//   - If [output.html] is omitted, the input file is overwritten in place.

import { readFileSync, writeFileSync } from "node:fs"

const OLD_DEFAULT = "https://yra45417.workers.dev"

function fail(msg) {
  console.error(`error: ${msg}`)
  process.exit(1)
}

const [, , inputPath, newUrlRaw, outputPathRaw] = process.argv

if (!inputPath || !newUrlRaw) {
  fail("usage: node scripts/set-manga-backend.mjs <input.html> <new-backend-url> [output.html]")
}

let origin
try {
  const u = new URL(newUrlRaw)
  if (u.protocol !== "https:") fail("backend URL must use https")
  if (u.pathname !== "/" && u.pathname !== "") fail("backend URL must be a bare origin with no path")
  origin = u.origin
} catch {
  fail(`invalid backend URL: ${newUrlRaw}`)
}

const outputPath = outputPathRaw || inputPath

const html = readFileSync(inputPath, "utf8")

const occurrences = html.split(OLD_DEFAULT).length - 1
if (occurrences === 0) {
  fail(
    `default backend URL "${OLD_DEFAULT}" was not found in ${inputPath}. ` +
      "The release format may have changed; inspect the file and update OLD_DEFAULT.",
  )
}

const patched = html.split(OLD_DEFAULT).join(origin)
writeFileSync(outputPath, patched)

console.log(`Replaced ${occurrences} occurrence(s) of ${OLD_DEFAULT}`)
console.log(`  -> ${origin}`)
console.log(`Wrote ${outputPath}`)
