#!/usr/bin/env python3
"""Stop all services. Data volumes are kept.

Usage:  ./scripts/stop.py
"""
import argparse

from _common import compose, info


def main() -> None:
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()
    info("Stopping services...")
    compose("down")
    info("Done. Data volumes preserved.")
    print("       To also remove data: docker compose down -v")


if __name__ == "__main__":
    main()
