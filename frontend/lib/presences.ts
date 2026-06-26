import { PRESENCE_DEFINITIONS } from "./constants";
import type { Memory, Presence, PresenceStatus, Status } from "./types";

function deriveStatus(
  presenceId: string,
  status: Status | null,
  memories: Memory[]
): PresenceStatus {
  if (!status) return "Resting";

  const related = memories.filter((m) => {
    const type = m.memory_type.toLowerCase();
    const content = m.content.toLowerCase();
    return (
      content.includes(presenceId) ||
      (presenceId === "gebo" && (type === "core" || type === "system")) ||
      (presenceId === "lockin" && type === "project") ||
      (presenceId === "dream" && type === "presence") ||
      (presenceId === "mya" && type === "preference") ||
      (presenceId === "slatt" && type === "system") ||
      (presenceId === "sleep" && type === "build_log") ||
      (presenceId === "dark" && type === "core")
    );
  });

  if (presenceId === "gebo") {
    if (status.message_count > 0) return "Awake";
    if (status.memory_count > 0) return "Quiet";
    return "Needs Memory";
  }

  if (related.length >= 3) return "Awake";
  if (related.length >= 1) return "Quiet";
  if (status.memory_count === 0) return "Needs Memory";
  return "Resting";
}

function lastContribution(
  presenceId: string,
  memories: Memory[]
): string {
  const match = memories.find((m) => {
    const c = m.content.toLowerCase();
    const n = presenceId.toLowerCase();
    return c.includes(n) || m.memory_type === presenceId;
  });
  if (match) {
    const preview =
      match.content.length > 80
        ? match.content.slice(0, 80) + "…"
        : match.content;
    return preview;
  }
  return "No recorded contribution yet";
}

export function buildPresences(
  status: Status | null,
  memories: Memory[]
): Presence[] {
  return PRESENCE_DEFINITIONS.map((def) => ({
    ...def,
    status: deriveStatus(def.id, status, memories),
    lastContribution: lastContribution(def.id, memories),
  }));
}

export function getActivePresence(presences: Presence[]): Presence {
  const awake = presences.find((p) => p.primary && p.status === "Awake");
  if (awake) return awake;
  const gebo = presences.find((p) => p.primary);
  return gebo ?? presences[0];
}

export function deriveGeboStatus(
  online: boolean,
  status: Status | null
): "Awake" | "Resting" | "Needs Setup" {
  if (!online) return "Resting";
  if (!status) return "Needs Setup";
  if (!status.consent && status.memory_count === 0 && status.message_count === 0) {
    return "Needs Setup";
  }
  return "Awake";
}
