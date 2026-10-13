import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";
import { AppShell } from "@/components/AppShell";
import { PrefsProvider } from "@/lib/prefs";
import "@/styles/tokens.css";
import "@/styles/app.css";

export const metadata: Metadata = {
  title: "ML-KEM Lab",
  description: "Learn CRYSTALS-Kyber / ML-KEM (FIPS 203) from modular arithmetic to the C reference.",
};

export const viewport: Viewport = { width: "device-width", initialScale: 1 };

// Runs before paint so the stored or system theme applies without a flash.
const THEME_BOOT = `try{var t=localStorage.getItem("kyber_theme");if(t!=="light"&&t!=="dark"){t=matchMedia("(prefers-color-scheme: light)").matches?"light":"dark"}document.documentElement.dataset.theme=t}catch(e){document.documentElement.dataset.theme="dark"}`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_BOOT }} />
      </head>
      <body>
        <PrefsProvider>
          <AppShell>{children}</AppShell>
        </PrefsProvider>
      </body>
    </html>
  );
}
