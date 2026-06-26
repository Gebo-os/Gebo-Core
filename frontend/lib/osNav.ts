export const THEME_STORAGE_KEY = "gebo-os-theme";

export interface OsNavItem {
  label: string;
  href: string;
  icon: string;
  match: string[];
}

export interface OsTabItem {
  id: string;
  label: string;
  href: string;
  match: string[];
}

/** 11 sidebar items mapped to all Living Console routes */
export const OS_SIDEBAR: OsNavItem[] = [
  { label: "Command Center", href: "/", icon: "⌂", match: ["/"] },
  { label: "Chat", href: "/chat", icon: "◎", match: ["/chat"] },
  { label: "AI Studio", href: "/chat", icon: "✦", match: ["/chat"] },
  { label: "Memory Fabric", href: "/memory", icon: "◈", match: ["/memory"] },
  { label: "Presences", href: "/presences", icon: "⊞", match: ["/presences"] },
  { label: "Actions", href: "/actions", icon: "◇", match: ["/actions"] },
  { label: "Reflexes", href: "/reflexes", icon: "⟳", match: ["/reflexes"] },
  { label: "Evolution", href: "/evolution", icon: "⬡", match: ["/evolution"] },
  { label: "Build Log", href: "/build-log", icon: "▣", match: ["/build-log"] },
  { label: "Network", href: "/settings", icon: "⬡", match: ["/settings"] },
  { label: "Settings", href: "/settings", icon: "⚙", match: ["/settings"] },
];

export const OS_TABS: OsTabItem[] = [
  { id: "command", label: "Command Center", href: "/", match: ["/"] },
  { id: "compute", label: "Compute", href: "/chat", match: ["/chat"] },
  { id: "memory", label: "Memory", href: "/memory", match: ["/memory"] },
  { id: "network", label: "Network", href: "/presences", match: ["/presences"] },
  {
    id: "orchestration",
    label: "AI Orchestration",
    href: "/reflexes",
    match: ["/reflexes", "/evolution"],
  },
  { id: "security", label: "Security", href: "/actions", match: ["/actions"] },
  {
    id: "system",
    label: "System",
    href: "/settings",
    match: ["/settings", "/build-log"],
  },
];

export const QUICK_COMMANDS = [
  { label: "Optimize System", href: "/settings", icon: "⚡" },
  { label: "Deep Scan", href: "/reflexes", icon: "🔍" },
  { label: "Summarize Activity", href: "/build-log", icon: "📋" },
  { label: "Create Automation", href: "/reflexes", icon: "⟳" },
  { label: "Generate Report", href: "/build-log", icon: "📊" },
] as const;

export function isRouteActive(pathname: string, match: string[]): boolean {
  if (match.includes(pathname)) return true;
  return match.some(
    (m) => m !== "/" && pathname.startsWith(`${m}/`)
  );
}

/** Pick the most specific active sidebar item when multiple share a route */
export function getActiveSidebarIndex(
  pathname: string,
  items: OsNavItem[]
): number {
  const exact = items.findIndex((item) => item.href === pathname);
  if (exact >= 0) return exact;

  let best = -1;
  let bestLen = -1;
  items.forEach((item, i) => {
    if (!isRouteActive(pathname, item.match)) return;
    const len = item.href.length;
    if (len > bestLen) {
      bestLen = len;
      best = i;
    }
  });
  return best;
}
