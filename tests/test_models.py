import pytest
from datetime import date
from pydantic import ValidationError
from app.models.producto import ProductoCrear, ProductoActualizar, ProductoRespuesta
from app.models.proveedor import ProveedorCrear, ProveedorActualizar, ProveedorRespuesta
from app.models.venta_historica import VentaCrear, VentaRespuesta
from app.models.orden_sugerida import OrdenSugerida, EstadoAlerta


class TestProductoModel:
    def test_producto_crear_valido(self):
        producto = ProductoCrear(
            nombre="Producto Test",
            id_proveedor="prov001",
            stock_actual=100,
            costo_unitario=10.0,
            costo_almacenamiento_anual=2.0,
            demanda_anual_estimada=1000,
        )
        assert producto.nombre == "Producto Test"
        assert producto.stock_actual == 100

    def test_producto_stock_negativo_falla(self):
        with pytest.raises(ValidationError):
            ProductoCrear(
                nombre="Producto Test",
                id_proveedor="prov001",
                stock_actual=-5,
                costo_unitario=10.0,
                costo_almacenamiento_anual=2.0,
                demanda_anual_estimada=1000,
            )

    def test_producto_costo_unitario_cero_falla(self):
        with pytest.raises(ValidationError):
            ProductoCrear(
                nombre="Producto Test",
                id_proveedor="prov001",
                stock_actual=100,
                costo_unitario=0,
                costo_almacenamiento_anual=2.0,
                demanda_anual_estimada=1000,
            )

    def test_producto_costo_almacenamiento_cero_falla(self):
        with pytest.raises(ValidationError):
            ProductoCrear(
                nombre="Producto Test",
                id_proveedor="prov001",
                stock_actual=100,
                costo_unitario=10.0,
                costo_almacenamiento_anual=0,
                demanda_anual_estimada=1000,
            )

    def test_producto_demanda_cero_falla(self):
        with pytest.raises(ValidationError):
            ProductoCrear(
                nombre="Producto Test",
                id_proveedor="prov001",
                stock_actual=100,
                costo_unitario=10.0,
                costo_almacenamiento_anual=2.0,
                demanda_anual_estimada=0,
            )

    def test_producto_actualizar_parcial(self):
        producto = ProductoActualizar(stock_actual=50)
        assert producto.stock_actual == 50
        assert producto.nombre is None
        assert producto.costo_unitario is None

    def test_producto_respuesta_con_id(self):
        producto = ProductoRespuesta(
            id="test123",
            nombre="Producto Test",
            id_proveedor="prov001",
            stock_actual=100,
            costo_unitario=10.0,
            costo_almacenamiento_anual=2.0,
            demanda_anual_estimada=1000,
            estado_activo=True,
        )
        assert producto.id == "test123"
        assert producto.estado_activo is True


class TestProveedorModel:
    def test_proveedor_crear_valido(self):
        proveedor = ProveedorCrear(
            nombre="Proveedor Test", costo_pedido_fijo=50.0, lead_time_promedio=5.0
        )
        assert proveedor.nombre == "Proveedor Test"
        assert proveedor.costo_pedido_fijo == 50.0

    def test_proveedor_default_nivel_servicio(self):
        proveedor = ProveedorCrear(
            nombre="Proveedor Test", costo_pedido_fijo=50.0, lead_time_promedio=5.0
        )
        assert proveedor.nivel_servicio_objetivo == 0.95

    def test_proveedor_costo_pedido_cero_falla(self):
        with pytest.raises(ValidationError):
            ProveedorCrear(
                nombre="Proveedor Test", costo_pedido_fijo=0, lead_time_promedio=5.0
            )

    def test_proveedor_lead_time_cero_falla(self):
        with pytest.raises(ValidationError):
            ProveedorCrear(
                nombre="Proveedor Test", costo_pedido_fijo=50.0, lead_time_promedio=0
            )

    def test_proveedor_nivel_servicio_bajo_falla(self):
        with pytest.raises(ValidationError):
            ProveedorCrear(
                nombre="Proveedor Test",
                costo_pedido_fijo=50.0,
                lead_time_promedio=5.0,
                nivel_servicio_objetivo=0.5,
            )

    def test_proveedor_nivel_servicio_alto_falla(self):
        with pytest.raises(ValidationError):
            ProveedorCrear(
                nombre="Proveedor Test",
                costo_pedido_fijo=50.0,
                lead_time_promedio=5.0,
                nivel_servicio_objetivo=1.0,
            )

    def test_proveedor_actualizar_parcial(self):
        proveedor = ProveedorActualizar(nombre="Nuevo Nombre")
        assert proveedor.nombre == "Nuevo Nombre"
        assert proveedor.costo_pedido_fijo is None

    def test_proveedor_respuesta_con_id(self):
        proveedor = ProveedorRespuesta(
            id="prov001",
            nombre="Proveedor Test",
            costo_pedido_fijo=50.0,
            lead_time_promedio=5.0,
            desviacion_estandar_lead_time=1.0,
            nivel_servicio_objetivo=0.95,
            estado_activo=True,
        )
        assert proveedor.id == "prov001"
        assert proveedor.estado_activo is True


class TestVentaModel:
    def test_venta_crear_valida(self):
        venta = VentaCrear(id_producto="prod001", cantidad=10)
        assert venta.id_producto == "prod001"
        assert venta.cantidad == 10
        assert venta.fecha_venta == date.today()

    def test_venta_crear_con_fecha(self):
        venta = VentaCrear(
            id_producto="prod001", cantidad=10, fecha_venta=date(2025, 1, 15)
        )
        assert venta.fecha_venta == date(2025, 1, 15)

    def test_venta_cantidad_cero_falla(self):
        with pytest.raises(ValidationError):
            VentaCrear(id_producto="prod001", cantidad=0)

    def test_venta_cantidad_negativa_falla(self):
        with pytest.raises(ValidationError):
            VentaCrear(id_producto="prod001", cantidad=-5)

    def test_venta_respuesta_con_id(self):
        venta = VentaRespuesta(
            id="vta001",
            id_producto="prod001",
            cantidad=10,
            fecha_venta=date(2025, 1, 15),
        )
        assert venta.id == "vta001"


class TestOrdenSugeridaModel:
    def test_orden_sugerida_valida(self):
        orden = OrdenSugerida(
            id_producto="prod001",
            nombre_producto="Producto Test",
            cantidad_eoq=50,
            punto_reorden=20,
            stock_seguridad=5,
            fecha_sugerida_pedido=date.today(),
            estado_alerta=EstadoAlerta.OPTIMO,
        )
        assert orden.cantidad_eoq == 50
        assert orden.estado_alerta == EstadoAlerta.OPTIMO

    def test_estado_alerta_enum(self):
        assert EstadoAlerta.OPTIMO == "optimo"
        assert EstadoAlerta.URGENTE == "Urgente"
        assert EstadoAlerta.PEDIR_AHORA == "Pedir ahora"
        assert EstadoAlerta.PROXIMO_PEDIDO == "Proximo pedido"
