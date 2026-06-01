import pytest
from contextlib import asynccontextmanager
from datetime import date
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from main import app
from app.models.producto import Producto
from app.models.proveedor import Proveedor
from app.models.venta import Venta
from app.models.orden_sugerida import OrdenSugerida, EstadoAlerta


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


class TestProveedoresAPI:
    async def test_listar_proveedores_vacios(self, client):
        with patch(
            "app.routes.proveedores_routes.proveedor_repo.listar_activos",
            new_callable=AsyncMock,
            return_value=[],
        ):
            response = await client.get("/proveedores")
            assert response.status_code == 200
            assert response.json() == []

    async def test_crear_proveedor(self, client):
        mock_proveedor = Proveedor(
            id="abc12345",
            nombre="Nuevo Proveedor",
            costo_pedido_fijo=100.0,
            lead_time_promedio=7.0,
            estado_activo=True,
        )
        with patch(
            "app.routes.proveedores_routes.proveedor_repo.crear",
            new_callable=AsyncMock,
            return_value=mock_proveedor,
        ):
            data = {
                "nombre": "Nuevo Proveedor",
                "costo_pedido_fijo": 100.0,
                "lead_time_promedio": 7.0,
            }
            response = await client.post("/proveedores", json=data)
            assert response.status_code == 201
            assert response.json()["nombre"] == "Nuevo Proveedor"
            assert "id" in response.json()

    async def test_crear_proveedor_datos_invalidos(self, client):
        data = {
            "nombre": "Proveedor Invalido",
            "costo_pedido_fijo": 0,
            "lead_time_promedio": 5.0,
        }
        response = await client.post("/proveedores", json=data)
        assert response.status_code == 422


class TestProductosAPI:
    async def test_listar_productos_vacios(self, client):
        with (
            patch(
                "app.routes.productos_routes.producto_repo.listar",
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            response = await client.get("/productos")
            assert response.status_code == 200
            assert response.json() == []

    async def test_crear_producto_sin_proveedor(self, client, proveedor_mock):
        with patch(
            "app.routes.productos_routes.proveedor_repo.obtener_por_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            data = {
                "nombre": "Producto Sin Proveedor",
                "id_proveedor": "prov999",
                "stock_actual": 50,
                "costo_unitario": 10.0,
                "costo_almacenamiento_anual": 2.0,
                "demanda_anual_estimada": 500,
            }
            response = await client.post("/productos", json=data)
            assert response.status_code == 404

    async def test_crear_producto_valido(self, client, proveedor_mock, producto_mock):
        with (
            patch(
                "app.routes.productos_routes.proveedor_repo.obtener_por_id",
                new_callable=AsyncMock,
                return_value=proveedor_mock,
            ),
            patch(
                "app.routes.productos_routes.producto_repo.listar_activos",
                new_callable=AsyncMock,
                return_value=[],
            ),
            patch(
                "app.routes.productos_routes.producto_repo.crear",
                new_callable=AsyncMock,
                return_value=producto_mock,
            ),
        ):
            data = {
                "nombre": "Producto Valido",
                "id_proveedor": "prov001",
                "stock_actual": 50,
                "costo_unitario": 10.0,
                "costo_almacenamiento_anual": 2.0,
                "demanda_anual_estimada": 500,
            }
            response = await client.post("/productos", json=data)
            assert response.status_code == 201
            assert response.json()["nombre"] == "Producto Test"

    async def test_crear_producto_stock_negativo_falla(self, client):
        data = {
            "nombre": "Producto Invalido",
            "id_proveedor": "prov001",
            "stock_actual": -10,
            "costo_unitario": 10.0,
            "costo_almacenamiento_anual": 2.0,
            "demanda_anual_estimada": 500,
        }
        response = await client.post("/productos", json=data)
        assert response.status_code == 422


class TestVentasAPI:
    async def test_registrar_venta_producto_inexistente(self, client):
        with patch(
            "app.routes.ventas_routes.producto_repo.obtener_por_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            data = {"id_producto": "prod999", "cantidad": 5}
            response = await client.post("/ventas", json=data)
            assert response.status_code == 404

    async def test_registrar_venta_stock_insuficiente(self, client, producto_mock):
        with patch(
            "app.routes.ventas_routes.producto_repo.obtener_por_id",
            new_callable=AsyncMock,
            return_value=producto_mock,
        ):
            data = {"id_producto": "prod001", "cantidad": 200}
            response = await client.post("/ventas", json=data)
            assert response.status_code == 400

    async def test_registrar_venta_exitosa(self, client, producto_mock):
        venta_mock = Venta(
            id="vta001", id_producto="prod001", cantidad=10, fecha_venta=date.today()
        )
        with (
            patch(
                "app.routes.ventas_routes.producto_repo.obtener_por_id",
                new_callable=AsyncMock,
                return_value=producto_mock,
            ),
            patch(
                "app.routes.ventas_routes.venta_repo.crear_con_descuento_stock",
                new_callable=AsyncMock,
                return_value=venta_mock,
            ),
        ):
            data = {"id_producto": "prod001", "cantidad": 10}
            response = await client.post("/ventas", json=data)
            assert response.status_code == 201
            assert "id" in response.json()


class TestOptimizacionAPI:
    async def test_obtener_sugerencia_producto_inexistente(self, client):
        with patch(
            "app.routes.optimizacion_routes.producto_repo.obtener_por_id",
            new_callable=AsyncMock,
            return_value=None,
        ):
            response = await client.get("/optimizar/prod999")
            assert response.status_code == 404


class TestRootAPI:
    async def test_raiz(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        assert "Saludo" in response.json()

class TestDashboardAPI:
    async def test_obtener_resumen_dashboard(self, client):
        with (
            patch(
                "app.routes.dashboard_routes.proveedor_repo.listar_activos",
                new_callable=AsyncMock,
                return_value=[],
            ),
            patch(
                "app.routes.dashboard_routes.producto_repo.listar_activos",
                new_callable=AsyncMock,
                return_value=[],
            ),
            patch(
                "app.routes.dashboard_routes.venta_repo.listar",
                new_callable=AsyncMock,
                return_value=[],
            )
        ):
            response = await client.get("/dashboard/resumen")
            assert response.status_code == 200
            data = response.json()
            assert data["total_proveedores"] == 0
            assert data["total_productos"] == 0
            assert data["total_ventas"] == 0
            assert data["distribucion_stock"] == {"bajo": 0, "medio": 0, "alto": 0}
            assert data["ventas_por_mes"] == []
