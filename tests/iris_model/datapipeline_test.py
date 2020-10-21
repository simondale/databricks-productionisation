from iris_model.datapipeline import DataProvider, Pipeline
from pyspark.sql import SparkSession, DataFrame
import seaborn as sns
import pytest


class TestDataProvider(DataProvider):
    def load_data(self, source: str) -> DataFrame:
        self.source = self.spark.createDataFrame(
            sns.load_dataset("iris").iloc[:1, :]
        ).cache()
        return self.source

    def save_data(self, data_frame: DataFrame, target: str):
        self.target = data_frame


@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder.getOrCreate()
    return spark


def test_pipeline(spark):
    # arrange
    data_provider = TestDataProvider(spark, None)
    pipeline = Pipeline(data_provider)

    # act
    pipeline.load_data()

    # assert
    source_records = data_provider.source.collect()
    target_records = data_provider.target.collect()
    assert len(source_records) == len(target_records)
