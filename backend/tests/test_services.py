"""Hint tiers and scoring. Runs with pytest or plain `python3 tests/test_services.py`."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.challenge_store import get_challenge, public_mode  # noqa: E402
from app.services.hint_service import base_points, hints_used, next_hint  # noqa: E402


class FakeRedis:
    def __init__(self):
        self.h = {}

    async def hget(self, key, field):
        return self.h.get(key, {}).get(field)

    async def hset(self, key, field, value):
        self.h.setdefault(key, {})[field] = str(value)

    async def hvals(self, key):
        return list(self.h.get(key, {}).values())

    async def expire(self, key, ttl):
        return True


def test_base_points_tiers():
    assert [base_points(n) for n in range(5)] == [10, 7, 4, 4, 4]


def test_hint_levels_advance_and_cap():
    async def run():
        r = FakeRedis()
        ch = get_challenge("medium", 10)
        assert ch["type"] == "gaps"
        h1 = await next_hint(r, 1, "medium", 10, ch, 0, "en")
        h2 = await next_hint(r, 1, "medium", 10, ch, 0, "el")
        h3 = await next_hint(r, 1, "medium", 10, ch, 0, "en")
        assert (h1["level"], h2["level"], h3["level"]) == (1, 2, 2)
        assert h1["points_if_correct"] == 7 and h2["points_if_correct"] == 4
        assert h2["hint"] == ch["gaps"][0]["hints"][1]["el"]
        assert await hints_used(r, 1, "medium", 10) == 2
        assert await hints_used(r, 2, "medium", 10) == 0
        assert await next_hint(r, 1, "medium", 10, ch, 9, "en") is None
    asyncio.run(run())


def test_duo_hint_slot():
    async def run():
        r = FakeRedis()
        ch = get_challenge("veryeasy", 0)
        h = await next_hint(r, 1, "veryeasy", 0, ch, 0, "en")
        assert h["hint"] == ch["hints"][0]["en"] and h["max_level"] == 2
    asyncio.run(run())


def test_unknown_lang_falls_back_to_english():
    assert public_mode("easy", "xx")["questions"][0]["q"] == get_challenge("easy", 0)["q"]["en"]


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
