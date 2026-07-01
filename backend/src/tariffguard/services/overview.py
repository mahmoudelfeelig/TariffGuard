from __future__ import annotations

from collections import Counter
from decimal import Decimal
from typing import Any


def build_overview(sessions: list[dict[str, Any]], alerts: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(session.get("status", "UNKNOWN") for session in sessions)
    revenue = sum(
        Decimal(str((session.get("price") or {}).get("displayTotal", "0")))
        for session in sessions
    )
    alert_counts = Counter(alert.get("flagCode", "UNKNOWN") for alert in alerts)
    trend = [
        {
            "date": "Today",
            "validated": counts["VALIDATED"],
            "flagged": counts["FLAGGED"],
            "rejected": counts["REJECTED"],
        }
    ]
    return {
        "kpis": {
            "sessionsProcessed": len(sessions),
            "validated": counts["VALIDATED"],
            "flagged": counts["FLAGGED"],
            "rejected": counts["REJECTED"],
            "estimatedRevenue": str(revenue),
        },
        "validationTrend": trend,
        "topAlertTypes": [
            {"name": code, "value": count} for code, count in alert_counts.most_common(5)
        ],
        "recentSessions": sessions[:10],
    }
