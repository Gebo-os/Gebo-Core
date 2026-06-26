"use client";

import { useGebo } from "@/lib/GeboProvider";

export function OsCenterEmblem() {
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
        <span className="os-emblem-ticks" />
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
