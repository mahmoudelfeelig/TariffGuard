import { useEffect, useState } from "react";
import type { Overview } from "./api/types";
import { getOverview } from "./api/client";
import { OverviewPage } from "./pages/OverviewPage";

function today() {
  return new Date().toISOString().slice(0, 10);
}

export default function App() {
  const [date, setDate] = useState(today());
  const [overview, setOverview] = useState<Overview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [requestId, setRequestId] = useState(0);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    getOverview(date)
      .then((data) => {
        if (active) {
          setOverview(data);
        }
      })
      .catch((exc: Error) => {
        if (active) {
          setError(exc.message);
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [date, requestId]);

  if (loading) {
    return <StateFrame title="Loading dashboard" body="Fetching validation metrics and recent sessions." loading />;
  }
  if (error) {
    return <StateFrame title="Dashboard unavailable" body={error} tone="error" onRetry={() => setRequestId((value) => value + 1)} />;
  }
  if (!overview) {
    return <StateFrame title="No overview data" body="The API returned no dashboard payload." />;
  }
  return <OverviewPage overview={overview} date={date} onDateChange={setDate} />;
}

function StateFrame({
  title,
  body,
  tone = "default",
  loading = false,
  onRetry,
}: {
  title: string;
  body: string;
  tone?: "default" | "error";
  loading?: boolean;
  onRetry?: () => void;
}) {
  return (
    <div className="min-h-screen bg-ink text-slate-100 lg:grid lg:grid-cols-[240px_1fr]">
      <aside className="hidden border-r border-line bg-sidebar p-5 lg:block">
        <Brand />
        <div className="mt-12 space-y-3">
          {[72, 56, 64, 52, 60].map((width, index) => (
            <div key={index} className="h-9 animate-pulse rounded bg-panelSoft/50" style={{ width: `${width}%` }} />
          ))}
        </div>
      </aside>
      <main className="flex min-h-screen flex-col">
        <header className="flex h-20 items-center border-b border-line px-5 lg:px-8">
          <div className="lg:hidden"><Brand /></div>
        </header>
        <div className="grid flex-1 place-items-center p-5">
          <div className={`w-full max-w-md border-l-2 ${tone === "error" ? "border-danger" : "border-mint"} bg-panel px-6 py-7 shadow-panel`}>
            {loading && <div className="mb-5 h-1 w-full overflow-hidden rounded bg-panelSoft"><div className="loading-bar h-full bg-mint" /></div>}
            <h1 className="text-xl font-semibold">{title}</h1>
            <p className="mt-2 text-sm leading-6 text-slate-400">{body}</p>
            {onRetry && <button onClick={onRetry} className="mt-5 rounded bg-mint px-4 py-2 text-sm font-semibold text-slate-950">Try again</button>}
          </div>
        </div>
      </main>
    </div>
  );
}

function Brand() {
  return (
    <div className="flex items-center gap-3">
      <div className="grid h-10 w-10 place-items-center overflow-hidden rounded bg-[#f4edf2]">
        <img src={`${import.meta.env.BASE_URL}assets/brand/elephant-logo.png`} alt="" className="h-9 w-9 object-contain" />
      </div>
      <div>
        <p className="text-base font-semibold leading-5 text-white">TariffGuard</p>
        <p className="text-[10px] font-semibold uppercase tracking-widest text-slate-500">EV operations</p>
      </div>
    </div>
  );
}
