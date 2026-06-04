from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.templates import templates
from app.routes.optimizacion_routes import obtener_alertas_pedidos
from app.routes.dashboard_routes import obtener_resumen_dashboard

router = APIRouter(tags=["pages"])


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@router.get("/dashboard")
async def dashboard(request: Request, session: AsyncSession = Depends(get_session)):
    resumen = await obtener_resumen_dashboard(session=session)
    alertas = await obtener_alertas_pedidos(session=session)
    return templates.TemplateResponse(request, "dashboard.html", {
        "total_proveedores": resumen["total_proveedores"],
        "total_productos": resumen["total_productos"],
        "total_ventas": resumen["total_ventas"],
        "distribucion_stock": resumen["distribucion_stock"],
        "ventas_por_mes": resumen["ventas_por_mes"],
        "alertas": alertas,
    })


@router.get("/optimizacion")
async def optimizacion(request: Request, session: AsyncSession = Depends(get_session)):
    alertas = await obtener_alertas_pedidos(session=session)
    criticas = [a for a in alertas if a.estado_alerta in ("Urgente", "Pedir ahora")]
    normales = [a for a in alertas if a.estado_alerta not in ("Urgente", "Pedir ahora")]
    return templates.TemplateResponse(request, "optimizacion.html", {
        "alertas_criticas": criticas,
        "alertas_normales": normales,
    })
