import json
from fastapi import APIRouter, Depends, Form, Query, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlencode

from app.core.storage import subir_imagen_supabase, validar_mime_imagen, imagen_url_transformada
from app.core.database import get_session
from app.core.templates import templates
from app.repository import proveedor_repo
from app.models.proveedor import ProveedorCreate, ProveedorUpdate

router = APIRouter(tags=["pages"])


@router.get("/proveedores")
async def listar_proveedores_pagina(
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
        thumb = imagen_url_transformada(p.imagen_url, 60, 60) if p.imagen_url else ""
        proveedores_rows.append({
            "id": p.id,
            "Imagen": thumb,
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
        "proveedores_headers": ["Imagen", "Nombre", "Costo Pedido", "Lead Time", "Nivel Servicio"],
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
async def crear_proveedor_pagina(
    session: AsyncSession = Depends(get_session),
    nombre: str = Form(...),
    costo_pedido_fijo: float = Form(...),
    lead_time_promedio: float = Form(...),
    desviacion_estandar_lead_time: float = Form(0.0),
    nivel_servicio_objetivo: float = Form(0.95),
    imagen: UploadFile | None = Form(None),
):
    if imagen and imagen.filename:
        error = validar_mime_imagen(imagen)
        if error:
            qs = urlencode({"toast": error, "toast_type": "error"})
            return RedirectResponse(url=f"/proveedores?{qs}", status_code=303)
    datos = ProveedorCreate(
        nombre=nombre,
        costo_pedido_fijo=costo_pedido_fijo,
        lead_time_promedio=lead_time_promedio,
        desviacion_estandar_lead_time=desviacion_estandar_lead_time,
        nivel_servicio_objetivo=nivel_servicio_objetivo,
    )
    proveedor = await proveedor_repo.crear(session, datos)
    if imagen and imagen.filename:
        imagen_url = await subir_imagen_supabase(imagen, folder=f"public/proveedores/{proveedor.id}")
        if imagen_url:
            await proveedor_repo.actualizar(session, proveedor.id, ProveedorUpdate(imagen_url=imagen_url))
    qs = urlencode({"toast": "Proveedor creado correctamente", "toast_type": "success"})
    return RedirectResponse(url=f"/proveedores?{qs}", status_code=303)


@router.post("/proveedores/{id}/delete")
async def eliminar_proveedor_pagina(id: str, session: AsyncSession = Depends(get_session)):
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
async def editar_proveedor_pagina(
    id: str,
    session: AsyncSession = Depends(get_session),
    nombre: str = Form(...),
    costo_pedido_fijo: float = Form(...),
    lead_time_promedio: float = Form(...),
    desviacion_estandar_lead_time: float = Form(0.0),
    nivel_servicio_objetivo: float = Form(0.95),
    imagen: UploadFile | None = Form(None),
):
    if imagen and imagen.filename:
        error = validar_mime_imagen(imagen)
        if error:
            qs = urlencode({"toast": error, "toast_type": "error"})
            return RedirectResponse(url=f"/proveedores?{qs}", status_code=303)
    datos = ProveedorUpdate(
        nombre=nombre,
        costo_pedido_fijo=costo_pedido_fijo,
        lead_time_promedio=lead_time_promedio,
        desviacion_estandar_lead_time=desviacion_estandar_lead_time,
        nivel_servicio_objetivo=nivel_servicio_objetivo,
    )
    await proveedor_repo.actualizar(session, id, datos)
    if imagen and imagen.filename:
        imagen_url = await subir_imagen_supabase(imagen, folder=f"public/proveedores/{id}")
        if imagen_url:
            await proveedor_repo.actualizar(session, id, ProveedorUpdate(imagen_url=imagen_url))
    return RedirectResponse(url="/proveedores", status_code=303)
