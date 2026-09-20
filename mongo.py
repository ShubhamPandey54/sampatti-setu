"""
Photos (found-item photos, complaint photos) are binary blobs that don't
belong in relational rows, so they live in MongoDB via GridFS. Everything
else — users, found items, FIR/NCR reports, audit log, match scores —
stays in SQLite (see app/models.py) because it's structured, relational,
and benefits from real foreign keys and transactions.
"""

import gridfs
from pymongo import MongoClient

from app.core.config import settings

mongo_client = MongoClient(settings.mongo_uri)
mongo_db = mongo_client[settings.mongo_db]
photo_bucket = gridfs.GridFS(mongo_db, collection="item_photos")


def save_photo(file_bytes: bytes, filename: str, content_type: str, metadata: dict) -> str:
    """Stores one photo, returns its GridFS file id as a string."""
    file_id = photo_bucket.put(
        file_bytes,
        filename=filename,
        content_type=content_type,
        metadata=metadata,
    )
    return str(file_id)


def get_photo(file_id: str):
    from bson import ObjectId
    return photo_bucket.get(ObjectId(file_id))
