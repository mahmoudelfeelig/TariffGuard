import json

from tariffguard.handlers import api
from tariffguard.repositories.dynamodb_repo import DuplicateChangedPayload, DuplicateSamePayload

SESSION_PAYLOAD = {
    "sessionId": "sess_001",
    "chargerId": "BER-CP-014",
    "userId": "user_928",
    "startedAt": "2026-06-30T08:10:00Z",
    "stoppedAt": "2026-06-30T09:25:00Z",
    "meterStartKwh": "1210.4",
    "meterStopKwh": "1242.8",
    "idleMinutes": 20,
    "tariffId": "berlin_public_standard",
}


def event(payload: dict) -> dict:
    return {
        "requestContext": {"http": {"method": "POST"}},
        "rawPath": "/sessions",
        "body": json.dumps(payload),
    }


def test_duplicate_same_payload_returns_existing_state(monkeypatch) -> None:
    class FakeRepo:
        def put_idempotency(self, key, payload_hash, session_id):
            raise DuplicateSamePayload(session_id)

        def get_session(self, session_id):
            return {"sessionId": session_id, "status": "VALIDATED"}

    monkeypatch.setattr(api, "repo", lambda: FakeRepo())
    response = api.handler(event(SESSION_PAYLOAD), None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"sessionId": "sess_001", "status": "VALIDATED"}


def test_duplicate_changed_payload_returns_conflict(monkeypatch) -> None:
    class FakeRepo:
        def put_idempotency(self, key, payload_hash, session_id):
            raise DuplicateChangedPayload()

    monkeypatch.setattr(api, "repo", lambda: FakeRepo())
    response = api.handler(event({**SESSION_PAYLOAD, "idleMinutes": 21}), None)

    assert response["statusCode"] == 409
    assert json.loads(response["body"])["error"] == "idempotency_conflict"
