/**
 * Generates update.json for Tauri 2 updater (SAP ABAP Agent GUI).
 *
 * Usage:
 *   node scripts/generate-update-json.mjs <version> [artifacts-dir] [release-tag]
 *
 * - <version>: e.g. "1.22.7"
 * - [artifacts-dir]: default "artifacts"
 * - [release-tag]: download URL tag — prefer "gui-latest" (rolling) or "gui-v1.22.7"
 *
 * Expected layout (from CI staging):
 *   artifacts/
 *     sap-abap-agent-gui-x86_64-pc-windows-msvc/  (installer + .sig / .nsis.zip + .sig)
 *
 * Artifact ranking (deterministic — first match with a sibling .sig wins):
 *   1. *.nsis.zip   (preferred Tauri updater archive)
 *   2. *.msi.zip
 *   3. *.AppImage.tar.gz / *.app.tar.gz
 *   4. *-setup.exe  (fallback when Tauri emits .exe.sig without .nsis.zip)
 *
 * MSI installers are never selected for the in-app updater URL (admin / Error 1925).
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

/** Lower rank index = higher preference. */
const BUNDLE_EXT_RANK = [
  ".nsis.zip",
  ".msi.zip",
  ".AppImage.tar.gz",
  ".app.tar.gz",
];

function artifactDir(target) {
  return `sap-abap-agent-gui-${target}`;
}

function rankOf(name) {
  const lower = name.toLowerCase();
  const i = BUNDLE_EXT_RANK.findIndex((ext) => lower.endsWith(ext));
  if (i !== -1) return i;
  // Signed NSIS installer fallback (not MSI — per-machine / elevation).
  if (lower.endsWith("-setup.exe") || lower.endsWith("_x64-setup.exe")) {
    return BUNDLE_EXT_RANK.length;
  }
  if (lower.endsWith(".exe") && !lower.endsWith(".msi")) {
    // Prefer *-setup.exe shape; demote generic .exe slightly
    return BUNDLE_EXT_RANK.length + 1;
  }
  return Number.POSITIVE_INFINITY;
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

  const ranked = [...bundles]
    .filter((b) => Number.isFinite(rankOf(b.name)))
    .sort((a, b) => {
      const dr = rankOf(a.name) - rankOf(b.name);
      if (dr !== 0) return dr;
      // Tie-break: stable lexicographic name
      return a.name.localeCompare(b.name);
    });

  for (const bundle of ranked) {
    const sig = sigs.get(bundle.name);
    if (!sig) continue;
    const kind =
      rankOf(bundle.name) < BUNDLE_EXT_RANK.length
        ? "archive"
        : "installer-exe-fallback";
    console.error(
      `[generate-update-json] selected ${bundle.name} (${kind}) for ${path.basename(targetDir)}`,
    );
    if (kind === "installer-exe-fallback") {
      console.error(
        "[generate-update-json] NOTE: no signed .nsis.zip — using signed NSIS .exe. " +
          "In-app updater supports this path; prefer createUpdaterArtifacts + signing so .nsis.zip appears next release.",
      );
    }
    return {
      signature: sig,
      url: `${BASE_URL}/${encodeURIComponent(bundle.name)}`,
      artifact: bundle.name,
      kind,
    };
  }

  const expectedArchive = BUNDLE_EXT_RANK.find((ext) =>
    bundles.some((b) => b.name.toLowerCase().endsWith(ext)),
  );
  if (expectedArchive) {
    throw new Error(
      `Found ${expectedArchive} under ${targetDir} but missing sibling .sig`,
    );
  }

  return null;
}

const platforms = {};
const pubDate = new Date().toISOString();
const selectionLog = [];

for (const [target, platformKey] of Object.entries(PLATFORM_MAP)) {
  const targetDir = path.join(artifactsDir, artifactDir(target));
  const info = findBundle(targetDir);
  if (info) {
    selectionLog.push(`${platformKey}=${info.artifact} (${info.kind})`);
    platforms[platformKey] = {
      signature: info.signature,
      url: info.url,
    };
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

// Human-readable selection summary on stderr (stdout is JSON only).
console.error(`[generate-update-json] platforms: ${selectionLog.join("; ")}`);

console.log(JSON.stringify(manifest, null, 2));
