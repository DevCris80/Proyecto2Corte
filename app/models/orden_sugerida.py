from pydantic import BaseModel, Field
from enum import StrEnum
from datetime import date

class EstadoAlerta(StrEnum):
    OPTIMO = "Óptimo"
    PEDIR_AHORA = "Pedir ahora"
    PROXIMO_PEDIDO = "Próximo pedido"
    URGENTE = "Urgente"

class OrdenSugerida(BaseModel):
    id_producto: str
    nombre_producto: str
    cantidad_eoq: int = Field(..., description="Cantidad óptima a pedir (Modelo Wilson)")
    punto_reorden: int = Field(..., description="Nivel de stock que dispara el pedido")
    stock_seguridad: int = Field(..., description="Colchón estadístico para evitar quiebres")
    fecha_sugerida_pedido: 
    estado_alerta: EstadoAlerta