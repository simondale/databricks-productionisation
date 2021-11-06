# Databricks notebook source
import uuid
import json
import base64
import hmac
import hashlib
import requests
import datetime

# COMMAND ----------

class Rfc1123DateProvider:
    """Provides the current date as a RFC1123 formatted string.
    """

    FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

    def __init__(self, datetime: datetime = None):
        """Initialises this instance to an optional datetime.
        Args:
            datetime:        The optional datetime to use
        """
        self.datetime = datetime

    def now(self) -> str:
        """Formats the specified datetime (if set) or the current UTC time
           using the RFC1123 format.
        Returns:
            The formatted datetime string
        """
        return (
            datetime.datetime.fromisoformat(self.datetime)
            if self.datetime is not None
            else datetime.datetime.utcnow()
        ).strftime(Rfc1123DateProvider.FORMAT)

# COMMAND ----------

class LogAnalyticsRequest:
    """Sends data to the Log Analytics workspace.
    """

    RESOURCE = "/api/logs"
    METHOD = "POST"
    CONTENT_TYPE = "application/json"

    def send(self, customer_id: str, headers: dict, data: str) -> None:  # pragma: nocover
        """Builds the URI and makes the HTTP request to LogAnalytics.
        Args:
            customer_id:    The customer ID of the Log Analytics workspace
            headers:        The headers for the HTTP request
            data:           The data for the HTTP request
        Returns:
            The response from the HTTP request
        """
        uri = f"https://{customer_id}.ods.opinsights.azure.com{self.RESOURCE}?api-version=2016-04-01"
        requests.post(uri, data=data, headers=headers)

# COMMAND ----------

class UuidGenerator:
    """Generates UUID strings.
    """

    def __init__(self, uuids: list = None):
        """Initialises this instance with an optional UUID.
        Args:
            uuid:       The optional UUID list
        """
        self.uuids = (
            [str(u) for u in uuids]
            if uuids is not None
            else None
        )

    def new(self):
        """Generates a new UUID or uses the specified (optional) value.
        Returns:
            The string representation of the UUID
        """
        if self.uuids is not None:
            length = len(self.uuids)
            if length > 1:
                return self.uuids.pop(0)
            elif length > 0:
                return self.uuids[0]
        return str(uuid.uuid4())

# COMMAND ----------

class LogAnalytics:
    """Writes custom log entries to an Azure Log Analytics workspace.
    """

    def __init__(
        self,
        date_provider: Rfc1123DateProvider = Rfc1123DateProvider(),
        log_request: LogAnalyticsRequest = LogAnalyticsRequest(),
        uuid_provider: UuidGenerator = UuidGenerator(),
    ):
        """Initialises this instance with default values, including a
           tracking ID that is consistent across all log messages.
        """
        self.date_provider = date_provider
        self.log_request = log_request
        self.uuid_provider = uuid_provider
        self.id = self.uuid_provider.new()
        self.customer_id = None
        self.shared_key = None
        self.log_type = None
        self.category = None

    def init(
        self,
        customer_id: str,
        shared_key: str,
        log_type: str,
        category: str = "",
    ) -> None:
        """Initialise this instance so that it is ready to send messages
           to a Log Analytics workspace.
        Args:
            customer_id:    The `CustomerId` property of the LogAnalytics workspace
            shared_key:     The shared key for the workspace
            log_type:       The custom log type name
            category:       The logging category for all messages
        """
        self.customer_id = customer_id
        self.shared_key = shared_key
        self.log_type = log_type
        self.category = category

    def log(self, level: str, message: str) -> None:
        """Create and post a log message to the Log Analytics workspace.
        Args:
            level:          The log level for the specified message
            message:        The log message to sent to Log Analytics
        """
        if self.log_type is not None:
            msg = [
                {
                    "id": self.uuid_provider.new(),
                    "tracker": self.id,
                    "level": level,
                    "category": self.category,
                    "message": message,
                }
            ]
            body = json.dumps(msg)
            self._post_data(body)

    def _build_signature(
        self,
        date: str,
        content_length: int,
        method: str,
        content_type: str,
        resource: str,
    ) -> str:
        """Create a signature for the specified message.
        Args:
            date:           The RFC1123 formatted date string
            content_length: The length of the log message data
            method:         The HTTP method used to send the data
            content_type:   The type of the data being sent
            resource:       The resource of the service accepting the log message
        Returns:
            The `SharedKey` authorization header
        """
        x_headers = f"x-ms-date:{date}"
        string_to_hash = f"{method}\n{str(content_length)}\n{content_type}\n{x_headers}\n{resource}"
        bytes_to_hash = string_to_hash.encode("utf-8")
        decoded_key = base64.b64decode(self.shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(
                decoded_key, bytes_to_hash, digestmod=hashlib.sha256
            ).digest()
        ).decode("utf-8")
        authorization = f"SharedKey {self.customer_id}:{encoded_hash}"
        return authorization

    def _post_data(self, body: str) -> None:
        """Send the specified data to the Log Analytics workspace.
        Args:
            body:           The data to send to Log Analytics
        """
        rfc1123date = self.date_provider.now()
        content_length = len(body)
        signature = self._build_signature(
            rfc1123date,
            content_length,
            self.log_request.METHOD,
            self.log_request.CONTENT_TYPE,
            self.log_request.RESOURCE,
        )
        headers = {
            "Content-Type": self.log_request.CONTENT_TYPE,
            "Authorization": signature,
            "Log-Type": self.log_type,
            "x-ms-date": rfc1123date,
        }
        self.log_request.send(self.customer_id, headers, body)
