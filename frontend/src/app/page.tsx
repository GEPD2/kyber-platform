"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ErrorState, Loading } from "@/components/State";
import { ApiError, api } from "@/lib/api";
import { LEVELS } from "@/lib/i18n";
import { usePrefs } from "@/lib/prefs";
import { MODES, type Me, type Mode } from "@/lib/types";
import { useAuthGuard } from "@/lib/useAuthGuard";

type Totals = Record<Mode, number>;

export default function LevelsPage() {
  const ok = useAuthGuard();
  const { t, lang } = usePrefs();
  const [me, setMe] = useState<Me | null>(null);
  const [totals, setTotals] = useState<Totals | null>(null);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setError("");
    try {
      const [profile, counts] = await Promise.all([api.me(), api.modes()]);
      setMe(profile);
      setTotals(counts);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    if (ok) void load();
  }, [ok, load]);

  if (!ok) return null;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!me || !totals) return <Loading />;

  return (
    <>
      <h1 className="h1">{t.chooseLevel}</h1>
      <p className="lead">{t.chooseLevelSub}</p>
      <div className="stats">
        <div className="panel stat">
          <div className="v">{me.stats.total_score}</div>
          <div className="k">{t.score}</div>
        </div>
        <div className="panel stat">
          <div className="v">{me.stats.total_correct}</div>
          <div className="k">{t.totalCorrect}</div>
        </div>
      </div>
      <div className="levels">
        {MODES.map((m) => {
          const info = LEVELS[m];
          const [name, sub] = info[lang];
          const total = totals[m];
          const solved = Math.min(me.mode_scores[m]?.correct ?? 0, total);
          const pct = total ? Math.round((solved / total) * 100) : 0;
          return (
            <Link key={m} href={`/play/${m}/`} className="panel level">
              <span className="badge">{info.badge}</span>
              <h3>{name}</h3>
              <p>{sub}</p>
              <div className="bar" aria-hidden>
                <span style={{ width: `${pct}%` }} />
              </div>
              <div className="meta">
                <span>
                  {solved}/{total} {t.solved}
                </span>
                <span>{solved === 0 ? t.start : solved === total ? t.review : t.resume} →</span>
              </div>
            </Link>
          );
        })}
      </div>
    </>
  );
}
