"""매일 아침 실행되는 정부지원사업 수집 진입점."""
from normalize import Announcement
from sources import busan, dongnae, bizinfo_api
import storage


def collect_all() -> list[Announcement]:
    items: list[Announcement] = []

    for name, fetch in (
        ("부산시", lambda: busan.fetch_latest(max_pages=2)),
        ("동래구", lambda: dongnae.fetch_latest(max_pages=2)),
        ("기업마당(소진공/중진공)", lambda: bizinfo_api.fetch_latest()),
    ):
        try:
            fetched = fetch()
            print(f"[main] {name}: {len(fetched)}건 수집")
            items.extend(fetched)
        except Exception as e:
            print(f"[main] {name} 수집 실패: {e}")

    return items


def main() -> None:
    items = collect_all()
    items = storage.mark_new_and_update(items)
    out_path = storage.save_daily_digest(items)

    new_items = [i for i in items if i.is_new]
    print(f"\n총 {len(items)}건 수집, 신규 {len(new_items)}건")
    print(f"저장 위치: {out_path}")

    if new_items:
        print("\n[신규 공고]")
        for i in new_items:
            print(f"- ({i.source}) {i.title}")


if __name__ == "__main__":
    main()
