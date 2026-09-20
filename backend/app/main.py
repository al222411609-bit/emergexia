import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import readiness
from .config import settings
from .routers import auth, modules, system
from .spark import stop_spark

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("emergexia")


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


@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception):
    """Cualquier error no previsto se registra completo y se devuelve con su causa,
    en vez de un 500 sin explicación."""
    log.error("Error no controlado en %s %s\n%s", request.method, request.url.path,
              "".join(traceback.format_exception(exc)))
    return JSONResponse(
        status_code=500,
        content={"detail": f"Error interno del servidor: {type(exc).__name__}: {exc}"},
    )


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "Emergexia", "spark_ready": readiness.is_ready(), "spark_error": readiness.last_error}
