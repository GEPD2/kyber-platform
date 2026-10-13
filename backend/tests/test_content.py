"""
Content self-check. Runs with pytest or plain `python3 tests/test_content.py`.

For every code question:
  - the template filled with the correct answers must pass its check
    (Python: executed against app/content/toy.py; C: found verbatim in the
    FIPS 203 reference, or compiled and tested with gcc),
  - every distractor must FAIL, so no option is accidentally also right,
  - every listed equivalent answer must PASS, so equivalence is proven.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app.content import LEVELS, toy  # noqa: E402
from app.content.schema import CONCEPTS, SECRET_KEYS  # noqa: E402
from app.services.answer_validator import normalize_code, validate_answer  # noqa: E402
from app.services.challenge_store import public_mode  # noqa: E402
from app.services import lab_runner  # noqa: E402

REF_C = os.path.join(ROOT, "tests", "data", "kyber_fips203_update.c")
GAP = re.compile(r"\[\[(\d+)\]\]")
ALL = [q for qs in LEVELS.values() for q in qs]


def fill(code: str, values: list[str]) -> str:
    return GAP.sub(lambda m: values[int(m.group(1))], code)


def correct_values(q: dict) -> list[str]:
    return [g["options"][g["correct"]] if g["mode"] == "choice" else g["accept"][0] for g in q["gaps"]]


def strip_c(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    src = re.sub(r"//[^\n]*", "", src)
    return re.sub(r"\s+", "", src)


_REF = None


def ref_source() -> str:
    global _REF
    if _REF is None:
        with open(REF_C, encoding="utf-8") as f:
            _REF = strip_c(f.read())
    return _REF


def run_python(code: str, check: str) -> bool:
    ns = {k: v for k, v in vars(toy).items() if not k.startswith("__")}
    ns["REF"] = toy
    try:
        exec(compile(code + "\n" + check, "<question>", "exec"), ns)
        return True
    except Exception:
        return False


def run_c(code: str, check: str) -> bool:
    with tempfile.TemporaryDirectory() as d:
        src, exe = os.path.join(d, "q.c"), os.path.join(d, "q")
        with open(src, "w") as f:
            f.write("#include <stdint.h>\n#include <stdio.h>\n#define KYBER_Q 3329\n" + code + "\n" + check)
        if subprocess.run(["gcc", "-O1", "-o", exe, src], capture_output=True).returncode != 0:
            return False
        return subprocess.run([exe], capture_output=True).returncode == 0


def passes(q: dict, values: list[str]) -> bool:
    code = fill(q["code"], values)
    if q["lang"] == "python":
        return run_python(code, q["check"])
    if q["ref"]:
        return strip_c(code) in ref_source()
    return run_c(code, q["check"])


def c_testable(q: dict) -> bool:
    if q["ref"]:
        return os.path.exists(REF_C)
    return shutil.which("gcc") is not None


def test_ids_unique_and_concepts_known():
    ids = [q["id"] for q in ALL]
    assert len(ids) == len(set(ids)), "duplicate question id"
    for q in ALL:
        for g in q.get("gaps", []):
            assert g["concept"] in CONCEPTS, (q["id"], g["concept"])


def test_gap_markers_match():
    for q in ALL:
        if q["type"] == "gaps":
            found = sorted(int(m) for m in GAP.findall(q["code"]))
            assert found == list(range(len(q["gaps"]))), q["id"]


def test_every_question_has_hints_card_explain_in_both_languages():
    for q in ALL:
        for key in ("title", "what", "why"):
            assert set(q["card"][key]) == {"en", "el"}, (q["id"], key)
        assert set(q["explain"]) == {"en", "el"} and q["explain"]["en"], q["id"]
        slots = [g["hints"] for g in q["gaps"]] if q["type"] == "gaps" else [q["hints"]]
        for hints in slots:
            assert len(hints) == 2, q["id"]
            for h in hints:
                assert set(h) == {"en", "el"} and h["en"] and h["el"], q["id"]


def test_hints_never_contain_the_answer():
    for q in ALL:
        if q["type"] == "gaps":
            pairs = [(g["hints"], correct_values(q)[i]) for i, g in enumerate(q["gaps"])]
        elif q["type"] == "duo":
            pairs = [(q["hints"], q["accept"][0])]
        elif q["type"] == "term":
            card_text = [q["card"][k] for k in ("formula", "example")] + [q["card"][k] for k in ("what", "why")]
            pairs = [(q["hints"] + [c if isinstance(c, dict) else {"en": c} for c in card_text], ex)
                     for ex in q["examples_ok"]]
        else:
            continue
        for hints, answer in pairs:
            a = normalize_code(answer)
            if len(a) < 3:
                continue
            for h in hints:
                for text in h.values():
                    assert a not in normalize_code(text), (q["id"], answer)


def test_public_view_has_no_secrets():
    def walk(v, qid):
        if isinstance(v, dict):
            assert not (set(v) & SECRET_KEYS), (qid, set(v) & SECRET_KEYS)
            for x in v.values():
                walk(x, qid)
        elif isinstance(v, list):
            for x in v:
                walk(x, qid)
    for mode in LEVELS:
        for lang in ("en", "el"):
            data = public_mode(mode, lang)
            assert data["total"] == len(LEVELS[mode])
            for q in data["questions"]:
                walk(q, q["id"])
                assert isinstance(q["q"], str) and isinstance(q["card"]["what"], str)


def test_answer_payload_fits_sanitiser_limit():
    for q in ALL:
        if q["type"] == "gaps":
            payload = json.dumps([v if g["mode"] == "text" else str(g["correct"])
                                  for g, v in zip(q["gaps"], correct_values(q))])
            assert len(payload) <= 256, q["id"]


def test_validator_accepts_correct_and_rejects_distractors():
    for q in ALL:
        if q["type"] == "btns":
            assert validate_answer(q, str(q["correct"]))["correct"]
            assert not validate_answer(q, str((q["correct"] + 1) % len(q["options"])))["correct"]
        elif q["type"] == "duo":
            for a in q["accept"]:
                assert validate_answer(q, " " + a + " ")["correct"], q["id"]
            assert not validate_answer(q, "")["correct"]
        elif q["type"] == "term":
            assert validate_answer(q, "  " + q["examples_ok"][0] + " ")["correct"], q["id"]
            assert not validate_answer(q, "")["correct"]
        else:
            good = [str(g["correct"]) if g["mode"] == "choice" else g["accept"][0] for g in q["gaps"]]
            res = validate_answer(q, json.dumps(good))
            assert res["correct"] and all(res["per_gap"]), q["id"]
            bad = list(good)
            g0 = q["gaps"][0]
            bad[0] = str((g0["correct"] + 1) % len(g0["options"])) if g0["mode"] == "choice" else "__wrong__"
            res = validate_answer(q, json.dumps(bad))
            assert not res["correct"] and res["per_gap"][0] is False, q["id"]


def test_code_templates_execute_and_distractors_fail():
    for q in ALL:
        if q["type"] != "gaps":
            continue
        if q["lang"] == "c" and not c_testable(q):
            print("SKIP (no gcc/reference):", q["id"])
            continue
        good = correct_values(q)
        assert passes(q, good), f"{q['id']}: correct answers do not pass"
        for i, g in enumerate(q["gaps"]):
            alts = ([o for j, o in enumerate(g["options"]) if j != g["correct"]]
                    if g["mode"] == "choice" else [])
            for wrong in alts:
                trial = list(good)
                trial[i] = wrong
                assert not passes(q, trial), f"{q['id']} gap {i}: distractor {wrong!r} also passes"
            if g["mode"] == "text":
                for eq in g["accept"][1:]:
                    trial = list(good)
                    trial[i] = eq
                    assert q["lang"] == "c" and q["ref"] or passes(q, trial), \
                        f"{q['id']} gap {i}: equivalent {eq!r} fails"


TERMS = [q for q in ALL if q["type"] == "term"]


def test_term_examples_and_diagnostics():
    assert TERMS, "no Lab steps"
    all_ok = {lab_runner.normalise_command(ex) for q in TERMS for ex in q["examples_ok"]}
    for q in TERMS:
        for ex in q["examples_ok"]:
            assert lab_runner.matches(q, ex), f"{q['id']}: should accept {ex!r}"
        for ex in q["examples_bad"]:
            assert not lab_runner.matches(q, ex), f"{q['id']}: should reject {ex!r}"
            out = lab_runner.wrong_output(q, ex)
            assert out, (q["id"], ex)
            for ok in all_ok:
                if len(ok) > 6:
                    assert ok not in out, f"{q['id']}: diagnostic for {ex!r} reveals {ok!r}"
        for pattern, _ in q["diagnostics"]:
            assert not any(lab_runner.matches(q, ex) and re.search(pattern, lab_runner.normalise_command(ex))
                           for ex in q["examples_ok"]), f"{q['id']}: diagnostic {pattern!r} fires on a correct command"


def test_term_outputs_render():
    for q in TERMS:
        for ex in q["examples_ok"]:
            out = lab_runner.step_output(q, ex, user_id=7)
            assert out.strip(), (q["id"], ex)
    monitor = next(q for q in TERMS if q["output"] == "monitor")
    out = lab_runner.step_output(monitor, monitor["examples_ok"][0], 7)
    assert "K == K' : YES" in out and "Kbar == K : NO" in out and "ek = 1184 B" in out
    chip = next(q for q in TERMS if q["output"] == "chip_id")
    assert lab_runner.step_output(chip, chip["examples_ok"][0], 7) == lab_runner.step_output(chip, chip["examples_ok"][0], 7)


def test_lab_public_view_has_files_and_no_secrets():
    data = public_mode("lab", "el")
    assert "main/mlkem_demo.c" in data["files"]
    raw = json.dumps(data, ensure_ascii=False)
    for q in TERMS:
        for ex in q["examples_ok"]:
            if len(ex) > 8:
                assert ex not in raw, f"public lab view leaks {ex!r}"


def _computed_duo_answers():
    t = toy
    return {
        "ve-mod": 25 % 17, "ve-neg": -2 % 17, "ve-negacyclic": -2 % 17,
        "ve-cbd-neg": t.cbd_eta2([0x0C])[0], "ve-cbd-pos": t.cbd_eta2([0x03])[0],
        "ve-root": t.ROOTS[3], "ve-bf-u": t.butterfly(3, 1, 9)[0], "ve-bf-v": t.butterfly(3, 1, 9)[1],
        "ve-pointwise": 11 * 3 % 17, "ve-decode": t.decode_bit(3),
        "me-cbd-hi": t.cbd_eta2([0x30])[1], "me-cbd-stored": t.cbd_eta2([0xC0])[1],
        "me-twist": t.twist([0, 0, 5, 0, 0, 0, 0, 0])[2], "me-that": (11 * 1 + 6 * 8 + 1) % 17,
        "me-modpow": t.modpow(3, 8, 17),
    }


def test_duo_answers_match_computation():
    computed = _computed_duo_answers()
    for q in ALL:
        if q["type"] == "duo":
            assert q["id"] in computed, f"no computation for {q['id']}"
            assert q["accept"][0] == str(computed[q["id"]]), (q["id"], q["accept"][0], computed[q["id"]])


def test_normalize_code():
    assert normalize_code("<<= 1") == normalize_code("<<=1")
    assert normalize_code("a , b") == normalize_code("a,b")
    assert normalize_code("'x'") == normalize_code('"x"')
    assert normalize_code("− 2") == normalize_code("-2")


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok  ", name)
            except AssertionError as e:
                failed += 1
                print("FAIL", name, e)
    print(f"{failed} failed")
    sys.exit(1 if failed else 0)
