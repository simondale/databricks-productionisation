from databricks_cli.sdk.api_client import ApiClient
from databricks_cli.runs.api import RunsApi

import os
import time
import argparse


def main(args):
    api = ApiClient(host=os.environ['DATABRICKS_HOST'], token=os.environ['DATABRICKS_TOKEN'])
    runs = RunsApi(api)

    json = {
        'run_name': 'datapipeline',
        'new_cluster': {
            'spark_version': args.get('spark_version', '7.1.x-cpu-ml-scala2.12'),
            'node_type_id': args.get('node_type', 'Standard_F8s'),
            'num_workers': args.get('num_workers', 1)
        },
        'spark_python_task': {
            'python_file': args.get('file', 'dbfs:/driver/datapipeline.py')
        }
    }

    rsp = runs.submit_run(json)

    run_id = rsp.get('run_id', None)
    if run_id is None:
        exit(1)

    while True:
        rsp = runs.get_run(str(run_id))
        state = rsp.get('state', {}).get('life_cycle_state')
        if state == 'SKIPPED':
            exit(1)
        if state == 'INTERNAL_ERROR':
            exit(1)
        if state == 'TERMINATED':
            break
        time.sleep(5)
           

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--spark-version')
    parser.add_argument('--node_type')
    parser.add_argument('--num_workers')
    parser.add_argument('--file')
    args = vars(parser.parse_args())
    args = {k: v for k, v in args.items() if v is not None}
    main(args)
