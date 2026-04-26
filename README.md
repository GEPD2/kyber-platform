# CRYSTALS-Kyber Training Platform

Post-Quantum Cryptography training application.  
Six difficulty levels from Duolingo-style arithmetic to raw C KEM implementation.

## Stack

| Service  | Image              | Role                              |
|----------|--------------------|-----------------------------------|
| nginx    | nginx:1.25-alpine  | Reverse proxy + static frontend   |
| backend  | python:3.11-slim   | FastAPI — auth, answers, scoring  |
| mysql    | mysql:8.0          | Users, submissions, leaderboard   |
| redis    | redis:7-alpine     | Rate limiting + session store     |

## Quick Start

```bash
# 1. Clone / extract the project
cd kyber-platform

# 2. Create your .env
cp .env.example .env
# Edit .env — replace every CHANGE_ME value with real secrets:
#   python3 -c "import secrets; print(secrets.token_hex(32))"

# 3. Start (builds images on first run)
./scripts/start.sh

# 4. Open http://localhost
```

## Directory Structure

```
kyber-platform/
├── docker-compose.yml          # Service definitions
├── .env.example                # Environment template (copy to .env)
├── README.md
│
├── frontend/
│   └── index.html              # Complete single-file training app
│
├── backend/
│   ├── Dockerfile              # Multi-stage, non-root (UID 1001)
│   ├── requirements.txt
│   └── app/
│       ├── main.py             # FastAPI app + middleware stack
│       ├── core/
│       │   ├── config.py       # Settings from environment
│       │   ├── database.py     # Async SQLAlchemy (aiomysql)
│       │   ├── security.py     # bcrypt, JWT, CSRF, sanitisation
│       │   ├── deps.py         # Shared FastAPI dependencies
│       │   └── redis_client.py # Async Redis singleton
│       ├── middleware/
│       │   ├── security.py     # Response security headers
│       │   └── rate_limit.py   # Redis sliding-window rate limiter
│       ├── models/
│       │   └── models.py       # SQLAlchemy ORM (users, submissions, leaderboard)
│       ├── routers/
│       │   ├── auth.py         # POST /api/auth/{register,login,logout,refresh}
│       │   ├── challenges.py   # GET /api/challenges/{mode}, POST /submit
│       │   ├── leaderboard.py  # GET /api/leaderboard/{mode|global}
│       │   └── users.py        # GET /api/users/me, PUT /me/password
│       └── services/
│           ├── answer_validator.py  # Server-side answer checking
│           └── challenge_store.py   # All correct answers (never sent to browser)
│
├── nginx/
│   ├── nginx.conf              # Rate limit zones, upstream
│   ├── certs/                  # Drop TLS certs here
│   │   └── README.md
│   └── conf.d/
│       ├── app.conf            # Active: HTTP (port 80)
│       └── app_tls.conf.disabled  # Rename to app.conf to enable TLS 1.3
│
├── mysql/
│   ├── my.cnf                  # InnoDB tuning
│   └── init/
│       └── 01_schema.sql       # Tables created on first boot
│
└── scripts/
    ├── start.sh                # Build + start all services
    ├── stop.sh                 # Stop (preserves volumes)
    ├── enable_tls.sh           # Swap HTTP → TLS 1.3 config
    └── disable_tls.sh          # Revert TLS → HTTP
```

## API Endpoints

```
POST /api/auth/register          — create account
POST /api/auth/login             — returns access_token + sets refresh cookie
POST /api/auth/logout            — revokes refresh token
POST /api/auth/refresh           — new access_token from refresh cookie
GET  /api/auth/csrf-token        — get CSRF token for state-changing requests

GET  /api/challenges/{mode}      — question metadata for a mode (no answers)
POST /api/challenges/submit      — validate answer, record score
GET  /api/challenges/progress/{mode}

GET  /api/leaderboard/global     — top 20 across all modes
GET  /api/leaderboard/{mode}     — top 20 for one mode

GET  /api/users/me               — own profile + stats
PUT  /api/users/me/password      — change password
```

## Security Implementation

| Threat          | Mitigation                                                    |
|-----------------|---------------------------------------------------------------|
| XSS             | html.escape on all string inputs + CSP headers in Nginx + X-XSS-Protection |
| CSRF            | HMAC-signed token (itsdangerous) tied to user ID, required on all mutations |
| Path traversal  | Regex block on `../` patterns in all answer inputs            |
| XXE             | Regex block on `<!ENTITY`, `SYSTEM`, `<!DOCTYPE` in inputs    |
| SQL injection   | SQLAlchemy ORM parameterised queries — no raw SQL              |
| Brute force     | Redis-backed login attempt counter + account lockout           |
| Password        | bcrypt (12 rounds) + constant-time verify                      |
| Rate limiting   | Nginx zones (general/auth/submit) + Redis sliding window middleware |
| Token leakage   | Refresh token in HttpOnly cookie, access token short-lived (60 min) |
| Token revocation| `revoked_tokens` table tracks invalidated JTIs                 |
| Info leakage    | Generic 500 handler, stack traces never reach client           |
| Container       | Non-root user UID 1001, multi-stage build, minimal runtime     |

## Enabling TLS 1.3 (HTTPS)

```bash
# 1. Obtain certificates (example: Let's Encrypt via certbot)
certbot certonly --standalone -d yourdomain.com

# 2. Copy to nginx/certs/
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./nginx/certs/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem   ./nginx/certs/

# 3. Activate
./scripts/enable_tls.sh

# 4. Reload nginx
docker compose restart nginx
```

The TLS config enforces:
- TLSv1.3 only (no 1.2)
- HSTS with preload (max-age=31536000)
- OCSP stapling
- Session tickets disabled
- HTTP → HTTPS redirect on port 80

## Environment Variables

See `.env.example` for the full list. Key secrets to generate:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
# Run twice — once for SECRET_KEY, once for JWT_SECRET
```

## Development Mode

```bash
# Set in .env:
APP_ENV=development
DEBUG=true

# API docs available at:
http://localhost/api/docs
```
