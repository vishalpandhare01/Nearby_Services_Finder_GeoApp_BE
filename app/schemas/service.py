from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ---------------------------
# CREATE (Admin input)
# ---------------------------
class ServiceCreate(BaseModel):
    name: str
    category: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    rating: Optional[float] = Field(None, ge=0, le=5)


# ---------------------------
# UPDATE (Admin input)
# ---------------------------
class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    rating: Optional[float] = Field(None, ge=0, le=5)


# ---------------------------
# RESPONSE (Public API / Map)
# ---------------------------
class ServiceResponse(BaseModel):
    id: UUID
    name: str
    category: str
    latitude: float
    longitude: float
    rating: Optional[float] = None
    created_at: datetime
    distance: Optional[float] = None  # km (for nearby search)
    

    class Config:
        from_attributes = True


# ---------------------------
# SEARCH (optional structured input)
# ---------------------------
class ServiceSearch(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float = Field(..., gt=0)
    category: Optional[str] = None