from decimal import Decimal

from tariffguard.models.session import SessionIngest
from tariffguard.models.tariff import TariffVersion
from tariffguard.services.pricing import calculate_price


def test_calculates_price_with_decimal_idle_tax_and_display_rounding() -> None:
    session = SessionIngest(
        sessionId="sess_001",
        chargerId="BER-CP-014",
        userId="user_928",
        startedAt="2026-06-30T08:10:00Z",
        stoppedAt="2026-06-30T09:25:00Z",
        meterStartKwh="1210.4",
        meterStopKwh="1242.8",
        idleMinutes=20,
        tariffId="berlin_public_standard",
    )
    tariff = TariffVersion(
        tariffId="berlin_public_standard",
        currency="EUR",
        validFrom="2026-06-01T00:00:00Z",
        pricePerKwh="0.49",
        sessionFee="0.35",
        idleFeePerMinute="0.10",
        idleGraceMinutes=15,
        taxRate="0.19",
    )

    price = calculate_price(session, tariff)

    assert price.energyKwh == Decimal("32.4")
    assert price.billableIdleMinutes == 5
    assert price.subtotal == Decimal("16.726")
    assert price.tax == Decimal("3.17794")
    assert price.displayTotal == Decimal("19.90")


def test_pricing_does_not_use_float_values() -> None:
    session = SessionIngest(
        sessionId="sess_002",
        chargerId="CP-1",
        userId="user",
        startedAt="2026-06-30T08:00:00Z",
        stoppedAt="2026-06-30T08:30:00Z",
        meterStartKwh="0.10",
        meterStopKwh="0.30",
        idleMinutes=0,
        tariffId="t1",
    )
    tariff = TariffVersion(
        tariffId="t1",
        currency="EUR",
        validFrom="2026-01-01T00:00:00Z",
        pricePerKwh="0.10",
        sessionFee="0.00",
        idleFeePerMinute="0.00",
        idleGraceMinutes=0,
        taxRate="0.19",
    )

    price = calculate_price(session, tariff)

    assert isinstance(price.total, Decimal)
    assert price.total == Decimal("0.0238")
