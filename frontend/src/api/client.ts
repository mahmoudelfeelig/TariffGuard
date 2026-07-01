import { mockAlerts, mockAudit, mockOverview, mockSessions, mockTariffs, mockTariffVersions } from "../data/mockData";
import type { AlertRecord, AuditSummary, Overview, SessionRow, TariffListItem, TariffVersion } from "./types";
import { authExpiredEvent, getAccessToken } from "../auth";

const useMocks = import.meta.env.VITE_USE_MOCKS === "true" || !import.meta.env.VITE_API_BASE_URL;
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL as string | undefined;

export async function getOverview(date: string): Promise<Overview> {
  if (useMocks) {
    await new Promise((resolve) => window.setTimeout(resolve, 250));
    return mockOverview;
  }
  const response = await authorizedFetch(`${apiBaseUrl}/overview?date=${date}`);
  if (!response.ok) {
    throw new Error(`Overview request failed with ${response.status}`);
  }
  return response.json() as Promise<Overview>;
}

async function getJson<T>(path: string): Promise<T> {
  const response = await authorizedFetch(`${apiBaseUrl}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function authorizedFetch(url: string): Promise<Response> {
  const accessToken = await getAccessToken();
  const headers = accessToken ? { Authorization: `Bearer ${accessToken}` } : undefined;
  const response = await fetch(url, { headers });
  if (response.status === 401) {
    window.dispatchEvent(new Event(authExpiredEvent));
    throw new Error("Your session has expired. Sign in again.");
  }
  if (response.status === 429) {
    throw new Error("The API request limit was reached. Please retry shortly.");
  }
  return response;
}

export async function getSession(sessionId: string): Promise<SessionRow> {
  if (useMocks) {
    await delay();
    const session = mockSessions.find((item) => item.sessionId === sessionId);
    if (!session) throw new Error("Session not found");
    return session;
  }
  return getJson<SessionRow>(`/sessions/${encodeURIComponent(sessionId)}`);
}

export async function getTariffs(): Promise<TariffListItem[]> {
  if (useMocks) {
    await delay();
    return mockTariffs;
  }
  const result = await getJson<{ tariffs: TariffListItem[] }>("/tariffs");
  return result.tariffs;
}

export async function getTariffVersions(tariffId: string): Promise<TariffVersion[]> {
  if (useMocks) {
    await delay();
    return mockTariffVersions[tariffId] ?? [];
  }
  const result = await getJson<{ versions: TariffVersion[] }>(`/tariffs/${encodeURIComponent(tariffId)}/versions`);
  return result.versions;
}

export async function getAlerts(date: string): Promise<AlertRecord[]> {
  if (useMocks) {
    await delay();
    return mockAlerts;
  }
  const result = await getJson<{ alerts: AlertRecord[] }>(`/alerts?date=${encodeURIComponent(date)}`);
  return result.alerts;
}

export async function getAudit(date: string): Promise<AuditSummary> {
  if (useMocks) {
    await delay();
    return { ...mockAudit, date };
  }
  return getJson<AuditSummary>(`/audit/daily?date=${encodeURIComponent(date)}`);
}

function delay() {
  return new Promise((resolve) => window.setTimeout(resolve, 180));
}
