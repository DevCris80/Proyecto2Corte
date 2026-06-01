from fastapi import APIRouter, Depends, Form, Query, UploadFile, File, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.templates import templates
from app.repository import producto_repo, proveedor_repo, venta_repo
from app.models.producto import ProductoCreate, ProductoUpdate
from app.models.proveedor import ProveedorCreate
from app.models.venta import VentaCreate
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


@router.get("/productos")
async def productos(
    request: Request,
    page: int = Query(1, ge=1),
    session: AsyncSession = Depends(get_session),
):
    productos_list, total, current_page, total_pages = await producto_repo.listar_activos_paginado(session, page)
    proveedores_list = await proveedor_repo.listar_activos(session)
    proveedores_map = {p.id: p for p in proveedores_list}

    productos_rows = []
    for p in productos_list:
        prov = proveedores_map.get(p.id_proveedor)
        productos_rows.append({
            "id": p.id,
            "Nombre": p.nombre,
            "Proveedor": prov.nombre if prov else "—",
            "Stock": str(p.stock_actual),
            "Costo Unit.": f"${p.costo_unitario:.2f}",
            "Demanda Anual": str(int(p.demanda_anual_estimada)),
        })

    proveedor_options = [(p.id, p.nombre) for p in proveedores_list]

    return templates.TemplateResponse(request, "productos.html", {
        "productos_rows": productos_rows,
        "productos_headers": ["Nombre", "Proveedor", "Stock", "Costo Unit.", "Demanda Anual"],
        "proveedor_options": proveedor_options,
        "page": current_page,
        "total_pages": total_pages,
        "total": total,
    })


@router.post("/productos")
async def crear_producto(
    request: Request,
    session: AsyncSession = Depends(get_session),
    nombre: str = Form(...),
    id_proveedor: str = Form(...),
    stock_actual: int = Form(...),
    costo_unitario: float = Form(...),
    costo_almacenamiento_anual: float = Form(...),
    demanda_anual_estimada: float = Form(...),
    imagen: UploadFile = File(None),
):
    datos = ProductoCreate(
        nombre=nombre,
        id_proveedor=id_proveedor,
        stock_actual=stock_actual,
        costo_unitario=costo_unitario,
        costo_almacenamiento_anual=costo_almacenamiento_anual,
        demanda_anual_estimada=demanda_anual_estimada,
    )
    producto = await producto_repo.crear(session, datos)
    if imagen and imagen.filename:
        from app.core.storage import subir_imagen_supabase
        imagen_url = await subir_imagen_supabase(imagen, folder=f"public/productos/{producto.id}")
        await producto_repo.actualizar(session, producto.id, ProductoUpdate(imagen_url=imagen_url))
    return RedirectResponse(url="/productos", status_code=303)


@router.post("/productos/{id}/delete")
async def eliminar_producto(id: str, session: AsyncSession = Depends(get_session)):
    await producto_repo.eliminar(session, id)
    return RedirectResponse(url="/productos", status_code=303)


@router.get("/proveedores")
async def proveedores(
    request: Request,
    page: int = Query(1, ge=1),
    session: AsyncSession = Depends(get_session),
):
    proveedores_list, total, current_page, total_pages = await proveedor_repo.listar_activos_paginado(session, page)

    proveedores_rows = []
    for p in proveedores_list:
        proveedores_rows.append({
            "id": p.id,
            "Nombre": p.nombre,
            "Costo Pedido": f"${p.costo_pedido_fijo:.2f}",
            "Lead Time": f"{p.lead_time_promedio} días",
            "Nivel Servicio": f"{p.nivel_servicio_objetivo:.0%}",
        })

    return templates.TemplateResponse(request, "proveedores.html", {
        "proveedores_rows": proveedores_rows,
        "proveedores_headers": ["Nombre", "Costo Pedido", "Lead Time", "Nivel Servicio"],
        "page": current_page,
        "total_pages": total_pages,
        "total": total,
    })


@router.post("/proveedores")
async def crear_proveedor(
    request: Request,
    session: AsyncSession = Depends(get_session),
    nombre: str = Form(...),
    costo_pedido_fijo: float = Form(...),
    lead_time_promedio: float = Form(...),
    desviacion_estandar_lead_time: float = Form(0.0),
    nivel_servicio_objetivo: float = Form(0.95),
):
    datos = ProveedorCreate(
        nombre=nombre,
        costo_pedido_fijo=costo_pedido_fijo,
        lead_time_promedio=lead_time_promedio,
        desviacion_estandar_lead_time=desviacion_estandar_lead_time,
        nivel_servicio_objetivo=nivel_servicio_objetivo,
    )
    await proveedor_repo.crear(session, datos)
    return RedirectResponse(url="/proveedores", status_code=303)


@router.post("/proveedores/{id}/delete")
async def eliminar_proveedor(id: str, session: AsyncSession = Depends(get_session)):
    await proveedor_repo.eliminar(session, id)
    return RedirectResponse(url="/proveedores", status_code=303)


@router.get("/ventas")
async def ventas(
    request: Request,
    page: int = Query(1, ge=1),
    session: AsyncSession = Depends(get_session),
):
    ventas_list, total, current_page, total_pages = await venta_repo.listar_paginado(session, page)
    productos_list = await producto_repo.listar_activos(session)
    productos_map = {p.id: p for p in productos_list}

    ventas_rows = []
    for v in ventas_list:
        prod = productos_map.get(v.id_producto)
        ventas_rows.append({
            "id": v.id,
            "ID": v.id[:8],
            "Producto": prod.nombre if prod else "—",
            "Cantidad": str(v.cantidad),
            "Fecha": v.fecha_venta.isoformat(),
        })

    producto_options = [(p.id, p.nombre) for p in productos_list]

    return templates.TemplateResponse(request, "ventas.html", {
        "ventas_rows": ventas_rows,
        "ventas_headers": ["ID", "Producto", "Cantidad", "Fecha"],
        "producto_options": producto_options,
        "total_ventas_valor": total,
        "page": current_page,
        "total_pages": total_pages,
        "total": total,
    })


@router.post("/ventas")
async def crear_venta(
    request: Request,
    session: AsyncSession = Depends(get_session),
    id_producto: str = Form(...),
    cantidad: int = Form(...),
):
    datos = VentaCreate(id_producto=id_producto, cantidad=cantidad)
    await venta_repo.crear_con_descuento_stock(session, datos)
    return RedirectResponse(url="/ventas", status_code=303)


@router.get("/optimizacion")
async def optimizacion(request: Request, session: AsyncSession = Depends(get_session)):
    alertas = await obtener_alertas_pedidos(session=session)
    criticas = [a for a in alertas if a.estado_alerta in ("Urgente", "Pedir ahora")]
    normales = [a for a in alertas if a.estado_alerta not in ("Urgente", "Pedir ahora")]
    return templates.TemplateResponse(request, "optimizacion.html", {
        "alertas_criticas": criticas,
        "alertas_normales": normales,
    })
