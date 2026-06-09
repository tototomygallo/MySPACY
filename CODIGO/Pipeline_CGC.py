import spacy
import numpy as np
from collections import defaultdict
from Herramientas.parseo import cargar_de_archivo

nlp = spacy.load("en_core_web_md")


# 1 al 15: Diccionario estándar de LIWC
negaciones_liwc = {
    "no", "not", "never", "neither", "nor", "nobody", "nothing", 
    "nowhere", "none", "cannot", "n't", "nope", "ain't"
}
#EL WITHOUT NO SE CUENTA COMO NEGACIÓN EN LIWC ASÍ QUE NO LO INCLUYO EN EL DICCIONARIO.


# 16 al 27: Negaciones semánticas / implícitas (Descomentar si querés probarlas)
#negaciones_semanticas = {
 #   "deny", "pretend", "dismiss", "ignore", "hardly", "barely", 
  #   "lack", "impossible", "refused", "unless", "except", "instead"
#}


# Lista de falsos amigos identificados y derivados a 'ipron' o 'negate'
determinantes_excluidos = {
    "all", "that", "this", "these", "every", "any", "those", "some", "no"
}

def conteo_categorias(text: str):
    """Analiza un texto y devuelve el conteo de categorías."""
    contador = defaultdict(int)
    doc = nlp(text)
    for t in doc:
        if t.is_punct or t.is_space: continue
        low = t.text.lower()
        
        # Lógica de categorías (la que ya tenías pulida)
        if t.pos_ == "PRON":
                    # Si es pronombre personal (I, you, he, she...) y no es 'it' (esto si queremos asemejarnos a LIWC)
                    if t.tag_ in ["PRP", "PRP$"]: #and low != "it": 
                        contador['ppron'] += 1
                        #print(f"PPRON detectado: '{t.text}' en '{text}'")
                    # Si es cualquier otro pronombre (anyone, that, something...)
                    else:
                        contador['ipron'] += 1
        elif t.pos_ == "DET": 
            contador['article'] += 1
            print(f"Artículo detectado: '{t.text}' en '{text}'")  # Debug para ver qué palabras se cuentan como artículos
        elif t.pos_ == "ADP": contador['prep'] += 1
        if t.dep_ == "neg" or low in negaciones_liwc : #!OJO QYE HACER IF Y NO ELIF CAGA POR REPETIDO
            contador['negate'] += 1  #or low in negaciones_semanticas
            #print(f"Negación detectada: '{t.text}' en '{text}'")  # Debug para ver qué palabras se cuentan como negaciones
        elif t.pos_ == "ADV": contador['adverb'] += 1
        # 6. Verbos Auxiliares
        elif t.pos_ == "AUX":
            contador['auxverb'] += 1
            
        # 7. Conjunciones
        # Coordinadas (and, but), SCONJ: Subordinadas (because, if)
        elif t.pos_ in ["CCONJ", "SCONJ"]:
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
    cats = ['ppron', 'ipron', 'article', 'prep', 'negate', 'adverb', 'auxverb', 'conj']
    lsm_scores = []

    print("article hablante 1:", (Data_hablante[p1]['article']/contador_palabras_hablante[p1])*100 if contador_palabras_hablante[p1] > 0 else 0, "total palabras:", contador_palabras_hablante[p1])
    print("article hablante 2:", (Data_hablante[p2]['article']/contador_palabras_hablante[p2])*100 if contador_palabras_hablante[p2] > 0 else 0, "total palabras:", contador_palabras_hablante[p2])
    
    for c in cats:
        # Porcentajes
        pct1 = (Data_hablante[p1][c] / contador_palabras_hablante[p1]) * 100 if contador_palabras_hablante[p1] > 0 else 0
        pct2 = (Data_hablante[p2][c] / contador_palabras_hablante[p2]) * 100 if contador_palabras_hablante[p2] > 0 else 0
        
        # Score por categoría
        score = 1 - (abs(pct1 - pct2) / (pct1 + pct2 + 0.0001))
        lsm_scores.append(score)
        
    return float(np.mean(lsm_scores))

print(calculo_LSM(cargar_de_archivo("/home/tgallo/Documents/Proyecto_modular/article.txt")))