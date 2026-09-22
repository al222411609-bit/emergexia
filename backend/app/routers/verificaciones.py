"""Bitácora de verificaciones por reconocimiento facial de operadores.

La comparación de rostros ocurre en el navegador (ver frontend/src/lib/faceVerify.js);
este endpoint solo guarda un registro de auditoría de cada verificación exitosa:
quién fue verificado, en qué momento del flujo (asignación a una emergencia o
salida de la ambulancia) y con qué distancia facial.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from ..mongo import get_db
from ..schemas import VerificacionIn
from ..security import current_username

router = APIRouter(prefix="/api/verificaciones", tags=["verificaciones"], dependencies=[Depends(current_username)])


@router.post("", status_code=201)
def registrar_verificacion(body: VerificacionIn, usuario: str = Depends(current_username)):
    doc = {
        **body.model_dump(),
        "verificado_por": usuario,
        "momento": datetime.now(timezone.utc),
    }
    get_db()["verificaciones"].insert_one(dict(doc))
    return {"ok": True}


@router.get("")
def listar_verificaciones(operador: str | None = None, limit: int = 50):
    query = {"operador": operador} if operador else {}
    rows = list(
        get_db()["verificaciones"]
        .find(query, {"_id": 0})
        .sort("momento", -1)
        .limit(max(1, min(limit, 200)))
    )
    return {"total": len(rows), "items": rows}
