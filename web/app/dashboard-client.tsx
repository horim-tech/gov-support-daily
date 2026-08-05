"use client";

import { useMemo, useState } from "react";
import type { Announcement } from "./lib/data";

const SOURCES = ["부산시", "동래구", "소진공", "중진공"] as const;

const SOURCE_COLOR: Record<string, string> = {
  부산시: "bg-source-busan",
  동래구: "bg-source-dongnae",
  소진공: "bg-source-sojingong",
  중진공: "bg-source-jungjingong",
};

function timeAgoLabel(dateStr: string | null): string {
  if (!dateStr) return "";
  return dateStr;
}

export default function DashboardClient({ items }: { items: Announcement[] }) {
  const [query, setQuery] = useState("");
  const [activeSource, setActiveSource] = useState<string>("전체");
  const [newOnly, setNewOnly] = useState(false);

  const counts = useMemo(() => {
    const total = items.length;
    const newCount = items.filter((i) => i.is_new).length;
    const perSource = Object.fromEntries(
      SOURCES.map((s) => [s, items.filter((i) => i.source === s).length])
    );
    return { total, newCount, perSource };
  }, [items]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return items.filter((item) => {
      if (activeSource !== "전체" && item.source !== activeSource) return false;
      if (newOnly && !item.is_new) return false;
      if (!q) return true;
      const haystack = `${item.title} ${item.summary ?? ""} ${item.target ?? ""}`.toLowerCase();
      return haystack.includes(q);
    });
  }, [items, query, activeSource, newOnly]);

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-foreground">정부지원사업 매일 브리핑</h1>
        <p className="mt-1 text-sm text-text-secondary">
          소진공 · 중진공 · 부산시 · 동래구 공고를 한 번에 확인하세요.
        </p>
      </header>

      {/* stat tiles */}
      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-3">
        <StatTile label="전체 공고" value={counts.total} />
        <StatTile label="오늘의 신규" value={counts.newCount} valueClassName="text-status-new" />
        {items.length === 0 && (
          <div className="col-span-full rounded-lg border border-border bg-surface p-4 text-sm text-text-secondary">
            아직 수집된 데이터가 없습니다. <code className="text-xs">scraper/main.py</code>를 먼저 실행하세요.
          </div>
        )}
      </div>

      {/* filters */}
      <div className="mb-5 flex flex-col gap-3">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="업종, 키워드로 검색 (예: 제조업, 청년창업, 수출)"
          className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-foreground placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-source-busan"
        />
        <div className="flex flex-wrap items-center gap-2">
          <SourceTab
            label="전체"
            active={activeSource === "전체"}
            onClick={() => setActiveSource("전체")}
            count={counts.total}
          />
          {SOURCES.map((s) => (
            <SourceTab
              key={s}
              label={s}
              active={activeSource === s}
              onClick={() => setActiveSource(s)}
              count={counts.perSource[s]}
              dotClassName={SOURCE_COLOR[s]}
            />
          ))}
          <label className="ml-auto flex items-center gap-1.5 text-sm text-text-secondary">
            <input
              type="checkbox"
              checked={newOnly}
              onChange={(e) => setNewOnly(e.target.checked)}
              className="h-4 w-4 rounded border-border accent-status-new"
            />
            신규만 보기
          </label>
        </div>
      </div>

      {/* list */}
      <ul className="flex flex-col gap-3">
        {filtered.map((item) => (
          <li key={`${item.source}-${item.external_id}`}>
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block rounded-lg border border-border bg-surface p-4 transition hover:border-source-busan"
            >
              <div className="flex items-center gap-2 text-xs">
                <span
                  className={`inline-block h-2 w-2 rounded-full ${SOURCE_COLOR[item.source] ?? "bg-text-muted"}`}
                  aria-hidden
                />
                <span className="font-medium text-text-secondary">{item.source}</span>
                {item.is_new && (
                  <span className="rounded-full bg-status-new/15 px-2 py-0.5 font-semibold text-status-new">
                    NEW
                  </span>
                )}
                <span className="ml-auto text-text-muted">{timeAgoLabel(item.posted_date)}</span>
              </div>
              <h2 className="mt-1.5 text-sm font-semibold text-foreground">{item.title}</h2>
              {(item.target || item.summary) && (
                <p className="mt-1 line-clamp-2 text-xs text-text-secondary">
                  {item.target}
                  {item.target && item.summary ? " · " : ""}
                  {item.summary}
                </p>
              )}
            </a>
          </li>
        ))}
        {filtered.length === 0 && items.length > 0 && (
          <li className="rounded-lg border border-border bg-surface p-6 text-center text-sm text-text-secondary">
            조건에 맞는 공고가 없습니다.
          </li>
        )}
      </ul>
    </div>
  );
}

function StatTile({
  label,
  value,
  valueClassName,
}: {
  label: string;
  value: number;
  valueClassName?: string;
}) {
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <div className={`text-2xl font-bold tabular-nums ${valueClassName ?? "text-foreground"}`}>
        {value}
      </div>
      <div className="mt-0.5 text-xs text-text-secondary">{label}</div>
    </div>
  );
}

function SourceTab({
  label,
  active,
  onClick,
  count,
  dotClassName,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
  count: number;
  dotClassName?: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition ${
        active
          ? "border-foreground bg-foreground text-background"
          : "border-border bg-surface text-text-secondary hover:border-text-muted"
      }`}
    >
      {dotClassName && <span className={`h-1.5 w-1.5 rounded-full ${dotClassName}`} aria-hidden />}
      {label}
      <span className="tabular-nums opacity-70">{count}</span>
    </button>
  );
}
