"""Arranque perezoso y seguro de Spark: si falla, la API sigue viva y explica por qué."""
import logging
import threading

from fastapi import HTTPException

from .spark import get_spark
from .tables import seed_if_empty

log = logging.getLogger("emergexia")
_lock = threading.Lock()
_ready = False
last_error: str | None = None


def _short(exc: Exception) -> str:
    text = str(exc).strip() or type(exc).__name__
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), type(exc).__name__)
    return first[:300]


def is_ready() -> bool:
    return _ready


def ensure_ready() -> None:
    """Conecta con Spark y crea las tablas la primera vez. Reintenta si falló antes."""
    global _ready, last_error
    if _ready:
        return
    with _lock:
        if _ready:
            return
        try:
            get_spark()
            seed_if_empty()
            _ready = True
            last_error = None
        except Exception as exc:  # noqa: BLE001
            last_error = f"{type(exc).__name__}: {_short(exc)}"
            log.exception("No se pudo iniciar Spark / tablas")
            raise


def require_spark() -> None:
    """Dependencia de FastAPI: responde 503 con el motivo si Spark no está disponible."""
    try:
        ensure_ready()
    except Exception:  # noqa: BLE001
        raise HTTPException(503, f"Spark no está disponible. {last_error}")
