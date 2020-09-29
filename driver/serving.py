from iris_model.serving import ServingPipeline, ServingDataProvider
from pyspark.sql import SparkSession


def main():
    spark = SparkSession.builder.getOrCreate()
    serving_data = ServingDataProvider(spark, None)
    serving = ServingPipeline(serving_data)
    serving.make_predictions()


if __name__ == '__main__':
    main()
