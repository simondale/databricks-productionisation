from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import monotonically_increasing_id


class FeatureDataProvider:
    def __init__(self, spark: SparkSession, dbutils):
        self.spark = spark
        self.dbutils = dbutils

    def get_training_dataframe(self) -> DataFrame:
        return self.spark.table("iris").withColumn(
            "id", monotonically_increasing_id()
        )

    def save_dataframe(self, data: DataFrame, target: str):
        data.write.format("delta").mode("overwrite").saveAsTable(target)


class FeatureStore:
    def __init__(self, feature_provider: FeatureDataProvider):
        self.feature_provider = feature_provider
        self.feature_data = feature_provider.get_training_dataframe().cache()

    def create_training_features(self):
        df = self.feature_data.select(
            "id", "sepal_length", "sepal_width", "petal_length", "petal_width"
        )
        self.feature_provider.save_dataframe(df, "iris_data")

    def create_training_target(self):
        df = self.feature_data.select(
            "id", "species"
        )
        self.feature_provider.save_dataframe(df, "iris_target")
