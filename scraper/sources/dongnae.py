"""부산 동래구 고시/공고 스크래퍼 (eminwon.dongnae.go.kr, 새올 전자민원창구).

이 시스템은 전국 대다수 지자체가 공통으로 쓰는 '새올 전자민원창구'로,
직접 GET 요청만으로는 빈 목록이 반환된다. 아래 순서가 반드시 필요하다:
  1) 목록 iframe(JSP) 페이지를 먼저 GET 해서 세션 쿠키를 발급받는다.
  2) 그 쿠키 + Referer를 붙여 OfrAction.do 에 POST 로 목록을 요청한다.
"""
import re
import requests
from bs4 import BeautifulSoup

from normalize import Announcement

BASE = "https://eminwon.dongnae.go.kr"
LIST_JSP = f"{BASE}/emwp/jsp/ofr/OfrNotAncmtLSub.jsp"
ACTION_URL = f"{BASE}/emwp/gov/mogaha/ntis/web/ofr/action/OfrAction.do"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
}
# not_ancmt_se_code: 01,04,05 = 고시/공고/입찰 등 공개 게시 구분 (사이트 기본값과 동일)
LIST_PARAMS = {"not_ancmt_se_code": "01,04,05", "list_gubun": "", "nodate_recent_mm": "12"}

DETAIL_ID_RE = re.compile(r"searchDetail\('(\d+)'\)")


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(HEADERS)
    s.get(LIST_JSP, params=LIST_PARAMS, timeout=15)
    return s


def _detail_url(mgt_no: str) -> str:
    return (
        f"{ACTION_URL}?Key=B_Subject&method=selectOfrNotAncmt"
        f"&methodnm=selectOfrNotAncmtRegst&not_ancmt_mgt_no={mgt_no}"
        f"&not_ancmt_se_code=01,04,05&context=NTIS&homepage_pbs_yn=Y"
        f"&countYn=Y&subCheck=Y&ofr_pageSize=10"
    )


def fetch_page(session: requests.Session, page: int = 1) -> list[Announcement]:
    form = {
        "epcCheck": "",
        "pageIndex": str(page),
        "jndinm": "OfrNotAncmtEJB",
        "context": "NTIS",
        "method": "selectListOfrNotAncmt",
        "methodnm": "selectListOfrNotAncmtHomepage",
        "not_ancmt_mgt_no": "",
        "homepage_pbs_yn": "Y",
        "subCheck": "Y",
        "ofr_pageSize": "10",
        "not_ancmt_se_code": LIST_PARAMS["not_ancmt_se_code"],
        "title": "고시공고",
        "cha_dep_code_nm": "",
        "initValue": "",
        "countYn": "Y",
        "list_gubun": "",
        "not_ancmt_sj": "",
        "not_ancmt_cn": "",
        "dept_nm": "",
        "cgg_code": "",
        "yyyy": "",
        "yyyymmdd": "",
        "recent_mm": "",
        "last_mm": "",
        "nodate_recent_mm": LIST_PARAMS["nodate_recent_mm"],
        "nodate_last_mm": "",
        "not_ancmt_reg_no": "",
        "Key": "",
        "temp": "",
    }
    resp = session.post(
        ACTION_URL,
        data=form,
        headers={"Referer": f"{LIST_JSP}?not_ancmt_se_code=01,04,05&list_gubun=&nodate_recent_mm=12"},
        timeout=15,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    results = []
    for row in soup.select("table.tb_t1 tbody tr"):
        cells = row.find_all("td")
        if len(cells) < 5:
            continue
        onclick = cells[0].find("a").get("onclick", "") if cells[0].find("a") else ""
        m = DETAIL_ID_RE.search(onclick)
        if not m:
            continue
        mgt_no = m.group(1)
        gosi_no = cells[1].get_text(" ", strip=True)
        title = cells[2].get_text(strip=True)
        dept = cells[3].get_text(strip=True)
        posted_date = cells[4].get_text(strip=True)

        results.append(
            Announcement(
                source="동래구",
                title=title,
                url=_detail_url(mgt_no),
                posted_date=posted_date,
                target=dept,
                summary=gosi_no,
                external_id=mgt_no,
            )
        )
    return results


def fetch_latest(max_pages: int = 2) -> list[Announcement]:
    s = _session()
    items: list[Announcement] = []
    for page in range(1, max_pages + 1):
        page_items = fetch_page(s, page)
        if not page_items:
            break
        items.extend(page_items)
    return items


if __name__ == "__main__":
    for a in fetch_latest(1):
        print(a.posted_date, a.external_id, a.title)
