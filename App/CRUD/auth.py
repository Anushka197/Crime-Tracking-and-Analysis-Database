"""
auth.py
-------
Authentication and Role-Based Access Control (RBAC) stubs.

Because this project uses a PostgreSQL backend without a built-in users
table, these functions are **service-level stubs** that can be wired to
any auth infrastructure (e.g. JWT, session cookies, OAuth).

Exports
-------
  ROLE_SCOPE_MAP  – dict mapping AuthRole → list[PermissionScope]
  login           – validates credentials (stub) and returns a TokenResponse
  check_access    – validates that a request's roles+scopes allow access
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from App.schema.case import (
    AuthRole,
    LoginRequest,
    PermissionScope,
    RBACAccessCheckRequest,
    RBACAccessCheckResponse,
    TokenResponse,
)

# ---------------------------------------------------------------------------
# Role → Scope mapping  (RBAC policy)
# ---------------------------------------------------------------------------

ROLE_SCOPE_MAP: dict[AuthRole, list[PermissionScope]] = {
    AuthRole.ADMIN: list(PermissionScope),          # full access
    AuthRole.OFFICER: [
        PermissionScope.CASE_READ,
        PermissionScope.CASE_OPEN,
        PermissionScope.EVIDENCE_WRITE,
        PermissionScope.PERSON_WRITE,
    ],
    AuthRole.INVESTIGATOR: [
        PermissionScope.CASE_READ,
        PermissionScope.EVIDENCE_WRITE,
        PermissionScope.PERSON_WRITE,
    ],
    AuthRole.PROSECUTOR: [
        PermissionScope.CASE_READ,
        PermissionScope.TRIAL_WRITE,
    ],
    AuthRole.ANALYST: [
        PermissionScope.CASE_READ,
        PermissionScope.ANALYTICS_READ,
    ],
}

# ---------------------------------------------------------------------------
# Endpoint access requirements  (route → required scopes)
# ---------------------------------------------------------------------------

_ENDPOINT_SCOPE_MAP: dict[tuple[str, str], list[PermissionScope]] = {
    ("POST", "/cases"):             [PermissionScope.CASE_OPEN],
    ("GET",  "/cases"):             [PermissionScope.CASE_READ],
    ("GET",  "/cases/{case_id}"):   [PermissionScope.CASE_READ],
    ("PATCH","/cases/{case_id}"):   [PermissionScope.CASE_OPEN],
    ("PATCH","/cases/{case_id}/close"): [PermissionScope.CASE_CLOSE],
    ("POST", "/cases/{case_id}/evidence"):  [PermissionScope.EVIDENCE_WRITE],
    ("GET",  "/cases/{case_id}/evidence"):  [PermissionScope.CASE_READ],
    ("POST", "/trials/{trial_id}/punishment"): [PermissionScope.TRIAL_WRITE],
    ("GET",  "/analytics/hotspots"): [PermissionScope.ANALYTICS_READ],
}

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def login(
    db: Session,
    payload: LoginRequest,
) -> TokenResponse:
    """Stub login: validates non-empty credentials and returns a synthetic token."""
    if not payload.username or not payload.password:
        raise ValueError("Username and password are required.")

    # --- Stub: accept any non-empty credentials ---
    # Default to OFFICER role for unknown users; override in production.
    role = AuthRole.OFFICER
    scopes = ROLE_SCOPE_MAP[role]

    expires_at = datetime.now(tz=timezone.utc) + timedelta(hours=8)

    return TokenResponse(
        access_token=f"stub-token-{payload.username}",
        token_type="bearer",
        expires_at=expires_at,
        person_id=None,  # link to Person.person_id in production
        roles=[role],
        scopes=scopes,
    )


def check_access(
    db: Session,
    payload: RBACAccessCheckRequest,
) -> RBACAccessCheckResponse:
    """Check whether the given roles/scopes allow access to the endpoint. Denies if no match found."""
    method = payload.method.upper()
    endpoint = payload.endpoint

    required: list[PermissionScope] | None = None

    # Exact match first
    if (method, endpoint) in _ENDPOINT_SCOPE_MAP:
        required = _ENDPOINT_SCOPE_MAP[(method, endpoint)]
    else:
        # Try prefix / pattern matching (simple startswith heuristic)
        for (m, pattern), scopes in _ENDPOINT_SCOPE_MAP.items():
            base = pattern.split("{")[0].rstrip("/")
            if m == method and endpoint.startswith(base):
                required = scopes
                break

    if required is None:
        return RBACAccessCheckResponse(
            allowed=False,
            required_scopes=[],
            reason="Endpoint not recognised or not protected.",
        )

    # Expand role-based scopes
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

    return RBACAccessCheckResponse(
        allowed=True,
        required_scopes=required,
        reason=None,
    )
