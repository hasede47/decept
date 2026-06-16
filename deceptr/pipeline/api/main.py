"""
DECEPTR API v1 — FastAPI
P1 Fix: CORS restricted via ALLOWED_ORIGINS env var
P1 Fix: Startup validation of critical environment variables
"""

import os
import sys
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import ExpiredSignatureError, JWTError, jwt
from datetime import datetime, timedelta

from api.routes import auth, alerts, iocs, attackers, campaigns, dgssi, canary

# ── Startup validation ─────────────────────────────────────────────────────────
REQUIRED_ENV_VARS = [
    "JWT_SECRET",
    "ELASTIC_PASSWORD",
    "MYSQL_PASSWORD",
    "REDIS_PASSWORD",
]

missing = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
if missing:
    print(f"[FATAL] Missing required environment variables: {missing}", file=sys.stderr)
    print("[FATAL] Copy .env.example to .env and fill in values.", file=sys.stderr)
    sys.exit(1)

# ── Config ─────────────────────────────────────────────────────────────────────
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# P1 Fix: CORS from env, not wildcard
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:8088")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="DECEPTR API",
    description="Plateforme de Cyberdeception - Chambre des Representants du Maroc",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,      # P1: no more wildcard *
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

security = HTTPBearer()


# ── Auth helpers ───────────────────────────────────────────────────────────────
def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# ── Existing routers ───────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(alerts.router)
app.include_router(iocs.router)
app.include_router(attackers.router)
app.include_router(campaigns.router)
app.include_router(dgssi.router)
app.include_router(canary.router)


# ── Core endpoints ─────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0", "platform": "DECEPTR"}


@app.get("/")
def root():
    return {
        "name": "DECEPTR API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth":      "/api/auth/login",
            "alerts":    "/api/alerts",
            "iocs":      "/api/iocs",
            "attackers": "/api/attackers",
            "campaigns": "/api/campaigns",
            "dgssi":     "/api/dgssi/rapport",
            "canary":    "/api/canary/trigger",
        }
    }


@app.get("/api/stats", dependencies=[Depends(verify_token)])
def get_stats():
    return {
        "honeypots": ["ssh", "telnet", "web"],
        "status": "running",
    }
