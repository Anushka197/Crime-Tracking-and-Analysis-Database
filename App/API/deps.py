"""
deps.py
-------
Shared FastAPI dependencies.

  get_db — yields a SQLAlchemy session per request.

Auth dependencies (get_current_user, get_current_active_user) live in
App.CRUD.auth to avoid circular imports, but are also importable from here
for convenience once the module graph is resolved at runtime.
"""

from typing import Generator
from sqlalchemy.orm import Session
from App.db.session import Session as SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session and close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
