"""
Script para poblar la base de datos con datos semilla.
Mercado tech, precios en COP, sin imágenes.

Uso: python scripts/seed_data.py
"""

import asyncio
import random
from datetime import date, timedelta

from sqlalchemy import delete

from sqlmodel import SQLModel

from app.core.database import async_session, engine
from app.models.proveedor import Proveedor, ProveedorCreate
from app.models.producto import Producto, ProductoCreate
from app.models.venta import Venta, VentaCreate
from app.repository import proveedor_repo, producto_repo, venta_repo

random.seed(42)

PROVEEDORES_DATA = [
    ProveedorCreate(
        nombre="TechDistribution Global S.A.",
        costo_pedido_fijo=350_000,
        lead_time_promedio=5.0,
        desviacion_estandar_lead_time=1.2,
        nivel_servicio_objetivo=0.95,
    ),
    ProveedorCreate(
        nombre="Periféricos y Componentes del Sur",
        costo_pedido_fijo=180_000,
        lead_time_promedio=3.0,
        desviacion_estandar_lead_time=0.8,
        nivel_servicio_objetivo=0.92,
    ),
    ProveedorCreate(
        nombre="Monitores y Pantallas Profesionales",
        costo_pedido_fijo=280_000,
        lead_time_promedio=6.0,
        desviacion_estandar_lead_time=1.5,
        nivel_servicio_objetivo=0.97,
    ),
    ProveedorCreate(
        nombre="Almacenamiento y Memoria Tech",
        costo_pedido_fijo=120_000,
        lead_time_promedio=3.5,
        desviacion_estandar_lead_time=0.9,
        nivel_servicio_objetivo=0.93,
    ),
    ProveedorCreate(
        nombre="Suministros de Oficina Tecnológica",
        costo_pedido_fijo=85_000,
        lead_time_promedio=2.0,
        desviacion_estandar_lead_time=0.5,
        nivel_servicio_objetivo=0.90,
    ),
    ProveedorCreate(
        nombre="Componentes Electrónicos Elite",
        costo_pedido_fijo=400_000,
        lead_time_promedio=7.0,
        desviacion_estandar_lead_time=2.0,
        nivel_servicio_objetivo=0.98,
    ),
]

PRODUCTOS_DATA = [
    {"nombre": "Mouse Inalámbrico Ergonómico",     "prov_idx": 1, "stock": 150, "costo": 120_000,     "almacenamiento": 24_000,    "demanda": 2_400},
    {"nombre": "Teclado Mecánico RGB",             "prov_idx": 1, "stock": 80,  "costo": 280_000,     "almacenamiento": 56_000,    "demanda": 1_800},
    {"nombre": "Audífonos Gaming 7.1",             "prov_idx": 1, "stock": 60,  "costo": 450_000,     "almacenamiento": 90_000,    "demanda": 1_200},
    {"nombre": "Monitor 27\" 4K IPS",               "prov_idx": 2, "stock": 35,  "costo": 1_800_000,   "almacenamiento": 450_000,   "demanda": 600},
    {"nombre": "Monitor UltraWide 34\"",            "prov_idx": 2, "stock": 15,  "costo": 3_200_000,   "almacenamiento": 800_000,   "demanda": 280},
    {"nombre": "Monitor 24\" FullHD 144Hz",         "prov_idx": 2, "stock": 45,  "costo": 850_000,     "almacenamiento": 212_500,   "demanda": 900},
    {"nombre": "SSD NVMe 1TB",                     "prov_idx": 3, "stock": 120, "costo": 350_000,     "almacenamiento": 70_000,    "demanda": 3_000},
    {"nombre": "Memoria RAM DDR5 32GB",            "prov_idx": 3, "stock": 90,  "costo": 520_000,     "almacenamiento": 104_000,   "demanda": 1_500},
    {"nombre": "Disco Duro Externo 4TB",           "prov_idx": 3, "stock": 40,  "costo": 420_000,     "almacenamiento": 84_000,    "demanda": 800},
    {"nombre": "Webcam HD 1080p",                  "prov_idx": 4, "stock": 100, "costo": 160_000,     "almacenamiento": 32_000,    "demanda": 2_000},
    {"nombre": "Hub USB-C 7 Puertos",              "prov_idx": 4, "stock": 75,  "costo": 95_000,      "almacenamiento": 19_000,    "demanda": 2_500},
    {"nombre": "Base Notebook Ajustable",          "prov_idx": 4, "stock": 55,  "costo": 110_000,     "almacenamiento": 22_000,    "demanda": 1_500},
    {"nombre": "Laptop Gamer Pro X 15\"",           "prov_idx": 0, "stock": 25,  "costo": 6_500_000,   "almacenamiento": 1_625_000, "demanda": 520},
    {"nombre": "PC Escritorio Office i7",          "prov_idx": 0, "stock": 18,  "costo": 4_200_000,   "almacenamiento": 1_050_000, "demanda": 380},
    {"nombre": "Tablet Profesional 12.9\"",         "prov_idx": 0, "stock": 30,  "costo": 3_200_000,   "almacenamiento": 800_000,   "demanda": 450},
    {"nombre": "Tarjeta Gráfica RTX 5070",         "prov_idx": 5, "stock": 8,   "costo": 8_500_000,   "almacenamiento": 2_125_000, "demanda": 180},
    {"nombre": "Fuente Poder 850W Modular",        "prov_idx": 5, "stock": 25,  "costo": 650_000,     "almacenamiento": 162_500,   "demanda": 400},
    {"nombre": "Procesador Ryzen 9 9950X",         "prov_idx": 5, "stock": 12,  "costo": 2_800_000,   "almacenamiento": 700_000,   "demanda": 200},
]

VENTAS_CONFIG = [
    # (producto_index, num_ventas, cantidad_maxima)
    (0,  18, 5),   # Mouse
    (1,  14, 4),   # Teclado
    (2,  10, 3),   # Audífonos
    (3,  5,  1),   # Monitor 27"
    (4,  3,  1),   # Monitor 34"
    (5,  8,  2),   # Monitor 24"
    (6,  12, 4),   # SSD
    (7,  10, 3),   # RAM
    (8,  7,  2),   # Disco Externo
    (9,  15, 5),   # Webcam
    (10, 18, 8),   # Hub USB-C
    (11, 10, 4),   # Base Notebook
    (12, 4,  1),   # Laptop
    (13, 3,  1),   # PC
    (14, 5,  1),   # Tablet
    (15, 2,  1),   # RTX 5070
    (16, 5,  2),   # Fuente Poder
    (17, 3,  1),   # Ryzen 9
]


async def limpiar_datos():
    async with async_session() as session:
        await session.execute(delete(Venta))
        await session.execute(delete(Producto))
        await session.execute(delete(Proveedor))
        await session.commit()
    print("  Datos anteriores eliminados.")


async def insertar_proveedores() -> list[Proveedor]:
    proveedores = []
    for p in PROVEEDORES_DATA:
        async with async_session() as session:
            prov = await proveedor_repo.crear(session, p)
            proveedores.append(prov)
            print(f"  ✓ Proveedor: {prov.nombre}")
    return proveedores


async def insertar_productos(proveedores: list[Proveedor]) -> list[Producto]:
    productos = []
    for d in PRODUCTOS_DATA:
        async with async_session() as session:
            prod = await producto_repo.crear(
                session,
                ProductoCreate(
                    nombre=d["nombre"],
                    id_proveedor=proveedores[d["prov_idx"]].id,
                    stock_actual=d["stock"],
                    costo_unitario=d["costo"],
                    costo_almacenamiento_anual=d["almacenamiento"],
                    demanda_anual_estimada=d["demanda"],
                ),
            )
            productos.append(prod)
            print(f"  ✓ Producto: {prod.nombre} — ${d['costo']:,.0f} | stock: {d['stock']}")
    return productos


async def insertar_ventas(productos: list[Producto]) -> int:
    total = 0
    today = date.today()
    dias = 90

    for prod_idx, num_ventas, cant_max in VENTAS_CONFIG:
        pid = productos[prod_idx].id
        for _ in range(num_ventas):
            async with async_session() as session:
                venta = await venta_repo.crear_con_descuento_stock(
                    session,
                    VentaCreate(
                        id_producto=pid,
                        cantidad=random.randint(1, cant_max),
                        fecha_venta=today - timedelta(days=random.randint(0, dias - 1)),
                    ),
                )
                if venta:
                    total += 1

    return total


async def main():
    print("=" * 52)
    print("  POBLAR BASE DE DATOS — DATOS SEMILLA")
    print("=" * 52)
    print()

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("  Tablas creadas/verificadas.")

    await limpiar_datos()
    print()

    print("Insertando proveedores...")
    proveedores = await insertar_proveedores()
    print(f"  → {len(proveedores)} proveedores creados\n")

    print("Insertando productos...")
    productos = await insertar_productos(proveedores)
    print(f"  → {len(productos)} productos creados\n")

    print("Insertando ventas...")
    total_ventas = await insertar_ventas(productos)
    print(f"  → {total_ventas} ventas creadas\n")

    print("✔  Base de datos poblada exitosamente.")


if __name__ == "__main__":
    asyncio.run(main())
