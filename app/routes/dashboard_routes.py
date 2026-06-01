from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repository import producto_repo, proveedor_repo, venta_repo

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/resumen", status_code=200)
async def obtener_resumen_dashboard(
    session: AsyncSession = Depends(get_session),
):
    try:
        total_proveedores = await proveedor_repo.contar_activos(session)
        total_productos = await producto_repo.contar_activos(session)
        total_ventas = await venta_repo.contar(session)
        ventas_por_mes = await venta_repo.listar_ventas_por_mes(session)
        distribucion_stock = await producto_repo.contar_distribucion_stock(session)

        return {
            "total_proveedores": total_proveedores,
            "total_productos": total_productos,
            "total_ventas": total_ventas,
            "ventas_por_mes": ventas_por_mes,
            "distribucion_stock": distribucion_stock,
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al generar dashboard: {str(error)}")
