from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from decimal import Decimal
from typing import Any


def build_overview(
    sessions: list[dict[str, Any]], alerts: list[dict[str, Any]], end_date: str | None = None
) -> dict[str, Any]:
    selected = date.fromisoformat(end_date) if end_date else date.today()
    start = selected - timedelta(days=6)
    window_sessions = (
        [
            session
            for session in sessions
            if start.isoformat()
            <= str(session.get("startedAt", ""))[:10]
            <= selected.isoformat()
            and session.get("status") != "INVALIDATED"
        ]
        if end_date
        else [session for session in sessions if session.get("status") != "INVALIDATED"]
    )
    counts = Counter(session.get("status", "UNKNOWN") for session in window_sessions)
    revenue = sum(
        Decimal(str((session.get("price") or {}).get("displayTotal", "0")))
        for session in window_sessions
    )
    alert_counts = Counter(alert.get("flagCode", "UNKNOWN") for alert in alerts)
    daily = {
        (start + timedelta(days=offset)).isoformat(): Counter()
        for offset in range(7)
    }
    for session in window_sessions:
        day = str(session.get("startedAt", ""))[:10]
        if day in daily:
            daily[day][session.get("status", "UNKNOWN")] += 1
            price = session.get("price") or {}
            daily[day]["revenue"] += Decimal(str(price.get("displayTotal", "0")))
            daily[day]["energy"] += Decimal(str(price.get("energyKwh", "0")))
    trend = [
        {
            "date": date.fromisoformat(day).strftime("%b %d"),
            "validated": values["VALIDATED"],
            "flagged": values["FLAGGED"],
            "rejected": values["REJECTED"],
            "sessions": values["VALIDATED"] + values["FLAGGED"] + values["REJECTED"],
            "revenue": str(values["revenue"]),
            "energyKwh": str(values["energy"]),
        }
        for day, values in daily.items()
    ]
    charger_counts = Counter(
        session.get("chargerId", "UNKNOWN") for session in window_sessions
    )
    return {
        "kpis": {
            "sessionsProcessed": len(window_sessions),
            "validated": counts["VALIDATED"],
            "flagged": counts["FLAGGED"],
            "rejected": counts["REJECTED"],
            "estimatedRevenue": str(revenue),
        },
        "validationTrend": trend,
        "topAlertTypes": [
            {"name": code, "value": count} for code, count in alert_counts.most_common(5)
        ],
        "topChargers": [
            {"name": charger_id, "value": count}
            for charger_id, count in charger_counts.most_common(6)
        ],
        "recentSessions": window_sessions[:10],
    }
