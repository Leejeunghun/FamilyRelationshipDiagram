# 배포 가이드

이 프로젝트를 실제 인터넷에 올리는 방법을 정리한 문서. 백엔드(FastAPI)와
프론트엔드(React/Vite)를 서로 다른 곳에 배포하고, GitHub으로 둘을 연결한다.

```
[React 프론트엔드] --(build)--> [GitHub Pages]
        |
        | API 호출
        v
[FastAPI 백엔드] --(GitHub 연동 자동배포)--> [Render]
        |
        | DB 연결
        v
[PostgreSQL] --(Supabase Free)
```

## Jekyll로 GitHub Pages를 써봤다면 — 무엇이 다른가

과거 Jekyll 블로그는 마크다운 원본을 push하면 **GitHub이 직접 Jekyll을 실행해서
정적 HTML로 빌드까지 해줬다.** 별도의 빌드 과정을 신경 쓸 필요가 없었던 이유다.

이 프로젝트는 React + TypeScript로 작성되어 있는데, GitHub Pages는 Jekyll만
"내장 기능"으로 지원하고 React/Vite는 알지 못한다. 즉 `.tsx` 원본 파일을 그대로
올려도 브라우저가 실행할 수 없는 상태다 — 누군가 `npm run build`를 실행해서
순수 HTML/CSS/JS 결과물(`dist/` 폴더)로 미리 "구워"줘야 한다.

그 빌드 과정을 자동화해주는 것이 **GitHub Actions**다. Jekyll이 "GitHub이 원래
할 줄 아는 요리"라면, Actions는 "GitHub한테 새 요리법(빌드 방법)을 알려줘서
대신 시키는 것"에 가깝다. 워크플로 파일을 한 번 만들어두면, 그 다음부터는
Jekyll 때처럼 그냥 `git push`만 하면 알아서 빌드되고 배포된다.

| | Jekyll 블로그 | 이 프로젝트 |
|---|---|---|
| 빌드 담당 | GitHub이 알아서 | GitHub Actions 워크플로가 대신 |
| 내가 할 일 | push | push (이후 동일하게 자동) |

## 사전 준비

- GitHub 저장소가 정상적으로 push 가능한 상태여야 한다 (저장소 존재 여부, 이름,
  접근 권한 확인).
- Render, Supabase 계정 (둘 다 무료 플랜으로 충분).

## 1. 데이터베이스 — Supabase

1. [supabase.com](https://supabase.com)에서 새 프로젝트 생성 (Free 플랜).
2. 프로젝트 설정 → Database → Connection string 복사 (`postgresql://...` 형태).
3. 이 문자열을 2단계의 `DATABASE_URL` 환경변수에 사용한다.
4. 주의: 1주일간 접속이 없으면 프로젝트가 자동 일시정지된다 (재접속 시 재개됨).

## 2. 백엔드 — Render

1. [render.com](https://render.com)에서 GitHub 계정으로 로그인 후 저장소 연결.
2. "New Web Service" 생성, Root Directory를 `backend`로 지정.
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. 환경변수(Environment) 설정:
   - `DATABASE_URL` — 1단계에서 복사한 Supabase 연결 문자열
   - `CORS_ORIGINS` — 3단계에서 만들 GitHub Pages 주소 (예: `https://<계정>.github.io`)
5. 배포가 끝나면 `https://<서비스이름>.onrender.com` 형태의 주소가 생긴다 —
   이 주소를 3단계에서 프론트엔드의 API 주소로 사용한다.
6. 이후로는 이 저장소에 `git push`만 하면 Render가 자동으로 재배포한다.
7. 주의: Render 무료 플랜은 디스크가 영구 저장되지 않는다. 재배포/재시작 시
   `backend/uploads/`에 저장된 업로드 사진이 모두 사라진다. 사진 업로드 기능을
   실제로 운영하려면 Supabase Storage 등 별도 오브젝트 스토리지 연동이 필요하다
   (현재는 미구현 — 향후 확장 과제).

## 3. 프론트엔드 — GitHub Pages

### 3-1. `frontend/vite.config.ts`에 base 경로 추가

GitHub Pages는 프로젝트 저장소일 경우 `https://<계정>.github.io/<저장소이름>/`
형태의 URL을 쓰므로, 빌드도 그 하위 경로 기준으로 만들어야 한다.

```ts
export default defineConfig({
  base: '/FamilyRelationshipDiagram/', // 실제 저장소 이름으로 교체
  // ...
})
```

### 3-2. 프로덕션 API 주소 지정

`frontend/.env.production` 파일 생성:

```
VITE_API_URL=https://<서비스이름>.onrender.com
```

### 3-3. GitHub Actions 워크플로 작성

`.github/workflows/deploy.yml`을 만들어 push할 때마다 자동으로 빌드 후
GitHub Pages에 배포하도록 한다 (일반적인 Vite + GitHub Pages 구성).

### 3-4. 저장소 설정에서 Pages 활성화

GitHub 저장소 Settings → Pages → Source를 "GitHub Actions"로 지정.

### 3-5. 배포 확인

master(또는 main)에 push하면 Actions 탭에서 워크플로 실행을 확인할 수 있고,
완료되면 `https://<계정>.github.io/<저장소이름>/`에서 접속 가능하다.

## 배포 후 체크리스트

- [ ] Render 백엔드 `/docs`(Swagger)가 정상 응답하는지 확인
- [ ] Render `CORS_ORIGINS`에 실제 GitHub Pages 주소가 정확히 들어있는지 확인
- [ ] 프론트엔드에서 사람 추가/관계 추가가 실제로 동작하는지 확인
- [ ] "내 ID" 기능으로 데이터가 브라우저별로 잘 분리되는지 확인
