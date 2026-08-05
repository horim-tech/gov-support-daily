import { getAnnouncements } from "./lib/data";
import DashboardClient from "./dashboard-client";

export const dynamic = "force-dynamic";

export default async function Page() {
  const items = await getAnnouncements();
  return <DashboardClient items={items} />;
}
