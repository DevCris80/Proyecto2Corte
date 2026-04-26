from fastapi import APIRouter, HTTPException
import uuid

from app.models.proveedor import ProveedorActualizar, ProveedorCrear, ProveedorRespuesta
from app.repository.csv_orm import guardar_csv, listar_csv, eliminar_csv, actualizar_csv
from app.core.config import RUTA_ARCHIVO_PROVEEDOR

router = APIRouter(prefix="/proveedores", tags=["proveedores"])

@router.post("", response_model=ProveedorRespuesta, status_code=201)
def crear_proveedor(proveedor: ProveedorCrear):
    try:
        nuevo_id = str(uuid.uuid4())[:8]

        diccionario_proveedor = proveedor.model_dump()
        diccionario_proveedor["id"] = nuevo_id
        diccionario_proveedor["estado_activo"] = True

        proveedor_nuevo = ProveedorRespuesta(**diccionario_proveedor)

        guardar_csv(proveedor_nuevo, RUTA_ARCHIVO_PROVEEDOR)

        return proveedor_nuevo
    except IOError:
        raise HTTPException(status_code=500, detail="Error de escritura en el archivo CSV")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(error)}")

@router.get("", response_model=list[ProveedorRespuesta], status_code=200)
def listar_proveedores():
    try:
        proveedores = list(listar_csv(ProveedorRespuesta, RUTA_ARCHIVO_PROVEEDOR))

        return [p for p in proveedores if p.estado_activo]
    except IOError:
        raise HTTPException(status_code=500, detail="Error de lectura en el archivo CSV")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(error)}")

@router.patch("/{id}", response_model=ProveedorRespuesta, status_code=200)
def actualizar_proveedor(id_producto: str, proveedor: ProveedorActualizar):
    datos_recibidos = id_producto.model_dump(exclude_unset=True)
    if not datos_recibidos:
        raise HTTPException(
            status_code=400, 
            detail="La peticion PATCH esta vacia. Debe enviar al menos un atributo valido."
        )

    exito = actualizar_csv(objeto_id=id_producto, campo_id="id", nuevos_datos=id_producto, ruta_archivo=RUTA_ARCHIVO_PROVEEDOR)

    if not exito:
        raise HTTPException(status_code=404, detail=f"Error: El producto con ID {id_producto} no fue encontrado.")

    return {
        "mensaje": "Producto actualizado correctamente",
        "campos_modificados": list(datos_recibidos.keys())
    }

@router.delete("/{id}", status_code=204)
def eliminar_proveedor(id: str):
    exito = eliminar_csv(id_registro=id, ruta_archivo=RUTA_ARCHIVO_PROVEEDOR)
    if not exito:
        raise HTTPException(status_code=404, detail="ID no encontrado")
    return {"mensaje": "Borrado exitoso"}