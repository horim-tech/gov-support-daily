"""수집 결과 저장 및 신규 공고 판별 (당장은 로컬 JSON 파일 기반)."""
import json
from datetime import date
from pathlib import Path

from normalize import Announcement

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SEEN_FILE = DATA_DIR / "seen_ids.json"


def load_seen() -> dict:
    if not SEEN_FILE.exists():
        return {}
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {source: set(ids) for source, ids in raw.items()}


def save_seen(seen: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    serializable = {source: sorted(ids) for source, ids in seen.items()}
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)


def mark_new_and_update(items: list[Announcement]) -> list[Announcement]:
    """items에 is_new 플래그를 채우고, seen_ids.json을 갱신한다."""
    seen = load_seen()
    for item in items:
        source_seen = seen.setdefault(item.source, set())
        if item.external_id and item.external_id not in source_seen:
            item.is_new = True
            source_seen.add(item.external_id)
    save_seen(seen)
    return items


def save_daily_digest(items: list[Announcement], run_date: date | None = None) -> Path:
    run_date = run_date or date.today()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / f"{run_date.isoformat()}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([item.to_dict() for item in items], f, ensure_ascii=False, indent=2)

    latest_path = DATA_DIR / "latest.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump([item.to_dict() for item in items], f, ensure_ascii=False, indent=2)

    return out_path
