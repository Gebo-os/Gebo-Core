"use client";

import { useCallback, useEffect, useState } from "react";
import { EmptyState } from "./EmptyState";
import {
  createReflex,
  getReflexEvents,
  getReflexes,
  toggleReflex,
} from "@/lib/api";
import { useGebo } from "@/lib/GeboProvider";
import type { Reflex, ReflexEvent } from "@/lib/types";

export function ReflexPanel() {
  const { online, status } = useGebo();
  const [reflexes, setReflexes] = useState<Reflex[]>([]);
  const [events, setEvents] = useState<ReflexEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [toggleId, setToggleId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    trigger_pattern: "",
    action_type: "save_memory",
  });

  const refresh = useCallback(async () => {
    try {
      const [r, e] = await Promise.all([getReflexes(), getReflexEvents()]);
      setReflexes(r);
      setEvents(e);
    } catch {
      setReflexes([]);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleToggle = async (id: number) => {
    setToggleId(id);
    setError(null);
    try {
      await toggleReflex(id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Toggle failed");
    } finally {
      setToggleId(null);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await createReflex({
        name: form.name.trim(),
        description: form.description.trim(),
        trigger_type: "keyword",
        trigger_pattern: form.trigger_pattern.trim(),
        action_type: form.action_type,
        approval_required: true,
        enabled: true,
      });
      setForm({
        name: "",
        description: "",
        trigger_pattern: "",
        action_type: "save_memory",
      });
      setShowCreate(false);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Create failed");
    }
  };

  const enabledCount = reflexes.filter((r) => r.enabled).length;
  const pendingFromReflex = events.filter((e) => e.result === "proposed").length;

  if (loading) {
    return <p className="text-muted">Loading reflex engine…</p>;
  }

  return (
    <div className="reflex-layout">
      <section className="panel reflex-status-panel">
        <div className="reflex-status-grid">
          <div>
            <div className="reflex-stat-label">Engine</div>
            <div className="reflex-stat-value">
              {online ? "Active" : "Offline"}
            </div>
          </div>
          <div>
            <div className="reflex-stat-label">Active reflexes</div>
            <div className="reflex-stat-value">
              {enabledCount}/{reflexes.length}
            </div>
          </div>
          <div>
            <div className="reflex-stat-label">Pending from reflexes</div>
            <div className="reflex-stat-value">{pendingFromReflex}</div>
          </div>
          <div>
            <div className="reflex-stat-label">Memory depth</div>
            <div className="reflex-stat-value">
              {status?.memory_count ?? 0}
            </div>
          </div>
        </div>
        <p className="reflex-loop-hint">
          Memory → Pattern → Intention → Proposed Action → Approval → Execution
          → Reflection → Stronger Memory
        </p>
      </section>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      <section className="reflex-section">
        <div className="reflex-section-header">
          <h2 className="reflex-section-title">Active Reflexes</h2>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => setShowCreate((v) => !v)}
          >
            {showCreate ? "Cancel" : "Create New Reflex"}
          </button>
        </div>

        {showCreate && (
          <form className="panel reflex-create-form" onSubmit={handleCreate}>
            <label>
              Name
              <input
                className="input"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
              />
            </label>
            <label>
              Purpose
              <textarea
                className="input"
                rows={2}
                value={form.description}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
                required
              />
            </label>
            <label>
              Trigger pattern (regex)
              <input
                className="input"
                value={form.trigger_pattern}
                onChange={(e) =>
                  setForm({ ...form, trigger_pattern: e.target.value })
                }
                required
              />
            </label>
            <label>
              Action type
              <select
                className="input"
                value={form.action_type}
                onChange={(e) =>
                  setForm({ ...form, action_type: e.target.value })
                }
              >
                <option value="save_memory">save_memory</option>
                <option value="write_project_note">write_project_note</option>
                <option value="create_plan">create_plan</option>
                <option value="summarize_recent_messages">
                  summarize_recent_messages
                </option>
              </select>
            </label>
            <button type="submit" className="btn btn-primary">
              Save Reflex
            </button>
          </form>
        )}

        {reflexes.length === 0 ? (
          <EmptyState
            title="No reflexes yet"
            description="Default reflexes seed on first backend start."
          />
        ) : (
          <div className="reflex-grid">
            {reflexes.map((reflex) => (
              <article key={reflex.id} className="reflex-card panel">
                <div className="reflex-card-header">
                  <h3 className="reflex-card-title">{reflex.name}</h3>
                  <span
                    className={`tag ${reflex.enabled ? "tag-green" : "tag-warning"}`}
                  >
                    {reflex.enabled ? "Enabled" : "Disabled"}
                  </span>
                </div>
                <p className="reflex-card-desc">{reflex.description}</p>
                <dl className="reflex-meta">
                  <div>
                    <dt>Trigger</dt>
                    <dd>
                      <code>{reflex.trigger_pattern}</code>
                    </dd>
                  </div>
                  <div>
                    <dt>Action</dt>
                    <dd>{reflex.action_type}</dd>
                  </div>
                  <div>
                    <dt>Approval</dt>
                    <dd>
                      {reflex.approval_required ? "Required" : "Auto"}
                    </dd>
                  </div>
                  <div>
                    <dt>Last used</dt>
                    <dd>
                      {reflex.last_used
                        ? new Date(reflex.last_used).toLocaleString()
                        : "Never"}
                    </dd>
                  </div>
                </dl>
                <button
                  type="button"
                  className="btn btn-sm btn-secondary"
                  disabled={toggleId === reflex.id || !online}
                  onClick={() => handleToggle(reflex.id)}
                >
                  {toggleId === reflex.id
                    ? "Updating…"
                    : reflex.enabled
                      ? "Disable"
                      : "Enable"}
                </button>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="reflex-section">
        <h2 className="reflex-section-title">Reflex History</h2>
        {events.length === 0 ? (
          <EmptyState
            title="No detections yet"
            description="Chat with Gebo to trigger pattern detection."
          />
        ) : (
          <div className="reflex-events">
            {events.slice(0, 20).map((event) => (
              <div key={event.id} className="reflex-event panel">
                <div className="reflex-event-header">
                  <span className="tag tag-green">
                    {event.reflex_name ?? "Reflex"}
                  </span>
                  <span className="reflex-event-time">
                    {new Date(event.detected_at).toLocaleString()}
                  </span>
                </div>
                <p className="reflex-event-input">{event.input_text}</p>
                <p className="reflex-event-result">
                  Result: {event.result ?? "—"}
                  {event.proposed_action_id
                    ? ` · Action #${event.proposed_action_id}`
                    : ""}
                </p>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
