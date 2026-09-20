from fastapi import APIRouter, Depends, HTTPException

from ..security import current_username
from ..spark import spark_info
from ..tables import count_by

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/spark/status")
def spark_status(_: str = Depends(current_username)):
    try:
        return spark_info()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(503, f"No se pudo conectar con Spark: {exc}")


@router.get("/dashboard/summary")
def summary(_: str = Depends(current_username)):
    """Conteos agregados con Spark (groupBy) para el panel de inicio."""
    return {
        "doctores": count_by("doctors", "estado"),
        "ambulancias": count_by("ambulances", "estado"),
        "emergencias": count_by("emergencies", "estado"),
        "operadores": count_by("operators", "estado"),
    }
