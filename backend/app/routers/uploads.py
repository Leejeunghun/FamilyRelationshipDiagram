import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile

# 정적 파일은 main.py에서 /uploads 경로에 StaticFiles로 마운트되므로,
# 업로드용 POST 엔드포인트는 경로 충돌을 피하기 위해 /upload(단수)를 사용한다.
router = APIRouter(prefix="/upload", tags=["uploads"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/photo")
async def upload_photo(request: Request, file: UploadFile):
    ext = ALLOWED_CONTENT_TYPES.get(file.content_type or "")
    if ext is None:
        raise HTTPException(status_code=400, detail="jpg/png/webp/gif 이미지만 업로드할 수 있습니다")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="파일 크기는 5MB를 넘을 수 없습니다")

    filename = f"{uuid.uuid4().hex}{ext}"
    (UPLOAD_DIR / filename).write_bytes(contents)

    return {"url": f"{str(request.base_url).rstrip('/')}/uploads/{filename}"}
