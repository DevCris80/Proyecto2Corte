from pydantic import BaseModel, Field
from enum import StrEnum
from datetime import date

class EstadoAlerta(StrEnum):
    OPTIMO = "optimo"
    PEDIR_AHORA = "Pedir ahora"
    PROXIMO_PEDIDO = "Proximo pedido"
    URGENTE = "Urgente"

class OrdenSugerida(BaseModel):
    id_producto: str
    nombre_producto: str
    cantidad_eoq: int = Field(..., description="Cantidad optima a pedir (Modelo Wilson)")
    punto_reorden: int = Field(..., description="Nivel de stock que dispara el pedido")
    stock_seguridad: int = Field(..., description="Colchon estadistico para evitar quiebres")
    fecha_sugerida_pedido: date = Field(..., description="Fecha recomendada para realizar el pedido")
    estado_alerta: EstadoAlerta