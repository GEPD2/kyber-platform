#!/usr/bin/env python3
"""Clear every user's answers, scores and hint counters; accounts are kept.

Needed once after the 2026-10 question rewrite, because stored question_id
values point at the old question order.

Usage:  ./scripts/reset_progress.py          (asks for confirmation)
        ./scripts/reset_progress.py --yes
"""
import argparse
import subprocess

from _common import fail, info, load_env

SQL = "DELETE FROM submissions;\nDELETE FROM leaderboard;\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--yes", action="store_true", help="do not ask for confirmation")
    args = parser.parse_args()

    env = load_env()
    db = env.get("MYSQL_DATABASE", "")
    if not args.yes:
        answer = input(f"Delete ALL submissions and leaderboard rows in '{db}'? [y/N] ")
        if answer.strip().lower() != "y":
            print("Aborted.")
            return

    try:
        subprocess.run(
            ["docker", "exec", "-i", "-e", f"MYSQL_PWD={env.get('MYSQL_PASSWORD', '')}", "kyber_mysql",
             "mysql", f"-u{env.get('MYSQL_USER', '')}", db],
            input=SQL.encode(), check=True)
    except FileNotFoundError:
        fail("docker not found on PATH.")
    except subprocess.CalledProcessError as e:
        fail(f"MySQL reset failed (exit {e.returncode}).", e.returncode)

    # Hint counters live in Redis under hint:*; they expire on their own, but clear them too.
    subprocess.run(
        ["docker", "exec", "-e", f"REDISCLI_AUTH={env.get('REDIS_PASSWORD', '')}", "kyber_redis",
         "sh", "-c", 'redis-cli --scan --pattern "hint:*" | xargs -r redis-cli del'],
        capture_output=True, check=False)

    info("Progress reset. Accounts are untouched.")


if __name__ == "__main__":
    main()
