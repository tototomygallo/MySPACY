from collections import defaultdict
import os
import re
import pandas as pd
import spacy

# Cargar modelo en alemán
nlp = spacy.load("de_core_news_sm")

DIRECTORIO_ALEMAN = "/home/tgallo/Documents/Proyecto_modular/dialogos_por_tarea"
OUTPUT_CSV = "LSM_RONDAS_AGREGADAS_R1_R8.csv"


# --- CONTEO DE CATEGORÍAS STTS ---
def conteo_categorias(text: str):
    contador = defaultdict(int)
    doc = nlp(text)
    LEMAS_AUX = {"sein", "haben", "werden"}

    for t in doc:
        if t.is_punct or t.is_space:
            continue

        tag = t.tag_
        lemma = t.lemma_.lower()

        if tag == "PTKNEG" or lemma == "kein":
            contador["negate"] += 1
        elif tag in ["PPER", "PRF", "POSS"]:
            contador["ppron"] += 1
        elif tag in ["PIS", "PDS", "PDAT", "PWS", "PWAT", "PRELS"]:
            contador["ipron"] += 1
        elif tag == "ART":
            contador["article"] += 1
        elif tag in ["APPR", "APPRART", "APPO"]:
            contador["prep"] += 1
        elif tag in ["ADV", "PAV"]:
            contador["adverb"] += 1
        elif tag.startswith("VA") or (
            t.pos_ in ["VERB", "AUX"] and lemma in LEMAS_AUX
        ):
            contador["auxverb"] += 1
        elif tag in ["KON", "KOUS", "KOUI"] or t.pos_ in ["CCONJ", "SCONJ"]:
            contador["conj"] += 1

    return contador, len(text.split())


# --- CÁLCULO DE LSM Y DESGLOSE POR CATEGORÍA ---
def calculo_LSM_agregado(conversation: list[str]):
    Data_hablante = defaultdict(lambda: defaultdict(int))
    contador_palabras_hablante = defaultdict(int)

    for line in conversation:
        if ":" not in line:
            continue
        user, text = line.split(":", 1)
        user = user.strip()

        counts, wc = conteo_categorias(text.strip())
        for cat, val in counts.items():
            Data_hablante[user][cat] += val
        contador_palabras_hablante[user] += wc

    hablantes_ids = list(Data_hablante.keys())
    if len(hablantes_ids) < 2:
        return None, None, None

    p1, p2 = hablantes_ids[0], hablantes_ids[1]

    cats = [
        "ppron",
        "ipron",
        "article",
        "prep",
        "negate",
        "adverb",
        "auxverb",
        "conj",
    ]
    lsm_scores = {}

    for c in cats:
        pct1 = (Data_hablante[p1][c] / contador_palabras_hablante[p1]) * 100
        pct2 = (Data_hablante[p2][c] / contador_palabras_hablante[p2]) * 100

        score = 1 - (abs(pct1 - pct2) / (pct1 + pct2 + 0.0001))
        lsm_scores[c] = score

    total_lsm = sum(lsm_scores.values()) / len(lsm_scores)
    return total_lsm, dict(contador_palabras_hablante), lsm_scores


# --- Cargar y concatenar todos los archivos de una ronda específica ---
def evaluar_ronda(directorio, ronda_target):
    patron_ronda = re.compile(rf"^{ronda_target}_", re.IGNORECASE)
    lineas_concatenadas = []
    archivos_encontrados = 0

    for nombre_archivo in sorted(os.listdir(directorio)):
        if nombre_archivo.endswith(".txt") and patron_ronda.match(
            nombre_archivo
        ):
            ruta_completa = os.path.join(directorio, nombre_archivo)
            with open(ruta_completa, "r", encoding="utf-8") as f:
                lineas_concatenadas.extend(f.readlines())
            archivos_encontrados += 1

    if archivos_encontrados == 0:
        return None

    lsm_total, conteo_palabras, scores_categoria = calculo_LSM_agregado(
        lineas_concatenadas
    )

    if lsm_total is None:
        return None

    hablantes = list(conteo_palabras.keys())
    p1, p2 = hablantes[0], hablantes[1]

    # Armar dict de resultados para esta ronda
    res = {
        "ronda": ronda_target,
        "tareas_unificadas": archivos_encontrados,
        f"palabras_{p1}": conteo_palabras[p1],
        f"palabras_{p2}": conteo_palabras[p2],
        "total_palabras": sum(conteo_palabras.values()),
        "lsm_global": lsm_total,
    }

    # Agregar scores individuales por categoría
    for cat, score in scores_categoria.items():
        res[f"lsm_{cat}"] = score

    return res


# --- EJECUCIÓN PRINCIPAL DE R1 A R8 ---
def ejecutar_todas_las_rondas():
    if not os.path.exists(DIRECTORIO_ALEMAN):
        print(f"Error: No existe el directorio '{DIRECTORIO_ALEMAN}'")
        return

    resultados = []
    rondas_target = [f"r{i}" for i in range(1, 9)]

    print(
        "================================================================="
    )
    print("  PROCESANDO RONDAS AGREGADAS (r1 a r8) - CORPUS GERMAN PENTOCV")
    print(
        "=================================================================\n"
    )

    for ronda in rondas_target:
        print(f"Procesando {ronda.upper()}...", end=" ")
        data_ronda = evaluar_ronda(DIRECTORIO_ALEMAN, ronda)

        if data_ronda:
            resultados.append(data_ronda)
            print(
                f"OK -> Tareas: {data_ronda['tareas_unificadas']} | Palabras: {data_ronda['total_palabras']} | LSM: {data_ronda['lsm_global']:.4f}"
            )
        else:
            print(f"OMITIDO (No se encontraron archivos suficientes).")

    # Crear DataFrame
    df = pd.DataFrame(resultados)

    if not df.empty:
        # Guardar a CSV
        df.to_csv(OUTPUT_CSV, index=False)

        print("\n" + "=" * 65)
        print(" RESUMEN GENERAL DE LSM ACUMULADO POR RONDA")
        print("=" * 65)
        cols_resumen = [
            "ronda",
            "tareas_unificadas",
            "total_palabras",
            "lsm_global",
        ]
        print(df[cols_resumen].to_string(index=False))

        print(f"\nPromedio de LSM entre las 8 rondas: {df['lsm_global'].mean():.4f}")
        print(f"Resultados completos exportados a '{OUTPUT_CSV}'")
    else:
        print("\nNo se pudieron procesar las rondas.")


if __name__ == "__main__":
    ejecutar_todas_las_rondas()


