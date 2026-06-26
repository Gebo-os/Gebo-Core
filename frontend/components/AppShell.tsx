"use client";

import { usePathname } from "next/navigation";
import { AmbientField } from "./AmbientField";
import { BottomNav } from "./BottomNav";
import { OfflineBanner } from "./OfflineBanner";
import { Sidebar } from "./Sidebar";
import { TopCommandBar } from "./TopCommandBar";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isPulse = pathname === "/";

  return (
    <div className={`shell ${isPulse ? "shell-pulse" : ""}`}>
      <AmbientField calm={!isPulse} />
      <Sidebar pathname={pathname} />
      <div className="shell-main">
        {!isPulse && <TopCommandBar />}
        <OfflineBanner />
        <main className="shell-content">
          <div className="shell-content-inner">{children}</div>
        </main>
      </div>
      <BottomNav pathname={pathname} />
    </div>
  );
}
