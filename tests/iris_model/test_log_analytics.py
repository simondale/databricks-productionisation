from iris_model.log_analytics import (
    LogAnalytics,
    LogAnalyticsRequest,
    Rfc1123DateProvider,
    UuidGenerator,
)

import datetime
import json
import uuid


class MockLogAnalyticsRequest(LogAnalyticsRequest):
    def send(self, customer_id: str, headers: dict, data: str) -> None:
        self.customer_id = customer_id
        self.headers = headers
        self.data = data


def test_build_signature():
    # arrange
    date = "2000-01-01T00:00:00"
    body = '[{"id": "9db4179b-17de-4b3b-ae68-aba7a524feba", "tracker": "c1425424-7a68-42dc-b87e-43e441fd9cef", "level": "INFO", "category": "", "message": "Test message"}]'
    customer_id = str(uuid.uuid4())
    shared_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=="
    event_log = LogAnalytics(date_provider=Rfc1123DateProvider(date))
    event_log.init(customer_id, shared_key, "Test")

    # act
    signature = event_log._build_signature(
        event_log.date_provider.datetime,
        len(body),
        LogAnalyticsRequest.METHOD,
        LogAnalyticsRequest.CONTENT_TYPE,
        LogAnalyticsRequest.RESOURCE,
    )

    # assert
    assert signature == f"SharedKey {customer_id}:XbHKAvGr03HLLReEZHtJwDgykdxjruQesZ8FgRH9qi4="


def test_log_analytics_logs_message():
    # arange
    log_type = "Test"
    level = "INFO"
    message = "Test message"
    date = "2000-01-01T00:00:00"
    uuids = [uuid.uuid4(), uuid.uuid4()]
    customer_id = str(uuid.uuid4())
    shared_key = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=="
    event_log = LogAnalytics(
        log_request=MockLogAnalyticsRequest(),
        date_provider=Rfc1123DateProvider(date),
        uuid_provider=UuidGenerator(uuids),
    )
    event_log.init(customer_id, shared_key, "Test")

    # act
    event_log.log(level, message)
    data = json.loads(event_log.log_request.data)
    headers = event_log.log_request.headers

    # assert
    assert len(headers) == 4
    assert headers.get("Log-Type") == log_type
    assert headers.get("x-ms-date") == datetime.datetime.fromisoformat(
        date
    ).strftime(Rfc1123DateProvider.FORMAT)
    assert headers.get("Authorization").startswith(f"SharedKey {customer_id}:")
    assert headers.get("Content-Type") == LogAnalyticsRequest.CONTENT_TYPE

    assert len(data) == 1
    assert data[0].get("level") == level
    assert data[0].get("message") == message
    assert data[0].get("tracker") == str(uuids[0])
    assert data[0].get("id") == str(uuids[1])


if __name__ == "__main__":
    test_build_signature()
