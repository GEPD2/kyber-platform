#!/usr/bin/env python3
"""Create a self-signed TLS certificate for local HTTPS.

Writes nginx/certs/fullchain.pem and nginx/certs/privkey.pem (mode 640: owner
and the owner's group, which the non-root nginx container is given),
valid for localhost, 127.0.0.1 and ::1 plus any --host you add. Browsers
will warn ("Not secure") because no CA vouches for it; accept it once.

Usage:  ./scripts/gen_certs.py                     (refuses to overwrite)
        ./scripts/gen_certs.py --force --days 365 --host kyber.lan --host 192.168.1.20
"""
import argparse
import ipaddress
import os
import shutil
import subprocess
import tempfile

from _common import ROOT, fail, info

CERT_DIR = ROOT / "nginx" / "certs"


def san_entries(hosts: list[str]) -> str:
    out = []
    for h in ["localhost", "127.0.0.1", "::1", *hosts]:
        try:
            ipaddress.ip_address(h)
            entry = f"IP:{h}"
        except ValueError:
            entry = f"DNS:{h}"
        if entry not in out:
            out.append(entry)
    return ",".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", action="append", default=[], help="extra DNS name or IP for the certificate")
    parser.add_argument("--days", type=int, default=825, help="validity in days (default 825)")
    parser.add_argument("--force", action="store_true", help="overwrite an existing certificate")
    args = parser.parse_args()

    if not shutil.which("openssl"):
        fail("openssl not found on PATH.")
    cert, key = CERT_DIR / "fullchain.pem", CERT_DIR / "privkey.pem"
    if (cert.exists() or key.exists()) and not args.force:
        fail(f"{cert.name} / {key.name} already exist in {CERT_DIR}. Use --force to replace them.")
    CERT_DIR.mkdir(parents=True, exist_ok=True)

    san = san_entries(args.host)
    # Write to temp files in the same directory, then rename, so a failure never
    # leaves a half-written key behind.
    with tempfile.TemporaryDirectory(dir=CERT_DIR) as tmp:
        tmp_key, tmp_cert = os.path.join(tmp, "key.pem"), os.path.join(tmp, "cert.pem")
        old_umask = os.umask(0o077)
        try:
            subprocess.run(
                ["openssl", "req", "-x509", "-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:prime256v1",
                 "-sha256", "-nodes", "-days", str(args.days),
                 "-keyout", tmp_key, "-out", tmp_cert,
                 "-subj", "/CN=localhost/O=Kyber Training Platform (local)",
                 "-addext", f"subjectAltName={san}",
                 "-addext", "basicConstraints=critical,CA:FALSE",
                 "-addext", "keyUsage=critical,digitalSignature",
                 "-addext", "extendedKeyUsage=serverAuth"],
                check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            fail(f"openssl failed: {e.stderr.decode(errors='replace').strip()}")
        finally:
            os.umask(old_umask)
        os.replace(tmp_key, key)
        os.replace(tmp_cert, cert)
    key.chmod(0o640)
    cert.chmod(0o644)

    fp = subprocess.run(["openssl", "x509", "-in", str(cert), "-noout", "-fingerprint", "-sha256", "-enddate"],
                        capture_output=True, text=True).stdout.strip()
    info(f"Certificate: {cert}")
    info(f"Private key: {key} (mode 640)")
    info(f"Valid for:   {san}")
    for line in fp.splitlines():
        info(line)
    info("Restart nginx to load it: docker compose restart nginx   (or ./scripts/start.py)")


if __name__ == "__main__":
    main()
