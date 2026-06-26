"use client";

import type { Action } from "@/lib/types";

interface ActionCardProps {
  action: Action;
  selected?: boolean;
  onSelect?: (action: Action) => void;
  onApprove?: (id: number) => void;
  onReject?: (id: number) => void;
  onRun?: (id: number) => void;
  loadingId?: number | null;
  compact?: boolean;
}

export function ActionCard({
  action,
  selected,
  onSelect,
  onApprove,
  onReject,
  onRun,
  loadingId,
  compact,
}: ActionCardProps) {
  const busy = loadingId === action.id;

  return (
    <article
      className={`action-card ${selected ? "selected" : ""}`}
      onClick={() => onSelect?.(action)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect?.(action);
        }
      }}
      role="button"
      tabIndex={0}
      aria-pressed={selected}
    >
      <div className="action-card-header">
        <span className="action-card-type">{action.action_type}</span>
        <StatusTag status={action.status} />
      </div>
      <h4 className="action-card-title">{action.title}</h4>
      {!compact && (
        <p className="action-card-desc">{action.description}</p>
      )}
      {(onApprove || onReject || onRun) && (
        <div
          className="action-card-buttons"
          onClick={(e) => e.stopPropagation()}
        >
          {action.status === "proposed" && onApprove && onReject && (
            <>
              <button
                type="button"
                className="btn btn-sm btn-primary"
                onClick={() => onApprove(action.id)}
                disabled={busy}
              >
                Approve
              </button>
              <button
                type="button"
                className="btn btn-sm btn-danger"
                onClick={() => onReject(action.id)}
                disabled={busy}
              >
                Reject
              </button>
            </>
          )}
          {action.status === "approved" && onRun && onReject && (
            <>
              <button
                type="button"
                className="btn btn-sm btn-primary"
                onClick={() => onRun(action.id)}
                disabled={busy}
              >
                Run Approved Action
              </button>
              <button
                type="button"
                className="btn btn-sm btn-danger"
                onClick={() => onReject(action.id)}
                disabled={busy}
              >
                Reject
              </button>
            </>
          )}
        </div>
      )}
    </article>
  );
}

function StatusTag({ status }: { status: string }) {
  const cls =
    status === "proposed"
      ? "tag-warning"
      : status === "approved"
        ? "tag-green"
        : status === "failed" || status === "rejected"
          ? "tag-danger"
          : "";
  return <span className={`tag ${cls}`}>{status}</span>;
}
