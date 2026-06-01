from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.storage import subir_imagen_supabase
from app.models.producto import ProductoCreate, ProductoPublic, ProductoUpdate
from app.repository import producto_repo, proveedor_repo

router = APIRouter(prefix="/productos", tags=["productos"])


@router.post("", response_model=ProductoPublic, status_code=201)
async def crear_producto(
    producto: ProductoCreate,
    session: AsyncSession = Depends(get_session),
):
    proveedor = await proveedor_repo.obtener_por_id(session, producto.id_proveedor)
    if not proveedor or not proveedor.estado_activo:
        raise HTTPException(
            status_code=404, detail="Proveedor no encontrado o inactivo"
        )

    productos_existentes = await producto_repo.listar_activos(session)
    nombre_nuevo = producto.nombre.strip().lower()
    for p in productos_existentes:
        if p.nombre.strip().lower() == nombre_nuevo:
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe un producto activo registrado como '{producto.nombre}'.",
            )

    try:
        return await producto_repo.crear(session, producto)
    except Exception as error:
        raise HTTPException(
            status_code=500, detail=f"Error inesperado: {str(error)}"
        )


@router.get("", response_model=list[ProductoPublic], status_code=200)
async def listar_productos(
    estado: bool = Query(None, description="Filtrar por estado activo"),
    session: AsyncSession = Depends(get_session),
):
    try:
        return await producto_repo.listar(session, estado)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(error)}")


@router.get("/buscar", response_model=list[ProductoPublic], status_code=200)
async def buscar_productos(
    nombre: str = Query(..., description="Nombre del producto a buscar"),
    session: AsyncSession = Depends(get_session),
):
    try:
        return await producto_repo.buscar_por_nombre(session, nombre)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(error)}")


@router.patch("/{id}", response_model=ProductoPublic, status_code=200)
async def actualizar_producto(
    id: str,
    datos: ProductoUpdate,
    session: AsyncSession = Depends(get_session),
):
    cambios = datos.model_dump(exclude_unset=True)
    if not cambios:
        raise HTTPException(
            status_code=400,
            detail="La peticion PATCH esta vacia. Debe enviar al menos un atributo valido.",
        )

    producto = await producto_repo.actualizar(session, id, datos)
    if not producto:
        raise HTTPException(
            status_code=404,
            detail=f"Producto con ID {id} no encontrado.",
        )
    return producto

@router.post("/{id}/imagen", response_model=ProductoPublic, status_code=200)
async def subir_imagen_producto(
    id: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    producto = await producto_repo.obtener_por_id(session, id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    
    url_imagen = await subir_imagen_supabase(file, folder="public/productos")
    
    actualizacion = ProductoUpdate(imagen_url=url_imagen)
    return await producto_repo.actualizar(session, id, actualizacion)


@router.delete("/{id}", status_code=200)
async def eliminar_producto(
    id: str,
    session: AsyncSession = Depends(get_session),
):
    try:
        exito = await producto_repo.eliminar(session, id)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(error)}")

    if not exito:
        raise HTTPException(status_code=404, detail="ID no encontrado")

    return {"mensaje": "Borrado exitoso"}
