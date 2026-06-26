import type { Presence, PresenceStatus } from "@/lib/types";

interface PresenceCardProps {
  presence: Presence;
}

export function PresenceCard({ presence }: PresenceCardProps) {
  return (
    <article
      className={`presence-card ${presence.primary ? "primary" : ""}`}
    >
      <div className="presence-card-header">
        <div className="presence-mark" aria-hidden="true">
          {presence.mark}
        </div>
        <div>
          <h3 className="presence-name">{presence.name}</h3>
          <p className="presence-role">{presence.role}</p>
        </div>
        <StatusTag status={presence.status} />
      </div>
      <div className="presence-meta">
        <MetaRow label="Focus" value={presence.focus} />
        <MetaRow label="Memory access" value={presence.memoryAccess} />
        <MetaRow label="Last contribution" value={presence.lastContribution} />
        <MetaRow label="Suggested use" value={presence.suggestedUse} />
      </div>
    </article>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="presence-meta-row">
      <span className="presence-meta-label">{label}</span>
      <span className="presence-meta-value">{value}</span>
    </div>
  );
}

function StatusTag({ status }: { status: PresenceStatus }) {
  const cls =
    status === "Awake"
      ? "tag-green"
      : status === "Needs Memory"
        ? "tag-warning"
        : "";
  return <span className={`tag ${cls}`}>{status}</span>;
}
