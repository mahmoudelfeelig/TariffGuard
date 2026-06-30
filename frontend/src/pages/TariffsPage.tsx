import { useEffect, useState } from "react";
import { ArrowDown, CalendarClock, Check, History, ReceiptText } from "lucide-react";
import { getTariffs, getTariffVersions } from "../api/client";
import type { TariffListItem, TariffVersion } from "../api/types";
import { ViewState } from "../components/ViewState";
import { formatDate, formatMoney } from "../lib/format";

export function TariffsPage() {
  const [tariffs, setTariffs] = useState<TariffListItem[] | null>(null);
  const [selectedId, setSelectedId] = useState("");
  const [versions, setVersions] = useState<TariffVersion[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getTariffs().then((items) => {
      setTariffs(items);
      setSelectedId((current) => current || items[0]?.tariffId || "");
    }).catch((reason: Error) => setError(reason.message));
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setVersions(null);
    getTariffVersions(selectedId).then(setVersions).catch((reason: Error) => setError(reason.message));
  }, [selectedId]);

  if (error) return <ViewState title="Tariffs unavailable" body={error} kind="error" />;
  if (!tariffs) return <ViewState title="Loading tariffs" body="Reading tariff IDs and immutable versions." kind="loading" />;
  if (!tariffs.length) return <ViewState title="No tariffs configured" body="Create the first tariff version through POST /tariffs." />;

  const current = versions?.[0];
  const previous = versions?.[1];

  return (
    <div className="grid min-w-0 gap-5 xl:grid-cols-[320px_minmax(0,1fr)]">
      <section className="min-w-0 border border-line bg-panel shadow-panel">
        <div className="border-b border-line p-5"><h2 className="font-semibold">Tariff catalog</h2><p className="mt-1 text-xs text-slate-500">{tariffs.length} configured tariff IDs</p></div>
        <div className="space-y-1 p-2">
          {tariffs.map((tariff) => (
            <button key={tariff.tariffId} onClick={() => setSelectedId(tariff.tariffId)} className={`w-full rounded p-3 text-left ${selectedId === tariff.tariffId ? "bg-mint/10 ring-1 ring-mint/30" : "hover:bg-panelSoft"}`}>
              <div className="flex items-center justify-between gap-3"><span className="truncate text-sm font-semibold">{tariff.tariffId}</span>{selectedId === tariff.tariffId && <Check size={15} className="text-mint" />}</div>
              <p className="mt-2 text-xs text-slate-500">{tariff.versions} version{tariff.versions === 1 ? "" : "s"} · {tariff.currentVersion.currency}</p>
            </button>
          ))}
        </div>
      </section>

      {!versions ? <ViewState title="Loading version history" body="Resolving the selected tariff timeline." kind="loading" /> : (
        <div className="min-w-0 space-y-5">
          <section className="border border-line bg-panel p-5 shadow-panel">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div><p className="text-xs font-semibold uppercase text-mint">Current tariff</p><h2 className="mt-2 text-xl font-semibold">{selectedId}</h2><p className="mt-1 text-sm text-slate-500">Effective {current ? formatDate(current.validFrom) : "-"}</p></div>
              <span className="flex items-center gap-2 rounded bg-mint/10 px-3 py-1.5 text-xs font-semibold text-mint"><span className="h-1.5 w-1.5 rounded-full bg-mint" />ACTIVE</span>
            </div>
            {current && <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4"><Rate icon={ReceiptText} label="Energy" value={`${formatMoney(current.pricePerKwh, current.currency)}/kWh`} /><Rate icon={CalendarClock} label="Session fee" value={formatMoney(current.sessionFee, current.currency)} /><Rate icon={History} label="Idle fee" value={`${formatMoney(current.idleFeePerMinute, current.currency)}/min`} /><Rate icon={ReceiptText} label="Tax" value={`${Number(current.taxRate) * 100}%`} /></div>}
          </section>

          {current && previous && (
            <section className="min-w-0 border border-line bg-panel p-5 shadow-panel">
              <h3 className="font-semibold">Version comparison</h3>
              <p className="mt-1 text-xs text-slate-500">Current version compared with the immediately preceding version</p>
              <div className="mt-5 overflow-x-auto">
                <table className="w-full min-w-[560px] text-sm">
                  <thead className="text-left text-xs uppercase text-slate-500"><tr><th className="pb-3">Field</th><th className="pb-3">Previous</th><th className="pb-3">Current</th><th className="pb-3">Change</th></tr></thead>
                  <tbody className="divide-y divide-line">
                    <Comparison label="Energy rate" before={previous.pricePerKwh} after={current.pricePerKwh} suffix={` ${current.currency}/kWh`} />
                    <Comparison label="Session fee" before={previous.sessionFee} after={current.sessionFee} suffix={` ${current.currency}`} />
                    <Comparison label="Idle fee" before={previous.idleFeePerMinute} after={current.idleFeePerMinute} suffix={` ${current.currency}/min`} />
                    <Comparison label="Grace period" before={previous.idleGraceMinutes.toString()} after={current.idleGraceMinutes.toString()} suffix=" min" />
                  </tbody>
                </table>
              </div>
            </section>
          )}

          <section className="border border-line bg-panel p-5 shadow-panel">
            <div className="flex items-center gap-2"><History size={17} className="text-sky" /><h3 className="font-semibold">Immutable version timeline</h3></div>
            <div className="mt-5 space-y-0">
              {versions.map((version, index) => (
                <div key={version.validFrom} className="relative flex gap-4 pb-6 last:pb-0">
                  {index < versions.length - 1 && <span className="absolute left-[7px] top-5 h-[calc(100%-12px)] w-px bg-line" />}
                  <span className={`relative mt-1 h-4 w-4 shrink-0 rounded-full border-4 ${index === 0 ? "border-mint bg-panel" : "border-slate-600 bg-panel"}`} />
                  <div><div className="flex flex-wrap items-center gap-2"><p className="text-sm font-semibold">{formatDate(version.validFrom)}</p>{index === 0 && <span className="text-[10px] font-semibold uppercase text-mint">Current</span>}</div><p className="mt-1 text-xs text-slate-500">{formatMoney(version.pricePerKwh, version.currency)}/kWh · {formatMoney(version.sessionFee, version.currency)} session fee</p></div>
                </div>
              ))}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

function Rate({ icon: Icon, label, value }: { icon: typeof ReceiptText; label: string; value: string }) {
  return <div className="border border-line bg-ink/40 p-4"><Icon size={16} className="text-slate-500" /><p className="mt-4 text-xs text-slate-500">{label}</p><p className="mt-1 font-semibold">{value}</p></div>;
}

function Comparison({ label, before, after, suffix }: { label: string; before: string; after: string; suffix: string }) {
  const delta = Number(after) - Number(before);
  return <tr><td className="py-4 font-medium">{label}</td><td className="py-4 text-slate-500">{before}{suffix}</td><td className="py-4">{after}{suffix}</td><td className={`py-4 font-semibold ${delta > 0 ? "text-amber" : delta < 0 ? "text-mint" : "text-slate-500"}`}><span className="inline-flex items-center gap-1">{delta !== 0 && <ArrowDown size={13} className={delta > 0 ? "rotate-180" : ""} />}{delta === 0 ? "No change" : Math.abs(delta).toFixed(2)}</span></td></tr>;
}
