"""Diagnóstico del backend de Emergexia.

Uso (dentro de la carpeta backend, con el entorno virtual activado):
    python diagnostico.py            # revisa todo, incluida una prueba real de Spark
    python diagnostico.py --rapido   # omite la prueba de Spark

Si algo falla, el detalle completo queda en diagnostico.log (mándalo si necesitas ayuda).
"""
import importlib
import importlib.metadata as md
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import traceback
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
LOG = os.path.join(HERE, "diagnostico.log")
PORT = int(os.getenv("PORT", "8000"))
TESTED_PYSPARK = "4.0.1"
OK, BAD, WARN = "  [OK]  ", "  [X]   ", "  [!]   "
problems = 0
log_lines: list[str] = []


def say(mark, text, hint=None):
    global problems
    print(mark + text)
    log_lines.append(mark + text)
    if hint:
        print("         → " + hint)
        log_lines.append("         → " + hint)
    if mark == BAD:
        problems += 1


def parse_netstat(text: str, port: int) -> list[str]:
    """PIDs de sockets en escucha en `port`. No depende del idioma de Windows (LISTENING/ESCUCHANDO)."""
    pids = set()
    for ln in text.splitlines():
        parts = ln.split()
        if len(parts) >= 5 and parts[0].upper() == "TCP" and parts[1].endswith(f":{port}") and parts[2] in ("0.0.0.0:0", "[::]:0", "*:*"):
            pids.add(parts[-1])
    return sorted(pids)


def pids_on_port(port: int) -> list[str]:
    """PID(s) que escuchan en el puerto (Windows: netstat; Mac/Linux: lsof)."""
    try:
        if os.name == "nt":
            return parse_netstat(subprocess.run(["netstat", "-ano", "-p", "tcp"], capture_output=True, text=True).stdout, port)
        out = subprocess.run(["lsof", "-ti", f"tcp:{port}", "-sTCP:LISTEN"], capture_output=True, text=True).stdout
        return sorted(set(out.split()))
    except Exception:  # noqa: BLE001
        return []


print("\nDiagnóstico de Emergexia\n" + "=" * 26)

# 1. Python
v = sys.version_info
if v >= (3, 10):
    say(OK, f"Python {v.major}.{v.minor}.{v.micro}  ({sys.platform})")
else:
    say(BAD, f"Python {v.major}.{v.minor} es muy antiguo", "Instala Python 3.10 o superior")

# 1b. WSL (Windows Subsystem for Linux)
try:
    if "microsoft" in open("/proc/version").read().lower():
        say(WARN, "Estás dentro de WSL",
            "El frontend y el backend deben correr AMBOS dentro de WSL (o ambos en Windows), no mezclados. "
            "Un backend viejo en Windows puede quedarse con el puerto 8000")
except OSError:
    pass

# 2. Paquetes
missing = []
for mod, pip_name in [("fastapi", "fastapi"), ("uvicorn", "uvicorn"), ("pyspark", "pyspark"),
                      ("jwt", "PyJWT"), ("dotenv", "python-dotenv"), ("pydantic", "pydantic"), ("pymongo", "pymongo")]:
    try:
        importlib.import_module(mod)
    except Exception:  # noqa: BLE001
        missing.append(pip_name)
if missing:
    say(BAD, "Faltan paquetes de Python: " + ", ".join(missing),
        "Activa el entorno virtual y ejecuta: pip install -r requirements.txt")
else:
    say(OK, "Paquetes de Python instalados")

# 2b. Versión de PySpark
pyspark_ver = None
try:
    pyspark_ver = md.version("pyspark")
except Exception:  # noqa: BLE001
    pass
if pyspark_ver:
    major = int(pyspark_ver.split(".")[0])
    if pyspark_ver == TESTED_PYSPARK:
        say(OK, f"PySpark {pyspark_ver}")
    elif major < 4 and v >= (3, 13):
        say(BAD, f"PySpark {pyspark_ver} no es compatible con Python {v.major}.{v.minor}",
            "Ejecuta: pip install -r requirements.txt   (instala PySpark 4.0.1)")
    else:
        say(WARN, f"Tienes PySpark {pyspark_ver}; el proyecto está probado con {TESTED_PYSPARK}",
            "Ejecuta: pip install -r requirements.txt   para igualar la versión probada")

# 3. Java
java = shutil.which("java")
if not java and os.getenv("JAVA_HOME"):
    cand = os.path.join(os.environ["JAVA_HOME"], "bin", "java")
    java = cand if os.path.exists(cand) or os.path.exists(cand + ".exe") else None
if not java:
    say(BAD, "No se encontró Java", "Instala Java 17 (Temurin, adoptium.net), cierra y abre la terminal, y revisa con: java -version")
else:
    out = subprocess.run([java, "-version"], capture_output=True, text=True)
    text = (out.stderr or out.stdout).strip().splitlines()[0]
    m = re.search(r'"(\d+)(?:\.(\d+))?', text)
    jmajor = int(m.group(1)) if m else 0
    if jmajor == 1 and m and m.group(2):
        jmajor = int(m.group(2))
    need17 = bool(pyspark_ver and int(pyspark_ver.split(".")[0]) >= 4)
    if need17 and jmajor < 17:
        say(BAD, f"Spark 4 necesita Java 17 o superior y tienes: {text}", "Instala Java 17 o 21 y apunta JAVA_HOME a esa versión")
    elif jmajor in (17, 21):
        say(OK, f"Java encontrado: {text}")
    elif jmajor > 21:
        say(WARN, f"Java {jmajor} puede ser demasiado nuevo: {text}", "Usa Java 17 o 21")
    else:
        say(WARN, f"Versión de Java poco habitual: {text}", "Usa Java 17 o 21")

# 4. Puerto y estado del backend
s = socket.socket()
s.settimeout(1)
listening = s.connect_ex(("127.0.0.1", PORT)) == 0
s.close()
if listening:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/health", timeout=5) as r:
            h = json.load(r)
        pids = pids_on_port(PORT)
        kill = (f"taskkill /PID {' /PID '.join(pids)} /F" if os.name == "nt" else f"kill {' '.join(pids)}") if pids else None
        if "mongo_ready" not in h:
            say(BAD, f"Lo que responde en el puerto {PORT} es una versión ANTIGUA del backend (sin MongoDB)",
                "Ciérrala y vuelve a iniciar el backend nuevo" + (f".  Proceso(s): {', '.join(pids)}  →  {kill}" if pids else ""))
        else:
            say(OK, f"El backend responde en el puerto {PORT} (versión {h.get('version')}, base '{h.get('database')}')")
            if len(pids) > 1:
                say(WARN, f"Hay varios procesos escuchando en el puerto {PORT}: {', '.join(pids)}",
                    "Si algo se comporta raro, ciérralos todos y arranca uno solo")
        if "mongo_ready" not in h:
            pass
        elif h.get("mongo_ready"):
            say(OK, "El backend está conectado a MongoDB")
        else:
            say(BAD, "El backend NO está conectado a MongoDB: " + str(h.get("mongo_error")),
                "Revisa MONGO_URI en backend/.env (y Network Access en Atlas)")
    except Exception:  # noqa: BLE001
        say(BAD, f"Algo usa el puerto {PORT}, pero no es el backend de Emergexia",
            "Ciérralo, o arranca el backend en otro puerto y define VITE_API_TARGET=http://127.0.0.1:OTRO_PUERTO")
else:
    b = socket.socket()
    try:
        b.bind(("127.0.0.1", PORT))
        say(BAD, f"El backend NO está corriendo (nadie escucha en el puerto {PORT})",
            f"Ábrelo en OTRA terminal: uvicorn app.main:app --reload --port {PORT}   y déjala abierta")
    except OSError as exc:
        say(BAD, f"El puerto {PORT} no se puede usar ({exc})",
            "Arranca con otro puerto (--port 8001) y en frontend define VITE_API_TARGET=http://127.0.0.1:8001")
    finally:
        b.close()

# 4b. MongoDB
if "pymongo" in missing:
    print("\n(Prueba de MongoDB omitida: falta pymongo)")
else:
    print("\nProbando MongoDB…")
    try:
        from app import mongo

        mongo.connect()
        info = mongo.mongo_info()
        say(OK, f"MongoDB {info['version']} conectado en {info['uri']}")
        say(OK, f"Base de datos de la app: '{info['database']}'" + (" (aún sin colecciones: se crean al arrancar el backend)" if not info["collections"] else f" → {info['collections']}"))
        mongo.close_client()
    except Exception as exc:  # noqa: BLE001
        say(BAD, str(exc), "Abre MongoDB Compass: si conecta ahí, copia su cadena de conexión a MONGO_URI en backend/.env")

# 5. Prueba real de Spark (con la misma configuración que usa la API)
if "--rapido" in sys.argv or missing or not java:
    print("\n(Prueba de Spark omitida)")
else:
    print("\nProbando Spark (opcional: solo se usa para análisis/resumen; puede tardar ~20 s)…")
    try:
        from app.spark import get_spark, stop_spark

        spark = get_spark()
        say(OK, f"Spark {spark.version} arrancó (master: {spark.sparkContext.master})")
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "t")
        spark.createDataFrame([(1, "a")], ["id", "v"]).write.mode("overwrite").parquet(path)
        n = spark.read.parquet(path).count()
        say(OK, f"Spark pudo escribir y leer datos ({n} fila)")
        stop_spark()
    except Exception as exc:  # noqa: BLE001
        full = "".join(traceback.format_exception(exc))
        lines = [ln.strip() for ln in str(exc).splitlines() if ln.strip()]
        causes = [ln for ln in lines if ln.startswith("Caused by") or re.match(r"^[\w.$]+(Exception|Error)\b", ln)]
        shown = (causes[-3:] or lines[:3])
        say(WARN, "Spark no arrancó (la app funciona sin él; solo afecta al resumen y a Configuración). Causa:")
        for ln in shown:
            print("          " + ln[:220])
        low = full.lower()
        hint = None
        if "hadoop_home" in low or "winutils" in low or "nativeio" in low:
            hint = "Windows necesita winutils.exe/hadoop.dll (define HADOOP_HOME), o usa WSL2 / Docker"
        elif "bind" in low or "address" in low:
            hint = "Problema de red local: prueba desconectar la VPN o define SPARK_DRIVER_HOST=127.0.0.1 en .env"
        elif "java" in low and ("not found" in low or "gateway" in low):
            hint = "Revisa la instalación de Java y JAVA_HOME"
        if hint:
            print("         → " + hint)
        log_lines.append(full)
        print(f"\n  Detalle completo guardado en: {LOG}")

with open(LOG, "w", encoding="utf-8") as fh:
    fh.write("\n".join(log_lines))

print("\n" + ("Todo lo esencial está en orden." if problems == 0 else f"Se encontraron {problems} problema(s). Corrige el primero y vuelve a ejecutar."))
sys.exit(1 if problems else 0)
