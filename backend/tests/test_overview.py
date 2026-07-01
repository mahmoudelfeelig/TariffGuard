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
