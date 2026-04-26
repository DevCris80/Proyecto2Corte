from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class VentaBase(BaseModel):
    id_producto: str
    cantidad: int = Field(..., gt=0)
    fecha_venta: date = Field(default_factory=date.today)


class VentaCrear(VentaBase):
    pass


class VentaActualizar(BaseModel):
    id_producto: Optional[str] = None
    cantidad: Optional[int] = Field(default=None, gt=0)
    fecha_venta: Optional[date] = None


class VentaRespuesta(VentaBase):
    id: str