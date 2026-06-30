from __future__ import annotations

import json
import os
from typing import Any

from pydantic import ValidationError

from tariffguard.models.session import SessionIngest, SessionRecord
from tariffguard.models.tariff import TariffVersion
from tariffguard.repositories.dynamodb_repo import (
    DuplicateChangedPayload,
    DuplicateSamePayload,
    DynamoRepository,
)
from tariffguard.services.idempotency import idempotency_key, payload_hash
from tariffguard.services.overview import build_overview
from tariffguard.utils.response import no_content, response
from tariffguard.utils.time import iso_now


def repo() -> DynamoRepository:
    return DynamoRepository(
        main_table_name=os.environ["MAIN_TABLE_NAME"],
        idempotency_table_name=os.environ["IDEMPOTENCY_TABLE_NAME"],
        sqs_queue_url=os.environ.get("SQS_QUEUE_URL"),
    )


def _body(event: dict[str, Any]) -> dict[str, Any]:
    raw = event.get("body") or "{}"
    return json.loads(raw) if isinstance(raw, str) else raw


def _route(event: dict[str, Any]) -> tuple[str, str]:
    request = event.get("requestContext", {}).get("http", {})
    return request.get("method", event.get("httpMethod", "GET")), event.get(
        "rawPath", event.get("path", "/")
    )


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    del context
    cors_origin = os.environ.get("CORS_ORIGIN", "*")
    method, path = _route(event)
    store = repo()

    if method == "OPTIONS":
        return no_content(cors_origin=cors_origin)
    if method == "GET" and path == "/health":
        return response(200, {"status": "ok"}, cors_origin=cors_origin)
    if method == "POST" and path == "/tariffs":
        try:
            tariff = TariffVersion.model_validate(_body(event))
        except ValidationError as exc:
            return response(
                400, {"error": "validation_error", "details": exc.errors()}, cors_origin=cors_origin
            )
        store.put_tariff(tariff)
        return response(201, tariff.model_dump(mode="json"), cors_origin=cors_origin)
    if method == "GET" and path == "/tariffs":
        return response(200, {"tariffs": store.list_tariffs()}, cors_origin=cors_origin)
    if method == "GET" and path.startswith("/tariffs/") and path.endswith("/versions"):
        tariff_id = path.split("/")[2]
        return response(
            200,
            {
                "versions": [
                    item.model_dump(mode="json") for item in store.get_tariff_versions(tariff_id)
                ]
            },
            cors_origin=cors_origin,
        )
    if method == "POST" and path == "/sessions":
        try:
            payload = _body(event)
            session = SessionIngest.model_validate(payload)
        except (ValidationError, json.JSONDecodeError) as exc:
            details = exc.errors() if isinstance(exc, ValidationError) else str(exc)
            return response(
                400, {"error": "validation_error", "details": details}, cors_origin=cors_origin
            )
        key = idempotency_key(session.chargerId, session.sessionId)
        digest = payload_hash(session.model_dump())
        try:
            store.put_idempotency(key, digest, session.sessionId)
        except DuplicateSamePayload as exc:
            existing = store.get_session(exc.session_id)
            return response(
                200,
                existing or {"sessionId": exc.session_id, "status": "PENDING_VALIDATION"},
                cors_origin=cors_origin,
            )
        except DuplicateChangedPayload:
            return response(
                409,
                {
                    "error": "idempotency_conflict",
                    "message": "same charger/session with changed payload",
                },
                cors_origin=cors_origin,
            )
        now = iso_now()
        record = SessionRecord(
            **session.model_dump(),
            status="PENDING_VALIDATION",
            rawPayload=session.model_dump(mode="json"),
            createdAt=now,
            updatedAt=now,
        )
        store.put_pending_session(record)
        store.enqueue_session(session.sessionId)
        return response(
            202,
            {"sessionId": session.sessionId, "status": "PENDING_VALIDATION"},
            cors_origin=cors_origin,
        )
    if method == "GET" and path.startswith("/sessions/"):
        session = store.get_session(path.split("/")[2])
        return response(
            200 if session else 404, session or {"error": "not_found"}, cors_origin=cors_origin
        )
    if method == "GET" and path.startswith("/chargers/") and path.endswith("/sessions"):
        charger_id = path.split("/")[2]
        return response(
            200, {"sessions": store.list_charger_sessions(charger_id)}, cors_origin=cors_origin
        )
    if method == "GET" and path == "/alerts":
        date = (event.get("queryStringParameters") or {}).get("date", iso_now()[:10])
        return response(200, {"alerts": store.list_alerts(date)}, cors_origin=cors_origin)
    if method == "GET" and path == "/audit/daily":
        date = (event.get("queryStringParameters") or {}).get("date", iso_now()[:10])
        return response(
            200,
            store.get_audit_summary(date) or {"date": date, "sessions": 0},
            cors_origin=cors_origin,
        )
    if method == "GET" and path == "/overview":
        date = (event.get("queryStringParameters") or {}).get("date", iso_now()[:10])
        return response(
            200,
            build_overview(store.recent_sessions_scan(), store.list_alerts(date)),
            cors_origin=cors_origin,
        )
    if method == "POST" and path == "/dev/seed":
        if os.environ.get("ENVIRONMENT") == "production":
            return response(404, {"error": "not_found"}, cors_origin=cors_origin)
        from tariffguard.seed_data import seed

        return response(201, seed(store), cors_origin=cors_origin)
    return response(404, {"error": "not_found", "path": path}, cors_origin=cors_origin)
