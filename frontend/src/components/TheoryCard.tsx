"use client";

import { usePrefs } from "@/lib/prefs";
import type { Card } from "@/lib/types";

export function TheoryCard({ card }: { card: Card }) {
  const { t } = usePrefs();
  return (
    <aside className="panel card" aria-label={t.theory}>
      <div className="kicker">{t.theory}</div>
      <h2>{card.title}</h2>
      <dl>
        <div>
          <dt>{t.what}</dt>
          <dd>{card.what}</dd>
        </div>
        <div>
          <dt>{t.formula}</dt>
          <dd className="formula">{card.formula}</dd>
        </div>
        <div>
          <dt>{t.example}</dt>
          <dd className="example">{card.example}</dd>
        </div>
        <div>
          <dt>{t.why}</dt>
          <dd>{card.why}</dd>
        </div>
      </dl>
    </aside>
  );
}
