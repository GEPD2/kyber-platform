"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { isLoggedIn } from "@/lib/api";
import { usePrefs } from "@/lib/prefs";

export function AppShell({ children }: { children: ReactNode }) {
  const { t, lang, setLang, theme, toggleTheme } = usePrefs();
  const path = usePathname() ?? "/";
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    setAuthed(isLoggedIn());
  }, [path]);

  const link = (href: string, label: string) => (
    <Link href={href} className={path === href || (href !== "/" && path.startsWith(href)) ? "active" : ""}>
      {label}
    </Link>
  );

  return (
    <div className="shell">
      <header className="topbar">
        <Link href="/" className="brand">
          <b>{t.appName}</b>
          <small>{t.appSub}</small>
        </Link>
        {authed && (
          <nav className="nav" aria-label="main">
            {link("/", t.levels)}
            {link("/leaderboard/", t.leaderboard)}
            {link("/account/", t.account)}
          </nav>
        )}
        <span className="spacer" />
        <button
          className="iconbtn"
          onClick={() => setLang(lang === "en" ? "el" : "en")}
          aria-label={t.language}
          title={t.language}
        >
          {lang === "en" ? "ΕΛ" : "EN"}
        </button>
        <button className="iconbtn" onClick={toggleTheme} aria-label={t.theme} title={t.theme}>
          {theme === "dark" ? "☀" : "☾"}
        </button>
      </header>
      <main className="main">{children}</main>
    </div>
  );
}
