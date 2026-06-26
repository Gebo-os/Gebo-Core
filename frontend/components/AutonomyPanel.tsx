"use client";

import { useCallback, useEffect, useState } from "react";
import { ActionCard } from "./ActionCard";
import { EmptyState } from "./EmptyState";
import {
  approveAction,
  getActions,
  rejectAction,
  runAction,
} from "@/lib/api";
import type { Action } from "@/lib/types";

export function AutonomyPanel() {
  const [actions, setActions] = useState<Action[]>([]);
  const [selected, setSelected] = useState<Action | null>(null);
  const [loadingId, setLoadingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      const data = await getActions();
      setActions(data);
      setSelected((prev) =>
        prev ? data.find((a) => a.id === prev.id) ?? null : null
      );
    } catch {
      setActions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, []);

  const handleApprove = async (id: number) => {
    setLoadingId(id);
    setError(null);
    try {
      await approveAction(id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Approve failed");
    } finally {
      setLoadingId(null);
    }
  };

  const handleReject = async (id: number) => {
    setLoadingId(id);
    setError(null);
    try {
      await rejectAction(id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reject failed");
    } finally {
      setLoadingId(null);
    }
  };

  const handleRun = async (id: number) => {
    setLoadingId(id);
    setError(null);
    try {
      await runAction(id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Run failed");
    } finally {
      setLoadingId(null);
    }
  };

  const proposed = actions.filter((a) => a.status === "proposed");
  const approved = actions.filter((a) => a.status === "approved");
  const completed = actions.filter((a) => a.status === "completed");
  const failed = actions.filter((a) => a.status === "failed");

  if (loading) {
    return (
      <div className="panel" style={{ padding: "2rem", textAlign: "center" }}>
        <span className="loading-pulse" aria-hidden="true" /> Loading actions…
      </div>
    );
  }

  return (
    <>
      <div className="alert alert-info actions-safety" role="note">
        Gebo can propose actions. Bb approves execution.
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {actions.length === 0 ? (
        <EmptyState
          title="No proposed actions"
          description="No proposed actions. Gebo will place suggestions here when a task needs approval."
        />
      ) : (
        <div className="actions-layout">
          <div>
            <ActionSection
              title={`Proposed (${proposed.length})`}
              actions={proposed}
              selected={selected}
              onSelect={setSelected}
              onApprove={handleApprove}
              onReject={handleReject}
              loadingId={loadingId}
            />
            <ActionSection
              title={`Approved (${approved.length})`}
              actions={approved}
              selected={selected}
              onSelect={setSelected}
              onRun={handleRun}
              onReject={handleReject}
              loadingId={loadingId}
            />
            <ActionSection
              title={`Completed (${completed.length})`}
              actions={completed}
              selected={selected}
              onSelect={setSelected}
              loadingId={loadingId}
            />
            <ActionSection
              title={`Failed (${failed.length})`}
              actions={failed}
              selected={selected}
              onSelect={setSelected}
              loadingId={loadingId}
            />
          </div>

          <aside className="action-detail-panel" aria-label="Action details">
            {selected ? (
              <>
                <h3 className="panel-title">Action Details</h3>
                <p className="action-card-type">{selected.action_type}</p>
                <h4 className="action-card-title">{selected.title}</h4>
                <p className="action-card-desc">{selected.description}</p>
                <p style={{ fontSize: "0.8rem", color: "var(--text-tertiary)", marginTop: "0.5rem" }}>
                  {new Date(selected.created_at).toLocaleString()}
                </p>
                <div className="action-card-buttons" style={{ marginTop: "1rem" }}>
                  {selected.status === "proposed" && (
                    <>
                      <button
                        type="button"
                        className="btn btn-sm btn-primary"
                        onClick={() => handleApprove(selected.id)}
                        disabled={loadingId === selected.id}
                      >
                        Approve
                      </button>
                      <button
                        type="button"
                        className="btn btn-sm btn-danger"
                        onClick={() => handleReject(selected.id)}
                        disabled={loadingId === selected.id}
                      >
                        Reject
                      </button>
                    </>
                  )}
                  {selected.status === "approved" && (
                    <>
                      <button
                        type="button"
                        className="btn btn-sm btn-primary"
                        onClick={() => handleRun(selected.id)}
                        disabled={loadingId === selected.id}
                      >
                        Run Approved Action
                      </button>
                      <button
                        type="button"
                        className="btn btn-sm btn-danger"
                        onClick={() => handleReject(selected.id)}
                        disabled={loadingId === selected.id}
                      >
                        Reject
                      </button>
                    </>
                  )}
                </div>
                {selected.payload_json && (
                  <pre className="action-result">
                    Payload:{" "}
                    {JSON.stringify(JSON.parse(selected.payload_json), null, 2)}
                  </pre>
                )}
                {selected.result_json && (
                  <pre className="action-result">
                    Result:{" "}
                    {JSON.stringify(JSON.parse(selected.result_json), null, 2)}
                  </pre>
                )}
              </>
            ) : (
              <p className="action-detail-empty">
                Select an action to view details.
              </p>
            )}
          </aside>
        </div>
      )}
    </>
  );
}

function ActionSection({
  title,
  actions,
  selected,
  onSelect,
  onApprove,
  onReject,
  onRun,
  loadingId,
}: {
  title: string;
  actions: Action[];
  selected: Action | null;
  onSelect: (a: Action) => void;
  onApprove?: (id: number) => void;
  onReject?: (id: number) => void;
  onRun?: (id: number) => void;
  loadingId?: number | null;
}) {
  if (actions.length === 0) return null;
  return (
    <section className="actions-section">
      <h3 className="actions-section-title">{title}</h3>
      {actions.map((a) => (
        <ActionCard
          key={a.id}
          action={a}
          selected={selected?.id === a.id}
          onSelect={onSelect}
          onApprove={onApprove}
          onReject={onReject}
          onRun={onRun}
          loadingId={loadingId}
          compact
        />
      ))}
    </section>
  );
}
