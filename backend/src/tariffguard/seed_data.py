from __future__ import annotations

from tariffguard.models.tariff import TariffVersion


def seed(store) -> dict[str, object]:
    tariffs = [
        TariffVersion(
            tariffId="berlin_public_standard",
            currency="EUR",
            validFrom="2026-06-01T00:00:00Z",
            pricePerKwh="0.49",
            sessionFee="0.35",
            idleFeePerMinute="0.10",
            idleGraceMinutes=15,
            taxRate="0.19",
        ),
        TariffVersion(
            tariffId="berlin_public_standard",
            currency="EUR",
            validFrom="2026-06-20T00:00:00Z",
            pricePerKwh="0.52",
            sessionFee="0.35",
            idleFeePerMinute="0.10",
            idleGraceMinutes=15,
            taxRate="0.19",
        ),
    ]
    for tariff in tariffs:
        store.put_tariff(tariff)
    return {"tariffs": len(tariffs)}
