"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { CodeGaps } from "./CodeGaps";
import { RichText } from "./RichText";
import { ErrorState, Loading } from "./State";
import { Terminal } from "./Terminal";
import { TheoryCard } from "./TheoryCard";
import { ApiError, api } from "@/lib/api";
import { LEVELS } from "@/lib/i18n";
import { usePrefs } from "@/lib/prefs";
import type { HintResult, Mode, ModeContent, Question, SubmitResult } from "@/lib/types";
import { useAuthGuard } from "@/lib/useAuthGuard";

interface QState {
  values: string[];
  status: (boolean | null)[];
  result: SubmitResult | null;
  hints: HintResult[];
  notice: string;
}

function freshState(q: Question | undefined): QState {
  const n = q?.type === "gaps" ? q.gaps.length : 1;
  return { values: Array(n).fill(""), status: Array(n).fill(null), result: null, hints: [], notice: "" };
}

export function PlayClient({ mode }: { mode: Mode }) {
  const ok = useAuthGuard();
  const { t, lang } = usePrefs();
  const [content, setContent] = useState<ModeContent | null>(null);
  const [answered, setAnswered] = useState<Record<number, boolean>>({});
  const [idx, setIdx] = useState(0);
  const [qs, setQs] = useState<QState>(freshState(undefined));
  const [streak, setStreak] = useState(0);
  const [score, setScore] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [showTheory, setShowTheory] = useState(true);
  const [started, setStarted] = useState(false);

  const load = useCallback(async () => {
    setError("");
    try {
      const [c, p] = await Promise.all([api.content(mode, lang), api.progress(mode)]);
      setContent(c);
      const map: Record<number, boolean> = {};
      for (const [k, v] of Object.entries(p.answered)) map[Number(k)] = v;
      setAnswered(map);
      if (!started) {
        const firstOpen = c.questions.findIndex((_, i) => map[i] !== true);
        setIdx(firstOpen === -1 ? 0 : firstOpen);
        setStarted(true);
      }
    } catch (e) {
      setError(e instanceof ApiError ? e.message : String(e));
    }
    // started only matters on the first load; a language switch keeps the position
  }, [mode, lang]);

  useEffect(() => {
    if (ok) void load();
  }, [ok, load]);

  const question = content?.questions[idx];

  useEffect(() => {
    setQs(freshState(question));
    // reset only when the question changes, not on a language reload
  }, [idx, question?.id]);

  const solvedCount = useMemo(() => Object.values(answered).filter(Boolean).length, [answered]);
  const total = content?.total ?? 0;
  const allDone = total > 0 && solvedCount === total;
  const locked = qs.result?.correct === true;

  const setValue = (gap: number, value: string) =>
    setQs((s) => {
      const values = [...s.values];
      values[gap] = value;
      const status = [...s.status];
      status[gap] = null;
      return { ...s, values, status, notice: "" };
    });

  async function check() {
    if (!question || locked) return;
    if (qs.values.some((v) => v.trim() === "")) {
      setQs((s) => ({ ...s, notice: t.fillAll }));
      return;
    }
    const payload = question.type === "gaps" ? JSON.stringify(qs.values.map((v) => v.trim())) : qs.values[0]!.trim();
    setBusy(true);
    try {
      const res = await api.submit(mode, idx, payload, streak, lang);
      setQs((s) => ({ ...s, result: res, status: res.per_gap, notice: "" }));
      setAnswered((a) => ({ ...a, [idx]: res.correct || a[idx] === true }));
      setStreak((n) => (res.correct ? n + 1 : 0));
      setScore(res.total_score);
    } catch (e) {
      setQs((s) => ({ ...s, notice: e instanceof ApiError ? e.message : String(e) }));
    } finally {
      setBusy(false);
    }
  }

  async function hint(gap: number) {
    if (!question) return;
    try {
      const h = await api.hint(mode, idx, gap, lang);
      setQs((s) => {
        const already = s.hints.some((x) => x.gap === h.gap && x.level === h.level);
        return { ...s, hints: already ? s.hints : [...s.hints, h], notice: already ? t.noMoreHints : "" };
      });
    } catch (e) {
      setQs((s) => ({ ...s, notice: e instanceof ApiError ? e.message : String(e) }));
    }
  }

  function onTermResult(res: SubmitResult) {
    setAnswered((a) => ({ ...a, [idx]: res.correct || a[idx] === true }));
    setStreak((n) => (res.correct ? n + 1 : 0));
    setScore(res.total_score);
  }

  function go(i: number) {
    if (content && i >= 0 && i < content.total) setIdx(i);
  }

  if (!ok) return null;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!content || !question) return <Loading />;

  const [levelName] = LEVELS[mode][lang];
  const lastHint = qs.hints[qs.hints.length - 1];
  const multiGap = question.type === "gaps" && question.gaps.length > 1;

  return (
    <>
      <div className="playhead">
        <Link href="/" className="btn ghost">← {t.levels}</Link>
        <h1>{levelName}</h1>
        <span className="pill">{t.questionOf(idx + 1, total)}</span>
        <span className="pill">{solvedCount}/{total} {t.solved}</span>
        <span className="pill">{t.streak} <b>{streak}</b></span>
        {score !== null && <span className="pill">{t.score} <b>{score}</b></span>}
        <span style={{ flex: 1 }} />
        <button className="iconbtn" onClick={() => setShowTheory((v) => !v)} aria-pressed={showTheory}>
          {showTheory ? t.hideTheory : t.showTheory}
        </button>
      </div>

      <div className="dots" role="navigation" aria-label="questions">
        {content.questions.map((q, i) => (
          <button
            key={q.id}
            className={`dot${answered[i] === true ? " done" : answered[i] === false ? " missed" : ""}${i === idx ? " here" : ""}`}
            onClick={() => go(i)}
            aria-current={i === idx}
            aria-label={`${i + 1}`}
          >
            {i + 1}
          </button>
        ))}
      </div>

      {allDone && (
        <div className="feedback ok" style={{ marginTop: 0, marginBottom: 18 }}>
          <div className="title">{t.levelDone}</div>
          {t.levelDoneSub} <Link href="/">{t.backToLevels}</Link>
        </div>
      )}

      <div className={`play${showTheory ? "" : " no-theory"}`}>
        {showTheory && <TheoryCard card={question.card} />}

        {question.type === "term" ? (
          <Terminal
            mode={mode}
            content={content}
            question={question}
            index={idx}
            streak={streak}
            allSolved={allDone}
            onResult={onTermResult}
            onAdvance={() => go(idx + 1)}
          />
        ) : (
          <section className="panel question">
            <div className="qsection">{question.section}</div>
            <p className="qtext"><RichText text={question.q} /></p>

            {question.type === "duo" && (
              <form className="duo" onSubmit={(e) => { e.preventDefault(); void check(); }}>
                <span>{question.prefix}</span>
                <input
                  className="input"
                  inputMode="numeric"
                  autoComplete="off"
                  value={qs.values[0] ?? ""}
                  disabled={locked}
                  onChange={(e) => setValue(0, e.target.value)}
                  aria-label={question.prefix}
                  style={qs.status[0] === false ? { borderColor: "var(--bad)" } : qs.status[0] ? { borderColor: "var(--ok)" } : undefined}
                />
              </form>
            )}

            {question.type === "btns" && (
              <div className="options" role="radiogroup">
                {question.options.map((opt, i) => {
                  const selected = qs.values[0] === String(i);
                  const st = selected ? qs.status[0] : null;
                  return (
                    <button
                      key={i}
                      role="radio"
                      aria-checked={selected}
                      disabled={locked}
                      className={`option${selected ? " selected" : ""}${st === true ? " ok" : st === false ? " bad" : ""}`}
                      onClick={() => setValue(0, String(i))}
                    >
                      <span className="key">{String.fromCharCode(65 + i)}</span>
                      <span>{opt}</span>
                    </button>
                  );
                })}
              </div>
            )}

            {question.type === "gaps" && (
              <CodeGaps question={question} values={qs.values} status={qs.status} locked={locked} onChange={setValue} onHint={hint} />
            )}

            {qs.hints.length > 0 && (
              <div className="hints">
                {qs.hints.map((h) => (
                  <div className="hintbox" key={`${h.gap}-${h.level}`}>
                    <div className="label">
                      {t.hint} {h.level}/{h.max_level}
                      {multiGap ? ` · [${h.gap + 1}]` : ""}
                    </div>
                    {h.hint}
                  </div>
                ))}
                {lastHint && !locked && (
                  <div className="qsection">
                    {t.hintsUsed}: {lastHint.hints_used} · {t.pointsIfCorrect}: {lastHint.points_if_correct}
                  </div>
                )}
              </div>
            )}

            {qs.notice && <div className="notice bad" style={{ marginTop: 14 }}>{qs.notice}</div>}

            {qs.result && (
              <div className={`feedback ${qs.result.correct ? "ok" : "bad"}`} role="status">
                <div className="title">
                  {qs.result.correct ? t.correct : t.notYet}
                  {qs.result.correct && qs.result.score_delta > 0 && ` · +${qs.result.score_delta} ${t.points}`}
                </div>
                {qs.result.correct
                  ? qs.result.already_correct ? t.alreadySolved : null
                  : question.type === "gaps" ? t.wrongGaps : t.wrongSingle}
                {qs.result.correct && qs.result.explain && (
                  <p style={{ margin: "8px 0 0" }}>
                    <b>{t.explanation}: </b>
                    {qs.result.explain}
                  </p>
                )}
              </div>
            )}

            <div className="actions">
              <button className="btn" onClick={() => go(idx - 1)} disabled={idx === 0}>← {t.prev}</button>
              {question.type !== "gaps" && !locked && (question.hint_levels[0] ?? 0) > 0 && (
                <button className="btn" onClick={() => hint(0)}>{t.hint}</button>
              )}
              <span className="spacer" />
              {!locked && (
                <button className="btn primary" onClick={() => void check()} disabled={busy}>{t.check}</button>
              )}
              {(locked || idx < total - 1) && (
                <button className={`btn${locked ? " primary" : ""}`} onClick={() => go(idx + 1)} disabled={idx >= total - 1}>
                  {t.next} →
                </button>
              )}
            </div>
          </section>
        )}
      </div>
    </>
  );
}
