from collections import defaultdict
import itertools
import os
import pandas as pd
from scipy.stats import pearsonr

# Importás el modelo que quieras auditar en el momento (spaCy_mod, NLTK, etc.)
#from LSM.LSM_SPACY import calculo_LSM
from LSM.LSM_SPACY_mod import calculo_LSM
#from LSM.LSM_NLTK import calculo_LSM

# Rutas y archivos

RUTA_SCOTUS_100 = "/home/tgallo/Documents/Proyecto_modular/muestra_scotus"
CSV_MAESTRO_LIWC_SCOTUS = "LIWC_SCOTUS_BASE.csv"
OUTPUT_FINAL_SCOTUS = "LSM_SPACY_MOD_SCOTUS.csv"


def ejecutar_pipeline_scotus_top3_hablantes():
    if not os.path.exists(CSV_MAESTRO_LIWC_SCOTUS):
        print(
            f"Error: No se encuentra '{CSV_MAESTRO_LIWC_SCOTUS}'. Corré primero el script base de LIWC."
        )
        return

    df_liwc = pd.read_csv(CSV_MAESTRO_LIWC_SCOTUS)
    archivos = [f for f in os.listdir(RUTA_SCOTUS_100) if f.endswith(".txt")]
    resultados_modelo = []

    print(
        f"Procesando {len(archivos)} archivos (100% SCOTUS) tomando combinaciones del top 3 de hablantes por archivo..."
    )

    for nombre_archivo in archivos:
        print(f"Procesando {nombre_archivo} con el modelo local...")
        ruta_completa = os.path.join(RUTA_SCOTUS_100, nombre_archivo)
        lineas_por_hablante = defaultdict(list)

        # 1. Agrupar líneas por hablante
        with open(ruta_completa, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    partes = line.split(":", 1)
                    hablante = partes[0].strip()
                    lineas_por_hablante[hablante].append(line.strip())

        # 2. Verificar que existan al menos 2 hablantes en la sesión
        if len(lineas_por_hablante) < 2:
            continue

        # 3. Seleccionar hasta los 3 hablantes con más intervenciones/líneas
        top3_hablantes = sorted(
            lineas_por_hablante.keys(),
            key=lambda h: len(lineas_por_hablante[h]),
            reverse=True,
        )[:3]

        # 4. Generar pares combinatorios entre los top hablantes (AB, BC, AC si hay 3)
        for p1, p2 in itertools.combinations(top3_hablantes, 2):
            # Filtro de seguridad (al menos 6 intervenciones cada uno)
            if len(lineas_por_hablante[p1]) < 6 or len(lineas_por_hablante[p2]) < 6:
                continue

            contenido_par = lineas_por_hablante[p1] + lineas_por_hablante[p2]
            id_virtual = f"{nombre_archivo.replace('.txt', '')}_{p1}_vs_{p2}"

            # 5. Calcular LSM para el par
            try:
                val_model = calculo_LSM(contenido_par)
                if val_model is not None:
                    resultados_modelo.append(
                        {
                            "id_virtual": id_virtual,
                            "lsm_model": val_model,
                            "grupo": "SCOTUS",
                        }
                    )
            except Exception as e:
                print(f"Error procesando par {id_virtual}: {e}")

    df_modelo = pd.DataFrame(resultados_modelo)

    if df_modelo.empty:
        print("No se generaron resultados de LSM para el modelo.")
        return

    # 6. Cruzar con el CSV de LIWC por id_virtual
    df_final = pd.merge(df_modelo, df_liwc, on="id_virtual", how="inner")

    # Limpieza
    df_final = df_final.dropna(subset=["lsm_liwc", "lsm_model"])
    df_final = df_final[df_final["lsm_model"] > 0]

    # 7. Correlación
    if not df_final.empty:
        r_val, p_val = pearsonr(df_final["lsm_liwc"], df_final["lsm_model"])
        print(f"\n--- RESULTADOS SCOTUS (TOP 3 SPEAKERS - COMBINACIONES) ---")
        print(f"Archivos/Pares procesados con éxito: {len(df_final)}")
        print(f"Correlación de Pearson (r): {r_val:.4f}")
        print(f"Valor p: {p_val:.4e}")

        df_final.to_csv(OUTPUT_FINAL_SCOTUS, index=False)
        print(f"Resultados exportados a '{OUTPUT_FINAL_SCOTUS}'")
    else:
        print("No se encontraron pares válidos emparejados con LIWC.")


if __name__ == "__main__":
    ejecutar_pipeline_scotus_top3_hablantes()