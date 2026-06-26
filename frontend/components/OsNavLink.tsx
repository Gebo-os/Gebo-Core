"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useGebo } from "@/lib/GeboProvider";

type OsNavLinkProps = React.ComponentProps<typeof Link>;

export function OsNavLink({ href, onClick, ...props }: OsNavLinkProps) {
  const router = useRouter();
  const { motionEnabled } = useGebo();

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    onClick?.(e);
    if (e.defaultPrevented) return;

    if (
      e.metaKey ||
      e.ctrlKey ||
      e.shiftKey ||
      e.altKey ||
      e.button !== 0
    ) {
      return;
    }

    const target =
      typeof href === "string"
        ? href
        : typeof href === "object" && href.pathname
          ? href.pathname
          : null;

    if (!target || !motionEnabled) return;

    const doc = document as Document & {
      startViewTransition?: (cb: () => void) => { finished: Promise<void> };
    };

    if (!doc.startViewTransition) return;

    e.preventDefault();
    doc.startViewTransition(() => {
      router.push(target);
    });
  };

  return <Link href={href} onClick={handleClick} {...props} />;
}
