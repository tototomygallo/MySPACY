import spacy
import numpy as np
from collections import defaultdict

nlp = spacy.load("es_core_news_md")


def es_negacion(t):
    return (
        t.lemma_.lower() == "no" or
        t.dep_ == "neg" or
        "Neg" in t.morph.get("PronType") or
        "Neg" in t.morph.get("Polarity")
    )


def conteo_categorias(text: str):
    contador = defaultdict(int)
    doc = nlp(text)

    for t in doc:
        if t.is_punct or t.is_space:
            continue

        # Negaciones
        if es_negacion(t):
            contador["negate"] += 1

        # Pronombres
        elif t.pos_ == "PRON":
            pron_type = t.morph.get("PronType")

            if "Prs" in pron_type:
                contador["ppron"] += 1
            else:
                contador["ipron"] += 1

        # Artículos
        elif t.pos_ == "DET":
            # opcional: contar solo artículos
            if "Art" in t.morph.get("PronType"):
                contador["article"] += 1

        # Preposiciones
        elif t.pos_ == "ADP":
            contador["prep"] += 1

        # Adverbios
        elif t.pos_ == "ADV":
            contador["adverb"] += 1

        # Auxiliares
        elif t.pos_ == "AUX":
            contador["auxverb"] += 1

        # Conjunciones
        elif t.pos_ in ("CCONJ", "SCONJ"):
            contador["conj"] += 1

    return contador, len([t for t in doc if not (t.is_space or t.is_punct)])


def calculo_LSM(conversation: list[str]) -> float:
    """
    Recibe una lista de strings ["USER: texto", "USER: texto"]
    Devuelve el valor LSM final.
    """
    Data_hablante = defaultdict(lambda: defaultdict(int))
    contador_palabras_hablante = defaultdict(int)
    
    # 1. Agrupao todo el texto por usuario
    for line in conversation:
        if ":" not in line: continue
        user, text = line.split(":", 1)
        user = user.strip()
        
        counts, wc = conteo_categorias(text.strip())
        for cat, val in counts.items():
            Data_hablante[user][cat] += val
        contador_palabras_hablante[user] += wc

    print(contador_palabras_hablante)
    # 2. Verificar que haya 2 hablantes
    hablantes_ids = list(Data_hablante.keys())
    if len(hablantes_ids) < 2: return 0.0
    
    # 3. Calcular porcentajes y LSM
    p1, p2 = hablantes_ids[0], hablantes_ids[1]
    cats = ['ppron', 'ipron', 'article', 'prep', 'negate', 'adverb', 'auxverb', 'conj']
    lsm_scores = []
    
    for c in cats:
        # Porcentajes
        pct1 = (Data_hablante[p1][c] / contador_palabras_hablante[p1]) * 100 if contador_palabras_hablante[p1] > 0 else 0
        pct2 = (Data_hablante[p2][c] / contador_palabras_hablante[p2]) * 100 if contador_palabras_hablante[p2] > 0 else 0
        
        # Score por categoría
        score = 1 - (abs(pct1 - pct2) / (pct1 + pct2 + 0.0001))
        lsm_scores.append(score)
        
    return float(np.mean(lsm_scores))


if __name__ == "__main__":

    conversation = [
        "A: Creo que no vamos a poder ir hoy porque está complicado.",
        "B: Sí, creo que no vamos a poder ir hoy, está bastante complicado.",

        "A: Alguien debería avisar que se cancela la reunión.",
        "B: Sí, alguien tendría que avisar que se cancela la reunión.",

        "A: Nadie respondió todavía, es raro.",
        "B: Nadie respondió aún, es bastante raro.",

        "A: Si no mejora el clima, lo dejamos para mañana.",
        "B: Si no mejora el clima, mejor lo dejamos para mañana.",

        "A: Eso no cambia demasiado las cosas.",
        "B: Eso no cambia demasiado la situación.",

        "A: Bueno, entonces no hay mucho más que hacer.",
        "B: Bueno, entonces no hay mucho más que hacer."
    ]

    score = calculo_LSM(conversation)

    print("\nLSM final:", score)