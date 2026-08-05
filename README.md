# 정부지원사업 매일 브리핑

소진공·중진공(기업마당 API) / 부산시 / 동래구 지원사업·고시공고를 매일 수집해서
신규 공고만 골라 보여주는 프로젝트.

## 현재 상태

- `scraper/` : Python 스크래퍼. 실행하면 `data/latest.json`에 오늘 수집 결과,
  `data/seen_ids.json`에 지금까지 본 공고 ID를 기록해 다음 실행부터 신규 여부를 판별한다.
- `web/` : Next.js 웹 대시보드. `data/latest.json`을 읽어서 필터·검색·신규 하이라이트를 보여준다.
- `.github/workflows/daily-scrape.yml` : 매일 아침(KST 07:00) 자동으로 스크래퍼를 실행하고
  결과를 저장소에 커밋하는 워크플로 (아직 GitHub 저장소에 연결 전).
- 기업마당 API 연동은 인증키 신청 후로 보류 중 — 지금은 부산시·동래구만 수집됨.

## 아키텍처 (DB 없이 무료로 운영)

별도 DB(Supabase 등) 없이, **GitHub Actions가 매일 데이터를 스크래핑해서 저장소에 커밋**하고
**Vercel이 그 커밋을 감지해 자동 재배포**하는 방식으로 단순화했다. 계정 2개(GitHub, Vercel)만
있으면 서버 비용 없이 매일 아침 최신 데이터를 볼 수 있다.

```
GitHub Actions(매일 07:00 KST) → 스크래퍼 실행 → data/*.json 커밋
        └→ 커밋이 push되면 Vercel이 자동 재배포 → 대시보드에 최신 데이터 반영
```

## 실행 방법 (로컬)

```bash
# 1. 스크래퍼 실행 (데이터 수집)
cd scraper
pip install -r requirements.txt
python main.py

# 2. 대시보드 실행 (다른 터미널에서)
cd web
npm install
npm run dev   # http://localhost:3000
```

기업마당 API를 쓰려면 `.env.example`을 `.env`로 복사 후 `BIZINFO_API_KEY`를 채운다.
(신청: https://www.bizinfo.go.kr/apiDetail.do?id=bizinfoApi)

## 소스별 수집 방식 메모

| 소스 | 방식 | 비고 |
|---|---|---|
| 소진공/중진공 | 기업마당 Open API | 인증키 필요 (사용자 직접 신청) |
| 부산시 | `busan.go.kr/biz/community02` 정적 HTML 스크래핑 | User-Agent 없으면 WAF가 차단함 |
| 동래구 | `eminwon.dongnae.go.kr` (새올 전자민원창구) | GET 단독 요청 시 빈 목록 반환됨. 목록 JSP를 먼저 GET해 세션 쿠키를 받은 뒤, 그 쿠키+Referer로 `OfrAction.do`에 POST해야 실제 데이터가 나온다 (`scraper/sources/dongnae.py` 참고) |

## 다음 단계 (모두 사용자 계정이 필요해 대기 중)

1. 기업마당 API 키 신청 → `.env`에 반영
2. GitHub 저장소 생성 후 이 프로젝트 push (`git init` → `git remote add` → `git push`)
3. 저장소 Settings → Secrets에 `BIZINFO_API_KEY` 등록 (있는 경우)
4. Vercel에서 이 GitHub 저장소 import, Root Directory를 `web`으로 지정해 배포
5. 배포 후 매일 아침 자동 갱신되는지 확인 (Actions 탭에서 워크플로 실행 로그 확인)
