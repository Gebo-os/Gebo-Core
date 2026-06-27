import { PageHeader } from "@/components/PageHeader";
import { ChatPanel } from "@/components/ChatPanel";

export default function StudioPage() {
  return (
    <>
      <PageHeader
        eyebrow="Creation"
        title="AI Studio"
        description="Build mode by default — sketch features, code, and plans with Gebo's memory context."
      />
      <ChatPanel defaultMode="build" studio />
    </>
  );
}
