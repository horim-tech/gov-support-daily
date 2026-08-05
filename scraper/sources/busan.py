"""부산광역시 기업지원 공고 스크래퍼 (busan.go.kr/biz/community02)."""
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

from normalize import Announcement

BASE_URL = "https://www.busan.go.kr"
LIST_URL = f"{BASE_URL}/biz/community02"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9",
}


def fetch_page(page: int = 1) -> list[Announcement]:
    resp = requests.get(LIST_URL, params={"curPage": page}, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    results = []
    rows = soup.select("table.boardList tbody tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 4:
            continue
        gosi_no = cells[0].get_text(strip=True)
        link = cells[1].find("a")
        if not link:
            continue
        title = link.get_text(strip=True)
        detail_url = urljoin(BASE_URL, link.get("href", ""))
        dept = cells[2].get_text(strip=True)
        posted_date = cells[3].get_text(strip=True)

        results.append(
            Announcement(
                source="부산시",
                title=title,
                url=detail_url,
                posted_date=posted_date,
                target=dept,
                external_id=gosi_no,
            )
        )
    return results


def fetch_latest(max_pages: int = 2) -> list[Announcement]:
    items: list[Announcement] = []
    for page in range(1, max_pages + 1):
        page_items = fetch_page(page)
        if not page_items:
            break
        items.extend(page_items)
    return items


if __name__ == "__main__":
    for a in fetch_latest(1):
        print(a.posted_date, a.external_id, a.title, a.url)
