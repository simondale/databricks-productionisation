from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import spark_partition_id
from pyspark.sql.functions import lit  # pylint: disable=no-name-in-module
from pyspark.sql.types import StructField, StructType, DoubleType, StringType
from sklearn import tree

import mlflow
import mlflow.sklearn
import logging


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
        self.training_data = training_data
        self.model_name = "iris"

    def train_model(self):
        logger = logging.getLogger(__name__)
        logger.info("training model")

        mlflow.set_tracking_uri("databricks")
        mlflow.set_experiment(f"/Experiments/{self.model_name}")
        with mlflow.start_run():

            schema = StructType(
                [
                    StructField("sepal_length", DoubleType(), True),
                    StructField("sepal_width", DoubleType(), True),
                    StructField("petal_length", DoubleType(), True),
                    StructField("petal_width", DoubleType(), True),
                    StructField("species", StringType(), True),
                    StructField("model_name", StringType(), True),
                    StructField("model_version", StringType(), True),
                ]
            )

            data = self.training_data.load_data()
            target = self.training_data.load_target()
            iris_data = (
                data.join(target, data.id == target.id, "inner")
                .select(
                    "sepal_length",
                    "sepal_width",
                    "petal_length",
                    "petal_width",
                    "species",
                )
                .groupBy([spark_partition_id(), lit(self.model_name)])
                .applyInPandas(self._train_model, schema)
            )

            iris_data.show()

        logger.info("training complete")

    @staticmethod
    def _train_model(key, data):
        _, model_name = key
        mlflow.set_experiment(f"/Experiments/{model_name}")
        with mlflow.start_run(nested=True) as run:
            iris_data = data.loc[
                :,
                ["sepal_length", "sepal_width", "petal_length", "petal_width"],
            ]
            iris_target = data.loc[:, ["species"]]

            sk_model = tree.DecisionTreeClassifier()
            sk_model = sk_model.fit(iris_data, iris_target)

            mlflow.log_param("criterion", sk_model.criterion)
            mlflow.log_param("splitter", sk_model.splitter)

            # log model
            artifact_path = "model"

            mlflow.sklearn.log_model(
                sk_model, artifact_path=artifact_path,
            )
            model_version = mlflow.register_model(
                f"runs:/{run.info.run_id}/{artifact_path}", model_name
            )
            mlflow.sklearn.save_model(
                sk_model,
                run.info.run_id,
                serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE,
            )

            data["model_name"] = model_name
            data["model_version"] = model_version.version

            return data
