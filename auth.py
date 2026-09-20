import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.sqlite import get_db
from app.models import OtpCode, User
from app.schemas import (
    LoginRequest,
    OtpRequiredResponse,
    SignupRequest,
    TokenResponse,
    VerifyOtpRequest,
)
from app.services.email import send_otp_email

router = APIRouter(prefix="/auth", tags=["auth"])


def _generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"


@router.post("/signup", response_model=OtpRequiredResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    if payload.role == "police" and not payload.police_id:
        raise HTTPException(status_code=400, detail="Police ID is required for police accounts.")

    code = _generate_otp()
    otp = OtpCode(
        email=payload.email,
        code=code,
        purpose="signup",
        role=payload.role,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.otp_expire_minutes),
        pending_full_name=payload.full_name,
        pending_hashed_password=hash_password(payload.password),
        pending_police_id=payload.police_id,
    )
    db.add(otp)
    db.commit()

    send_otp_email(payload.email, code)
    return OtpRequiredResponse(message=f"Verification code sent to {payload.email}.")


@router.post("/login", response_model=OtpRequiredResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email, User.role == payload.role).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email, password, or role.")

    code = _generate_otp()
    otp = OtpCode(
        email=payload.email,
        code=code,
        purpose="login",
        role=payload.role,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.otp_expire_minutes),
    )
    db.add(otp)
    db.commit()

    send_otp_email(payload.email, code)
    return OtpRequiredResponse(message=f"Verification code sent to {payload.email}.")


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    otp = (
        db.query(OtpCode)
        .filter(
            OtpCode.email == payload.email,
            OtpCode.role == payload.role,
            OtpCode.code == payload.code,
            OtpCode.consumed == False,  # noqa: E712
        )
        .order_by(OtpCode.id.desc())
        .first()
    )
    if not otp:
        raise HTTPException(status_code=401, detail="Incorrect or already-used verification code.")
    if otp.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="This verification code has expired. Please request a new one.")

    otp.consumed = True

    if otp.purpose == "signup":
        user = User(
            full_name=otp.pending_full_name,
            email=otp.email,
            hashed_password=otp.pending_hashed_password,
            role=otp.role,
            police_id=otp.pending_police_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user = db.query(User).filter(User.email == otp.email, User.role == otp.role).first()
        db.commit()
        if not user:
            raise HTTPException(status_code=404, detail="Account no longer exists.")

    token = create_access_token(subject=user.email, role=user.role)
    return TokenResponse(access_token=token, role=user.role, full_name=user.full_name)
