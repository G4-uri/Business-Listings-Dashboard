"""Business logic kept out of the routers so it is unit-testable and reusable."""
from sqlalchemy import and_, func, insert, select
from sqlalchemy.orm import Session

from .models import Listing
from .schemas import ListingIn

DIMENSIONS = {"city": Listing.city, "category": Listing.category, "source": Listing.source}


def bulk_insert(db: Session, rows: list[ListingIn]) -> tuple[int, int]:
    """Insert rows in ONE statement batch; rows whose fingerprint exists are skipped by the DB
    (pre-check + INSERT IGNORE on the UNIQUE key), so this is safe to re-run. Returns (inserted, skipped)."""
    seen, payload = set(), []
    for r in rows:                       # de-dupe inside the payload itself first
        fp = r.fingerprint()
        if fp in seen:
            continue
        seen.add(fp)
        d = r.model_dump(exclude={"scraped_at"})
        d["fingerprint"] = fp
        if r.scraped_at:
            d["scraped_at"] = r.scraped_at
        payload.append(d)

    inserted = 0
    if payload:
        # 1) ask the DB which fingerprints already exist -> exact inserted/skipped counts on any backend
        fps = [d["fingerprint"] for d in payload]
        existing = set()
        for i in range(0, len(fps), 1000):
            existing |= set(db.scalars(select(Listing.fingerprint).where(Listing.fingerprint.in_(fps[i:i + 1000]))))
        fresh = [d for d in payload if d["fingerprint"] not in existing]
        # 2) insert only the new ones; IGNORE still protects against a concurrent writer racing us
        if fresh:
            stmt = insert(Listing)
            stmt = stmt.prefix_with("OR IGNORE" if db.get_bind().dialect.name == "sqlite" else "IGNORE")
            for i in range(0, len(fresh), 1000):  # small packets are friendlier to shared MySQL servers
                db.execute(stmt, fresh[i:i + 1000])
            db.commit()
        inserted = len(fresh)
    return inserted, len(rows) - inserted


def _filters(city=None, category=None, source=None, q=None, skip: str | None = None):
    """Build WHERE clauses. `skip` drops one dimension - used for cross-filtering so a chart
    still shows its sibling bars when it is itself the active filter."""
    conds = []
    for name, val in (("city", city), ("category", category), ("source", source)):
        if val and name != skip:
            conds.append(DIMENSIONS[name] == val)
    if q:
        like = f"%{q.strip()}%"
        conds.append(Listing.business_name.like(like) | Listing.address.like(like) | Listing.area.like(like))
    return conds


def counts_by(db: Session, dimension: str, city=None, category=None, source=None, cross: bool = True):
    col = DIMENSIONS[dimension]
    conds = _filters(city, category, source, skip=dimension if cross else None)
    stmt = select(col.label("label"), func.count().label("count")).group_by(col).order_by(func.count().desc(), col)
    if conds:
        stmt = stmt.where(and_(*conds))
    return [{"label": r.label, "count": r.count} for r in db.execute(stmt)]


def summary(db: Session, city=None, category=None, source=None):
    conds = _filters(city, category, source)
    where = and_(*conds) if conds else None

    def one(expr):
        s = select(expr).select_from(Listing)  # explicit FROM: unfiltered count(*) would otherwise be 1
        return db.scalar(s.where(where) if where is not None else s) or 0

    return {
        "total_listings": one(func.count()),
        "cities": one(func.count(func.distinct(Listing.city))),
        "categories": one(func.count(func.distinct(Listing.category))),
        "sources": one(func.count(func.distinct(Listing.source))),
        "with_phone": one(func.count(Listing.phone)),
        "with_coordinates": one(func.count(Listing.latitude)),
    }


def search(db: Session, page: int, page_size: int, city=None, category=None, source=None, q=None):
    conds = _filters(city, category, source, q)
    base = select(Listing)
    cnt = select(func.count()).select_from(Listing)
    if conds:
        base, cnt = base.where(and_(*conds)), cnt.where(and_(*conds))
    total = db.scalar(cnt) or 0
    items = db.scalars(base.order_by(Listing.id).offset((page - 1) * page_size).limit(page_size)).all()
    return total, items


def options(db: Session):
    return {n: [r[0] for r in db.execute(select(c).distinct().order_by(c))] for n, c in
            (("cities", Listing.city), ("categories", Listing.category), ("sources", Listing.source))}
