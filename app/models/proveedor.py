from typing import Optional
from sqlmodel import Field, SQLModel


class ProveedorBase(SQLModel):
    nombre: str
    costo_pedido_fijo: float = Field(gt=0)
    lead_time_promedio: float = Field(gt=0)
    desviacion_estandar_lead_time: float = 0.0
    nivel_servicio_objetivo: float = Field(default=0.95, ge=0.8, le=0.99)
    imagen_url: Optional[str] = None


class Proveedor(ProveedorBase, table=True):
    __tablename__ = "proveedores"
    id: str = Field(primary_key=True)
    estado_activo: bool = True


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(SQLModel):
    nombre: Optional[str] = None
    costo_pedido_fijo: Optional[float] = Field(default=None, gt=0)
    lead_time_promedio: Optional[float] = Field(default=None, gt=0)
    desviacion_estandar_lead_time: Optional[float] = None
    nivel_servicio_objetivo: Optional[float] = Field(default=None, ge=0.8, le=0.99)
    estado_activo: Optional[bool] = None
    imagen_url: Optional[str] = None


class ProveedorPublic(ProveedorBase):
    id: str
    estado_activo: bool
