"""Conexión a MongoDB (base de datos principal de Emergexia)."""
import re
import threading

from pymongo import MongoClient
from pymongo.errors import ConfigurationError, OperationFailure, PyMongoError, ServerSelectionTimeoutError

from .config import settings

_lock = threading.Lock()
_client: MongoClient | None = None


def safe_uri() -> str:
    """La URI sin la contraseña, para mostrarla en mensajes."""
    return re.sub(r"//([^:@/]+):[^@]+@", r"//\1:***@", settings.mongo_uri)


def get_client() -> MongoClient:
    global _client
    with _lock:
        if _client is None:
            _client = MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=settings.mongo_timeout_ms)
        return _client


def get_db():
    return get_client()[settings.mongo_db]


def close_client() -> None:
    global _client
    with _lock:
        if _client is not None:
            _client.close()
            _client = None


def _is_atlas() -> bool:
    return settings.mongo_uri.startswith("mongodb+srv://") or "mongodb.net" in settings.mongo_uri


def connect() -> None:
    """Comprueba la conexión. Lanza RuntimeError con un mensaje en español y accionable."""
    try:
        get_client().admin.command("ping")
    except ServerSelectionTimeoutError:
        close_client()
        if _is_atlas():
            raise RuntimeError(
                f"No se pudo conectar a Atlas ({safe_uri()}). Lo más común: tu IP no está permitida. "
                "En Atlas entra a Network Access → Add IP Address → 'Add current IP address' "
                "(o 0.0.0.0/0 solo para pruebas). También revisa tu internet o VPN."
            )
        raise RuntimeError(
            f"No se pudo conectar a MongoDB en {safe_uri()}. "
            "Verifica que MongoDB esté encendido y que MONGO_URI en backend/.env sea correcta."
        )
    except OperationFailure as exc:
        close_client()
        raise RuntimeError(
            f"MongoDB rechazó las credenciales ({exc.details.get('errmsg', exc) if exc.details else exc}). "
            "Revisa usuario y contraseña en MONGO_URI (en Atlas: Database Access)."
        )
    except ConfigurationError as exc:
        close_client()
        raise RuntimeError(
            f"No se pudo resolver o interpretar MONGO_URI ({exc}). Revisa que esté bien copiada, "
            "tu conexión a internet/VPN y que la contraseña no tenga símbolos sin codificar."
        )
    except PyMongoError as exc:
        close_client()
        raise RuntimeError(f"Problema de conexión con MongoDB: {exc}")


def mongo_info() -> dict:
    client = get_client()
    db = get_db()
    return {
        "connected": True,
        "uri": safe_uri(),
        "database": settings.mongo_db,
        "version": client.server_info().get("version"),
        "collections": {name: db[name].count_documents({}) for name in sorted(db.list_collection_names()) if name != "counters"},
    }
