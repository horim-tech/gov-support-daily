import { readFile } from "node:fs/promises";
import path from "node:path";

export type Announcement = {
  source: "부산시" | "동래구" | "소진공" | "중진공" | string;
  title: string;
  url: string;
  posted_date: string | null;
  period_start: string | null;
  period_end: string | null;
  target: string | null;
  summary: string | null;
  external_id: string | null;
  is_new: boolean;
};

const DATA_FILE = path.join(process.cwd(), "..", "data", "latest.json");

export async function getAnnouncements(): Promise<Announcement[]> {
  try {
    const raw = await readFile(DATA_FILE, "utf-8");
    const items = JSON.parse(raw) as Announcement[];
    return items.sort((a, b) => (b.posted_date ?? "").localeCompare(a.posted_date ?? ""));
  } catch {
    return [];
  }
}
