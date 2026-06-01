from typing import Optional
from sqlmodel import Field, SQLModel


class ProductoBase(SQLModel):
    nombre: str
    id_proveedor: str = Field(foreign_key="proveedores.id")
    stock_actual: int = Field(ge=0)
    costo_unitario: float = Field(gt=0)
    costo_almacenamiento_anual: float = Field(gt=0)
    demanda_anual_estimada: float = Field(gt=0)
    imagen_url: Optional[str] = None


class Producto(ProductoBase, table=True):
    __tablename__ = "productos"
    id: str = Field(primary_key=True)
    estado_activo: bool = True


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(SQLModel):
    nombre: Optional[str] = None
    id_proveedor: Optional[str] = None
    stock_actual: Optional[int] = Field(default=None, ge=0)
    costo_unitario: Optional[float] = Field(default=None, gt=0)
    costo_almacenamiento_anual: Optional[float] = Field(default=None, gt=0)
    demanda_anual_estimada: Optional[float] = Field(default=None, gt=0)
    estado_activo: Optional[bool] = None
    imagen_url: Optional[str] = None


class ProductoPublic(ProductoBase):
    id: str
    estado_activo: bool
