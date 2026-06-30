from __future__ import annotations

from pydantic import BaseModel


class AlertRecord(BaseModel):
    alertId: str
    date: str
    sessionId: str
    chargerId: str
    flagCode: str
    severity: str
    metric: str | None = None
    createdAt: str
