import math
import uuid
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.proveedor import Proveedor, ProveedorCreate, ProveedorUpdate


async def listar_activos(session: AsyncSession):
    result = await session.execute(
        select(Proveedor).where(Proveedor.estado_activo)
    )
    return result.scalars().all()


async def contar_activos(session: AsyncSession) -> int:
    query = select(func.count()).select_from(Proveedor).where(Proveedor.estado_activo)
    result = await session.execute(query)
    return result.scalar() or 0


async def listar_activos_paginado(
    session: AsyncSession, page: int = 1, per_page: int = 50
) -> tuple[list[Proveedor], int, int, int]:
    total = await contar_activos(session)
    total_pages = max(1, math.ceil(total / per_page))
    query = (
        select(Proveedor)
        .where(Proveedor.estado_activo)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await session.execute(query)
    items = list(result.scalars().all())
    return items, total, page, total_pages


async def obtener_por_id(session: AsyncSession, id: str) -> Proveedor | None:
    result = await session.execute(select(Proveedor).where(Proveedor.id == id))
    return result.scalar_one_or_none()


async def crear(session: AsyncSession, datos: ProveedorCreate) -> Proveedor:
    proveedor = Proveedor(
        id=str(uuid.uuid4())[:8],
        **datos.model_dump(),
    )
    session.add(proveedor)
    await session.commit()
    await session.refresh(proveedor)
    return proveedor


async def actualizar(
    session: AsyncSession, id: str, datos: ProveedorUpdate
) -> Proveedor | None:
    proveedor = await obtener_por_id(session, id)
    if not proveedor:
        return None

    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(proveedor, campo, valor)

    session.add(proveedor)
    await session.commit()
    await session.refresh(proveedor)
    return proveedor


async def eliminar(session: AsyncSession, id: str) -> bool:
    proveedor = await obtener_por_id(session, id)
    if not proveedor:
        return False

    proveedor.estado_activo = False
    session.add(proveedor)
    await session.commit()
    return True
