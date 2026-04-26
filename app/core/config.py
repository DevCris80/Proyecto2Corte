from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"

RUTA_ARCHIVO_PROVEEDOR = DATA_DIR / "proveedores.csv"
RUTA_ARCHIVO_PRODUCTOS = DATA_DIR / "productos.csv"
RUTA_ARCHIVO_VENTAS = DATA_DIR / "ventas.csv"