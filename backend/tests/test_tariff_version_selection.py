from decimal import Decimal

from tariffguard.models.tariff import TariffVersion
from tariffguard.utils.time import parse_iso


def select_version(versions: list[TariffVersion], timestamp: str) -> TariffVersion | None:
    session_time = parse_iso(timestamp)
    applicable = [version for version in versions if parse_iso(version.validFrom) <= session_time]
    return max(applicable, key=lambda version: parse_iso(version.validFrom), default=None)


def test_selects_newest_tariff_version_before_session_start() -> None:
    versions = [
        TariffVersion(
            tariffId="standard",
            currency="EUR",
            validFrom="2026-06-01T00:00:00Z",
            pricePerKwh="0.49",
            sessionFee="0.35",
            idleFeePerMinute="0.10",
            idleGraceMinutes=15,
            taxRate="0.19",
        ),
        TariffVersion(
            tariffId="standard",
            currency="EUR",
            validFrom="2026-06-20T00:00:00Z",
            pricePerKwh="0.52",
            sessionFee="0.35",
            idleFeePerMinute="0.10",
            idleGraceMinutes=15,
            taxRate="0.19",
        ),
    ]

    chosen = select_version(versions, "2026-06-30T08:00:00Z")

    assert chosen is not None
    assert chosen.pricePerKwh == Decimal("0.52")


def test_returns_none_when_no_tariff_version_is_old_enough() -> None:
    versions = [
        TariffVersion(
            tariffId="standard",
            currency="EUR",
            validFrom="2026-07-01T00:00:00Z",
            pricePerKwh="0.49",
            sessionFee="0.35",
            idleFeePerMinute="0.10",
            idleGraceMinutes=15,
            taxRate="0.19",
        )
    ]

    assert select_version(versions, "2026-06-30T08:00:00Z") is None
