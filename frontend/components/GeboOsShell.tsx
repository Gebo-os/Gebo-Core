"use client";

import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { OsNavLink } from "@/components/OsNavLink";
import { useGebo } from "@/lib/GeboProvider";
import {
  getActiveSidebarIndex,
  isRouteActive,
  OS_SIDEBAR,
  OS_TABS,
  QUICK_COMMANDS,
  THEME_STORAGE_KEY,
} from "@/lib/osNav";

function useOsTheme() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === "light" || stored === "dark") {
      setTheme(stored);
      return;
    }
    const prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;
    setTheme(prefersLight ? "light" : "dark");
  }, []);

  const toggleTheme = () => {
    setTheme((prev) => {
      const next = prev === "dark" ? "light" : "dark";
      localStorage.setItem(THEME_STORAGE_KEY, next);
      return next;
    });
  };

  return { theme, toggleTheme };
}

function useClock() {
  const [time, setTime] = useState("");
  useEffect(() => {
    const tick = () => {
      setTime(
        new Date().toLocaleTimeString([], {
          hour: "numeric",
          minute: "2-digit",
        })
      );
    };
    tick();
    const id = setInterval(tick, 30000);
    return () => clearInterval(id);
  }, []);
  return time;
}

function OsSidebar({ pathname }: { pathname: string }) {
  const { online, agentRuntime } = useGebo();
  const activeIndex = getActiveSidebarIndex(pathname, OS_SIDEBAR);
  const systemStatus = online
    ? agentRuntime?.healthy
      ? "Optimal"
      : "Degraded"
    : "Offline";

  return (
    <aside className="os-sidebar" aria-label="Gebo OS navigation">
      <nav className="os-sidebar-nav">
        {OS_SIDEBAR.map((item, index) => {
          const active = index === activeIndex;
          return (
            <OsNavLink
              key={item.label}
              href={item.href}
              className={`os-sidebar-link ${active ? "active" : ""}`}
              aria-current={active ? "page" : undefined}
            >
              <span className="os-sidebar-icon" aria-hidden="true">
                {item.icon}
              </span>
              {item.label}
            </OsNavLink>
          );
        })}
      </nav>
      <footer className="os-sidebar-footer">
        <div className="os-sidebar-user">
          <span className="os-sidebar-avatar" aria-hidden="true">
            G
          </span>
          <div>
            <strong>Gebo User</strong>
            <span>Administrator</span>
          </div>
        </div>
        <div className="os-sidebar-status">
          <span
            className={`os-sidebar-status-dot ${online ? "online" : "offline"}`}
            aria-hidden="true"
          />
          System Status {systemStatus}
        </div>
      </footer>
    </aside>
  );
}

function AssistantRail() {
  const { geboStatus, online, agentRuntime, status } = useGebo();
  const [listening, setListening] = useState(true);

  const memoryGb = ((status?.memory_count ?? 0) * 0.5 + 8).toFixed(0);
  const contextTokens = Math.min(
    128000,
    (status?.message_count ?? 0) * 512 + 32000
  );

  return (
    <aside className="os-assistant-rail">
      <header className="os-assistant-header">
        <strong>Gebo Assistant</strong>
        <span>Always at your service</span>
      </header>
      <div
        className={`os-assistant-wave ${listening ? "active" : "paused"}`}
        aria-hidden="true"
      >
        {Array.from({ length: 24 }).map((_, i) => (
          <span key={i} style={{ animationDelay: `${i * 0.06}s` }} />
        ))}
      </div>
      <p className="os-assistant-label">
        {online
          ? listening
            ? `${geboStatus} · Listening…`
            : `${geboStatus} · Paused`
          : "Backend offline"}
      </p>
      <button
        type="button"
        className="os-assistant-stop"
        onClick={() => setListening((v) => !v)}
      >
        {listening ? "Stop Listening" : "Start Listening"}
      </button>
      <div className="os-quick-section">
        <span className="os-quick-title">Quick Commands</span>
        <ul className="os-quick-commands">
          {QUICK_COMMANDS.map((cmd) => (
            <li key={cmd.label}>
              <OsNavLink href={cmd.href}>
                <span aria-hidden="true">{cmd.icon}</span>
                {cmd.label}
              </OsNavLink>
            </li>
          ))}
        </ul>
      </div>
      <footer className="os-assistant-stats">
        <div>
          <span>Assistant Memory</span>
          <strong>{memoryGb} GB</strong>
        </div>
        <div>
          <span>Context Window</span>
          <strong>{contextTokens.toLocaleString()} tokens</strong>
        </div>
        {agentRuntime && (
          <p className="os-assistant-foot">
            {agentRuntime.active_agents} agents ·{" "}
            {agentRuntime.healthy ? "optimal" : "degraded"}
          </p>
        )}
        <div className="os-assistant-mini-wave" aria-hidden="true">
          {Array.from({ length: 8 }).map((_, i) => (
            <span key={i} style={{ animationDelay: `${i * 0.1}s` }} />
          ))}
        </div>
      </footer>
    </aside>
  );
}

function OsCommandDock() {
  const router = useRouter();
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const text = query.trim();
    if (!text) return;
    sessionStorage.setItem("gebo-chat-pending", text);
    router.push("/chat");
  };

  return (
    <footer className="os-command-dock">
      <div className="os-dock-tools">
        <OsNavLink href="/chat" title="Terminal" aria-label="Terminal">
          &gt;_
        </OsNavLink>
        <OsNavLink href="/memory" title="Files" aria-label="Files">
          ▤
        </OsNavLink>
        <OsNavLink href="/" title="Apps" aria-label="Apps">
          ⊞
        </OsNavLink>
      </div>
      <form className="os-dock-input-wrap" onSubmit={handleSubmit}>
        <span className="os-dock-logo" aria-hidden="true">
          G
        </span>
        <input
          type="text"
          className="os-dock-input"
          placeholder="Ask Gebo anything…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label="Ask Gebo"
        />
        <button type="submit" className="os-dock-send" aria-label="Send">
          →
        </button>
      </form>
      <div className="os-dock-tools">
        <OsNavLink href="/actions" title="Actions" aria-label="Actions">
          ◇
        </OsNavLink>
        <OsNavLink href="/reflexes" title="AI" aria-label="AI">
          ✦
        </OsNavLink>
        <OsNavLink href="/build-log" title="Code" aria-label="Code">
          &lt;/&gt;
        </OsNavLink>
        <OsNavLink href="/presences" title="Devices" aria-label="Devices">
          ◉
        </OsNavLink>
      </div>
      <div className="os-dock-glow" aria-hidden="true" />
    </footer>
  );
}

function OsTopBar({
  pathname,
  theme,
  onToggleTheme,
  time,
}: {
  pathname: string;
  theme: "dark" | "light";
  onToggleTheme: () => void;
  time: string;
}) {
  const { online } = useGebo();

  return (
    <header className="os-pulse-header">
      <div className="os-pulse-brand">
        <OsNavLink href="/" className="os-pulse-brand-link">
          <span className="os-pulse-logo" aria-hidden="true">
            G
          </span>
          <span className="os-pulse-title">Gebo OS</span>
        </OsNavLink>
      </div>
      <nav className="os-pulse-tabs" aria-label="Gebo OS sections">
        {OS_TABS.map((tab) => {
          const active = isRouteActive(pathname, tab.match);
          return (
            <OsNavLink
              key={tab.id}
              href={tab.href}
              className={`os-pulse-tab ${active ? "active" : ""}`}
              aria-current={active ? "page" : undefined}
            >
              {tab.label}
            </OsNavLink>
          );
        })}
      </nav>
      <div className="os-pulse-header-actions">
        <OsNavLink href="/chat" className="os-header-icon" aria-label="Search">
          ⌕
        </OsNavLink>
        <OsNavLink href="/" className="os-header-icon" aria-label="App grid">
          ⊞
        </OsNavLink>
        <OsNavLink
          href="/actions"
          className="os-header-icon"
          aria-label="Notifications"
        >
          🔔
          {online && <span className="os-header-badge" aria-hidden="true" />}
        </OsNavLink>
        <OsNavLink
          href="/settings"
          className="os-header-icon"
          aria-label="Settings"
        >
          ⚙
        </OsNavLink>
        <button
          type="button"
          className="os-header-icon os-theme-toggle"
          onClick={onToggleTheme}
          aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
        >
          {theme === "dark" ? "☀" : "☾"}
        </button>
        <time className="os-header-time">{time}</time>
      </div>
    </header>
  );
}

function PulseLoadingSkeleton() {
  return (
    <div className="os-pulse-grid">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div key={i} className="skeleton os-widget-skeleton" />
      ))}
    </div>
  );
}

export function GeboOsShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { loading, online, motionEnabled } = useGebo();
  const { theme, toggleTheme } = useOsTheme();
  const time = useClock();
  const isPulse = pathname === "/";

  return (
    <div
      className={`os-pulse ${motionEnabled ? "os-motion-on" : "os-motion-off"}`}
      data-theme={theme}
    >
      {online === false && (
        <div className="os-offline-strip" role="status">
          Backend offline — start FastAPI on port 8000. Chat and memory are
          paused until Gebo reconnects.
        </div>
      )}
      <div className="os-pulse-frame">
        <OsSidebar pathname={pathname} />
        <div className="os-pulse-main">
          <OsTopBar
            pathname={pathname}
            theme={theme}
            onToggleTheme={toggleTheme}
            time={time}
          />
          <div className="os-pulse-body">
            <div
              className={`os-content-view ${isPulse ? "os-content-view--pulse" : "os-content-view--page"}`}
              key={pathname}
            >
              {loading && isPulse ? (
                <PulseLoadingSkeleton />
              ) : isPulse ? (
                children
              ) : (
                <div className="os-content-frame">{children}</div>
              )}
            </div>
            <AssistantRail />
          </div>
          <OsCommandDock />
        </div>
      </div>
    </div>
  );
}
