import os
import pandas as pd
from Herramientas.parseo import cargar_de_lista
#from LSM.LSM_SPACY import calculo_LSM
#from LSM.LSM_SPACY_mod import calculo_LSM
from LSM.LSM_NLTK import calculo_LSM

from LSM.LIWC import computar_LSM_LIWC

import shutil



#directorios = ["/home/tgallo/Documents/Proyecto_modular/output", "/home/tgallo/Documents/Proyecto_modular/CGC-transcripts/diez_porciento"] # faltaria ver como hacer scotus
directorios = ["/home/tgallo/Documents/Proyecto_modular/SW_PROCESSED"] #! archivo 3511 en B hay algo raro en el texto

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

        # --- NUEVA LÓGICA CON HEADER ---
        # Leemos el contenido original y le pegamos el header 'id:text' arriba
        with open(ruta_original, 'r', encoding='utf-8') as f_original:
            lineas_dialogo = f_original.readlines()
        
        with open(ruta_csv, 'w', encoding='utf-8') as f_nuevo:
            f_nuevo.write("id:text\n")  # Inyectamos el header que pide el profe
            f_nuevo.writelines(lineas_dialogo)
        # -------------------------------
        
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
df_total.to_csv("LSM_NLTK_SW.csv", index=False)