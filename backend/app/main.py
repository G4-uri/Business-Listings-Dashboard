"""FastAPI entry point.  Run:  uvicorn app.main:app --reload   ->  docs at /docs"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from .config import settings
from .database import Base, SessionLocal, engine
from .routers import listings, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)  # no-op when schema.sql was already applied
    yield


app = FastAPI(
    title="Business Listings API",
    version="1.0.0",
    description="Bulk-ingest scraped business listings and serve aggregated counts "
                "(city / category / source) to the React dashboard.",
    lifespan=lifespan,
)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_list, allow_methods=["*"], allow_headers=["*"])
app.include_router(listings.router)
app.include_router(stats.router)


@app.get("/health", tags=["meta"])
def health():
    """Liveness + DB connectivity check (handy for the demo and for Docker/K8s probes)."""
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ok"}
