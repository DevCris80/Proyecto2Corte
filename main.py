import traceback as tb
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
from sqlmodel import SQLModel

from app.core.database import engine
from app.core.templates import templates
from app.routes.pages import router as pages_router
from app.routes.productos_pages import router as productos_pages_router
from app.routes.proveedores_pages import router as proveedores_pages_router
from app.routes.ventas_pages import router as ventas_pages_router
from app.routes.proveedores_routes import router as proveedor_router
from app.routes.productos_routes import router as productos_router
from app.routes.ventas_routes import router as ventas_router
from app.routes.optimizacion_routes import router as optimizacion_router
from app.routes.dashboard_routes import router as dashboard_router

"""
@contextmanager
def lifespan(app: FastAPI):
    # Creación de tablas síncrona
    SQLModel.metadata.create_all(engine)
    yield
    # Limpieza de conexiones al apagar
    engine.dispose()
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    await engine.dispose()



app = FastAPI(lifespan=lifespan)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    try:
        trace = "".join(tb.format_exception(type(exc), exc, exc.__traceback__))
        status = getattr(exc, "status_code", 500)
        return templates.TemplateResponse(request, "error.html", {
            "status_code": status,
            "detail": str(exc) or "Error interno del servidor",
            "traceback": trace,
        }, status_code=status)
    except Exception:
        return PlainTextResponse(
            f"Error interno del servidor: {exc}",
            status_code=500,
        )


app.include_router(pages_router)
app.include_router(productos_pages_router)
app.include_router(proveedores_pages_router)
app.include_router(ventas_pages_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(proveedor_router)
app.include_router(productos_router)
app.include_router(ventas_router)
app.include_router(optimizacion_router)
app.include_router(dashboard_router)
