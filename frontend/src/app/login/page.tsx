"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { ApiError, api } from "@/lib/api";
import { usePrefs } from "@/lib/prefs";

export default function LoginPage() {
  const { t } = usePrefs();
  const router = useRouter();
  const [tab, setTab] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setInfo("");
    try {
      if (tab === "login") {
        await api.login(username.trim(), password);
        router.replace("/");
      } else {
        await api.register(username.trim(), email.trim(), password);
        setInfo(t.registered);
        setTab("login");
        setPassword("");
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel auth">
      <div className="tabs" role="tablist">
        <button role="tab" aria-selected={tab === "login"} className={tab === "login" ? "on" : ""} onClick={() => setTab("login")}>
          {t.login}
        </button>
        <button role="tab" aria-selected={tab === "register"} className={tab === "register" ? "on" : ""} onClick={() => setTab("register")}>
          {t.register}
        </button>
      </div>
      {info && <div className="notice ok">{info}</div>}
      {error && <div className="notice bad" role="alert">{error}</div>}
      <form onSubmit={onSubmit}>
        <div className="field">
          <label htmlFor="u">{t.username}</label>
          <input id="u" className="input" autoComplete="username" required value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>
        {tab === "register" && (
          <div className="field">
            <label htmlFor="e">{t.email}</label>
            <input id="e" type="email" className="input" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
        )}
        <div className="field">
          <label htmlFor="p">{t.password}</label>
          <input
            id="p"
            type="password"
            className="input"
            autoComplete={tab === "login" ? "current-password" : "new-password"}
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button className="btn primary" style={{ width: "100%" }} disabled={busy}>
          {tab === "login" ? t.login : t.register}
        </button>
      </form>
    </div>
  );
}
