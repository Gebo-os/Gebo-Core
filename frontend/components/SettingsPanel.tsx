"use client";

import { API_URL, getExportUrl } from "@/lib/api";
import { SAFETY_RULES } from "@/lib/constants";
import { useGebo } from "@/lib/GeboProvider";

export function SettingsPanel() {
  const {
    online,
    status,
    toggleConsent,
    consentLoading,
    geboStatus,
  } = useGebo();

  const pendingTotal =
    (status?.proposed_action_count ?? 0) +
    (status?.approved_action_count ?? 0);

  return (
    <>
      <section className="settings-section panel">
        <h2 className="settings-section-title">Privacy & Memory</h2>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Memory Collection</h4>
            <p>
              When enabled, Gebo auto-saves useful statements from chat into
              memory.
            </p>
          </div>
          <button
            type="button"
            className={`btn ${status?.consent ? "btn-danger" : "btn-primary"}`}
            onClick={toggleConsent}
            disabled={!online || consentLoading}
          >
            {consentLoading
              ? "Updating…"
              : status?.consent
                ? "Stop Memory Collection"
                : "Allow Memory Collection"}
          </button>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Export Memory</h4>
            <p>Download all memories, messages, settings, and actions as JSON.</p>
          </div>
          <a
            href={getExportUrl()}
            className="btn btn-secondary"
            target="_blank"
            rel="noopener noreferrer"
          >
            Export
          </a>
        </div>
      </section>

      <section className="settings-section panel">
        <h2 className="settings-section-title">System</h2>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>App Status</h4>
            <p>
              {online
                ? `Gebo is ${geboStatus.toLowerCase()}. Backend connected.`
                : "Backend Offline — start the FastAPI server on port 8000."}
            </p>
          </div>
          <span className={`tag ${online ? "tag-green" : "tag-danger"}`}>
            {online ? "Online" : "Offline"}
          </span>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Ollama Model</h4>
            <p>
              {status?.model ?? "Unknown"} — local inference via Ollama.
            </p>
          </div>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Backend URL</h4>
            <p>{API_URL}</p>
          </div>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>GitHub Repo Memory</h4>
            <p>
              Read-only ingest from GitHub or local git repos. Run{" "}
              <code>python scripts/ingest_repo_memory.py</code> in backend after{" "}
              <code>gh auth login</code>.
            </p>
          </div>
          <span className={`tag ${online ? "tag-green" : "tag-warning"}`}>
            {online ? "Backend ready" : "Offline"}
          </span>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Counts</h4>
            <p>
              {status?.memory_count ?? 0} memories ·{" "}
              {status?.message_count ?? 0} messages ·{" "}
              {pendingTotal} pending actions
            </p>
          </div>
        </div>
      </section>

      <section className="settings-section panel">
        <h2 className="settings-section-title">Local-Only</h2>
        <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>
          Gebo Core runs entirely on your machine. No cloud APIs, no external
          accounts, no internet required after setup. SQLite stores your data at{" "}
          <code style={{ fontSize: "0.8rem" }}>backend/data/gebo.db</code>.
        </p>
      </section>

      <section className="settings-section panel">
        <h2 className="settings-section-title">Safety Rules</h2>
        <ul className="settings-list">
          {SAFETY_RULES.map((rule) => (
            <li key={rule}>{rule}</li>
          ))}
        </ul>
      </section>

      <section className="settings-section">
        <div className="settings-warning">
          <strong>Reset not available.</strong> Destructive reset is not
          implemented in V0. To start fresh, manually delete{" "}
          <code>backend/data/gebo.db</code> while the backend is stopped.
        </div>
      </section>
    </>
  );
}
