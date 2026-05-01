import os
import re
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
import config

router = APIRouter()

CHUNK_SIZE = 1024 * 512  # 512 KB chunks

def _iter_file(path: str, start: int, end: int):
    with open(path, "rb") as f:
        f.seek(start)
        remaining = end - start + 1
        while remaining > 0:
            chunk = f.read(min(CHUNK_SIZE, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk

@router.get("/recordings/{filename}")
def get_recording(filename: str, request: Request):
    filepath = os.path.join(config.RECORDINGS_DIR, os.path.basename(filename))
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Recording not found")

    file_size = os.path.getsize(filepath)
    range_header = request.headers.get("range")

    if range_header:

        match = re.match(r"bytes=(\d*)-(\d*)", range_header)
        if match:
            start_str, end_str = match.group(1), match.group(2)
            start = int(start_str) if start_str else 0
            end   = int(end_str)   if end_str   else file_size - 1
            end   = min(end, file_size - 1)

            content_length = end - start + 1
            headers = {
                "Content-Range":  f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges":  "bytes",
                "Content-Length": str(content_length),
                "Content-Type":   "video/webm" if filename.endswith(".webm") else "video/mp4",
            }
            return StreamingResponse(
                _iter_file(filepath, start, end),
                status_code=206,
                headers=headers,
                media_type="video/webm" if filename.endswith(".webm") else "video/mp4",
            )

    headers = {
        "Accept-Ranges":  "bytes",
        "Content-Length": str(file_size),
        "Content-Type":   "video/webm" if filename.endswith(".webm") else "video/mp4",
    }
    return StreamingResponse(
        _iter_file(filepath, 0, file_size - 1),
        status_code=200,
        headers=headers,
        media_type="video/webm" if filename.endswith(".webm") else "video/mp4",
    )
