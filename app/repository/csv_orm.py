import csv
import os

from app.models.proveedor import ProveedorRespuesta

RUTA_ARCHIVO_PROVEEDOR = "data/proveedores.csv"
RUTA_ARCHIVO_PRODUCTOS = ""
RUTA_ARCHIVO_VENTAS = ""

def guardar_proveedor(proveedor: ProveedorRespuesta):
    archivo_existe = os.path.exists(RUTA_ARCHIVO_PROVEEDOR) 