"use client";

import Link from "next/link";
import { NAV_ITEMS } from "@/lib/constants";

interface BottomNavProps {
  pathname: string;
}

export function BottomNav({ pathname }: BottomNavProps) {
  return (
    <nav className="bottomnav" aria-label="Mobile navigation">
      <div className="bottomnav-inner">
        {NAV_ITEMS.map((item) => {
          const active =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`bottomnav-link ${active ? "active" : ""}`}
              aria-current={active ? "page" : undefined}
            >
              <span className="bottomnav-dot" aria-hidden="true" />
              {item.shortLabel}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
