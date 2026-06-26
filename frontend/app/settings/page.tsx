import { PageHeader } from "@/components/PageHeader";
import { SettingsPanel } from "@/components/SettingsPanel";

export default function SettingsPage() {
  return (
    <>
      <PageHeader
        eyebrow="Control"
        title="Settings"
        description="Privacy, model, memory, and system configuration."
      />
      <SettingsPanel />
    </>
  );
}
