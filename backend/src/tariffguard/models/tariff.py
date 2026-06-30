from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class TariffVersion(BaseModel):
    tariffId: str = Field(min_length=1)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    validFrom: str
    pricePerKwh: Decimal
    sessionFee: Decimal
    idleFeePerMinute: Decimal
    idleGraceMinutes: int = Field(ge=0)
    taxRate: Decimal


class TariffListItem(BaseModel):
    tariffId: str
    versions: int
    currentVersion: TariffVersion | None = None
