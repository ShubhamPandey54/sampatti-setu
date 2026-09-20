from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------------- Auth ----------------
class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = Field(pattern="^(citizen|police)$")
    police_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = Field(pattern="^(citizen|police)$")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str


class OtpRequiredResponse(BaseModel):
    otp_required: bool = True
    message: str


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    role: str = Field(pattern="^(citizen|police)$")


# ---------------- Found items ----------------
class FoundItemCreate(BaseModel):
    item_name: str
    category: str
    brand: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    event_date: date
    location_ps: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None


class MatchOut(BaseModel):
    ref_number: str
    score: int
    label: str


class FoundItemOut(BaseModel):
    id: int
    tracker_id: str
    item_name: str
    category: str
    brand: Optional[str]
    color: Optional[str]
    description: Optional[str]
    event_date: date
    location_ps: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    status_code: int
    photo_ids: List[str] = []
    matches: List[MatchOut] = []

    class Config:
        from_attributes = True


# ---------------- Stolen / lost reports ----------------
class StolenReportCreate(BaseModel):
    report_type: str = Field(pattern="^(FIR|NCR)$")
    item_name: str
    category: str
    brand: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    event_date: date
    location_ps: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    complainant_mobile: str = Field(pattern=r"^\d{10}$")


class StolenReportOut(BaseModel):
    id: int
    fir_number: str
    report_type: str
    item_name: str
    category: str
    brand: Optional[str]
    color: Optional[str]
    description: Optional[str]
    event_date: date
    location_ps: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    status_code: int
    photo_ids: List[str] = []
    matches: List[MatchOut] = []

    class Config:
        from_attributes = True


class StatusUpdateRequest(BaseModel):
    new_status_code: int
    note: Optional[str] = None
