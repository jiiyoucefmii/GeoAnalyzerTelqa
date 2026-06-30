from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class PlaceCategory(str, Enum):
    clothing_store = "clothing_store"
    delivery_company = "delivery_company"


class SourceStatus(str, Enum):
    candidate = "candidate"
    verified = "verified"
    rejected = "rejected"
    manually_added = "manually_added"


class VerificationResult(str, Enum):
    pass_ = "pass"
    fail = "fail"
    uncertain = "uncertain"


class PlaceBase(BaseModel):
    name: str = Field(min_length=1)
    category: PlaceCategory
    subtype: str | None = None
    phone: str | None = None
    website: str | None = None
    address_text: str | None = None
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    wilaya: str
    commune: str | None = None
    source_status: SourceStatus = SourceStatus.candidate
    verification_score: int = Field(default=0, ge=0, le=100)
    google_place_id: str | None = None
    google_maps_url: str | None = None


class PlaceCreate(PlaceBase):
    pass


class PlacePatch(BaseModel):
    name: str | None = None
    category: PlaceCategory | None = None
    subtype: str | None = None
    phone: str | None = None
    website: str | None = None
    address_text: str | None = None
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    wilaya: str | None = None
    commune: str | None = None
    source_status: SourceStatus | None = None
    verification_score: int | None = Field(default=None, ge=0, le=100)
    google_place_id: str | None = None
    google_maps_url: str | None = None


class PlaceOut(PlaceBase):
    id: UUID
    last_verified_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class VerificationCheckCreate(BaseModel):
    check_type: str
    result: str
    details: str | None = None
    evidence_url: str | None = None
    checked_by: str | None = "admin"


class IngestionRequest(BaseModel):
    wilaya: str
    queries: list[str] = Field(default_factory=list)
    included_types: list[str] = Field(default_factory=list)
    max_pages_per_query: int = Field(default=3, ge=1, le=3)
    enqueue: bool = False


class ClusterRequest(BaseModel):
    wilaya: str
    eps_m: int = Field(default=750, ge=100, le=5000)
    min_samples: int = Field(default=3, ge=2, le=20)


class DistanceRequest(BaseModel):
    wilaya: str
    use_google_routes: bool = False


class VerificationRunRequest(BaseModel):
    wilaya: str | None = None
    place_id: UUID | None = None


class ApiMessage(BaseModel):
    ok: bool = True
    message: str
    data: dict[str, Any] | None = None
