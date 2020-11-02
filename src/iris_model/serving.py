from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import spark_partition_id
from pyspark.sql.functions import lit  # pylint: disable=no-name-in-module
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    TimestampType,
)

import mlflow.sklearn
import pandas as pd
import json
import datetime


class ServingDataProvider:
    def __init__(self, spark: SparkSession, dbutils):
        self.spark = spark
        self.dbutils = dbutils

    def load_data(self) -> DataFrame:
        return self.spark.table("iris_data")

    def save_data(self, data: DataFrame, target: str):
        data.write.format("delta").option("mergeSchema", True).mode(
            "append"
        ).saveAsTable(target)


class ServingPipeline:
    def __init__(self, serving_data: ServingDataProvider):
        self.serving_data = serving_data

    def make_predictions(self):
        df = self.serving_data.load_data()
        df = df.select(
            "sepal_length", "sepal_width", "petal_length", "petal_width"
        )

        schema = StructType.fromJson(json.loads(df.schema.json()))
        schema.add(StructField("prediction", StringType(), True))
        schema.add(StructField("model_name", StringType(), True))
        schema.add(StructField("model_version", StringType(), True))
        schema.add(StructField("serving_datetime", TimestampType(), True))

        df = df.groupBy(
            spark_partition_id(), lit("iris"), lit("None")
        ).applyInPandas(self, schema)

        self.serving_data.save_data(df, "iris_results")

    def __call__(self, key: tuple, pdf: pd.DataFrame) -> pd.DataFrame:
        return self._predict_species(key, pdf)

    def _predict_species(self, key: tuple, pdf: pd.DataFrame) -> pd.DataFrame:
        _, model_name, model_version = key
        model = mlflow.sklearn.load_model(
            f"models:/{model_name}/{model_version}"
        )
        pdf["prediction"] = model.predict(pdf)
        pdf["model_name"] = model_name
        pdf["model_version"] = model_version
        pdf["serving_datetime"] = datetime.datetime.utcnow()
        return pdf
