from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import expr
from pyspark.sql.types import StructType, StructField, StringType

import mlflow.sklearn
import pandas as pd
import json


class ServingDataProvider:
    def __init__(self, spark: SparkSession, dbutils):
        self.spark = spark
        self.dbutils = dbutils

    def load_data(self) -> DataFrame:
        return self.spark.table("iris_data")

    def save_data(self, data: DataFrame, target: str):
        data.write.format("delta").mode("overwrite").saveAsTable(target)


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

        df = df.groupBy(
            expr("monotonically_increasing_id() % 1000")
        ).applyInPandas(self._predict_species, schema)

        self.serving_data.save_data(df, "iris_results")

    @staticmethod
    def _predict_species(pdf: pd.DataFrame) -> pd.DataFrame:
        model = mlflow.sklearn.load_model("models:/iris/None")
        pdf["prediction"] = model.predict(pdf)
        return pdf
