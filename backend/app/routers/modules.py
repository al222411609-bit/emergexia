"""Doctores, Ambulancias, Emergencias y Operadores: mismo patrón, tablas distintas."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..schemas import AmbulanceIn, DoctorIn, EmergencyIn, OperatorIn
from ..security import current_username
from ..tables import insert_row, list_rows, next_id


def build_router(path: str, table: str, model: type[BaseModel], before_insert=None) -> APIRouter:
    router = APIRouter(prefix=f"/api/{path}", tags=[path], dependencies=[Depends(current_username)])

    @router.get("")
    def list_items():
        rows = list_rows(table)
        return {"total": len(rows), "items": rows}

    @router.post("", status_code=201)
    def create_item(body: model):  # type: ignore[valid-type]
        data = body.model_dump()
        if before_insert:
            data = before_insert(data)
        return insert_row(table, data)

    return router


def _emergency_defaults(data: dict) -> dict:
    data["folio"] = f"EMG-{next_id('emergencies'):04d}"
    data["creado"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return data


routers = [
    build_router("doctores", "doctors", DoctorIn),
    build_router("ambulancias", "ambulances", AmbulanceIn),
    build_router("emergencias", "emergencies", EmergencyIn, _emergency_defaults),
    build_router("operadores", "operators", OperatorIn),
]
