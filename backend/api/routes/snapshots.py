import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import config

router = APIRouter()

@router.get("/snapshots/{filename}")
def get_snapshot(filename: str):
    filepath = os.path.join(config.SNAPSHOTS_DIR, os.path.basename(filename))
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return FileResponse(filepath, media_type="image/jpeg")
