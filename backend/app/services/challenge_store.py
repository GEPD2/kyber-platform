"""
Challenge store — all question data with correct answers lives here.
The API strips answers before sending to the browser.
VALID_MODES matches all 6 difficulty levels in the frontend.
"""
from typing import Any

VALID_MODES = {"veryeasy", "easy", "medium", "hard", "veryhard", "insane"}

# Correct answers only — the minimal server-side truth needed for validation.
# The full question text, theory, and templates are kept in the frontend JS.
# The backend only needs: type, correct/ans/gaps fields.

ANSWER_KEYS: dict[str, list[dict]] = {

"veryeasy": [
  {"type":"duo","ans":"8"},
  {"type":"duo","ans":"15"},
  {"type":"duo","ans":"15"},
  {"type":"duo","ans":"0"},
  {"type":"duo","ans":"0"},
  {"type":"duo","ans":"15"},
  {"type":"duo","ans":"12"},
  {"type":"duo","ans":"11"},
  {"type":"duo","ans":"16"},
  {"type":"duo","ans":"0"},
],

"easy": [
  {"type":"btns","correct":0},
  {"type":"btns","correct":1},
  {"type":"btns","correct":2},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":1},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
],

"medium": [
  # 5 duo
  {"type":"duo","ans":"2"},
  {"type":"duo","ans":"15"},
  {"type":"duo","ans":"2"},
  {"type":"duo","ans":"9"},
  {"type":"duo","ans":"16"},
  # 5 btns
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  # 8 gaps
  {"type":"gaps","gaps":["mod","mod","1"]},
  {"type":"gaps","gaps":["8","(b2+b3)","q"]},
  {"type":"gaps","gaps":["n","[::-1]","i"]},
  {"type":"gaps","gaps":["length","step","<<= 1"]},
  {"type":"gaps","gaps":["inv_roots","n_inv"]},
  {"type":"gaps","gaps":["zip","a, b"]},
  {"type":"gaps","gaps":["s_ntt[col]","prod","e_ntt[row]"]},
  {"type":"gaps","gaps":["q - c","abs(c-q//2)","d0"]},
],

"hard": [
  # 8 btns
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  {"type":"btns","correct":0},
  # 13 gaps
  {"type":"gaps","gaps":["1","1","mod",">>="]},
  {"type":"gaps","gaps":["i","4","b3","q"]},
  {"type":"gaps","gaps":["poly","n","length","j","a[f]","<<= 1"]},
  {"type":"gaps","gaps":["inv_roots","q"]},
  {"type":"gaps","gaps":["0","row","acc","row"]},
  {"type":"gaps","gaps":["0","i"]},
  {"type":"gaps","gaps":["j","rr","row","row"]},
  {"type":"gaps","gaps":["c","tTr","i"]},
  {"type":"gaps","gaps":["roots","j","stu","stu_n[i]"]},
  {"type":"gaps","gaps":["c","q","d0"]},
  {"type":"gaps","gaps":["N","psi","Q","2","N"]},
  {"type":"gaps","gaps":["ROOTS","Q"]},
  {"type":"gaps","gaps":["Q","MSG"]},
],

"veryhard": [
  {"type":"gaps","gaps":["mod","exp","b","exp"]},
  {"type":"gaps","gaps":["i","p","(b[2]+b[3])","q"]},
  {"type":"gaps","gaps":["len(a)","n","[::-1]","rev"]},
  {"type":"gaps","gaps":["poly","2","length","2","length","step","t","<<=1"]},
  {"type":"gaps","gaps":["inv_roots","n_inv"]},
  {"type":"gaps","gaps":["x","a"]},
  {"type":"gaps","gaps":["n","col","p","row"]},
  {"type":"gaps","gaps":["[0]*n","i"]},
  {"type":"gaps","gaps":["2"]},
  {"type":"gaps","gaps":["roots","j"]},
  {"type":"gaps","gaps":["row","row"]},
  {"type":"gaps","gaps":["c","tTr","i"]},
  {"type":"gaps","gaps":["roots","j"]},
  {"type":"gaps","gaps":["stu","i"]},
  {"type":"gaps","gaps":["q","q","d0"]},
  {"type":"gaps","gaps":["N","psi","Q","2"]},
  {"type":"gaps","gaps":["N","omega_inv"]},
  {"type":"gaps","gaps":["k","1"]},
  {"type":"gaps","gaps":["length","length","step","a[f]","<<="]},
  {"type":"gaps","gaps":["N_INV","S0"]},
  {"type":"gaps","gaps":["T0","1"]},
  {"type":"gaps","gaps":["U0","U1","V"]},
  {"type":"gaps","gaps":["DECODED"]},
  {"type":"gaps","gaps":["i","n","Q"]},
  {"type":"gaps","gaps":["i"]},
  {"type":"gaps","gaps":["[0,0]","[2,0]"]},
  {"type":"gaps","gaps":["sn","ROOTS","N_INV","MSG"]},
],

"insane": [
  {"type":"gaps","gaps":["20159","KYBER_Q"]},
  {"type":"gaps","gaps":["QINV","16"]},
  {"type":"gaps","gaps":["coeffs","vec"]},
  {"type":"gaps","gaps":["b->coeffs[i]"]},
  {"type":"gaps","gaps":["b->coeffs[i]"]},
  {"type":"gaps","gaps":["k++","j+len","j"]},
  {"type":"gaps","gaps":["F"]},
  {"type":"gaps","gaps":["a","b","b","b"]},
  {"type":"gaps","gaps":["r","r","r"]},
  {"type":"gaps","gaps":["vec"]},
  {"type":"gaps","gaps":["0","i","r"]},
  {"type":"gaps","gaps":["coeffs"]},
  {"type":"gaps","gaps":["KYBER_Q","0xf"]},
  {"type":"gaps","gaps":["8","8"]},
  {"type":"gaps","gaps":["0x55555555","0x55555555","0x3","2","b"]},
  {"type":"gaps","gaps":["seed","i","j"]},
  {"type":"gaps","gaps":["seed","nonce","&skpv"]},
  {"type":"gaps","gaps":["0","e1.vec[0]","0"]},
  {"type":"gaps","gaps":["&bp","skpv","mp","m"]},
  {"type":"gaps","gaps":["t","KYBER_Q","j"]},
  {"type":"gaps","gaps":["j","2"]},
  {"type":"gaps","gaps":["pk","pk","KYBER_SYMBYTES"]},
  {"type":"gaps","gaps":["buf","buf","ct","ct","ss"]},
  {"type":"gaps","gaps":["buf","kr","cmp","ss"]},
  {"type":"gaps","gaps":["b[i]","8","b[i]"]},
  {"type":"gaps","gaps":["i"]},
  {"type":"gaps","gaps":["i"]},
  {"type":"gaps","gaps":["KYBER_Q","KYBER_Q"]},
  {"type":"gaps","gaps":["pk","seed"]},
  {"type":"gaps","gaps":["b","v"]},
  {"type":"gaps","gaps":["i"]},
  {"type":"gaps","gaps":["seed","nonce","buf"]},
],

}


def _strip_answers(ch: dict) -> dict:
    """Remove correct-answer fields before sending to browser."""
    STRIP = {"correct", "ans", "gaps", "cor"}
    return {k: v for k, v in ch.items() if k not in STRIP}


def get_mode_meta(mode: str) -> dict:
    """Public: return question count and answer-stripped questions."""
    items = ANSWER_KEYS.get(mode, [])
    # Return minimal metadata — browser already has full question text
    return {
        "mode":  mode,
        "total": len(items),
        "questions": [{"type": q["type"]} for q in items],
    }


def get_challenge(mode: str, question_id: int) -> dict | None:
    """Internal: return full challenge record including correct answers."""
    items = ANSWER_KEYS.get(mode, [])
    if 0 <= question_id < len(items):
        return items[question_id]
    return None
