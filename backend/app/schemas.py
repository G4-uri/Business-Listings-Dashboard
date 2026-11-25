"""Pydantic schemas = the API contract. Normalisation lives here so every entry
path (notebook, curl, tests) is cleaned the same way before touching the DB."""
import hashlib
import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


def _squash(v: str | None) -> str | None:
    if v is None:
        return None
    v = re.sub(r"\s+", " ", str(v)).strip(" ,;")
    return v or None


class ListingIn(BaseModel):
    business_name: str = Field(min_length=2, max_length=255)
    category: str = Field(min_length=2, max_length=100)
    sub_category: str | None = Field(default=None, max_length=100)
    address: str | None = Field(default=None, max_length=500)
    area: str | None = Field(default=None, max_length=150)
    city: str = Field(min_length=2, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    phone: str | None = None
    website: str | None = Field(default=None, max_length=500)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    source: str = Field(min_length=2, max_length=60)
    source_url: str | None = Field(default=None, max_length=500)
    scraped_at: datetime | None = None

    @field_validator("business_name", "category", "sub_category", "address", "area",
                     "city", "state", "source", "source_url", "website", mode="before")
    @classmethod
    def _clean_text(cls, v):
        return _squash(v)

    @field_validator("city", "state", mode="before")
    @classmethod
    def _title(cls, v):
        v = _squash(v)
        return v.title() if v else v

    @field_validator("phone", mode="before")
    @classmethod
    def _phone(cls, v):
        """Indian mobiles/landlines -> '+91 XXXXXXXXXX'; anything else is kept digits-only or dropped."""
        if not v:
            return None
        digits = re.sub(r"\D", "", str(v))
        if len(digits) >= 10:
            return f"+91 {digits[-10:]}"
        return None

    @model_validator(mode="after")
    def _fingerprint_ready(self):
        if not self.business_name or not self.city:
            raise ValueError("business_name and city are required")
        return self

    def fingerprint(self) -> str:
        """Identity of a business = name + city + first 40 chars of address (case/space-insensitive).
        Re-posting the same scrape therefore never creates duplicates."""
        key = "|".join(
            re.sub(r"[^a-z0-9]", "", (p or "").lower())
            for p in (self.business_name, self.city, (self.address or "")[:40])
        )
        return hashlib.sha256(key.encode()).hexdigest()


class BulkIn(BaseModel):
    listings: list[ListingIn] = Field(min_length=1)


class BulkResult(BaseModel):
    received: int
    inserted: int
    duplicates_skipped: int


class ListingOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    business_name: str
    category: str
    sub_category: str | None
    address: str | None
    area: str | None
    city: str
    state: str | None
    phone: str | None
    website: str | None
    latitude: float | None
    longitude: float | None
    source: str
    source_url: str | None


class Page(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ListingOut]


class CountRow(BaseModel):
    label: str
    count: int


class CountResponse(BaseModel):
    dimension: str
    total: int
    data: list[CountRow]


class Summary(BaseModel):
    total_listings: int
    cities: int
    categories: int
    sources: int
    with_phone: int
    with_coordinates: int


class FilterOptions(BaseModel):
    cities: list[str]
    categories: list[str]
    sources: list[str]
