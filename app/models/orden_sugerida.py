from enum import StrEnum
from datetime import date
from sqlmodel import Field, SQLModel


class EstadoAlerta(StrEnum):
    OPTIMO = "optimo"
    PEDIR_AHORA = "Pedir ahora"
    PROXIMO_PEDIDO = "Proximo pedido"
    URGENTE = "Urgente"


class OrdenSugerida(SQLModel):
    id_producto: str
    nombre_producto: str
    cantidad_eoq: int = Field(ge=0)
    punto_reorden: int = Field(ge=0)
    stock_seguridad: int = Field(ge=0)
    fecha_sugerida_pedido: date
    estado_alerta: EstadoAlerta
