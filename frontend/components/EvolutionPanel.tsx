"use client";

import { useCallback, useEffect, useState } from "react";
import { EmptyState } from "./EmptyState";
import {
  approveUpgrade,
  getEvolutionEvents,
  getEvolutionScores,
  getEvolutionStatus,
  getEvolutionUpgrades,
  rejectUpgrade,
  scoreAction,
  suggestUpgrade,
} from "@/lib/api";
import { useGebo } from "@/lib/GeboProvider";
import type {
  AutonomyScore,
  EvolutionEvent,
  EvolutionStatus,
  UpgradeSuggestion,
} from "@/lib/types";

const UPGRADE_TYPES = [
  "reflex",
  "tool",
  "agent",
  "memory_rule",
  "ui_improvement",
  "backend_improvement",
  "prompt_improvement",
  "workflow_improvement",
];

export function EvolutionPanel() {
  const { online } = useGebo();
  const [status, setStatus] = useState<EvolutionStatus | null>(null);
  const [events, setEvents] = useState<EvolutionEvent[]>([]);
  const [scores, setScores] = useState<AutonomyScore[]>([]);
  const [upgrades, setUpgrades] = useState<UpgradeSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  const [scoreForm, setScoreForm] = useState({
    action_id: "",
    mission_value: 7,
    speed_score: 7,
    risk_score: 7,
    approval_score: 8,
    memory_impact: 7,
    product_impact: 7,
    money_impact: 5,
    notes: "",
  });

  const [suggestForm, setSuggestForm] = useState({
    upgrade_type: "reflex",
    title: "",
    description: "",
    reason: "",
  });

  const refresh = useCallback(async () => {
    try {
      const [st, ev, sc, up] = await Promise.all([
        getEvolutionStatus(),
        getEvolutionEvents(),
        getEvolutionScores(),
        getEvolutionUpgrades(),
      ]);
      setStatus(st);
      setEvents(ev);
      setScores(sc);
      setUpgrades(up);
    } catch {
      setStatus(null);
      setEvents([]);
      setScores([]);
      setUpgrades([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleScore = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await scoreAction({
        action_id: Number(scoreForm.action_id),
        mission_value: scoreForm.mission_value,
        speed_score: scoreForm.speed_score,
        risk_score: scoreForm.risk_score,
        approval_score: scoreForm.approval_score,
        memory_impact: scoreForm.memory_impact,
        product_impact: scoreForm.product_impact,
        money_impact: scoreForm.money_impact,
        notes: scoreForm.notes,
      });
      setScoreForm((f) => ({ ...f, action_id: "", notes: "" }));
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Score failed");
    }
  };

  const handleSuggest = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await suggestUpgrade(suggestForm);
      setSuggestForm({
        upgrade_type: "reflex",
        title: "",
        description: "",
        reason: "",
      });
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Suggest failed");
    }
  };

  const handleApprove = async (id: number) => {
    setBusyId(id);
    setError(null);
    try {
      await approveUpgrade(id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Approve failed");
    } finally {
      setBusyId(null);
    }
  };

  const handleReject = async (id: number) => {
    setBusyId(id);
    setError(null);
    try {
      await rejectUpgrade(id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reject failed");
    } finally {
      setBusyId(null);
    }
  };

  const proposed = upgrades.filter((u) => u.status === "proposed");
  const approved = upgrades.filter((u) => u.status === "approved");
  const rejected = upgrades.filter((u) => u.status === "rejected");
  const reflexCandidates = proposed.filter((u) => u.upgrade_type === "reflex");
  const toolCandidates = proposed.filter((u) => u.upgrade_type === "tool");
  const agentCandidates = proposed.filter((u) => u.upgrade_type === "agent");
  const learned = events.filter((e) => e.score > 0 || e.status === "scored");

  const renderUpgradeCards = (items: UpgradeSuggestion[], empty: string) =>
    items.length === 0 ? (
      <p className="evolution-empty-hint">{empty}</p>
    ) : (
      <div className="reflex-grid">
        {items.map((upgrade) => (
          <article key={upgrade.id} className="reflex-card panel">
            <div className="reflex-card-header">
              <h3 className="reflex-card-title">{upgrade.title}</h3>
              <span className="tag tag-green">{upgrade.upgrade_type}</span>
            </div>
            <p className="reflex-card-desc">{upgrade.description}</p>
            <p className="evolution-reason">{upgrade.reason}</p>
            {upgrade.status === "proposed" && (
              <div className="reflex-card-buttons">
                <button
                  type="button"
                  className="btn btn-sm btn-primary"
                  disabled={busyId === upgrade.id || !online}
                  onClick={() => handleApprove(upgrade.id)}
                >
                  Approve
                </button>
                <button
                  type="button"
                  className="btn btn-sm btn-secondary"
                  disabled={busyId === upgrade.id || !online}
                  onClick={() => handleReject(upgrade.id)}
                >
                  Reject
                </button>
              </div>
            )}
            {upgrade.status !== "proposed" && (
              <span className="tag">{upgrade.status}</span>
            )}
          </article>
        ))}
      </div>
    );

  if (loading) {
    return <p className="text-muted">Loading evolution loop…</p>;
  }

  return (
    <div className="evolution-layout">
      <section className="panel evolution-status-panel">
        <p className="evolution-loop-hint">
          Observe → Decide → Propose → Approve → Execute → Reflect → Score →
          Upgrade → Remember
        </p>
        <div className="reflex-status-grid">
          <div>
            <div className="reflex-stat-label">Autonomy score</div>
            <div className="reflex-stat-value">
              {status?.average_autonomy_score ?? "—"}
              {status?.average_autonomy_score ? "/10" : ""}
            </div>
          </div>
          <div>
            <div className="reflex-stat-label">Lessons learned</div>
            <div className="reflex-stat-value">
              {status?.total_evolution_events ?? 0}
            </div>
          </div>
          <div>
            <div className="reflex-stat-label">Proposed upgrades</div>
            <div className="reflex-stat-value">
              {status?.proposed_upgrades ?? 0}
            </div>
          </div>
          <div>
            <div className="reflex-stat-label">Approved upgrades</div>
            <div className="reflex-stat-value">
              {status?.approved_upgrades ?? 0}
            </div>
          </div>
        </div>
        {status?.latest_lesson && (
          <p className="evolution-latest-lesson">
            Latest: {status.latest_lesson.slice(0, 200)}
            {status.latest_lesson.length > 200 ? "…" : ""}
          </p>
        )}
      </section>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      <section className="evolution-section">
        <h2 className="reflex-section-title">Score Action Outcome</h2>
        <form className="panel evolution-form" onSubmit={handleScore}>
          <label>
            Action ID
            <input
              className="input"
              type="number"
              min={1}
              value={scoreForm.action_id}
              onChange={(e) =>
                setScoreForm({ ...scoreForm, action_id: e.target.value })
              }
              required
              disabled={!online}
            />
          </label>
          <div className="evolution-score-grid">
            {(
              [
                ["mission_value", "Mission"],
                ["speed_score", "Speed"],
                ["risk_score", "Risk"],
                ["approval_score", "Approval"],
                ["memory_impact", "Memory"],
                ["product_impact", "Product"],
                ["money_impact", "Money"],
              ] as const
            ).map(([key, label]) => (
              <label key={key}>
                {label}
                <input
                  className="input"
                  type="number"
                  min={1}
                  max={10}
                  value={scoreForm[key]}
                  onChange={(e) =>
                    setScoreForm({
                      ...scoreForm,
                      [key]: Number(e.target.value),
                    })
                  }
                  disabled={!online}
                />
              </label>
            ))}
          </div>
          <label>
            Notes (outcome, next improvement)
            <textarea
              className="input"
              rows={3}
              value={scoreForm.notes}
              onChange={(e) =>
                setScoreForm({ ...scoreForm, notes: e.target.value })
              }
              disabled={!online}
            />
          </label>
          <button type="submit" className="btn btn-primary" disabled={!online}>
            Score &amp; Learn
          </button>
        </form>
      </section>

      <section className="evolution-section">
        <h2 className="reflex-section-title">What Gebo Learned</h2>
        {learned.length === 0 ? (
          <EmptyState
            title="No scored lessons yet"
            description="Score a completed action to teach Gebo what worked."
          />
        ) : (
          <div className="evolution-timeline">
            {learned.slice(0, 8).map((event) => (
              <div key={event.id} className="evolution-timeline-item panel">
                <div className="reflex-event-header">
                  <span className="tag tag-green">
                    {event.score}/10 · {event.source_type}
                  </span>
                  <span className="reflex-event-time">
                    {new Date(event.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="reflex-event-input">{event.lesson}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="evolution-section">
        <h2 className="reflex-section-title">New Reflex Candidates</h2>
        {renderUpgradeCards(
          reflexCandidates,
          "No reflex upgrades proposed yet."
        )}
      </section>

      <section className="evolution-section">
        <h2 className="reflex-section-title">New Tool Candidates</h2>
        {renderUpgradeCards(toolCandidates, "No tool upgrades proposed yet.")}
      </section>

      <section className="evolution-section">
        <h2 className="reflex-section-title">New Agent Candidates</h2>
        {renderUpgradeCards(agentCandidates, "No agent upgrades proposed yet.")}
      </section>

      <section className="evolution-section">
        <h2 className="reflex-section-title">Other Upgrade Suggestions</h2>
        {renderUpgradeCards(
          proposed.filter(
            (u) => !["reflex", "tool", "agent"].includes(u.upgrade_type)
          ),
          "No other pending upgrades."
        )}
      </section>

      <section className="evolution-section">
        <h2 className="reflex-section-title">Approved Evolutions</h2>
        {renderUpgradeCards(approved, "No approved upgrades yet.")}
      </section>

      <section className="evolution-section">
        <h2 className="reflex-section-title">Rejected Evolutions</h2>
        {renderUpgradeCards(rejected, "No rejected upgrades.")}
      </section>

      <section className="evolution-section">
        <h2 className="reflex-section-title">Suggest Upgrade</h2>
        <form className="panel evolution-form" onSubmit={handleSuggest}>
          <label>
            Type
            <select
              className="input"
              value={suggestForm.upgrade_type}
              onChange={(e) =>
                setSuggestForm({
                  ...suggestForm,
                  upgrade_type: e.target.value,
                })
              }
              disabled={!online}
            >
              {UPGRADE_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </label>
          <label>
            Title
            <input
              className="input"
              value={suggestForm.title}
              onChange={(e) =>
                setSuggestForm({ ...suggestForm, title: e.target.value })
              }
              required
              disabled={!online}
            />
          </label>
          <label>
            Description
            <textarea
              className="input"
              rows={2}
              value={suggestForm.description}
              onChange={(e) =>
                setSuggestForm({
                  ...suggestForm,
                  description: e.target.value,
                })
              }
              required
              disabled={!online}
            />
          </label>
          <label>
            Reason
            <textarea
              className="input"
              rows={2}
              value={suggestForm.reason}
              onChange={(e) =>
                setSuggestForm({ ...suggestForm, reason: e.target.value })
              }
              required
              disabled={!online}
            />
          </label>
          <button type="submit" className="btn btn-secondary" disabled={!online}>
            Propose Upgrade
          </button>
        </form>
      </section>

      <section className="evolution-section">
        <h2 className="reflex-section-title">Evolution Timeline</h2>
        {events.length === 0 ? (
          <EmptyState
            title="No evolution events yet"
            description="Complete actions and score outcomes to start learning."
          />
        ) : (
          <div className="evolution-timeline">
            {events.slice(0, 15).map((event) => (
              <div key={event.id} className="evolution-timeline-item panel">
                <div className="reflex-event-header">
                  <span className="tag">
                    {event.source_type}
                    {event.score > 0 ? ` · ${event.score}/10` : ""}
                  </span>
                  <span className="reflex-event-time">
                    {new Date(event.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="reflex-event-input">{event.lesson}</p>
                {event.recommended_upgrade && (
                  <p className="reflex-event-result">
                    Upgrade hint: {event.recommended_upgrade}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {scores.length > 0 && (
        <section className="evolution-section">
          <h2 className="reflex-section-title">Recent Outcomes</h2>
          {scores.slice(0, 8).map((s) => (
            <div key={s.id} className="evolution-score-row panel">
              Action #{s.action_id ?? "—"} · Total {s.total_score}/10
              {s.notes ? ` · ${s.notes.slice(0, 120)}` : ""}
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
