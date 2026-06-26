"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { CHAT_MODES } from "@/lib/constants";
import { useGebo } from "@/lib/GeboProvider";
import { saveMemory, sendChat } from "@/lib/api";
import type { ChatMessage, ChatMode } from "@/lib/types";

const PENDING_KEY = "gebo-chat-pending";

export function ChatPanel() {
  const { status, refresh, refreshMemories, triggerPulse, online } = useGebo();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<ChatMode>("ask");
  const [loading, setLoading] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!loading) {
      setElapsed(0);
      return;
    }
    const id = setInterval(() => setElapsed((e) => e + 1), 1000);
    return () => clearInterval(id);
  }, [loading]);

  useEffect(() => {
    const pending = sessionStorage.getItem(PENDING_KEY);
    if (pending) {
      setInput(pending);
      sessionStorage.removeItem(PENDING_KEY);
    }
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const getPrefixedMessage = useCallback(
    (text: string) => {
      const m = CHAT_MODES.find((c) => c.value === mode);
      if (!m || mode === "ask") return text;
      if (text.toLowerCase().startsWith(m.prefix.toLowerCase().trim())) {
        return text;
      }
      return m.prefix + text;
    },
    [mode]
  );

  const handleSend = useCallback(async () => {
    const raw = input.trim();
    if (!raw || loading || online === false) return;

    const text = getPrefixedMessage(raw);
    setInput("");
    setError(null);

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await sendChat(text);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: res.reply,
          recalled: res.recalled_memories,
          proposedActionIds: res.proposed_actions.map((a) => a.id),
          detectedReflexes: res.detected_reflexes,
          wikiSources: res.wiki_sources,
          timestamp: new Date().toISOString(),
        },
      ]);
      await refresh();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Chat failed";
      setError(msg);
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: msg.includes("Ollama")
            ? msg
            : `Could not reach Gebo: ${msg}`,
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, online, getPrefixedMessage, refresh]);

  const handleSaveAsMemory = async (content: string) => {
    try {
      await saveMemory("core", content);
      await refreshMemories();
      triggerPulse();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const consentOn = status?.consent ?? false;

  return (
    <div className="chat-layout">
      <div className="chat-toolbar">
        {CHAT_MODES.map((m) => (
          <button
            key={m.value}
            type="button"
            className={`chat-mode-btn ${mode === m.value ? "active" : ""}`}
            onClick={() => setMode(m.value)}
            aria-pressed={mode === m.value}
          >
            {m.label}
          </button>
        ))}
        <div className="chat-consent-badge">
          <span
            className={`chat-consent-dot ${consentOn ? "on" : "off"}`}
            aria-hidden="true"
          />
          Memory collection {consentOn ? "on" : "off"}
        </div>
      </div>

      <div className="chat-messages" role="log" aria-live="polite">
        {messages.length === 0 && (
          <EmptyStateInline text="Start a conversation. Gebo recalls memory and proposes actions when needed." />
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`chat-message ${msg.role}`}
          >
            <div className="chat-message-header">
              <span className="chat-message-role">
                {msg.role === "user" ? "Bb" : "Gebo"}
              </span>
              <span className="chat-message-time">
                {new Date(msg.timestamp).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
            <div className="chat-message-body">{msg.content}</div>

            {msg.recalled && msg.recalled.length > 0 && (
              <div className="chat-recalled">
                <div className="chat-recalled-label">Recalled memories</div>
                {msg.recalled.map((m) => (
                  <div key={m.id} className="chat-recalled-item">
                    <span className="tag tag-green">{m.memory_type}</span>{" "}
                    {m.content.length > 100
                      ? m.content.slice(0, 100) + "…"
                      : m.content}
                  </div>
                ))}
              </div>
            )}

            {msg.wikiSources && msg.wikiSources.length > 0 && (
              <div className="chat-recalled">
                <div className="chat-recalled-label">Referenced wiki</div>
                {msg.wikiSources.map((title) => (
                  <div key={title} className="chat-recalled-item">
                    <span className="tag">wiki</span> {title}
                  </div>
                ))}
              </div>
            )}

            {msg.detectedReflexes && msg.detectedReflexes.length > 0 && (
              <div className="chat-recalled">
                <div className="chat-recalled-label">Reflex detected</div>
                {msg.detectedReflexes.map((reflex) => (
                  <div key={reflex.reflex_id} className="chat-recalled-item">
                    <span className="tag tag-green">{reflex.name}</span>
                    {reflex.proposals_created > 0
                      ? ` · ${reflex.proposals_created} action(s) proposed`
                      : " · pattern matched"}
                  </div>
                ))}
              </div>
            )}

            {msg.role === "assistant" && (
              <div className="chat-message-actions">
                <button
                  type="button"
                  className="btn btn-sm btn-secondary"
                  onClick={() => handleSaveAsMemory(msg.content)}
                >
                  Save as Memory
                </button>
                {msg.proposedActionIds && msg.proposedActionIds.length > 0 && (
                  <Link href="/actions" className="btn btn-sm btn-ghost">
                    View proposed actions →
                  </Link>
                )}
                {msg.detectedReflexes && msg.detectedReflexes.length > 0 && (
                  <Link href="/reflexes" className="btn btn-sm btn-ghost">
                    View reflexes →
                  </Link>
                )}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="chat-message assistant">
            <div className="chat-message-header">
              <span className="chat-message-role">Gebo</span>
            </div>
            <div className="chat-message-body">
              <span className="loading-pulse" aria-hidden="true" /> Thinking
              {elapsed > 0 ? ` · ${elapsed}s` : "…"}
              {elapsed >= 6 && (
                <span
                  style={{
                    display: "block",
                    marginTop: "0.35rem",
                    fontSize: "0.78rem",
                    color: "var(--text-tertiary)",
                  }}
                >
                  Local model is generating — this can take a few seconds.
                </span>
              )}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      <div className="chat-composer">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            mode === "ask"
              ? "Message Gebo…"
              : CHAT_MODES.find((m) => m.value === mode)?.prefix + "…"
          }
          disabled={loading}
          aria-label="Chat message"
        />
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleSend}
          disabled={loading || !input.trim() || online === false}
        >
          {online === false ? "Offline" : "Send"}
        </button>
      </div>
    </div>
  );
}

function EmptyStateInline({ text }: { text: string }) {
  return (
    <p style={{ color: "var(--text-tertiary)", fontSize: "0.9rem", padding: "1rem 0" }}>
      {text}
    </p>
  );
}
