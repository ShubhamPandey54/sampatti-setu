from datetime import datetime, date

from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import relationship

from app.db.sqlite import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)          # "citizen" | "police"
    police_id = Column(String(40), nullable=True)      # only for role == "police"
    created_at = Column(DateTime, default=datetime.utcnow)

    found_items = relationship("FoundItem", back_populates="reporter")
    stolen_reports = relationship("StolenReport", back_populates="complainant")


class OtpCode(Base):
    __tablename__ = "otp_codes"

    id = Column(Integer, primary_key=True)
    email = Column(String(160), index=True, nullable=False)
    code = Column(String(6), nullable=False)
    purpose = Column(String(20), nullable=False)   # "signup" | "login"
    role = Column(String(20), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    consumed = Column(Boolean, default=False)

    # only populated for purpose == "signup": the not-yet-verified account fields,
    # so we don't create the User row until the email is actually confirmed.
    pending_full_name = Column(String(120), nullable=True)
    pending_hashed_password = Column(String(255), nullable=True)
    pending_police_id = Column(String(40), nullable=True)


class FoundItem(Base):
    __tablename__ = "found_items"

    id = Column(Integer, primary_key=True)
    tracker_id = Column(String(30), unique=True, index=True)  # e.g. "FND-1001"
    item_name = Column(String(160), nullable=False)
    category = Column(String(80), nullable=False)
    brand = Column(String(80), nullable=True)
    color = Column(String(40), nullable=True)
    description = Column(Text, nullable=True)
    event_date = Column(Date, nullable=False)          # date the item was found
    location_ps = Column(String(10), nullable=False)    # police station code
    latitude = Column(String(30), nullable=True)         # GPS captured at report time
    longitude = Column(String(30), nullable=True)
    photo_ids = Column(JSON, default=list)              # list of GridFS file id strings
    status_code = Column(Integer, default=1)             # index into FOUND_STAGES
    created_at = Column(DateTime, default=datetime.utcnow)

    reporter_id = Column(Integer, ForeignKey("users.id"))
    reporter = relationship("User", back_populates="found_items")

    audit_log = relationship("AuditLogEntry", back_populates="found_item", cascade="all, delete-orphan")


class StolenReport(Base):
    __tablename__ = "stolen_reports"

    id = Column(Integer, primary_key=True)
    fir_number = Column(String(30), unique=True, index=True)  # e.g. "FIR-DL-1002"
    report_type = Column(String(10), nullable=False)          # "FIR" | "NCR"
    item_name = Column(String(160), nullable=False)
    category = Column(String(80), nullable=False)
    brand = Column(String(80), nullable=True)
    color = Column(String(40), nullable=True)
    description = Column(Text, nullable=True)
    event_date = Column(Date, nullable=False)           # date the item was lost
    location_ps = Column(String(10), nullable=False)
    latitude = Column(String(30), nullable=True)
    longitude = Column(String(30), nullable=True)
    complainant_mobile = Column(String(15), nullable=False)
    photo_ids = Column(JSON, default=list)
    status_code = Column(Integer, default=1)             # index into FIR_STAGES
    created_at = Column(DateTime, default=datetime.utcnow)

    complainant_id = Column(Integer, ForeignKey("users.id"))
    complainant = relationship("User", back_populates="stolen_reports")

    audit_log = relationship("AuditLogEntry", back_populates="stolen_report", cascade="all, delete-orphan")


class AuditLogEntry(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)
    time = Column(DateTime, default=datetime.utcnow)
    note = Column(Text, nullable=False)

    found_item_id = Column(Integer, ForeignKey("found_items.id"), nullable=True)
    stolen_report_id = Column(Integer, ForeignKey("stolen_reports.id"), nullable=True)

    found_item = relationship("FoundItem", back_populates="audit_log")
    stolen_report = relationship("StolenReport", back_populates="audit_log")
