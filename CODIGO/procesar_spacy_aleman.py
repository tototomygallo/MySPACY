from collections import defaultdict
import os
import re
import pandas as pd
import spacy

from LSM.LSM_SPACY_ALEMAN import calculo_LSM

# Cargar modelo en alemán
nlp = spacy.load("de_core_news_md")

# --- CONFIGURACIÓN DE RUTAS ---
DIRECTORIO_ALEMAN = "/home/tgallo/Documents/Proyecto_modular/dialogos_por_tarea"
OUTPUT_FINAL = "LSM_GERMAN_R1_R8.csv"

# --- FILTRADO DE ARCHIVOS (Solo r1, r2, r3, r4) ---
def cargar_archivos_r1_a_r4(directorio):
    """Filtra y carga solo los archivos de diálogos pertenecientes a las rondas r1, r2, r3 y r4."""
    # Expresión regular que busca que el archivo comience con r1, r2, r3, r4,...,r8
    patron_ronda = re.compile(r"^r[1-8]_", re.IGNORECASE)

    for nombre_archivo in sorted(os.listdir(directorio)):
        if nombre_archivo.endswith(".txt") and patron_ronda.match(
            nombre_archivo
        ):
            ruta_completa = os.path.join(directorio, nombre_archivo)
            with open(ruta_completa, "r", encoding="utf-8") as f:
                lineas = f.readlines()
            yield nombre_archivo, lineas



# --- PIPELINE PRINCIPAL ---

def ejecutar_pipeline_aleman_subconjunto():
    if not os.path.exists(DIRECTORIO_ALEMAN):
        print(f"Error: No existe el directorio '{DIRECTORIO_ALEMAN}'")
        return

    resultados_modelo = []
    print(
        "Procesando subconjunto de datos (Rondas r1 a r4, todas las tareas)..."
    )

    for nombre_archivo, contenido in cargar_archivos_r1_a_r4(DIRECTORIO_ALEMAN):
        try:
            val_modelo = calculo_LSM(contenido)

            # Extraer la ronda y la tarea para tener metadata ordenada en el CSV
            # Ej: de "r1_part3_1_2.txt" extrae ronda="r1"
            partes_nombre = nombre_archivo.split("_")
            ronda = partes_nombre[0]

            if val_modelo is not None:
                resultados_modelo.append(
                    {
                        "archivo": nombre_archivo,
                        "ronda": ronda,
                        "lsm_model": val_modelo,
                        "grupo": "r1_r4_subset",
                    }
                )
            else:
                print(
                    f"Omisión: {nombre_archivo} no cumple el mínimo de palabras o hablantes."
                )

        except Exception as e:
            print(f"Error procesando {nombre_archivo}: {e}")

    # Crear DataFrame con los resultados
    df_final = pd.DataFrame(resultados_modelo)

    if not df_final.empty:
        print(f"\n--- RESUMEN R1 a R4 ---")
        print(f"Total de tareas/archivos procesados: {len(df_final)}")
        print(f"Promedio general LSM (r1-r4): {df_final['lsm_model'].mean():.4f}")

        # Mostrar desglose rápido por ronda
        print("\nPromedio LSM por ronda:")
        print(df_final.groupby("ronda")["lsm_model"].mean())

        # Exportar CSV
        df_final.to_csv(OUTPUT_FINAL, index=False)
        print(f"\nResultados guardados en '{OUTPUT_FINAL}'")
    else:
        print(
            "No se encontraron archivos que coincidan con el patrón r1 a r4."
        )


if __name__ == "__main__":
    ejecutar_pipeline_aleman_subconjunto()