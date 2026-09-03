# 가족관계도

사람(Person)과 관계(부모-자식, 배우자)를 입력하면 React Flow + dagre로 자동 레이아웃된
가족관계도를 보여주는 토이 프로젝트. 형제자매/사촌/조상/자손은 저장하지 않고
parent-child, spouse 두 관계만으로 계산해서 도출한다.

## 폴더 구조

```
backend/   FastAPI + SQLAlchemy API 서버
frontend/  React + TypeScript + Tailwind + React Flow 클라이언트
```

## 백엔드 실행

```bash
cd backend
python -m venv .venv
./.venv/Scripts/activate       # Windows (PowerShell: .venv\Scripts\Activate.ps1)
pip install -r requirements.txt
python seed.py                 # 샘플 3세대 가족 데이터 채우기 (선택, owner_id="seed-demo"로 생성됨)
uvicorn app.main:app --reload --port 8000
```

- API 문서: http://localhost:8000/docs
- 기본 DB는 로컬 SQLite(`backend/family_tree.db`)이며, `backend/.env` (`.env.example` 참고)에서
  `DATABASE_URL`을 Supabase Postgres 연결 문자열로 바꾸면 그대로 전환된다.

## 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

- http://localhost:5173 에서 확인. `VITE_API_URL` 환경변수(기본 `.env` 참고)로 백엔드 주소를 지정한다.
- "사람 추가" 폼에서 얼굴 사진 파일(jpg/png/webp/gif, 5MB 이하)을 선택하면 백엔드
  `POST /upload/photo`로 업로드되고, 반환된 URL이 `photo_url`로 저장된다.
- **로그인 없는 데이터 구분**: 회원가입 없이도 각자 다른 가족관계도를 보게 하기 위해,
  브라우저에 처음 접속하면 임의의 ID(`localStorage`)가 발급되고 모든 API 요청에
  `X-Owner-Id` 헤더로 실려서 그 ID의 데이터만 조회/수정된다. 우측 상단 "내 ID" 버튼에서
  이 값을 확인/복사하거나, 다른 사람에게 받은 ID로 전환해 같은 가족관계도를 공유할 수 있다.
  단, 진짜 로그인이 아니라 값을 아는 사람은 누구나 접근 가능한 수준의 구분이다.

## 배포 (기획서 4~5단계, 계정 필요 — 직접 진행)

- **백엔드 → Render**: GitHub 저장소 연결 후 Free Web Service로 배포. 시작 명령어는
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. 환경변수로 `DATABASE_URL`(Supabase),
  `CORS_ORIGINS`(GitHub Pages 도메인)를 설정한다.
- **DB → Supabase**: 프로젝트 생성 후 Connection string을 `DATABASE_URL`에 사용. 1주일간
  미접속 시 자동 일시정지되니 참고.
- **업로드된 사진 주의**: 사진은 현재 `backend/uploads/`에 로컬 파일로 저장된다. Render Free
  Web Service는 디스크가 영구 저장되지 않아 재배포/재시작 시 업로드된 사진이 모두 사라진다.
  실제로 운영하려면 Supabase Storage 등 별도 오브젝트 스토리지 연동이 필요하다(향후 확장 과제).
- **프론트엔드 → GitHub Pages**: `frontend/vite.config.ts`에 `base: '/<저장소이름>/'`를 추가한 뒤
  `npm run build`로 나온 `dist/`를 GitHub Pages에 배포 (GitHub Actions 워크플로 구성 필요).
  배포 전 `frontend/.env.production`에 Render 백엔드 URL을 `VITE_API_URL`로 지정한다.

## 관계 계산 로직

`backend/app/relationships.py`의 `FamilyGraph`가 전체 Person/Relationship을 한 번 읽어
인접 리스트로 구성한 뒤, 부모/자녀/배우자/형제/조상/자손/사촌을 그래프 순회로 계산한다.
`GET /people/{id}/relatives`에서 결과를 확인할 수 있다.
