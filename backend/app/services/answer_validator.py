"""
Server-side answer validator. Correct answers never leave the server.

Answer payloads from the client:
  btns  -> option index as a string ("0".."3")
  duo   -> the typed value
  gaps  -> JSON array, one entry per gap: option index for choice gaps,
           typed text for text gaps
  term  -> the shell command typed in the Lab terminal

normalize_code() is the single equivalence rule (whitespace and quote style
are ignored). Anything beyond that must be listed explicitly in a gap's
accept list, so equivalence is a content decision, not a parser guess.
"""

import json
import re

from app.services.lab_runner import matches as term_matches

_WS = re.compile(r"\s+")
_UNICODE_MINUS = str.maketrans({"−": "-", "–": "-", "×": "*"})


def normalize_code(value: str) -> str:
    s = str(value).translate(_UNICODE_MINUS)
    s = _WS.sub("", s)
    return s.replace("'", '"')


def _matches(submitted: str, accept: list[str]) -> bool:
    n = normalize_code(submitted)
    return n != "" and any(n == normalize_code(a) for a in accept)


def _index(raw) -> int | None:
    try:
        return int(str(raw).strip())
    except (TypeError, ValueError):
        return None


def validate_answer(challenge: dict, raw_answer: str) -> dict:
    """Return {"correct": bool, "per_gap": [bool, ...]}. per_gap never reveals the answer."""
    qtype = challenge.get("type")

    if qtype == "btns":
        ok = _index(raw_answer) == challenge.get("correct")
        return {"correct": ok, "per_gap": [ok]}

    if qtype == "duo":
        ok = _matches(raw_answer, challenge.get("accept", []))
        return {"correct": ok, "per_gap": [ok]}

    if qtype == "term":
        ok = term_matches(challenge, raw_answer)
        return {"correct": ok, "per_gap": [ok]}

    if qtype == "gaps":
        gaps = challenge.get("gaps", [])
        try:
            submitted = json.loads(raw_answer)
        except (json.JSONDecodeError, ValueError, TypeError):
            return {"correct": False, "per_gap": [False] * len(gaps)}
        if not isinstance(submitted, list) or len(submitted) != len(gaps):
            return {"correct": False, "per_gap": [False] * len(gaps)}

        per_gap = []
        for gap, value in zip(gaps, submitted):
            if gap["mode"] == "choice":
                per_gap.append(_index(value) == gap["correct"])
            else:
                per_gap.append(_matches(value, gap["accept"]))
        return {"correct": all(per_gap), "per_gap": per_gap}

    return {"correct": False, "per_gap": []}
