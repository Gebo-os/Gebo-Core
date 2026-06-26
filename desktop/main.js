/**
 * Gebo Owner NODE — Electron desktop shell.
 * Starts local backend + frontend if needed, opens the Living Console.
 */
const { app, BrowserWindow, shell } = require("electron");
const { spawn } = require("child_process");
const fs = require("fs");
const http = require("http");
const path = require("path");

const FRONTEND_URL = "http://localhost:3000";
const BACKEND_URL = "http://127.0.0.1:8000";
const ROOT = path.resolve(__dirname, "..");
const BACKEND_DIR = path.join(ROOT, "backend");
const FRONTEND_DIR = path.join(ROOT, "frontend");
const PYTHON = path.join(BACKEND_DIR, ".venv", "Scripts", "python.exe");
const NPM = process.platform === "win32" ? "npm.cmd" : "npm";

/** @type {import('child_process').ChildProcess[]} */
const children = [];
let mainWindow = null;

function ping(url) {
  return new Promise((resolve) => {
    const req = http.get(url, (res) => {
      res.resume();
      resolve(res.statusCode >= 200 && res.statusCode < 500);
    });
    req.on("error", () => resolve(false));
    req.setTimeout(2000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function waitFor(url, label, attempts = 60) {
  for (let i = 0; i < attempts; i++) {
    if (await ping(url)) return true;
    await new Promise((r) => setTimeout(r, 1000));
  }
  throw new Error(`${label} did not start at ${url}`);
}

function track(child) {
  children.push(child);
  child.on("exit", () => {
    const idx = children.indexOf(child);
    if (idx >= 0) children.splice(idx, 1);
  });
}

function spawnHidden(cmd, args, cwd) {
  const child = spawn(cmd, args, {
    cwd,
    stdio: "ignore",
    detached: false,
    windowsHide: true,
    shell: false,
  });
  track(child);
  return child;
}

async function ensureBackend() {
  if (await ping(`${BACKEND_URL}/health`)) return;

  if (!fs.existsSync(PYTHON)) {
    throw new Error(
      `Python venv not found at ${PYTHON}. Run: cd backend; python -m venv .venv; pip install -r requirements.txt`
    );
  }

  spawnHidden(PYTHON, ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"], BACKEND_DIR);
  await waitFor(`${BACKEND_URL}/health`, "Backend");
}

async function ensureFrontend() {
  if (await ping(FRONTEND_URL)) return;

  const nextDir = path.join(FRONTEND_DIR, ".next");
  const hasBuild = fs.existsSync(nextDir);

  if (hasBuild) {
    spawnHidden(NPM, ["run", "start", "--", "-p", "3000"], FRONTEND_DIR);
  } else {
    spawnHidden(NPM, ["run", "dev", "--", "-p", "3000"], FRONTEND_DIR);
  }
  await waitFor(FRONTEND_URL, "Frontend", 90);
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 960,
    minHeight: 640,
    backgroundColor: "#050505",
    title: "Gebo Owner NODE",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadURL(FRONTEND_URL);
  mainWindow.on("closed", () => {
    mainWindow = null;
  });

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith("http://127.0.0.1:8000") || url.startsWith("http://localhost:8000")) {
      shell.openExternal(url);
    }
    return { action: "deny" };
  });
}

function shutdownChildren() {
  for (const child of children) {
    try {
      if (process.platform === "win32") {
        spawn("taskkill", ["/pid", String(child.pid), "/f", "/t"], { stdio: "ignore", windowsHide: true });
      } else {
        child.kill("SIGTERM");
      }
    } catch {
      /* ignore */
    }
  }
  children.length = 0;
}

app.whenReady().then(async () => {
  try {
    await ensureBackend();
    await ensureFrontend();
    createWindow();
  } catch (err) {
    const { dialog } = require("electron");
    dialog.showErrorBox(
      "Gebo Owner NODE — startup failed",
      `${err.message}\n\nEnsure Ollama is running and dependencies are installed. See README.md.`
    );
    app.quit();
  }
});

app.on("window-all-closed", () => {
  shutdownChildren();
  if (process.platform !== "darwin") app.quit();
});

app.on("before-quit", () => shutdownChildren());

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
