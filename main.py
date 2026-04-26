from fastapi import FastAPI

from app.routes.proveedores_routes import router as proveedor_router
from app.routes.productos_routes import router as productos_router
from app.routes.ventas_routes import router as ventas_router
from app.routes.optimizacion_routes import router as optimizacion_router

app = FastAPI()

app.include_router(router=proveedor_router)
app.include_router(router=productos_router)
app.include_router(router=ventas_router)
app.include_router(router=optimizacion_router)

@app.get("/")
async def raiz():
    return {"Saludo": "Hola profe"}