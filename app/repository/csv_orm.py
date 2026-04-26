import os
import csv
from typing import Type
from pydantic import BaseModel

def guardar_csv(objeto: Type[BaseModel], ruta_archivo: str):
    archivo_existe = os.path.exists(ruta_archivo)

    datos = objeto.model_dump()
    campos = list(datos.keys())

    with open(file=ruta_archivo, mode="a+", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=campos)

        if not archivo_existe:
            writer.writeheader()

        writer.writerow(datos)

def listar_csv(objeto: Type[BaseModel], ruta_archivo: str):
    if not os.path.isfile(ruta_archivo):
        return

    with open(file=ruta_archivo, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for fila in reader:
            yield objeto(**fila)

def eliminar_csv(id_registro: str, ruta_archivo: str):
    if not os.path.isfile(ruta_archivo):
        return False

    registros_actualizados = []
    registro_encontrado = False
    campos = []

    with open(file=ruta_archivo, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        campos = reader.fieldnames
        
        for fila in reader:
            if fila.get("id") == id_registro:
                fila["estado_activo"] = "False"
                registro_encontrado = True
            
            registros_actualizados.append(fila)

    if not registro_encontrado:
        return False

    with open(file=ruta_archivo, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=campos)
        writer.writeheader()
        writer.writerows(registros_actualizados)

    return True

def actualizar_csv(objeto_id: str, campo_id: str, nuevos_datos: BaseModel, ruta_archivo: str):
    if not os.path.isfile(ruta_archivo):
        return False

    filas = []
    actualizado = False
    campos = []

    with open(file=ruta_archivo, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        campos = reader.fieldnames

        for fila in reader:
            if fila.get(campo_id) == str(objeto_id):
                datos_a_actualizar = nuevos_datos.model_dump(exclude_unset=True)
                
                datos_a_actualizar_str = {k: str(v) for k, v in datos_a_actualizar.items()}
                
                fila.update(datos_a_actualizar_str)
                actualizado = True

            filas.append(fila)

    if not actualizado:
        return False

    with open(file=ruta_archivo, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=campos)
        writer.writeheader()
        writer.writerows(filas)

    return True