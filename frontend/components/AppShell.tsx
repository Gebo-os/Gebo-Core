"use client";

import { usePathname } from "next/navigation";
import { BottomNav } from "./BottomNav";
import { Sidebar } from "./Sidebar";
import { TopCommandBar } from "./TopCommandBar";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="shell">
      <Sidebar pathname={pathname} />
      <div className="shell-main">
        <TopCommandBar />
        <main className="shell-content">
          <div className="shell-content-inner">{children}</div>
        </main>
      </div>
      <BottomNav pathname={pathname} />
    </div>
  );
}
