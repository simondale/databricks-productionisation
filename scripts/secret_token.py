from databricks_cli.sdk.api_client import ApiClient
from databricks_cli.runs.api import RunsApi

import os
import time
import base64


def main():
    api = ApiClient(
        host=os.environ["DATABRICKS_HOST"],
        token=os.environ["DATABRICKS_TOKEN"],
    )
    runs = RunsApi(api)

    response = api.perform_query(method="GET", path="/preview/scim/v2/Me")
    username = response.get("userName")
    path = f"/Users/{username}/token"

    notebook = """import base64
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
dbutils.notebook.exit(base64.b64encode(token.encode('utf-8')).decode('utf-8'))
"""

    api.perform_query(
        method="POST",
        path="/workspace/import",
        data={
            "content": base64.b64encode(notebook.encode("utf-8")).decode(
                "utf-8"
            ),
            "path": path,
            "language": "PYTHON",
            "overwrite": True,
            "format": "SOURCE",
        },
    )

    json = {
        "existing_cluster_id": os.environ["DATABRICKS_CLUSTER_ID"],
        "notebook_task": {"notebook_path": path},
    }

    rsp = runs.submit_run(json)

    run_id = rsp.get("run_id", None)
    if run_id is None:
        exit(1)

    while True:
        rsp = runs.get_run(str(run_id))
        state = rsp.get("state", {}).get("life_cycle_state")
        if state == "SKIPPED":
            exit(1)
        if state == "INTERNAL_ERROR":
            exit(1)
        if state == "TERMINATED":
            break
        time.sleep(5)

    output = runs.get_run_output(run_id)
    token = output.get("notebook_output").get("result")
    print(base64.b64decode(token.encode("utf-8")).decode("utf-8"))


if __name__ == "__main__":
    main()
