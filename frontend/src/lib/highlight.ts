// Small tokenizer for Python and C snippets. Returns tokens, not HTML, so
// nothing is ever injected with innerHTML.

export type TokenKind = "kw" | "fn" | "num" | "str" | "cm" | "pp" | "const" | "plain";
export interface Token {
  kind: TokenKind;
  text: string;
}

const PY_KW = new Set([
  "def", "return", "for", "in", "if", "else", "elif", "while", "import", "from",
  "and", "or", "not", "is", "True", "False", "None", "assert", "lambda", "with", "as",
]);
const PY_FN = new Set(["len", "range", "min", "max", "abs", "zip", "sum", "int", "list", "bytes", "enumerate", "format", "all", "any"]);
const C_KW = new Set([
  "void", "int", "long", "char", "unsigned", "const", "static", "inline", "typedef", "struct",
  "for", "while", "if", "else", "return", "sizeof", "uint8_t", "uint16_t", "uint32_t",
  "uint64_t", "int16_t", "int32_t", "int64_t", "size_t", "poly", "Keccak",
]);

const PY_RE = /(#.*$)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\b0x[0-9a-fA-F]+\b|\b\d+\b)|([A-Za-z_]\w*)|(\s+)|(.)/gm;
const C_RE = /(\/\*.*?\*\/|\/\/.*$)|(^\s*#\s*\w+)|("(?:[^"\\]|\\.)*")|(\b0x[0-9a-fA-F]+\b|\b\d+\b)|([A-Za-z_]\w*)|(\s+)|(.)/gm;

export function tokenize(src: string, lang: "python" | "c"): Token[] {
  const out: Token[] = [];
  const push = (kind: TokenKind, text: string) => {
    const last = out[out.length - 1];
    if (last && last.kind === kind) last.text += text;
    else out.push({ kind, text });
  };
  if (lang === "python") {
    for (const m of src.matchAll(PY_RE)) {
      const [, cm, str, num, word, ws, other] = m;
      if (cm) push("cm", cm);
      else if (str) push("str", str);
      else if (num) push("num", num);
      else if (word) push(PY_KW.has(word) ? "kw" : PY_FN.has(word) ? "fn" : /^[A-Z][A-Z0-9_]+$/.test(word) ? "const" : "plain", word);
      else push("plain", ws ?? other ?? "");
    }
  } else {
    for (const m of src.matchAll(C_RE)) {
      const [, cm, pp, str, num, word, ws, other] = m;
      if (cm) push("cm", cm);
      else if (pp) push("pp", pp);
      else if (str) push("str", str);
      else if (num) push("num", num);
      else if (word) push(C_KW.has(word) ? "kw" : /^[A-Z][A-Z0-9_]+$/.test(word) ? "const" : "plain", word);
      else push("plain", ws ?? other ?? "");
    }
  }
  return out;
}

// Same marker the backend uses: [[0]], [[1]], ...
export const GAP_RE = /\[\[(\d+)\]\]/g;

export type Segment = { kind: "code"; text: string } | { kind: "gap"; index: number };

export function splitGaps(line: string): Segment[] {
  const segs: Segment[] = [];
  let last = 0;
  for (const m of line.matchAll(GAP_RE)) {
    const at = m.index ?? 0;
    if (at > last) segs.push({ kind: "code", text: line.slice(last, at) });
    segs.push({ kind: "gap", index: Number(m[1]) });
    last = at + m[0].length;
  }
  if (last < line.length) segs.push({ kind: "code", text: line.slice(last) });
  return segs;
}
