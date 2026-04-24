from fastapi import APIRouter, HTTPException
import uuid

from app.models.proveedor import ProveedorCrear, ProveedorRespuesta

router = APIRouter(prefix="/proveedores", tags=["proveedores"])

@router.post("", response_model=ProveedorRespuesta, status_code=201)
def crear_proveedor(proveedor: ProveedorCrear):
    try:
        nuevo_id = str(uuid.uuid4())[:8]

        diccionario_proveedor = proveedor.model_dump()
        diccionario_proveedor["id"] = nuevo_id
        diccionario_proveedor["estado_activo"] = True

        proveedor_nuevo = ProveedorRespuesta(**diccionario_proveedor)

        return proveedor_nuevo
    except IOError as error:
        raise HTTPException(status_code=500, detail="Error de escritura en el archivo CSV")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(error)}")