"""Acceso a datos en MongoDB: usuarios, doctores, ambulancias, emergencias y operadores."""
import logging
from datetime import datetime, timezone

from pymongo import ReturnDocument

from .config import settings
from .mongo import get_db
from .security import hash_password

log = logging.getLogger("emergexia")


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ───────────────────────── ids autoincrementales ─────────────────────────
def _next_id(name: str) -> int:
    """Contador por colección (colección 'counters')."""
    doc = get_db()["counters"].find_one_and_update(
        {"_id": name}, {"$inc": {"seq": 1}}, upsert=True, return_document=ReturnDocument.AFTER
    )
    return doc["seq"]


# ───────────────────────── módulos de datos ─────────────────────────
def list_rows(name: str) -> list[dict]:
    return list(get_db()[name].find({}, {"_id": 0}).sort("id", 1))


def insert_row(name: str, data: dict) -> dict:
    row_id = _next_id(name)
    doc = {"id": row_id, **data, "created_at": _now()}
    if name == "emergencies":
        doc["folio"] = f"EMG-{row_id:04d}"
    db = get_db()
    db[name].insert_one(dict(doc))   # copia: pymongo agrega _id al dict que recibe
    log.info("Guardado en MongoDB %s.%s (id=%s)", db.name, name, row_id)
    return doc


def source_name(name: str) -> str:
    """'base.colección', para mostrar dónde viven los datos."""
    return f"{get_db().name}.{name}"


# ───────────────────────── usuarios ─────────────────────────
def find_user(username: str) -> dict | None:
    return get_db()["users"].find_one({"username": username.strip().lower()}, {"_id": 0})


def upsert_user(username: str, password: str, full_name: str | None = None, role: str = "Administrador") -> dict:
    """Crea el usuario, o si ya existe le cambia la contraseña (y nombre/rol si se indican)."""
    username = username.strip().lower()
    users = get_db()["users"]
    existing = users.find_one({"username": username})
    if existing:
        changes = {"password_hash": hash_password(password), "active": True}
        if full_name:
            changes["full_name"] = full_name
        if role:
            changes["role"] = role
        users.update_one({"username": username}, {"$set": changes})
        return {"username": username, "created": False}
    users.insert_one({
        "id": _next_id("users"),
        "username": username,
        "password_hash": hash_password(password),
        "full_name": full_name or username,
        "role": role,
        "active": True,
        "created_at": _now(),
    })
    return {"username": username, "created": True}


def seed_admin() -> None:
    """Crea el administrador inicial (desde .env) solo si aún no hay ningún usuario."""
    if get_db()["users"].count_documents({}) == 0:
        upsert_user(settings.admin_username, settings.admin_password, settings.admin_name, "Administrador")


# ───────────────────────── datos de ejemplo (opcional) ─────────────────────────
def seed_demo() -> None:
    """Rellena las colecciones vacías con datos de ejemplo (SEED_DEMO_DATA=true)."""
    db = get_db()
    samples = {
        "doctors": [
            {"nombres": "Laura", "apellidos": "Méndez", "nombre": "Laura Méndez", "especialidad": "Medicina de urgencias", "cedula_profesional": "8451203", "celular": "55 1234 5601", "turno": "Matutino", "estado": "Activo"},
            {"nombres": "Carlos", "apellidos": "Ortega", "nombre": "Carlos Ortega", "especialidad": "Cardiología", "cedula_profesional": "8451204", "celular": "55 1234 5602", "turno": "Vespertino", "estado": "Activo"},
            {"nombres": "Sofía", "apellidos": "Ramírez", "nombre": "Sofía Ramírez", "especialidad": "Traumatología", "cedula_profesional": "8451205", "celular": "55 1234 5603", "turno": "Nocturno", "estado": "En guardia"},
            {"nombres": "Andrés", "apellidos": "Villalobos", "nombre": "Andrés Villalobos", "especialidad": "Pediatría", "cedula_profesional": "8451206", "celular": "55 1234 5604", "turno": "Matutino", "estado": "Descanso"},
        ],
        "ambulances": [
            {"placa": "AMB-101", "tipo": "Avanzada", "conductor": "Jorge Salinas", "estado": "Disponible"},
            {"placa": "AMB-102", "tipo": "Básica", "conductor": "Marcos Herrera", "estado": "En servicio"},
            {"placa": "AMB-103", "tipo": "Avanzada", "conductor": "Elena Cruz", "estado": "Disponible"},
            {"placa": "AMB-104", "tipo": "Básica", "conductor": "Pablo Núñez", "estado": "Mantenimiento"},
        ],
        "emergencies": [
            {"descripcion": "Accidente vehicular en Av. Reforma", "prioridad": "Alta", "estado": "En curso", "ambulancia": "AMB-102"},
            {"descripcion": "Dolor torácico, adulto mayor", "prioridad": "Alta", "estado": "Asignada", "ambulancia": "AMB-101"},
            {"descripcion": "Caída con posible fractura", "prioridad": "Media", "estado": "Pendiente", "ambulancia": None},
        ],
        "operators": [
            {"nombre": "Mariana Torres", "turno": "Matutino", "extension": "201", "estado": "En línea"},
            {"nombre": "Ricardo Paredes", "turno": "Vespertino", "extension": "202", "estado": "En línea"},
            {"nombre": "Daniela Ibarra", "turno": "Nocturno", "extension": "203", "estado": "Desconectado"},
        ],
    }
    for name, rows in samples.items():
        if db[name].count_documents({}) == 0:
            for row in rows:
                insert_row(name, row)
