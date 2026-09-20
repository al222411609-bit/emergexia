import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import readiness
from .config import settings
from .routers import auth, modules, system
from .spark import stop_spark

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        readiness.ensure_ready()   # conecta con Spark y crea tablas de ejemplo
    except Exception:              # noqa: BLE001
        pass                       # la API arranca igual; el error se ve en /api/health y en el login
    yield
    stop_spark()


app = FastAPI(title="Emergexia API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

needs_spark = [Depends(readiness.require_spark)]
app.include_router(auth.router)   # el login no depende de Spark
app.include_router(system.router, dependencies=needs_spark)
for r in modules.routers:
    app.include_router(r, dependencies=needs_spark)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "Emergexia", "spark_ready": readiness.is_ready(), "spark_error": readiness.last_error}
