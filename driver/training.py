from iris_model.training import TrainingPipeline, TrainingDataProvider
from iris_model.log_analytics import LogAnalytics
from pyspark.sql import SparkSession
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
import os


def main():
    spark = SparkSession.builder.getOrCreate()
    training_data = TrainingDataProvider(spark, None)
    training = TrainingPipeline(training_data)
    training.train_model()


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.addHandler(
        AzureLogHandler(
            connection_string=os.environ["APPINSIGHTS_INSTRUMENTATION_KEY"]
        )
    )

    log_analytics = LogAnalytics()
    log_analytics.init(
        os.environ["LOGANALYTICS_ID"],
        os.environ["LOGANALYTICS_KEY"],
        "IrisModel",
        "Training",
    )
    log_analytics.log("INFO", "Starting execution")

    try:
        logger.info("calling main")
        main()
        logger.info("main completed")
        log_analytics.log("INFO", "Completed successfully")
    except Exception as e:
        message = f"Error caught: {e}"
        log_analytics.log("ERROR", message)
        print(message)
