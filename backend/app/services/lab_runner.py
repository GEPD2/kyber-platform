"""
Runs one simulated terminal command for a Lab step. Matching rules, the
diagnostics for wrong commands, and the step output all stay server-side.
"""
import re
import shlex

from app.content import lab_outputs

_WS = re.compile(r"\s+")


def normalise_command(cmd: str) -> str:
    s = _WS.sub(" ", str(cmd)).strip().rstrip(";").strip()
    return s.replace(" | ", "|").replace("|", " | ")


def matches(challenge: dict, cmd: str) -> bool:
    c = normalise_command(cmd)
    return c != "" and any(re.fullmatch(p, c) for p in challenge["accept"])


def _program(cmd: str) -> str:
    try:
        parts = shlex.split(cmd)
    except ValueError:
        parts = cmd.split()
    while parts and parts[0] == "sudo":
        parts = parts[1:]
    return parts[0] if parts else ""


def wrong_output(challenge: dict, cmd: str) -> str:
    c = normalise_command(cmd)
    for pattern, template in challenge.get("diagnostics", []):
        m = re.search(pattern, c)
        if m:
            return m.expand(template)
    prog = _program(c)
    if prog in KNOWN_PROGRAMS:
        return f"[lab] '{prog}' exists, but this is not the command for the current task. Type 'task' or 'hint'."
    return f"bash: {prog or c}: command not found"


def step_output(challenge: dict, cmd: str, user_id: int) -> str:
    return getattr(lab_outputs, challenge["output"])(normalise_command(cmd), user_id)


KNOWN_PROGRAMS = {
    "ls", "lsusb", "lspci", "dmesg", "journalctl", "usermod", "adduser", "gpasswd", "groups",
    "id", "chmod", "source", ".", "get_idf", "esptool", "esptool.py", "python", "python3",
    "idf.py", "screen", "minicom", "picocom", "make", "cmake", "gcc", "cat", "grep", "tail",
}
