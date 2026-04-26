from fastapi import APIRouter, HTTPException

from app.models.venta_historica import VentaCrear, VentaRespuesta
from app.repository.csv_orm import guardar_csv, listar_csv
from app.models.producto import ProductoRespuesta
from app.core.config import RUTA_ARCHIVO_PRODUCTOS, RUTA_ARCHIVO_VENTAS


router = APIRouter(prefix="/ventas", tags=["ventas"])

@router.post("/", response_model=VentaRespuesta, status_code=201)
def registrar_venta(venta_in: VentaCrear):
    productos = list(listar_csv(ProductoRespuesta, RUTA_ARCHIVO_PRODUCTOS))
    if not any(p.id == venta_in.id_producto and p.estado_activo for p in productos):
        raise HTTPException(status_code=404, detail="Producto no encontrado o inactivo")

    nueva_venta = VentaRespuesta(**venta_in.model_dump())

    guardar_csv(nueva_venta, RUTA_ARCHIVO_VENTAS)
    
    return nueva_venta