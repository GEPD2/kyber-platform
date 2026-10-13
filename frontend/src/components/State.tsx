"use client";

import { usePrefs } from "@/lib/prefs";

export function Loading() {
  const { t } = usePrefs();
  return <div className="state">{t.loading}</div>;
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  const { t } = usePrefs();
  return (
    <div className="state error" role="alert">
      <p>
        {t.error}: {message}
      </p>
      {onRetry && (
        <button className="btn" onClick={onRetry}>
          {t.retry}
        </button>
      )}
    </div>
  );
}

export function Empty() {
  const { t } = usePrefs();
  return <div className="state">{t.empty}</div>;
}
