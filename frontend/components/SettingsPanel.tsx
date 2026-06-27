"use client";

import { useEffect, useState } from "react";
import { IntegrationsLearnPanel } from "@/components/IntegrationsLearnPanel";
import { downloadMemoryExport, getApiUrl } from "@/lib/api";
import { SAFETY_RULES } from "@/lib/constants";
import { useGebo } from "@/lib/GeboProvider";
import { isRecaptchaConfigured } from "@/lib/recaptcha";

export function SettingsPanel() {
  const {
    online,
    status,
    codex,
    wiki,
    motionEnabled,
    setMotionEnabled,
    toggleConsent,
    consentLoading,
    geboStatus,
    agentRuntime,
    network,
    toggleInternetAccess,
    networkLoading,
  } = useGebo();
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === "undefined" || !window.location.hash) return;
    const id = window.location.hash.slice(1);
    const el = document.getElementById(id);
    el?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  const handleExport = async () => {
    setExportError(null);
    setExporting(true);
    try {
      await downloadMemoryExport();
    } catch (err) {
      setExportError(err instanceof Error ? err.message : "Export failed");
    } finally {
      setExporting(false);
    }
  };

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
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleExport}
            disabled={!online || exporting}
          >
            {exporting ? "Exporting…" : "Export"}
          </button>
        </div>
        {exportError && (
          <p className="alert alert-error" role="alert">
            {exportError}
          </p>
        )}
      </section>

      <section className="settings-section panel">
        <h2 className="settings-section-title">Appearance</h2>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Generative Motion</h4>
            <p>
              Animated living backdrop and pulse. Turn off for a calmer, lighter
              interface (also reduces CPU use).
            </p>
          </div>
          <button
            type="button"
            className={`btn ${motionEnabled ? "btn-secondary" : "btn-primary"}`}
            onClick={() => setMotionEnabled(!motionEnabled)}
            aria-pressed={motionEnabled}
          >
            {motionEnabled ? "Turn Off Motion" : "Turn On Motion"}
          </button>
        </div>
      </section>

      <section id="network" className="settings-section panel">
        <h2 className="settings-section-title">Network &amp; Localhost</h2>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Internet Access (CORS)</h4>
            <p>
              When enabled, the backend accepts requests from any origin — full
              network access for LAN devices and remote clients. When disabled,
              only localhost origins are allowed.
            </p>
          </div>
          <button
            type="button"
            className={`btn ${network?.internet_access ? "btn-danger" : "btn-primary"}`}
            onClick={toggleInternetAccess}
            disabled={!online || networkLoading || !network}
          >
            {networkLoading
              ? "Updating…"
              : network?.internet_access
                ? "Restrict to Localhost"
                : "Enable Full Internet Access"}
          </button>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>CORS Mode</h4>
            <p>
              {network?.cors_mode === "open"
                ? "Open — any origin can reach the API."
                : "Localhost — restricted to local dev origins."}
            </p>
          </div>
          <span
            className={`tag ${
              network?.cors_mode === "open" ? "tag-green" : "tag-warning"
            }`}
          >
            {network?.cors_mode ?? "—"}
          </span>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Living Console (Frontend)</h4>
            <p>
              <a
                href={network?.frontend_url ?? "http://localhost:3000"}
                target="_blank"
                rel="noopener noreferrer"
                className="os-widget-link"
              >
                {network?.frontend_url ?? "http://localhost:3000"}
              </a>
            </p>
          </div>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Backend API</h4>
            <p>
              <a
                href={network?.backend_url ?? getApiUrl()}
                target="_blank"
                rel="noopener noreferrer"
                className="os-widget-link"
              >
                {network?.backend_url ?? getApiUrl()}
              </a>
              {" · "}
              bind <code>{network?.bind_host ?? "0.0.0.0"}</code>
            </p>
          </div>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Quick Links</h4>
            <p style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem" }}>
              <a href="/" className="os-widget-link">Pulse</a>
              <a href="/chat" className="os-widget-link">Chat</a>
              <a href="/memory" className="os-widget-link">Memory</a>
              <a href="/actions" className="os-widget-link">Actions</a>
              <a href="/reflexes" className="os-widget-link">Reflexes</a>
              <a href="/evolution" className="os-widget-link">Evolution</a>
            </p>
          </div>
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
            <p>{network?.backend_url ?? getApiUrl()}</p>
          </div>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Gebo Lattice Prompting</h4>
            <p>
              Expert style #01 — Identity → Memory → Architecture → Output.
              See <code>prompts/01-gebo-lattice-prompting.md</code> and{" "}
              <code>memory/core/00-default-gebo-build-prompt.md</code>.
            </p>
          </div>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Gebo Ecosystem Master</h4>
            <p>
              Official master prompt — Presence, Memory, Owner Node, native tools,
              build priority. See <code>GEBO-ECOSYSTEM-MASTER.md</code> in repo root.
            </p>
          </div>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Gebo Gym</h4>
            <p>
              Official training loop: Learn → Grow → Act → Verify → Repeat.
              Run <code>.\scripts\gebo-gym.ps1</code> from the repo root. See{" "}
              <code>GEBO-GYM.md</code>.
            </p>
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
            <h4>Agent Runtime</h4>
            <p>
              Internal 24/7 supervisor — {agentRuntime?.active_agents ?? "—"} active
              workers ticking every {agentRuntime?.tick_interval_sec ?? 30}s.
              Agents are never shown in UI; this is ops-only heartbeat.
            </p>
          </div>
          <span
            className={`tag ${
              agentRuntime?.healthy && agentRuntime?.running
                ? "tag-green"
                : online
                  ? "tag-warning"
                  : "tag-danger"
            }`}
          >
            {!online
              ? "Offline"
              : agentRuntime?.healthy
                ? "Optimal"
                : agentRuntime?.running
                  ? "Degraded"
                  : "Stopped"}
          </span>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Codex Parallel Lane</h4>
            <p>
              Runs alongside agent ticks every {agentRuntime?.tick_interval_sec ?? 30}s.
              {agentRuntime?.codex_lane
                ? ` Status: ${agentRuntime.codex_lane.status} — ${agentRuntime.codex_lane.message}`
                : " Start backend to see lane status."}
            </p>
          </div>
          <span
            className={`tag ${
              agentRuntime?.codex_lane?.available ? "tag-green" : "tag-warning"
            }`}
          >
            {agentRuntime?.codex_lane?.available ? "Parallel" : "Codex off"}
          </span>
        </div>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Custom Model</h4>
            <p>
              Build <code>gebo-custom</code> with{" "}
              <code>.\scripts\create-gebo-model.ps1</code>, then set{" "}
              <code>OLLAMA_MODEL=gebo-custom</code> in backend/.env.
            </p>
          </div>
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
        <h2 className="settings-section-title">Codex Engine</h2>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Codex CLI</h4>
            <p>
              {codex?.available
                ? `${codex.version ?? "Connected"} — Gebo can run approval-gated review and build tasks.`
                : "Not detected. Install with: npm install -g @openai/codex"}
            </p>
          </div>
          <span className={`tag ${codex?.available ? "tag-green" : "tag-warning"}`}>
            {codex?.available ? "Connected" : "Not found"}
          </span>
        </div>
        {codex?.available && (
          <>
            <div className="settings-row">
              <div className="settings-row-info">
                <h4>Working Directory</h4>
                <p><code style={{ fontSize: "0.8rem" }}>{codex.workdir}</code></p>
              </div>
            </div>
            <div className="settings-row">
              <div className="settings-row-info">
                <h4>How to use</h4>
                <p>
                  In Chat, say &ldquo;review with codex&rdquo; or &ldquo;use codex to build&hellip;&rdquo;.
                  Gebo proposes an action; approve and run it in the Actions queue.
                  Build tasks can write files and always require your approval.
                </p>
              </div>
            </div>
          </>
        )}
      </section>

      <section className="settings-section panel">
        <h2 className="settings-section-title">Knowledge Wiki</h2>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Offline Wiki</h4>
            <p>
              {wiki?.available
                ? `${wiki.title ?? "ZIM loaded"} — Gebo consults this for facts when memory has no answer (mode: ${wiki.auto_mode}).`
                : wiki?.enabled
                  ? "Enabled, but no ZIM file found. Drop a .zim into backend/data/wiki/."
                  : "Disabled."}
            </p>
          </div>
          <span className={`tag ${wiki?.available ? "tag-green" : "tag-warning"}`}>
            {wiki?.available ? "Loaded" : wiki?.enabled ? "No ZIM" : "Off"}
          </span>
        </div>
        {wiki?.available ? (
          <>
            <div className="settings-row">
              <div className="settings-row-info">
                <h4>ZIM File</h4>
                <p>
                  <code style={{ fontSize: "0.8rem" }}>{wiki.zim_path}</code>
                  {wiki.article_count != null && (
                    <> · {wiki.article_count.toLocaleString()} articles</>
                  )}
                  {wiki.has_fulltext_index === false && (
                    <> · no full-text index (search disabled)</>
                  )}
                </p>
              </div>
            </div>
            <div className="settings-row">
              <div className="settings-row-info">
                <h4>How it works</h4>
                <p>
                  Fully offline. When you ask a research/factual question with no
                  matching memory, Gebo searches the wiki and uses it as
                  reference. No internet is used.
                </p>
              </div>
            </div>
          </>
        ) : (
          <div className="settings-row">
            <div className="settings-row-info">
              <h4>Add a knowledge base</h4>
              <p>
                Download a free ZIM (e.g. Simple English Wikipedia) from{" "}
                <code>download.kiwix.org/zim/</code> and place it in{" "}
                <code style={{ fontSize: "0.8rem" }}>backend/data/wiki/</code>,
                then restart the backend.
              </p>
            </div>
          </div>
        )}
      </section>

      <section className="settings-section panel">
        <h2 className="settings-section-title">Production Security</h2>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>reCAPTCHA Enterprise</h4>
            <p>
              {isRecaptchaConfigured()
                ? "Site key configured — ready for login/register when Firebase Auth UI ships."
                : "Not configured. Set NEXT_PUBLIC_RECAPTCHA_SITE_KEY for production bot protection."}
            </p>
          </div>
          <span
            className={`tag ${isRecaptchaConfigured() ? "tag-green" : "tag-warning"}`}
          >
            {isRecaptchaConfigured() ? "Configured" : "Stub"}
          </span>
        </div>
      </section>

      <section className="settings-section panel">
        <h2 className="settings-section-title">Local-First Core</h2>
        <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>
          Gebo Core runs on your machine with SQLite at{" "}
          <code style={{ fontSize: "0.8rem" }}>backend/data/gebo.db</code>.
          Internet access controls who can reach the API — Ollama and wiki remain
          local unless you explicitly use external tools via Codex.
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

      <IntegrationsLearnPanel />

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
