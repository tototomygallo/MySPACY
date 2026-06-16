import pandas as pd
from spacy.lang.en.stop_words import STOP_WORDS
import os
#from Herramientas.parseo import cargar_de_lista
from procesar import compute_ENTR

def cargar_de_archivo(filepath: str) -> list[str]:
    """Lee un archivo y devuelve una lista de líneas."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def cargar_de_lista(directory: str):
    """Generador que entrega conversaciones de una carpeta."""
    for filename in sorted(os.listdir(directory)):
        if filename.endswith((".txt", ".phrases")):
            yield filename, cargar_de_archivo(os.path.join(directory, filename))


DIRECTORIO_SW = "/home/tgallo/Documents/Proyecto_modular/SW_PROCESSED"

def run():

    resultados = []

    for nombre_archivo, contenido in cargar_de_lista(DIRECTORIO_SW):

        print(f"Procesando {nombre_archivo}...")

        A = []
        B = []

        for linea in contenido:

            if linea.startswith("A:"):
                A.append(linea)

            elif linea.startswith("B:"):
                B.append(linea)

        if len(A) == 0 or len(B) == 0:
            continue

        try:
            res = compute_ENTR(A, B, list(STOP_WORDS))

            print(
                f"  ENTR1: {res['entr1']:.4f}, "
                f"ENTR2: {res['entr2']:.4f}"
            )

            resultados.append({
                "archivo": nombre_archivo,
                "entr1": res["entr1"],
                "entr2": res["entr2"]
            })

        except Exception as e:
            print(f"Error en {nombre_archivo}: {e}")

    df = pd.DataFrame(resultados)
    df.to_csv("ENTR_SPACY_SW.csv", index=False)

    print(f"\nGuardado ENTR_SPACY_SW.csv ({len(df)} diálogos)")

if __name__ == "__main__":
    run()