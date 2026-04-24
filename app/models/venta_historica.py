from pydantic import BaseModel, Field
from datetime import date
import uuid

class VentaBase(BaseModel):
    id_producto: str
    cantidad: int = Field(..., gt=0)
    fecha_venta: date = Field(default_factory=date.today) 

class VentaCreate(VentaBase):
    pass

class VentaResponse(VentaBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))