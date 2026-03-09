"""
auth.py
-------
Real authentication using pwdlib (Argon2) for password hashing
and PyJWT (HS256) for access tokens.

Public API
----------
  register_user(db, payload)   -> AppUser
  login_user(db, payload)      -> TokenOut
  change_password(db, payload) -> UserOut
  get_current_user(token, db)  -> AppUser   (FastAPI Depends target)
  get_current_active_user(user)-> AppUser   (FastAPI Depends target)

Legacy RBAC (kept for /auth/access-check endpoint)
  ROLE_SCOPE_MAP, check_access
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from App.db.models import AppUser
from App.db.session import Session as SessionLocal
from App.schema.core import (
    ChangePasswordRequest,
    TokenOut,
    UserLoginRequest,
    UserOut,
    UserRegisterRequest,
)
from App.schema.case import (
    AuthRole,
    PermissionScope,
    RBACAccessCheckRequest,
    RBACAccessCheckResponse,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# TODO: Move to env var / settings before production
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 1
API_PREFIX = "/api/v1"

# ---------------------------------------------------------------------------
# Password hashing (Argon2 via pwdlib)
# ---------------------------------------------------------------------------

_password_hash = PasswordHash.recommended()
_DUMMY_HASH = _password_hash.hash("dummypassword")  # timing-safe dummy


def _hash_password(plain: str) -> str:
    return _password_hash.hash(plain)


def _verify_password(plain: str, hashed: str) -> bool:
    return _password_hash.verify(plain, hashed)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def _create_access_token(user: AppUser) -> tuple[str, datetime]:
    """Return (encoded_token, expires_at)."""
    expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user.user_id),
        "username": user.username,
        "role": user.role,
        "exp": expires_at,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expires_at


# ---------------------------------------------------------------------------
# OAuth2 scheme  (tokenUrl must match the real login endpoint path)
# ---------------------------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ---------------------------------------------------------------------------
# CRUD functions
# ---------------------------------------------------------------------------

def register_user(db: Session, payload: UserRegisterRequest) -> AppUser:
    """Hash password and insert a new AppUser. Raises ValueError on duplicates."""
    # Check uniqueness
    if db.query(AppUser).filter(AppUser.username == payload.username).first():
        raise ValueError(f"Username '{payload.username}' is already taken.")
    if db.query(AppUser).filter(AppUser.email == payload.email).first():
        raise ValueError(f"Email '{payload.email}' is already registered.")

    user = AppUser(
        username=payload.username,
        email=payload.email,
        mobile_number=payload.mobile_number,
        hashed_password=_hash_password(payload.password),
        role="viewer",          # role is NEVER set via API
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, payload: UserLoginRequest) -> TokenOut:
    """Verify credentials and return a JWT TokenOut. Always takes constant time."""
    user = db.query(AppUser).filter(AppUser.username == payload.username).first()

    if not user:
        # Timing-safe: still run hash verify even when user not found
        _verify_password(payload.password, _DUMMY_HASH)
        raise ValueError("Incorrect username or password.")

    if not _verify_password(payload.password, user.hashed_password):
        raise ValueError("Incorrect username or password.")

    if not user.is_active:
        raise ValueError("Account is disabled.")

    # Update last_login timestamp
    user.last_login = datetime.now(tz=timezone.utc)
    db.commit()

    token, expires_at = _create_access_token(user)
    return TokenOut(access_token=token, token_type="bearer", expires_at=expires_at)


def change_password(db: Session, payload: ChangePasswordRequest) -> UserOut:
    """Verify current password and store the new Argon2 hash."""
    user = db.query(AppUser).filter(AppUser.username == payload.username).first()

    if not user:
        _verify_password(payload.current_password, _DUMMY_HASH)
        raise ValueError("Incorrect username or current password.")

    if not _verify_password(payload.current_password, user.hashed_password):
        raise ValueError("Incorrect username or current password.")

    if not user.is_active:
        raise ValueError("Account is disabled.")

    user.hashed_password = _hash_password(payload.new_password)
    db.commit()
    db.refresh(user)

    return UserOut(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        mobile_number=getattr(user, "mobile_number", None),
        role=user.role,
        is_active=user.is_active,
    )


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> AppUser:
    """Decode JWT and return the live AppUser from DB (creates its own session)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    db = SessionLocal()
    try:
        user = db.get(AppUser, int(user_id))
    finally:
        db.close()

    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Annotated[AppUser, Depends(get_current_user)],
) -> AppUser:
    """Raise 400 if the user account is disabled."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user.")
    return current_user


# ---------------------------------------------------------------------------
# Legacy RBAC (kept for /auth/access-check endpoint — unchanged)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Role → Scope mapping  (RBAC policy)
# ---------------------------------------------------------------------------

# Convenience alias
S = PermissionScope

ROLE_SCOPE_MAP: dict[AuthRole, list[PermissionScope]] = {

    # ── ADMIN: everything ──────────────────────────────────────────────────
    AuthRole.ADMIN: list(PermissionScope),

    # ── OFFICER: all field operations; no trial/judge/punishment authority ─
    AuthRole.OFFICER: [
        S.ADDRESS_READ, S.ADDRESS_WRITE,
        S.PERSON_READ,  S.PERSON_WRITE,
        S.CASE_READ,    S.CASE_OPEN,    S.CASE_CLOSE,
        S.OFFICER_ASSIGN, S.OFFICER_UNLINK,
        S.EVIDENCE_READ,  S.EVIDENCE_WRITE,
        S.WITNESS_READ,   S.WITNESS_WRITE,
        S.SUSPECT_READ,   S.SUSPECT_WRITE,
        S.VICTIM_READ,    S.VICTIM_WRITE,
        S.TRIAL_READ,                          # can read trials, not manage them
        S.ANALYTICS_READ,
    ],

    # ── INVESTIGATOR: full read on everything + evidence/witness/suspect write ─
    AuthRole.INVESTIGATOR: [
        S.ADDRESS_READ,
        S.PERSON_READ,
        S.CASE_READ,
        S.EVIDENCE_READ,  S.EVIDENCE_WRITE,
        S.WITNESS_READ,   S.WITNESS_WRITE,
        S.SUSPECT_READ,   S.SUSPECT_WRITE,
        S.VICTIM_READ,
        S.TRIAL_READ,
        S.ANALYTICS_READ,
    ],

    # ── PROSECUTOR: all prosecution/trial/punishment authority ────────────
    AuthRole.PROSECUTOR: [
        S.CASE_READ,
        S.PERSON_READ,
        S.EVIDENCE_READ,
        S.WITNESS_READ,
        S.SUSPECT_READ,
        S.VICTIM_READ,
        S.TRIAL_READ,    S.TRIAL_WRITE,
        S.PUNISHMENT_WRITE,
        S.JUDGE_ASSIGN,
        S.ANALYTICS_READ,
    ],

    # ── ANALYST: read-only on cases + analytics only ──────────────────────
    AuthRole.ANALYST: [
        S.CASE_READ,
        S.ANALYTICS_READ,
    ],

    # -- VIEWER: read-only access for default self-registered users --
    AuthRole.VIEWER: [
        S.ADDRESS_READ,
        S.PERSON_READ,
        S.CASE_READ,
        S.EVIDENCE_READ,
        S.WITNESS_READ,
        S.SUSPECT_READ,
        S.VICTIM_READ,
        S.TRIAL_READ,
        S.ANALYTICS_READ,
    ],
}


# ---------------------------------------------------------------------------
# Endpoint → Required scope  (every route from all 7 routers)
# ---------------------------------------------------------------------------

_ENDPOINT_SCOPE_MAP: dict[tuple[str, str], list[PermissionScope]] = {

    # ── Addresses (persons.py) ────────────────────────────────────────────
    ("POST",   "/addresses"):                               [S.ADDRESS_WRITE],
    ("GET",    "/addresses"):                               [S.ADDRESS_READ],
    ("GET",    "/addresses/{address_id}"):                  [S.ADDRESS_READ],
    ("PATCH",  "/addresses/{address_id}"):                  [S.ADDRESS_WRITE],

    # ── Persons (persons.py) ──────────────────────────────────────────────
    ("POST",   "/persons"):                                 [S.PERSON_WRITE],
    ("GET",    "/persons"):                                 [S.PERSON_READ],
    ("GET",    "/persons/{person_id}"):                     [S.PERSON_READ],
    ("PATCH",  "/persons/{person_id}"):                     [S.PERSON_WRITE],
    ("GET",    "/persons/{person_id}/cases"):               [S.PERSON_READ, S.CASE_READ],

    # ── Cases (cases.py) ──────────────────────────────────────────────────
    ("POST",   "/cases"):                                   [S.CASE_OPEN],
    ("GET",    "/cases"):                                   [S.CASE_READ],
    ("GET",    "/cases/{case_id}"):                         [S.CASE_READ],
    ("PATCH",  "/cases/{case_id}"):                         [S.CASE_OPEN],
    ("PATCH",  "/cases/{case_id}/close"):                   [S.CASE_CLOSE],
    ("GET",    "/cases/{case_id}/details"):                 [S.CASE_READ],

    # ── Officer assignment (cases.py) ─────────────────────────────────────
    ("POST",   "/cases/{case_id}/officers/{officer_id}"):   [S.OFFICER_ASSIGN],
    ("DELETE", "/cases/{case_id}/officers/{officer_id}"):   [S.OFFICER_UNLINK],

    # ── Evidence (evidence.py) ────────────────────────────────────────────
    ("POST",   "/cases/{case_id}/evidence"):                [S.EVIDENCE_WRITE],
    ("GET",    "/cases/{case_id}/evidence"):                [S.EVIDENCE_READ],
    ("GET",    "/evidence/{evidence_id}"):                  [S.EVIDENCE_READ],
    ("PATCH",  "/evidence/{evidence_id}"):                  [S.EVIDENCE_WRITE],

    # ── Witnesses & Testimony (witnesses.py) ──────────────────────────────
    ("POST",   "/cases/{case_id}/witnesses"):               [S.WITNESS_WRITE],
    ("GET",    "/cases/{case_id}/witnesses"):               [S.WITNESS_READ],
    ("POST",   "/cases/{case_id}/witnesses/{witness_id}/testimony"): [S.WITNESS_WRITE],
    ("GET",    "/cases/{case_id}/testimonies"):             [S.WITNESS_READ],

    # ── Suspects (suspects.py) ────────────────────────────────────────────
    ("POST",   "/cases/{case_id}/suspects"):                [S.SUSPECT_WRITE],
    ("GET",    "/cases/{case_id}/suspects"):                [S.SUSPECT_READ],
    ("PATCH",  "/cases/{case_id}/suspects/{suspect_id}"):   [S.SUSPECT_WRITE],
    ("GET",    "/suspects/{suspect_id}"):                   [S.SUSPECT_READ],

    # ── Victims (victims.py) ──────────────────────────────────────────────
    ("POST",   "/cases/{case_id}/victims"):                 [S.VICTIM_WRITE],
    ("GET",    "/cases/{case_id}/victims"):                 [S.VICTIM_READ],
    ("GET",    "/victims"):                                 [S.VICTIM_READ],

    # ── Trials, Hearings, Punishments (trials.py) ─────────────────────────
    ("POST",   "/cases/{case_id}/trials"):                  [S.TRIAL_WRITE],
    ("GET",    "/cases/{case_id}/trials"):                  [S.TRIAL_READ],
    ("GET",    "/cases/{case_id}/trials/{trial_id}"):       [S.TRIAL_READ],
    ("POST",   "/cases/{case_id}/trials/{trial_id}/hearing"):    [S.TRIAL_WRITE],
    ("POST",   "/cases/{case_id}/trials/{trial_id}/punishment"): [S.PUNISHMENT_WRITE],
    ("POST",   "/cases/{case_id}/trials/{trial_id}/judge/{judge_id}"): [S.JUDGE_ASSIGN],

    # ── Analytics & Snapshot (system.py) ─────────────────────────────────
    ("GET",    "/cases/{case_id}/snapshot"):                [S.ANALYTICS_READ],
    ("GET",    "/analytics/hotspots"):                      [S.ANALYTICS_READ],
}


def _normalize_endpoint(endpoint: str) -> str:
    """Normalize path for RBAC map matching (strip prefix/query/trailing slash)."""
    normalized = endpoint.split("?", maxsplit=1)[0].strip()
    if not normalized:
        return "/"
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    if normalized.startswith(API_PREFIX):
        normalized = normalized[len(API_PREFIX):] or "/"
    if len(normalized) > 1 and normalized.endswith("/"):
        normalized = normalized.rstrip("/")
    return normalized


def _pattern_to_regex(pattern: str) -> re.Pattern[str]:
    """
    Convert '/cases/{case_id}/evidence' into a regex that matches concrete paths.
    """
    escaped = re.escape(pattern)
    escaped = re.sub(r"\\\{[^{}]+\\\}", r"[^/]+", escaped)
    return re.compile(rf"^{escaped}$")


def _required_scopes_for_endpoint(
    method: str,
    endpoint: str,
) -> list[PermissionScope] | None:
    method = method.upper().strip()
    endpoint = _normalize_endpoint(endpoint)

    exact = _ENDPOINT_SCOPE_MAP.get((method, endpoint))
    if exact is not None:
        return exact

    for (mapped_method, pattern), scopes in _ENDPOINT_SCOPE_MAP.items():
        if mapped_method != method:
            continue
        if _pattern_to_regex(pattern).fullmatch(endpoint):
            return scopes
    return None


def _role_scopes_for_user(user: AppUser) -> set[PermissionScope]:
    role_value = (user.role or "").strip().lower()
    try:
        role = AuthRole(role_value)
    except ValueError:
        return set()
    return set(ROLE_SCOPE_MAP.get(role, []))


def enforce_rbac(
    request: Request,
    current_user: Annotated[AppUser, Depends(get_current_active_user)],
) -> AppUser:
    """
    FastAPI dependency to enforce route RBAC using request method + path.
    """
    required = _required_scopes_for_endpoint(request.method, request.url.path)
    if required is None:
        # Fail closed: no explicit policy means deny.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="RBAC policy is not configured for this endpoint.",
        )

    caller_scopes = _role_scopes_for_user(current_user)
    missing = [scope for scope in required if scope not in caller_scopes]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing scopes: {', '.join(scope.value for scope in missing)}",
        )
    return current_user


def check_access(
    db: Session,
    payload: RBACAccessCheckRequest,
) -> RBACAccessCheckResponse:
    """Check whether the given roles/scopes allow access to the endpoint."""
    required = _required_scopes_for_endpoint(payload.method, payload.endpoint)

    if required is None:
        return RBACAccessCheckResponse(
            allowed=False,
            required_scopes=[],
            reason="Endpoint not recognised or not protected.",
        )

    caller_scopes: set[PermissionScope] = set(payload.scopes)
    for role in payload.roles:
        caller_scopes.update(ROLE_SCOPE_MAP.get(role, []))

    missing = [s for s in required if s not in caller_scopes]
    if missing:
        return RBACAccessCheckResponse(
            allowed=False,
            required_scopes=required,
            reason=f"Missing scopes: {', '.join(s.value for s in missing)}",
        )

    return RBACAccessCheckResponse(allowed=True, required_scopes=required, reason=None)
