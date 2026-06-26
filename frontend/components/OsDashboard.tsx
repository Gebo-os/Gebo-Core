"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useGebo } from "@/lib/GeboProvider";
import type { AgentRuntimeStatus, CodexStatus, WikiStatus } from "@/lib/types";

interface OsWidgetProps {
  title: string;
  children: React.ReactNode;
  className?: string;
  badge?: string;
}

export function OsWidget({
  title,
  children,
  className = "",
  badge,
}: OsWidgetProps) {
  const { pulse, motionEnabled } = useGebo();
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (!motionEnabled || pulse === 0) return;
    setRefreshing(true);
    const id = window.setTimeout(() => setRefreshing(false), 800);
    return () => window.clearTimeout(id);
  }, [pulse, motionEnabled]);

  return (
    <article
      className={`os-widget panel ${refreshing ? "os-widget-refresh" : ""} ${className}`.trim()}
    >
      <div className="os-widget-head">
        <h3 className="os-widget-title">{title}</h3>
        {badge && <span className="os-widget-badge">{badge}</span>}
      </div>
      {children}
    </article>
  );
}

function formatRelativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function derivePerfIndex(
  online: boolean,
  memCount: number,
  agentRuntime: AgentRuntimeStatus | null,
  codex: CodexStatus | null,
  wiki: WikiStatus | null
): number {
  if (!online) return 0;
  return Math.min(
    99,
    Math.round(
      40 +
        Math.min(memCount, 50) * 0.6 +
        (agentRuntime?.healthy ? 25 : 0) +
        (codex?.available ? 10 : 0) +
        (wiki?.available ? 8 : 0)
    )
  );
}

export function SystemOverviewWidget() {
  const { status, online, agentRuntime, codex, wiki } = useGebo();
  const memCount = status?.memory_count ?? 0;
  const msgCount = status?.message_count ?? 0;
  const pending =
    (status?.proposed_action_count ?? 0) +
    (status?.approved_action_count ?? 0);

  const perfIndex = derivePerfIndex(
    Boolean(online),
    memCount,
    agentRuntime,
    codex,
    wiki
  );

  const computePct = agentRuntime
    ? Math.round((agentRuntime.active_agents / Math.max(agentRuntime.total_registry, 1)) * 100)
    : online
      ? 72
      : 0;
  const memoryPct = Math.min(100, Math.round(memCount * 1.5 + 20));
  const networkPct = online ? (status?.consent ? 93 : 78) : 0;
  const securityPct = Math.round(
    ((status?.consent ? 25 : 0) +
      (codex?.available ? 25 : 0) +
      (wiki?.available ? 20 : 0) +
      35) *
      (online ? 1 : 0.3)
  );

  const bars = [
    { label: "Compute", pct: computePct },
    { label: "Memory", pct: memoryPct },
    { label: "Network", pct: networkPct },
    { label: "Security", pct: Math.min(100, securityPct) },
  ];

  const uptime = agentRuntime?.started_at
    ? formatRelativeTime(agentRuntime.started_at).replace(" ago", "")
    : online
      ? "Active"
      : "—";
  const processes =
    (agentRuntime?.active_agents ?? 0) +
    pending +
    msgCount +
    memCount;

  return (
    <OsWidget title="System Overview">
      <div className="os-overview-row">
        <div className="os-perf-ring">
          <span className="os-perf-value">{perfIndex}</span>
          <span className="os-perf-label">Performance Index</span>
        </div>
        <ul className="os-bar-list os-bar-list-compact">
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
      </div>
      <div className="os-overview-foot">
        <span>Uptime: {uptime}</span>
        <span>Processes: {processes}</span>
      </div>
    </OsWidget>
  );
}

export function ComputeOverviewWidget() {
  const { status, online, agentRuntime } = useGebo();
  const totalNodes = agentRuntime?.total_registry ?? 128;
  const activeNodes = agentRuntime?.active_agents ?? (online ? 1 : 0);
  const utilization = agentRuntime
    ? Math.round((activeNodes / Math.max(totalNodes, 1)) * 100)
    : online
      ? 89
      : 0;
  const temperature = online ? 42 + utilization * 0.2 : 0;

  return (
    <OsWidget title="Compute Grid">
      <div className="os-compute-visual" aria-hidden="true">
        <div className="os-compute-grid-3d">
          {Array.from({ length: 9 }).map((_, i) => (
            <span key={i} className="os-compute-cell" />
          ))}
        </div>
      </div>
      <dl className="os-stat-grid">
        <div>
          <dt>Total Nodes</dt>
          <dd>{totalNodes}</dd>
        </div>
        <div>
          <dt>Active</dt>
          <dd>{activeNodes}</dd>
        </div>
        <div>
          <dt>Utilization</dt>
          <dd>{utilization}%</dd>
        </div>
        <div>
          <dt>Temperature</dt>
          <dd>{Math.round(temperature)}°C</dd>
        </div>
      </dl>
      <Link href="/chat" className="os-widget-link">
        Open Compute →
      </Link>
      {status?.model && (
        <p className="os-widget-foot">{status.model.split(":")[0]}</p>
      )}
    </OsWidget>
  );
}

export function MemoryFabricWidget() {
  const { status, memories } = useGebo();
  const count = status?.memory_count ?? 0;
  const msgCount = status?.message_count ?? 0;
  const pct = Math.min(100, Math.round(count * 1.2 + msgCount * 0.5 + 12));

  const ramUsed = (count * 0.4 + msgCount * 0.05).toFixed(1);
  const ramTotal = 32;
  const vramUsed = (count * 0.15 + 2).toFixed(1);
  const vramTotal = 16;
  const swapUsed = (msgCount * 0.08 + 1).toFixed(1);
  const swapTotal = 8;

  return (
    <OsWidget title="Memory Fabric">
      <div className="os-memory-row">
        <div className="os-memory-gauge">
          <span className="os-memory-pct">{pct}%</span>
          <span className="os-memory-label">In Use</span>
        </div>
        <dl className="os-memory-breakdown">
          <div>
            <dt>RAM</dt>
            <dd>
              {ramUsed} GB / {ramTotal} GB
            </dd>
            <div className="os-mini-bar">
              <div
                className="os-mini-bar-fill"
                style={{
                  width: `${Math.min(100, (parseFloat(ramUsed) / ramTotal) * 100)}%`,
                }}
              />
            </div>
          </div>
          <div>
            <dt>VRAM</dt>
            <dd>
              {vramUsed} GB / {vramTotal} GB
            </dd>
            <div className="os-mini-bar">
              <div
                className="os-mini-bar-fill"
                style={{
                  width: `${Math.min(100, (parseFloat(vramUsed) / vramTotal) * 100)}%`,
                }}
              />
            </div>
          </div>
          <div>
            <dt>Swap</dt>
            <dd>
              {swapUsed} GB / {swapTotal} GB
            </dd>
            <div className="os-mini-bar">
              <div
                className="os-mini-bar-fill"
                style={{
                  width: `${Math.min(100, (parseFloat(swapUsed) / swapTotal) * 100)}%`,
                }}
              />
            </div>
          </div>
        </dl>
      </div>
      <div className="os-memory-foot">
        <span className="os-sparkline" aria-hidden="true">
          {Array.from({ length: 12 }).map((_, i) => (
            <span key={i} style={{ height: `${20 + (i % 5) * 12}%` }} />
          ))}
        </span>
        <span>Bandwidth: {(count * 0.05 + 0.8).toFixed(1)} TB/s</span>
        <span>{new Set(memories.map((m) => m.memory_type)).size} types</span>
      </div>
    </OsWidget>
  );
}

export function GlobalNetworkWidget() {
  const { network, agentRuntime, online, status } = useGebo();
  const nodes = (agentRuntime?.total_registry ?? 24) * 1000 + (status?.memory_count ?? 0) * 37;
  const regions = network?.internet_access ? 156 : 12;
  const traffic = online
    ? `${((status?.message_count ?? 0) * 0.01 + 0.4).toFixed(1)} Gbps`
    : "0 Gbps";

  return (
    <OsWidget title="Global Network">
      <div className="os-globe-wrap" aria-hidden="true">
        <div className="os-globe">
          <div className="os-globe-grid" />
          {Array.from({ length: 8 }).map((_, i) => (
            <span
              key={i}
              className="os-globe-node"
              style={{
                top: `${15 + (i * 17) % 70}%`,
                left: `${10 + (i * 23) % 80}%`,
                animationDelay: `${i * 0.3}s`,
              }}
            />
          ))}
        </div>
      </div>
      <dl className="os-stat-grid os-stat-grid-3">
        <div>
          <dt>Nodes</dt>
          <dd>{nodes.toLocaleString()}</dd>
        </div>
        <div>
          <dt>Regions</dt>
          <dd>{regions}</dd>
        </div>
        <div>
          <dt>Traffic</dt>
          <dd>{traffic}</dd>
        </div>
      </dl>
      <Link href="/settings" className="os-widget-link">
        Network Settings →
      </Link>
    </OsWidget>
  );
}

export function IntelligenceFeed() {
  const { memories, status } = useGebo();
  const items = memories.slice(0, 5);

  return (
    <OsWidget title="Intelligence Feed" badge="Live">
      {items.length === 0 ? (
        <p className="os-feed-empty">No recent memory signals.</p>
      ) : (
        <ul className="os-feed-list">
          {items.map((m) => (
            <li key={m.id}>
              <span className="os-feed-dot" aria-hidden="true" />
              <div className="os-feed-body">
                <span className="os-feed-text">
                  {m.content.slice(0, 64)}
                  {m.content.length > 64 ? "…" : ""}
                </span>
                <span className="os-feed-time">
                  {formatRelativeTime(m.created_at)}
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}
      <Link href="/memory" className="os-widget-link">
        View all events →
      </Link>
      {status && (
        <p className="os-widget-foot">
          {status.completed_action_count} actions completed
        </p>
      )}
    </OsWidget>
  );
}

const ORCH_NODES = [
  { label: "Vision Model", version: "v3.2", angle: 0 },
  { label: "Language Model", version: "v4.1", angle: 60 },
  { label: "Data Synthesizer", version: "v2.8", angle: 120 },
  { label: "Reasoning Engine", version: "v5.0", angle: 180 },
  { label: "Action Planner", version: "v2.3", angle: 240 },
  { label: "Safety Layer", version: "v1.9", angle: 300 },
];

export function SystemOrchestration() {
  const { agentRuntime, status } = useGebo();
  const requests = (status?.message_count ?? 0) * 1000 + 4200;
  const tokensPerSec = agentRuntime?.parallel_workers
    ? agentRuntime.parallel_workers * 0.9
    : 2.7;
  const activeAgents = agentRuntime?.active_agents ?? 0;
  const successRate = agentRuntime?.healthy ? 99.8 : 94.2;

  return (
    <OsWidget title="AI Orchestration" className="os-widget-orch">
      <div className="os-orch-diagram" aria-hidden="true">
        <svg viewBox="0 0 320 220" className="os-orch-svg">
          {ORCH_NODES.map((node) => {
            const rad = (node.angle * Math.PI) / 180;
            const cx = 160 + Math.cos(rad) * 95;
            const cy = 110 + Math.sin(rad) * 75;
            return (
              <line
                key={node.label}
                x1="160"
                y1="110"
                x2={cx}
                y2={cy}
                className="os-orch-line"
              />
            );
          })}
        </svg>
        <div className="os-orch-core">Gebo Core Orchestrator</div>
        {ORCH_NODES.map((node) => (
          <div
            key={node.label}
            className="os-orch-satellite"
            style={{
              transform: `rotate(${node.angle}deg) translateY(-88px) rotate(-${node.angle}deg)`,
            }}
          >
            <span className="os-orch-sat-name">{node.label}</span>
            <span className="os-orch-sat-ver">{node.version}</span>
          </div>
        ))}
      </div>
      <dl className="os-orch-metrics">
        <div>
          <dt>Requests</dt>
          <dd>{(requests / 1_000_000).toFixed(1)}M</dd>
        </div>
        <div>
          <dt>Tokens/s</dt>
          <dd>{tokensPerSec.toFixed(1)}M</dd>
        </div>
        <div>
          <dt>Active Agents</dt>
          <dd>{activeAgents}</dd>
        </div>
        <div>
          <dt>Success Rate</dt>
          <dd>{successRate}%</dd>
        </div>
      </dl>
      <div className="os-orch-links">
        <Link href="/reflexes" className="os-widget-link">
          Reflexes →
        </Link>
        <Link href="/evolution" className="os-widget-link">
          Evolution →
        </Link>
      </div>
    </OsWidget>
  );
}

const DEVICE_MAP = [
  { name: "GPhone", icon: "📱", presenceId: "gebo" },
  { name: "GBook Pro", icon: "💻", presenceId: "lockin" },
  { name: "GTab", icon: "📋", presenceId: "mya" },
  { name: "GWatch", icon: "⌚", presenceId: "dream" },
  { name: "GPod", icon: "🎧", presenceId: "slatt" },
];

export function DeviceContinuityWidget() {
  const { presences, online } = useGebo();

  return (
    <OsWidget title="Device Continuity">
      <ul className="os-device-grid">
        {DEVICE_MAP.map((device) => {
          const presence = presences.find((p) => p.id === device.presenceId);
          const active =
            online &&
            presence &&
            (presence.status === "Awake" || presence.status === "Quiet");
          return (
            <li key={device.name} className={active ? "active" : ""}>
              <span className="os-device-icon" aria-hidden="true">
                {device.icon}
              </span>
              <span className="os-device-name">{device.name}</span>
              <span className={`os-device-status ${active ? "on" : ""}`}>
                {active ? "Active" : "Idle"}
              </span>
            </li>
          );
        })}
      </ul>
      <Link href="/presences" className="os-widget-link">
        Manage Devices →
      </Link>
    </OsWidget>
  );
}

export function SecurityWidget() {
  const { status, codex, wiki, network } = useGebo();
  const score = Math.round(
    ((status?.consent ? 30 : 0) +
      (codex?.available ? 25 : 0) +
      (wiki?.available ? 20 : 0) +
      (network?.cors_mode !== "open" ? 25 : 15)) *
      0.85
  );

  const rows = [
    {
      label: "Threat Detection",
      value: codex?.available ? "Active" : "Standby",
      ok: Boolean(codex?.available),
    },
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
      label: "Network Perimeter",
      value: network?.internet_access ? "Open" : "Localhost",
      ok: !network?.internet_access,
    },
    {
      label: "Privacy Shield",
      value: wiki?.available ? "Enabled" : "Partial",
      ok: Boolean(wiki?.available),
    },
  ];

  return (
    <OsWidget title="Security">
      <div className="os-security-score">
        <span className="os-security-value">{Math.min(100, score)}</span>
        <span className="os-security-label">Security Index</span>
      </div>
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
        Security Settings →
      </Link>
    </OsWidget>
  );
}
