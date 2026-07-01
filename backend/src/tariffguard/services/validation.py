from __future__ import annotations

from decimal import Decimal

from tariffguard.models.session import SessionIngest, ValidationFlag
from tariffguard.models.tariff import TariffVersion
from tariffguard.utils.time import parse_iso


def _flag(
    code: str, severity: str, message: str, rejects: bool, metric: str | None = None
) -> ValidationFlag:
    return ValidationFlag(
        code=code,
        severity=severity,  # type: ignore[arg-type]
        message=message,
        rejectsSession=rejects,
        metric=metric,
    )


def duration_minutes(started_at: str, stopped_at: str) -> Decimal:
    delta = parse_iso(stopped_at) - parse_iso(started_at)
    total_microseconds = (
        (delta.days * 24 * 60 * 60 + delta.seconds) * 1_000_000 + delta.microseconds
    )
    return Decimal(total_microseconds) / Decimal(60_000_000)


def validate_session(session: SessionIngest, tariff: TariffVersion | None) -> list[ValidationFlag]:
    flags: list[ValidationFlag] = []
    started = parse_iso(session.startedAt)
    stopped = parse_iso(session.stoppedAt)
    duration = duration_minutes(session.startedAt, session.stoppedAt)
    energy_kwh = session.meterStopKwh - session.meterStartKwh

    if session.meterStopKwh < session.meterStartKwh:
        flags.append(
            _flag(
                "METER_REVERSED", "HIGH", "Meter stop is below meter start.", True, str(energy_kwh)
            )
        )
    if stopped <= started:
        flags.append(
            _flag(
                "NEGATIVE_DURATION",
                "HIGH",
                "Session stop time is not after start time.",
                True,
                str(duration),
            )
        )
    if tariff is None:
        flags.append(
            _flag(
                "MISSING_TARIFF",
                "HIGH",
                "No tariff version applies to the session timestamp.",
                True,
            )
        )

    if duration > 0:
        average_kw = energy_kwh / (duration / Decimal(60))
    else:
        average_kw = Decimal("0")

    if energy_kwh == 0 and duration > 30:
        flags.append(
            _flag(
                "ZERO_ENERGY_LONG_DURATION",
                "MEDIUM",
                "Long session with no energy delivered.",
                False,
                str(duration),
            )
        )
    if energy_kwh > 150:
        flags.append(
            _flag(
                "EXCESSIVE_ENERGY",
                "HIGH",
                "Energy delivered is above expected charging bounds.",
                False,
                str(energy_kwh),
            )
        )
    if average_kw > 350:
        flags.append(
            _flag(
                "SUSPICIOUS_AVERAGE_POWER",
                "HIGH",
                "Average power is above plausible EV charger limits.",
                False,
                str(average_kw),
            )
        )
    if session.idleMinutes > 120:
        flags.append(
            _flag(
                "LONG_IDLE_TIME",
                "MEDIUM",
                "Idle time is unusually long.",
                False,
                str(session.idleMinutes),
            )
        )
    if duration > 360:
        flags.append(
            _flag(
                "LONG_SESSION_DURATION",
                "LOW",
                "Session duration is longer than six hours.",
                False,
                str(duration),
            )
        )

    return flags


def status_from_flags(flags: list[ValidationFlag]) -> str:
    if any(flag.rejectsSession for flag in flags):
        return "REJECTED"
    if flags:
        return "FLAGGED"
    return "VALIDATED"
