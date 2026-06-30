from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from tariffguard.models.session import PriceBreakdown, SessionIngest
from tariffguard.models.tariff import TariffVersion

CENT = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_price(session: SessionIngest, tariff: TariffVersion) -> PriceBreakdown:
    energy_kwh = session.meterStopKwh - session.meterStartKwh
    billable_idle = max(0, session.idleMinutes - tariff.idleGraceMinutes)
    energy_amount = energy_kwh * tariff.pricePerKwh
    idle_amount = Decimal(billable_idle) * tariff.idleFeePerMinute
    subtotal = energy_amount + tariff.sessionFee + idle_amount
    tax = subtotal * tariff.taxRate
    total = subtotal + tax
    return PriceBreakdown(
        energyKwh=energy_kwh,
        billableIdleMinutes=billable_idle,
        energyAmount=energy_amount,
        sessionFee=tariff.sessionFee,
        idleAmount=idle_amount,
        subtotal=subtotal,
        tax=tax,
        total=total,
        displayTotal=money(total),
        currency=tariff.currency,
    )
