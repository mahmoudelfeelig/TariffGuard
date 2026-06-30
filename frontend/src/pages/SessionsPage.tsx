import { useMemo, useState } from "react";
import { ArrowRight, Filter, Search } from "lucide-react";
import type { SessionRow, SessionStatus } from "../api/types";
import { StatusBadge } from "../components/StatusBadge";
import { formatDate, formatMoney } from "../lib/format";

const statuses: Array<SessionStatus | "ALL"> = ["ALL", "VALIDATED", "FLAGGED", "REJECTED", "PENDING_VALIDATION", "FAILED_PROCESSING"];

export function SessionsPage({ sessions, onOpenSession }: { sessions: SessionRow[]; onOpenSession: (sessionId: string) => void }) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<SessionStatus | "ALL">("ALL");

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return sessions.filter((session) => {
      const matchesStatus = status === "ALL" || session.status === status;
      const matchesQuery = !normalized || [session.sessionId, session.chargerId, session.userId].some((value) => value.toLowerCase().includes(normalized));
      return matchesStatus && matchesQuery;
    });
  }, [query, sessions, status]);

  return (
    <div className="space-y-5">
      <div className="grid gap-3 md:grid-cols-3">
        <Metric label="Visible sessions" value={filtered.length.toString()} detail={`${sessions.length} loaded`} />
        <Metric label="Requires attention" value={sessions.filter((item) => item.status === "FLAGGED" || item.status === "REJECTED").length.toString()} detail="Flagged or rejected" />
        <Metric label="Processed value" value={formatMoney(sessions.reduce((sum, item) => sum + Number(item.price?.displayTotal ?? 0), 0).toFixed(2))} detail="Loaded result set" />
      </div>

      <section className="border border-line bg-panel shadow-panel">
        <div className="flex flex-col gap-3 border-b border-line p-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="font-semibold">Session registry</h2>
            <p className="mt-1 text-xs text-slate-500">Inspect validation outcomes and calculated totals</p>
          </div>
          <div className="flex flex-col gap-2 sm:flex-row">
            <label className="flex h-10 items-center gap-2 rounded border border-line bg-ink px-3 text-slate-400">
              <Search size={16} />
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Session, charger, user" className="w-full bg-transparent text-sm text-white outline-none sm:w-48" />
            </label>
            <label className="flex h-10 items-center gap-2 rounded border border-line bg-ink px-3 text-slate-400">
              <Filter size={16} />
              <select value={status} onChange={(event) => setStatus(event.target.value as SessionStatus | "ALL")} className="bg-transparent text-sm text-white outline-none">
                {statuses.map((item) => <option key={item} value={item} className="bg-panel">{item.split("_").join(" ")}</option>)}
              </select>
            </label>
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="grid min-h-52 place-items-center text-center">
            <div><Search className="mx-auto text-slate-600" /><p className="mt-3 text-sm font-medium">No sessions match these filters</p></div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[900px] text-left text-sm">
              <thead className="bg-panelSoft/40 text-xs uppercase text-slate-500">
                <tr>{["Session", "Charger", "User", "Started", "Energy", "Total", "Status", ""].map((header, index) => <th key={`${header}-${index}`} className="px-5 py-3 font-semibold">{header}</th>)}</tr>
              </thead>
              <tbody className="divide-y divide-line">
                {filtered.map((session) => (
                  <tr key={session.sessionId} className="group hover:bg-panelSoft/50">
                    <td className="px-5 py-4 font-semibold">{session.sessionId}</td>
                    <td className="px-5 py-4 text-slate-300">{session.chargerId}</td>
                    <td className="px-5 py-4 text-slate-400">{session.userId}</td>
                    <td className="whitespace-nowrap px-5 py-4 text-slate-400">{formatDate(session.startedAt)}</td>
                    <td className="px-5 py-4 tabular-nums">{session.energyKwh ? `${session.energyKwh} kWh` : "-"}</td>
                    <td className="px-5 py-4 tabular-nums">{session.price ? formatMoney(session.price.displayTotal, session.price.currency) : "-"}</td>
                    <td className="px-5 py-4"><StatusBadge status={session.status} /></td>
                    <td className="px-5 py-4 text-right"><button onClick={() => onOpenSession(session.sessionId)} aria-label={`Open ${session.sessionId}`} className="grid h-8 w-8 place-items-center rounded border border-line text-slate-400 group-hover:border-mint/40 group-hover:text-mint"><ArrowRight size={15} /></button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

function Metric({ label, value, detail }: { label: string; value: string; detail: string }) {
  return <article className="border border-line bg-panel p-4 shadow-panel"><p className="text-xs font-semibold uppercase text-slate-500">{label}</p><p className="mt-3 text-2xl font-semibold">{value}</p><p className="mt-1 text-xs text-slate-500">{detail}</p></article>;
}
