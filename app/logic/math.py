import math
import statistics
from datetime import date
from typing import List
from app.models.producto import ProductoRespuesta
from app.models.proveedor import ProveedorRespuesta
from app.models.venta_historica import VentaRespuesta
from app.models.orden_sugerida import OrdenSugerida, EstadoAlerta

def calcular_optimizacion(
    producto: ProductoRespuesta, 
    proveedor: ProveedorRespuesta, 
    historico_ventas: List[VentaRespuesta]
) -> OrdenSugerida:
    
    ventas_cantidades = [v.cantidad for v in historico_ventas]
    n_ventas = len(ventas_cantidades)

    demanda_diaria = sum(ventas_cantidades) / max(n_ventas, 1)
    demanda_anual = producto.demanda_anual_estimada

    numerador_eoq = 2 * demanda_anual * proveedor.costo_pedido_fijo
    cantidad_eoq = math.ceil(math.sqrt(numerador_eoq / producto.costo_almacenamiento_anual))

    z_score = 1.645

    if n_ventas < 5:
        stock_seguridad = math.ceil(0.20 * (demanda_diaria * proveedor.lead_time_promedio))
    else:
        desviacion_estandar_demanda = statistics.stdev(ventas_cantidades)
        termino_demanda = proveedor.lead_time_promedio * (desviacion_estandar_demanda ** 2)
        termino_lt = (demanda_diaria ** 2) * (proveedor.desviacion_estandar_lead_time ** 2)
        stock_seguridad = math.ceil(z_score * math.sqrt(termino_demanda + termino_lt))

    punto_reorden = math.ceil((demanda_diaria * proveedor.lead_time_promedio) + stock_seguridad)

    if producto.stock_actual <= (punto_reorden * 0.5):
        alerta = EstadoAlerta.URGENTE
    elif producto.stock_actual <= punto_reorden:
        alerta = EstadoAlerta.PEDIR_AHORA
    elif producto.stock_actual <= (punto_reorden * 1.2):
        alerta = EstadoAlerta.PROXIMO_PEDIDO
    else:
        alerta = EstadoAlerta.OPTIMO

    return OrdenSugerida(
        id_producto=producto.id,
        nombre_producto=producto.nombre,
        cantidad_eoq=cantidad_eoq,
        punto_reorden=punto_reorden,
        stock_seguridad=stock_seguridad,
        fecha_sugerida_pedido=date.today(),
        estado_alerta=alerta
    )