from __future__ import annotations

from decimal import Decimal
from typing import Any

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from tariffguard.models.alert import AlertRecord
from tariffguard.models.session import SessionRecord
from tariffguard.models.tariff import TariffVersion
from tariffguard.utils.time import day_from_iso, iso_now, parse_iso


def _dump(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return _dump(value.model_dump(mode="json"))
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, list):
        return [_dump(item) for item in value]
    if isinstance(value, dict):
        return {key: _dump(item) for key, item in value.items()}
    return value


class DuplicateSamePayload(Exception):
    def __init__(self, session_id: str) -> None:
        super().__init__("duplicate same payload")
        self.session_id = session_id


class DuplicateChangedPayload(Exception):
    pass


class DynamoRepository:
    def __init__(
        self,
        *,
        main_table_name: str,
        idempotency_table_name: str,
        sqs_queue_url: str | None = None,
        dynamodb_resource: Any | None = None,
        sqs_client: Any | None = None,
    ) -> None:
        dynamodb = dynamodb_resource or boto3.resource("dynamodb")
        self.main = dynamodb.Table(main_table_name)
        self.idempotency = dynamodb.Table(idempotency_table_name)
        self.sqs = sqs_client or boto3.client("sqs")
        self.sqs_queue_url = sqs_queue_url

    def put_idempotency(self, key: str, payload_hash: str, session_id: str) -> None:
        try:
            self.idempotency.put_item(
                Item={
                    "idempotencyKey": key,
                    "payloadHash": payload_hash,
                    "sessionId": session_id,
                    "createdAt": iso_now(),
                },
                ConditionExpression="attribute_not_exists(idempotencyKey)",
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise
            existing = self.idempotency.get_item(Key={"idempotencyKey": key}).get("Item", {})
            if existing.get("payloadHash") == payload_hash:
                raise DuplicateSamePayload(existing.get("sessionId", session_id)) from exc
            raise DuplicateChangedPayload() from exc

    def put_tariff(self, tariff: TariffVersion) -> None:
        item = _dump(tariff)
        item.update(
            {
                "PK": f"TARIFF#{tariff.tariffId}",
                "SK": f"VERSION#{tariff.validFrom}",
                "entityType": "TARIFF_VERSION",
                "GSI1PK": "TARIFFS",
                "GSI1SK": f"{tariff.tariffId}#{tariff.validFrom}",
            }
        )
        self.main.put_item(Item=item)

    def list_tariffs(self) -> list[dict[str, Any]]:
        response = self.main.query(
            IndexName="GSI1", KeyConditionExpression=Key("GSI1PK").eq("TARIFFS")
        )
        grouped: dict[str, list[dict[str, Any]]] = {}
        for item in response.get("Items", []):
            grouped.setdefault(item["tariffId"], []).append(item)
        result = []
        for tariff_id, versions in grouped.items():
            versions.sort(key=lambda item: item["validFrom"], reverse=True)
            result.append(
                {"tariffId": tariff_id, "versions": len(versions), "currentVersion": versions[0]}
            )
        return sorted(result, key=lambda item: item["tariffId"])

    def get_tariff_versions(self, tariff_id: str) -> list[TariffVersion]:
        response = self.main.query(
            KeyConditionExpression=Key("PK").eq(f"TARIFF#{tariff_id}")
            & Key("SK").begins_with("VERSION#"),
            ScanIndexForward=False,
        )
        return [TariffVersion.model_validate(item) for item in response.get("Items", [])]

    def get_tariff_for_timestamp(self, tariff_id: str, timestamp: str) -> TariffVersion | None:
        versions = self.get_tariff_versions(tariff_id)
        session_time = parse_iso(timestamp)
        applicable = [
            version for version in versions if parse_iso(version.validFrom) <= session_time
        ]
        return max(applicable, key=lambda version: parse_iso(version.validFrom), default=None)

    def put_pending_session(self, session: SessionRecord) -> None:
        item = _dump(session)
        now = iso_now()
        session_item = {
            **item,
            "PK": f"SESSION#{session.sessionId}",
            "SK": "METADATA",
            "entityType": "SESSION",
            "GSI1PK": f"CHARGER#{session.chargerId}",
            "GSI1SK": f"SESSION#{session.startedAt}#{session.sessionId}",
        }
        charger_item = {
            **item,
            "PK": f"CHARGER#{session.chargerId}",
            "SK": f"SESSION#{session.startedAt}#{session.sessionId}",
            "entityType": "CHARGER_SESSION",
            "sessionPK": f"SESSION#{session.sessionId}",
            "updatedAt": now,
        }
        self.main.put_item(Item=session_item)
        self.main.put_item(Item=charger_item)

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        return self.main.get_item(Key={"PK": f"SESSION#{session_id}", "SK": "METADATA"}).get("Item")

    def update_session_result(self, record: SessionRecord) -> None:
        self.put_pending_session(record)

    def list_charger_sessions(self, charger_id: str) -> list[dict[str, Any]]:
        response = self.main.query(
            KeyConditionExpression=Key("PK").eq(f"CHARGER#{charger_id}")
            & Key("SK").begins_with("SESSION#"),
            ScanIndexForward=False,
        )
        return response.get("Items", [])

    def put_alerts(self, alerts: list[AlertRecord]) -> None:
        for alert in alerts:
            item = _dump(alert)
            item.update(
                {
                    "PK": f"ALERT_DAY#{alert.date}",
                    "SK": f"ALERT#{alert.severity}#{alert.sessionId}#{alert.flagCode}",
                    "entityType": "ALERT",
                }
            )
            self.main.put_item(Item=item)

    def list_alerts(self, date: str) -> list[dict[str, Any]]:
        response = self.main.query(
            KeyConditionExpression=Key("PK").eq(f"ALERT_DAY#{date}")
            & Key("SK").begins_with("ALERT#")
        )
        return response.get("Items", [])

    def put_audit_summary(self, date: str, summary: dict[str, Any]) -> None:
        self.main.put_item(
            Item={
                "PK": f"AUDIT_DAY#{date}",
                "SK": "SUMMARY",
                "entityType": "AUDIT_SUMMARY",
                **_dump(summary),
            }
        )

    def get_audit_summary(self, date: str) -> dict[str, Any] | None:
        return self.main.get_item(Key={"PK": f"AUDIT_DAY#{date}", "SK": "SUMMARY"}).get("Item")

    def recent_sessions_scan(self, limit: int = 25) -> list[dict[str, Any]]:
        response = self.main.scan(
            FilterExpression="entityType = :entity",
            ExpressionAttributeValues={":entity": "SESSION"},
            Limit=limit,
        )
        return sorted(
            response.get("Items", []), key=lambda item: item.get("startedAt", ""), reverse=True
        )

    def enqueue_session(self, session_id: str) -> None:
        if not self.sqs_queue_url:
            raise RuntimeError("SQS_QUEUE_URL is not configured")
        self.sqs.send_message(
            QueueUrl=self.sqs_queue_url, MessageBody=f'{{"sessionId":"{session_id}"}}'
        )


def alerts_from_session(record: SessionRecord) -> list[AlertRecord]:
    now = iso_now()
    date = day_from_iso(record.startedAt)
    return [
        AlertRecord(
            alertId=f"{record.sessionId}:{flag.code}",
            date=date,
            sessionId=record.sessionId,
            chargerId=record.chargerId,
            flagCode=flag.code,
            severity=flag.severity,
            metric=flag.metric,
            createdAt=now,
        )
        for flag in record.validationFlags
        if flag.severity in {"MEDIUM", "HIGH"}
    ]
