from typing import Optional
from pydantic import BaseModel, Field


class ProductoBase(BaseModel):
    nombre: str
    id_proveedor: str
    stock_actual: int = Field(..., ge=0)
    costo_unitario: float = Field(..., gt=0)
    costo_almacenamiento_anual: float = Field(
        ...,
        gt=0,
        description="Costo de tener una unidad guardada un año"
    )
    demanda_anual_estimada: float = Field(..., gt=0)


class ProductoCrear(ProductoBase):
    pass

class ProductoActualizar(BaseModel):
    nombre: Optional[str] = None
    id_proveedor: Optional[str] = None
    stock_actual: Optional[int] = Field(default=None, ge=0)
    costo_unitario: Optional[float] = Field(default=None, gt=0)
    costo_almacenamiento_anual: Optional[float] = Field(
        default=None,
        gt=0
    )
    demanda_anual_estimada: Optional[float] = Field(
        default=None,
        gt=0
    )
    estado_activo: Optional[bool] = None


class ProductoRespuesta(ProductoBase):
    id: str
    estado_activo: bool