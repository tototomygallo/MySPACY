import spacy
from collections import defaultdict

nlp = spacy.load("en_core_web_md")

def auditar_categorias(text: str):
    """Analiza el texto y guarda las palabras encontradas en cada categoría."""
    # En lugar de sumar 1, guardamos la palabra en una lista
    hallazgos = defaultdict(list)
    doc = nlp(text)
    
    for t in doc:
        if t.is_punct or t.is_space: continue
        low = t.text.lower()
        
        categoria = None
        
        # Misma lógica de tu función original
        if t.pos_ == "PRON":
            if t.tag_ in ["PRP", "PRP$"]:
                categoria = 'ppron'
            else:
                categoria = 'ipron'
        elif t.pos_ == "DET": 
            categoria = 'article'
        elif t.pos_ == "ADP": 
            categoria = 'prep'
        elif t.dep_ == "neg": 
            categoria = 'negate'
        elif t.pos_ == "ADV": 
            categoria = 'adverb'
        elif t.pos_ == "AUX":
            categoria = 'auxverb'
        elif t.pos_ in ["CCONJ", "SCONJ"]:
            categoria = 'conj'
            
        if categoria:
            hallazgos[categoria].append(low)
            
    return hallazgos, len(text.split())

def calculo_manual(file_path):
    print(f"=== REPORTE DE AUDITORÍA PARA CÁLCULO MANUAL ===")
    print(f"Archivo: {file_path}\n")
    
    # Agrupamos por hablante
    auditoria_hablantes = defaultdict(lambda: defaultdict(list))
    word_counts = defaultdict(int)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if ":" not in line: continue
            user, text = line.split(":", 1)
            user = user.strip()
            
            halls, wc = auditar_categorias(text.strip())
            for cat, lista_palabras in halls.items():
                auditoria_hablantes[user][cat].extend(lista_palabras)
            word_counts[user] += wc

    # Mostrar resultados
    categorias_orden = ['ppron', 'ipron', 'article', 'prep', 'negate', 'adverb', 'auxverb', 'conj']
    
    for user, cats in auditoria_hablantes.items():
        print(f"👤 HABLEANTE: {user}")
        print(f"   Word Count Total (Denominador): {word_counts[user]}")
        print("-" * 40)
        
        for c in categorias_orden:
            palabras = cats.get(c, [])
            conteo = len(palabras)
            pct = (conteo / word_counts[user] * 100) if word_counts[user] > 0 else 0
            
            print(f"   [{c.upper()}]: {conteo} palabras ({pct:.2f}%)")
            print(f"   👉 Palabras: {palabras if palabras else 'Ninguna'}")
            print("")
        print("=" * 50)

if __name__ == "__main__":
    # Poné acá el nombre de uno de los archivos que te dio el profe
    ruta_test = "archivos_unitest/4_3_RoundB_all.txt" 
    try:
        calculo_manual(ruta_test)
    except FileNotFoundError:
        print(f"No encontré el archivo {ruta_test}. Asegurate de que esté en la misma carpeta.")