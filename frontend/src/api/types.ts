export type SessionStatus = "PENDING_VALIDATION" | "VALIDATED" | "FLAGGED" | "REJECTED" | "FAILED_PROCESSING";

export type ValidationTrendPoint = {
  date: string;
  validated: number;
  flagged: number;
  rejected: number;
};

export type AlertType = {
  name: string;
  value: number;
};

export type SessionRow = {
  sessionId: string;
  chargerId: string;
  userId: string;
  startedAt: string;
  meterStartKwh?: string;
  meterStopKwh?: string;
  stoppedAt?: string;
  idleMinutes?: number;
  tariffId?: string;
  energyKwh?: string;
  price?: PriceBreakdown;
  tariffSnapshot?: TariffVersion;
  validationFlags?: ValidationFlag[];
  rawPayload?: Record<string, unknown>;
  status: SessionStatus;
};

export type ValidationFlag = {
  code: string;
  severity: "LOW" | "MEDIUM" | "HIGH";
  message: string;
  rejectsSession?: boolean;
  metric?: string | null;
};

export type PriceBreakdown = {
  energyKwh?: string;
  billableIdleMinutes?: number;
  energyAmount?: string;
  sessionFee?: string;
  idleAmount?: string;
  subtotal?: string;
  tax?: string;
  total?: string;
  displayTotal: string;
  currency: string;
};

export type TariffVersion = {
  tariffId: string;
  currency: string;
  validFrom: string;
  pricePerKwh: string;
  sessionFee: string;
  idleFeePerMinute: string;
  idleGraceMinutes: number;
  taxRate: string;
};

export type TariffListItem = {
  tariffId: string;
  versions: number;
  currentVersion: TariffVersion;
};

export type AlertRecord = {
  alertId: string;
  date: string;
  sessionId: string;
  chargerId: string;
  flagCode: string;
  severity: "LOW" | "MEDIUM" | "HIGH";
  metric?: string | null;
  createdAt: string;
};

export type AuditSummary = {
  date: string;
  sessions: number;
  validated: number;
  flagged: number;
  rejected: number;
  estimatedRevenue: string;
  createdAt?: string;
};

export type Overview = {
  kpis: {
    sessionsProcessed: number;
    validated: number;
    flagged: number;
    rejected: number;
    estimatedRevenue: string;
  };
  validationTrend: ValidationTrendPoint[];
  topAlertTypes: AlertType[];
  recentSessions: SessionRow[];
};
