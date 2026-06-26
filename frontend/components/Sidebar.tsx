"use client";

import Link from "next/link";
import { NAV_ITEMS } from "@/lib/constants";
import { useGebo } from "@/lib/GeboProvider";

interface SidebarProps {
  pathname: string;
}

export function Sidebar({ pathname }: SidebarProps) {
  const { online, geboStatus } = useGebo();

  return (
    <aside className="sidebar" aria-label="Main navigation">
      <div className="sidebar-brand">
        <div className="sidebar-brand-mark">
          <div className="sidebar-logo" aria-hidden="true">
            G
          </div>
          <div>
            <div className="sidebar-title">Gebo</div>
            <div className="sidebar-subtitle">Living Console</div>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const active =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`sidebar-link ${active ? "active" : ""}`}
              aria-current={active ? "page" : undefined}
            >
              <span className="sidebar-link-dot" aria-hidden="true" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-status-pill">
          <span
            className={`sidebar-status-dot ${online ? "online" : "offline"}`}
            aria-hidden="true"
          />
          {online === null
            ? "Connecting…"
            : online
              ? geboStatus
              : "Backend Offline"}
        </div>
      </div>
    </aside>
  );
}
