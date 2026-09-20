import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "si", "sí"}


class Settings:
    # Spark
    spark_master: str = os.getenv("SPARK_MASTER", "local[*]")
    spark_app_name: str = os.getenv("SPARK_APP_NAME", "Emergexia")
    spark_ui_enabled: bool = _bool(os.getenv("SPARK_UI_ENABLED", "false"))
    spark_shuffle_partitions: str = os.getenv("SPARK_SHUFFLE_PARTITIONS", "4")
    spark_driver_memory: str = os.getenv("SPARK_DRIVER_MEMORY", "1g")
    spark_driver_host: str | None = os.getenv("SPARK_DRIVER_HOST") or None

    # Datos
    data_dir: str = os.getenv("DATA_DIR", str(BASE_DIR / "data"))

    # Seguridad
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-cambiar")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")
    admin_name: str = os.getenv("ADMIN_NAME", "Yessica López")

    cors_origins: list[str] = [
        o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()
    ]


settings = Settings()
