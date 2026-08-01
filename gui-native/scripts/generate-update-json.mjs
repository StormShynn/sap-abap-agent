/**
 * Generates update.json for Tauri 2 updater (SAP ABAP Agent GUI).
 *
 * Usage:
 *   node scripts/generate-update-json.mjs <version> [artifacts-dir] [release-tag]
 *
 * - <version>: e.g. "1.19.0"
 * - [artifacts-dir]: default "artifacts"
 * - [release-tag]: download URL tag — prefer "gui-latest" (rolling) or "gui-v1.19.0"
 *
 * Expected layout (from CI staging):
 *   artifacts/
 *     sap-abap-agent-gui-x86_64-pc-windows-msvc/  (installer + .sig / .nsis.zip + .sig)
 */

import fs from "fs";
import path from "path";

const version = process.argv[2];
const artifactsDir = process.argv[3] || "artifacts";
const releaseTag = process.argv[4] || `gui-v${version}`;

if (!version) {
  console.error(
    "Usage: node generate-update-json.mjs <version> [artifacts-dir] [release-tag]",
  );
  process.exit(1);
}

const REPO = "StormShynn/sap-abap-agent";
const BASE_URL = `https://github.com/${REPO}/releases/download/${releaseTag}`;

const PLATFORM_MAP = {
  "x86_64-pc-windows-msvc": "windows-x86_64",
  "x86_64-unknown-linux-gnu": "linux-x86_64",
  "aarch64-apple-darwin": "darwin-aarch64",
  "x86_64-apple-darwin": "darwin-x86_64",
};

const BUNDLE_EXT_RANK = [
  ".nsis.zip",
  ".msi.zip",
  ".AppImage.tar.gz",
  ".app.tar.gz",
];

function artifactDir(target) {
  return `sap-abap-agent-gui-${target}`;
}

function findBundle(targetDir) {
  if (!fs.existsSync(targetDir)) {
    console.warn(`Warning: Directory not found: ${targetDir}`);
    return null;
  }

  const entries = fs.readdirSync(targetDir, { withFileTypes: true });
  const sigs = new Map();
  const bundles = [];

  for (const entry of entries) {
    if (!entry.isFile()) continue;
    const full = path.join(targetDir, entry.name);
    if (entry.name.endsWith(".sig")) {
      const stem = entry.name.slice(0, -4);
      sigs.set(stem, fs.readFileSync(full, "utf8").trim());
    } else {
      bundles.push({ name: entry.name, path: full });
    }
  }

  const ranked = [...bundles].sort((a, b) => {
    const rank = (name) => {
      const i = BUNDLE_EXT_RANK.findIndex((ext) => name.endsWith(ext));
      return i === -1 ? BUNDLE_EXT_RANK.length : i;
    };
    return rank(a.name) - rank(b.name);
  });

  for (const bundle of ranked) {
    const sig = sigs.get(bundle.name);
    if (sig) {
      return {
        signature: sig,
        url: `${BASE_URL}/${encodeURIComponent(bundle.name)}`,
      };
    }
  }

  const expected = BUNDLE_EXT_RANK.find((ext) =>
    bundles.some((b) => b.name.endsWith(ext)),
  );
  if (expected) {
    throw new Error(`Missing signature for updater artifact in ${targetDir}`);
  }

  // Fallback: signed raw .exe (Tauri sometimes emits .exe.sig without .nsis.zip)
  for (const bundle of ranked) {
    if (!bundle.name.toLowerCase().endsWith(".exe")) continue;
    const sig = sigs.get(bundle.name);
    if (sig) {
      return {
        signature: sig,
        url: `${BASE_URL}/${encodeURIComponent(bundle.name)}`,
      };
    }
  }

  return null;
}

const platforms = {};
const pubDate = new Date().toISOString();

for (const [target, platformKey] of Object.entries(PLATFORM_MAP)) {
  const targetDir = path.join(artifactsDir, artifactDir(target));
  const info = findBundle(targetDir);
  if (info) {
    platforms[platformKey] = info;
  }
}

if (Object.keys(platforms).length === 0) {
  console.error(
    `No signed updater platforms found under ${artifactsDir}. ` +
      `Ensure TAURI_SIGNING_PRIVATE_KEY is set and createUpdaterArtifacts is true.`,
  );
  process.exit(1);
}

const manifest = {
  version,
  notes: `SAP ABAP Agent GUI v${version}`,
  pub_date: pubDate,
  platforms,
};

console.log(JSON.stringify(manifest, null, 2));
