import os
import random
import shutil
from pathlib import Path

# ==========================
# Configuración
# ==========================
RUTA_CGC = Path("/home/tgallo/Documents/Proyecto_modular/CGC-transcripts-v2 (1)/out")
RUTA_MUESTRA = Path("/home/tgallo/Documents/Proyecto_modular/muestra_cgc")

PORCENTAJE_MUESTRA = 1  # 50% de las sesiones
SEED = 42

# ==========================
# Funciones
# ==========================
def obtener_sesion(nombre_archivo: str) -> str:
    """
    Extrae la sesión del nombre del archivo.
    Ejemplo: s01.objects.1.phrases -> s01
             s12.task2.phrases -> s12
    """
    return nombre_archivo.split(".")[0]

def generar_carpeta_muestra_por_sesion():
    rng = random.Random(SEED)
    
    # Crear la carpeta de destino si no existe
    RUTA_MUESTRA.mkdir(parents=True, exist_ok=True)
    
    # 1. Agrupar todos los archivos por su sesión correspondiente
    sesiones_dict = {}
    archivos = [f for f in os.listdir(RUTA_CGC) if f.endswith('.phrases')]
    
    for archivo in archivos:
        sesion = obtener_sesion(archivo)
        if sesion not in sesiones_dict:
            sesiones_dict[sesion] = []
        sesiones_dict[sesion].append(archivo)
        
    sesiones_unicas = sorted(sesiones_dict.keys())
    total_sesiones = len(sesiones_unicas)
    
    # 2. Calcular cuántas sesiones tomar (50%)
    num_sesiones_muestra = max(1, int(total_sesiones * PORCENTAJE_MUESTRA))
    
    # 3. Muestrear las sesiones enteras
    sesiones_elegidas = sorted(rng.sample(sesiones_unicas, num_sesiones_muestra))
    
    print(f"Total de sesiones encontradas en CGC: {total_sesiones}")
    print(f"Sesiones seleccionadas ({len(sesiones_elegidas)}): {', '.join(sesiones_elegidas)}")
    
    # 4. Copiar TODOS los archivos/tareas de esas sesiones elegidas
    archivos_copiados = 0
    for sesion in sesiones_elegidas:
        archivos_de_sesion = sesiones_dict[sesion]
        for nombre_archivo in archivos_de_sesion:
            origen = RUTA_CGC / nombre_archivo
            destino = RUTA_MUESTRA / nombre_archivo
            shutil.copy(origen, destino)
            archivos_copiados += 1
            
    print(f"\n¡Listo! Se copiaron {archivos_copiados} archivos en total pertenecientes a las {len(sesiones_elegidas)} sesiones.")
    print(f"Muestra guardada en: {RUTA_MUESTRA}")

if __name__ == "__main__":
    generar_carpeta_muestra_por_sesion()