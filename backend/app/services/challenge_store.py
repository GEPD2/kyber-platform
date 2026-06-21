"""
Challenge store, all question data with correct answers lives here.
The API strips answers before sending to the browser.
VALID_MODES matches all 6 difficulty levels in the frontend.
"""
from typing import Any

VALID_MODES = {"veryeasy", "easy", "medium", "hard", "veryhard", "insane"}

# Correct answers only, the minimal server-side truth needed for validation.
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
  {"type":"gaps","gaps":["j","rr","row"]},
  {"type":"gaps","gaps":["c","tTr","i"]},
  {"type":"gaps","gaps":["roots","j","stu","stu_n[i]"]},
  {"type":"gaps","gaps":["c","q","dq2"]},
  {"type":"gaps","gaps":["N","psi","2","N","N"]},
  {"type":"gaps","gaps":["ROOTS","Q","A"]},
  {"type":"gaps","gaps":["Q","MSG"]},
],

"veryhard": [
  {"type":"gaps","gaps":["mod","exp","b","exp"]},
  {"type":"gaps","gaps":["i","p","(b[2]+b[3])","q"]},
  {"type":"gaps","gaps":["len(a)","n","[::-1]","rev"]},
  {"type":"gaps","gaps":["poly","2","length","2","length","step","s","<<=1"]},
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
  {"type":"gaps","gaps":["[0,0]","[2,0]"]},
  {"type":"gaps","gaps":["sn","ROOTS","N_INV","MSG"]},
  {"type":"gaps","gaps":["i"]},
],

# INSANE (32 C fill-the-gap), rebuilt on the canonical kyber_fips203_update.c
# (plain % q, normal-domain zetas, real names). Order mirrors that file
# top-to-bottom: primitives -> K-PKE -> ML-KEM. Keep in lock-step with the
# frontend INS array in frontend/main.html (same order, same gap answers).
"insane": [
  {"type":"gaps","gaps":["3329","KYBER_N"]},
  {"type":"gaps","gaps":["i+20","1"]},
  {"type":"gaps","gaps":["i"]},
  {"type":"gaps","gaps":["2","r"]},
  {"type":"gaps","gaps":["rate","0"]},
  {"type":"gaps","gaps":["domain","0x80"]},
  {"type":"gaps","gaps":["168","72"]},
  {"type":"gaps","gaps":["128","2*len"]},
  {"type":"gaps","gaps":["KYBER_Q","KYBER_Q"]},
  {"type":"gaps","gaps":["127","128"]},
  {"type":"gaps","gaps":["N_INV"]},
  {"type":"gaps","gaps":["64","KYBER_Q"]},
  {"type":"gaps","gaps":["KYBER_Q","KYBER_Q"]},
  {"type":"gaps","gaps":["rho","R"]},
  {"type":"gaps","gaps":["KYBER_Q","KYBER_N"]},
  {"type":"gaps","gaps":["j","j","b"]},
  {"type":"gaps","gaps":["nonce","eta"]},
  {"type":"gaps","gaps":["KYBER_Q","d"]},
  {"type":"gaps","gaps":["1","7"]},
  {"type":"gaps","gaps":["d","KYBER_Q"]},
  {"type":"gaps","gaps":["t","d"]},
  {"type":"gaps","gaps":["SEED_BYTES","CT_C2_BYTES"]},
  {"type":"gaps","gaps":["sha3_512","sigma","e[i]"]},
  {"type":"gaps","gaps":["tmp","e[i]","rho"]},
  {"type":"gaps","gaps":["i","e1[i]"]},
  {"type":"gaps","gaps":["mu","KYBER_DV"]},
  {"type":"gaps","gaps":["tmp","v","1"]},
  {"type":"gaps","gaps":["ek","sha3_256","z"]},
  {"type":"gaps","gaps":["32","sha3_512","32"]},
  {"type":"gaps","gaps":["h","mp"]},
  {"type":"gaps","gaps":["Kbar","Kr"]},
  {"type":"gaps","gaps":["SS_BYTES","SS_BYTES"]},
],

}


def _strip_answers(ch: dict) -> dict:
    """Remove correct-answer fields before sending to browser."""
    STRIP = {"correct", "ans", "gaps", "cor"}
    return {k: v for k, v in ch.items() if k not in STRIP}


def get_mode_meta(mode: str) -> dict:
    """Public: return question count and answer-stripped questions."""
    items = ANSWER_KEYS.get(mode, [])
    # Return minimal metadata, browser already has full question text
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
