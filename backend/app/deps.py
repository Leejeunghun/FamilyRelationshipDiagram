from fastapi import Header, HTTPException


def get_owner_id(x_owner_id: str | None = Header(default=None)) -> str:
    """로그인 없이 브라우저별로 발급된 익명 ID를 요청 헤더(X-Owner-Id)에서 읽는다.
    실제 인증이 아니라 단순 구분값이므로, 값을 아는 사람은 누구나 그 ID의 데이터에
    접근할 수 있다는 한계가 있다 (토이 프로젝트 수준에서 허용).
    """
    if not x_owner_id or not x_owner_id.strip():
        raise HTTPException(status_code=400, detail="X-Owner-Id 헤더가 필요합니다")
    return x_owner_id.strip()
