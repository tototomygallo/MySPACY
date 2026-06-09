import os
import pandas as pd
import random
import itertools
from collections import defaultdict
from scipy.stats import pearsonr
#from LSM.myspacy import calculo_LSM
from LSM.LSM_SPACY_mod import calculo_LSM
#from LSM.LSM_NLTK import calculo_LSM
from LSM.LIWC import computar_LSM_LIWC
# --- CONFIGURACIÓN ---
# Apuntamos directo a tu nueva carpeta fija
RUTA_MUESTRA = "/home/tgallo/Documents/Proyecto_modular/muestra_scotus"  
OUTPUT_LIWC = "tests/"

def pipeline_scotus():
    # Chequeo rápido de seguridad
    if not os.path.exists(RUTA_MUESTRA) or not os.listdir(RUTA_MUESTRA):
        print(f"Error: La carpeta {RUTA_MUESTRA} está vacía. Corré primero el script de la muestra.")
        return

    archivos = [f for f in os.listdir(RUTA_MUESTRA) if f.endswith('.txt')]
    resultados_scotus = []
    
    print(f"Procesando pipeline sobre la muestra fija ({len(archivos)} archivos)...")

    for nombre_archivo in archivos:
        print(f"Procesando archivo: {nombre_archivo}")
        ruta_completa = os.path.join(RUTA_MUESTRA, nombre_archivo)
        lineas_por_hablante = defaultdict(list)
        
        # 1. Agrupar diálogos por hablante
        with open(ruta_completa, 'r', encoding='utf-8') as f:
            for line in f:
                if ":" in line:
                    partes = line.split(":", 1)
                    hablante = partes[0].strip()
                    lineas_por_hablante[hablante].append(line.strip())
        
        # 2. Generar pares virtuales
        hablantes = list(lineas_por_hablante.keys())
        for p1, p2 in itertools.combinations(hablantes, 2):
            
            # Filtro de calidad: Al menos 6 intervenciones cada uno
            if len(lineas_por_hablante[p1]) < 6 or len(lineas_por_hablante[p2]) < 6:
                continue
                
            contenido_par = lineas_por_hablante[p1] + lineas_por_hablante[p2]
            id_virtual = f"{nombre_archivo.replace('.txt','')}_{p1}_vs_{p2}"
            ruta_csv_temp = os.path.join(OUTPUT_LIWC, f"{id_virtual}.csv")
            
            # 3. Crear CSV temporal para LIWC-cli
            with open(ruta_csv_temp, 'w', encoding='utf-8') as f_temp:
                f_temp.write("id:text\n")
                for ln in contenido_par:
                    f_temp.write(f"{ln}\n")
            
            try:
                # 4. Cálculos cruzados
                val_model = calculo_LSM(contenido_par)
                val_liwc = computar_LSM_LIWC(ruta_csv_temp, OUTPUT_LIWC)
                
                # 5. Guardar si pasó los filtros de NaNs
                if val_liwc and not pd.isna(val_liwc) and val_model > 0:
                    resultados_scotus.append({
                        "archivo": id_virtual,
                        "lsm_model": val_model, # Nombre genérico para el modelo bajo prueba
                        "lsm_liwc": val_liwc,
                        "grupo": "SCOTUS"
                    })
            except Exception as e:
                print(f"Error en par {id_virtual}: {e}")
            finally:
                if os.path.exists(ruta_csv_temp):
                    os.remove(ruta_csv_temp)

    # --- FINALIZACIÓN Y CORRELACIÓN ---
    df_scotus = pd.DataFrame(resultados_scotus)
    
    if not df_scotus.empty:
        r_val, p_val = pearsonr(df_scotus['lsm_liwc'], df_scotus['lsm_model'])
        print(f"\n--- RESULTADOS SCOTUS ---")
        print(f"Pares válidos procesados: {len(df_scotus)}")
        print(f"Correlación de Pearson (r): {r_val:.4f}")
        print(f"Valor p: {p_val:.4e}")
        
        # Guardamos el CSV con los resultados de la corrida
        df_scotus.to_csv("LSM_SPACY_MOD_SCOTUS.csv", index=False)
    else:
        print("No se generaron datos válidos.")

if __name__ == "__main__":
    pipeline_scotus()