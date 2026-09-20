from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.mongo import save_photo
from app.db.sqlite import get_db
from app.deps import get_current_user, require_role
from app.matching import compute_score, match_label
from app.models import AuditLogEntry, FoundItem, StolenReport, User
from app.reference_data import FIR_STAGES
from app.schemas import MatchOut, StatusUpdateRequest, StolenReportCreate, StolenReportOut

router = APIRouter(prefix="/stolen-reports", tags=["stolen-reports"])


def _matches_for(stolen: StolenReport, db: Session) -> List[MatchOut]:
    out = []
    for found in db.query(FoundItem).all():
        score = compute_score(found, stolen)
        label = match_label(score)
        if label:
            out.append(MatchOut(ref_number=found.tracker_id, score=score, label=label))
    return sorted(out, key=lambda m: m.score, reverse=True)


@router.post("", response_model=StolenReportOut)
def file_stolen_report(
    payload: StolenReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("citizen")),
):
    prefix = "FIR" if payload.report_type == "FIR" else "NCR"
    report = StolenReport(
        report_type=payload.report_type,
        item_name=payload.item_name,
        category=payload.category,
        brand=payload.brand,
        color=payload.color,
        description=payload.description,
        event_date=payload.event_date,
        location_ps=payload.location_ps,
        latitude=payload.latitude,
        longitude=payload.longitude,
        complainant_mobile=payload.complainant_mobile,
        complainant_id=user.id,
        photo_ids=[],
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    report.fir_number = f"{prefix}-DL-{1000 + report.id}"
    db.add(AuditLogEntry(stolen_report_id=report.id, note=f"{payload.report_type} filed by complainant."))
    db.commit()
    db.refresh(report)

    result = StolenReportOut.model_validate(report)
    result.matches = _matches_for(report, db)
    return result


@router.post("/{report_id}/photos")
def upload_stolen_report_photos(
    report_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("citizen")),
):
    report = db.query(StolenReport).filter(
        StolenReport.id == report_id, StolenReport.complainant_id == user.id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    ids = list(report.photo_ids or [])
    for f in files[:3]:
        file_id = save_photo(
            file_bytes=f.file.read(),
            filename=f.filename,
            content_type=f.content_type,
            metadata={"stolen_report_id": report_id},
        )
        ids.append(file_id)
    report.photo_ids = ids
    db.commit()
    return {"photo_ids": ids}


@router.get("/mine", response_model=List[StolenReportOut])
def my_stolen_reports(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    reports = db.query(StolenReport).filter(StolenReport.complainant_id == user.id).all()
    out = []
    for report in reports:
        r = StolenReportOut.model_validate(report)
        r.matches = _matches_for(report, db)
        out.append(r)
    return out


@router.get("", response_model=List[StolenReportOut])
def list_stolen_reports(db: Session = Depends(get_db), user: User = Depends(require_role("police"))):
    """FIR/NCR register — police only."""
    reports = db.query(StolenReport).all()
    out = []
    for report in reports:
        r = StolenReportOut.model_validate(report)
        r.matches = _matches_for(report, db)
        out.append(r)
    return out


@router.patch("/{report_id}/status", response_model=StolenReportOut)
def update_stolen_report_status(
    report_id: int,
    payload: StatusUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("police")),
):
    report = db.query(StolenReport).filter(StolenReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    if not (1 <= payload.new_status_code <= len(FIR_STAGES)):
        raise HTTPException(status_code=400, detail="Invalid status code.")

    report.status_code = payload.new_status_code
    stage_name = FIR_STAGES[payload.new_status_code - 1]
    note = f"Status → [{stage_name}]" + (f": {payload.note}" if payload.note else "")
    db.add(AuditLogEntry(stolen_report_id=report.id, note=note))
    db.commit()
    db.refresh(report)

    result = StolenReportOut.model_validate(report)
    result.matches = _matches_for(report, db)
    return result
