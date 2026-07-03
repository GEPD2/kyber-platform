"""
Server-side answer validator.
The correct answers for every question live only here, never sent to the browser.
The frontend sends the user's answer to POST /api/challenges/submit,
and this module does the comparison.

For 'buttons' type  → answer is the string of the correct option index ("0","1","2","3")
For 'duo' type      → answer is a stripped string compared to the expected value
For 'gaps' type     → answer is a JSON array of strings, one per gap
"""

import json
from typing import Any


def _norm(s: Any) -> str:
    """Remove ALL whitespace, mirroring the frontend's normAns().
    Several gap answers contain internal spaces ("a, b", "q - c", "<<= 1");
    a user typing "a,b" must be judged the same way on both sides."""
    return "".join(str(s).split())


def validate_answer(challenge: dict, raw_answer: str) -> bool:
    """
    Returns True if raw_answer matches the correct answer for this challenge.
    challenge, dict from CHALLENGE_DATA (includes correct answer fields)
    raw_answer, sanitised string from the client
    """
    qtype = challenge.get("type")

    if qtype == "btns":
        # correct field is the integer index of the correct option
        try:
            submitted = int(raw_answer.strip())
        except (ValueError, TypeError):
            return False
        return submitted == challenge.get("correct")

    elif qtype == "duo":
        # ans field is the expected string (number or short expression)
        return _norm(raw_answer) == _norm(challenge.get("ans", ""))

    elif qtype == "gaps":
        results = grade_gaps(challenge, raw_answer)
        return results is not None and all(results)

    return False


def grade_gaps(challenge: dict, raw_answer: str) -> list[bool] | None:
    """Per-gap grading for 'gaps' questions.
    raw_answer is a JSON-encoded list of strings, one per gap.
    Returns one bool per expected gap, or None if the payload is malformed."""
    try:
        submitted = json.loads(raw_answer)
        if not isinstance(submitted, list):
            return None
    except (json.JSONDecodeError, ValueError):
        return None

    expected_gaps: list = challenge.get("gaps", [])
    if len(submitted) != len(expected_gaps):
        return None

    return [_norm(s) == _norm(e) for s, e in zip(submitted, expected_gaps)]
