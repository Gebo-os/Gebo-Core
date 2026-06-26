import type {
  Action,
  ChatResponse,
  Memory,
  Status,
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
