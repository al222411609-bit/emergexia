# Emergexia

Sistema de Gestión Médica y de Emergencias. Interfaz de inicio de sesión y panel con módulos
(Doctores, Ambulancias, Emergencias, Operadores y Configuración), con un backend que **se conecta a Apache Spark**.

```
emergexia/
├── backend/            API en Python (FastAPI) + PySpark
│   └── app/
│       ├── spark.py        ← conexión a Spark (SparkSession)
│       ├── tables.py       ← tablas Parquet leídas/escritas con Spark + datos de ejemplo
│       ├── readiness.py    ← arranque seguro de Spark (no tumba la API si falla)
│       ├── security.py     ← contraseñas (PBKDF2) y tokens JWT
│       ├── routers/        ← auth, módulos, estado de Spark
│       └── main.py
├── frontend/           React + Vite (login, panel, módulos, configuración)
│   └── src/
│       ├── pages/          ← Login, Home, ModulePage, SettingsPage
│       ├── components/     ← Layout (menú lateral + barra superior), Logo
│       ├── lib/            ← api.js, auth.jsx, modules.js (define los módulos)
│       └── styles/app.css  ← colores y estilos (variables al inicio)
└── docker-compose.yml  (opcional)
```

## Requisitos

- Python 3.10+
- **Java 11, 17 o 21** (lo necesita Spark) → comprueba con `java -version`
- Node.js 18+

## Puesta en marcha

### 1. Backend (terminal 1)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

La primera vez Spark tarda unos segundos en arrancar y crea las tablas con datos de ejemplo en `backend/data/`.
Documentación interactiva de la API: <http://localhost:8000/docs>

### 2. Frontend (terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Abre <http://localhost:5173>

### Acceso inicial

| Usuario | Contraseña |
|---------|------------|
| `admin` | `admin123` |

Cámbialos en `backend/.env` (`ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_NAME`) y reinicia el backend.
Cambia también `JWT_SECRET`. El login **no depende de Spark**: puedes entrar aunque Spark falle.

## Conexión a Spark

Toda la configuración está en `backend/.env`:

| Variable | Para qué sirve |
|----------|----------------|
| `SPARK_MASTER` | `local[*]` (Spark embebido, por defecto) · `spark://host:7077` (clúster standalone) · `yarn` · `k8s://…` |
| `SPARK_APP_NAME` | Nombre de la aplicación en Spark (`Emergexia`) |
| `SPARK_UI_ENABLED` | `true` abre la UI de Spark en el puerto 4040 |
| `SPARK_DRIVER_HOST` | IP del backend si usas un clúster remoto |
| `DATA_DIR` | Dónde se guardan las tablas (Parquet). Acepta `hdfs://`, `s3a://`, etc. |

Cómo se usa Spark hoy:

- Cada tabla (`doctors`, `ambulances`, `emergencies`, `operators`) es una carpeta Parquet.
- Las listas y los conteos del resumen (`GET /api/dashboard/summary`) se calculan con DataFrames de Spark.
- En **Configuración** de la app hay un botón *Verificar* que muestra el estado real de la conexión
  (`GET /api/spark/status`: master, versión, ID de aplicación).

> Nota: cada alta añade un archivo Parquet pequeño. Es ideal para arrancar y para clústeres;
> más adelante podemos pasar a Delta Lake o a una base de datos con Spark por encima.

## Si el login no te deja entrar

Primero ejecuta el diagnóstico (en la carpeta `backend`, con el entorno virtual activado):

```bash
python diagnostico.py
```

Revisa Python, paquetes, Java, si el backend está corriendo y si Spark puede leer y escribir. Cada problema trae la solución.

| Mensaje en el login | Qué significa | Solución |
|---------------------|---------------|----------|
| `El backend no respondió (código 500)` | El backend no está corriendo o se cerró al arrancar | Arráncalo: `uvicorn app.main:app --reload --port 8000` y no cierres esa terminal |
| `Usuario o contraseña incorrectos` | Credenciales distintas a `.env` | Por defecto `admin` / `admin123` |

Si Spark falla (Java ausente, Windows sin `winutils`…), el login sigue funcionando y las pantallas de datos
muestran el motivo; también lo ves en <http://localhost:8000/api/health> (`spark_error`).

## Con Docker (opcional)

```bash
docker compose up --build
```

Web en <http://localhost:8080> y API en <http://localhost:8000/docs>.

## API principal

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/login` | Devuelve token JWT y datos del usuario |
| GET | `/api/auth/me` | Usuario de la sesión |
| GET / POST | `/api/doctores` · `/api/ambulancias` · `/api/emergencias` · `/api/operadores` | Listar / crear |
| GET | `/api/dashboard/summary` | Conteos por estado (Spark) |
| GET | `/api/spark/status` | Estado de la conexión a Spark |
| GET | `/api/health` | Estado de la API y de Spark (sin login) |

## Personalizar

- **Foto y animación del login**: `frontend/src/assets/ambulance.jpg` y `frontend/src/assets/heartbeat.json` (Lottie). Reemplaza los archivos con el mismo nombre para cambiarlos. La animación se pinta de blanco por código en `components/Heartbeat.jsx`; usa `<Heartbeat recolor={false} />` para ver sus colores originales.
- **Colores**: variables `--red-*` al inicio de `frontend/src/styles/app.css`.
- **Módulos, columnas y formularios**: `frontend/src/lib/modules.js`.
- **Campos/tablas nuevas**: `backend/app/tables.py` (esquemas) y `backend/app/schemas.py` (validación).
