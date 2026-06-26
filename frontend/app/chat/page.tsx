import { PageHeader } from "@/components/PageHeader";
import { ChatPanel } from "@/components/ChatPanel";

export default function ChatPage() {
  return (
    <>
      <PageHeader
        eyebrow="Conversation"
        title="Gebo Chat"
        description="Command console with memory awareness. Gebo recalls context and proposes actions when needed."
      />
      <ChatPanel />
    </>
  );
}
