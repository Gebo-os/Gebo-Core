import type {
  Action,
  AgentRuntimeStatus,
  AutonomyScore,
  ChatResponse,
  CodexStatus,
  EvolutionEvent,
  EvolutionStatus,
  Memory,
  NetworkSettings,
  GeboBootstrap,
  CliStatus,
  IntegrationsStatus,
  KnowledgeStatus,
  LearningCycleResult,
  Reflex,
  ReflexCreatePayload,
  ReflexEvent,
  ScoreActionPayload,
  Status,
  SuggestUpgradePayload,
  UpgradeSuggestion,
  WikiStatus,
} from "./types";

export function getApiUrl(): string {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (typeof window !== "undefined") {
    return `http://${window.location.hostname}:8000`;
  }
  return "http://localhost:8000";
}

/** @deprecated Prefer getApiUrl() for runtime resolution on LAN clients. */
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
  options?: RequestInit & { timeoutMs?: number; signal?: AbortSignal }
): Promise<T> {
  const { timeoutMs = 30000, signal, ...fetchOptions } = options ?? {};
  const res = await fetch(`${getApiUrl()}${path}`, {
    ...fetchOptions,
    signal: signal ?? AbortSignal.timeout(timeoutMs),
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

export async function getHealth(signal?: AbortSignal): Promise<{ ok: boolean; app?: string }> {
  return request("/health", { signal });
}

/** One-call system snapshot — preferred for app startup and consumer integrations. */
export async function getBootstrap(signal?: AbortSignal): Promise<GeboBootstrap> {
  return request("/integrate/bootstrap", { signal });
}

export async function getStatus(signal?: AbortSignal): Promise<Status> {
  return request("/status", { signal });
}

export async function setConsent(allowed: boolean): Promise<{ consent: boolean }> {
  return request("/settings/consent", {
    method: "POST",
    body: JSON.stringify({ allowed }),
  });
}

export async function getNetworkSettings(signal?: AbortSignal): Promise<NetworkSettings> {
  return request("/settings/network", { signal });
}

export async function setNetworkSettings(
  internet_access: boolean
): Promise<NetworkSettings> {
  return request("/settings/network", {
    method: "POST",
    body: JSON.stringify({ internet_access }),
  });
}

export async function getMemories(signal?: AbortSignal): Promise<Memory[]> {
  return request("/memory", { signal });
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

export async function sendChatStream(
  message: string,
  onToken: (token: string) => void,
  signal?: AbortSignal
): Promise<ChatResponse> {
  const res = await fetch(`${getApiUrl()}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    signal: signal ?? AbortSignal.timeout(120000),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(parseErrorDetail(err.detail) || `Request failed: ${res.status}`);
  }

  const reader = res.body?.getReader();
  if (!reader) {
    throw new Error("Streaming not supported");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const payload = JSON.parse(line.slice(6)) as {
        type: string;
        content?: string;
        detail?: string;
        reply?: string;
        recalled_memories?: ChatResponse["recalled_memories"];
        proposed_actions?: ChatResponse["proposed_actions"];
        detected_reflexes?: ChatResponse["detected_reflexes"];
        wiki_sources?: string[];
      };

      if (payload.type === "token" && payload.content) {
        onToken(payload.content);
      } else if (payload.type === "error") {
        throw new Error(payload.detail ?? "Chat stream failed");
      } else if (payload.type === "done") {
        return {
          reply: payload.reply ?? "",
          recalled_memories: payload.recalled_memories ?? [],
          proposed_actions: payload.proposed_actions ?? [],
          detected_reflexes: payload.detected_reflexes ?? [],
          wiki_sources: payload.wiki_sources ?? [],
        };
      }
    }
  }

  throw new Error("Chat stream ended without completion");
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

export async function getAgentRuntimeStatus(): Promise<AgentRuntimeStatus> {
  return request("/agents/runtime/status");
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
  return `${getApiUrl()}/memory/export`;
}

export async function checkBackendOnline(signal?: AbortSignal): Promise<boolean> {
  try {
    await getHealth(signal);
    return true;
  } catch {
    return false;
  }
}

export async function getIntegrationsStatus(): Promise<IntegrationsStatus> {
  return request("/integrations/status");
}

export async function getCliStatus(): Promise<CliStatus> {
  return request("/cli/status");
}

export async function getKnowledgeStatus(): Promise<KnowledgeStatus> {
  return request("/knowledge/status");
}

export async function runLearningCycle(): Promise<LearningCycleResult> {
  return request("/learning/cycle", { method: "POST", timeoutMs: 300000 });
}

export interface WebKnowledgeCollectResult {
  github?: { ingested?: number };
  official_docs?: { ingested?: number };
}

export async function runWebKnowledgeCollect(): Promise<WebKnowledgeCollectResult> {
  return request("/knowledge/web-collect", { method: "POST", timeoutMs: 300000 });
}
