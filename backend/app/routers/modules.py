"""Doctores, Ambulancias, Emergencias y Operadores: mismo patrón, colecciones distintas (MongoDB)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError, WriteError

from ..repository import insert_row, list_rows, source_name
from ..schemas import AmbulanceIn, DoctorIn, EmergencyIn, OperatorIn
from ..security import current_username


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
            field = next(iter((exc.details or {}).get("keyPattern", {"valor": 1})))
            raise HTTPException(409, f"Ya existe un registro con ese valor de '{field}'.")
        except WriteError as exc:
            raise HTTPException(422, f"MongoDB rechazó el documento: {exc}")

    return router


routers = [
    build_router("doctores", "doctors", DoctorIn),
    build_router("ambulancias", "ambulances", AmbulanceIn),
    build_router("emergencias", "emergencies", EmergencyIn),
    build_router("operadores", "operators", OperatorIn),
]
