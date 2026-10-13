"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState, type FormEvent } from "react";
import { ErrorState, Loading } from "@/components/State";
import { ApiError, api } from "@/lib/api";
import { usePrefs } from "@/lib/prefs";
import type { Me } from "@/lib/types";
import { useAuthGuard } from "@/lib/useAuthGuard";

export default function AccountPage() {
  const ok = useAuthGuard();
  const router = useRouter();
  const { t, lang } = usePrefs();
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState("");
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const load = useCallback(async () => {
    setError("");
    try {
      setMe(await api.me());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    if (ok) void load();
  }, [ok, load]);

  async function onChange(e: FormEvent) {
    e.preventDefault();
    setMsg(null);
    try {
      await api.changePassword(current, next);
      setMsg({ ok: true, text: t.saved });
      setCurrent("");
      setNext("");
    } catch (err) {
      setMsg({ ok: false, text: err instanceof ApiError ? err.message : String(err) });
    }
  }

  async function onLogout() {
    await api.logout().catch(() => undefined);
    router.replace("/login/");
  }

  if (!ok) return null;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!me) return <Loading />;

  return (
    <>
      <h1 className="h1">{t.profile}</h1>
      <p className="lead">
        {me.username} · {me.email} · {t.memberSince} {new Date(me.created_at).toLocaleDateString(lang === "el" ? "el-GR" : "en-GB")}
      </p>
      <div className="stats">
        <div className="panel stat"><div className="v">{me.stats.total_score}</div><div className="k">{t.score}</div></div>
        <div className="panel stat"><div className="v">{me.stats.total_correct}</div><div className="k">{t.totalCorrect}</div></div>
        <div className="panel stat"><div className="v">{me.stats.modes_played}</div><div className="k">{t.levels}</div></div>
      </div>
      <form className="panel auth" style={{ margin: "0 0 20px", maxWidth: 420 }} onSubmit={onChange}>
        <h2 style={{ marginTop: 0, fontSize: 17 }}>{t.changePassword}</h2>
        {msg && <div className={`notice ${msg.ok ? "ok" : "bad"}`}>{msg.text}</div>}
        <div className="field">
          <label htmlFor="cp">{t.currentPassword}</label>
          <input id="cp" type="password" className="input" autoComplete="current-password" required value={current} onChange={(e) => setCurrent(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="np">{t.newPassword}</label>
          <input id="np" type="password" className="input" autoComplete="new-password" required value={next} onChange={(e) => setNext(e.target.value)} />
        </div>
        <button className="btn primary">{t.save}</button>
      </form>
      <button className="btn" onClick={onLogout}>{t.logout}</button>
    </>
  );
}
