"""
main.py
-------
FastAPI application entry-point.
All domain routers are mounted under the /api/v1 prefix.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from App.API import api_router
from App.db.models import AppUser
from App.db.session import engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Ensure auth table exists so login/register flows work even on older DB dumps.
    AppUser.__table__.create(bind=engine, checkfirst=True)
    yield

app = FastAPI(
    title="Crime Tracking & Analysis API",
    version="2.0.0",
    description="REST endpoints for the Crime-Tracking-and-Analysis-Database.",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")
