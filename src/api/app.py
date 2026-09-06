"""FastAPI application for the Smart Internship Platform."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.storage.engine import init_db, get_engine
from .routes import listings, departments, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    # Startup: ensure DB tables exist
    engine = get_engine()
    init_db(engine)
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="Akıllı Staj Platformu API",
    description="Smart Internship & Career Opportunities Platform for Turkey",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(listings.router, prefix="/api/v1", tags=["Listings"])
app.include_router(departments.router, prefix="/api/v1", tags=["Departments"])
