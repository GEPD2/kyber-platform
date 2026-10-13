"""
Question content schema and builder helpers.

Every question lives here on the server only. The public view (see
challenge_store.public_question) removes every field listed in SECRET_KEYS,
recursively, before anything reaches the browser.

Code templates mark gaps with [[0]], [[1]], ... in order of appearance.
"""
from typing import Any

SECRET_KEYS = {"correct", "accept", "explain", "check", "ref", "hints",
               "examples_ok", "examples_bad", "diagnostics", "output"}

LANGS = ("en", "el")

CONCEPTS = {
    "modular", "negacyclic", "cbd", "bitrev", "butterfly", "twist", "roots",
    "n_inv", "ntt_layers", "basemul", "matrix", "transpose", "encode",
    "decode", "noise", "compress", "hash_role", "fo_transform", "implicit_reject",
    "sampling", "sizes", "security", "reduction", "constant_time", "serialise",
    "serial", "toolchain", "flashing", "rng",
}


def L(en: str, el: str) -> dict[str, str]:
    return {"en": en, "el": el}


def card(title: dict, what: dict, formula: str, example: str, why: dict) -> dict:
    """Small theory card: one sentence, one formula, one q=17 example, why Kyber needs it."""
    return {"title": title, "what": what, "formula": formula, "example": example, "why": why}


def choice(options: list[str], correct: int, concept: str, hints: list[dict]) -> dict:
    return {"mode": "choice", "options": options, "correct": correct,
            "concept": concept, "hints": hints}


def text(accept: list[str], concept: str, hints: list[dict], width: int = 6) -> dict:
    """Free-text gap. accept[0] is the canonical answer; the rest are equivalents."""
    return {"mode": "text", "accept": accept, "concept": concept,
            "hints": hints, "width": width}


def duo(id: str, section: dict, q: dict, prefix: str, accept: list[str],
        card: dict, hints: list[dict], explain: dict) -> dict:
    return {"id": id, "type": "duo", "section": section, "q": q, "prefix": prefix,
            "card": card, "hints": hints, "accept": accept, "explain": explain}


def btns(id: str, section: dict, q: dict, options: list, correct: int,
         card: dict, hints: list[dict], explain: dict) -> dict:
    return {"id": id, "type": "btns", "section": section, "q": q, "options": options,
            "card": card, "hints": hints, "correct": correct, "explain": explain}


def gaps(id: str, section: dict, q: dict, lang: str, code: str, gaps: list[dict],
         card: dict, explain: dict, check: str = "", ref: bool = False) -> dict:
    """
    check: Python run after the filled template (tests only, never sent).
    ref:   C template must appear verbatim in the canonical FIPS 203 reference.
    """
    return {"id": id, "type": "gaps", "section": section, "q": q, "lang": lang,
            "code": code.strip("\n"), "gaps": gaps, "card": card,
            "explain": explain, "check": check, "ref": ref}


def term(id: str, section: dict, q: dict, card: dict, hints: list[dict],
         accept: list[str], examples_ok: list[str], examples_bad: list[str],
         diagnostics: list[tuple[str, str]], output: str, explain: dict, concept: str) -> dict:
    """
    One step of the simulated terminal (Lab level).
    accept:      regexes, matched with re.fullmatch on the whitespace-normalised command
    diagnostics: (regex searched in a wrong command, simulated error output)
    output:      name of a function in lab_outputs that produces the step's output
    """
    return {"id": id, "type": "term", "section": section, "q": q, "card": card,
            "hints": hints, "accept": accept, "examples_ok": examples_ok,
            "examples_bad": examples_bad, "diagnostics": diagnostics,
            "output": output, "explain": explain, "concept": concept}


def localise(value: Any, lang: str) -> Any:
    """Collapse {"en":..,"el":..} leaves to one language."""
    if isinstance(value, dict):
        if set(value.keys()) == set(LANGS):
            return value[lang]
        return {k: localise(v, lang) for k, v in value.items()}
    if isinstance(value, list):
        return [localise(v, lang) for v in value]
    return value


def strip_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: strip_secrets(v) for k, v in value.items() if k not in SECRET_KEYS}
    if isinstance(value, list):
        return [strip_secrets(v) for v in value]
    return value
