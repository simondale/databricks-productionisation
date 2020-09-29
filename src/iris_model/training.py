from pyspark.sql import SparkSession, DataFrame
from sklearn import tree

import mlflow
import mlflow.sklearn
import seaborn as sns


class TrainingDataProvider:
    def __init__(self, spark: SparkSession, dbutils):
        self.spark = spark
        self.dbutils = dbutils

    def load_data(self) -> DataFrame:
        return self.spark.table("iris_data")

    def load_target(self) -> DataFrame:
        return self.spark.table("iris_target")


class TrainingPipeline:
    def __init__(self, training_data: TrainingDataProvider):
        self.model_name = "iris"
        self.format = mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE

    def train_model(self):
        mlflow.set_tracking_uri("databricks")
        mlflow.set_experiment(f"/Experiments/{self.model_name}")

        with mlflow.start_run() as run:
            iris_df = sns.load_dataset("iris")

            iris_data = iris_df.loc[
                :, ["sepal_length", "sepal_width", "petal_length", "petal_width"]
            ]
            iris_target = iris_df.loc[:, ["species"]]

            sk_model = tree.DecisionTreeClassifier()
            sk_model = sk_model.fit(iris_data, iris_target)

            mlflow.log_param("criterion", sk_model.criterion)
            mlflow.log_param("splitter", sk_model.splitter)

            # log model
            mlflow.sklearn.log_model(
                sk_model, registered_model_name=self.model_name, artifact_path="model"
            )
            mlflow.sklearn.save_model(
                sk_model, run.info.run_id, serialization_format=self.format
            )   

