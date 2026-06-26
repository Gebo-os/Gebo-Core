"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { PageHeader } from "@/components/PageHeader";
import { StatusCard } from "@/components/StatusCard";
import { EmptyState } from "@/components/EmptyState";
import { LivingPulse } from "@/components/LivingPulse";
import { useGebo } from "@/lib/GeboProvider";

export default function PulseHome() {
  const router = useRouter();
  const {
    online,
    status,
    codex,
    wiki,
    geboStatus,
    mission,
    activePresence,
    memories,
    loading,
  } = useGebo();
  const [quickInput, setQuickInput] = useState("");

  const lastMemory = memories[0];
  const pendingActions =
    (status?.proposed_action_count ?? 0) +
    (status?.approved_action_count ?? 0);

  const statusClass =
    geboStatus === "Awake"
      ? "awake"
      : geboStatus === "Resting"
        ? "resting"
        : "setup";

  const handleQuickSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const text = quickInput.trim();
    if (!text) return;
    sessionStorage.setItem("gebo-chat-pending", text);
    router.push("/chat");
  };

  if (loading) {
    return (
      <>
        <PageHeader eyebrow="Home" title="Pulse" description="Loading…" />
        <div className="status-card-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton" style={{ height: 88 }} />
          ))}
        </div>
      </>
    );
  }

  return (
    <>
      <PageHeader
        eyebrow="Home"
        title="Pulse"
        description="Gebo's current state at a glance."
      />

      <section className="living-hero">
        <LivingPulse />
        <div className="living-hero-overlay">
          <span className={`living-hero-state ${statusClass}`}>
            <span
              className={`pulse-status-indicator ${statusClass}`}
              aria-hidden="true"
            />
            {geboStatus}
          </span>
          <p className="living-hero-caption">
            {online
              ? `${status?.memory_count ?? 0} memories · ${
                  status?.message_count ?? 0
                } messages`
              : "Backend offline — start the FastAPI server"}
          </p>
        </div>
      </section>

      <section className="pulse-mission">
        <div className="pulse-mission-label">Current Mission</div>
        <p className="pulse-mission-text">{mission}</p>
      </section>

      <div className="status-card-grid" style={{ marginBottom: "2rem" }}>
        <StatusCard
          label="Memories"
          value={status?.memory_count ?? 0}
          sub="Stored continuity"
          accent
        />
        <StatusCard
          label="Pending Actions"
          value={pendingActions}
          sub="Awaiting approval"
        />
        <StatusCard
          label="Messages"
          value={status?.message_count ?? 0}
          sub="Conversation history"
        />
        <StatusCard
          label="Active Presence"
          value={activePresence?.name ?? "Gebo"}
          sub={activePresence?.status ?? "—"}
        />
        <StatusCard
          label="Model"
          value={status?.model ?? "—"}
          sub={online ? "Ollama local" : "Backend Offline"}
        />
        <StatusCard
          label="Memory Collection"
          value={status?.consent ? "On" : "Off"}
          sub={status?.consent ? "Auto-capture active" : "Manual only"}
        />
        <StatusCard
          label="Codex Engine"
          value={codex?.available ? "Connected" : "Not found"}
          sub={codex?.available ? codex.version ?? "Ready" : "Install Codex CLI"}
          accent={codex?.available}
        />
        <StatusCard
          label="Knowledge Wiki"
          value={wiki?.available ? "Loaded" : wiki?.enabled ? "No ZIM" : "Off"}
          sub={
            wiki?.available
              ? wiki.title ?? "Offline knowledge"
              : "Add a .zim to data/wiki"
          }
          accent={wiki?.available}
        />
      </div>

      {lastMemory ? (
        <section className="panel" style={{ marginBottom: "2rem" }}>
          <h2 className="panel-title">Last Meaningful Memory</h2>
          <div className="pulse-memory-preview">
            <span className="tag tag-green">{lastMemory.memory_type}</span>
            <p style={{ marginTop: "0.5rem", fontSize: "0.9rem", lineHeight: 1.55 }}>
              {lastMemory.content.length > 200
                ? lastMemory.content.slice(0, 200) + "…"
                : lastMemory.content}
            </p>
            <time
              style={{
                display: "block",
                marginTop: "0.5rem",
                fontSize: "0.75rem",
                color: "var(--text-tertiary)",
              }}
              dateTime={lastMemory.created_at}
            >
              {new Date(lastMemory.created_at).toLocaleString()}
            </time>
          </div>
        </section>
      ) : (
        <div style={{ marginBottom: "2rem" }}>
          <EmptyState
            title="No memories yet"
            description="No memory yet. Add your first core memory to give Gebo continuity."
            action={
              <Link href="/memory" className="btn btn-primary">
                Open Memory Garden
              </Link>
            }
          />
        </div>
      )}

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "1rem",
          alignItems: "flex-end",
        }}
      >
        <Link href="/chat" className="btn btn-primary btn-lg">
          Continue to Chat
        </Link>
        <form
          onSubmit={handleQuickSubmit}
          style={{ flex: 1, minWidth: "240px", display: "flex", gap: "0.5rem" }}
        >
          <input
            type="text"
            className="field-input"
            placeholder="Quick command…"
            value={quickInput}
            onChange={(e) => setQuickInput(e.target.value)}
            aria-label="Quick command"
          />
          <button type="submit" className="btn btn-secondary">
            Go
          </button>
        </form>
      </div>
    </>
  );
}
