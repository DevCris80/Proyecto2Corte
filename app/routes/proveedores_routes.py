from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.storage import subir_imagen_supabase
from app.models.proveedor import ProveedorCreate, ProveedorPublic, ProveedorUpdate
from app.repository import proveedor_repo

router = APIRouter(prefix="/proveedores", tags=["proveedores"])


@router.post("", response_model=ProveedorPublic, status_code=201)
async def crear_proveedor(
    proveedor: ProveedorCreate,
    session: AsyncSession = Depends(get_session),
):
    try:
        return await proveedor_repo.crear(session, proveedor)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(error)}")


@router.get("", response_model=list[ProveedorPublic], status_code=200)
async def listar_proveedores(
    session: AsyncSession = Depends(get_session),
):
    try:
        return await proveedor_repo.listar_activos(session)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(error)}")


@router.patch("/{id}", response_model=ProveedorPublic, status_code=200)
async def actualizar_proveedor(
    id: str,
    datos: ProveedorUpdate,
    session: AsyncSession = Depends(get_session),
):
    cambios = datos.model_dump(exclude_unset=True)
    if not cambios:
        raise HTTPException(
            status_code=400,
            detail="La peticion PATCH esta vacia. Debe enviar al menos un atributo valido.",
        )

    proveedor = await proveedor_repo.actualizar(session, id, datos)
    if not proveedor:
        raise HTTPException(
            status_code=404,
            detail=f"Proveedor con ID {id} no encontrado.",
        )
    return proveedor


@router.post("/{id}/imagen", response_model=ProveedorPublic, status_code=200)
async def subir_imagen_proveedor(
    id: str,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    proveedor = await proveedor_repo.obtener_por_id(session, id)
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado.")
    
    url_imagen = await subir_imagen_supabase(file, folder="public/proveedores")
    
    actualizacion = ProveedorUpdate(imagen_url=url_imagen)
    return await proveedor_repo.actualizar(session, id, actualizacion)


@router.delete("/{id}", status_code=204)
async def eliminar_proveedor(
    id: str,
    session: AsyncSession = Depends(get_session),
):
    exito = await proveedor_repo.eliminar(session, id)
    if not exito:
        raise HTTPException(status_code=404, detail="ID no encontrado")
    return {"detail": f"Proveedor con ID {id} ha sido desactivado."}
