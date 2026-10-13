#!/usr/bin/env python3
"""Build and start all services.

Loads the host firewall (scripts/firewall.py, through sudo) before the
containers publish their ports.

Usage:  ./scripts/start.py                (first run builds the images)
        ./scripts/start.py --build        (force an image rebuild)
        ./scripts/start.py --no-firewall  (start without the nftables table)
"""
import argparse
import os
import subprocess
import sys

from _common import ROOT, compose, fail, firewall, info, load_env, set_env_value, warn

SECRETS = ("SECRET_KEY", "JWT_SECRET", "MYSQL_ROOT_PASSWORD", "MYSQL_PASSWORD", "REDIS_PASSWORD")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--build", action="store_true", help="rebuild images before starting")
    parser.add_argument("--no-firewall", action="store_true", help="do not load the nftables firewall this time")
    args = parser.parse_args()

    env = load_env()
    certs = ROOT / "nginx" / "certs"
    if not ((certs / "fullchain.pem").is_file() and (certs / "privkey.pem").is_file()):
        info("No TLS certificate found; creating a local self-signed one (HTTPS-only site).")
        if subprocess.run([sys.executable, str(ROOT / "scripts" / "gen_certs.py")]).returncode != 0:
            fail("Could not create the certificate; the site cannot start without one.")
    key = certs / "privkey.pem"
    # The nginx container runs as uid 101 and reads the key through its group.
    if key.stat().st_mode & 0o777 != 0o640:
        key.chmod(0o640)
    os.environ.setdefault("CERT_GID", str(key.stat().st_gid))
    if env.get("TLS_ENABLED", "true").lower() != "true":
        set_env_value("TLS_ENABLED", "true")
        warn("TLS_ENABLED was false; set to true (the site is HTTPS-only).")
    # Only a count is printed: nothing derived from the secret settings reaches the log.
    placeholders = sum("CHANGE_ME" in env.get(name, "") for name in SECRETS)
    if placeholders:
        warn(f"{placeholders} secret(s) in .env still have the CHANGE_ME placeholder. "
             "Find them with: grep -n CHANGE_ME .env")

    # The firewall goes up before the ports are published, so they are never open unfiltered.
    if args.no_firewall:
        warn("Firewall skipped (--no-firewall): every published port is reachable from the network.")
    elif not firewall("--apply", env):
        warn("Firewall NOT loaded. The site still starts; run: sudo ./scripts/firewall.py --apply")

    info("Starting CRYSTALS-Kyber Training Platform...")
    compose("up", "-d", *(["--build"] if args.build else []))
    print()
    info("Services started:")
    compose("ps", "--format", "table {{.Name}}\t{{.Status}}\t{{.Ports}}")
    print()
    info("Application: https://localhost   (HTTPS only; port 80 is closed)")
    info("Logs:        docker compose logs -f")
    info("Stop:        ./scripts/stop.py")


if __name__ == "__main__":
    main()
