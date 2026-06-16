import os
import pandas as pd
import itertools
from collections import defaultdict
from procesar import compute_ENTR
from spacy.lang.en.stop_words import STOP_WORDS

RUTA_MUESTRA = "/home/tgallo/Documents/Proyecto_modular/muestra_scotus"

def run():

    archivos = [f for f in os.listdir(RUTA_MUESTRA) if f.endswith(".txt")]
    resultados = []

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

        for p1, p2 in itertools.combinations(hablantes, 2):

            A = lineas_por_hablante[p1]
            B = lineas_por_hablante[p2]

            res = compute_ENTR(A, B, list(STOP_WORDS))
            print(f"  Par: {p1} vs {p2} - ENTR1: {res['entr1']:.4f}, ENTR2: {res['entr2']:.4f}")

            resultados.append({
                "id_virtual": f"{nombre_archivo.replace('.txt','')}_{p1}_vs_{p2}",
                "entr1": res["entr1"],
                "entr2": res["entr2"]
            })

    df = pd.DataFrame(resultados)
    df.to_csv("ENTR_SPACY_SCOTUS.csv", index=False)

if __name__ == "__main__":
    run()