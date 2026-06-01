from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.venta import VentaCreate, VentaPublic
from app.repository import venta_repo, producto_repo

router = APIRouter(prefix="/ventas", tags=["ventas"])


@router.post("", response_model=VentaPublic, status_code=201)
async def registrar_venta(
    venta_in: VentaCreate,
    session: AsyncSession = Depends(get_session),
):
    producto = await producto_repo.obtener_por_id(session, venta_in.id_producto)
    if not producto or not producto.estado_activo:
        raise HTTPException(
            status_code=404, detail="El producto no existe o esta inactivo."
        )

    if producto.stock_actual < venta_in.cantidad:
        raise HTTPException(
            status_code=400,
            detail=f"No puedes vender {venta_in.cantidad}, solo hay {producto.stock_actual} disponibles.",
        )

    venta = await venta_repo.crear_con_descuento_stock(session, venta_in)
    if not venta:
        raise HTTPException(
            status_code=500,
            detail="Error al registrar la venta con descuento de stock.",
        )

    return venta


@router.get("", response_model=list[VentaPublic], status_code=200)
async def listar_ventas(
    session: AsyncSession = Depends(get_session),
):
    try:
        return await venta_repo.listar(session)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(error)}")
