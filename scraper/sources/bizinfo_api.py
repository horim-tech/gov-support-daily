"""기업마당(bizinfo.go.kr) Open API — 소진공/중진공 공고를 대신 조회.

인증키(crtfcKey)는 https://www.bizinfo.go.kr/apiDetail.do?id=bizinfoApi 에서
직접 신청/승인받아 BIZINFO_API_KEY 환경변수로 넣어야 한다. 키가 없으면
빈 목록을 반환한다(다른 소스 수집은 계속 진행되도록).
"""
import os
import requests

from normalize import Announcement

API_URL = "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do"

# 기업마당 응답의 excInsttNm(수행기관명) 값과 우리가 표시할 소스명 매핑
TARGET_INSTITUTIONS = {
    "소상공인시장진흥공단": "소진공",
    "중소벤처기업진흥공단": "중진공",
}


def fetch_latest(search_cnt: int = 100) -> list[Announcement]:
    api_key = os.environ.get("BIZINFO_API_KEY")
    if not api_key:
        print("[bizinfo_api] BIZINFO_API_KEY 미설정 - 기업마당 API 건너뜀")
        return []

    resp = requests.get(
        API_URL,
        params={"crtfcKey": api_key, "dataType": "json", "searchCnt": search_cnt},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    items = data.get("jsonArray", data.get("items", []))
    results = []
    for item in items:
        exc_insttnm = (item.get("excInsttNm") or "").strip()
        matched_source = next(
            (label for keyword, label in TARGET_INSTITUTIONS.items() if keyword in exc_insttnm),
            None,
        )
        if not matched_source:
            continue

        period = item.get("reqstBeginEndDe") or ""
        period_start, _, period_end = period.partition("~")

        results.append(
            Announcement(
                source=matched_source,
                title=item.get("pblancNm", "").strip(),
                url=item.get("pblancUrl", ""),
                posted_date=item.get("creatPnttm"),
                period_start=period_start.strip() or None,
                period_end=period_end.strip() or None,
                target=item.get("trgetNm"),
                summary=item.get("bsnsSumryCn"),
                external_id=item.get("pblancId"),
            )
        )
    return results


if __name__ == "__main__":
    for a in fetch_latest():
        print(a.source, a.posted_date, a.title)
