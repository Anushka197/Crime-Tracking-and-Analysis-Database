"""
main.py
-------
FastAPI application entry-point.
All domain routers are mounted under the /api/v1 prefix.
"""

from fastapi import FastAPI
from App.API import api_router

app = FastAPI(
    title="Crime Tracking & Analysis API",
    version="2.0.0",
    description="REST endpoints for the Crime-Tracking-and-Analysis-Database.",
)

app.include_router(api_router, prefix="/api/v1")
