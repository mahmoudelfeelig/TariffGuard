export function formatMoney(value: string, currency = "EUR"): string {
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(Number(value));
}

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}
