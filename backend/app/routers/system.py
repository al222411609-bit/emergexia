from fastapi import APIRouter, Depends

from ..analytics import count_by_state
from ..mongo import mongo_info
from ..readiness import require_mongo, require_spark
from ..security import current_username
from ..spark import spark_info

router = APIRouter(prefix="/api", tags=["system"], dependencies=[Depends(current_username)])


@router.get("/mongo/status", dependencies=[Depends(require_mongo)])
def mongo_status():
    return mongo_info()


@router.get("/spark/status", dependencies=[Depends(require_spark)])
def spark_status():
    return spark_info()


@router.get("/dashboard/summary", dependencies=[Depends(require_mongo), Depends(require_spark)])
def summary():
    """Conteos por estado: los datos vienen de MongoDB y Spark los agrega (groupBy)."""
    return count_by_state()
