import math
import pytest
from datetime import date
from app.models.producto import ProductoRespuesta
from app.models.proveedor import ProveedorRespuesta
from app.models.venta_historica import VentaRespuesta
from app.models.orden_sugerida import OrdenSugerida, EstadoAlerta
from app.logic.math import calcular_optimizacion


@pytest.fixture
def producto_base():
    return ProductoRespuesta(
        id="prod001",
        nombre="Producto Test",
        id_proveedor="prov001",
        stock_actual=100,
        costo_unitario=10.0,
        costo_almacenamiento_anual=2.0,
        demanda_anual_estimada=1000,
        estado_activo=True,
    )


@pytest.fixture
def proveedor_base():
    return ProveedorRespuesta(
        id="prov001",
        nombre="Proveedor Test",
        costo_pedido_fijo=50.0,
        lead_time_promedio=5.0,
        desviacion_estandar_lead_time=1.0,
        nivel_servicio_objetivo=0.95,
        estado_activo=True,
    )


@pytest.fixture
def ventas_varias():
    return [
        VentaRespuesta(
            id="v1", id_producto="prod001", cantidad=10, fecha_venta=date(2025, 1, 1)
        ),
        VentaRespuesta(
            id="v2", id_producto="prod001", cantidad=12, fecha_venta=date(2025, 1, 15)
        ),
        VentaRespuesta(
            id="v3", id_producto="prod001", cantidad=8, fecha_venta=date(2025, 2, 1)
        ),
        VentaRespuesta(
            id="v4", id_producto="prod001", cantidad=15, fecha_venta=date(2025, 2, 15)
        ),
        VentaRespuesta(
            id="v5", id_producto="prod001", cantidad=11, fecha_venta=date(2025, 3, 1)
        ),
    ]


@pytest.fixture
def ventas_pocas():
    return [
        VentaRespuesta(
            id="v1", id_producto="prod001", cantidad=10, fecha_venta=date(2025, 1, 1)
        ),
        VentaRespuesta(
            id="v2", id_producto="prod001", cantidad=12, fecha_venta=date(2025, 1, 15)
        ),
    ]


class TestEOQ:
    def test_eoq_calculo_basico(self, producto_base, proveedor_base, ventas_varias):
        resultado = calcular_optimizacion(producto_base, proveedor_base, ventas_varias)
        eoq_esperado = 224
        assert resultado.cantidad_eoq == eoq_esperado

    def test_eoq_con_diferentes_costos(self, proveedor_base, ventas_varias):
        producto = ProductoRespuesta(
            id="prod002",
            nombre="Producto EOQ",
            id_proveedor="prov001",
            stock_actual=50,
            costo_unitario=10.0,
            costo_almacenamiento_anual=1.0,
            demanda_anual_estimada=2000,
            estado_activo=True,
        )
        resultado = calcular_optimizacion(producto, proveedor_base, ventas_varias)
        assert resultado.cantidad_eoq > 0


class TestStockSeguridad:
    def test_stock_seguridad_con_pocas_ventas(
        self, producto_base, proveedor_base, ventas_pocas
    ):
        resultado = calcular_optimizacion(producto_base, proveedor_base, ventas_pocas)
        assert resultado.stock_seguridad >= 0
        demanda_diaria = 22 / 2 
        esperado_minimo = 0.20 * demanda_diaria * proveedor_base.lead_time_promedio
        assert resultado.stock_seguridad >= math.ceil(esperado_minimo)

    def test_stock_seguridad_con_muchas_ventas(
        self, producto_base, proveedor_base, ventas_varias
    ):
        resultado = calcular_optimizacion(producto_base, proveedor_base, ventas_varias)
        assert resultado.stock_seguridad >= 0

    def test_stock_seguridad_sin_ventas(self, producto_base, proveedor_base):
        resultado = calcular_optimizacion(producto_base, proveedor_base, [])
        assert resultado.stock_seguridad >= 0


class TestAlertas:
    def test_alerta_urgente(self, proveedor_base, ventas_varias):
        producto = ProductoRespuesta(
            id="prod003",
            nombre="Stock Bajo",
            id_proveedor="prov001",
            stock_actual=5,
            costo_unitario=10.0,
            costo_almacenamiento_anual=2.0,
            demanda_anual_estimada=1000,
            estado_activo=True,
        )
        resultado = calcular_optimizacion(producto, proveedor_base, ventas_varias)
        assert resultado.estado_alerta == EstadoAlerta.URGENTE

    def test_alerta_pedir_ahora(self, proveedor_base, ventas_varias):
        producto = ProductoRespuesta(
            id="prod004",
            nombre="Stock Medio",
            id_proveedor="prov001",
            stock_actual=50,
            costo_unitario=10.0,
            costo_almacenamiento_anual=2.0,
            demanda_anual_estimada=1000,
            estado_activo=True,
        )
        resultado = calcular_optimizacion(producto, proveedor_base, ventas_varias)
        assert resultado.estado_alerta == EstadoAlerta.PEDIR_AHORA

    def test_alerta_proximo_pedido(self, proveedor_base, ventas_varias):
        producto = ProductoRespuesta(
            id="prod005",
            nombre="Stock Proximo",
            id_proveedor="prov001",
            stock_actual=90,
            costo_unitario=10.0,
            costo_almacenamiento_anual=2.0,
            demanda_anual_estimada=1000,
            estado_activo=True,
        )
        resultado = calcular_optimizacion(producto, proveedor_base, ventas_varias)
        assert resultado.estado_alerta == EstadoAlerta.PROXIMO_PEDIDO

    def test_alerta_optimo(self, proveedor_base, ventas_varias):
        producto = ProductoRespuesta(
            id="prod006",
            nombre="Stock Alto",
            id_proveedor="prov001",
            stock_actual=200,
            costo_unitario=10.0,
            costo_almacenamiento_anual=2.0,
            demanda_anual_estimada=1000,
            estado_activo=True,
        )
        resultado = calcular_optimizacion(producto, proveedor_base, ventas_varias)
        assert resultado.estado_alerta == EstadoAlerta.OPTIMO


class TestPuntoReorden:
    def test_punto_reorden_calculado(
        self, producto_base, proveedor_base, ventas_varias
    ):
        resultado = calcular_optimizacion(producto_base, proveedor_base, ventas_varias)
        demanda_diaria = 56 / 5
        punto_esperado = math.ceil(
            demanda_diaria * proveedor_base.lead_time_promedio
            + resultado.stock_seguridad
        )
        assert resultado.punto_reorden == punto_esperado
        assert resultado.punto_reorden >= resultado.stock_seguridad


class TestCamposRespuesta:
    def test_respuesta_tiene_id_producto(
        self, producto_base, proveedor_base, ventas_varias
    ):
        resultado = calcular_optimizacion(producto_base, proveedor_base, ventas_varias)
        assert resultado.id_producto == producto_base.id

    def test_respuesta_tiene_nombre_producto(
        self, producto_base, proveedor_base, ventas_varias
    ):
        resultado = calcular_optimizacion(producto_base, proveedor_base, ventas_varias)
        assert resultado.nombre_producto == producto_base.nombre

    def test_respuesta_tiene_fecha_sugerida(
        self, producto_base, proveedor_base, ventas_varias
    ):
        resultado = calcular_optimizacion(producto_base, proveedor_base, ventas_varias)
        assert str(resultado.fecha_sugerida_pedido) == str(date.today())
