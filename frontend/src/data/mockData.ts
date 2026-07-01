import type { AlertRecord, AuditSummary, Operator, Overview, SessionRow, TariffListItem, TariffVersion } from "../api/types";

const tariffCurrent: TariffVersion = {
  tariffId: "berlin_public_standard",
  currency: "EUR",
  validFrom: "2026-06-01T00:00:00Z",
  pricePerKwh: "0.49",
  sessionFee: "0.35",
  idleFeePerMinute: "0.10",
  idleGraceMinutes: 15,
  taxRate: "0.19",
};

const tariffPrevious: TariffVersion = {
  ...tariffCurrent,
  validFrom: "2026-01-01T00:00:00Z",
  pricePerKwh: "0.45",
  sessionFee: "0.30",
};

export const mockSessions: SessionRow[] = [
  {
    sessionId: "sess_001",
    chargerId: "BER-CP-014",
    userId: "user_928",
    startedAt: "2026-06-30T08:10:00Z",
    stoppedAt: "2026-06-30T09:25:00Z",
    meterStartKwh: "1210.4",
    meterStopKwh: "1242.8",
    idleMinutes: 20,
    tariffId: tariffCurrent.tariffId,
    energyKwh: "32.4",
    price: {
      energyKwh: "32.4",
      billableIdleMinutes: 5,
      energyAmount: "15.876",
      sessionFee: "0.35",
      idleAmount: "0.50",
      subtotal: "16.726",
      tax: "3.17794",
      total: "19.90394",
      displayTotal: "19.90",
      currency: "EUR",
    },
    tariffSnapshot: tariffCurrent,
    validationFlags: [],
    rawPayload: {
      sessionId: "sess_001",
      chargerId: "BER-CP-014",
      userId: "user_928",
      startedAt: "2026-06-30T08:10:00Z",
      stoppedAt: "2026-06-30T09:25:00Z",
      meterStartKwh: "1210.4",
      meterStopKwh: "1242.8",
      idleMinutes: 20,
      tariffId: tariffCurrent.tariffId,
    },
    status: "VALIDATED",
  },
  {
    sessionId: "sess_002",
    chargerId: "BER-CP-020",
    userId: "user_441",
    startedAt: "2026-06-30T07:35:00Z",
    stoppedAt: "2026-06-30T08:05:00Z",
    meterStartKwh: "500.0",
    meterStopKwh: "681.2",
    idleMinutes: 4,
    tariffId: tariffCurrent.tariffId,
    energyKwh: "181.2",
    price: { displayTotal: "112.46", currency: "EUR" },
    tariffSnapshot: tariffCurrent,
    validationFlags: [
      { code: "EXCESSIVE_ENERGY", severity: "HIGH", message: "Energy usage exceeds 150 kWh.", metric: "181.2 kWh" },
      { code: "SUSPICIOUS_AVERAGE_POWER", severity: "HIGH", message: "Average charging power exceeds 350 kW.", metric: "362.4 kW" },
    ],
    status: "FLAGGED",
  },
  {
    sessionId: "sess_003",
    chargerId: "BER-CP-006",
    userId: "user_119",
    startedAt: "2026-06-30T06:05:00Z",
    stoppedAt: "2026-06-30T06:45:00Z",
    meterStartKwh: "702.0",
    meterStopKwh: "700.0",
    idleMinutes: 0,
    tariffId: tariffCurrent.tariffId,
    energyKwh: "-2.0",
    validationFlags: [{ code: "METER_REVERSED", severity: "HIGH", message: "Stop meter is below start meter.", rejectsSession: true, metric: "-2.0 kWh" }],
    status: "REJECTED",
  },
  {
    sessionId: "sess_004",
    chargerId: "BER-CP-031",
    userId: "user_305",
    startedAt: "2026-06-30T05:45:00Z",
    stoppedAt: "2026-06-30T06:30:00Z",
    meterStartKwh: "120.0",
    meterStopKwh: "120.0",
    idleMinutes: 0,
    tariffId: tariffCurrent.tariffId,
    energyKwh: "0",
    status: "PENDING_VALIDATION",
  },
];

export const mockTariffs: TariffListItem[] = [
  { tariffId: tariffCurrent.tariffId, versions: 2, currentVersion: tariffCurrent },
  {
    tariffId: "berlin_fleet_offpeak",
    versions: 1,
    currentVersion: { ...tariffCurrent, tariffId: "berlin_fleet_offpeak", pricePerKwh: "0.35", sessionFee: "0.20", idleFeePerMinute: "0.08" },
  },
];

export const mockTariffVersions: Record<string, TariffVersion[]> = {
  berlin_public_standard: [tariffCurrent, tariffPrevious],
  berlin_fleet_offpeak: [mockTariffs[1].currentVersion],
};

export const mockAlerts: AlertRecord[] = [
  { alertId: "sess_002:power", date: "2026-06-30", sessionId: "sess_002", chargerId: "BER-CP-020", flagCode: "SUSPICIOUS_AVERAGE_POWER", severity: "HIGH", metric: "362.4 kW", createdAt: "2026-06-30T08:05:04Z" },
  { alertId: "sess_002:energy", date: "2026-06-30", sessionId: "sess_002", chargerId: "BER-CP-020", flagCode: "EXCESSIVE_ENERGY", severity: "HIGH", metric: "181.2 kWh", createdAt: "2026-06-30T08:05:04Z" },
  { alertId: "sess_003:meter", date: "2026-06-30", sessionId: "sess_003", chargerId: "BER-CP-006", flagCode: "METER_REVERSED", severity: "HIGH", metric: "-2.0 kWh", createdAt: "2026-06-30T06:45:03Z" },
  { alertId: "sess_005:idle", date: "2026-06-30", sessionId: "sess_005", chargerId: "BER-CP-011", flagCode: "LONG_IDLE_TIME", severity: "MEDIUM", metric: "146 min", createdAt: "2026-06-30T04:30:00Z" },
];

export const mockAudit: AuditSummary = {
  date: "2026-06-30",
  sessions: 1284,
  validated: 1168,
  flagged: 91,
  rejected: 25,
  estimatedRevenue: "24891.42",
  createdAt: "2026-06-30T23:55:00Z",
};

export const mockOperators: Operator[] = [
  { username: "demo-admin", email: "admin@tariffguard.demo", enabled: true, status: "CONFIRMED", role: "admin", createdAt: "2026-06-20T08:00:00Z" },
  { username: "demo-operator", email: "operations@tariffguard.demo", enabled: true, status: "CONFIRMED", role: "operator", createdAt: "2026-06-24T09:30:00Z" },
];

export const mockOverview: Overview = {
  kpis: {
    sessionsProcessed: 1284,
    validated: 1168,
    flagged: 91,
    rejected: 25,
    estimatedRevenue: "24891.42",
  },
  validationTrend: [
    { date: "Jun 24", validated: 160, flagged: 14, rejected: 3, sessions: 177, revenue: "3240.20", energyKwh: "6412.4" },
    { date: "Jun 25", validated: 174, flagged: 11, rejected: 4, sessions: 189, revenue: "3584.10", energyKwh: "7022.8" },
    { date: "Jun 26", validated: 182, flagged: 18, rejected: 5, sessions: 205, revenue: "3821.72", energyKwh: "7510.3" },
    { date: "Jun 27", validated: 171, flagged: 10, rejected: 2, sessions: 183, revenue: "3468.25", energyKwh: "6801.7" },
    { date: "Jun 28", validated: 196, flagged: 16, rejected: 4, sessions: 216, revenue: "4102.90", energyKwh: "8093.2" },
    { date: "Jun 29", validated: 207, flagged: 13, rejected: 3, sessions: 223, revenue: "4258.40", energyKwh: "8350.5" },
    { date: "Jun 30", validated: 178, flagged: 9, rejected: 4, sessions: 191, revenue: "3415.85", energyKwh: "6914.8" },
  ],
  topAlertTypes: [
    { name: "SUSPICIOUS_AVERAGE_POWER", value: 38 },
    { name: "LONG_IDLE_TIME", value: 24 },
    { name: "EXCESSIVE_ENERGY", value: 18 },
    { name: "METER_REVERSED", value: 11 },
  ],
  topChargers: [
    { name: "BER-CP-014", value: 96 },
    { name: "BER-CP-020", value: 84 },
    { name: "BER-CP-006", value: 77 },
    { name: "BER-CP-031", value: 69 },
    { name: "BER-CP-011", value: 58 },
  ],
  recentSessions: mockSessions,
};
