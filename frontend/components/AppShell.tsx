"use client";

import { AmbientField } from "./AmbientField";
import { GeboOsShell } from "./GeboOsShell";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="shell shell-os-mockup">
      <AmbientField calm={false} />
      <div className="shell-main">
        <main className="shell-content">
          <div className="shell-content-inner">
            <GeboOsShell>{children}</GeboOsShell>
          </div>
        </main>
      </div>
    </div>
  );
}
