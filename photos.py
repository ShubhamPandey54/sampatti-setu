from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from gridfs.errors import NoFile

from app.db.mongo import get_photo

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/{file_id}")
def get_photo_by_id(file_id: str):
    """
    Streams a photo straight out of MongoDB GridFS.

    NOTE: this endpoint is intentionally unauthenticated so plain <img src="...">
    tags can load it without attaching a bearer token. For a production
    deployment, put a short-lived signed token on the URL (or proxy it through
    an authenticated route) instead of leaving it fully open.
    """
    try:
        grid_out = get_photo(file_id)
    except (InvalidId, NoFile):
        raise HTTPException(status_code=404, detail="Photo not found.")

    return StreamingResponse(grid_out, media_type=grid_out.content_type or "image/jpeg")
