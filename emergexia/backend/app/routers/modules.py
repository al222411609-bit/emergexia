"""Doctores, Ambulancias, Emergencias y Operadores: mismo patrón, colecciones distintas (MongoDB)."""
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError, WriteError

from ..repository import find_operator_by_name, find_row, insert_row, list_rows, set_despacho, source_name
from ..schemas import AmbulanceIn, DespachoIn, DoctorIn, EmergencyIn, OperatorIn
from ..security import current_username


def _duplicate_field(exc: DuplicateKeyError) -> str:
    """Nombre del campo repetido: del keyPattern si el servidor lo da, si no del texto del error."""
    pattern = (exc.details or {}).get("keyPattern")
    if pattern:
        return next(iter(pattern))
    m = re.search(r"index:\s*(\w+?)_(?:uniq|idx|1)\b", str(exc))
    if m:
        return m.group(1)
    m = re.search(r"dup key:\s*\{\s*(\w+)", str(exc))
    return m.group(1) if m else "correo o la placa"


def build_router(path: str, collection: str, model: type[BaseModel]) -> APIRouter:
    router = APIRouter(prefix=f"/api/{path}", tags=[path], dependencies=[Depends(current_username)])

    @router.get("")
    def list_items():
        rows = list_rows(collection)
        return {"total": len(rows), "items": rows, "source": source_name(collection)}

    @router.post("", status_code=201)
    def create_item(body: model):  # type: ignore[valid-type]
        try:
            saved = insert_row(collection, body.model_dump())
            return {**saved, "saved_in": source_name(collection)}
        except DuplicateKeyError as exc:
            field = _duplicate_field(exc)
            raise HTTPException(409, f"Ya existe un registro con ese {field}." if field == "correo o la placa" else f"Ya existe un registro con ese valor de '{field}'.")
        except WriteError as exc:
            raise HTTPException(422, f"MongoDB rechazó el documento: {exc}")

    @router.get("/{item_id}")
    def get_item(item_id: int):
        """Un solo registro completo, para la ventana de 'ver perfil'."""
        row = find_row(collection, item_id)
        if not row:
            raise HTTPException(404, "No existe ese registro.")
        return {**row, "saved_in": source_name(collection)}

    return router


ESTADOS_QUE_REQUIEREN_SALIDA = {"En camino", "En sitio", "Trasladando"}

emergencias_router = build_router("emergencias", "emergencies", EmergencyIn)


@emergencias_router.patch("/{item_id}/despacho")
def despachar(item_id: int, body: DespachoIn):
    """Confirma la salida de la ambulancia: exige que el navegador ya haya verificado con
    face-api.js que la persona frente a la cámara es el paramédico elegido (body.verificado=true).
    Sin esa confirmación, la emergencia no puede pasar a 'En camino'."""
    emergencia = find_row("emergencies", item_id)
    if not emergencia:
        raise HTTPException(404, "No existe esa emergencia.")
    if not emergencia.get("ambulancia"):
        raise HTTPException(422, "Primero asigna una ambulancia a esta emergencia.")
    if body.operador not in (emergencia.get("paramedicos") or []):
        raise HTTPException(422, "Ese operador no está en la lista de paramédicos de esta emergencia.")
    if not body.verificado:
        raise HTTPException(
            403,
            "Verificación facial fallida o no realizada: la cara frente a la cámara no coincide "
            "con la foto registrada del paramédico. La ambulancia no puede salir.",
        )
    operador_doc = find_operator_by_name(body.operador)
    if not operador_doc or not operador_doc.get("foto"):
        raise HTTPException(422, "Ese operador no tiene una fotografía registrada; no se puede verificar.")

    despacho = {
        "operador": body.operador,
        "verificado": True,
        "distancia": body.distancia,
        "verificado_en": (body.verificado_en or datetime.now(timezone.utc)).isoformat(),
    }
    updated = set_despacho(item_id, despacho, "En camino")
    return {**updated, "saved_in": source_name("emergencies")}


routers = [
    build_router("doctores", "doctors", DoctorIn),
    build_router("ambulancias", "ambulances", AmbulanceIn),
    emergencias_router,
    build_router("operadores", "operators", OperatorIn),
]