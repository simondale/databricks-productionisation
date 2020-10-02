from iris_model.features import FeatureStore, FeatureDataProvider
from pyspark.sql import SparkSession


def main():
    spark = SparkSession.builder.getOrCreate()
    feature_provider = FeatureDataProvider(spark, None)
    feature_store = FeatureStore(feature_provider)
    feature_store.create_training_features()
    feature_store.create_training_target()


if __name__ == "__main__":
    main()
