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

# Development

```
python setup.py develop
```

# Build

```
python setup.py bdist_wheel
```

# Hosting

```
gunicorn --bind 0.0.0.0:5000 iris_model.hosting:app
```

# Docker

```
build -t iris_model .
```

```
docker run --rm -e DATABRICKS_HOST -e DATABRICKS_TOKEN -p 5000:5000 -it iris_model
```

# API Testing

```
curl -H 'Content-Type: application/json' -d '{"columns":["sepal_length","sepal_width","petal_length","petal_width"],"index":[0,1],"data":[[5.1,3.5,1.4,0.2],[2.9,1.0,5.4,3.2]]}' http://localhost:5000/predict
```


Update the `venv/bin/activate` script to add these lines:

```
if [ -f "$VIRTUAL_ENV/../.env" ] ; then
   source <(cat "$VIRTUAL_ENV/../.env" | sed -e 's/^/export /g')
fi
```

Then create a file called `.env` in the root folder with the following contents:

```
DATABRICKS_ADDRESS=<url to databricks workspace>
DATABRICKS_API_TOKEN=<databricks access token>
DATABRICKS_ORG=<org id>
DATABRICKS_CLUSTER_ID=<cluster id>
DATABRICKS_PORT=15001
SPARK_LOCAL_IP=127.0.0.1
DATABRICKS_HOST=<url to databricks workspace>
DATABRICKS_TOKEN=<databricks access token>
DATABRICKS_TENANT=<azure ad tenant id>
DATABRICKS_ADLS_PASSTHROUGH=1
```

Also, in order to access secret scopes through `dbutils`, we need to set an environment variable `DATABRICKS_SECRET_TOKEN`.
This can be achieved by registering an alias and calling the `scripts/secret_token.py` file. Add the following to `venv/bin/activate`:

```
alias dbutils_token='export DATABRICKS_SECRET_TOKEN=$(python $VIRTUAL_ENV/../scripts/secret_token.py) && sed -e "s/DATABRICKS_SECRET_TOKEN=.*/DATABRICKS_SECRET_TOKEN=$DATABRICKS_SECRET_TOKEN/g" -i "" $VIRTUAL_ENV/../.env'
```

Now we can deactivate the virtual environment and re-activate it to setup the new environment variables:

```
deactivate
source venv/bin/activate
```
