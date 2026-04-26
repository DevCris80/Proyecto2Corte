import uuid

from fastapi import APIRouter, HTTPException

from app.models.venta_historica import VentaCrear, VentaRespuesta
from app.repository.csv_orm import actualizar_csv, guardar_csv, listar_csv
from app.models.producto import ProductoActualizar, ProductoRespuesta
from app.core.config import RUTA_ARCHIVO_PRODUCTOS, RUTA_ARCHIVO_VENTAS


router = APIRouter(prefix="/ventas", tags=["ventas"])

@router.post("/", response_model=VentaRespuesta, status_code=201)
def registrar_venta(venta_in: VentaCrear):
    productos = list(listar_csv(ProductoRespuesta, RUTA_ARCHIVO_PRODUCTOS))
    producto = next((p for p in productos if p.id == venta_in.id_producto and p.estado_activo), None)

    if not producto:
        raise HTTPException(status_code=404, detail="El producto no existe o está inactivo.")

    if producto.stock_actual < venta_in.cantidad:
        raise HTTPException(
            status_code=400, 
            detail=f"No puedes vender {venta_in.cantidad}, solo hay {producto.stock_actual} disponibles."
        )

    nueva_venta = VentaRespuesta(id= str(uuid.uuid4()), **venta_in.model_dump())
    
    guardar_csv(nueva_venta, RUTA_ARCHIVO_VENTAS) 

    nuevo_stock = producto.stock_actual - venta_in.cantidad
    
    producto_actualizado = ProductoActualizar(stock_actual=nuevo_stock)

    exito_actualizacion = actualizar_csv(
        objeto_id=producto.id,
        campo_id="id",
        nuevos_datos=producto_actualizado,
        ruta_archivo=RUTA_ARCHIVO_PRODUCTOS
    )

    if not exito_actualizacion:
        raise HTTPException(
            status_code=500, 
            detail="Se guardo la venta pero fallo la deduccion de inventario en el archivo CSV."
        )

    return nueva_venta

@router.get("/", response_model=list[VentaRespuesta], status_code=200)
def listar_ventas():
    try:
        ventas = list(listar_csv(VentaRespuesta, RUTA_ARCHIVO_VENTAS))

        return ventas
    except IOError:
        raise HTTPException(status_code=500, detail="Error de lectura en el archivo CSV")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(error)}")