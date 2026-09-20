"""Conexión a Apache Spark (una sola SparkSession compartida por la API).

La importación de pyspark es PEREZOSA a propósito: si pyspark o Java no están
disponibles, la API debe seguir arrancando y el login debe funcionar igual.
El motivo del fallo se ve en /api/health y en la pantalla de Configuración.
"""
from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any

from .config import settings

if TYPE_CHECKING:  # solo para el editor / type checker, no se ejecuta
    from pyspark.sql import SparkSession

_lock = threading.Lock()
_spark: Any = None


def get_spark() -> "SparkSession":
    global _spark
    with _lock:
        if _spark is None:
            try:
                from pyspark.sql import SparkSession
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(
                    "No se pudo importar pyspark. Instala las dependencias con "
                    "'pip install -r requirements.txt' y verifica Java 17 o 21."
                ) from exc

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
            try:
                _spark.stop()
            except Exception:  # noqa: BLE001
                pass
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
