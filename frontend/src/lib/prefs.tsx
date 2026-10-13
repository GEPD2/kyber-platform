"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { DICT } from "./i18n";
import type { Lang } from "./types";

type Theme = "light" | "dark";

interface Prefs {
  lang: Lang;
  theme: Theme;
  t: (typeof DICT)["en"];
  setLang: (l: Lang) => void;
  toggleTheme: () => void;
}

const PrefsContext = createContext<Prefs | null>(null);

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* storage blocked: preference lasts for this page only */
  }
}

export function PrefsProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>("en");
  const [theme, setTheme] = useState<Theme>("dark");

  useEffect(() => {
    const storedLang = read("kyber_lang");
    setLangState(storedLang === "el" || storedLang === "en" ? storedLang
      : navigator.language.toLowerCase().startsWith("el") ? "el" : "en");
    setTheme(document.documentElement.dataset.theme === "light" ? "light" : "dark");
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    write("kyber_lang", l);
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme((prev) => {
      const next: Theme = prev === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      write("kyber_theme", next);
      return next;
    });
  }, []);

  return (
    <PrefsContext.Provider value={{ lang, theme, t: DICT[lang], setLang, toggleTheme }}>
      {children}
    </PrefsContext.Provider>
  );
}

export function usePrefs(): Prefs {
  const ctx = useContext(PrefsContext);
  if (!ctx) throw new Error("usePrefs outside PrefsProvider");
  return ctx;
}
