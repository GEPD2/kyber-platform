#!/usr/bin/env python3
"""Build and start all services.

Usage:  ./scripts/start.py          (first run builds the images)
        ./scripts/start.py --build  (force an image rebuild)
"""
import argparse
import subprocess
import sys

from _common import ROOT, compose, fail, info, load_env, set_env_value, warn

SECRETS = ("SECRET_KEY", "JWT_SECRET", "MYSQL_ROOT_PASSWORD", "MYSQL_PASSWORD", "REDIS_PASSWORD")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--build", action="store_true", help="rebuild images before starting")
    args = parser.parse_args()

    env = load_env()
    certs = ROOT / "nginx" / "certs"
    if not ((certs / "fullchain.pem").is_file() and (certs / "privkey.pem").is_file()):
        info("No TLS certificate found; creating a local self-signed one (HTTPS-only site).")
        if subprocess.run([sys.executable, str(ROOT / "scripts" / "gen_certs.py")]).returncode != 0:
            fail("Could not create the certificate; the site cannot start without one.")
    if env.get("TLS_ENABLED", "true").lower() != "true":
        set_env_value("TLS_ENABLED", "true")
        warn("TLS_ENABLED was false; set to true (the site is HTTPS-only).")
    for key in SECRETS:
        if "CHANGE_ME" in env.get(key, ""):
            warn(f"{key} still has placeholder value; replace it in .env")

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
