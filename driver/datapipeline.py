from iris_model.datapipeline import DeltaDataProvider, Pipeline
from pyspark.sql import SparkSession


def main():
    spark = SparkSession.builder.getOrCreate()
    delta_provider = DeltaDataProvider(spark, None)
    pipeline = Pipeline(delta_provider)
    pipeline.load_data()


if __name__ == '__main__':
    main()
