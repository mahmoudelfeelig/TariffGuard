from tariffguard.services.overview import build_overview


def test_overview_ignores_missing_prices() -> None:
    sessions = [
        {"sessionId": "validated", "status": "VALIDATED", "price": {"displayTotal": "12.50"}},
        {"sessionId": "pending", "status": "PENDING_VALIDATION", "price": None},
        {"sessionId": "rejected", "status": "REJECTED"},
    ]

    result = build_overview(sessions, [])

    assert result["kpis"]["sessionsProcessed"] == 3
    assert result["kpis"]["estimatedRevenue"] == "12.50"


def test_overview_builds_real_seven_day_trend_and_filters_selected_window() -> None:
    sessions = [
        {
            "sessionId": "one",
            "status": "VALIDATED",
            "startedAt": "2026-06-25T10:00:00Z",
            "price": {"displayTotal": "8.50"},
        },
        {
            "sessionId": "two",
            "status": "FLAGGED",
            "startedAt": "2026-07-01T10:00:00Z",
            "price": {"displayTotal": "4.00"},
        },
        {
            "sessionId": "old",
            "status": "REJECTED",
            "startedAt": "2026-06-20T10:00:00Z",
        },
    ]

    result = build_overview(sessions, [], "2026-07-01")

    assert result["kpis"]["sessionsProcessed"] == 2
    assert len(result["validationTrend"]) == 7
    assert result["validationTrend"][0]["validated"] == 1
    assert result["validationTrend"][-1]["flagged"] == 1
    assert result["validationTrend"][0]["revenue"] == "8.50"
    assert result["topChargers"][0] == {"name": "UNKNOWN", "value": 2}
