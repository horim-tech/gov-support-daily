"""공고 데이터 공통 스키마."""
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Announcement:
    source: str  # "소진공" | "중진공" | "부산시" | "동래구"
    title: str
    url: str
    posted_date: Optional[str] = None      # 등록일 (YYYY-MM-DD)
    period_start: Optional[str] = None     # 접수 시작일
    period_end: Optional[str] = None       # 접수 마감일
    target: Optional[str] = None           # 지원대상
    summary: Optional[str] = None          # 사업요약
    external_id: Optional[str] = None      # 소스별 고유 ID (중복판별용)
    is_new: bool = False                   # 어제까지 없던 신규 공고인지

    def to_dict(self) -> dict:
        return asdict(self)
