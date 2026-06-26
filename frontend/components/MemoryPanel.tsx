"use client";

import { useCallback, useMemo, useState } from "react";
import { EmptyState } from "./EmptyState";
import { MemoryCard } from "./MemoryCard";
import { MEMORY_TYPE_FILTERS, MEMORY_TYPES } from "@/lib/constants";
import { useGebo } from "@/lib/GeboProvider";
import { getExportUrl, saveMemory } from "@/lib/api";
import type { Memory } from "@/lib/types";

export function MemoryPanel() {
  const { memories, refreshMemories, online, triggerPulse } = useGebo();
  const [memoryType, setMemoryType] = useState("core");
  const [content, setContent] = useState("");
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [sourceFilter, setSourceFilter] = useState("all");
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sources = useMemo(() => {
    const set = new Set(memories.map((m) => m.source));
    return ["all", ...Array.from(set)];
  }, [memories]);

  const filtered = useMemo(() => {
    return memories.filter((m) => {
      const q = search.toLowerCase();
      const matchesSearch =
        !q ||
        m.content.toLowerCase().includes(q) ||
        m.memory_type.toLowerCase().includes(q);
      const matchesType =
        typeFilter === "all" ||
        m.memory_type.toLowerCase() === typeFilter ||
        (typeFilter === "core" && m.memory_type === "manual");
      const matchesSource =
        sourceFilter === "all" || m.source === sourceFilter;
      return matchesSearch && matchesType && matchesSource;
    });
  }, [memories, search, typeFilter, sourceFilter]);

  const handleSave = async () => {
    const text = content.trim();
    if (!text) return;
    setLoading(true);
    setError(null);
    try {
      await saveMemory(memoryType, text);
      setContent("");
      await refreshMemories();
      triggerPulse();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setLoading(false);
    }
  };

  const handleView = useCallback((m: Memory) => {
    setExpandedId((prev) => (prev === m.id ? null : m.id));
  }, []);

  return (
    <>
      <section className="panel memory-form-panel">
        <h2 className="panel-title">Add Memory</h2>
        <div className="memory-form-grid">
          <div>
            <label className="field-label" htmlFor="memory-type">
              Type
            </label>
            <select
              id="memory-type"
              className="field-select"
              value={memoryType}
              onChange={(e) => setMemoryType(e.target.value)}
            >
              {MEMORY_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="field-label" htmlFor="memory-content">
              Content
            </label>
            <textarea
              id="memory-content"
              className="field-textarea"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Write a permanent memory…"
              rows={3}
            />
          </div>
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleSave}
            disabled={loading || !content.trim() || !online}
          >
            {loading ? "Saving…" : "Save Memory"}
          </button>
        </div>
        {error && (
          <div className="alert alert-error" role="alert">
            {error}
          </div>
        )}
      </section>

      <div className="memory-toolbar">
        <input
          type="search"
          className="field-input"
          placeholder="Search memories…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search memories"
        />
        <select
          className="field-select"
          style={{ width: "auto", minWidth: "140px" }}
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          aria-label="Filter by type"
        >
          {MEMORY_TYPE_FILTERS.map((f) => (
            <option key={f.value} value={f.value}>
              {f.label}
            </option>
          ))}
        </select>
        <select
          className="field-select"
          style={{ width: "auto", minWidth: "140px" }}
          value={sourceFilter}
          onChange={(e) => setSourceFilter(e.target.value)}
          aria-label="Filter by source"
        >
          {sources.map((s) => (
            <option key={s} value={s}>
              {s === "all" ? "All sources" : s}
            </option>
          ))}
        </select>
        <a
          href={getExportUrl()}
          className="btn btn-secondary"
          target="_blank"
          rel="noopener noreferrer"
        >
          Export Memory
        </a>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          title="No memory yet"
          description="No memory yet. Add your first core memory to give Gebo continuity."
          action={
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => document.getElementById("memory-content")?.focus()}
            >
              Add Memory
            </button>
          }
        />
      ) : (
        <div className="memory-grid">
          {filtered.map((m) => (
            <MemoryCard
              key={m.id}
              memory={m}
              onView={handleView}
              expanded={expandedId === m.id}
            />
          ))}
        </div>
      )}
    </>
  );
}
