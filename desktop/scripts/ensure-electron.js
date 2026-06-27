#!/usr/bin/env node
/**
 * Ensures Electron binary + ffmpeg.dll are present on Windows.
 * Fixes partial/corrupt npm postinstall extractions.
 */
const { downloadArtifact } = require("@electron/get");
const extract = require("extract-zip");
const fs = require("fs");
const path = require("path");

const electronDir = path.join(__dirname, "..", "node_modules", "electron");
const distDir = path.join(electronDir, "dist");
const { version } = require(path.join(electronDir, "package.json"));

function platformPath() {
  if (process.platform === "win32") return "electron.exe";
  if (process.platform === "darwin") {
    return "Electron.app/Contents/MacOS/Electron";
  }
  return "electron";
}

function isComplete() {
  const exe = path.join(distDir, platformPath());
  const ffmpeg =
    process.platform === "win32"
      ? path.join(distDir, "ffmpeg.dll")
      : path.join(distDir, "libffmpeg.so");
  return fs.existsSync(exe) && (process.platform !== "win32" || fs.existsSync(ffmpeg));
}

async function main() {
  if (process.env.ELECTRON_SKIP_BINARY_DOWNLOAD === "1") {
    return;
  }
  if (isComplete()) {
    return;
  }

  fs.mkdirSync(distDir, { recursive: true });
  const zipPath = await downloadArtifact({
    version,
    artifactName: "electron",
    force: process.env.ELECTRON_FORCE_DOWNLOAD === "1",
    platform: process.platform,
    arch: process.arch,
  });

  // Clear partial extract (e.g. locales-only folder)
  for (const entry of fs.readdirSync(distDir)) {
    fs.rmSync(path.join(distDir, entry), { recursive: true, force: true });
  }

  await extract(zipPath, { dir: distDir });
  fs.writeFileSync(path.join(electronDir, "path.txt"), platformPath(), "utf8");
  fs.writeFileSync(path.join(distDir, "version"), `v${version}`, "utf8");

  if (!isComplete()) {
    throw new Error(
      `Electron install incomplete — missing ${platformPath()} or ffmpeg in ${distDir}`
    );
  }
  console.log(`Electron ${version} ready (${distDir})`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
