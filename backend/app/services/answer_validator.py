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
        expected = str(challenge.get("ans", "")).strip()
        return raw_answer.strip() == expected

    elif qtype == "gaps":
        # gaps field is a list of correct strings, one per gap
        # raw_answer is a JSON-encoded list
        try:
            submitted: list = json.loads(raw_answer)
            if not isinstance(submitted, list):
                return False
        except (json.JSONDecodeError, ValueError):
            return False

        expected_gaps: list = challenge.get("gaps", [])
        if len(submitted) != len(expected_gaps):
            return False

        return all(
            str(s).strip() == str(e).strip()
            for s, e in zip(submitted, expected_gaps)
        )

    return False
