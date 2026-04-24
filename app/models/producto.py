from pydantic import BaseModel, Field

class ProductoBase(BaseModel):
    nombre: str
    id_proveedor: str
    stock_actual: int = Field(..., ge=0)
    costo_unitario: float = Field(..., gt=0)
    costo_almacenamiento_anual: float = Field(..., gt=0, description="Costo de tener una unidad guardada un año")
    demanda_anual_estimada: float = Field(..., gt=0)

class ProductoCreate(ProductoBase):
    id: str

class ProductoRespuesta(ProductoBase):
    id: str
    estado_activo: bool