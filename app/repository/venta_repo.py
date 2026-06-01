import math
import uuid
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.venta import Venta, VentaCreate
from app.models.producto import Producto


async def listar(session: AsyncSession) -> list[Venta]:
    result = await session.execute(select(Venta))
    return result.scalars().all()


async def contar(session: AsyncSession) -> int:
    query = select(func.count()).select_from(Venta)
    result = await session.execute(query)
    return result.scalar() or 0


async def listar_paginado(
    session: AsyncSession, page: int = 1, per_page: int = 50
) -> tuple[list[Venta], int, int, int]:
    total = await contar(session)
    total_pages = max(1, math.ceil(total / per_page))
    query = (
        select(Venta)
        .order_by(Venta.fecha_venta.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await session.execute(query)
    items = list(result.scalars().all())
    return items, total, page, total_pages


async def buscar_por_nombre_producto(
    session: AsyncSession, nombre: str
):
    result = await session.execute(
        select(Venta)
        .join(Producto, Venta.id_producto == Producto.id)
        .where(
            Producto.nombre.ilike(f"%{nombre}%"),
        )
        .order_by(Venta.fecha_venta.desc())
    )
    return result.scalars().all()


async def contar_busqueda_producto(session: AsyncSession, nombre: str) -> int:
    query = (
        select(func.count())
        .select_from(Venta)
        .join(Producto, Venta.id_producto == Producto.id)
        .where(
            Producto.nombre.ilike(f"%{nombre}%"),
        )
    )
    result = await session.execute(query)
    return result.scalar() or 0


async def buscar_por_nombre_producto_paginado(
    session: AsyncSession, nombre: str, page: int = 1, per_page: int = 50
) -> tuple[list[Venta], int, int, int]:
    total = await contar_busqueda_producto(session, nombre)
    total_pages = max(1, math.ceil(total / per_page))
    query = (
        select(Venta)
        .join(Producto, Venta.id_producto == Producto.id)
        .where(
            Producto.nombre.ilike(f"%{nombre}%"),
        )
        .order_by(Venta.fecha_venta.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await session.execute(query)
    items = list(result.scalars().all())
    return items, total, page, total_pages


async def obtener_por_id(session: AsyncSession, id: str) -> Venta | None:
    result = await session.execute(select(Venta).where(Venta.id == id))
    return result.scalar_one_or_none()


async def crear(
    session: AsyncSession, datos: VentaCreate
) -> Venta:
    venta = Venta(id=str(uuid.uuid4())[:8], **datos.model_dump())
    session.add(venta)
    await session.commit()
    await session.refresh(venta)
    return venta


async def crear_con_descuento_stock(
    session: AsyncSession, datos: VentaCreate
) -> Venta | None:
    producto = await session.execute(
        select(Producto).where(
            Producto.id == datos.id_producto,
            Producto.estado_activo,
        )
    )
    producto = producto.scalar_one_or_none()
    if not producto:
        return None

    if producto.stock_actual < datos.cantidad:
        return None

    venta = Venta(id=str(uuid.uuid4())[:8], **datos.model_dump())
    producto.stock_actual -= datos.cantidad

    session.add(venta)
    session.add(producto)
    await session.commit()
    await session.refresh(venta)
    return venta
