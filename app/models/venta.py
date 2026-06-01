from datetime import date
from sqlmodel import Field, SQLModel


class VentaBase(SQLModel):
    id_producto: str = Field(foreign_key="productos.id")
    cantidad: int = Field(gt=0)
    fecha_venta: date = Field(default_factory=date.today)


class Venta(VentaBase, table=True):
    __tablename__ = "ventas"
    id: str = Field(primary_key=True)


class VentaCreate(VentaBase):
    pass


class VentaPublic(VentaBase):
    id: str
