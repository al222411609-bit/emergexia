"""Conexión a Apache Spark (una sola SparkSession compartida por la API)."""
import threading

from pyspark.sql import SparkSession

from .config import settings

_lock = threading.Lock()
_spark: SparkSession | None = None


def get_spark() -> SparkSession:
    global _spark
    with _lock:
        if _spark is None:
            builder = (
                SparkSession.builder.appName(settings.spark_app_name)
                .master(settings.spark_master)
                .config("spark.sql.shuffle.partitions", settings.spark_shuffle_partitions)
                .config("spark.ui.enabled", str(settings.spark_ui_enabled).lower())
                .config("spark.driver.memory", settings.spark_driver_memory)
                .config("spark.sql.session.timeZone", "UTC")
            )
            if settings.spark_driver_host:
                builder = builder.config("spark.driver.host", settings.spark_driver_host)
            _spark = builder.getOrCreate()
            _spark.sparkContext.setLogLevel("WARN")
        return _spark


def stop_spark() -> None:
    global _spark
    with _lock:
        if _spark is not None:
            _spark.stop()
            _spark = None


def spark_info() -> dict:
    spark = get_spark()
    sc = spark.sparkContext
    return {
        "connected": True,
        "app_name": sc.appName,
        "app_id": sc.applicationId,
        "master": sc.master,
        "version": spark.version,
        "data_dir": settings.data_dir,
    }
