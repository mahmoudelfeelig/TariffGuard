import { AlertCircle, Inbox, LoaderCircle } from "lucide-react";

export function ViewState({
  title,
  body,
  kind = "empty",
  onRetry,
}: {
  title: string;
  body: string;
  kind?: "loading" | "empty" | "error";
  onRetry?: () => void;
}) {
  const Icon = kind === "loading" ? LoaderCircle : kind === "error" ? AlertCircle : Inbox;
  return (
    <div className="grid min-h-72 place-items-center border border-line bg-panel p-6 text-center shadow-panel">
      <div className="max-w-sm">
        <span className={`mx-auto grid h-11 w-11 place-items-center rounded bg-panelSoft ${kind === "error" ? "text-danger" : "text-mint"}`}>
          <Icon size={20} className={kind === "loading" ? "animate-spin" : ""} />
        </span>
        <h2 className="mt-4 text-base font-semibold">{title}</h2>
        <p className="mt-2 text-sm leading-6 text-slate-500">{body}</p>
        {onRetry && <button onClick={onRetry} className="mt-4 rounded bg-mint px-4 py-2 text-sm font-semibold text-slate-950">Try again</button>}
      </div>
    </div>
  );
}
