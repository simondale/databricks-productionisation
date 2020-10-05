from pyspark.sql import SparkSession, DataFrame
import seaborn as sns


class DataProvider:
    def __init__(self, spark: SparkSession, dbutils):
        self.spark = spark
        self.dbutils = dbutils

    def load_data(self, source: str) -> DataFrame:
        pass  # pragma: no cover

    def save_data(self, data_frame: DataFrame, target: str):
        pass  # pragma: no cover


class DeltaDataProvider(DataProvider):  # pragma: no cover
    def load_data(self, source: str) -> DataFrame:
        pdf = sns.load_dataset("iris")
        return self.spark.createDataFrame(pdf)

    def save_data(self, data_frame: DataFrame, target: str):
        data_frame.write.format("delta").mode("overwrite").saveAsTable("iris")


class Pipeline:
    def __init__(self, data: DataProvider):
        self.data = data

    def load_data(self):
        df = self.data.load_data("iris")
        self.data.save_data(df, "iris")
