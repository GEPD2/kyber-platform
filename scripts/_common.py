"""Shared helpers for the management scripts (standard library only)."""
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"


def info(msg: str) -> None:
    print(f"[INFO] {msg}", flush=True)


def warn(msg: str) -> None:
    print(f"[WARN] {msg}", flush=True)


def fail(msg: str, code: int = 1) -> NoReturn:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)


def load_env(required: bool = True) -> dict[str, str]:
    """Parse .env as KEY=VALUE lines. Values are never passed through a shell."""
    if not ENV_FILE.exists():
        if required:
            fail(".env not found.\n        Run: cp .env.example .env  then fill in the secret values.")
        return {}
    env: dict[str, str] = {}
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        env[key.strip()] = value
    return env


def set_env_value(key: str, value: str) -> bool:
    """Replace KEY=... in .env in place. Returns False if the key is not present."""
    if not ENV_FILE.exists():
        return False
    lines = ENV_FILE.read_text(encoding="utf-8").splitlines(keepends=True)
    found = False
    for i, line in enumerate(lines):
        if line.split("=", 1)[0].strip() == key and not line.lstrip().startswith("#"):
            lines[i] = f"{key}={value}\n"
            found = True
    if found:
        tmp = ENV_FILE.with_suffix(".tmp")
        tmp.write_text("".join(lines), encoding="utf-8")
        tmp.replace(ENV_FILE)
    return found


def compose(*args: str, check: bool = True, **kwargs) -> subprocess.CompletedProcess:
    """Run `docker compose <args>` from the project root."""
    try:
        return subprocess.run(["docker", "compose", *args], cwd=ROOT, check=check, **kwargs)
    except FileNotFoundError:
        fail("docker not found on PATH.")
    except subprocess.CalledProcessError as e:
        fail(f"docker compose {' '.join(args)} failed (exit {e.returncode}).", e.returncode)


def firewall(action: str, env: dict[str, str]) -> bool:
    """Load (--apply) or remove (--remove) the nftables table of scripts/firewall.py.

    Needs root, so it goes through sudo (which may ask for the password).
    Settings in .env: FIREWALL_ENABLED (default true), FIREWALL_ALLOW (comma
    list, default 443), FIREWALL_HOST_INPUT (default false).
    """
    if env.get("FIREWALL_ENABLED", "true").lower() != "true":
        info("Firewall: disabled (FIREWALL_ENABLED=false in .env).")
        return True
    if not shutil.which("nft"):
        warn("Firewall: nft not found; install nftables to enable it.")
        return False
    cmd = [sys.executable, str(ROOT / "scripts" / "firewall.py"), action]
    if action == "--apply":
        for port in env.get("FIREWALL_ALLOW", "443").split(","):
            if port.strip():
                cmd += ["--allow", port.strip()]
        if env.get("FIREWALL_HOST_INPUT", "false").lower() == "true":
            cmd.append("--host-input")
    if os.geteuid() != 0:
        if not shutil.which("sudo"):
            warn("Firewall: needs root and sudo is not installed.")
            return False
        info("Firewall: root is needed for nftables; sudo may ask for your password.")
        cmd = ["sudo", *cmd]
    return subprocess.run(cmd).returncode == 0
