/**
 * Gebo Owner NODE — Electron desktop shell.
 * Starts local backend + frontend if needed, opens the Living Console.
 */
const { app, BrowserWindow, shell } = require("electron");
const { spawn } = require("child_process");
const fs = require("fs");
const http = require("http");
const path = require("path");

const FRONTEND_URL = "http://127.0.0.1:3000";
const BACKEND_URL = "http://127.0.0.1:8000";
const NPM = process.platform === "win32" ? "npm.cmd" : "npm";

let ROOT = "";
let BACKEND_DIR = "";
let FRONTEND_DIR = "";
let PYTHON = "";
let UVICORN = "";

/** @type {import('child_process').ChildProcess[]} */
const children = [];
let mainWindow = null;

function resolveGeboRoot() {
  if (process.env.GEBO_ROOT) {
    const envRoot = path.resolve(process.env.GEBO_ROOT);
    if (fs.existsSync(path.join(envRoot, "backend", "app", "main.py"))) {
      return envRoot;
    }
  }

  const devRoot = path.resolve(__dirname, "..");
  if (fs.existsSync(path.join(devRoot, "backend", "app", "main.py"))) {
    return devRoot;
  }

  const exeDir = path.dirname(process.execPath);
  const configPath = path.join(exeDir, "gebo-root.json");
  if (fs.existsSync(configPath)) {
    try {
      const cfg = JSON.parse(fs.readFileSync(configPath, "utf8"));
      if (cfg.root) {
        const configured = path.resolve(cfg.root);
        if (fs.existsSync(path.join(configured, "backend", "app", "main.py"))) {
          return configured;
        }
      }
    } catch {
      /* ignore malformed config */
    }
  }

  const home = app.getPath("home");
  const candidates = [
    path.join(exeDir, "gebo-core-private"),
    path.join(exeDir, "..", "Official Owner NODE", "gebo-core-private"),
    path.join(home, "Desktop", "Official Owner NODE", "gebo-core-private"),
    path.join(home, "Documents", "gebo-core-private"),
  ];

  for (const candidate of candidates) {
    if (fs.existsSync(path.join(candidate, "backend", "app", "main.py"))) {
      return candidate;
    }
  }

  throw new Error(
    "Could not find Gebo Core repo.\n\n" +
      "Place gebo-root.json next to this app with: {\"root\": \"C:\\\\path\\\\to\\\\gebo-core-private\"}\n" +
      "Or set GEBO_ROOT environment variable."
  );
}

function initPaths() {
  ROOT = resolveGeboRoot();
  BACKEND_DIR = path.join(ROOT, "backend");
  FRONTEND_DIR = path.join(ROOT, "frontend");
  PYTHON = path.join(BACKEND_DIR, ".venv", "Scripts", "python.exe");
  UVICORN = path.join(BACKEND_DIR, ".venv", "Scripts", "uvicorn.exe");
}

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

async function bootstrapReady() {
  return ping(`${BACKEND_URL}/integrate/bootstrap`);
}

function killPort8000Windows() {
  const { execSync } = require("child_process");
  try {
    const out = execSync("netstat -ano | findstr :8000 | findstr LISTENING", {
      encoding: "utf8",
      windowsHide: true,
    });
    const pids = new Set();
    for (const line of out.split(/\r?\n/)) {
      const parts = line.trim().split(/\s+/);
      const pid = parts[parts.length - 1];
      if (pid && /^\d+$/.test(pid)) pids.add(pid);
    }
    for (const pid of pids) {
      try {
        execSync(`taskkill /PID ${pid} /F /T`, { stdio: "ignore", windowsHide: true });
      } catch {
        /* ignore */
      }
    }
  } catch {
    /* no listeners */
  }
}

async function ensureBackend() {
  if (await bootstrapReady()) return;

  if (await ping(`${BACKEND_URL}/health`)) {
    if (process.platform === "win32") killPort8000Windows();
    await new Promise((r) => setTimeout(r, 2000));
  }

  if (await bootstrapReady()) return;

  if (!fs.existsSync(PYTHON)) {
    throw new Error(
      `Python venv not found at ${PYTHON}.\nRun: cd backend && python -m venv .venv && pip install -r requirements.txt`
    );
  }

  const backendExe = fs.existsSync(UVICORN) ? UVICORN : PYTHON;
  const backendArgs = fs.existsSync(UVICORN)
    ? ["app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    : ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"];

  spawnHidden(backendExe, backendArgs, BACKEND_DIR);
  await waitFor(`${BACKEND_URL}/integrate/bootstrap`, "Backend bootstrap", 90);
}

async function ensureFrontend() {
  if (await ping(FRONTEND_URL)) return;

  const nextDir = path.join(FRONTEND_DIR, ".next");
  const hasBuild = fs.existsSync(nextDir);

  if (hasBuild) {
    spawnHidden(NPM, ["run", "start", "--", "-H", "127.0.0.1", "-p", "3000"], FRONTEND_DIR);
  } else {
    spawnHidden(NPM, ["run", "dev", "--", "-H", "127.0.0.1", "-p", "3000"], FRONTEND_DIR);
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
        spawn("taskkill", ["/pid", String(child.pid), "/f", "/t"], {
          stdio: "ignore",
          windowsHide: true,
        });
      } else {
        child.kill("SIGTERM");
      }
    } catch {
      /* ignore */
    }
  }
  children.length = 0;
}

function ensureElectronBinaryDev() {
  if (app.isPackaged) return;
  const electronDist = path.join(ROOT, "node_modules", "electron", "dist");
  const exe = path.join(electronDist, "electron.exe");
  const ffmpeg = path.join(electronDist, "ffmpeg.dll");
  if (!fs.existsSync(exe) || !fs.existsSync(ffmpeg)) {
    throw new Error(
      `Electron binary incomplete (missing electron.exe or ffmpeg.dll).\n` +
        `Run: cd desktop && node scripts/ensure-electron.js`
    );
  }
}

app.whenReady().then(async () => {
  try {
    initPaths();
    ensureElectronBinaryDev();
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
