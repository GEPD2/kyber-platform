#!/usr/bin/env python3
"""Stop all services and remove the host firewall table. Data volumes are kept.

Usage:  ./scripts/stop.py
        ./scripts/stop.py --keep-firewall   (leave the nftables table loaded)
"""
import argparse

from _common import compose, firewall, info, load_env, warn


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--keep-firewall", action="store_true", help="leave the nftables table loaded")
    args = parser.parse_args()
    info("Stopping services...")
    compose("down")
    # Removed after the containers are gone, so no published port is ever unfiltered.
    if not args.keep_firewall and not firewall("--remove", load_env(required=False)):
        warn("Firewall table not removed. Remove it with: sudo nft delete table inet kyber")
    info("Done. Data volumes preserved.")
    print("       To also remove data: docker compose down -v")


if __name__ == "__main__":
    main()
