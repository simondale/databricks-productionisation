from iris_model.training import TrainingPipeline, TrainingDataProvider
from pyspark.sql import SparkSession


def main():
    spark = SparkSession.builder.getOrCreate()
    training_data = TrainingDataProvider(spark, None)
    training = TrainingPipeline(training_data)
    training.train_model()


if __name__ == "__main__":
    main()
