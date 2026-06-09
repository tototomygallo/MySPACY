import os
import random
import shutil

RUTA_SCOTUS = "/home/tgallo/Documents/Proyecto_modular/scotus-transcripts/out"
# Nueva carpeta para fijar tu muestra del 10%
RUTA_MUESTRA = "/home/tgallo/Documents/Proyecto_modular/muestra_scotus"
PORCENTAJE_MUESTRA = 0.1  # 10%

def generar_carpeta_muestra():
    random.seed(42) # Semilla fija para reproducibilidad
    
    # Crear la carpeta de destino si no existe
    os.makedirs(RUTA_MUESTRA, exist_ok=True)
    
    archivos = [f for f in os.listdir(RUTA_SCOTUS) if f.endswith('.txt')]
    num_muestra = max(1, int(len(archivos) * PORCENTAJE_MUESTRA))
    muestra = random.sample(archivos, num_muestra)
    
    print(f"Copiando {num_muestra} archivos a la carpeta de muestra...")
    
    for nombre_archivo in muestra:
        origen = os.path.join(RUTA_SCOTUS, nombre_archivo)
        destino = os.path.join(RUTA_MUESTRA, nombre_archivo)
        shutil.copy(origen, destino)
        
    print(f"¡Listo! Muestra guardada en: {RUTA_MUESTRA}")

if __name__ == "__main__":
    generar_carpeta_muestra()