import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import schemas, services
from ..config import settings
from ..database import get_db

router = APIRouter(prefix="/api/listings", tags=["listings"])


@router.post("/bulk", response_model=schemas.BulkResult, status_code=201,
             summary="Bulk insert listings (idempotent)")
def bulk_create(payload: schemas.BulkIn, db: Session = Depends(get_db)):
    """Accepts up to `MAX_BULK_ROWS` listings. Duplicates (same name + city + address) are skipped,
    so re-running a scraper never inflates the table."""
    if len(payload.listings) > settings.max_bulk_rows:
        raise HTTPException(413, f"Too many rows: max {settings.max_bulk_rows} per request")
    inserted, skipped = services.bulk_insert(db, payload.listings)
    return schemas.BulkResult(received=len(payload.listings), inserted=inserted, duplicates_skipped=skipped)


@router.get("", response_model=schemas.Page, summary="Browse listings (filter + paginate + search)")
def list_listings(page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=200),
                  city: str | None = None, category: str | None = None, source: str | None = None,
                  q: str | None = Query(None, description="substring of name / address / area"),
                  db: Session = Depends(get_db)):
    total, items = services.search(db, page, page_size, city, category, source, q)
    return schemas.Page(total=total, page=page, page_size=page_size, items=items)


@router.get("/export.csv", summary="Download the (filtered) listings as CSV")
def export_csv(city: str | None = None, category: str | None = None, source: str | None = None,
               db: Session = Depends(get_db)):
    _, items = services.search(db, 1, 100000, city, category, source)
    buf = io.StringIO()
    cols = ["business_name", "category", "sub_category", "address", "area", "city", "state",
            "phone", "website", "latitude", "longitude", "source", "source_url"]
    w = csv.writer(buf)
    w.writerow(cols)
    for it in items:
        w.writerow([getattr(it, c) for c in cols])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=listings.csv"})
