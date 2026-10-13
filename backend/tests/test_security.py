"""IDOR and XSS regression checks. Runs with pytest or plain `python3 tests/test_security.py`.

The route checks need the backend dependencies (FastAPI, SQLAlchemy); without
them they are reported as skipped. Run them in the container:
    docker compose cp backend/tests backend:/tmp/tests
    docker compose exec -e PYTHONPATH=/app backend python /tmp/tests/test_security.py
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.challenge_store import LEVEL_ORDER, public_mode  # noqa: E402

FRONTEND_SRC = Path(__file__).resolve().parents[2] / "frontend" / "src"

# Routes reachable without a logged-in user. Everything else must resolve the
# user from the access token, never from a client-supplied id.
PUBLIC_ROUTES = {"/api/auth/register", "/api/auth/login", "/api/auth/logout",
                 "/api/auth/refresh", "/health"}
# The only path parameter any route may take: a level name, checked against VALID_MODES.
ALLOWED_PATH_PARAMS = {"mode"}


try:  # under pytest a skip is reported as a skip, not a failure
    import pytest
    Skip = pytest.skip.Exception
except ImportError:
    class Skip(Exception):
        pass


def _routes():
    try:
        from fastapi.routing import APIRoute
        from app.main import app
    except ImportError as e:  # backend dependencies not installed on this machine
        raise Skip(f"needs the backend dependencies ({e.name})")

    def names(dependant):
        for d in dependant.dependencies:
            yield getattr(d.call, "__name__", "")
            yield from names(d)

    return [(r.path, r.methods, [p.name for p in r.dependant.path_params], set(names(r.dependant)))
            for r in app.routes if isinstance(r, APIRoute)]


def test_idor_no_object_ids_in_routes():
    for path, _, params, _ in _routes():
        assert set(params) <= ALLOWED_PATH_PARAMS, f"{path} takes path parameters {params}"


def test_idor_every_private_route_uses_token_user():
    for path, _, _, deps in _routes():
        if path not in PUBLIC_ROUTES:
            assert "get_current_user" in deps, f"{path} does not depend on get_current_user"


def test_csrf_on_every_authenticated_mutation():
    for path, methods, _, deps in _routes():
        if path not in PUBLIC_ROUTES and methods & {"POST", "PUT", "PATCH", "DELETE"}:
            assert "require_csrf" in deps, f"{sorted(methods)} {path} has no CSRF check"


def test_stored_xss_username_allow_list():
    try:
        from app.core.security import sanitise_username
    except ImportError as e:
        raise Skip(f"needs the backend dependencies ({e.name})")
    for bad in ["<script>alert(1)</script>", '"><img src=x onerror=alert(1)>', "javascript:alert(1)",
                "a b", "ab", "x" * 33, "admin'--", "&lt;b&gt;"]:
        try:
            sanitise_username(bad)
        except ValueError:
            continue
        raise AssertionError(f"username accepted: {bad!r}")
    assert sanitise_username("alice_01") == "alice_01"


# Real attack shapes. A literal placeholder such as "source <script>" in a
# theory card is fine: the frontend renders every string as text.
ATTACK = re.compile(r"javascript:|<\w+[^>]*\son\w+\s*=|<iframe|<object|<embed|srcdoc=", re.I)


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _strings(v)
    elif isinstance(node, (list, tuple)):
        for v in node:
            yield from _strings(v)


def test_content_has_no_markup_attacks():
    for mode in LEVEL_ORDER:
        for lang in ("en", "el"):
            for s in _strings(public_mode(mode, lang)):
                assert not ATTACK.search(s), f"{mode}/{lang}: {s[:80]!r}"


# DOM XSS sinks. The single allowed one is the static theme script in layout.tsx.
SINKS = re.compile(r"dangerouslySetInnerHTML|\.innerHTML|\.outerHTML|insertAdjacentHTML|"
                   r"document\.write|\beval\(|new Function\(")


def test_frontend_has_no_dom_xss_sinks():
    if not FRONTEND_SRC.is_dir():
        raise Skip("frontend/src not present")
    hits = []
    for f in FRONTEND_SRC.rglob("*.ts*"):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if SINKS.search(line) and not line.lstrip().startswith("//"):
                hits.append(str(f.relative_to(FRONTEND_SRC)))
    assert hits == ["app/layout.tsx"], f"DOM sinks: {hits}"


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok  ", name)
            except Skip as e:
                print("skip", name, f"({e})")
            except AssertionError as e:
                failed += 1
                print("FAIL", name, e)
    sys.exit(1 if failed else 0)
