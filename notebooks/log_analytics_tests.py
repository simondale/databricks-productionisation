# Databricks notebook source
# MAGIC %run ./log_analytics

# COMMAND ----------

class MockLogAnalyticsRequest(LogAnalyticsRequest):
  def send(self, customer_id: str, headers: dict, data: str) -> None:
    self.customer_id = customer_id
    self.headers = headers
    self.data = data

# COMMAND ----------

class LogAnalyticsTests(unittest.TestCase):
  def test_build_signature(self):
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
    self.assertEqual(
      f"SharedKey {customer_id}:XbHKAvGr03HLLReEZHtJwDgykdxjruQesZ8FgRH9qi4=", 
      signature, 
      "Signatures must match")
    
  def test_log_analytics_logs_message(self):
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
    self.assertEqual(4, len(headers), "There must be 4 headers")
    self.assertEqual(log_type, headers.get("Log-Type"), "The Log-Type header must be set")
    self.assertEqual(
      datetime.datetime.fromisoformat(
        date
      ).strftime(Rfc1123DateProvider.FORMAT),
      headers.get("x-ms-date"),
      "The x-ms-date header must be set"
    )
    self.assertTrue(
      headers.get("Authorization").startswith(f"SharedKey {customer_id}:"), 
      "The shared key header must start with a customer ID"
    )
    self.assertEqual(
      LogAnalyticsRequest.CONTENT_TYPE, 
      headers.get("Content-Type"),
      "The Content-Type header must be set"
    )

    self.assertEqual(1, len(data), "There must be 1 data item")
    self.assertEqual(level, data[0].get("level"), "The log level must be set")
    self.assertEqual(message, data[0].get("message"), "The log message must be set")
    self.assertEqual(str(uuids[0]), data[0].get("tracker"), "The log tracker must be set")
    self.assertEqual(str(uuids[1]), data[0].get("id"), "The log ID must be set")
