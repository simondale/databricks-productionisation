# Create a Conda Environment

The first step is to create a conda environment that can be used to develop a Python library:

```
conda env create --force --name <env> --file conda.yml
conda env config vars set --name <env> SPARK_LOCAL_IP=127.0.0.1
conda env config vars set --name <env> DATABRICKS_ADDRESS=...
conda env config vars set --name <env> DATABRICKS_API_TOKEN=...
conda env config vars set --name <env> DATABRICKS_ORG=...
conda env config vars set --name <env> DATABRICKS_CLUSTER_ID=...
conda env config vars set --name <env> DATABRICKS_PORT=15001
conda env config vars set --name <env> DATABRICKS_HOST=...
conda env config vars set --name <env> DATABRICKS_TOKEN=...
conda activate <env>
```

Replace the ...s above with relevant settings from Databricks

#