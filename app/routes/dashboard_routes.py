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
        proveedores = await proveedor_repo.listar_activos(session)
        productos = await producto_repo.listar_activos(session)
        ventas = await venta_repo.listar(session)

        # Agrupación de ventas por mes
        ventas_por_mes_dict = {}
        for v in ventas:
            # v.fecha_venta is datetime, we need "YYYY-MM"
            # In Venta model, fecha_venta is datetime
            mes = v.fecha_venta.strftime("%Y-%m")
            ventas_por_mes_dict[mes] = ventas_por_mes_dict.get(mes, 0) + v.cantidad

        ventas_por_mes = [
            {"mes": k, "cantidad": v}
            for k, v in sorted(ventas_por_mes_dict.items())
        ]

        # Distribución de stock
        stock_bajo = 0
        stock_medio = 0
        stock_alto = 0

        for p in productos:
            if p.stock_actual < 10:
                stock_bajo += 1
            elif p.stock_actual <= 50:
                stock_medio += 1
            else:
                stock_alto += 1

        distribucion_stock = {
            "bajo": stock_bajo,
            "medio": stock_medio,
            "alto": stock_alto
        }

        return {
            "total_proveedores": len(proveedores),
            "total_productos": len(productos),
            "total_ventas": len(ventas),
            "ventas_por_mes": ventas_por_mes,
            "distribucion_stock": distribucion_stock
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error al generar dashboard: {str(error)}")
