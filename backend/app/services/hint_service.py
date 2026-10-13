"""
Tiered hints. Level 1 names the concept, level 2 gives the formula. No level
reveals the answer. Usage is counted per user and question in Redis and lowers
the base points of a correct answer: 0 hints -> 10, 1 -> 7, 2 or more -> 4.
"""
from app.content.schema import localise
from app.services.challenge_store import hint_slots

HINT_TTL = 30 * 86400
BASE_POINTS = (10, 7, 4)


def _key(user_id: int, mode: str, qid: int) -> str:
    return f"hint:{user_id}:{mode}:{qid}"


def base_points(hints_used: int) -> int:
    return BASE_POINTS[min(hints_used, len(BASE_POINTS) - 1)]


async def hints_used(redis, user_id: int, mode: str, qid: int) -> int:
    levels = await redis.hvals(_key(user_id, mode, qid))
    return sum(int(v) for v in levels)


async def next_hint(redis, user_id: int, mode: str, qid: int,
                    challenge: dict, gap: int, lang: str) -> dict | None:
    slots = hint_slots(challenge)
    if not (0 <= gap < len(slots)) or not slots[gap]:
        return None
    hints = slots[gap]
    key = _key(user_id, mode, qid)
    shown = int(await redis.hget(key, str(gap)) or 0)
    if shown < len(hints):
        shown += 1
        await redis.hset(key, str(gap), shown)
        await redis.expire(key, HINT_TTL)
    used = await hints_used(redis, user_id, mode, qid)
    return {
        "gap": gap,
        "level": shown,
        "max_level": len(hints),
        "hint": localise(hints[shown - 1], lang),
        "hints_used": used,
        "points_if_correct": base_points(used),
    }
