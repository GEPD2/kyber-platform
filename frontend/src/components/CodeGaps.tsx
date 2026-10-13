"use client";

import { Fragment, useMemo } from "react";
import { splitGaps, tokenize } from "@/lib/highlight";
import { usePrefs } from "@/lib/prefs";
import { displayOrder } from "@/lib/shuffle";
import type { GapsQuestion } from "@/lib/types";

interface Props {
  question: GapsQuestion;
  values: string[];
  status: (boolean | null)[];
  locked: boolean;
  onChange: (gap: number, value: string) => void;
  onHint: (gap: number) => void;
}

function Code({ text, lang }: { text: string; lang: "python" | "c" }) {
  return (
    <>
      {tokenize(text, lang).map((tk, i) =>
        tk.kind === "plain" ? <Fragment key={i}>{tk.text}</Fragment> : <span key={i} className={`tk-${tk.kind}`}>{tk.text}</span>,
      )}
    </>
  );
}

export function CodeGaps({ question, values, status, locked, onChange, onHint }: Props) {
  const { t } = usePrefs();
  const lines = useMemo(() => question.code.split("\n"), [question.code]);
  const orders = useMemo(
    () => question.gaps.map((g, i) => (g.mode === "choice" ? displayOrder(g.options.length, `${question.id}:${i}`) : [])),
    [question],
  );

  return (
    <div className="code">
      <div className="bar-top">
        <span>{question.lang === "c" ? "C" : "Python"}</span>
        <span>{question.gaps.map((_, i) => `[${i + 1}]`).join(" ")}</span>
      </div>
      <div className="lines">
        {lines.map((line, li) => (
          <div className="line" key={li}>
            <span className="ln">{li + 1}</span>
            <span>
              {splitGaps(line).map((seg, si) => {
                if (seg.kind === "code") return <Code key={si} text={seg.text} lang={question.lang} />;
                const i = seg.index;
                const gap = question.gaps[i];
                if (!gap) return null;
                const st = status[i];
                const cls = `gap${st === true ? " ok" : st === false ? " bad" : ""}`;
                const label = `${t.hintFor} ${i + 1}`;
                return (
                  <span className={cls} key={si}>
                    {gap.mode === "choice" ? (
                      <select
                        aria-label={`gap ${i + 1}`}
                        value={values[i] ?? ""}
                        disabled={locked}
                        onChange={(e) => onChange(i, e.target.value)}
                      >
                        <option value="">{`‹${t.pick}›`}</option>
                        {(orders[i] ?? []).map((orig) => (
                          <option key={orig} value={String(orig)}>
                            {gap.options[orig]}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <input
                        aria-label={`gap ${i + 1}`}
                        value={values[i] ?? ""}
                        disabled={locked}
                        spellCheck={false}
                        autoComplete="off"
                        size={Math.max(3, gap.width)}
                        placeholder="?"
                        onChange={(e) => onChange(i, e.target.value)}
                      />
                    )}
                    {question.gaps.length > 1 && <sup className="gapno">{i + 1}</sup>}
                    {!locked && (question.hint_levels[i] ?? 0) > 0 && (
                      <button type="button" className="gaphint" title={label} aria-label={label} onClick={() => onHint(i)}>
                        ?
                      </button>
                    )}
                  </span>
                );
              })}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
