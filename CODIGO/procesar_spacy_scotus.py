import os
import pandas as pd
import itertools
from collections import defaultdict
from scipy.stats import pearsonr

# Importás el modelo que quieras auditar en el momento (spaCy_mod, NLTK, etc.)
from LSM.myspacy import calculo_LSM
#from LSM.LSM_SPACY_mod import calculo_LSM
#from LSM.LSM_NLTK import calculo_LSM
import shutil

RUTA_MUESTRA = "/home/tgallo/Documents/Proyecto_modular/muestra_scotus"  
CSV_MAESTRO_LIWC_SCOTUS = "LIWC_SCOTUS_BASE.csv"
OUTPUT_FINAL_SCOTUS = "LSM_SPACY_SCOTUS.csv"  # Modificá el nombre según el modelo de turno

def ejecutar_pipeline_rapido_scotus():
    if not os.path.exists(CSV_MAESTRO_LIWC_SCOTUS):
        print(f"Error: No se encuentra '{CSV_MAESTRO_LIWC_SCOTUS}'. Corré primero 'precomputar_liwc_scotus.py'.")
        return
        
    df_liwc = pd.read_csv(CSV_MAESTRO_LIWC_SCOTUS)
    archivos = [f for f in os.listdir(RUTA_MUESTRA) if f.endswith('.txt')]
    resultados_modelo = []
    
    print("Calculando métricas del modelo sobre pares virtuales de SCOTUS...")

    for nombre_archivo in archivos:
        ruta_completa = os.path.join(RUTA_MUESTRA, nombre_archivo)
        lineas_por_hablante = defaultdict(list)
        
        with open(ruta_completa, 'r', encoding='utf-8') as f:
            for line in f:
                if ":" in line:
                    partes = line.split(":", 1)
                    hablante = partes[0].strip()
                    lineas_por_hablante[hablante].append(line.strip())
        
        hablantes = list(lineas_por_hablante.keys())
        for p1, p2 in itertools.combinations(hablantes, 2):
            
            if len(lineas_por_hablante[p1]) < 6 or len(lineas_por_hablante[p2]) < 6:
                continue
                
            contenido_par = lineas_por_hablante[p1] + lineas_por_hablante[p2]
            id_virtual = f"{nombre_archivo.replace('.txt','')}_{p1}_vs_{p2}"
            
            try:
                val_model = calculo_LSM(contenido_par)
                resultados_modelo.append({
                    "id_virtual": id_virtual,
                    "lsm_model": val_model,
                    "grupo": "SCOTUS"
                })
            except Exception as e:
                print(f"Error procesando par {id_virtual} con el modelo: {e}")

    df_modelo = pd.DataFrame(resultados_modelo)

    # El cruce mágico usando la clave única del par virtual
    df_final = pd.merge(df_modelo, df_liwc, on="id_virtual", how="inner")
    
    # Limpieza estricta de NaNs o scores caídos a cero
    df_final = df_final.dropna(subset=['lsm_liwc', 'lsm_model'])
    df_final = df_final[df_final['lsm_model'] > 0]

    if not df_final.empty:
        r_val, p_val = pearsonr(df_final['lsm_liwc'], df_final['lsm_model'])
        print(f"\n--- RESULTADOS SCOTUS ---")
        print(f"Pares emparejados con éxito: {len(df_final)}")
        print(f"Correlación de Pearson (r): {r_val:.4f}")
        print(f"Valor p: {p_val:.4e}")
        
        # Guardar para los PLOTS
        df_final.to_csv(OUTPUT_FINAL_SCOTUS, index=False)
        print(f"Resultados exportados a '{OUTPUT_FINAL_SCOTUS}'")
    else:
        print("No se encontraron pares válidos para correlacionar.")

if __name__ == "__main__":
    ejecutar_pipeline_rapido_scotus()