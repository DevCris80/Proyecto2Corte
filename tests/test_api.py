import pytest
from contextlib import asynccontextmanager
from datetime import date
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from main import app
from app.models.producto import Producto
from app.models.proveedor import Proveedor
from app.models.venta import Venta


@asynccontextmanager
async def _noop_lifespan(_app):
    yield

app.lifespan_context = _noop_lifespan


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def proveedor_mock():
    return Proveedor(
        id="prov001",
        nombre="Proveedor Test",
        costo_pedido_fijo=50.0,
        lead_time_promedio=5.0,
        desviacion_estandar_lead_time=1.0,
        nivel_servicio_objetivo=0.95,
        estado_activo=True,
    )


@pytest.fixture
def producto_mock():
    return Producto(
        id="prod001",
        nombre="Producto Test",
        id_proveedor="prov001",
        stock_actual=100,
        costo_unitario=10.0,
        costo_almacenamiento_anual=2.0,
        demanda_anual_estimada=1000,
        estado_activo=True,
    )


class TestPagesRoutes:
    async def test_index_returns_html(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert "SISPRO" in response.text

    async def test_productos_page(self, client):
        with (
            patch(
                "app.routes.pages.producto_repo.buscar_con_filtros_paginado",
                new_callable=AsyncMock,
                return_value=([], 0, 1, 1),
            ),
            patch(
                "app.routes.pages.proveedor_repo.listar_activos_resumen_cached",
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            response = await client.get("/productos")
            assert response.status_code == 200
            assert "Productos" in response.text

    async def test_proveedores_page(self, client):
        with (
            patch(
                "app.routes.pages.proveedor_repo.buscar_con_filtros_paginado",
                new_callable=AsyncMock,
                return_value=([], 0, 1, 1),
            ),
        ):
            response = await client.get("/proveedores")
            assert response.status_code == 200
            assert "Proveedores" in response.text

    async def test_crear_producto_form(self, client):
        with (
            patch(
                "app.routes.pages.producto_repo.crear",
                new_callable=AsyncMock,
                return_value=Producto(
                    id="new001", nombre="Test", id_proveedor="prov001",
                    stock_actual=10, costo_unitario=5.0,
                    costo_almacenamiento_anual=1.0, demanda_anual_estimada=100,
                ),
            ),
        ):
            response = await client.post("/productos", data={
                "nombre": "Test",
                "id_proveedor": "prov001",
                "stock_actual": "10",
                "costo_unitario": "5.0",
                "costo_almacenamiento_anual": "1.0",
                "demanda_anual_estimada": "100",
            })
            assert response.status_code == 303
            assert response.headers["location"] == "/productos"

    async def test_crear_proveedor_form(self, client):
        with patch(
            "app.routes.pages.proveedor_repo.crear",
            new_callable=AsyncMock,
            return_value=Proveedor(
                id="new001", nombre="Test Prov", costo_pedido_fijo=50.0,
                lead_time_promedio=5.0,
            ),
        ):
            response = await client.post("/proveedores", data={
                "nombre": "Test Prov",
                "costo_pedido_fijo": "50.0",
                "lead_time_promedio": "5.0",
            })
            assert response.status_code == 303
            assert response.headers["location"] == "/proveedores"

    async def test_ventas_page(self, client):
        with (
            patch(
                "app.routes.pages.venta_repo.listar_paginado",
                new_callable=AsyncMock,
                return_value=([], 0, 1, 1),
            ),
            patch(
                "app.routes.pages.producto_repo.listar_activos",
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            response = await client.get("/ventas")
            assert response.status_code == 200
            assert "Ventas" in response.text

    async def test_crear_venta_form(self, client):
        with patch(
            "app.routes.pages.venta_repo.crear_con_descuento_stock",
            new_callable=AsyncMock,
        ):
            response = await client.post("/ventas", data={
                "id_producto": "prod001",
                "cantidad": "5",
            })
            assert response.status_code == 303
            assert response.headers["location"] == "/ventas"


class TestOptimizacionAPI:
    async def test_obtener_sugerencia_producto_inexistente(self, client):
        with patch(
            "app.routes.optimizacion_routes.producto_repo.obtener_por_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await client.get("/optimizar/prod999")
            assert response.status_code == 404


class TestDashboardAPI:
    async def test_obtener_resumen_dashboard(self, client):
        with (
            patch(
                "app.routes.dashboard_routes.proveedor_repo.contar_activos",
                new_callable=AsyncMock,
                return_value=0,
            ),
            patch(
                "app.routes.dashboard_routes.producto_repo.contar_activos",
                new_callable=AsyncMock,
                return_value=0,
            ),
            patch(
                "app.routes.dashboard_routes.venta_repo.contar",
                new_callable=AsyncMock,
                return_value=0,
            ),
            patch(
                "app.routes.dashboard_routes.venta_repo.listar_ventas_por_mes",
                new_callable=AsyncMock,
                return_value=[],
            ),
            patch(
                "app.routes.dashboard_routes.producto_repo.contar_distribucion_stock",
                new_callable=AsyncMock,
                return_value={"bajo": 0, "medio": 0, "alto": 0},
            ),
        ):
            response = await client.get("/dashboard/resumen")
            assert response.status_code == 200
            data = response.json()
            assert data["total_proveedores"] == 0
            assert data["total_productos"] == 0
            assert data["total_ventas"] == 0
            assert data["distribucion_stock"] == {"bajo": 0, "medio": 0, "alto": 0}
            assert data["ventas_por_mes"] == []
