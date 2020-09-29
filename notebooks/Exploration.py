# Databricks notebook source
import seaborn as sns
import pandas as pd

iris_df = sns.load_dataset('iris')

# COMMAND ----------

iris_df.head()

# COMMAND ----------

iris_df.describe()

# COMMAND ----------

sns.swarmplot(x='species', y='petal_length', data=iris_df)

# COMMAND ----------

sns.pairplot(iris_df, hue='species')

# COMMAND ----------

import mlflow
import mlflow.sklearn
from sklearn import tree

model_name = 'iris'

with mlflow.start_run() as run:
  iris_data = iris_df.loc[:, ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']]
  iris_target = iris_df.loc[:, ['species']]

  sk_model = tree.DecisionTreeClassifier()
  sk_model = sk_model.fit(iris_data, iris_target)
  
  mlflow.log_param('criterion', sk_model.criterion)
  mlflow.log_param('splitter', sk_model.splitter)
  
  # log model
  mlflow.sklearn.log_model(iris_df, registered_model_name=model_name, artifact_path='model')
  mlflow.sklearn.save_model(sk_model, run.info.run_id, serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE)

  # compare output
  runs_df = mlflow.search_runs(run.info.experiment_id)

# COMMAND ----------

runs_df



# COMMAND ----------

