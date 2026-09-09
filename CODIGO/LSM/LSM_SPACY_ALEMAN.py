import spacy
from collections import defaultdict
from Herramientas.parseo import cargar_de_archivo

# Cargar el modelo en alemán (asegurate de tenerlo descargado: python -m spacy download de_core_news_md)
nlp = spacy.load("de_core_news_md")


def conteo_categorias(text: str):
    """Analiza un texto en alemán y devuelve el conteo de las 8 categorías funcionales de LSM."""
    contador = defaultdict(int)
    doc = nlp(text)

    # Lemas de auxiliares principales en alemán
    LEMAS_AUX = {"sein", "haben", "werden"}

    for t in doc:
        if t.is_punct or t.is_space:
            continue

        tag = t.tag_  # Etiqueta STTS fina para alemán
        lemma = t.lemma_.lower()

        # 1. Negaciones ('nicht' o determinantes negativos como 'kein/keine')
        if tag == "PTKNEG" or lemma == "kein":
            contador["negate"] += 1

        # 2. Pronombres Personales (ich, du, er, sich, mein, dein...)
        elif tag in ["PPER", "PRF", "POSS"]:
            contador["ppron"] += 1

        # 3. Pronombres Impersonales/Demostrativos (das, dies, jemand, wer...)
        elif tag in ["PIS", "PDS", "PDAT", "PWS", "PWAT", "PRELS"]:
            contador["ipron"] += 1

        # 4. Artículos (der, die, das, ein, eine...)
        elif tag == "ART":
            contador["article"] += 1

        # 5. Preposiciones (in, auf, mit y fusiones como im, am, zum)
        elif tag in ["APPR", "APPRART", "APPO"]:
            contador["prep"] += 1

        # 6. Adverbios (hier, da, schnell, damit, darüber...)
        elif tag in ["ADV", "PAV"]:
            contador["adverb"] += 1

        # 7. Verbos Auxiliares (formas conjugadas de sein, haben, werden)
        elif tag.startswith("VA") or (
            t.pos_ in ["VERB", "AUX"] and lemma in LEMAS_AUX
        ):
            contador["auxverb"] += 1

        # 8. Conjunciones (und, oder, aber, weil, dass...)
        elif tag in ["KON", "KOUS", "KOUI"] or t.pos_ in ["CCONJ", "SCONJ"]:
            contador["conj"] += 1

    return contador, len(text.split())

def calculo_LSM(conversation: list[str], min_palabras: int = 20) -> float:
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

    
    # 2. Verificar que haya 2 hablantes
    hablantes_ids = list(Data_hablante.keys())
    if len(hablantes_ids) < 2: return None
    
    # 3. Calcular porcentajes y LSM
    p1, p2 = hablantes_ids[0], hablantes_ids[1]

    # 3. Verificar cantidad mínima de palabras
    if (contador_palabras_hablante[p1] < min_palabras or
        contador_palabras_hablante[p2] < min_palabras):
        return None

    cats = ['ppron', 'ipron', 'article', 'prep', 'negate', 'adverb', 'auxverb', 'conj']
    lsm_scores = []
    
    for c in cats:
        # Porcentajes
        pct1 = (Data_hablante[p1][c] / contador_palabras_hablante[p1]) * 100
        pct2 = (Data_hablante[p2][c] / contador_palabras_hablante[p2]) * 100
        
        # Score por categoría
        score = 1 - (abs(pct1 - pct2) / (pct1 + pct2 + 0.0001))
        lsm_scores.append(score)
        
    return sum(lsm_scores) / len(lsm_scores)

