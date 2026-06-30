from __future__ import annotations

from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

SessionStatus = Literal[
    "PENDING_VALIDATION", "VALIDATED", "FLAGGED", "REJECTED", "FAILED_PROCESSING"
]


class SessionIngest(BaseModel):
    sessionId: str = Field(min_length=1)
    chargerId: str = Field(min_length=1)
    userId: str = Field(min_length=1)
    startedAt: str
    stoppedAt: str
    meterStartKwh: Decimal
    meterStopKwh: Decimal
    idleMinutes: int = Field(ge=0)
    tariffId: str = Field(min_length=1)

    @field_validator("meterStartKwh", "meterStopKwh")
    @classmethod
    def non_negative_meter(cls, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("meter values must be non-negative")
        return value


class ValidationFlag(BaseModel):
    code: str
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    message: str
    rejectsSession: bool = False
    metric: str | None = None


class PriceBreakdown(BaseModel):
    energyKwh: Decimal
    billableIdleMinutes: int
    energyAmount: Decimal
    sessionFee: Decimal
    idleAmount: Decimal
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    displayTotal: Decimal
    currency: str


class SessionRecord(BaseModel):
    sessionId: str
    chargerId: str
    userId: str
    startedAt: str
    stoppedAt: str
    meterStartKwh: Decimal
    meterStopKwh: Decimal
    idleMinutes: int
    tariffId: str
    status: SessionStatus
    rawPayload: dict[str, Any]
    price: PriceBreakdown | None = None
    tariffSnapshot: dict[str, Any] | None = None
    validationFlags: list[ValidationFlag] = Field(default_factory=list)
    createdAt: str
    updatedAt: str
