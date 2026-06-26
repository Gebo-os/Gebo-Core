"use client";

import Image from "next/image";
import Link from "next/link";
import { useGebo } from "@/lib/GeboProvider";

interface OsWidgetProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

export function OsWidget({ title, children, className = "" }: OsWidgetProps) {
  return (
    <article className={`os-widget panel ${className}`.trim()}>
      <h3 className="os-widget-title">{title}</h3>
      {children}
    </article>
  );
}

export function CommandCenterHero() {
  const { geboStatus, online, agentRuntime } = useGebo();
  return (
    <section className="os-command-hero">
      <div className="os-command-brand">
        <Image
          src="/brand/gebo-os-dark.png"
          alt="Gebo OS command center"
          width={480}
          height={270}
          className="os-command-ref os-command-ref-dark"
          priority
        />
        <Image
          src="/brand/gebo-os-light.png"
          alt="Gebo OS light theme reference"
          width={480}
          height={270}
          className="os-command-ref os-command-ref-light"
        />
        <div className="os-command-mark" aria-hidden="true">
          G
        </div>
      </div>
      <div className="os-command-meta">
        <span className="os-command-badge">Owner NODE · Command Center</span>
        <p className="os-command-state">
          {online ? `Gebo ${geboStatus}` : "Backend offline"}
        </p>
        <p className="os-command-tagline">
          Idea → Income · Memory → Experience · Presence → Action
        </p>
        {agentRuntime && (
          <p className="os-command-runtime">
            {agentRuntime.active_agents} agents active ·{" "}
            {agentRuntime.healthy ? "runtime optimal" : "runtime degraded"}
          </p>
        )}
      </div>
    </section>
  );
}

export function SystemOverviewWidget() {
  const { status, online, agentRuntime, codex, wiki } = useGebo();
  const memCount = status?.memory_count ?? 0;
  const msgCount = status?.message_count ?? 0;
  const pending =
    (status?.proposed_action_count ?? 0) +
    (status?.approved_action_count ?? 0);
  const perfIndex = online
    ? Math.min(
        99,
        Math.round(
          40 +
            Math.min(memCount, 50) * 0.6 +
            (agentRuntime?.healthy ? 25 : 0) +
            (codex?.available ? 10 : 0) +
            (wiki?.available ? 8 : 0)
        )
      )
    : 0;

  const bars = [
    { label: "Memory", pct: Math.min(100, memCount * 2) },
    { label: "Messages", pct: Math.min(100, msgCount * 3) },
    { label: "Actions", pct: Math.min(100, pending * 10) },
    {
      label: "Agents",
      pct: agentRuntime
        ? Math.round((agentRuntime.active_agents / agentRuntime.total_registry) * 100)
        : 0,
    },
  ];

  return (
    <OsWidget title="System Overview">
      <div className="os-perf-ring">
        <span className="os-perf-value">{perfIndex}</span>
        <span className="os-perf-label">Performance Index</span>
      </div>
      <ul className="os-bar-list">
        {bars.map((b) => (
          <li key={b.label}>
            <span>{b.label}</span>
            <div className="os-bar-track">
              <div className="os-bar-fill" style={{ width: `${b.pct}%` }} />
            </div>
            <span className="os-bar-pct">{b.pct}%</span>
          </li>
        ))}
      </ul>
    </OsWidget>
  );
}

export function ComputeOverviewWidget() {
  const { status, online } = useGebo();
  return (
    <OsWidget title="Compute Grid">
      <div className="os-compute-visual" aria-hidden="true">
        <div className="os-compute-core" />
      </div>
      <dl className="os-memory-stats">
        <div>
          <dt>Model</dt>
          <dd>{status?.model?.split(":")[0] ?? "—"}</dd>
        </div>
        <div>
          <dt>Backend</dt>
          <dd>{online ? "Online" : "Offline"}</dd>
        </div>
        <div>
          <dt>Route</dt>
          <dd>Ollama local</dd>
        </div>
      </dl>
      <Link href="/chat" className="os-widget-link">
        Open Chat →
      </Link>
    </OsWidget>
  );
}

export function IntelligenceFeed() {
  const { memories, status } = useGebo();
  const items = memories.slice(0, 4);
  return (
    <OsWidget title="Intelligence Feed">
      {items.length === 0 ? (
        <p className="os-feed-empty">No recent memory signals.</p>
      ) : (
        <ul className="os-feed-list">
          {items.map((m) => (
            <li key={m.id}>
              <span className="tag tag-green">{m.memory_type}</span>
              <span className="os-feed-text">
                {m.content.slice(0, 72)}
                {m.content.length > 72 ? "…" : ""}
              </span>
            </li>
          ))}
        </ul>
      )}
      <Link href="/memory" className="os-widget-link">
        Open Memory →
      </Link>
      {status && (
        <p className="os-widget-foot">
          {status.completed_action_count} actions completed
        </p>
      )}
    </OsWidget>
  );
}

export function SystemOrchestration() {
  const { agentRuntime } = useGebo();
  const agentLabel = agentRuntime
    ? `${agentRuntime.active_agents} Active Agents`
    : "Agent Runtime";

  return (
    <OsWidget title="AI Orchestration">
      <div className="os-orchestration-grid">
        <div className="os-orch-node os-orch-core">Gebo Core Orchestrator</div>
        <div className="os-orch-node">Reflex Engine</div>
        <div className="os-orch-node">Evolution Loop</div>
        <div className="os-orch-node">Memory API</div>
        <div className="os-orch-node">Approval Gate</div>
        <div className="os-orch-node">{agentLabel}</div>
      </div>
      <Link href="/reflexes" className="os-widget-link">
        Reflexes →
      </Link>
      <Link href="/evolution" className="os-widget-link">
        Evolution →
      </Link>
    </OsWidget>
  );
}

export function MemoryFabricWidget() {
  const { status, memories } = useGebo();
  const count = status?.memory_count ?? 0;
  const pct = Math.min(100, Math.round((count / Math.max(count, 50)) * 78));
  return (
    <OsWidget title="Memory Fabric">
      <div className="os-memory-gauge">
        <span className="os-memory-pct">{pct}%</span>
        <span className="os-memory-label">continuity load</span>
      </div>
      <dl className="os-memory-stats">
        <div>
          <dt>Entries</dt>
          <dd>{count}</dd>
        </div>
        <div>
          <dt>Types</dt>
          <dd>{new Set(memories.map((m) => m.memory_type)).size || "—"}</dd>
        </div>
        <div>
          <dt>Messages</dt>
          <dd>{status?.message_count ?? 0}</dd>
        </div>
      </dl>
    </OsWidget>
  );
}
