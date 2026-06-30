from decimal import Decimal

from tariffguard.models.session import SessionIngest
from tariffguard.models.tariff import TariffVersion
from tariffguard.services.validation import duration_minutes, status_from_flags, validate_session


def tariff() -> TariffVersion:
    return TariffVersion(
        tariffId="standard",
        currency="EUR",
        validFrom="2026-01-01T00:00:00Z",
        pricePerKwh="0.49",
        sessionFee="0.35",
        idleFeePerMinute="0.10",
        idleGraceMinutes=15,
        taxRate="0.19",
    )


def session(**overrides) -> SessionIngest:
    data = {
        "sessionId": "sess",
        "chargerId": "charger",
        "userId": "user",
        "startedAt": "2026-06-30T08:00:00Z",
        "stoppedAt": "2026-06-30T09:00:00Z",
        "meterStartKwh": "100",
        "meterStopKwh": "140",
        "idleMinutes": 0,
        "tariffId": "standard",
    }
    data.update(overrides)
    return SessionIngest(**data)


def codes(flags) -> set[str]:
    return {flag.code for flag in flags}


def test_reversed_meter_rejects_session() -> None:
    flags = validate_session(session(meterStartKwh="10", meterStopKwh="9"), tariff())
    assert "METER_REVERSED" in codes(flags)
    assert status_from_flags(flags) == "REJECTED"


def test_high_average_power_flags_session() -> None:
    flags = validate_session(
        session(
            startedAt="2026-06-30T08:00:00Z", stoppedAt="2026-06-30T08:10:00Z", meterStopKwh="170"
        ),
        tariff(),
    )
    assert "SUSPICIOUS_AVERAGE_POWER" in codes(flags)
    assert status_from_flags(flags) == "FLAGGED"


def test_missing_tariff_rejects_session() -> None:
    flags = validate_session(session(), None)
    assert "MISSING_TARIFF" in codes(flags)
    assert status_from_flags(flags) == "REJECTED"


def test_medium_validation_flags_are_flagged_not_rejected() -> None:
    flags = validate_session(
        session(meterStopKwh="100", stoppedAt="2026-06-30T09:01:00Z", idleMinutes=121), tariff()
    )
    assert {"ZERO_ENERGY_LONG_DURATION", "LONG_IDLE_TIME"} <= codes(flags)
    assert status_from_flags(flags) == "FLAGGED"


def test_duration_minutes_is_decimal_without_float_rounding() -> None:
    duration = duration_minutes("2026-06-30T08:00:00Z", "2026-06-30T08:00:00.100000Z")

    assert duration == Decimal("0.001666666666666666666666666667")
