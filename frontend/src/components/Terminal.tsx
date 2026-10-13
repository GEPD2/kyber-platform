"use client";

import { useCallback, useEffect, useRef, useState, type KeyboardEvent } from "react";
import { ApiError, api } from "@/lib/api";
import { usePrefs } from "@/lib/prefs";
import type { Lang, Mode, ModeContent, SubmitResult, TermQuestion } from "@/lib/types";

type LineKind = "cmd" | "out" | "err" | "info" | "ok" | "task";
interface Line {
  kind: LineKind;
  text: string;
}

interface Props {
  mode: Mode;
  content: ModeContent;
  question: TermQuestion;
  index: number;
  streak: number;
  allSolved: boolean;
  onResult: (res: SubmitResult) => void;
  onAdvance: () => void;
}

const STORE_KEY = "kyber_lab_terminal";
const MAX_LINES = 1500;

function load(): Line[] {
  try {
    const raw = sessionStorage.getItem(STORE_KEY);
    return raw ? (JSON.parse(raw) as Line[]) : [];
  } catch {
    return [];
  }
}

function save(lines: Line[]): void {
  try {
    sessionStorage.setItem(STORE_KEY, JSON.stringify(lines.slice(-MAX_LINES)));
  } catch {
    /* storage blocked: scrollback lasts for this page only */
  }
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

// Lines whose pace makes the simulation feel like the real tool.
function delayFor(line: string): number {
  if (/^Writing at 0x/.test(line)) return 90;
  if (/^Connecting/.test(line) || /^Detecting chip/.test(line)) return 220;
  if (/^\[\d+\/\d+\]/.test(line)) return 60;
  if (/^I \(\d+\) mlkem_demo/.test(line)) return 70;
  return 14;
}

function tree(files: Record<string, string>): string {
  const paths = Object.keys(files).sort();
  const dirs = new Map<string, string[]>();
  for (const p of paths) {
    const [dir, name] = p.includes("/") ? [p.slice(0, p.lastIndexOf("/")), p.slice(p.lastIndexOf("/") + 1)] : ["", p];
    dirs.set(dir, [...(dirs.get(dir) ?? []), name]);
  }
  const out = ["."];
  const top = dirs.get("") ?? [];
  const subdirs = [...dirs.keys()].filter((d) => d !== "");
  const entries = [...subdirs.map((d) => ({ d })), ...top.map((f) => ({ f }))];
  entries.forEach((e, i) => {
    const last = i === entries.length - 1;
    if ("d" in e) {
      out.push(`${last ? "└──" : "├──"} ${e.d}/`);
      (dirs.get(e.d) ?? []).forEach((f, j, arr) => out.push(`${last ? "    " : "│   "}${j === arr.length - 1 ? "└──" : "├──"} ${f}`));
    } else {
      out.push(`${last ? "└──" : "├──"} ${e.f}`);
    }
  });
  return out.join("\n");
}

export function Terminal({ mode, content, question, index, streak, allSolved, onResult, onAdvance }: Props) {
  const { t, lang } = usePrefs();
  const files = content.files ?? {};
  const cwd = content.cwd ?? "~";
  const prompt = `${content.prompt_user ?? "student@lab"}:${cwd}$`;
  const [lines, setLines] = useState<Line[]>([]);
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<string[]>([]);
  const [histPos, setHistPos] = useState(-1);
  const [busy, setBusy] = useState(false);
  const screenRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const announced = useRef<string>("");

  const push = useCallback((add: Line[]) => {
    setLines((prev) => {
      const next = [...prev, ...add].slice(-MAX_LINES);
      save(next);
      return next;
    });
  }, []);

  useEffect(() => {
    const stored = load();
    setLines(stored.length ? stored : [{ kind: "info", text: t.termWelcome }]);
    // initial scrollback only; later language switches keep it
  }, []);

  useEffect(() => {
    const key = `${question.id}:${lang}`;
    if (announced.current === key) return;
    announced.current = key;
    push([{ kind: "task", text: `[${t.termTask} ${index + 1}/${content.total}] ${question.q.replace(/<[^>]+>/g, "")}` }]);
  }, [question.id, question.q, index, content.total, lang, push, t.termTask]);

  useEffect(() => {
    screenRef.current?.scrollTo({ top: screenRef.current.scrollHeight });
  }, [lines]);

  async function stream(text: string, kind: LineKind) {
    for (const line of text.split("\n")) {
      push([{ kind, text: line }]);
      await sleep(delayFor(line));
    }
  }

  async function hint(l: Lang) {
    try {
      const h = await api.hint(mode, index, 0, l);
      push([{ kind: "info", text: `${t.hint} ${h.level}/${h.max_level}: ${h.hint}` },
            { kind: "info", text: `${t.hintsUsed}: ${h.hints_used} · ${t.pointsIfCorrect}: ${h.points_if_correct}` }]);
    } catch (e) {
      push([{ kind: "err", text: e instanceof ApiError ? e.message : String(e) }]);
    }
  }

  function builtin(cmd: string): boolean {
    const [name, ...args] = cmd.split(/\s+/);
    const arg = args.join(" ");
    const isProjectPath = (p: string) => p === "" || p === "." || (!p.startsWith("/") && !p.startsWith("~") && !p.startsWith("-"));
    switch (name) {
      case "help":
        push([{ kind: "info", text: t.termHelp }]);
        return true;
      case "task":
        push([{ kind: "task", text: question.q.replace(/<[^>]+>/g, "") }]);
        return true;
      case "clear":
        setLines([]);
        save([]);
        return true;
      case "history":
        push([{ kind: "out", text: history.map((h, i) => `${String(i + 1).padStart(4)}  ${h}`).join("\n") || "" }]);
        return true;
      case "pwd":
        push([{ kind: "out", text: "/home/student/mlkem-esp32" }]);
        return true;
      case "whoami":
        push([{ kind: "out", text: "student" }]);
        return true;
      case "cd":
        push([{ kind: "info", text: t.termCd }]);
        return true;
      case "tree":
        push([{ kind: "out", text: tree(files) }]);
        return true;
      case "ls": {
        if (!isProjectPath(arg)) return false;
        const dir = arg.replace(/^\.\/?/, "").replace(/\/$/, "");
        const names = new Set<string>();
        for (const p of Object.keys(files)) {
          if (dir === "") names.add(p.includes("/") ? `${p.split("/")[0]}/` : p);
          else if (p.startsWith(`${dir}/`)) names.add(p.slice(dir.length + 1));
        }
        push([names.size ? { kind: "out", text: [...names].sort().join("  ") }
                         : { kind: "err", text: `ls: cannot access '${arg}': ${t.termNoFile}` }]);
        return true;
      }
      case "cat": {
        if (!isProjectPath(arg) || arg === "") return false;
        const path = arg.replace(/^\.\//, "");
        const body = files[path];
        push([body !== undefined ? { kind: "out", text: body.replace(/\n$/, "") }
                                 : { kind: "err", text: `cat: ${arg}: ${t.termNoFile}` }]);
        return true;
      }
      default:
        return false;
    }
  }

  async function run(raw: string) {
    const cmd = raw.trim();
    push([{ kind: "cmd", text: `${prompt} ${raw}` }]);
    if (!cmd) return;
    setHistory((h) => [...h, cmd]);
    setHistPos(-1);
    if (cmd === "hint") {
      await hint(lang);
      return;
    }
    if (builtin(cmd)) return;
    if (allSolved) {
      push([{ kind: "ok", text: t.termLabDone }]);
      return;
    }
    setBusy(true);
    try {
      const res = await api.submit(mode, index, cmd, streak, lang);
      await stream(res.output, res.correct ? "out" : "err");
      onResult(res);
      if (res.correct) {
        push([{ kind: "ok", text: `✓ ${t.termStepDone}${res.score_delta ? ` · +${res.score_delta} ${t.points}` : ""}` }]);
        if (res.explain) push([{ kind: "info", text: res.explain }]);
        if (index === content.total - 1) push([{ kind: "ok", text: t.termLabDone }]);
        else onAdvance();
      }
    } catch (e) {
      const msg = e instanceof ApiError ? (e.status === 422 ? t.termRejected : e.message) : String(e);
      push([{ kind: "err", text: msg }]);
    } finally {
      setBusy(false);
      inputRef.current?.focus();
    }
  }

  function onKey(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !busy) {
      const v = input;
      setInput("");
      void run(v);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (!history.length) return;
      const pos = histPos === -1 ? history.length - 1 : Math.max(0, histPos - 1);
      setHistPos(pos);
      setInput(history[pos] ?? "");
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (histPos === -1) return;
      const pos = histPos + 1;
      if (pos >= history.length) {
        setHistPos(-1);
        setInput("");
      } else {
        setHistPos(pos);
        setInput(history[pos] ?? "");
      }
    } else if (e.key === "l" && e.ctrlKey) {
      e.preventDefault();
      setLines([]);
      save([]);
    } else if (e.key === "c" && e.ctrlKey && !window.getSelection()?.toString()) {
      e.preventDefault();
      push([{ kind: "cmd", text: `${prompt} ${input}^C` }]);
      setInput("");
    }
  }

  return (
    <div className="term" onClick={() => inputRef.current?.focus()}>
      <div className="term-bar">
        <span className="edot r" /><span className="edot y" /><span className="edot g" />
        <span className="term-title">student@lab: ~/mlkem-esp32</span>
      </div>
      <div className="term-screen" ref={screenRef} role="log" aria-live="polite">
        {lines.map((l, i) => (
          <div key={i} className={`tl tl-${l.kind}`}>{l.text || " "}</div>
        ))}
        <div className="tl tl-input">
          <span className="tl-prompt">{prompt}</span>
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKey}
            disabled={busy}
            spellCheck={false}
            autoComplete="off"
            autoCapitalize="off"
            aria-label="terminal input"
            autoFocus
          />
        </div>
      </div>
    </div>
  );
}
