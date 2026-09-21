"""Prueba real de guardado en MongoDB (sin abrir el sitio web).

Uso (en la carpeta backend, con el entorno virtual activado):
    python probar_guardado.py

Se conecta con el MONGO_URI de .env, guarda una ambulancia de prueba, la lee de vuelta
y la borra. Sirve para saber si el problema está en la base o en otra parte.
"""
import sys
import time

from app import dbschema, mongo, repository
from app.config import settings

OK, BAD = "  [OK]  ", "  [X]   "


def main() -> int:
    print(f"\nBase de datos configurada: '{settings.mongo_db}'  ({mongo.safe_uri()})\n")
    try:
        mongo.connect()
        dbschema.ensure_schema()
    except RuntimeError as exc:
        print(BAD + str(exc))
        return 1
    db = mongo.get_db()
    print(OK + f"Conectado. Colecciones en '{db.name}': {sorted(db.list_collection_names())}")

    placa = f"PRUEBA-{int(time.time()) % 100000}"
    try:
        saved = repository.insert_row("ambulances", {"placa": placa, "tipo": "Básica", "conductor": "Prueba", "estado": "Disponible"})
        print(OK + f"Guardado en {repository.source_name('ambulances')} con id {saved['id']} (placa {placa})")
    except Exception as exc:  # noqa: BLE001
        print(BAD + f"MongoDB NO permitió guardar: {type(exc).__name__}: {exc}")
        print("         → Copia este mensaje completo y mándamelo.")
        return 1

    found = [r for r in repository.list_rows("ambulances") if r["placa"] == placa]
    print((OK if found else BAD) + ("Se pudo leer de vuelta la ambulancia guardada" if found else "Se guardó pero NO se pudo leer de vuelta"))

    db["ambulances"].delete_one({"placa": placa})
    print(OK + "Registro de prueba borrado (no queda basura en tu base)")

    print("\nDocumentos por colección ahora mismo:")
    for name in sorted(db.list_collection_names()):
        print(f"    {name:<12} {db[name].count_documents({})}")
    print("\nSi esto sale bien, la base funciona: revisa que solo haya UN backend corriendo (python diagnostico.py).")
    return 0 if found else 1


if __name__ == "__main__":
    sys.exit(main())
