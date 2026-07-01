import type { SessionStatus } from "../api/types";

const styles: Record<SessionStatus, string> = {
  VALIDATED: "bg-emerald-400/15 text-emerald-300 ring-emerald-400/30",
  FLAGGED: "bg-amber-400/15 text-amber-300 ring-amber-400/30",
  REJECTED: "bg-red-400/15 text-red-300 ring-red-400/30",
  PENDING_VALIDATION: "bg-sky-400/15 text-sky-300 ring-sky-400/30",
  FAILED_PROCESSING: "bg-zinc-400/15 text-zinc-300 ring-zinc-400/30",
  INVALIDATED: "bg-slate-400/10 text-slate-400 ring-slate-400/20",
};

export function StatusBadge({ status }: { status: SessionStatus }) {
  return (
    <span className={`inline-flex min-w-24 justify-center rounded px-2 py-1 text-xs font-semibold ring-1 ${styles[status]}`}>
      {status.replace("_", " ")}
    </span>
  );
}
