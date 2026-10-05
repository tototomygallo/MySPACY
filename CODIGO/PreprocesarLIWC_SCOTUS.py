from collections import defaultdict
import itertools
import os
import pandas as pd
from LSM.LIWC import computar_LSM_LIWC

RUTA_MUESTRA = "/home/tgallo/Documents/Proyecto_modular/muestra_scotus"
OUTPUT_LIWC = "tests/"
CSV_MAESTRO_LIWC_SCOTUS = "LIWC_SCOTUS_BASE.csv"


def generar_base_liwc_scotus_top3_hablantes():
    if not os.path.exists(RUTA_MUESTRA) or not os.listdir(RUTA_MUESTRA):
        print(f"Error: La carpeta {RUTA_MUESTRA} está vacía.")
        return

    # Asegurarse de que el directorio temporal existe
    os.makedirs(OUTPUT_LIWC, exist_ok=True)

    archivos = [f for f in os.listdir(RUTA_MUESTRA) if f.endswith(".txt")]
    resultados_liwc = []

    print(
        f"Iniciando precómputo de LIWC sobre 100% SCOTUS ({len(archivos)} archivos) - Combinaciones Top 3 hablantes..."
    )

    for nombre_archivo in archivos:
        ruta_completa = os.path.join(RUTA_MUESTRA, nombre_archivo)
        lineas_por_hablante = defaultdict(list)

        # 1. Agrupar diálogos por hablante
        with open(ruta_completa, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    partes = line.split(":", 1)
                    hablante = partes[0].strip()
                    lineas_por_hablante[hablante].append(line.strip())

        # 2. Verificar que existan al menos 2 hablantes
        if len(lineas_por_hablante) < 2:
            continue

        # 3. Seleccionar hasta los 3 hablantes con mayor número de intervenciones
        top3_hablantes = sorted(
            lineas_por_hablante.keys(),
            key=lambda h: len(lineas_por_hablante[h]),
            reverse=True,
        )[:3]

        # 4. Generar combinaciones para cada par (AB, BC, AC)
        for p1, p2 in itertools.combinations(top3_hablantes, 2):
            # Filtro de seguridad (al menos 6 intervenciones cada uno)
            if (
                len(lineas_por_hablante[p1]) < 6
                or len(lineas_por_hablante[p2]) < 6
            ):
                continue

            contenido_par = lineas_por_hablante[p1] + lineas_por_hablante[p2]
            id_virtual = f"{nombre_archivo.replace('.txt', '')}_{p1}_vs_{p2}"
            ruta_csv_temp = os.path.join(OUTPUT_LIWC, f"{id_virtual}.csv")

            # Crear CSV temporal con header para LIWC
            with open(ruta_csv_temp, "w", encoding="utf-8") as f_temp:
                f_temp.write("id:text\n")
                for ln in contenido_par:
                    f_temp.write(f"{ln}\n")

            try:
                print(f"LIWC procesando par: {id_virtual}")
                val_liwc = computar_LSM_LIWC(ruta_csv_temp, OUTPUT_LIWC)

                if val_liwc is not None:
                    resultados_liwc.append(
                        {"id_virtual": id_virtual, "lsm_liwc": val_liwc}
                    )
            except Exception as e:
                print(f"Error en LIWC para par {id_virtual}: {e}")
            finally:
                if os.path.exists(ruta_csv_temp):
                    os.remove(ruta_csv_temp)

    # 5. Guardar la base estática
    df_liwc = pd.DataFrame(resultados_liwc)
    df_liwc.to_csv(CSV_MAESTRO_LIWC_SCOTUS, index=False)
    print(
        f"\n¡Listo! Base maestra SCOTUS guardada en '{CSV_MAESTRO_LIWC_SCOTUS}' con {len(df_liwc)} pares (Top 3)."
    )


if __name__ == "__main__":
    generar_base_liwc_scotus_top3_hablantes()