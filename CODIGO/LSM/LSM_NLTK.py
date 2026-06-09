import spacy
import numpy as np
from collections import defaultdict
from Herramientas.parseo import cargar_de_archivo
import nltk


nlp = spacy.load("en_core_web_md")

def conteo_categorias(text: str):
    """Analiza un texto y devuelve el conteo de categorías."""
    contador = defaultdict(int)
    tokens = nltk.word_tokenize(text)
    tags = nltk.pos_tag(tokens)
    for word, tag in tags:
        low = word.lower()
        if tag in ["PRP", "PRP$"]: #PPRONS
            contador['ppron'] += 1
        elif tag in ["WP", "WP$", "WDT"]: #IPRONS
            contador['ipron'] += 1
        elif tag == "DT": #ARTICLES y mas determinantes
            contador['article'] += 1
        elif tag == "IN": #? PREP OJO QUE IN TAMBIÉN TAGGEA PARA CONJ SUBORDINADAS
            contador['prep'] += 1
        #elif tag == "RB" and low == "not": #!ENCONTRAR MANERA DE IDENTIFICAR NEGATE EN NLTK
            #contador['negate'] += 1
        elif tag == "RB" or (tag == "RBR" or tag == "RBS"): #ADVERBS normales, comparativos y superlativos #! SOLO MODALES, FALTA INCLUIR LOS VERBOS to be, have y do como AUXVERBS
            contador['adverb'] += 1 
        elif tag in ["MD"]:
            contador['auxverb'] += 1
        elif tag in ["CC"]:
            contador['conj'] += 1    
    return contador, len(text.split())

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
    cats = ['ppron', 'ipron', 'article', 'prep', 'adverb', 'auxverb', 'conj']
    lsm_scores = []
    
    for c in cats:
        # Porcentajes
        pct1 = (Data_hablante[p1][c] / contador_palabras_hablante[p1]) * 100 if contador_palabras_hablante[p1] > 0 else 0
        pct2 = (Data_hablante[p2][c] / contador_palabras_hablante[p2]) * 100 if contador_palabras_hablante[p2] > 0 else 0
        
        # Score por categoría
        score = 1 - (abs(pct1 - pct2) / (pct1 + pct2 + 0.0001))
        lsm_scores.append(score)
        
    return float(np.mean(lsm_scores))

