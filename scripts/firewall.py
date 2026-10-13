#!/usr/bin/env python3
"""Host firewall for the platform (nftables), in its own table `inet kyber`.

Docker publishes ports with DNAT, so that traffic never reaches the host INPUT
chain; a plain host firewall (ufw included) does not see it. This ruleset
hooks the FORWARD path instead: from other machines only the published HTTPS
port is reachable, and every other port Docker publishes is dropped.
Connections from this machine itself are not affected.

With --host-input it also drops new inbound connections to the host itself,
except loopback, ICMP, DHCP and the --allow ports.

The table is separate from ufw / firewalld / Docker rules and never flushes
them. Remove it at any time with:  sudo nft delete table inet kyber

start.py loads this table (through sudo) before the containers start, and
stop.py removes it after they stop. Settings in .env: FIREWALL_ENABLED,
FIREWALL_ALLOW, FIREWALL_HOST_INPUT.

Usage:  ./scripts/firewall.py                 print the ruleset (changes nothing)
        ./scripts/firewall.py --check         syntax check with nft -c
        sudo ./scripts/firewall.py --apply    load it (not persistent across reboots)
        sudo ./scripts/firewall.py --remove   delete the table
        options: --allow PORT (repeatable, default 443), --host-input
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess

from _common import fail, info

TABLE = "kyber"


def ruleset(allow: list[int], host_input: bool) -> str:
    ports = ", ".join(str(p) for p in sorted(set(allow)))
    lines = [
        f"table inet {TABLE} {{",
        "    # Runs just before Docker's own forward rules; a drop here is final.",
        "    chain forward {",
        "        type filter hook forward priority -1; policy accept;",
        "        ct state established,related accept",
        "        ct state invalid drop",
        "        # A published port: the connection was DNATed by Docker.",
        f"        ct status dnat ct original proto-dst {{ {ports} }} accept",
        "        ct state new ct status dnat drop",
        "    }",
    ]
    if host_input:
        lines += [
            "",
            "    chain input {",
            "        type filter hook input priority -1; policy accept;",
            '        iifname "lo" accept',
            "        ct state established,related accept",
            "        ct state invalid drop",
            "        meta l4proto { icmp, ipv6-icmp } accept",
            "        udp dport { 67, 68, 546, 547 } accept",
            f"        tcp dport {{ {ports} }} accept",
            "        ct state new drop",
            "    }",
        ]
    lines.append("}")
    return "\n".join(lines) + "\n"


def nft(args: list[str], text: str | None = None, sandbox: bool = False) -> subprocess.CompletedProcess:
    # sandbox: run in a private user + network namespace, so a non-root check
    # gets the netlink access nft needs without touching the host's rules.
    cmd = (["unshare", "-rn"] if sandbox else []) + ["nft", *args]
    return subprocess.run(cmd, input=text, text=True, capture_output=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="syntax check only (nft -c)")
    action.add_argument("--apply", action="store_true", help="load the table (root)")
    action.add_argument("--remove", action="store_true", help="delete the table (root)")
    parser.add_argument("--allow", type=int, action="append", help="port reachable from other machines (default 443)")
    parser.add_argument("--host-input", action="store_true", help="also drop new inbound connections to the host")
    args = parser.parse_args()

    allow = args.allow or [443]
    if any(not 0 < p < 65536 for p in allow):
        fail("--allow takes port numbers 1-65535.")
    rules = ruleset(allow, args.host_input)

    if not (args.check or args.apply or args.remove):
        print(rules, end="")
        return
    if not shutil.which("nft"):
        fail("nft not found. Install nftables (Debian/Ubuntu: sudo apt install nftables).")
    for other in ("ufw", "firewall-cmd"):
        if shutil.which(other):
            info(f"{other} is installed. It keeps working: this table only adds rules and never flushes others.")

    if args.check:
        r = nft(["-c", "-f", "-"], rules, sandbox=os.geteuid() != 0 and bool(shutil.which("unshare")))
        if r.returncode:
            fail(f"nft rejected the ruleset:\n{r.stderr.strip()}")
        info("Ruleset syntax OK (nothing was loaded).")
        return

    if os.geteuid() != 0:
        fail("Needs root: run it with sudo.")
    if args.remove:
        r = nft(["delete", "table", "inet", TABLE])
        if r.returncode and "No such file" not in r.stderr:
            fail(r.stderr.strip())
        info(f"Table inet {TABLE} removed.")
        return

    # Create-then-delete makes the load idempotent: the old table is replaced atomically.
    r = nft(["-f", "-"], f"table inet {TABLE}\ndelete table inet {TABLE}\n" + rules)
    if r.returncode:
        fail(f"nft failed:\n{r.stderr.strip()}")
    info(f"Loaded table inet {TABLE}; reachable from other machines: {', '.join(map(str, sorted(set(allow))))}.")
    info("Not persistent across reboots: ./scripts/start.py loads it again, ./scripts/stop.py removes it.")


if __name__ == "__main__":
    main()
