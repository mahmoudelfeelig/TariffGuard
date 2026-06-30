from tariffguard.handlers import validation_worker


def test_worker_returns_partial_batch_failures(monkeypatch) -> None:
    def fake_process(store, session_id):
        if session_id == "bad":
            raise RuntimeError("boom")

    monkeypatch.setattr(validation_worker, "repo", lambda: object())
    monkeypatch.setattr(validation_worker, "process_session", fake_process)

    result = validation_worker.handler(
        {
            "Records": [
                {"messageId": "ok-1", "body": '{"sessionId":"good"}'},
                {"messageId": "bad-1", "body": '{"sessionId":"bad"}'},
            ]
        },
        None,
    )

    assert result == {"batchItemFailures": [{"itemIdentifier": "bad-1"}]}
