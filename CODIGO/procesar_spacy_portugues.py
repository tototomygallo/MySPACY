import os
import pandas as pd
from LSM.LSM_SPACY_PORTUGUES import calculo_LSM

# Rutas de entrada y salida para Portugués
DIRECTORIO_PORTUGUES = "/home/tgallo/Documents/Proyecto_modular/CORPUS_LIMPIO_DIADICO"
OUTPUT_FINAL = "LSM_SPACY_PORTUGUES.csv"


def cargar_archivos_limpios(directorio: str):
    """Lee todos los archivos .txt de la carpeta preprocesada y devuelve una lista de tuplas (nombre_archivo, lineas)."""
    archivos_datos = []
    if not os.path.exists(directorio):
        print(f"Error: No se encuentra el directorio '{directorio}'.")
        return archivos_datos

    for file in sorted(os.listdir(directorio)):
        if file.endswith(".txt"):
            ruta = os.path.join(directorio, file)
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                lineas = f.readlines()
            archivos_datos.append((file, lineas))

    return archivos_datos


def ejecutar_pipeline_muestra_pt():
    # 1. Cargar todos los archivos preprocesados
    todos_los_archivos = cargar_archivos_limpios(DIRECTORIO_PORTUGUES)

    if not todos_los_archivos:
        print("No se encontraron archivos en la carpeta de entrada.")
        return

    # 2. Seleccionar el 10% (6 archivos de los 60 totales)
    total_archivos = len(todos_los_archivos)
    cantidad_muestra = max(1, int(total_archivos * 1))
    muestra = todos_los_archivos[:cantidad_muestra]

    print(f"Total de archivos diádicos encontrados: {total_archivos}")
    print(f"Procesando muestra del 10% ({len(muestra)} archivos)...\n")

    resultados_modelo = []

    # 3. Calcular LSM para la muestra usando la función de portugués
    for nombre_archivo, contenido in muestra:
        try:
            val_modelo = calculo_LSM(contenido)

            if val_modelo is not None:
                resultados_modelo.append({
                    "archivo": nombre_archivo,
                    "lsm_spacy_pt": val_modelo,
                    "grupo": "CORPUS_LIMPIO_DIADICO"
                })
                print(f"OK: {nombre_archivo} -> LSM: {val_modelo:.4f}")
            else:
                print(f"SKIP (No cumplió requisitos de palabras/hablantes): {nombre_archivo}")

        except Exception as e:
            print(f"Error procesando {nombre_archivo}: {e}")

    # 4. Convertir a DataFrame y guardar
    df_resultado = pd.DataFrame(resultados_modelo)

    if not df_resultado.empty:
        print("\n--- RESUMEN DE MUESTRA PORTUGUÉS ---")
        print(df_resultado)
        print(f"\nPromedio LSM en la muestra: {df_resultado['lsm_spacy_pt'].mean():.4f}")

        df_resultado.to_csv(OUTPUT_FINAL, index=False)
        print(f"Resultados exportados a '{OUTPUT_FINAL}'")
    else:
        print("No se pudieron obtener scores de LSM para los archivos de la muestra.")


if __name__ == "__main__":
    ejecutar_pipeline_muestra_pt()