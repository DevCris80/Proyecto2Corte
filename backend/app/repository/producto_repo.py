import math
import uuid
from typing import Optional
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.producto import Producto, ProductoCreate, ProductoUpdate


async def listar(
    session: AsyncSession, estado: Optional[bool] = None
):
    query = select(Producto)
    if estado is not None:
        query = query.where(Producto.estado_activo == estado)
    result = await session.execute(query)
    return result.scalars().all()


async def listar_activos(session: AsyncSession):
    return await listar(session, estado=True)


async def contar_activos(session: AsyncSession) -> int:
    query = select(func.count()).select_from(Producto).where(Producto.estado_activo)
    result = await session.execute(query)
    return result.scalar() or 0


async def listar_activos_paginado(
    session: AsyncSession, page: int = 1, per_page: int = 50
) -> tuple[list[Producto], int, int, int]:
    total = await contar_activos(session)
    total_pages = max(1, math.ceil(total / per_page))
    query = (
        select(Producto)
        .where(Producto.estado_activo)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await session.execute(query)
    items = list(result.scalars().all())
    return items, total, page, total_pages


async def obtener_por_id(session: AsyncSession, id: str) -> Producto | None:
    result = await session.execute(select(Producto).where(Producto.id == id))
    return result.scalar_one_or_none()


async def buscar_por_nombre(
    session: AsyncSession, nombre: str
):
    result = await session.execute(
        select(Producto).where(
            Producto.nombre.ilike(f"%{nombre}%"),
            Producto.estado_activo,
        )
    )
    return result.scalars().all()


async def crear(session: AsyncSession, datos: ProductoCreate) -> Producto:
    producto = Producto(
        id=str(uuid.uuid4())[:8],
        **datos.model_dump(),
    )
    session.add(producto)
    await session.commit()
    await session.refresh(producto)
    return producto


async def actualizar(
    session: AsyncSession, id: str, datos: ProductoUpdate
) -> Producto | None:
    producto = await obtener_por_id(session, id)
    if not producto:
        return None

    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(producto, campo, valor)

    session.add(producto)
    await session.commit()
    await session.refresh(producto)
    return producto


async def eliminar(session: AsyncSession, id: str) -> bool:
    producto = await obtener_por_id(session, id)
    if not producto:
        return False

    producto.estado_activo = False
    session.add(producto)
    await session.commit()
    return True
