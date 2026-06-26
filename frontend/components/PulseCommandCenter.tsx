"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  ComputeOverviewWidget,
  IntelligenceFeed,
  MemoryFabricWidget,
  OsWidget,
  SystemOrchestration,
  SystemOverviewWidget,
} from "@/components/OsDashboard";
import { useGebo } from "@/lib/GeboProvider";

const OS_TABS = [
  { id: "command", label: "Command Center", href: "/" },
  { id: "compute", label: "Compute", href: "/chat" },
  { id: "memory", label: "Memory", href: "/memory" },
  { id: "network", label: "Network", href: "/settings" },
  { id: "orchestration", label: "AI Orchestration", href: "/reflexes" },
  { id: "security", label: "Security", href: "/settings" },
  { id: "system", label: "System", href: "/settings" },
] as const;

const QUICK_COMMANDS = [
  { label: "Open Chat", href: "/chat" },
  { label: "Memory Garden", href: "/memory" },
  { label: "Action Queue", href: "/actions" },
  { label: "Reflex Engine", href: "/reflexes" },
  { label: "Evolution Loop", href: "/evolution" },
];

function OsCenterEmblem() {
  const { geboStatus, online, mission } = useGebo();
  const statusClass =
    geboStatus === "Awake"
      ? "awake"
      : geboStatus === "Resting"
        ? "resting"
        : "setup";

  return (
    <div className="os-emblem-wrap">
      <div className="os-emblem-rings" aria-hidden="true">
        <span className="os-emblem-ring os-emblem-ring-1" />
        <span className="os-emblem-ring os-emblem-ring-2" />
        <span className="os-emblem-ring os-emblem-ring-3" />
      </div>
      <div className={`os-emblem-mark ${statusClass}`} aria-hidden="true">
        G
      </div>
      <div className="os-emblem-meta">
        <span className="os-command-badge">Gebo OS · Owner NODE</span>
        <p className={`os-emblem-state ${statusClass}`}>
          {online ? geboStatus : "Offline"}
        </p>
        <p className="os-emblem-mission">{mission}</p>
      </div>
    </div>
  );
}

function PresenceContinuityWidget() {
  const { activePresence, presences, status } = useGebo();
  return (
    <OsWidget title="Presence Continuity">
      <div className="os-presence-active">
        <span className="os-presence-mark">{activePresence?.mark ?? "G"}</span>
        <div>
          <strong>{activePresence?.name ?? "Gebo"}</strong>
          <p>{activePresence?.status ?? "—"}</p>
        </div>
        <span className="tag tag-green">Active</span>
      </div>
      <ul className="os-presence-list">
        {presences.slice(0, 4).map((p) => (
          <li key={p.id}>
            <span>{p.mark}</span>
            <span>{p.name}</span>
            <span className="os-presence-status">{p.status}</span>
          </li>
        ))}
      </ul>
      <Link href="/presences" className="os-widget-link">
        All Presences →
      </Link>
      {status && (
        <p className="os-widget-foot">
          {status.message_count} messages · consent{" "}
          {status.consent ? "on" : "off"}
        </p>
      )}
    </OsWidget>
  );
}

function SecurityWidget() {
  const { status, codex, wiki, network } = useGebo();
  const rows = [
    {
      label: "Memory Collection",
      value: status?.consent ? "On" : "Off",
      ok: Boolean(status?.consent),
    },
    {
      label: "Approval Gate",
      value: "Active",
      ok: true,
    },
    {
      label: "Network",
      value: network?.cors_mode === "open" ? "Open" : "Localhost",
      ok: true,
    },
    {
      label: "Codex",
      value: codex?.available ? "Ready" : "Off",
      ok: Boolean(codex?.available),
    },
    {
      label: "Wiki",
      value: wiki?.available ? "Loaded" : "Off",
      ok: Boolean(wiki?.available),
    },
  ];

  return (
    <OsWidget title="Security & Privacy">
      <ul className="os-security-list">
        {rows.map((row) => (
          <li key={row.label}>
            <span>{row.label}</span>
            <span className={row.ok ? "os-sec-ok" : "os-sec-warn"}>
              {row.value}
            </span>
          </li>
        ))}
      </ul>
      <Link href="/settings" className="os-widget-link">
        Settings →
      </Link>
    </OsWidget>
  );
}

function AssistantRail() {
  const { geboStatus, online, agentRuntime } = useGebo();
  return (
    <aside className="os-assistant-rail">
      <div className="os-assistant-wave" aria-hidden="true">
        {Array.from({ length: 12 }).map((_, i) => (
          <span key={i} style={{ animationDelay: `${i * 0.08}s` }} />
        ))}
      </div>
      <p className="os-assistant-label">
        {online ? `${geboStatus} · Listening` : "Backend offline"}
      </p>
      <ul className="os-quick-commands">
        {QUICK_COMMANDS.map((cmd) => (
          <li key={cmd.href}>
            <Link href={cmd.href}>{cmd.label}</Link>
          </li>
        ))}
      </ul>
      {agentRuntime && (
        <p className="os-assistant-foot">
          {agentRuntime.active_agents} agents ·{" "}
          {agentRuntime.healthy ? "optimal" : "degraded"}
        </p>
      )}
    </aside>
  );
}

function OsCommandDock() {
  const router = useRouter();
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const text = query.trim();
    if (!text) return;
    sessionStorage.setItem("gebo-chat-pending", text);
    router.push("/chat");
  };

  return (
    <footer className="os-command-dock">
      <div className="os-dock-tools" aria-hidden="true">
        <span title="Terminal">⌘</span>
        <span title="Files">▤</span>
        <span title="Apps">⊞</span>
      </div>
      <form className="os-dock-input-wrap" onSubmit={handleSubmit}>
        <span className="os-dock-logo" aria-hidden="true">
          G
        </span>
        <input
          type="text"
          className="os-dock-input"
          placeholder="Ask Gebo anything…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label="Ask Gebo"
        />
        <button type="submit" className="os-dock-send" aria-label="Send">
          →
        </button>
      </form>
      <div className="os-dock-tools" aria-hidden="true">
        <span>◇</span>
        <span>✦</span>
        <span>&lt;/&gt;</span>
      </div>
    </footer>
  );
}

export function PulseCommandCenter() {
  const { loading, online } = useGebo();

  if (loading) {
    return (
      <div className="os-pulse os-pulse-loading">
        <div className="os-pulse-tabs">
          {OS_TABS.map((tab) => (
            <span key={tab.id} className="os-pulse-tab skeleton" />
          ))}
        </div>
        <div className="os-pulse-grid">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="skeleton os-widget-skeleton" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="os-pulse">
      <header className="os-pulse-header">
        <div className="os-pulse-brand">
          <span className="os-pulse-logo" aria-hidden="true">
            G
          </span>
          <span className="os-pulse-title">Gebo OS</span>
        </div>
        <nav className="os-pulse-tabs" aria-label="Command center sections">
          {OS_TABS.map((tab) => (
            <Link
              key={tab.id}
              href={tab.href}
              className={`os-pulse-tab ${tab.id === "command" ? "active" : ""}`}
              aria-current={tab.id === "command" ? "page" : undefined}
            >
              {tab.label}
            </Link>
          ))}
        </nav>
        <div className="os-pulse-header-status">
          <span
            className={`os-pulse-live ${online ? "online" : "offline"}`}
            aria-hidden="true"
          />
          {!online && (
            <span className="os-pulse-offline-hint">Backend offline</span>
          )}
        </div>
      </header>

      <div className="os-pulse-body">
        <div className="os-pulse-grid">
          <div className="os-pulse-col os-pulse-col-left">
            <SystemOverviewWidget />
            <ComputeOverviewWidget />
            <MemoryFabricWidget />
          </div>

          <div className="os-pulse-col os-pulse-col-center">
            <OsCenterEmblem />
            <SystemOrchestration />
          </div>

          <div className="os-pulse-col os-pulse-col-right">
            <IntelligenceFeed />
            <PresenceContinuityWidget />
            <SecurityWidget />
          </div>
        </div>

        <AssistantRail />
      </div>

      <OsCommandDock />
    </div>
  );
}
