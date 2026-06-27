import type { ChatMode } from "./types";

export const CHAT_PENDING_KEY = "gebo-chat-pending";
export const CHAT_MODE_PENDING_KEY = "gebo-chat-mode";

/** Queue a message (and optional mode) then navigate to /chat or /studio */
export function queueChatNavigation(
  prompt: string,
  mode?: ChatMode,
  target: "chat" | "studio" = "chat"
): string {
  if (typeof sessionStorage !== "undefined") {
    sessionStorage.setItem(CHAT_PENDING_KEY, prompt);
    if (mode) {
      sessionStorage.setItem(CHAT_MODE_PENDING_KEY, mode);
    } else {
      sessionStorage.removeItem(CHAT_MODE_PENDING_KEY);
    }
  }
  return target === "studio" ? "/studio" : "/chat";
}

export function consumeChatQueue(): { prompt: string | null; mode: ChatMode | null } {
  if (typeof sessionStorage === "undefined") {
    return { prompt: null, mode: null };
  }
  const prompt = sessionStorage.getItem(CHAT_PENDING_KEY);
  const modeRaw = sessionStorage.getItem(CHAT_MODE_PENDING_KEY);
  if (prompt) sessionStorage.removeItem(CHAT_PENDING_KEY);
  if (modeRaw) sessionStorage.removeItem(CHAT_MODE_PENDING_KEY);
  const mode =
    modeRaw === "ask" ||
    modeRaw === "remember" ||
    modeRaw === "plan" ||
    modeRaw === "build" ||
    modeRaw === "search"
      ? modeRaw
      : null;
  return { prompt, mode };
}
