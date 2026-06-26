"use client";

import { usePathname } from "next/navigation";
import { AmbientField } from "./AmbientField";
import { BottomNav } from "./BottomNav";
import { OfflineBanner } from "./OfflineBanner";
import { Sidebar } from "./Sidebar";
import { TopCommandBar } from "./TopCommandBar";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="shell">
      <AmbientField calm={pathname !== "/"} />
      <Sidebar pathname={pathname} />
      <div className="shell-main">
        <TopCommandBar />
        <OfflineBanner />
        <main className="shell-content">
          <div className="shell-content-inner">{children}</div>
        </main>
      </div>
      <BottomNav pathname={pathname} />
    </div>
  );
}
