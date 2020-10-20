import uuid
import json
import base64
import hmac
import hashlib
import requests
import datetime


class LogAnalytics:
    """Writes custom log entries to an Azure Log Analytics workspace.
    """

    def __init__(self):
        """Initialises this instance with default values, including a
           tracking ID that is consistent across all log messages.
        """
        self.id = uuid.uuid4()

    def init(self, customer_id, shared_key, log_type, category=''):
        """Initialise this instance so that it is ready to send messages
           to a Log Analytics workspace.

        Args:
            customer_id:   The `CustomerId` property of the LogAnalytics workspace
            shared_key:  The shared key for the workspace
            log_type:       The custom log type name
            category:       The logging category for all messages
        """
        self.customer_id = customer_id
        self.shared_key = shared_key
        self.log_type = log_type
        self.category = category

    def log(self, level, message):
        """Create and post a log message to the Log Analytics workspace.

        Args:
            level:          The log level for the specified message
            message:        The log message to sent to Log Analytics
        """
        if self.log_type is not None:
            msg = [{
                'id': str(uuid.uuid4()),
                'tracker': str(self.id),
                'level': level,
                'category': self.category,
                'message': message
            }]
            body = json.dumps(msg)
            self._post_data(body)
    
    def _build_signature(self, date, content_length, method, content_type, resource):
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
        x_headers = f'x-ms-date:{date}'
        string_to_hash = f'{method}\n{str(content_length)}\n{content_type}\n{x_headers}\n{resource}'
        bytes_to_hash = string_to_hash.encode('utf-8')
        decoded_key = base64.b64decode(self.shared_key)
        encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode('utf-8')
        authorization = f'SharedKey {self.customer_id}:{encoded_hash}'
        return authorization

    def _post_data(self, body):
        """Send the specified data to the Log Analytics workspace.

        Args:
            body:           The data to send to Log Analytics

        Returns:
            The response from the remote server
        """
        method = 'POST'
        content_type = 'application/json'
        resource = '/api/logs'
        rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        content_length = len(body)
        signature = self._build_signature(rfc1123date, content_length, method, content_type, resource)
        uri = f'https://{self.customer_id}.ods.opinsights.azure.com{resource}?api-version=2016-04-01'
        headers = {
            'Content-Type': content_type,
            'Authorization': signature,
            'Log-Type': self.log_type,
            'x-ms-date': rfc1123date
        }
        response = requests.post(uri, data=body, headers=headers)
        return response
