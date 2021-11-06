from iris_model.serving import ServingPipeline, ServingDataProvider
from iris_model.log_analytics import LogAnalytics
from pyspark.sql import SparkSession
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
import os


def main():
    spark = SparkSession.builder.getOrCreate()
    serving_data = ServingDataProvider(spark, None)
    serving = ServingPipeline(serving_data)
    serving.make_predictions()

    spark.sql("SELECT * FROM `iris_results`").show()


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
        "Serving",
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
