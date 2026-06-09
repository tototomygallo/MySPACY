import os
import pandas as pd
from scipy.stats import pearsonr
from Herramientas.parseo import cargar_de_lista
from LSM.myspacy import calculo_LSM
#from LSM.LSM_SPACY_mod import calculo_LSM
#from LSM.LSM_NLTK import calculo_LSM
import shutil

DIRECTORIO_SW = "/home/tgallo/Documents/Proyecto_modular/SW_PROCESSED"
CSV_MAESTRO_LIWC = "LIWC_SW_BASE.csv"
OUTPUT_FINAL = "LSM_SPACY_SW.csv"

def ejecutar_pipeline_rapido():
    # 1. Control de seguridad: Verificar si tenemos la base de LIWC
    if not os.path.exists(CSV_MAESTRO_LIWC):
        print(f"Error: No se encuentra '{CSV_MAESTRO_LIWC}'. Corré primero 'precomputar_liwc.py'.")
        return
        
    # Cargar los datos estáticos de LIWC
    df_liwc = pd.read_csv(CSV_MAESTRO_LIWC)
    
    resultados_modelo = []
    print("Calculando métricas del modelo local...")

    # 2. Correr solo tu algoritmo (NLTK / spaCy)
    for nombre_archivo, contenido in cargar_de_lista(DIRECTORIO_SW):
        try:
            val_modelo = calculo_LSM(contenido)
            resultados_modelo.append({
                "archivo": nombre_archivo,
                "lsm_model": val_modelo, # Nombre genérico para adaptarlo fácil
                "grupo": os.path.basename(DIRECTORIO_SW)
            })
        except Exception as e:
            print(f"Error procesando {nombre_archivo} con el modelo: {e}")

    df_modelo = pd.DataFrame(resultados_modelo)

    # 3. EL TRUCO: Cruzar las tablas por la columna 'archivo' usando un merge interno
    # Esto descarta automáticamente cualquier NaN o archivo que haya fallado en LIWC
    df_final = pd.merge(df_modelo, df_liwc, on="archivo", how="inner")
    
    # Limpieza de seguridad por si quedó algún valor roto
    df_final = df_final.dropna(subset=['lsm_liwc', 'lsm_model'])
    df_final = df_final[df_final['lsm_model'] > 0]

    # 4. Calcular correlación instantánea
    if not df_final.empty:
        r_val, p_val = pearsonr(df_final['lsm_liwc'], df_final['lsm_model'])
        print(f"\n--- RESULTADOS SW_PROCESSED ---")
        print(f"Archivos cruzados con éxito: {len(df_final)}")
        print(f"Correlación de Pearson (r): {r_val:.4f}")
        print(f"Valor p: {p_val:.4e}")
        
        # Guardar resultados listos para los PLOTS
        df_final.to_csv(OUTPUT_FINAL, index=False)
        print(f"Resultados exportados a '{OUTPUT_FINAL}'")
    else:
        print("No se pudieron emparejar datos válidos para la correlación.")

if __name__ == "__main__":
    ejecutar_pipeline_rapido()