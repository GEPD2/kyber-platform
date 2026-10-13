# CRYSTALS-Kyber Training Platform

A training application for post-quantum cryptography, built around ML-KEM
(FIPS 203, formerly CRYSTALS-Kyber). Seven levels lead from modular arithmetic
by hand to the C reference implementation and a simulated ESP32 lab that
generates a real ML-KEM key.

## Stack

| Service  | Image                         | Role                                                   |
|----------|-------------------------------|--------------------------------------------------------|
| nginx    | built from `frontend/` (owasp/modsecurity-crs, nginx 1.30) | TLS 1.3, WAF (ModSecurity + OWASP CRS), rate limits, static site |
| backend  | python:3.11-slim              | FastAPI: auth, question content, validation, scoring   |
| mysql    | mysql:8.0                     | Users, submissions, leaderboard                        |
| redis    | redis:7-alpine                | Rate limiting, lockouts, hint counters                 |

## Quick start

```bash
cd kyber-platform

# 1. Create your .env and replace every CHANGE_ME value with a real secret
cp .env.example .env
python3 -c "import secrets; print(secrets.token_hex(32))"   # one per secret

# 2. Build and start (the first build takes a few minutes)
./scripts/start.py --build

# 3. Open https://localhost and accept the self-signed certificate once
```

`start.py` creates the local TLS certificate on its first run, warns about any
secret still set to `CHANGE_ME`, and loads the host firewall through `sudo` (it
asks for your password). `stop.py` removes the firewall again. The site is HTTPS
only; see below.

## Levels

| # | Mode       | What it trains                                                        |
|---|------------|-----------------------------------------------------------------------|
| 1 | Very Easy  | Arithmetic mod 17 by hand: reduction, CBD, roots, butterflies          |
| 2 | Easy       | One concept per question: MLWE, hash roles, η₁, encoding, Shor         |
| 3 | Medium     | First code: butterfly, CBD, twist, INTT, key generation, decoding      |
| 4 | Hard       | Toy NTT, CPA encryption, noise budget, compression, FIPS 203 sizes     |
| 5 | Very Hard  | A mini ML-KEM in Python with the real SHA-3 / SHAKE functions          |
| 6 | Insane     | ML-KEM in C, checked against the FIPS 203 reference                    |
| 7 | Lab        | Simulated ESP32 terminal: find, flash and run ML-KEM on a board         |

Every question has a short theory card (what it is, a formula, a worked example
with q = 17, and why ML-KEM needs it). Code gaps only ask about Kyber itself
(twist, butterfly, transpose, hash roles, nonces, the FO transform), never about
variable names. Medium and Hard gaps are multiple choice; typed gaps accept every
listed equivalent form. Hints come in two levels and lower the points of that
question from 10 to 7 to 4; the answer itself is never revealed.

## Directory structure

```
kyber-platform/
├── docker-compose.yml            # services; only port 443 is published
├── docker-compose.override.yml   # dev: hot reload, MySQL/Redis on 127.0.0.1:3307/6380
├── .env.example                  # template; copy to .env (never committed)
│
├── frontend/                     # Next.js 16 + TypeScript, static export
│   ├── Dockerfile                # node build + CSP hashes, then the WAF nginx image
│   ├── scripts/csp-hashes.mjs    # hashes every inline script for the CSP
│   └── src/
│       ├── app/                  # /, /login, /play/[mode], /leaderboard, /account
│       ├── components/           # PlayClient, CodeGaps, TheoryCard, Terminal, ...
│       ├── lib/                  # api.ts (typed client), i18n.ts (EN/EL), types.ts
│       └── styles/               # tokens.css (all colour values, dark/light), app.css
│
├── backend/
│   ├── Dockerfile                # multi-stage, non-root (UID 1001)
│   ├── requirements.txt          # pinned (PyMySQL 1.1.1 on purpose, see the comment)
│   ├── app/
│   │   ├── main.py               # FastAPI app and middleware stack
│   │   ├── core/                 # config, database, security, deps, redis client
│   │   ├── middleware/           # security headers, Redis rate limiter
│   │   ├── models/models.py      # ORM: users, submissions, leaderboard, revoked_tokens
│   │   ├── routers/              # auth, challenges, leaderboard, users
│   │   ├── content/              # ALL question content and answers (server only)
│   │   │   ├── cards.py          # shared theory cards
│   │   │   ├── toy.py            # executable toy Kyber (q = 17) and mini ML-KEM
│   │   │   ├── veryeasy.py ... insane.py
│   │   │   ├── lab.py            # Lab steps: accepted commands, diagnostics, cards
│   │   │   └── lab_outputs.py    # simulated esptool / ESP-IDF output
│   │   └── services/
│   │       ├── answer_validator.py  # equivalence rules, per-gap result
│   │       ├── challenge_store.py   # strips answers and hints before sending
│   │       ├── hint_service.py      # tiered hints, 10 / 7 / 4 points
│   │       ├── lab_runner.py        # runs one simulated terminal command
│   │       └── mlkem.py             # ML-KEM 512/768/1024 in pure Python
│   └── tests/
│       ├── test_content.py       # runs every template; every distractor must fail
│       ├── test_services.py      # hints and scoring
│       ├── test_mlkem.py         # mlkem.py vs the C reference, byte for byte
│       ├── test_security.py      # IDOR, CSRF and XSS regression checks
│       └── data/kyber_fips203_update.c   # canonical FIPS 203 reference
│
├── nginx/
│   ├── nginx.conf                # rate-limit zones, upstream
│   ├── conf.d/app.conf           # HTTPS-only vhost (TLS 1.3, 8443 in the container)
│   ├── modsecurity/kyber-exclusions.conf   # the one WAF exclusion (answer field)
│   └── certs/                    # fullchain.pem + privkey.pem (never committed)
│
├── mysql/
│   ├── my.cnf
│   └── init/01_schema.sql        # tables created on first boot
│
└── scripts/                      # Python 3.9+, standard library only
    ├── _common.py                # project root, .env parsing, docker compose helper
    ├── start.py                  # start everything (pass --build to rebuild images)
    ├── stop.py                   # stop; data volumes are kept
    ├── backup.py                 # mysqldump into backups/kyber_<timestamp>.sql.gz
    ├── gen_certs.py              # local self-signed certificate
    ├── firewall.py               # nftables host firewall (start/stop load and remove it)
    └── reset_progress.py         # clear answers and scores, keep accounts
```

## API

```
POST /api/auth/register            create an account
POST /api/auth/login               access token; refresh token in an HttpOnly cookie
POST /api/auth/logout              revoke the refresh token
POST /api/auth/refresh             new access token from the refresh cookie
GET  /api/auth/csrf-token          CSRF token for state-changing requests

GET  /api/challenges/modes         question count per mode
GET  /api/challenges/{mode}?lang=en|el
                                   question content without answers or hints
                                   (lab: also the virtual project files)
POST /api/challenges/submit        validate; returns right/wrong per gap, the
                                   explanation only when correct, and for Lab
                                   steps the simulated terminal output
POST /api/challenges/hint          next hint level for one gap (lowers the points)
GET  /api/challenges/progress/{mode}

GET  /api/leaderboard/global       top 20 across all modes
GET  /api/leaderboard/{mode}       top 20 for one mode

GET  /api/users/me                 own profile and statistics
PUT  /api/users/me/password        change password
```

## Content self-check

```bash
cd backend
python3 tests/test_content.py      # or: pytest tests/
python3 tests/test_services.py
python3 tests/test_mlkem.py        # needs gcc for the C cross-check
python3 tests/test_security.py     # route checks need the backend dependencies:
# docker compose cp backend/tests backend:/tmp/tests
# docker compose exec -e PYTHONPATH=/app backend python /tmp/tests/test_security.py
```

`test_content.py` fills every code template with the correct answer and runs it:
Python against `content/toy.py`, C either found verbatim in the FIPS 203 reference
or compiled and tested with gcc. It proves that every distractor fails, every
listed equivalent passes, no hint (and no Lab card) gives the answer away, and the public
view contains no answer field.

Scope of the verification: the C reference passes its own self-tests (SHA-3 and
SHAKE known-answer vectors, NTT and INTT, basemul against schoolbook, KEM round
trip, implicit rejection) for k = 2, 3, 4, and `mlkem.py` matches it byte for
byte. The official NIST ACVP vectors have not been run.

## Lab: simulated ESP32 terminal

A terminal in the browser that walks through the real ESP-IDF flow without any
hardware: finding the serial port (`ls /dev/ttyUSB*`, `lsusb`, `dmesg`), the
`dialout` group, sourcing `export.sh`, `esptool.py chip_id` and `flash_id`,
`idf.py set-target`, `build`, `flash` and `monitor`. Commands are checked on the
server; wrong ones get realistic tool errors (a wrong port, a missing group, a
script run instead of sourced). Output follows esptool v4.7 and ESP-IDF v5.3.

The final `monitor` step runs a real ML-KEM-768 from `services/mlkem.py` and
prints the key sizes, H(ek), K == K′, and the implicit-rejection key for a
tampered ciphertext. Only the board and its timings are simulated. The built-ins
`help`, `hint`, `task`, `ls`, `cat` and `tree` run in the browser over a small
virtual ESP-IDF project.

## HTTPS only

The site is served only over HTTPS (TLS 1.3, HTTP/2) on port 443 (nginx runs as
a non-root user and listens on 8443 inside the container). There is no
plain-HTTP listener: port 80 is neither published by docker-compose nor served by
nginx, so `http://localhost` is refused instead of redirected, and nothing, not
even the first request path, travels in clear text.

`start.py` creates a self-signed certificate on its first run if `nginx/certs/`
is empty (EC P-256, valid for localhost, 127.0.0.1 and ::1). The key is mode 640:
only you and your group can read it, and the container gets that group
(`CERT_GID`, set by `start.py`). To
recreate it or add names:

```bash
./scripts/gen_certs.py --force --host kyber.lan --host 192.168.1.20
docker compose restart nginx
```

`TLS_ENABLED=true` (the backend default) gives every cookie the `Secure` flag,
and `ALLOWED_ORIGINS_RAW` lists only `https://` origins.

No HSTS and no OCSP stapling are sent for the local self-signed setup: HSTS on
`localhost` would force HTTPS on every localhost port of the machine. With a real
domain and a CA-signed certificate (for example from
`certbot certonly --standalone -d your.domain`, copied into `nginx/certs/`),
enable both from the comment in `nginx/conf.d/app.conf`.

TLS ends at nginx. Behind it, the links from nginx to the backend and from the
backend to MySQL and Redis stay inside the private Docker network. In development
MySQL and Redis are reachable from the host only on 127.0.0.1 (ports 3307 and
6380, configurable with `MYSQL_HOST_PORT` and `REDIS_HOST_PORT`).

## Web application firewall

nginx runs ModSecurity v3 with the OWASP Core Rule Set 4 (paranoia level 1,
anomaly threshold 5) in blocking mode. It rejects with 403 the usual attack
shapes before they reach the backend: XSS and SQL injection in any field, path
traversal, and scanner tools.

The answers of this platform are code and shell commands by design, so exactly
one field, `answer` on `POST /api/challenges/submit`, skips the code-injection
rule families (`nginx/modsecurity/kyber-exclusions.conf`). Without it, 21 of the
147 accepted answers would be blocked; with it, all pass and every other field
keeps the full rule set.

```bash
docker compose logs nginx | grep '"ruleId"'      # what the WAF matched
MODSEC_RULE_ENGINE=DetectionOnly ./scripts/start.py   # log only, block nothing
```

## Host firewall

Docker publishes ports with DNAT, which bypasses the host INPUT chain, so ufw
alone does not see that traffic. `scripts/firewall.py` adds its own nftables
table (`inet kyber`) on the forward path: from other machines only port 443 is
reachable, every other port Docker publishes is dropped. It never touches ufw,
firewalld or Docker's own rules.

`start.py` loads it before the containers start and `stop.py` removes it after
they stop. Settings in `.env`: `FIREWALL_ENABLED`, `FIREWALL_ALLOW` (default
443) and `FIREWALL_HOST_INPUT` (also drop new inbound connections to the host).

```bash
./scripts/firewall.py                  # print the ruleset
./scripts/firewall.py --check          # syntax check, changes nothing
sudo nft delete table inet kyber       # remove by hand
```

## Security

| Threat            | Mitigation                                                                 |
|-------------------|----------------------------------------------------------------------------|
| Eavesdropping     | HTTPS only (TLS 1.3); port 80 closed; Secure cookies                        |
| Answer leakage    | Answers, hints and explanations stay on the server; checked by tests       |
| XSS (stored, reflected, DOM) | React text rendering, no innerHTML; CSP with script hashes, no 'unsafe-inline'; WAF; nosniff |
| CSRF              | HMAC-signed token (itsdangerous) tied to the user, required on mutations   |
| Path traversal    | Answer inputs reject `../` patterns                                         |
| XXE               | Answer inputs reject `<!ENTITY`, `SYSTEM "`, `<!DOCTYPE`                    |
| SQL injection     | SQLAlchemy ORM with bound parameters; no raw SQL; WAF                       |
| IDOR              | No route takes a user or object id; every query uses the token's user (tested) |
| Network exposure  | nftables table: only 443 reachable from other machines                     |
| Brute force       | Redis login-attempt counter with lockout                                   |
| Passwords         | bcrypt (12 rounds), constant-time verify                                   |
| Rate limiting     | nginx zones (general, auth, submit and hint) plus a Redis sliding window   |
| Token theft       | Refresh token in an HttpOnly cookie; access token lives 60 minutes         |
| Token revocation  | `revoked_tokens` table of invalidated JTIs                                 |
| Information leaks | Generic 500 handler; no stack traces reach the client                      |
| Containers        | Non-root backend (UID 1001) and nginx (UID 101), multi-stage builds        |

## Keeping secrets out of git

`.gitignore` excludes the real `.env` (and every `.env.*` except `.env.example`),
all certificates and private keys, database dumps under `backups/`, Claude Code
folders (`.claude/`) and local notes (`CLAUDE.local.md`), and build output. Before
the first push, check what would be committed:

```bash
git status --ignored
git check-ignore -v .env nginx/certs/privkey.pem
```

## Development mode

`docker-compose.override.yml` is loaded automatically: the backend runs with hot
reload from `./backend/app`, and MySQL and Redis are published on 127.0.0.1 only.
For a production-like run use only the main file:

```bash
docker compose -f docker-compose.yml up -d
```

With `APP_ENV=development` and `DEBUG=true` in `.env`, the API docs are at
https://localhost/api/docs.

## After upgrading from the old question set

Stored question ids point at the old order. Run once:

```bash
./scripts/reset_progress.py
```
