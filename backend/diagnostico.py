"""Diagnóstico del backend de Emergexia.

Uso (dentro de la carpeta backend, con el entorno virtual activado):
    python diagnostico.py            # revisa todo, incluida una prueba real de Spark
    python diagnostico.py --rapido   # omite la prueba de Spark
"""
import importlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import urllib.request

PORT = int(os.getenv("PORT", "8000"))
OK, BAD, WARN = "  [OK]  ", "  [X]   ", "  [!]   "
problems = 0


def say(mark, text, hint=None):
    global problems
    print(mark + text)
    if hint:
        print("         → " + hint)
    if mark == BAD:
        problems += 1


print("\nDiagnóstico de Emergexia\n" + "=" * 26)

# 1. Python
v = sys.version_info
if v >= (3, 10):
    say(OK, f"Python {v.major}.{v.minor}.{v.micro}")
else:
    say(BAD, f"Python {v.major}.{v.minor} es muy antiguo", "Instala Python 3.10 o superior")

# 2. Paquetes
missing = []
for mod, pip_name in [("fastapi", "fastapi"), ("uvicorn", "uvicorn"), ("pyspark", "pyspark"),
                      ("jwt", "PyJWT"), ("dotenv", "python-dotenv"), ("pydantic", "pydantic")]:
    try:
        importlib.import_module(mod)
    except Exception:  # noqa: BLE001
        missing.append(pip_name)
if missing:
    say(BAD, "Faltan paquetes de Python: " + ", ".join(missing),
        "Activa el entorno virtual y ejecuta: pip install -r requirements.txt")
else:
    say(OK, "Paquetes de Python instalados")

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
    major = int(m.group(1)) if m else 0
    if major == 1 and m and m.group(2):
        major = int(m.group(2))
    if major in (8, 11, 17, 21):
        say(OK, f"Java encontrado: {text}")
    elif major > 21:
        say(WARN, f"Java {major} es demasiado nuevo para Spark 3.5: {text}",
            "Instala Java 17 o 21 y apunta JAVA_HOME a esa versión")
    else:
        say(WARN, f"Versión de Java poco habitual: {text}", "Spark 3.5 funciona con Java 8, 11, 17 y 21")

# 4. Puerto y estado del backend
s = socket.socket()
s.settimeout(1)
listening = s.connect_ex(("127.0.0.1", PORT)) == 0
s.close()
if listening:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/health", timeout=5) as r:
            h = json.load(r)
        say(OK, f"El backend responde en el puerto {PORT}")
        if h.get("spark_ready"):
            say(OK, "Spark está conectado")
        else:
            say(BAD, "Spark NO está conectado: " + str(h.get("spark_error")),
                "El login funciona igual; el detalle también aparece en Configuración")
    except Exception:  # noqa: BLE001
        say(BAD, f"Algo usa el puerto {PORT}, pero no es el backend de Emergexia",
            f"Ciérralo, o arranca el backend en otro puerto y define VITE_API_TARGET=http://127.0.0.1:OTRO_PUERTO")
else:
    b = socket.socket()
    try:
        b.bind(("127.0.0.1", PORT))
        say(BAD, f"El backend NO está corriendo (nadie escucha en el puerto {PORT})",
            f"Ejecuta en esta carpeta: uvicorn app.main:app --reload --port {PORT}   y deja esa terminal abierta")
    except OSError as exc:
        say(BAD, f"El puerto {PORT} no se puede usar ({exc})",
            "Arranca con otro puerto (--port 8001) y en frontend define VITE_API_TARGET=http://127.0.0.1:8001")
    finally:
        b.close()

# 5. Prueba real de Spark
if "--rapido" in sys.argv or missing or not java:
    print("\n(Prueba de Spark omitida)")
else:
    print("\nProbando Spark (puede tardar ~20 s)…")
    try:
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.master("local[1]").appName("diagnostico").config("spark.ui.enabled", "false").getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")
        say(OK, f"Spark {spark.version} arrancó")
        tmp = tempfile.mkdtemp()
        spark.createDataFrame([(1, "a")], ["id", "v"]).write.mode("overwrite").parquet(os.path.join(tmp, "t"))
        n = spark.read.parquet(os.path.join(tmp, "t")).count()
        say(OK, f"Spark pudo escribir y leer datos ({n} fila)")
        spark.stop()
    except Exception as exc:  # noqa: BLE001
        first = next((ln for ln in str(exc).splitlines() if ln.strip()), type(exc).__name__)[:300]
        hint = None
        if "HADOOP_HOME" in str(exc) or "winutils" in str(exc).lower() or "NativeIO" in str(exc):
            hint = "Windows necesita winutils.exe/hadoop.dll (define HADOOP_HOME) o usa WSL2 / Docker"
        elif "JAVA" in str(exc).upper():
            hint = "Revisa la instalación de Java y JAVA_HOME"
        say(BAD, "Spark falló: " + first, hint)

print("\n" + ("Todo en orden." if problems == 0 else f"Se encontraron {problems} problema(s). Corrige el primero y vuelve a ejecutar."))
sys.exit(1 if problems else 0)
