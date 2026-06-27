"use client";

import { useCallback, useEffect, useState } from "react";
import {
  getCliStatus,
  getIntegrationsStatus,
  getKnowledgeStatus,
  runLearningCycle,
  runWebKnowledgeCollect,
} from "@/lib/api";
import type { CliStatus, IntegrationsStatus, KnowledgeStatus } from "@/lib/types";

export function IntegrationsLearnPanel() {
  const [integrations, setIntegrations] = useState<IntegrationsStatus | null>(null);
  const [clis, setClis] = useState<CliStatus | null>(null);
  const [knowledge, setKnowledge] = useState<KnowledgeStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [collecting, setCollecting] = useState(false);
  const [webCollecting, setWebCollecting] = useState(false);
  const [lastResult, setLastResult] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [i, c, k] = await Promise.all([
        getIntegrationsStatus(),
        getCliStatus(),
        getKnowledgeStatus(),
      ]);
      setIntegrations(i);
      setClis(c);
      setKnowledge(k);
    } catch {
      setIntegrations(null);
      setClis(null);
      setKnowledge(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleLearningCycle = async () => {
    setCollecting(true);
    setLastResult(null);
    try {
      const result = await runLearningCycle();
      setLastResult(result.lesson ?? "Learning cycle complete.");
      await refresh();
    } catch (e) {
      setLastResult(e instanceof Error ? e.message : "Learning cycle failed.");
    } finally {
      setCollecting(false);
    }
  };

  const handleWebCollect = async () => {
    setWebCollecting(true);
    setLastResult(null);
    try {
      const result = await runWebKnowledgeCollect();
      const gh = result.github?.ingested ?? 0;
      const docs = result.official_docs?.ingested ?? 0;
      setLastResult(`Web collect: ${gh} GitHub + ${docs} doc memories ingested.`);
      await refresh();
    } catch (e) {
      setLastResult(e instanceof Error ? e.message : "Web collection failed.");
    } finally {
      setWebCollecting(false);
    }
  };

  if (loading && !integrations) {
    return <p className="settings-muted">Loading integrations…</p>;
  }

  const learnable =
    integrations?.items.filter((x) => x.mode === "learnable") ?? [];
  const connectors =
    integrations?.items.filter((x) => x.mode === "connector") ?? [];

  return (
    <>
      <section className="settings-section panel">
        <h2 className="settings-section-title">Integrations &amp; Learning</h2>
        <div className="settings-row">
          <div className="settings-row-info">
            <h4>Learning Cycle</h4>
            <p>
              Ingest OSS catalog, official doc metadata, integration learnables,
              and files from <code>backend/data/private-docs/</code> into Gebo memory.
            </p>
          </div>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleLearningCycle}
            disabled={collecting || webCollecting}
          >
            {collecting ? "Collecting…" : "Run Learning Cycle"}
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleWebCollect}
            disabled={collecting || webCollecting || !knowledge?.web_fetch_ready}
            title={
              knowledge?.web_fetch_ready
                ? "Fetch GitHub READMEs and official docs from the web"
                : "Enable internet access in Settings first"
            }
          >
            {webCollecting ? "Fetching web…" : "Web Deep Collect"}
          </button>
        </div>
        {lastResult && (
          <p className="settings-muted" style={{ marginTop: "0.75rem" }}>
            {lastResult}
          </p>
        )}
        {knowledge && (
          <div className="settings-row">
            <div className="settings-row-info">
              <h4>Knowledge Stats</h4>
              <p>
                {knowledge.knowledge_memory_count} knowledge memories ·{" "}
                {knowledge.web_knowledge_memory_count ?? 0} web-fetched ·{" "}
                {knowledge.catalog_oss_count} OSS refs ·{" "}
                {knowledge.catalog_docs_count} doc URLs ·{" "}
                {knowledge.private_doc_count} private files
                {!knowledge.internet_access && (
                  <> · <strong>internet off</strong> — enable for web fetch</>
                )}
              </p>
            </div>
          </div>
        )}
      </section>

      <section className="settings-section panel">
        <h2 className="settings-section-title">CLI Toolkit</h2>
        <p className="settings-muted">
          {clis
            ? `${clis.available} / ${clis.total} CLIs available locally`
            : "Backend offline"}
        </p>
        <ul className="os-integration-list">
          {(clis?.items ?? []).map((cli) => (
            <li key={cli.id} className={cli.available ? "ok" : "missing"}>
              <strong>{cli.name}</strong>
              <span>{cli.available ? cli.version ?? "installed" : cli.install_hint}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="settings-section panel">
        <h2 className="settings-section-title">Learnable (Gebo studies docs)</h2>
        <ul className="os-integration-list">
          {learnable.map((item) => (
            <li key={item.id} className="ok">
              <strong>{item.name}</strong>
              <span>{item.category}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="settings-section panel">
        <h2 className="settings-section-title">Connectors (need credentials)</h2>
        <ul className="os-integration-list">
          {connectors.map((item) => (
            <li key={item.id} className={item.configured ? "ok" : "missing"}>
              <strong>{item.name}</strong>
              <span>{item.status}</span>
            </li>
          ))}
        </ul>
        <p className="settings-muted">
          Official docs: <code>docs/official/</code> · Workflow:{" "}
          <code>docs/official/MICRO-WORKFLOW.md</code>
        </p>
      </section>
    </>
  );
}
