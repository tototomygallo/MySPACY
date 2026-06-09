import os
import pandas as pd
from LSM.LIWC import computar_LSM_LIWC

# 1. Definir rutas originales
ruta_original = "/home/tgallo/Documents/Proyecto_modular/negaciones.csv"
carpeta_output = "/home/tgallo/Documents/Proyecto_modular/pruebitas_cat/"

# Crear la carpeta de salida si no existe
os.makedirs(carpeta_output, exist_ok=True)

# 2. Definir ruta para el archivo temporal con header
ruta_temporal = "/home/tgallo/Documents/Proyecto_modular/negaciones_con_header.csv"

try:
    # 3. Leer el archivo original
    with open(ruta_original, "r", encoding="utf-8") as f:
        lineas_dialogo = f.readlines()

    # 4. Escribir el nuevo archivo inyectando el header obligatorio
    with open(ruta_temporal, "w", encoding="utf-8") as f_nuevo:
        f_nuevo.write("id:text\n")  # Encabezado para LIWC
        f_nuevo.writelines(lineas_dialogo)

    print("Header inyectado con éxito. Ejecutando LIWC...")

    # 5. Correr LIWC apuntando al archivo temporal
    computar_LSM_LIWC(ruta_temporal, carpeta_output)

finally:
    # 6. Limpieza: Borramos el archivo temporal para no ensuciar tu directorio
    if os.path.exists(ruta_temporal):
        os.remove(ruta_temporal)
        print("Limpieza completada: archivo temporal eliminado.")