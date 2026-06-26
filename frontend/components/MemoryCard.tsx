"use client";

import type { Memory } from "@/lib/types";

interface MemoryCardProps {
  memory: Memory;
  onView?: (memory: Memory) => void;
  expanded?: boolean;
}

export function MemoryCard({ memory, onView, expanded }: MemoryCardProps) {
  const preview =
    expanded || memory.content.length <= 280
      ? memory.content
      : memory.content.slice(0, 280) + "…";

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(memory.content);
    } catch {
      /* clipboard unavailable */
    }
  };

  return (
    <article className="memory-card">
      <div className="memory-card-header">
        <span className="tag tag-green">{formatType(memory.memory_type)}</span>
        <span className="tag">{memory.source}</span>
        <time className="memory-card-date" dateTime={memory.created_at}>
          {new Date(memory.created_at).toLocaleString()}
        </time>
      </div>
      <p className="memory-card-content">{preview}</p>
      <div className="memory-card-actions">
        {onView && !expanded && memory.content.length > 280 && (
          <button
            type="button"
            className="btn btn-sm btn-ghost"
            onClick={() => onView(memory)}
          >
            View full
          </button>
        )}
        <button
          type="button"
          className="btn btn-sm btn-secondary"
          onClick={handleCopy}
        >
          Copy
        </button>
        <button
          type="button"
          className="btn btn-sm btn-ghost"
          disabled
          title="Archive not available in V0"
        >
          Archive
        </button>
        <button
          type="button"
          className="btn btn-sm btn-ghost"
          disabled
          title="Delete not supported by backend"
        >
          Delete
        </button>
      </div>
    </article>
  );
}

function formatType(type: string): string {
  const map: Record<string, string> = {
    core: "Core",
    project: "Project",
    career: "Career",
    presence: "Presence",
    build_log: "Build Log",
    preference: "Preference",
    system: "System",
    manual: "Core",
    auto: "Auto",
    plan: "Project",
    summary: "Build Log",
    project_note: "Project",
  };
  return map[type.toLowerCase()] || type;
}
