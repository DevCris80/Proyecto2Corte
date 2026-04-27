import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parent.parent
os.chdir(ROOT_DIR)

from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def temp_csv_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_csv_paths(temp_csv_dir):
    rutas = {
        "RUTA_ARCHIVO_PROVEEDOR": os.path.join(temp_csv_dir, "proveedores.csv"),
        "RUTA_ARCHIVO_PRODUCTOS": os.path.join(temp_csv_dir, "productos.csv"),
        "RUTA_ARCHIVO_VENTAS": os.path.join(temp_csv_dir, "ventas.csv"),
    }
    return rutas


@pytest.fixture
def setup_proveedor(mock_csv_paths):
    from app.models.proveedor import ProveedorRespuesta
    from app.repository.csv_orm import guardar_csv

    proveedor = ProveedorRespuesta(
        id="prov001",
        nombre="Proveedor Test",
        costo_pedido_fijo=50.0,
        lead_time_promedio=5.0,
        desviacion_estandar_lead_time=1.0,
        nivel_servicio_objetivo=0.95,
        estado_activo=True,
    )
    guardar_csv(proveedor, mock_csv_paths["RUTA_ARCHIVO_PROVEEDOR"])
    return mock_csv_paths


@pytest.fixture
def setup_producto(mock_csv_paths, setup_proveedor):
    from app.models.producto import ProductoRespuesta
    from app.repository.csv_orm import guardar_csv

    producto = ProductoRespuesta(
        id="prod001",
        nombre="Producto Test",
        id_proveedor="prov001",
        stock_actual=100,
        costo_unitario=10.0,
        costo_almacenamiento_anual=2.0,
        demanda_anual_estimada=1000,
        estado_activo=True,
    )
    guardar_csv(producto, mock_csv_paths["RUTA_ARCHIVO_PRODUCTOS"])
    return mock_csv_paths


class TestProveedoresAPI:
    def test_listar_proveedores_vacios(self, client, mock_csv_paths):
        with patch(
            "app.routes.proveedores_routes.RUTA_ARCHIVO_PROVEEDOR",
            mock_csv_paths["RUTA_ARCHIVO_PROVEEDOR"],
        ):
            response = client.get("/proveedores")
            assert response.status_code == 200
            assert response.json() == []

    def test_crear_proveedor(self, client, mock_csv_paths):
        with patch(
            "app.routes.proveedores_routes.RUTA_ARCHIVO_PROVEEDOR",
            mock_csv_paths["RUTA_ARCHIVO_PROVEEDOR"],
        ):
            data = {
                "nombre": "Nuevo Proveedor",
                "costo_pedido_fijo": 100.0,
                "lead_time_promedio": 7.0,
            }
            response = client.post("/proveedores", json=data)
            assert response.status_code == 201
            assert response.json()["nombre"] == "Nuevo Proveedor"
            assert "id" in response.json()

    def test_crear_proveedor_datos_invalidos(self, client, mock_csv_paths):
        with patch(
            "app.routes.proveedores_routes.RUTA_ARCHIVO_PROVEEDOR",
            mock_csv_paths["RUTA_ARCHIVO_PROVEEDOR"],
        ):
            data = {
                "nombre": "Proveedor Invalido",
                "costo_pedido_fijo": 0,
                "lead_time_promedio": 5.0,
            }
            response = client.post("/proveedores", json=data)
            assert response.status_code == 422


class TestProductosAPI:
    def test_listar_productos_vacios(self, client, mock_csv_paths):
        with patch(
            "app.routes.productos_routes.RUTA_ARCHIVO_PRODUCTOS",
            mock_csv_paths["RUTA_ARCHIVO_PRODUCTOS"],
        ):
            with patch(
                "app.routes.productos_routes.RUTA_ARCHIVO_PROVEEDOR",
                mock_csv_paths["RUTA_ARCHIVO_PROVEEDOR"],
            ):
                response = client.get("/productos")
                assert response.status_code == 200
                assert response.json() == []

    def test_crear_producto_sin_proveedor(self, client, mock_csv_paths):
        with patch(
            "app.routes.productos_routes.RUTA_ARCHIVO_PRODUCTOS",
            mock_csv_paths["RUTA_ARCHIVO_PRODUCTOS"],
        ):
            with patch(
                "app.routes.productos_routes.RUTA_ARCHIVO_PROVEEDOR",
                mock_csv_paths["RUTA_ARCHIVO_PROVEEDOR"],
            ):
                data = {
                    "nombre": "Producto Sin Proveedor",
                    "id_proveedor": "prov999",
                    "stock_actual": 50,
                    "costo_unitario": 10.0,
                    "costo_almacenamiento_anual": 2.0,
                    "demanda_anual_estimada": 500,
                }
                response = client.post("/productos", json=data)
                assert response.status_code == 404

    def test_crear_producto_valido(self, client, setup_proveedor):
        from app.routes.productos_routes import (
            RUTA_ARCHIVO_PRODUCTOS,
            RUTA_ARCHIVO_PROVEEDOR,
        )

        with patch(
            "app.routes.productos_routes.RUTA_ARCHIVO_PRODUCTOS",
            setup_proveedor["RUTA_ARCHIVO_PRODUCTOS"],
        ):
            with patch(
                "app.routes.productos_routes.RUTA_ARCHIVO_PROVEEDOR",
                setup_proveedor["RUTA_ARCHIVO_PROVEEDOR"],
            ):
                data = {
                    "nombre": "Producto Valido",
                    "id_proveedor": "prov001",
                    "stock_actual": 50,
                    "costo_unitario": 10.0,
                    "costo_almacenamiento_anual": 2.0,
                    "demanda_anual_estimada": 500,
                }
                response = client.post("/productos", json=data)
                assert response.status_code == 201
                assert response.json()["nombre"] == "Producto Valido"

    def test_crear_producto_stock_negativo_falla(self, client, setup_proveedor):
        with patch(
            "app.routes.productos_routes.RUTA_ARCHIVO_PRODUCTOS",
            setup_proveedor["RUTA_ARCHIVO_PRODUCTOS"],
        ):
            with patch(
                "app.routes.productos_routes.RUTA_ARCHIVO_PROVEEDOR",
                setup_proveedor["RUTA_ARCHIVO_PROVEEDOR"],
            ):
                data = {
                    "nombre": "Producto Invalido",
                    "id_proveedor": "prov001",
                    "stock_actual": -10,
                    "costo_unitario": 10.0,
                    "costo_almacenamiento_anual": 2.0,
                    "demanda_anual_estimada": 500,
                }
                response = client.post("/productos", json=data)
                assert response.status_code == 422


class TestVentasAPI:
    def test_registrar_venta_producto_inexistente(self, client, mock_csv_paths):
        with patch(
            "app.routes.ventas_routes.RUTA_ARCHIVO_PRODUCTOS",
            mock_csv_paths["RUTA_ARCHIVO_PRODUCTOS"],
        ):
            with patch(
                "app.routes.ventas_routes.RUTA_ARCHIVO_VENTAS",
                mock_csv_paths["RUTA_ARCHIVO_VENTAS"],
            ):
                data = {"id_producto": "prod999", "cantidad": 5}
                response = client.post("/ventas", json=data)
                assert response.status_code == 404

    def test_registrar_venta_stock_insuficiente(self, client, setup_producto):
        from app.routes.ventas_routes import RUTA_ARCHIVO_PRODUCTOS, RUTA_ARCHIVO_VENTAS

        with patch(
            "app.routes.ventas_routes.RUTA_ARCHIVO_PRODUCTOS",
            setup_producto["RUTA_ARCHIVO_PRODUCTOS"],
        ):
            with patch(
                "app.routes.ventas_routes.RUTA_ARCHIVO_VENTAS",
                setup_producto["RUTA_ARCHIVO_VENTAS"],
            ):
                data = {"id_producto": "prod001", "cantidad": 200}
                response = client.post("/ventas", json=data)
                assert response.status_code == 400

    def test_registrar_venta_exitosa(self, client, setup_producto):
        from app.routes.ventas_routes import RUTA_ARCHIVO_PRODUCTOS, RUTA_ARCHIVO_VENTAS

        with patch(
            "app.routes.ventas_routes.RUTA_ARCHIVO_PRODUCTOS",
            setup_producto["RUTA_ARCHIVO_PRODUCTOS"],
        ):
            with patch(
                "app.routes.ventas_routes.RUTA_ARCHIVO_VENTAS",
                setup_producto["RUTA_ARCHIVO_VENTAS"],
            ):
                data = {"id_producto": "prod001", "cantidad": 10}
                response = client.post("/ventas", json=data)
                assert response.status_code == 201
                assert "id" in response.json()


class TestOptimizacionAPI:
    def test_obtener_sugerencia_producto_inexistente(self, client, mock_csv_paths):
        with patch(
            "app.routes.optimizacion_routes.RUTA_ARCHIVO_PRODUCTOS",
            mock_csv_paths["RUTA_ARCHIVO_PRODUCTOS"],
        ):
            with patch(
                "app.routes.optimizacion_routes.RUTA_ARCHIVO_PROVEEDOR",
                mock_csv_paths["RUTA_ARCHIVO_PROVEEDOR"],
            ):
                with patch(
                    "app.routes.optimizacion_routes.RUTA_ARCHIVO_VENTAS",
                    mock_csv_paths["RUTA_ARCHIVO_VENTAS"],
                ):
                    response = client.get("/optimizar/prod999")
                    assert response.status_code == 404


class TestRootAPI:
    def test_raiz(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "Saludo" in response.json()
