"""
App/API/__init__.py
-------------------
Builds the v1 APIRouter that includes every domain sub-router.
"""

from fastapi import APIRouter

from App.API.Routing import (
    cases_router,
    evidence_router,
    persons_router,
    suspects_router,
    system_router,
    trials_router,
    victims_router,
    witnesses_router,
)

api_router = APIRouter()

# People
api_router.include_router(persons_router)

# Case lifecycle
api_router.include_router(cases_router)

# Case-scoped entities
api_router.include_router(evidence_router)
api_router.include_router(witnesses_router)
api_router.include_router(suspects_router)
api_router.include_router(victims_router)
api_router.include_router(trials_router)

# Analytics + Auth
api_router.include_router(system_router)

__all__ = ["api_router"]
