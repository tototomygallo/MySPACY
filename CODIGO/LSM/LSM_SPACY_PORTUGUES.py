from collections import defaultdict
import spacy

# Cargar modelo de portugués
nlp = spacy.load("pt_core_news_md")


def conteo_categorias(text: str):
    """Analiza un texto en portugués y devuelve el conteo de categorías y el total de tokens válidos."""
    contador = defaultdict(int)
    doc = nlp(text)

    # Denominador preciso de spaCy (excluye puntuación y espacios)
    tokens_validos = [t for t in doc if not (t.is_punct or t.is_space)]

    for t in tokens_validos:
        # Atributo morfológico en dict o lista para verificar claves/valores
        polarity = t.morph.get("Polarity")
        prontype = t.morph.get("PronType")
        definite = t.morph.get("Definite")

        # 1. Negaciones (Estricto por marcador morfológico UD)
        if "Neg" in polarity:
            contador["negate"] += 1

        # 2 y 3. Pronombres (Personales/Poseedores vs Impersonales/Otros)
        elif t.pos_ == "PRON":
            if "Prs" in prontype:
                contador["ppron"] += 1
            else:
                contador["ipron"] += 1

        # 4. Artículos (Definidos e Indefinidos)
        elif t.pos_ == "DET" and any(d in definite for d in ["Def", "Ind"]):
            contador["article"] += 1

        # 5. Preposiciones
        elif t.pos_ == "ADP":
            contador["prep"] += 1

        # 6. Adverbios (Evaluado tras negate)
        elif t.pos_ == "ADV":
            contador["adverb"] += 1

        # 7. Verbos Auxiliares
        elif t.pos_ == "AUX":
            contador["auxverb"] += 1

        # 8. Conjunciones (Coordinantes y Subordinantes)
        elif t.pos_ in ["CCONJ", "SCONJ"]:
            contador["conj"] += 1

    return contador, len(tokens_validos)


def calculo_LSM(conversation: list[str], min_palabras: int = 20) -> float:
    """Recibe una lista de strings ["USER: texto", "USER: texto"]

    Devuelve el valor LSM final para portugués.
    """
    Data_hablante = defaultdict(lambda: defaultdict(int))
    contador_palabras_hablante = defaultdict(int)

    # 1. Agrupar todo el texto por usuario
    for line in conversation:
        if ":" not in line:
            continue
        user, text = line.split(":", 1)
        user = user.strip()

        counts, wc = conteo_categorias(text.strip())
        for cat, val in counts.items():
            Data_hablante[user][cat] += val
        contador_palabras_hablante[user] += wc

    # 2. Verificar que haya 2 hablantes
    hablantes_ids = list(Data_hablante.keys())
    if len(hablantes_ids) < 2:
        return None

    # 3. Verificar cantidad mínima de palabras
    p1, p2 = hablantes_ids[0], hablantes_ids[1]

    if (
        contador_palabras_hablante[p1] < min_palabras
        or contador_palabras_hablante[p2] < min_palabras
    ):
        return None

    # 4. Calcular porcentajes y LSM por categoría
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
    lsm_scores = []

    for c in cats:
        # Porcentajes sobre el total de palabras de cada hablante
        pct1 = (Data_hablante[p1][c] / contador_palabras_hablante[p1]) * 100
        pct2 = (Data_hablante[p2][c] / contador_palabras_hablante[p2]) * 100

        # Score por categoría
        score = 1 - (abs(pct1 - pct2) / (pct1 + pct2 + 0.0001))
        lsm_scores.append(score)

    return sum(lsm_scores) / len(lsm_scores)