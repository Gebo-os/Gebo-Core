"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { COMMAND_DRAFT_KEY } from "@/lib/constants";

export function TopCommandBar() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem(COMMAND_DRAFT_KEY);
    if (stored) {
      setQuery(stored);
      sessionStorage.removeItem(COMMAND_DRAFT_KEY);
    }
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      const typing =
        target &&
        (target.tagName === "INPUT" ||
          target.tagName === "TEXTAREA" ||
          target.isContentEditable);

      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        inputRef.current?.focus();
        inputRef.current?.select();
        return;
      }
      if (e.key === "/" && !typing) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      const text = query.trim();
      if (!text) return;
      sessionStorage.setItem("gebo-chat-pending", text);
      setQuery("");
      inputRef.current?.blur();
      router.push("/chat");
    },
    [query, router]
  );

  return (
    <header className="topbar">
      <form className="topbar-command" onSubmit={handleSubmit} role="search">
        <span className="topbar-command-icon" aria-hidden="true">
          ⌘
        </span>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Escape") {
              setQuery("");
              inputRef.current?.blur();
            }
          }}
          placeholder="Ask, remember, build, plan, or search Gebo memory…"
          aria-label="Command input"
          aria-keyshortcuts="Control+K /"
        />
        <kbd>⌘K</kbd>
      </form>
    </header>
  );
}
