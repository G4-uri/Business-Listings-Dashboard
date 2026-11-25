from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas, services
from ..database import get_db

router = APIRouter(prefix="/api", tags=["dashboard"])


def _count(dim: str, db, city, category, source, cross) -> schemas.CountResponse:
    data = services.counts_by(db, dim, city, category, source, cross)
    return schemas.CountResponse(dimension=dim, total=sum(d["count"] for d in data), data=data)


@router.get("/stats/by-city", response_model=schemas.CountResponse, summary="Listing count per city")
def by_city(category: str | None = None, source: str | None = None, city: str | None = None,
            cross: bool = True, db: Session = Depends(get_db)):
    """`cross=true` (default) ignores the `city` filter itself so sibling bars stay visible - the
    behaviour the dashboard's cross-filtering needs. Set `cross=false` for strict filtering."""
    return _count("city", db, city, category, source, cross)


@router.get("/stats/by-category", response_model=schemas.CountResponse, summary="Listing count per category")
def by_category(city: str | None = None, source: str | None = None, category: str | None = None,
                cross: bool = True, db: Session = Depends(get_db)):
    return _count("category", db, city, category, source, cross)


@router.get("/stats/by-source", response_model=schemas.CountResponse, summary="Listing count per data source")
def by_source(city: str | None = None, category: str | None = None, source: str | None = None,
              cross: bool = True, db: Session = Depends(get_db)):
    return _count("source", db, city, category, source, cross)


@router.get("/stats/summary", response_model=schemas.Summary, summary="Headline numbers")
def get_summary(city: str | None = None, category: str | None = None, source: str | None = None,
                db: Session = Depends(get_db)):
    return services.summary(db, city, category, source)


@router.get("/filters", response_model=schemas.FilterOptions, summary="Values for the filter dropdowns")
def get_filters(db: Session = Depends(get_db)):
    return services.options(db)
