"""Doctores, Ambulancias, Emergencias y Operadores: mismo patrón, colecciones distintas (MongoDB)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from pymongo.errors import DuplicateKeyError, WriteError

from ..repository import insert_row, list_rows, source_name
from ..schemas import AmbulanceIn, DoctorIn, EmergencyIn, OperatorIn
from ..security import current_username


<<<<<<< HEAD
def build_router(path: str, collection: str, model: type[BaseModel], derive=None) -> APIRouter:
=======
def build_router(path: str, collection: str, model: type[BaseModel]) -> APIRouter:
>>>>>>> ecb314e0be1671f363a199180d1176f6feb81edb
    router = APIRouter(prefix=f"/api/{path}", tags=[path], dependencies=[Depends(current_username)])

    @router.get("")
    def list_items():
        rows = list_rows(collection)
        return {"total": len(rows), "items": rows, "source": source_name(collection)}

    @router.post("", status_code=201)
    def create_item(body: model):  # type: ignore[valid-type]
        try:
<<<<<<< HEAD
            data = body.model_dump()
            if derive:
                # p. ej. doctores: junta nombres + apellidos en un campo "nombre"
                # para poder mostrarlo/enlazarlo igual que en los demás módulos.
                data = {**data, **derive(data)}
            saved = insert_row(collection, data)
=======
            saved = insert_row(collection, body.model_dump())
>>>>>>> ecb314e0be1671f363a199180d1176f6feb81edb
            return {**saved, "saved_in": source_name(collection)}
        except DuplicateKeyError as exc:
            field = next(iter((exc.details or {}).get("keyPattern", {"valor": 1})))
            raise HTTPException(409, f"Ya existe un registro con ese valor de '{field}'.")
        except WriteError as exc:
            raise HTTPException(422, f"MongoDB rechazó el documento: {exc}")

    return router


routers = [
<<<<<<< HEAD
    build_router(
        "doctores", "doctors", DoctorIn,
        derive=lambda d: {"nombre": f"{d['nombres']} {d['apellidos']}".strip()},
    ),
=======
    build_router("doctores", "doctors", DoctorIn),
>>>>>>> ecb314e0be1671f363a199180d1176f6feb81edb
    build_router("ambulancias", "ambulances", AmbulanceIn),
    build_router("emergencias", "emergencies", EmergencyIn),
    build_router("operadores", "operators", OperatorIn),
]
