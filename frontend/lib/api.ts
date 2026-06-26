import type {
  Action,
  AutonomyScore,
  ChatResponse,
  CodexStatus,
  EvolutionEvent,
  EvolutionStatus,
  Memory,
  Reflex,
  ReflexCreatePayload,
  ReflexEvent,
  ScoreActionPayload,
  Status,
  SuggestUpgradePayload,
  UpgradeSuggestion,
  WikiStatus,
} from "./types";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function parseErrorDetail(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (typeof d === "object" && d && "msg" in d ? String(d.msg) : String(d)))
      .join(", ");
  }
  return "Request failed";
}

async function request<T>(
  path: string,
  options?: RequestInit & { timeoutMs?: number }
): Promise<T> {
  const { timeoutMs = 30000, ...fetchOptions } = options ?? {};
  const res = await fetch(`${API_URL}${path}`, {
    ...fetchOptions,
    signal: AbortSignal.timeout(timeoutMs),
    headers: {
      "Content-Type": "application/json",
      ...fetchOptions.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(parseErrorDetail(err.detail) || `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function getHealth(): Promise<{ ok: boolean; app?: string }> {
  return request("/health");
}

export async function getStatus(): Promise<Status> {
  return request("/status");
}

export async function setConsent(allowed: boolean): Promise<{ consent: boolean }> {
  return request("/settings/consent", {
    method: "POST",
    body: JSON.stringify({ allowed }),
  });
}

export async function getMemories(): Promise<Memory[]> {
  return request("/memory");
}

export async function saveMemory(
  memory_type: string,
  content: string
): Promise<{ id: number; ok: boolean }> {
  return request("/memory", {
    method: "POST",
    body: JSON.stringify({ memory_type, content }),
  });
}

export async function sendChat(message: string): Promise<ChatResponse> {
  return request("/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
    timeoutMs: 120000,
  });
}

export async function getActions(): Promise<Action[]> {
  return request("/actions");
}

export async function approveAction(id: number): Promise<void> {
  await request(`/actions/${id}/approve`, { method: "POST" });
}

export async function rejectAction(id: number): Promise<void> {
  await request(`/actions/${id}/reject`, { method: "POST" });
}

export async function runAction(id: number): Promise<unknown> {
  return request(`/actions/${id}/run`, { method: "POST" });
}

export async function getCodexStatus(): Promise<CodexStatus> {
  return request("/codex/status");
}

export async function getWikiStatus(): Promise<WikiStatus> {
  return request("/wiki/status");
}

export async function getReflexes(): Promise<Reflex[]> {
  return request("/reflexes");
}

export async function createReflex(body: ReflexCreatePayload): Promise<Reflex> {
  return request("/reflexes", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function toggleReflex(id: number): Promise<Reflex> {
  return request(`/reflexes/${id}/toggle`, { method: "POST" });
}

export async function getReflexEvents(): Promise<ReflexEvent[]> {
  return request("/reflex-events");
}

export async function getEvolutionStatus(): Promise<EvolutionStatus> {
  return request("/evolution/status");
}

export async function getEvolutionEvents(): Promise<EvolutionEvent[]> {
  return request("/evolution/events");
}

export async function getEvolutionScores(): Promise<AutonomyScore[]> {
  return request("/evolution/scores");
}

export async function getEvolutionUpgrades(): Promise<UpgradeSuggestion[]> {
  return request("/evolution/upgrades");
}

export async function scoreAction(body: ScoreActionPayload): Promise<unknown> {
  return request("/evolution/score-action", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function suggestUpgrade(
  body: SuggestUpgradePayload
): Promise<unknown> {
  return request("/evolution/suggest-upgrade", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function approveUpgrade(id: number): Promise<unknown> {
  return request(`/evolution/upgrades/${id}/approve`, { method: "POST" });
}

export async function rejectUpgrade(id: number): Promise<unknown> {
  return request(`/evolution/upgrades/${id}/reject`, { method: "POST" });
}

export function getExportUrl(): string {
  return `${API_URL}/memory/export`;
}

export async function checkBackendOnline(): Promise<boolean> {
  try {
    await getHealth();
    return true;
  } catch {
    return false;
  }
}
