import { BUILD_LOG_STORAGE_KEY } from "./constants";
import type { BuildLogEntry } from "./types";

function loadRaw(): BuildLogEntry[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(BUILD_LOG_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as BuildLogEntry[]) : [];
  } catch {
    return [];
  }
}

function saveRaw(entries: BuildLogEntry[]): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(BUILD_LOG_STORAGE_KEY, JSON.stringify(entries));
}

export function getBuildLogs(): BuildLogEntry[] {
  return loadRaw().sort(
    (a, b) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
}

export function addBuildLog(
  entry: Omit<BuildLogEntry, "id" | "created_at">
): BuildLogEntry {
  const newEntry: BuildLogEntry = {
    ...entry,
    id: crypto.randomUUID(),
    created_at: new Date().toISOString(),
  };
  const entries = [newEntry, ...loadRaw()];
  saveRaw(entries);
  return newEntry;
}

export function deleteBuildLog(id: string): void {
  saveRaw(loadRaw().filter((e) => e.id !== id));
}
