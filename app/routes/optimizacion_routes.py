from fastapi import APIRouter, HTTPException

from app.models.orden_sugerida import EstadoAlerta, OrdenSugerida
from app.models.producto import ProductoRespuesta
from app.models.proveedor import ProveedorRespuesta
from app.models.venta_historica import VentaRespuesta
from app.core.config import RUTA_ARCHIVO_PRODUCTOS, RUTA_ARCHIVO_PROVEEDOR, RUTA_ARCHIVO_VENTAS
from app.logic.math import calcular_optimizacion
from app.repository.csv_orm import listar_csv


router = APIRouter(prefix="/optimizar", tags=["motor matematico"])

@router.get("/pedidos", response_model=list[OrdenSugerida], status_code=200)
def obtener_alertas_pedidos():
    productos = [p for p in listar_csv(ProductoRespuesta, RUTA_ARCHIVO_PRODUCTOS) if p.estado_activo]
    proveedores = {p.id: p for p in listar_csv(ProveedorRespuesta, RUTA_ARCHIVO_PROVEEDOR) if p.estado_activo}
    todas_las_ventas = list(listar_csv(VentaRespuesta, RUTA_ARCHIVO_VENTAS))

    alertas_necesarias = []

    for producto in productos:
        proveedor = proveedores.get(producto.id_proveedor)
        
        if not proveedor:
            continue

        ventas_producto = [v for v in todas_las_ventas if v.id_producto == producto.id]

        resultado = calcular_optimizacion(producto, proveedor, ventas_producto)

        if resultado.estado_alerta != EstadoAlerta.OPTIMO:
            alertas_necesarias.append(resultado)

    return alertas_necesarias

@router.get("/{id_producto}", response_model=OrdenSugerida, status_code=200)
def obtener_sugerencia_pedido(id_producto: str):
    productos = list(listar_csv(ProductoRespuesta, RUTA_ARCHIVO_PRODUCTOS))
    producto = next((p for p in productos if p.id == id_producto and p.estado_activo), None)
    
    if not producto:
        raise HTTPException(status_code=404, detail=f"El producto {id_producto} no existe o esta inactivo.")

    proveedores = list(listar_csv(ProveedorRespuesta, RUTA_ARCHIVO_PROVEEDOR))
    proveedor = next((p for p in proveedores if p.id == producto.id_proveedor and p.estado_activo), None)

    if not proveedor:
        raise HTTPException(
            status_code=409, 
            detail="Conflicto de integridad: El proveedor asociado a este producto no existe."
        )

    todas_las_ventas = list(listar_csv(VentaRespuesta, RUTA_ARCHIVO_VENTAS))
    ventas_producto = [v for v in todas_las_ventas if v.id_producto == id_producto]

    try:
        orden_calculada = calcular_optimizacion(
            producto=producto, 
            proveedor=proveedor, 
            historico_ventas=ventas_producto
        )
        return orden_calculada

    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Error matematico: El costo de almacenamiento no puede ser cero.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno en el motor de calculo: {str(e)}")


