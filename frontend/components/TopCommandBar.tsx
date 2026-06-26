"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { COMMAND_DRAFT_KEY } from "@/lib/constants";

export function TopCommandBar() {
  const router = useRouter();
  const [query, setQuery] = useState("");

  useEffect(() => {
    const stored = sessionStorage.getItem(COMMAND_DRAFT_KEY);
    if (stored) {
      setQuery(stored);
      sessionStorage.removeItem(COMMAND_DRAFT_KEY);
    }
  }, []);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      const text = query.trim();
      if (!text) return;
      sessionStorage.setItem("gebo-chat-pending", text);
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
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask, remember, build, plan, or search Gebo memory…"
          aria-label="Command input"
        />
        <kbd>Enter</kbd>
      </form>
    </header>
  );
}
