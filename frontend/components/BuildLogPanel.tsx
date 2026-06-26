"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { EmptyState } from "./EmptyState";
import { addBuildLog, deleteBuildLog, getBuildLogs } from "@/lib/buildLog";
import { saveMemory } from "@/lib/api";
import type { BuildLogEntry } from "@/lib/types";

export function BuildLogPanel() {
  const [entries, setEntries] = useState<BuildLogEntry[]>([]);
  const [built, setBuilt] = useState("");
  const [broke, setBroke] = useState("");
  const [learned, setLearned] = useState("");
  const [nextMission, setNextMission] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const refresh = useCallback(() => {
    setEntries(getBuildLogs());
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleSubmit = () => {
    if (!built.trim() && !learned.trim()) return;
    addBuildLog({
      built: built.trim(),
      broke: broke.trim(),
      learned: learned.trim(),
      next_mission: nextMission.trim(),
    });
    setBuilt("");
    setBroke("");
    setLearned("");
    setNextMission("");
    refresh();
    setMessage("Log entry saved.");
    setTimeout(() => setMessage(null), 3000);
  };

  const handleConvertToMemory = async (entry: BuildLogEntry) => {
    setLoading(true);
    try {
      const text = [
        `# Build Log — ${new Date(entry.created_at).toLocaleDateString()}`,
        entry.built && `Built: ${entry.built}`,
        entry.broke && `Broke: ${entry.broke}`,
        entry.learned && `Learned: ${entry.learned}`,
        entry.next_mission && `Next: ${entry.next_mission}`,
      ]
        .filter(Boolean)
        .join("\n");
      await saveMemory("build_log", text);
      setMessage("Converted to memory.");
    } catch {
      setMessage("Could not save memory. Check backend connection.");
    } finally {
      setLoading(false);
      setTimeout(() => setMessage(null), 3000);
    }
  };

  return (
    <>
      <section className="panel build-log-form">
        <h2 className="panel-title">Daily Log</h2>
        <div className="build-log-grid">
          <div>
            <label className="field-label" htmlFor="built">
              What was built
            </label>
            <textarea
              id="built"
              className="field-textarea"
              value={built}
              onChange={(e) => setBuilt(e.target.value)}
              placeholder="Shipped, fixed, or progressed…"
              rows={3}
            />
          </div>
          <div>
            <label className="field-label" htmlFor="broke">
              What broke
            </label>
            <textarea
              id="broke"
              className="field-textarea"
              value={broke}
              onChange={(e) => setBroke(e.target.value)}
              placeholder="Issues, blockers, regressions…"
              rows={3}
            />
          </div>
          <div>
            <label className="field-label" htmlFor="learned">
              What was learned
            </label>
            <textarea
              id="learned"
              className="field-textarea"
              value={learned}
              onChange={(e) => setLearned(e.target.value)}
              placeholder="Insights worth keeping…"
              rows={3}
            />
          </div>
          <div>
            <label className="field-label" htmlFor="next-mission">
              Next mission
            </label>
            <textarea
              id="next-mission"
              className="field-textarea"
              value={nextMission}
              onChange={(e) => setNextMission(e.target.value)}
              placeholder="Tomorrow's focus…"
              rows={3}
            />
          </div>
        </div>
        <button
          type="button"
          className="btn btn-primary"
          style={{ marginTop: "1rem" }}
          onClick={handleSubmit}
          disabled={!built.trim() && !learned.trim()}
        >
          Save Log Entry
        </button>
        {message && (
          <p style={{ marginTop: "0.75rem", fontSize: "0.85rem", color: "var(--green-dim)" }}>
            {message}
          </p>
        )}
      </section>

      {entries.length === 0 ? (
        <EmptyState
          title="No build logs yet"
          description="No build logs yet. Record what changed today."
        />
      ) : (
        entries.map((entry) => (
          <article key={entry.id} className="build-log-entry">
            <time className="build-log-date" dateTime={entry.created_at}>
              {new Date(entry.created_at).toLocaleString()}
            </time>
            {entry.built && (
              <LogField label="Built" value={entry.built} />
            )}
            {entry.broke && (
              <LogField label="Broke" value={entry.broke} />
            )}
            {entry.learned && (
              <LogField label="Learned" value={entry.learned} />
            )}
            {entry.next_mission && (
              <LogField label="Next mission" value={entry.next_mission} />
            )}
            <div className="build-log-actions">
              <button
                type="button"
                className="btn btn-sm btn-secondary"
                onClick={() => handleConvertToMemory(entry)}
                disabled={loading}
              >
                Convert to Memory
              </button>
              <Link
                href="/actions"
                className="btn btn-sm btn-ghost"
              >
                Create Action →
              </Link>
              <button
                type="button"
                className="btn btn-sm btn-ghost"
                onClick={() => {
                  deleteBuildLog(entry.id);
                  refresh();
                }}
              >
                Remove
              </button>
            </div>
          </article>
        ))
      )}
    </>
  );
}

function LogField({ label, value }: { label: string; value: string }) {
  return (
    <div className="build-log-field">
      <div className="build-log-field-label">{label}</div>
      <div className="build-log-field-value">{value}</div>
    </div>
  );
}
