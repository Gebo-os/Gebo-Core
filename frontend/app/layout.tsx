import type { Metadata } from "next";
import { AppShell } from "@/components/AppShell";
import { GeboProvider } from "@/lib/GeboProvider";
import "./globals.css";

export const metadata: Metadata = {
  title: "Gebo Living Console",
  description: "Private memory intelligence for Bb",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <GeboProvider>
          <AppShell>{children}</AppShell>
        </GeboProvider>
      </body>
    </html>
  );
}
