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


async def buscar_por_nombre(session: AsyncSession, nombre: str):
    result = await session.execute(
        select(Proveedor).where(
            Proveedor.nombre.ilike(f"%{nombre}%"),
            Proveedor.estado_activo,
        )
    )
    return result.scalars().all()


async def contar_busqueda_nombre(session: AsyncSession, nombre: str) -> int:
    query = (
        select(func.count())
        .select_from(Proveedor)
        .where(
            Proveedor.nombre.ilike(f"%{nombre}%"),
            Proveedor.estado_activo,
        )
    )
    result = await session.execute(query)
    return result.scalar() or 0


async def buscar_por_nombre_paginado(
    session: AsyncSession, nombre: str, page: int = 1, per_page: int = 50
) -> tuple[list[Proveedor], int, int, int]:
    total = await contar_busqueda_nombre(session, nombre)
    total_pages = max(1, math.ceil(total / per_page))
    query = (
        select(Proveedor)
        .where(
            Proveedor.nombre.ilike(f"%{nombre}%"),
            Proveedor.estado_activo,
        )
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


def _build_proveedor_conditions(
    busqueda_nombre: str = "",
    lead_time_min: float | None = None,
    lead_time_max: float | None = None,
    costo_min: float | None = None,
    costo_max: float | None = None,
    nivel_servicio_min: float | None = None,
) -> list:
    conditions = [Proveedor.estado_activo == True]
    if busqueda_nombre:
        conditions.append(Proveedor.nombre.ilike(f"%{busqueda_nombre}%"))
    if lead_time_min is not None:
        conditions.append(Proveedor.lead_time_promedio >= lead_time_min)
    if lead_time_max is not None:
        conditions.append(Proveedor.lead_time_promedio <= lead_time_max)
    if costo_min is not None:
        conditions.append(Proveedor.costo_pedido_fijo >= costo_min)
    if costo_max is not None:
        conditions.append(Proveedor.costo_pedido_fijo <= costo_max)
    if nivel_servicio_min is not None:
        conditions.append(Proveedor.nivel_servicio_objetivo >= nivel_servicio_min)
    return conditions


async def contar_con_filtros(
    session: AsyncSession,
    *,
    busqueda_nombre: str = "",
    lead_time_min: float | None = None,
    lead_time_max: float | None = None,
    costo_min: float | None = None,
    costo_max: float | None = None,
    nivel_servicio_min: float | None = None,
) -> int:
    conditions = _build_proveedor_conditions(
        busqueda_nombre=busqueda_nombre,
        lead_time_min=lead_time_min,
        lead_time_max=lead_time_max,
        costo_min=costo_min,
        costo_max=costo_max,
        nivel_servicio_min=nivel_servicio_min,
    )
    query = select(func.count()).select_from(Proveedor).where(*conditions)
    result = await session.execute(query)
    return result.scalar() or 0


async def buscar_con_filtros_paginado(
    session: AsyncSession,
    *,
    busqueda_nombre: str = "",
    lead_time_min: float | None = None,
    lead_time_max: float | None = None,
    costo_min: float | None = None,
    costo_max: float | None = None,
    nivel_servicio_min: float | None = None,
    ordenar_por: str = "nombre",
    orden_dir: str = "asc",
    page: int = 1,
    per_page: int = 50,
) -> tuple[list[Proveedor], int, int, int]:
    conditions = _build_proveedor_conditions(
        busqueda_nombre=busqueda_nombre,
        lead_time_min=lead_time_min,
        lead_time_max=lead_time_max,
        costo_min=costo_min,
        costo_max=costo_max,
        nivel_servicio_min=nivel_servicio_min,
    )

    col_map = {
        "nombre": Proveedor.nombre,
        "lead_time_promedio": Proveedor.lead_time_promedio,
        "costo_pedido_fijo": Proveedor.costo_pedido_fijo,
        "nivel_servicio_objetivo": Proveedor.nivel_servicio_objetivo,
    }
    col = col_map.get(ordenar_por, Proveedor.nombre)
    order = col.asc() if orden_dir == "asc" else col.desc()

    total = await contar_con_filtros(
        session,
        busqueda_nombre=busqueda_nombre,
        lead_time_min=lead_time_min,
        lead_time_max=lead_time_max,
        costo_min=costo_min,
        costo_max=costo_max,
        nivel_servicio_min=nivel_servicio_min,
    )
    total_pages = max(1, math.ceil(total / per_page))

    query = (
        select(Proveedor)
        .where(*conditions)
        .order_by(order)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await session.execute(query)
    items = list(result.scalars().all())
    return items, total, page, total_pages
