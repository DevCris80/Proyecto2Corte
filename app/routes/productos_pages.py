import json
from fastapi import APIRouter, Depends, Form, Query, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlencode

from app.core.storage import subir_imagen_supabase, validar_mime_imagen, imagen_url_transformada
from app.core.database import get_session
from app.core.templates import templates
from app.repository import producto_repo, proveedor_repo
from app.models.producto import ProductoCreate, ProductoUpdate

router = APIRouter(tags=["pages"])


@router.get("/productos")
async def listar_productos_pagina(
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
        thumb = imagen_url_transformada(p.imagen_url, 60, 60) if p.imagen_url else ""
        productos_rows.append({
            "id": p.id,
            "Imagen": thumb,
            "Nombre": p.nombre,
            "Proveedor": nombre_prov,
            "Stock": str(p.stock_actual),
            "Costo Unit.": f"${p.costo_unitario:,.2f}",
            "Demanda Anual": str(int(p.demanda_anual_estimada)),
            "detail_data": json.dumps({
                "titulo": p.nombre,
                "imagen_url": p.imagen_url or "",
                "imagen_modal": imagen_url_transformada(p.imagen_url, 300) if p.imagen_url else "",
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
        "productos_headers": ["Imagen", "Nombre", "Proveedor", "Stock", "Costo Unit.", "Demanda Anual"],
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
async def crear_producto_pagina(
    session: AsyncSession = Depends(get_session),
    nombre: str = Form(...),
    id_proveedor: str = Form(...),
    stock_actual: int = Form(...),
    costo_unitario: float = Form(...),
    costo_almacenamiento_anual: float = Form(...),
    demanda_anual_estimada: float = Form(...),
    imagen: UploadFile | None = Form(None),
):
    if imagen and imagen.filename:
        error = validar_mime_imagen(imagen)
        if error:
            qs = urlencode({"toast": error, "toast_type": "error"})
            return RedirectResponse(url=f"/productos?{qs}", status_code=303)
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
        imagen_url = await subir_imagen_supabase(imagen, folder=f"public/productos/{producto.id}")
        if imagen_url:
            await producto_repo.actualizar(session, producto.id, ProductoUpdate(imagen_url=imagen_url))
    return RedirectResponse(url="/productos", status_code=303)


@router.post("/productos/{id}/delete")
async def eliminar_producto_pagina(id: str, session: AsyncSession = Depends(get_session)):
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
async def editar_producto_pagina(
    id: str,
    session: AsyncSession = Depends(get_session),
    nombre: str = Form(...),
    id_proveedor: str = Form(...),
    stock_actual: int = Form(...),
    costo_unitario: float = Form(...),
    costo_almacenamiento_anual: float = Form(...),
    demanda_anual_estimada: float = Form(...),
    imagen: UploadFile | None = Form(None),
):
    if imagen and imagen.filename:
        error = validar_mime_imagen(imagen)
        if error:
            qs = urlencode({"toast": error, "toast_type": "error"})
            return RedirectResponse(url=f"/productos?{qs}", status_code=303)
    datos = ProductoUpdate(
        nombre=nombre,
        id_proveedor=id_proveedor,
        stock_actual=stock_actual,
        costo_unitario=costo_unitario,
        costo_almacenamiento_anual=costo_almacenamiento_anual,
        demanda_anual_estimada=demanda_anual_estimada,
    )
    await producto_repo.actualizar(session, id, datos)
    if imagen and imagen.filename:
        imagen_url = await subir_imagen_supabase(imagen, folder=f"public/productos/{id}")
        if imagen_url:
            await producto_repo.actualizar(session, id, ProductoUpdate(imagen_url=imagen_url))
    return RedirectResponse(url="/productos", status_code=303)
