import json
from fastapi import APIRouter, Depends, Form, Query, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import subir_imagen_supabase
from app.core.database import get_session
from app.core.templates import templates
from app.repository import producto_repo, proveedor_repo, venta_repo
from app.models.producto import ProductoCreate, ProductoUpdate
from app.models.proveedor import ProveedorCreate, ProveedorUpdate
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
    busqueda_nombre: str = Query(""),
    id_proveedor: str = Query(""),
    costo_min: str = Query(""),
    costo_max: str = Query(""),
    stock_min: str = Query(""),
    stock_max: str = Query(""),
    session: AsyncSession = Depends(get_session),
):
    costo_min_val = float(costo_min) if costo_min != "" else None
    costo_max_val = float(costo_max) if costo_max != "" else None
    stock_min_val = int(stock_min) if stock_min != "" else None
    stock_max_val = int(stock_max) if stock_max != "" else None

    productos_list, total, current_page, total_pages = await producto_repo.buscar_con_filtros_paginado(
        session,
        busqueda_nombre=busqueda_nombre,
        id_proveedor=id_proveedor,
        costo_min=costo_min_val,
        costo_max=costo_max_val,
        stock_min=stock_min_val,
        stock_max=stock_max_val,
        page=page,
    )
    proveedores_resumen = await proveedor_repo.listar_activos_resumen_cached()


    productos_rows = []
    for p, nombre_prov in productos_list:
        productos_rows.append({
            "id": p.id,
            "Nombre": p.nombre,
            "Proveedor": nombre_prov,
            "Stock": str(p.stock_actual),
            "Costo Unit.": f"${p.costo_unitario:,.2f}",
            "Demanda Anual": str(int(p.demanda_anual_estimada)),
            "detail_data": json.dumps({
                "titulo": p.nombre,
                "imagen_url": p.imagen_url or "",
                "campos": [
                    {"label": "Nombre", "valor": p.nombre},
                    {"label": "Proveedor", "valor": nombre_prov},
                    {"label": "Stock Actual", "valor": str(p.stock_actual)},
                    {"label": "Costo Unitario", "valor": f"${p.costo_unitario:,.2f}"},
                    {"label": "Costo Almac. Anual", "valor": f"${p.costo_almacenamiento_anual:,.2f}"},
                    {"label": "Demanda Anual Est.", "valor": str(int(p.demanda_anual_estimada))},
                ],
            }),
        })

    proveedor_options = proveedores_resumen

    filtros_activos = bool(id_proveedor or costo_min or costo_max or stock_min or stock_max)

    extra_params = {
        "busqueda_nombre": busqueda_nombre,
        "id_proveedor": id_proveedor,
        "costo_min": costo_min,
        "costo_max": costo_max,
        "stock_min": stock_min,
        "stock_max": stock_max,
    }

    return templates.TemplateResponse(request, "productos.html", {
        "productos_rows": productos_rows,
        "productos_headers": ["Nombre", "Proveedor", "Stock", "Costo Unit.", "Demanda Anual"],
        "proveedor_options": proveedor_options,
        "page": current_page,
        "total_pages": total_pages,
        "total": total,
        "busqueda_nombre": busqueda_nombre,
        "id_proveedor_filtro": id_proveedor,
        "costo_min_filtro": costo_min,
        "costo_max_filtro": costo_max,
        "stock_min_filtro": stock_min,
        "stock_max_filtro": stock_max,
        "filtros_activos": filtros_activos,
        "extra_params": extra_params,
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
    form = await request.form()
    imagen = form.get("imagen")
    if isinstance(imagen, UploadFile) and imagen.filename:
        imagen_url = await subir_imagen_supabase(imagen, folder=f"public/productos/{producto.id}")
        if imagen_url:
            await producto_repo.actualizar(session, producto.id, ProductoUpdate(imagen_url=imagen_url))
    return RedirectResponse(url="/productos", status_code=303)


@router.post("/productos/{id}/delete")
async def eliminar_producto(id: str, session: AsyncSession = Depends(get_session)):
    await producto_repo.eliminar(session, id)
    return RedirectResponse(url="/productos", status_code=303)


@router.get("/productos/{id}/editar")
async def editar_producto_form(
    request: Request,
    id: str,
    session: AsyncSession = Depends(get_session),
):
    producto = await producto_repo.obtener_por_id(session, id)
    if not producto:
        return RedirectResponse(url="/productos", status_code=303)
    proveedores_list = await proveedor_repo.listar_activos_cached()
    proveedor_options = [(p.id, p.nombre) for p in proveedores_list]
    return templates.TemplateResponse(request, "editar_producto.html", {
        "producto": producto,
        "proveedor_options": proveedor_options,
    })


@router.post("/productos/{id}/editar")
async def editar_producto(
    request: Request,
    id: str,
    session: AsyncSession = Depends(get_session),
    nombre: str = Form(...),
    id_proveedor: str = Form(...),
    stock_actual: int = Form(...),
    costo_unitario: float = Form(...),
    costo_almacenamiento_anual: float = Form(...),
    demanda_anual_estimada: float = Form(...),
):
    datos = ProductoUpdate(
        nombre=nombre,
        id_proveedor=id_proveedor,
        stock_actual=stock_actual,
        costo_unitario=costo_unitario,
        costo_almacenamiento_anual=costo_almacenamiento_anual,
        demanda_anual_estimada=demanda_anual_estimada,
    )
    await producto_repo.actualizar(session, id, datos)
    form = await request.form()
    imagen = form.get("imagen")
    if isinstance(imagen, UploadFile) and imagen.filename:
        imagen_url = await subir_imagen_supabase(imagen, folder=f"public/productos/{id}")
        if imagen_url:
            await producto_repo.actualizar(session, id, ProductoUpdate(imagen_url=imagen_url))
    return RedirectResponse(url="/productos", status_code=303)


@router.get("/proveedores")
async def proveedores(
    request: Request,
    page: int = Query(1, ge=1),
    busqueda_nombre: str = Query(""),
    lead_time_min: str = Query(""),
    lead_time_max: str = Query(""),
    costo_min: str = Query(""),
    costo_max: str = Query(""),
    nivel_servicio_min: str = Query(""),
    session: AsyncSession = Depends(get_session),
):
    lead_time_min_val = float(lead_time_min) if lead_time_min != "" else None
    lead_time_max_val = float(lead_time_max) if lead_time_max != "" else None
    costo_min_val = float(costo_min) if costo_min != "" else None
    costo_max_val = float(costo_max) if costo_max != "" else None
    nivel_servicio_min_val = float(nivel_servicio_min) if nivel_servicio_min != "" else None

    proveedores_list, total, current_page, total_pages = await proveedor_repo.buscar_con_filtros_paginado(
        session,
        busqueda_nombre=busqueda_nombre,
        lead_time_min=lead_time_min_val,
        lead_time_max=lead_time_max_val,
        costo_min=costo_min_val,
        costo_max=costo_max_val,
        nivel_servicio_min=nivel_servicio_min_val,
        page=page,
    )

    proveedores_rows = []
    for p in proveedores_list:
        proveedores_rows.append({
            "id": p.id,
            "Nombre": p.nombre,
            "Costo Pedido": f"${p.costo_pedido_fijo:,.2f}",
            "Lead Time": f"{p.lead_time_promedio} días",
            "Nivel Servicio": f"{p.nivel_servicio_objetivo:.0%}",
            "detail_data": json.dumps({
                "titulo": p.nombre,
                "imagen_url": p.imagen_url or "",
                "proveedor_id": p.id,
                "campos": [
                    {"label": "Nombre", "valor": p.nombre},
                    {"label": "Costo Pedido Fijo", "valor": f"${p.costo_pedido_fijo:,.2f}"},
                    {"label": "Lead Time Promedio", "valor": f"{p.lead_time_promedio} días"},
                    {"label": "Desv. Est. Lead Time", "valor": f"{p.desviacion_estandar_lead_time:.2f} días"},
                    {"label": "Nivel Servicio Objetivo", "valor": f"{p.nivel_servicio_objetivo:.0%}"},
                ],
            }),
        })

    filtros_activos = bool(
        lead_time_min or lead_time_max
        or costo_min or costo_max
        or nivel_servicio_min
    )

    extra_params = {
        "busqueda_nombre": busqueda_nombre,
        "lead_time_min": lead_time_min,
        "lead_time_max": lead_time_max,
        "costo_min": costo_min,
        "costo_max": costo_max,
        "nivel_servicio_min": nivel_servicio_min,
    }

    return templates.TemplateResponse(request, "proveedores.html", {
        "proveedores_rows": proveedores_rows,
        "proveedores_headers": ["Nombre", "Costo Pedido", "Lead Time", "Nivel Servicio"],
        "page": current_page,
        "total_pages": total_pages,
        "total": total,
        "busqueda_nombre": busqueda_nombre,
        "lead_time_min_filtro": lead_time_min,
        "lead_time_max_filtro": lead_time_max,
        "costo_min_filtro": costo_min,
        "costo_max_filtro": costo_max,
        "nivel_servicio_min_filtro": nivel_servicio_min,
        "filtros_activos": filtros_activos,
        "extra_params": extra_params,
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
    proveedor = await proveedor_repo.crear(session, datos)
    form = await request.form()
    imagen = form.get("imagen")
    if isinstance(imagen, UploadFile) and imagen.filename:
        imagen_url = await subir_imagen_supabase(imagen, folder=f"public/proveedores/{proveedor.id}")
        if imagen_url:
            await proveedor_repo.actualizar(session, proveedor.id, ProveedorUpdate(imagen_url=imagen_url))
    return RedirectResponse(url="/proveedores", status_code=303)


@router.post("/proveedores/{id}/delete")
async def eliminar_proveedor(id: str, session: AsyncSession = Depends(get_session)):
    await proveedor_repo.eliminar(session, id)
    return RedirectResponse(url="/proveedores", status_code=303)


@router.get("/proveedores/{id}/editar")
async def editar_proveedor_form(
    request: Request,
    id: str,
    session: AsyncSession = Depends(get_session),
):
    proveedor = await proveedor_repo.obtener_por_id(session, id)
    if not proveedor:
        return RedirectResponse(url="/proveedores", status_code=303)
    return templates.TemplateResponse(request, "editar_proveedor.html", {
        "proveedor": proveedor,
    })


@router.post("/proveedores/{id}/editar")
async def editar_proveedor(
    request: Request,
    id: str,
    session: AsyncSession = Depends(get_session),
    nombre: str = Form(...),
    costo_pedido_fijo: float = Form(...),
    lead_time_promedio: float = Form(...),
    desviacion_estandar_lead_time: float = Form(0.0),
    nivel_servicio_objetivo: float = Form(0.95),
):
    datos = ProveedorUpdate(
        nombre=nombre,
        costo_pedido_fijo=costo_pedido_fijo,
        lead_time_promedio=lead_time_promedio,
        desviacion_estandar_lead_time=desviacion_estandar_lead_time,
        nivel_servicio_objetivo=nivel_servicio_objetivo,
    )
    await proveedor_repo.actualizar(session, id, datos)
    form = await request.form()
    imagen = form.get("imagen")
    if isinstance(imagen, UploadFile) and imagen.filename:
        imagen_url = await subir_imagen_supabase(imagen, folder=f"public/proveedores/{id}")
        if imagen_url:
            await proveedor_repo.actualizar(session, id, ProveedorUpdate(imagen_url=imagen_url))
    return RedirectResponse(url="/proveedores", status_code=303)


@router.get("/ventas")
async def ventas(
    request: Request,
    page: int = Query(1, ge=1),
    busqueda_nombre: str = Query(""),
    session: AsyncSession = Depends(get_session),
):
    if busqueda_nombre:
        ventas_list, total, current_page, total_pages = await venta_repo.buscar_por_nombre_producto_paginado(session, busqueda_nombre, page)
    else:
        ventas_list, total, current_page, total_pages = await venta_repo.listar_paginado(session, page)
    productos_list = await producto_repo.listar_activos(session)
    productos_map = {p.id: p for p in productos_list}

    ventas_rows = []
    for v in ventas_list:
        prod = productos_map.get(v.id_producto)
        nombre_prod = prod.nombre if prod else "—"
        ventas_rows.append({
            "id": v.id,
            "ID": v.id[:8],
            "Producto": nombre_prod,
            "Cantidad": str(v.cantidad),
            "Fecha": v.fecha_venta.isoformat(),
            "detail_data": json.dumps({
                "titulo": f"Venta {v.id[:8]}",
                "imagen_url": "",
                "campos": [
                    {"label": "ID", "valor": v.id[:8]},
                    {"label": "Producto", "valor": nombre_prod},
                    {"label": "Cantidad", "valor": str(v.cantidad)},
                    {"label": "Fecha", "valor": v.fecha_venta.isoformat()},
                ],
            }),
        })

    producto_options = [(p.id, p.nombre) for p in productos_list]

    extra_params = {"busqueda_nombre": busqueda_nombre}

    return templates.TemplateResponse(request, "ventas.html", {
        "ventas_rows": ventas_rows,
        "ventas_headers": ["ID", "Producto", "Cantidad", "Fecha"],
        "producto_options": producto_options,
        "total_ventas_valor": total,
        "page": current_page,
        "total_pages": total_pages,
        "total": total,
        "busqueda_nombre": busqueda_nombre,
        "extra_params": extra_params,
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


@router.get("/ventas/{id}/editar")
async def editar_venta_form(
    request: Request,
    id: str,
    session: AsyncSession = Depends(get_session),
):
    venta = await venta_repo.obtener_por_id(session, id)
    if not venta:
        return RedirectResponse(url="/ventas", status_code=303)
    productos_list = await producto_repo.listar_activos(session)
    producto_options = [(p.id, p.nombre) for p in productos_list]
    return templates.TemplateResponse(request, "editar_venta.html", {
        "venta": venta,
        "producto_options": producto_options,
    })


@router.post("/ventas/{id}/delete")
async def eliminar_venta(id: str, session: AsyncSession = Depends(get_session)):
    venta = await venta_repo.obtener_por_id(session, id)
    if venta:
        await session.delete(venta)
        await session.commit()
    return RedirectResponse(url="/ventas", status_code=303)


@router.post("/ventas/{id}/editar")
async def editar_venta(
    id: str,
    session: AsyncSession = Depends(get_session),
    id_producto: str = Form(...),
    cantidad: int = Form(...),
):
    venta = await venta_repo.obtener_por_id(session, id)
    if not venta:
        return RedirectResponse(url="/ventas", status_code=303)
    if id_producto != venta.id_producto:
        venta.id_producto = id_producto
    if cantidad != venta.cantidad:
        venta.cantidad = cantidad
    session.add(venta)
    await session.commit()
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
