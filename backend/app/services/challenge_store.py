"""
Challenge store. All question content and answers live in app/content/ on the
server. Only public_mode() output, with every secret field removed, is ever
sent to the browser.
"""
from app.content import LEVEL_EXTRAS, LEVELS
from app.content.schema import localise, strip_secrets

LEVEL_ORDER = list(LEVELS.keys())
VALID_MODES = set(LEVEL_ORDER)
VALID_LANGS = {"en", "el"}


def mode_size(mode: str) -> int:
    return len(LEVELS.get(mode, []))


def get_challenge(mode: str, question_id: int) -> dict | None:
    """Internal: full record including answers. Never return this to a client."""
    items = LEVELS.get(mode, [])
    if 0 <= question_id < len(items):
        return items[question_id]
    return None


def public_question(q: dict, lang: str) -> dict:
    """Answer-free view. Hints are fetched one level at a time via /hint, so only their count is sent."""
    out = localise(strip_secrets(q), lang)
    out["hint_levels"] = [len(h) for h in hint_slots(q)]
    return out


def public_mode(mode: str, lang: str = "en") -> dict:
    lang = lang if lang in VALID_LANGS else "en"
    items = LEVELS.get(mode, [])
    return {
        "mode": mode,
        "total": len(items),
        "questions": [public_question(q, lang) for q in items],
        **LEVEL_EXTRAS.get(mode, {}),
    }


def explanation(challenge: dict, lang: str) -> str:
    return localise(challenge.get("explain", {"en": "", "el": ""}), lang)


def hint_slots(challenge: dict) -> list[list[dict]]:
    """Hints per gap. duo/btns questions have a single slot."""
    if challenge["type"] == "gaps":
        return [g.get("hints", []) for g in challenge["gaps"]]
    return [challenge.get("hints", [])]
