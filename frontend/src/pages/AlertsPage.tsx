import { useEffect, useMemo, useState } from "react";
import { AlertOctagon, ArrowRight, Gauge, ShieldAlert, TimerReset } from "lucide-react";
import { getAlerts } from "../api/client";
import type { AlertRecord } from "../api/types";
import { ViewState } from "../components/ViewState";
import { formatDate } from "../lib/format";

const severityStyle = {
  HIGH: { accent: "border-danger", text: "text-danger", icon: AlertOctagon },
  MEDIUM: { accent: "border-amber", text: "text-amber", icon: ShieldAlert },
  LOW: { accent: "border-sky", text: "text-sky", icon: Gauge },
};

export function AlertsPage({ date, onOpenSession }: { date: string; onOpenSession: (sessionId: string) => void }) {
  const [alerts, setAlerts] = useState<AlertRecord[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setAlerts(null);
    setError(null);
    getAlerts(date).then(setAlerts).catch((reason: Error) => setError(reason.message));
  }, [date]);

  const groups = useMemo(() => ({
    HIGH: alerts?.filter((item) => item.severity === "HIGH") ?? [],
    MEDIUM: alerts?.filter((item) => item.severity === "MEDIUM") ?? [],
    LOW: alerts?.filter((item) => item.severity === "LOW") ?? [],
  }), [alerts]);

  if (error) return <ViewState title="Alerts unavailable" body={error} kind="error" />;
  if (!alerts) return <ViewState title="Loading alerts" body={`Reading validation alerts for ${date}.`} kind="loading" />;
  if (!alerts.length) return <ViewState title="No alerts for this date" body="No medium or high severity validation flags were recorded." />;

  return (
    <div className="space-y-5">
      <div className="grid gap-3 sm:grid-cols-3">
        {(["HIGH", "MEDIUM", "LOW"] as const).map((severity) => {
          const style = severityStyle[severity];
          const Icon = style.icon;
          return <article key={severity} className={`border border-line border-t-2 ${style.accent} bg-panel p-4 shadow-panel`}><div className="flex justify-between"><p className="text-xs font-semibold uppercase text-slate-500">{severity} severity</p><Icon size={17} className={style.text} /></div><p className="mt-4 text-3xl font-semibold">{groups[severity].length}</p><p className="mt-1 text-xs text-slate-500">Open alerts</p></article>;
        })}
      </div>

      <div className="grid gap-5 xl:grid-cols-3">
        {(["HIGH", "MEDIUM", "LOW"] as const).map((severity) => {
          const style = severityStyle[severity];
          return (
            <section key={severity} className="min-w-0">
              <div className="mb-3 flex items-center justify-between"><h2 className="text-sm font-semibold">{severity.charAt(0) + severity.slice(1).toLowerCase()}</h2><span className="rounded bg-panel px-2 py-1 text-xs text-slate-500">{groups[severity].length}</span></div>
              <div className="space-y-3">
                {groups[severity].length ? groups[severity].map((alert) => (
                  <article key={alert.alertId} className={`border border-line border-l-2 ${style.accent} bg-panel p-4 shadow-panel transition-transform hover:-translate-y-0.5`}>
                    <div className="flex items-start justify-between gap-3"><span className={`text-[10px] font-semibold uppercase ${style.text}`}>{alert.flagCode.split("_").join(" ")}</span><button onClick={() => onOpenSession(alert.sessionId)} aria-label={`Open ${alert.sessionId}`} className="text-slate-500 hover:text-white"><ArrowRight size={16} /></button></div>
                    <p className="mt-3 text-sm font-semibold">{alert.sessionId}</p>
                    <p className="mt-1 text-xs text-slate-500">{alert.chargerId}</p>
                    <div className="mt-4 flex items-center justify-between border-t border-line pt-3 text-xs"><span className="flex items-center gap-1.5 text-slate-500"><TimerReset size={13} />{formatDate(alert.createdAt)}</span><span className="font-semibold text-slate-300">{alert.metric ?? "Threshold exceeded"}</span></div>
                  </article>
                )) : <div className="border border-dashed border-line p-5 text-center text-xs text-slate-600">No {severity.toLowerCase()} alerts</div>}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}
