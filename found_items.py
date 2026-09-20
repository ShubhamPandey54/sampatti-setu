from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.mongo import save_photo
from app.db.sqlite import get_db
from app.deps import get_current_user, require_role
from app.matching import compute_score, match_label
from app.models import AuditLogEntry, FoundItem, StolenReport, User
from app.reference_data import FOUND_STAGES
from app.schemas import FoundItemCreate, FoundItemOut, MatchOut, StatusUpdateRequest

router = APIRouter(prefix="/found-items", tags=["found-items"])


def _matches_for(found: FoundItem, db: Session) -> List[MatchOut]:
    out = []
    for stolen in db.query(StolenReport).all():
        score = compute_score(found, stolen)
        label = match_label(score)
        if label:
            out.append(MatchOut(ref_number=stolen.fir_number, score=score, label=label))
    return sorted(out, key=lambda m: m.score, reverse=True)


@router.post("", response_model=FoundItemOut)
def report_found_item(
    payload: FoundItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("citizen")),
):
    item = FoundItem(
        item_name=payload.item_name,
        category=payload.category,
        brand=payload.brand,
        color=payload.color,
        description=payload.description,
        event_date=payload.event_date,
        location_ps=payload.location_ps,
        latitude=payload.latitude,
        longitude=payload.longitude,
        reporter_id=user.id,
        photo_ids=[],
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    item.tracker_id = f"FND-{1000 + item.id}"
    db.add(AuditLogEntry(found_item_id=item.id, note="Reported by citizen."))
    db.commit()
    db.refresh(item)

    result = FoundItemOut.model_validate(item)
    result.matches = _matches_for(item, db)
    return result


@router.post("/{item_id}/photos")
def upload_found_item_photos(
    item_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("citizen")),
):
    item = db.query(FoundItem).filter(FoundItem.id == item_id, FoundItem.reporter_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Found item not found.")

    ids = list(item.photo_ids or [])
    for f in files[:3]:
        file_id = save_photo(
            file_bytes=f.file.read(),
            filename=f.filename,
            content_type=f.content_type,
            metadata={"found_item_id": item_id},
        )
        ids.append(file_id)
    item.photo_ids = ids
    db.commit()
    return {"photo_ids": ids}


@router.get("/mine", response_model=List[FoundItemOut])
def my_found_items(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(FoundItem).filter(FoundItem.reporter_id == user.id).all()
    out = []
    for item in items:
        r = FoundItemOut.model_validate(item)
        r.matches = _matches_for(item, db)
        out.append(r)
    return out


@router.get("", response_model=List[FoundItemOut])
def list_found_items(db: Session = Depends(get_db), user: User = Depends(require_role("police"))):
    """Malkhana register — police only."""
    items = db.query(FoundItem).all()
    out = []
    for item in items:
        r = FoundItemOut.model_validate(item)
        r.matches = _matches_for(item, db)
        out.append(r)
    return out


@router.patch("/{item_id}/status", response_model=FoundItemOut)
def update_found_item_status(
    item_id: int,
    payload: StatusUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("police")),
):
    item = db.query(FoundItem).filter(FoundItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Found item not found.")
    if not (1 <= payload.new_status_code <= len(FOUND_STAGES)):
        raise HTTPException(status_code=400, detail="Invalid status code.")

    item.status_code = payload.new_status_code
    stage_name = FOUND_STAGES[payload.new_status_code - 1]
    note = f"Status → [{stage_name}]" + (f": {payload.note}" if payload.note else "")
    db.add(AuditLogEntry(found_item_id=item.id, note=note))
    db.commit()
    db.refresh(item)

    result = FoundItemOut.model_validate(item)
    result.matches = _matches_for(item, db)
    return result
