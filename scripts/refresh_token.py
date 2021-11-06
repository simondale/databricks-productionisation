import requests
import certifi
import urllib
import time
import sys
import os


def main():
    tenant_id = os.environ.get("DATABRICKS_TENANT", "Common")
    client_id = os.environ.get(
        "DATABRICKS_CLIENT_ID", "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
    )

    token_response = {}
    code_response = {}

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    kwargs = {"verify": certifi.where()}

    code_url = (
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/devicecode"
    )
    token_url = (
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    )
    scope = urllib.parse.quote(
        "https://storage.azure.com/.default offline_access"
    )
    client_body = f"client_id={client_id}&scope={scope}"
    response = requests.post(
        code_url, data=client_body, headers=headers, **kwargs
    )
    code_response = response.json()
    print(code_response.get("message"), file=sys.stderr)

    grant_type = urllib.parse.quote(
        "urn:ietf:params:oauth:grant-type:device_code"
    )
    device_code = code_response.get("device_code")
    token_body = f"grant_type={grant_type}&client_id={client_id}&device_code={device_code}"

    expires_in = code_response.get("expires_in")
    while expires_in > 0:
        token_response = requests.post(
            token_url, data=token_body, headers=headers, **kwargs
        ).json()
        if token_response.get("refresh_token") is not None:
            break
        time.sleep(5)
        expires_in -= 5

    refresh_token = token_response.get("refresh_token")
    print(refresh_token)


if __name__ == "__main__":
    main()
