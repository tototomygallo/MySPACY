import os
import pandas as pd
import itertools
from collections import defaultdict
# Importamos ambas funciones de procesamiento
from procesar import compute_ENTR, compute_ENTR_dinamico_LSM, obtener_top_25_corpus
from nltk.corpus import stopwords

# Clase 1: Stopwords estándar de NLTK (o podés usar STOP_WORDS de spaCy, el que prefieras)
Word_class = stopwords.words('english')
clase1_stopwords = Word_class

RUTA_MUESTRA = "/home/tgallo/Documents/Proyecto_modular/muestra_scotus"

def cargar_todo_el_corpus(archivos) -> list[list[str]]:
    """Carga todas las líneas de todos los archivos para poder calcular el Top 25 global."""
    contenidos_totales = []
    for nombre_archivo in archivos:
        ruta = os.path.join(RUTA_MUESTRA, nombre_archivo)
        with open(ruta, "r", encoding="utf-8") as f:
            contenidos_totales.append([line.strip() for line in f if line.strip()])
    return contenidos_totales

def run():
    archivos = [f for f in os.listdir(RUTA_MUESTRA) if f.endswith(".txt")]
    
    # 1. Obtener la Clase 2 (Top 25) de forma global para SCOTUS
    solo_contenidos = cargar_todo_el_corpus(archivos)
    clase2_top25 = obtener_top_25_corpus(solo_contenidos)
    
    resultados = []

    # 2. Procesar cada archivo y sus combinaciones de hablantes
    for nombre_archivo in archivos:
        print(f"Procesando {nombre_archivo}...")
        ruta = os.path.join(RUTA_MUESTRA, nombre_archivo)
        lineas_por_hablante = defaultdict(list)

        with open(ruta, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    hablante = line.split(":", 1)[0].strip()
                    lineas_por_hablante[hablante].append(line.strip())

        hablantes = list(lineas_por_hablante.keys())

        # Cruza todos los hablantes de a pares (p1 vs p2)
        for p1, p2 in itertools.combinations(hablantes, 2):
            A = lineas_por_hablante[p1]
            B = lineas_por_hablante[p2]

            if len(A) == 0 or len(B) == 0: continue

            try:
                # Cómputos para las 3 clases
                res_c1 = compute_ENTR(A, B, clase1_stopwords)
                res_c2 = compute_ENTR(A, B, clase2_top25)
                res_c3 = compute_ENTR_dinamico_LSM(A, B)  # Clase 3 dinámica por par

                print(f"  Par: {p1} vs {p2} - C1_E1: {res_c1['entr1']:.4f} | C2_E1: {res_c2['entr1']:.4f} | C3_E1: {res_c3['entr1']:.4f}")

                resultados.append({
                    "id_virtual": f"{nombre_archivo.replace('.txt','')}_{p1}_vs_{p2}",
                    "entr1_clase1": res_c1["entr1"], "entr2_clase1": res_c1["entr2"],
                    "entr1_clase2": res_c2["entr1"], "entr2_clase2": res_c2["entr2"],
                    "entr1_clase3": res_c3["entr1"], "entr2_clase3": res_c3["entr2"]
                })
            except Exception as e:
                print(f"Error procesando par {p1} vs {p2} en {nombre_archivo}: {e}")

    df = pd.DataFrame(resultados)
    df.to_csv("ENTR_SPACY_SCOTUS.csv", index=False)
    print(f"\n¡Listo! Matriz completa de SCOTUS guardada ({len(df)} pares analizados).")

if __name__ == "__main__":
    run()