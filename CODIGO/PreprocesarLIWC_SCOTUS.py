import os
import pandas as pd
import itertools
from collections import defaultdict
from LSM.LIWC import computar_LSM_LIWC

RUTA_MUESTRA = "/home/tgallo/Documents/Proyecto_modular/muestra_scotus"  
OUTPUT_LIWC = "tests/"
CSV_MAESTRO_LIWC_SCOTUS = "LIWC_SCOTUS_BASE.csv"

def generar_base_liwc_scotus():
    if not os.path.exists(RUTA_MUESTRA) or not os.listdir(RUTA_MUESTRA):
        print(f"Error: La carpeta {RUTA_MUESTRA} está vacía.")
        return

    archivos = [f for f in os.listdir(RUTA_MUESTRA) if f.endswith('.txt')]
    resultados_liwc = []
    
    print("Iniciando precómputo de LIWC para pares virtuales de SCOTUS...")

    for nombre_archivo in archivos:
        ruta_completa = os.path.join(RUTA_MUESTRA, nombre_archivo)
        lineas_por_hablante = defaultdict(list)
        
        # 1. Agrupar diálogos por hablante
        with open(ruta_completa, 'r', encoding='utf-8') as f:
            for line in f:
                if ":" in line:
                    partes = line.split(":", 1)
                    hablante = partes[0].strip()
                    lineas_por_hablante[hablante].append(line.strip())
        
        # 2. Generar pares virtuales idénticos
        hablantes = list(lineas_por_hablante.keys())
        for p1, p2 in itertools.combinations(hablantes, 2):
            
            # Filtro de calidad estricto (mismo criterio de siempre)
            if len(lineas_por_hablante[p1]) < 6 or len(lineas_por_hablante[p2]) < 6:
                continue
                
            contenido_par = lineas_por_hablante[p1] + lineas_por_hablante[p2]
            id_virtual = f"{nombre_archivo.replace('.txt','')}_{p1}_vs_{p2}"
            ruta_csv_temp = os.path.join(OUTPUT_LIWC, f"{id_virtual}.csv")
            
            # 3. Crear CSV temporal con header para LIWC
            with open(ruta_csv_temp, 'w', encoding='utf-8') as f_temp:
                f_temp.write("id:text\n")
                for ln in contenido_par:
                    f_temp.write(f"{ln}\n")
            
            try:
                print(f"LIWC procesando par: {id_virtual}")
                val_liwc = computar_LSM_LIWC(ruta_csv_temp, OUTPUT_LIWC)
                
                # Guardamos la métrica con su ID único combinatorio
                resultados_liwc.append({
                    "id_virtual": id_virtual,
                    "lsm_liwc": val_liwc
                })
            except Exception as e:
                print(f"Error en LIWC para par {id_virtual}: {e}")
            finally:
                if os.path.exists(ruta_csv_temp):
                    os.remove(ruta_csv_temp)

    # Guardar base estática indexada por par virtual
    df_liwc = pd.DataFrame(resultados_liwc)
    df_liwc.to_csv(CSV_MAESTRO_LIWC_SCOTUS, index=False)
    print(f"¡Listo! Base maestra SCOTUS guardada en '{CSV_MAESTRO_LIWC_SCOTUS}' con {len(df_liwc)} pares.")

if __name__ == "__main__":
    generar_base_liwc_scotus()