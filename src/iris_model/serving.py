from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StringType

import mlflow.sklearn
import pandas as pd


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

        def prediction(
            sepal_length: pd.Series,
            sepal_width: pd.Series,
            petal_length: pd.Series,
            petal_width: pd.Series,
        ) -> pd.Series:
            model = mlflow.sklearn.load_model("models:/iris/None")
            pdf = pd.DataFrame(
                {
                    "sepal_length": sepal_length,
                    "sepal_width": sepal_width,
                    "petal_length": petal_length,
                    "petal_width": petal_width,
                }
            )
            pdf["prediction"] = model.predict(pdf)
            return pdf["prediction"]

        predict_species = pandas_udf(prediction, StringType())
        df = df.withColumn(
            "prediction",
            predict_species(  # pylint: disable=too-many-function-args, redundant-keyword-arg
                "sepal_length", "sepal_width", "petal_length", "petal_width"
            ),
        )

        self.serving_data.save_data(df, "iris_results")
