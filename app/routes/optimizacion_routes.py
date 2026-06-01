from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.orden_sugerida import EstadoAlerta, OrdenSugerida
from app.repository import producto_repo, proveedor_repo, venta_repo
from app.logic.math import calcular_optimizacion

router = APIRouter(prefix="/optimizar", tags=["motor matematico"])


@router.get("/pedidos", response_model=list[OrdenSugerida], status_code=200)
async def obtener_alertas_pedidos(
    session: AsyncSession = Depends(get_session),
):
    productos = await producto_repo.listar_activos(session)
    proveedores = {
        p.id: p
        for p in await proveedor_repo.listar_activos(session)
    }
    todas_las_ventas = await venta_repo.listar(session)

    alertas = []
    for producto in productos:
        proveedor = proveedores.get(producto.id_proveedor)
        if not proveedor:
            continue

        ventas_producto = [v for v in todas_las_ventas if v.id_producto == producto.id]
        resultado = calcular_optimizacion(producto, proveedor, ventas_producto)

        if resultado.estado_alerta != EstadoAlerta.OPTIMO:
            alertas.append(resultado)

    return alertas


@router.get("/{id_producto}", response_model=OrdenSugerida, status_code=200)
async def obtener_sugerencia_pedido(
    id_producto: str,
    session: AsyncSession = Depends(get_session),
):
    producto = await producto_repo.obtener_por_id(session, id_producto)
    if not producto or not producto.estado_activo:
        raise HTTPException(
            status_code=404,
            detail=f"El producto {id_producto} no existe o esta inactivo.",
        )

    proveedor = await proveedor_repo.obtener_por_id(
        session, producto.id_proveedor
    )
    if not proveedor or not proveedor.estado_activo:
        raise HTTPException(
            status_code=409,
            detail="Conflicto de integridad: El proveedor asociado a este producto no existe.",
        )

    todas_las_ventas = await venta_repo.listar(session)
    ventas_producto = [v for v in todas_las_ventas if v.id_producto == id_producto]

    try:
        return calcular_optimizacion(producto, proveedor, ventas_producto)
    except ZeroDivisionError:
        raise HTTPException(
            status_code=400,
            detail="Error matematico: El costo de almacenamiento no puede ser cero.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en el motor de calculo: {str(e)}",
        )
