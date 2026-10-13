import { Fragment, type ReactNode } from "react";

// Renders the only markup question texts use, <b> and <code>, as React nodes.
// Anything else is shown as literal text; nothing goes through innerHTML.
const TAG_RE = /<(b|code)>(.*?)<\/\1>/g;

export function RichText({ text }: { text: string }) {
  const out: ReactNode[] = [];
  let last = 0;
  for (const m of text.matchAll(TAG_RE)) {
    const at = m.index ?? 0;
    if (at > last) out.push(<Fragment key={`t${at}`}>{text.slice(last, at)}</Fragment>);
    out.push(m[1] === "b" ? <b key={`b${at}`}>{m[2]}</b> : <code key={`c${at}`}>{m[2]}</code>);
    last = at + m[0].length;
  }
  if (last < text.length) out.push(<Fragment key="end">{text.slice(last)}</Fragment>);
  return <>{out}</>;
}
