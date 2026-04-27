import os
import pandas as pd
from Herramientas.parseo import cargar_de_lista
from LSM.myspacy import calculo_LSM
from LSM.LIWC import computar_LSM_LIWC
import shutil



directorios = ["/home/tgallo/Documents/Proyecto_modular/output", "/home/tgallo/Documents/Proyecto_modular/CGC-transcripts/out"] # faltaria ver como hacer scotus
output_liwc = "tests/" #  LIWC outputfolder para el csv de resultados
resultados_finales = []

for dir_path in directorios:
    # Usamos tu generador que ya filtra .txt
    for nombre_archivo, contenido in cargar_de_lista(dir_path):
        
        ruta_original = os.path.join(dir_path, nombre_archivo)
        
        # 1. Creamos la ruta con .csv (solo el nombre)
        ruta_csv = ruta_original.replace(".txt", ".csv").replace(".phrases", ".csv")
        
        # 2. Copiamos el archivo físicamente a la nueva extensión
        # Esto es lo que LIWC necesita para "verlo" como CSV
        shutil.copy(ruta_original, ruta_csv)
        
        try:
            # 3. Calculamos ambos (LIWC y Spacy) y guardamos resultados
            val_spacy = calculo_LSM(contenido)
            val_liwc = computar_LSM_LIWC(ruta_csv, output_liwc)
            
            resultados_finales.append({
                "archivo": nombre_archivo,
                "lsm_spacy": val_spacy,
                "lsm_liwc": val_liwc,
                "grupo": os.path.basename(dir_path)
            })
        finally:
            # 4. LIMPIEZA: Borramos el .csv temporal para que no moleste
            if os.path.exists(ruta_csv):
                os.remove(ruta_csv)

# 5. Guardamos todo en un CSV para los PLOTS
df_total = pd.DataFrame(resultados_finales)
df_total.to_csv("datos_para_plotear.csv", index=False)