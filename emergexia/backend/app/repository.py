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


# Campos que jamás deben salir en un GET (contraseñas/PIN, aunque estén hasheados).
_HIDDEN_FIELDS = {"pin_hash", "password_hash"}


# ───────────────────────── módulos de datos ─────────────────────────
def list_rows(name: str) -> list[dict]:
    hide = {"_id": 0, **{f: 0 for f in _HIDDEN_FIELDS}}
    return list(get_db()[name].find({}, hide).sort("id", 1))


def insert_row(name: str, data: dict) -> dict:
    row_id = _next_id(name)
    doc = {"id": row_id, **data, "created_at": _now()}
    if name == "emergencies":
        doc["folio"] = f"EMG-{row_id:04d}"
        doc.setdefault("despacho", None)
    if name in ("doctors", "operators") and "nombres" in doc:
        # 'nombre' completo se guarda ya calculado: así las tablas, los <select> de Emergencias
        # y el resumen no necesitan volver a unir nombres + apellidos.
        doc["nombre"] = f"{doc['nombres'].strip()} {doc['apellidos'].strip()}".strip()
        doc["correo"] = doc["correo"].strip().lower()
    if name == "operators":
        # El PIN nunca se guarda en texto plano; si viene vacío no se crea acceso individual.
        pin = doc.pop("pin_acceso", None)
        doc["pin_hash"] = hash_password(pin) if pin else None
    db = get_db()
    db[name].insert_one(dict(doc))   # copia: pymongo agrega _id al dict que recibe
    log.info("Guardado en MongoDB %s.%s (id=%s)", db.name, name, row_id)
    doc.pop("pin_hash", None)
    return doc


def source_name(name: str) -> str:
    """'base.colección', para mostrar dónde viven los datos."""
    return f"{get_db().name}.{name}"


def find_row(name: str, row_id: int) -> dict | None:
    return get_db()[name].find_one({"id": row_id}, {"_id": 0, **{f: 0 for f in _HIDDEN_FIELDS}})


def find_operator_by_name(nombre: str) -> dict | None:
    """Usado por la verificación facial: trae la foto registrada del operador elegido."""
    return get_db()["operators"].find_one({"nombre": nombre}, {"_id": 0, **{f: 0 for f in _HIDDEN_FIELDS}})


def set_despacho(row_id: int, despacho: dict, nuevo_estado: str) -> dict | None:
    """Guarda la confirmación de salida (verificación facial) de una emergencia y actualiza su estado."""
    db = get_db()
    updated = db["emergencies"].find_one_and_update(
        {"id": row_id},
        {"$set": {"despacho": despacho, "estado": nuevo_estado}},
        projection={"_id": 0},
        return_document=ReturnDocument.AFTER,
    )
    return updated


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
            {"nombres": "Laura", "apellidos": "Méndez Ibarra", "celular": "5512345601", "correo": "laura.mendez@emergexia.mx", "especialidad": "Medicina de urgencias", "estado": "Activo"},
            {"nombres": "Carlos", "apellidos": "Ortega Vidal", "celular": "5512345602", "correo": "carlos.ortega@emergexia.mx", "especialidad": "Cardiología", "estado": "Activo"},
            {"nombres": "Sofía", "apellidos": "Ramírez Castro", "celular": "5512345603", "correo": "sofia.ramirez@emergexia.mx", "especialidad": "Traumatología", "estado": "En guardia"},
            {"nombres": "Andrés", "apellidos": "Villalobos Peña", "celular": "5512345604", "correo": "andres.villalobos@emergexia.mx", "especialidad": "Pediatría", "estado": "Descanso"},
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
            {"nombres": "Mariana", "apellidos": "Torres Gil", "celular": "5512345701", "correo": "mariana.torres@emergexia.mx", "turno": "Matutino", "extension": "201", "estado": "En línea"},
            {"nombres": "Ricardo", "apellidos": "Paredes Luna", "celular": "5512345702", "correo": "ricardo.paredes@emergexia.mx", "turno": "Vespertino", "extension": "202", "estado": "En línea"},
            {"nombres": "Daniela", "apellidos": "Ibarra Soto", "celular": "5512345703", "correo": "daniela.ibarra@emergexia.mx", "turno": "Nocturno", "extension": "203", "estado": "Desconectado"},
        ],
    }
    for name, rows in samples.items():
        if db[name].count_documents({}) == 0:
            for row in rows:
                insert_row(name, row)
