import json
from fastapi import APIRouter, Depends, Form, Query, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlencode

from app.core.database import get_session
from app.core.templates import templates
from app.repository import producto_repo, venta_repo
from app.models.venta import VentaCreate

router = APIRouter(tags=["pages"])


@router.get("/ventas")
async def listar_ventas_pagina(
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
async def crear_venta_pagina(
    request: Request,
    session: AsyncSession = Depends(get_session),
    id_producto: str = Form(...),
    cantidad: int = Form(...),
):
    datos = VentaCreate(id_producto=id_producto, cantidad=cantidad)
    venta = await venta_repo.crear_con_descuento_stock(session, datos)
    if not venta:
        qs = urlencode({"toast": "No hay suficiente stock para realizar la venta", "toast_type": "error"})
        return RedirectResponse(url=f"/ventas?{qs}", status_code=303)
    qs = urlencode({"toast": "Venta registrada correctamente", "toast_type": "success"})
    return RedirectResponse(url=f"/ventas?{qs}", status_code=303)


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
async def eliminar_venta_pagina(id: str, session: AsyncSession = Depends(get_session)):
    venta = await venta_repo.obtener_por_id(session, id)
    if venta:
        await session.delete(venta)
        await session.commit()
    return RedirectResponse(url="/ventas", status_code=303)


@router.post("/ventas/{id}/editar")
async def editar_venta_pagina(
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
