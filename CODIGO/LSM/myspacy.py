import spacy
import numpy as np
from collections import defaultdict

nlp = spacy.load("en_core_web_md")

def get_functional_counts(text: str):
    """Analiza un texto y devuelve el conteo de categorías funcionales."""
    counts = defaultdict(int)
    doc = nlp(text)
    for t in doc:
        if t.is_punct or t.is_space: continue
        low = t.text.lower()
        
        # Lógica de categorías (la que ya tenías pulida)
        if t.pos_ == "PRON":
            if t.tag_ in ["PRP", "PRP$"] and low != "it": counts['ppron'] += 1
        elif t.pos_ == "DET": counts['article'] += 1
        elif t.pos_ == "ADP": counts['prep'] += 1
        elif t.dep_ == "neg": counts['negate'] += 1
        elif t.pos_ == "ADV": counts['adverb'] += 1
    
    return counts, len(text.split())

def compute_LSM(conversation: list[str]) -> float:
    """
    Recibe una lista de strings ["USER: texto", "USER: texto"]
    Devuelve el valor LSM final.
    """
    user_data = defaultdict(lambda: defaultdict(int))
    user_wc = defaultdict(int)
    
    # 1. Agrupar todo el texto por usuario
    for line in conversation:
        if ":" not in line: continue
        user, text = line.split(":", 1)
        user = user.strip()
        
        counts, wc = get_functional_counts(text.strip())
        for cat, val in counts.items():
            user_data[user][cat] += val
        user_wc[user] += wc

    # 2. Verificar que haya 2 hablantes
    uids = list(user_data.keys())
    if len(uids) < 2: return 0.0
    
    # 3. Calcular porcentajes y LSM
    p1, p2 = uids[0], uids[1]
    cats = ['ppron', 'ipron', 'article', 'prep', 'negate', 'adverb']
    lsm_scores = []
    
    for c in cats:
        # Porcentajes
        pct1 = (user_data[p1][c] / user_wc[p1]) * 100 if user_wc[p1] > 0 else 0
        pct2 = (user_data[p2][c] / user_wc[p2]) * 100 if user_wc[p2] > 0 else 0
        
        # Score por categoría
        score = 1 - (abs(pct1 - pct2) / (pct1 + pct2 + 0.0001))
        lsm_scores.append(score)
        
    return float(np.mean(lsm_scores))