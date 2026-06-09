import os
import pandas as pd
import shutil
from Herramientas.parseo import cargar_de_lista
from LSM.LIWC import computar_LSM_LIWC

DIRECTORIO_SW = "/home/tgallo/Documents/Proyecto_modular/SW_PROCESSED"
OUTPUT_LIWC = "tests/"
CSV_MAESTRO_LIWC = "LIWC_SW_BASE.csv"

def generar_base_liwc():
    if not os.path.exists(DIRECTORIO_SW):
        print(f"Error: No existe el directorio {DIRECTORIO_SW}")
        return

    resultados_liwc = []
    print("Iniciando precómputo de LIWC (esto puede tardar)...")

    for nombre_archivo, _ in cargar_de_lista(DIRECTORIO_SW):
        ruta_original = os.path.join(DIRECTORIO_SW, nombre_archivo)
        ruta_csv = ruta_original.replace(".txt", ".csv").replace(".phrases", ".csv")
        
        # Preparar archivo con header para LIWC
        with open(ruta_original, 'r', encoding='utf-8') as f_original:
            lineas_dialogo = f_original.readlines()
        
        with open(ruta_csv, 'w', encoding='utf-8') as f_nuevo:
            f_nuevo.write("id:text\n")
            f_nuevo.writelines(lineas_dialogo)
        
        try:
            print(f"LIWC procesando: {nombre_archivo}")
            val_liwc = computar_LSM_LIWC(ruta_csv, OUTPUT_LIWC)
            
            # Guardamos el ID del archivo y su score estático
            resultados_liwc.append({
                "archivo": nombre_archivo,
                "lsm_liwc": val_liwc
            })
        except Exception as e:
            print(f"Error en LIWC para {nombre_archivo}: {e}")
        finally:
            if os.path.exists(ruta_csv):
                os.remove(ruta_csv)

    # Guardar la base de datos estática
    df_liwc = pd.DataFrame(resultados_liwc)
    df_liwc.to_csv(CSV_MAESTRO_LIWC, index=False)
    print(f"¡Listo! Base maestra guardada en '{CSV_MAESTRO_LIWC}' con {len(df_liwc)} archivos.")

if __name__ == "__main__":
    generar_base_liwc()