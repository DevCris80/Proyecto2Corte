from fastapi import APIRouter, HTTPException, Query
import uuid

from app.models.producto import ProductoCrear, ProductoRespuesta, ProductoActualizar
from app.repository.csv_orm import eliminar_csv, guardar_csv, listar_csv, actualizar_csv
from app.core.config import RUTA_ARCHIVO_PRODUCTOS, RUTA_ARCHIVO_PROVEEDOR

router = APIRouter(prefix="/productos", tags=["productos"])

@router.post("", response_model=ProductoRespuesta, status_code=201)
def crear_producto(producto: ProductoCrear):
    try:
        proveedores = list(listar_csv(ProductoRespuesta, RUTA_ARCHIVO_PROVEEDOR))
        if not any(p.id == producto.id_proveedor and p.estado_activo for p in proveedores):
            raise HTTPException(status_code=404, detail="Proveedor no encontrado o inactivo")

        nuevo_id = str(uuid.uuid4())[:8]

        diccionario_producto = producto.model_dump()
        diccionario_producto["id"] = nuevo_id
        diccionario_producto["estado_activo"] = True

        producto_nuevo = ProductoRespuesta(**diccionario_producto)

        guardar_csv(producto_nuevo, RUTA_ARCHIVO_PRODUCTOS)

        return producto_nuevo
    except IOError:
        raise HTTPException(status_code=500, detail="Error de escritura en el archivo CSV")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(error)}")


@router.get("", response_model=list[ProductoRespuesta], status_code=200)
def listar_productos(estado: bool = Query(None, description="Filtrar por estado activo")):
    try:
        productos = list(listar_csv(ProductoRespuesta, RUTA_ARCHIVO_PRODUCTOS))

        if estado is not None:
            productos = [p for p in productos if p.estado_activo == estado]

        return productos
    except IOError:
        raise HTTPException(status_code=500, detail="Error de lectura en el archivo CSV")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(error)}")

@router.get("/buscar/", response_model=list[ProductoRespuesta], status_code=200)
def buscar_productos(nombre: str = Query(..., description="Nombre del producto a buscar")):
    try:
        productos = list(listar_csv(ProductoRespuesta, RUTA_ARCHIVO_PRODUCTOS))

        productos_encontrados = [p for p in productos if nombre.lower() in p.nombre.lower() and p.estado_activo]

        return productos_encontrados
    except IOError:
        raise HTTPException(status_code=500, detail="Error de lectura en el archivo CSV")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(error)}")

@router.delete("/{id}", status_code=204)
def eliminar_producto(id: str):
    try:
        exito = eliminar_csv(id_registro=id, ruta_archivo=RUTA_ARCHIVO_PRODUCTOS)
        if not exito:
            raise HTTPException(status_code=404, detail="ID no encontrado")
        return {"mensaje": "Borrado exitoso"}
    except IOError:
        raise HTTPException(status_code=500, detail="Error de escritura en el archivo CSV")
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error en el proceso: {str(error)}")

@router.patch("/{id}", response_model=ProductoRespuesta, status_code=200)
def actualizar_producto(id: str, producto: ProductoActualizar):
    datos_recibidos = producto.model_dump(exclude_unset=True)
    if not datos_recibidos:
        raise HTTPException(
            status_code=400, 
            detail="La peticion PATCH esta vacia. Debe enviar al menos un atributo valido."
        )

    exito = actualizar_csv(objeto_id=id, campo_id="id", nuevos_datos=producto, ruta_archivo=RUTA_ARCHIVO_PRODUCTOS)

    if not exito:
        raise HTTPException(status_code=404, detail=f"Error: El producto con ID {id} no fue encontrado.")

    return {
        "mensaje": "Producto actualizado correctamente",
        "campos_modificados": list(datos_recibidos.keys())
    }