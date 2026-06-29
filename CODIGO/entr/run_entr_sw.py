import os
import pandas as pd
#from spacy.lang.en.stop_words import STOP_WORDS
from procesar import compute_ENTR, compute_ENTR_dinamico_LSM, obtener_top_25_corpus
from nltk.corpus import stopwords

Word_class = stopwords.words('english')

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

# --- DEFINICIÓN DE LAS CLASES EXPLICITADAS POR AGUS ---
# Clase 1: Stopwords estándar
clase1_stopwords = Word_class

# Clase 3: Unión de categorías usadas en tu LSM_SPACY_mod
# (Negaciones de LIWC + Artículos puros + Pronombres sin el "it")
negaciones_liwc = {"no", "not", "never", "neither", "nor", "nobody", "nothing", "nowhere", "none", "cannot", "n't", "nope", "ain't"}
articulos_puros = {"the", "a", "an"}
# Agregamos pronombres típicos en inglés para mapear la categoría completa
pronombres_lsm = {"i", "you", "he", "she", "we", "they", "me", "him", "her", "us", "them", "my", "your", "his", "their", "mine", "yours", "hers", "ours", "theirs"}
#clase3_lsm_union = list(negaciones_liwc.union(articulos_puros).union(pronombres_lsm))

def run():
    # 1. Carga previa de todas las conversaciones en memoria para extraer la Clase 2 de todo el corpus
    conversaciones = list(cargar_de_lista(DIRECTORIO_SW))
    solo_contenidos = [contenido for _, contenido in conversaciones]
    
    # Obtener la Clase 2 de forma global
    clase2_top25 = obtener_top_25_corpus(solo_contenidos)

    resultados = []

    # 2. Correr el bucle de procesamiento de métricas
    for nombre_archivo, contenido in conversaciones:
        print(f"Procesando {nombre_archivo}...")
        A, B = [], []
        for linea in contenido:
            if linea.startswith("A:"): A.append(linea)
            elif linea.startswith("B:"): B.append(linea)

        if len(A) == 0 or len(B) == 0: continue

        try:
            # Cómputos cruzados para las 3 clases
            res_c1 = compute_ENTR(A, B, clase1_stopwords)
            res_c2 = compute_ENTR(A, B, clase2_top25)
            # Cómputo para Clase 3 (Dinámica según las POS tags de LSM)
            res_c3 = compute_ENTR_dinamico_LSM(A, B)

            resultados.append({
                "archivo": nombre_archivo,
                "entr1_clase1": res_c1["entr1"], "entr2_clase1": res_c1["entr2"],
                "entr1_clase2": res_c2["entr1"], "entr2_clase2": res_c2["entr2"],
                "entr1_clase3": res_c3["entr1"], "entr2_clase3": res_c3["entr2"]
            })
        except Exception as e:
            print(f"Error en {nombre_archivo}: {e}")

    df = pd.DataFrame(resultados)
    df.to_csv("ENTR_SPACY_SW.csv", index=False)
    print(f"\n¡Listo! Matriz completa guardada en ENTR_SPACY_SW.csv ({len(df)} diálogos).")

if __name__ == "__main__":
    run()