#!/usr/bin/env python3
"""Dump the MySQL database to a timestamped .sql.gz file.

Usage:  ./scripts/backup.py [output_dir]      (default: ./backups/)
"""
import argparse
import gzip
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from _common import ROOT, fail, info, load_env


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("output_dir", nargs="?", default="./backups", help="directory for the dump")
    args = parser.parse_args()

    env = load_env()
    out_dir = (ROOT / args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    outfile = out_dir / f"kyber_{datetime.now():%Y%m%d_%H%M%S}.sql.gz"
    db = env.get("MYSQL_DATABASE", "")
    info(f"Backing up database '{db}' to {outfile} ...")

    # The password goes in the container's environment, not on a command line visible in ps.
    cmd = ["docker", "compose", "exec", "-T", "-e", f"MYSQL_PWD={env.get('MYSQL_PASSWORD', '')}", "mysql",
           "mysqldump", "--no-tablespaces", "--single-transaction", "--quick",
           "-u", env.get("MYSQL_USER", ""), db]
    try:
        with subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE) as proc, gzip.open(outfile, "wb") as gz:
            assert proc.stdout is not None
            shutil.copyfileobj(proc.stdout, gz)
        code = proc.returncode
    except FileNotFoundError:
        fail("docker not found on PATH.")
    if code != 0:
        outfile.unlink(missing_ok=True)
        fail(f"mysqldump failed (exit {code}); no backup written.", code)

    size = outfile.stat().st_size
    info(f"Backup complete: {outfile} ({size / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()
