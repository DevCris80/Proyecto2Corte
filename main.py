from contextlib import asynccontextmanager
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel

from app.core.database import engine
from app.routes.pages import router as pages_router
from app.routes.proveedores_routes import router as proveedor_router
from app.routes.productos_routes import router as productos_router
from app.routes.ventas_routes import router as ventas_router
from app.routes.optimizacion_routes import router as optimizacion_router
from app.routes.dashboard_routes import router as dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    await engine.dispose()



app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pages_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(proveedor_router)
app.include_router(productos_router)
app.include_router(ventas_router)
app.include_router(optimizacion_router)
app.include_router(dashboard_router)
