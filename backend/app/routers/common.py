import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

from ..config import settings

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}
MAX_UPLOAD_BYTES = 250 * 1024 * 1024


def save_upload(upload: UploadFile) -> Path:
    extension = Path(upload.filename or ".wav").suffix.lower()
    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(400, "不支持的音频格式")
    path = settings.uploads / f"{uuid.uuid4().hex}{extension}"
    with path.open("wb") as output:
        shutil.copyfileobj(upload.file, output)
    if path.stat().st_size > MAX_UPLOAD_BYTES:
        path.unlink(missing_ok=True)
        raise HTTPException(413, "音频文件不能超过 250 MB")
    return path
