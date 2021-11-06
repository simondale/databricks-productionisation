from databricks_cli.sdk.api_client import ApiClient
from databricks_cli.runs.api import RunsApi
from databricks_cli.clusters.api import ClusterApi

import os
import time
import argparse


def PipelineException(Exception):
    """An exception thrown when a pipeline fails."""


def execute_job(
    name: str, libraries: list, driver: str, cluster_id: str
) -> None:
    api = ApiClient(
        host=os.environ["DATABRICKS_HOST"],
        token=os.environ["DATABRICKS_TOKEN"],
    )
    runs = RunsApi(api)

    json = {
        "run_name": name,
        "existing_cluster_id": cluster_id,
        "libraries": [{"whl": library} for library in libraries],
        "spark_python_task": {"python_file": driver},
    }

    response = runs.submit_run(json)
    run_id = response.get("run_id", None)
    if run_id is None:
        raise PipelineException("Run ID not present")

    while True:
        rsp = runs.get_run(str(run_id))
        state = rsp.get("state", {}).get("life_cycle_state")
        if state == "SKIPPED":
            raise PipelineException("Job skipped")
        if state == "INTERNAL_ERROR":
            raise PipelineException(f"Internal Error: {rsp.reason}")
        if state == "TERMINATED":
            break
        time.sleep(5)

    return runs.get_run_output(run_id)


def get_create_cluster(args) -> str:
    cluster_id = os.environ.get("DATABRICKS_CLUSTER_ID")
    if cluster_id is None:
        api = ApiClient(
            host=os.environ["DATABRICKS_HOST"],
            token=os.environ["DATABRICKS_TOKEN"],
        )

        clusters = ClusterApi(api)

        json = {
            "cluster_name": args.get("cluster_name", "test"),
            "spark_version": args.get(
                "spark_version", "7.3.x-cpu-ml-scala2.12"
            ),
            "node_type_id": args.get("node_type", "Standard_F4s"),
            "num_workers": args.get("num_workers", 1),
        }

        response = clusters.create_cluster(json)
        cluster_id = response.get("cluster_id")
        created = True
    else:
        created = False

    return cluster_id, created


def delete_cluster(cluster_id: str) -> dict:
    api = ApiClient(
        host=os.environ["DATABRICKS_HOST"],
        token=os.environ["DATABRICKS_TOKEN"],
    )

    clusters = ClusterApi(api)

    json = {"cluster_id": cluster_id}

    return clusters.create_cluster(json)


def main(args):
    cluster_id, created = get_create_cluster(args)

    try:
        # upload_file

        data_output = execute_job(
            "data",
            ["dbfs:/models/iris_model-0.0.1-py3-none-any.whl"],
            "dbfs:/driver/datapipeline.py",
            cluster_id,
        )
        features_output = execute_job(
            "features",
            ["dbfs:/models/iris_model-0.0.1-py3-none-any.whl"],
            "dbfs:/driver/features.py",
            cluster_id,
        )
        training_output = execute_job(
            "training",
            ["dbfs:/models/iris_model-0.0.1-py3-none-any.whl"],
            "dbfs:/driver/training.py",
            cluster_id,
        )
        serving_output = execute_job(
            "serving",
            ["dbfs:/models/iris_model-0.0.1-py3-none-any.whl"],
            "dbfs:/driver/serving.py",
            cluster_id,
        )

        print("done")

    finally:
        if created:
            delete_cluster(cluster_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--spark-version")
    parser.add_argument("--node_type")
    parser.add_argument("--num_workers")
    parser.add_argument("--file")
    parser.add_argument("--library")
    parser.add_argument("--cluster-id")
    parser.add_argument("--cluster-name")
    args = vars(parser.parse_args())
    args = {k: v for k, v in args.items() if v is not None}
    main(args)
