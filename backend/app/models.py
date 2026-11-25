"""ORM model mirroring database/schema.sql (`listing_master`)."""
from datetime import datetime

from sqlalchemy import DECIMAL, BigInteger, DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base

# BigInteger PKs need a variant on SQLite (tests) so autoincrement works.
_PK = BigInteger().with_variant(Integer, "sqlite")


class Listing(Base):
    __tablename__ = "listing_master"

    id: Mapped[int] = mapped_column(_PK, primary_key=True, autoincrement=True)
    business_name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100))
    sub_category: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(String(500))
    area: Mapped[str | None] = mapped_column(String(150))
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(30))
    website: Mapped[str | None] = mapped_column(String(500))
    latitude: Mapped[float | None] = mapped_column(DECIMAL(9, 6))
    longitude: Mapped[float | None] = mapped_column(DECIMAL(9, 6))
    source: Mapped[str] = mapped_column(String(60))
    source_url: Mapped[str | None] = mapped_column(String(500))
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_city", "city"),
        Index("idx_category", "category"),
        Index("idx_source", "source"),
        Index("idx_city_category", "city", "category"),
    )
