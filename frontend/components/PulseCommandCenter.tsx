"use client";

import {
  ComputeOverviewWidget,
  DeviceContinuityWidget,
  GlobalNetworkWidget,
  IntelligenceFeed,
  MemoryFabricWidget,
  SecurityWidget,
  SystemOrchestration,
  SystemOverviewWidget,
} from "@/components/OsDashboard";
import { OsCenterEmblem } from "@/components/OsCenterEmblem";

export function PulseCommandCenter() {
  return (
    <div className="os-pulse-grid">
      <div className="os-pulse-col os-pulse-col-left">
        <SystemOverviewWidget />
        <ComputeOverviewWidget />
        <MemoryFabricWidget />
      </div>

      <div className="os-pulse-col os-pulse-col-center">
        <OsCenterEmblem />
        <SystemOrchestration />
      </div>

      <div className="os-pulse-col os-pulse-col-right">
        <GlobalNetworkWidget />
        <IntelligenceFeed />
        <DeviceContinuityWidget />
        <SecurityWidget />
      </div>
    </div>
  );
}
