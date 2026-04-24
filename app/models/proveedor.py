from pydantic import BaseModel, Field

class ProveedorBase(BaseModel):
    nombre: str
    costo_pedido_fijo: float = Field(..., gt=0, description="Costo por pedido")
    lead_time_promedio: float = Field(..., gt=0, description="Dias promedio de entrega")
    desviacion_estandar_lead_time: float = Field(default=0.0, description="Variabilidad en dias de entrega")
    nivel_servicio_objetivo: float = Field(default=0.95, ge=0.8, le=0.99)

class ProveedorCrear(ProveedorBase):
    id: str

class ProveedorRespuesta(ProveedorBase):
    id: int
    estado_activo: bool
    
    
