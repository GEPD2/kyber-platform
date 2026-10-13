"use client";

import { useCallback, useEffect, useState } from "react";
import { Empty, ErrorState, Loading } from "@/components/State";
import { ApiError, api } from "@/lib/api";
import { usePrefs } from "@/lib/prefs";
import type { LeaderRow } from "@/lib/types";
import { useAuthGuard } from "@/lib/useAuthGuard";

export default function LeaderboardPage() {
  const ok = useAuthGuard();
  const { t } = usePrefs();
  const [rows, setRows] = useState<LeaderRow[] | null>(null);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setError("");
    try {
      setRows(await api.leaderboard());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    if (ok) void load();
  }, [ok, load]);

  if (!ok) return null;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!rows) return <Loading />;

  return (
    <>
      <h1 className="h1">{t.leaderboard}</h1>
      <div className="panel table-wrap">
        {rows.length === 0 ? (
          <Empty />
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>{t.rank}</th>
                <th>{t.player}</th>
                <th className="num">{t.totalScore}</th>
                <th className="num">{t.totalCorrect}</th>
                <th className="num">{t.bestStreak}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.rank}>
                  <td className="mono">{r.rank}</td>
                  <td>{r.username}</td>
                  <td className="num">{r.total_score}</td>
                  <td className="num">{r.total_correct}</td>
                  <td className="num">{r.best_streak ?? 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
