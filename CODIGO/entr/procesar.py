import spacy   # https://spacy.io/
from spacy.tokens.doc import Doc
#from spacy.lang.es import SpanishDefaults
from spacy.lang.en.stop_words import STOP_WORDS
from nltk.corpus import stopwords
from collections import Counter

#Word_class = list(STOP_WORDS)

Word_class = stopwords.words('english')
print(Word_class)
###############################################################################
def read_stopwords(filename) -> list[str]:
    ''' Reads filename into a list of strings. Ignore lines starting with #. '''
    with open(filename) as f:
        return [line.rstrip() for line in f if len(line)>0 and line[0]!="#"]
    
def count_word(word:str, nlp_text:list[Doc], lemmatize:bool=True) -> int:
    ''' Count the occurrences of a (by default, lemmatized) word in a 
        list of NLP-processed sentences. '''
    res:int = 0
    lemma = NLP(word)[0].lemma_.lower()
    for nlp_sentence in nlp_text:
        for token in nlp_sentence:
            if (lemmatize     and token.lemma_.lower() == lemma) or \
               (not lemmatize and token.text.lower() == word.lower()):
                res += 1
    return res

def count_all_words(nlp_text:list[Doc]) -> int:
    ''' Return the number of all words uttered by a speaker in a dialogue.
        'ALL' in Nenkova 2008 '''
    res:int = 0
    for nlp_sentence in nlp_text:
        for token in nlp_sentence:
            if not token.is_punct:
                res += 1
    return res

###############################################################################
# Sobreescribe stopwords con lista curada a mano.
#SpanishDefaults.stop_words = read_stopwords('./stopwords.txt')

# Inicialización del modelo de NLP en espaǹol.
NLP = spacy.load("en_core_web_md")
###############################################################################





def obtener_top_25_corpus(lista_conversaciones) -> list[str]:
    """
    Busca las 25 palabras de contenido lematizadas más frecuentes de TODO el corpus.
    """
    conteo_global = Counter()
    print("Extrayendo las 25 palabras más frecuentes del corpus (Clase 2)...")
    
    for contenido in lista_conversaciones:
        for linea in contenido:
            if not (linea.startswith("A:") or linea.startswith("B:")): continue
            texto = linea.split(":", 1)[1].strip()
            doc = NLP(texto)
            for token in doc:
                if not token.is_punct and not token.is_space:
                    lemma = token.lemma_.lower()
                    # Filtramos stopwords para quedarnos solo con palabras de contenido
                    if lemma not in STOP_WORDS and lemma.isalpha():
                        conteo_global[lemma] += 1
                        
    top_25 = [word for word, count in conteo_global.most_common(25)]
    print(f"Top 25 de contenido: {top_25}")
    return top_25







def compute_ENTR(textsA:list[str], textsB:list[str], word_class:list[str], lemmatize:bool=True) -> dict[str,float]:
    """Compute ENTR1 and ENTR2 for two speakers given their texts as lists of utterances.

    Parameters:
    - textsA, textsB: lists of utterance strings for speaker A and B (required).
    - word_class: list of lexical items (e.g., stopwords or most-frequent words).
    - lemmatize: whether to compare lemmas (default True).

    Returns a dictionary with keys 'entr1', 'entr2'. If a metric cannot be 
    computed (e.g., division by zero) the corresponding value is None.
    """
    
    # Run NLP on each text in the list, resulting in a list of Doc objects.
    # (spacy.tokens.doc.Doc). Each Doc object has the words with its
    # corresponding attributes (e.g.: lemma_, pos_, dep_, is_stop).

    # CORRECCIÓN: Quitamos el "A:" o "B:" antes de dárselo a spaCy para no ensuciar los tokens
    clean_A = [t.split(":", 1)[1].strip() if ":" in t else t for t in textsA]
    clean_B = [t.split(":", 1)[1].strip() if ":" in t else t for t in textsB]
    
    nlpA:list[Doc] = [NLP(t) for t in clean_A]
    nlpB:list[Doc] = [NLP(t) for t in clean_B]

    print(nlpA)
    print(nlpB)

    # Count all words from each speaker.
    ALL_A = count_all_words(nlpA)
    ALL_B = count_all_words(nlpB)

    # Compute ENTR1 and ENTR2.
    entr1:float = 0.0
    entr2_dividend:float = 0.0
    entr2_divisor:float = 0.0
    for w in word_class:
        count_A_w = count_word(w, nlpA, lemmatize=lemmatize)
        count_B_w = count_word(w, nlpB, lemmatize=lemmatize)
        
        if ALL_A>0 and ALL_B>0:  # prevent division by 0
            entr1 -= abs((count_A_w / ALL_A) - (count_B_w / ALL_B))
        
        entr2_dividend += abs(count_A_w - count_B_w)
        entr2_divisor += (count_A_w + count_B_w)
    
    res:dict[str][float] = dict()
    res['entr1'] = entr1 if (ALL_A>0 and ALL_B>0) else None
    res['entr2'] = -(entr2_dividend / entr2_divisor) if entr2_divisor!=0.0 else None
    return res



def compute_ENTR_dinamico_LSM(textsA: list[str], textsB: list[str]) -> dict[str, float]:
    """
    Calcula ENTR1 y ENTR2 para la Clase 3 (Unión dinámica de categorías LSM).
    En lugar de una lista estática, la bolsa de palabras se genera extrayendo 
    los lemmas que pertenezcan a las categorías funcionales de LSM en ESTE diálogo.
    """
    # 1. Limpieza y procesamiento con spaCy
    clean_A = [t.split(":", 1)[1].strip() if ":" in t else t for t in textsA]
    clean_B = [t.split(":", 1)[1].strip() if ":" in t else t for t in textsB]
    
    nlpA = [NLP(t) for t in clean_A]
    nlpB = [NLP(t) for t in clean_B]

    ALL_A = count_all_words(nlpA)
    ALL_B = count_all_words(nlpB)

    # 2. Definimos las categorías de LSM estándar (las POS tags de spaCy)
    # Ajustalas si en tu script usás etiquetas sutilmente distintas (ej: AUX, PRON, DET, ADP, ADV, CCONJ, SCONJ)
    CATEGORIAS_LSM = {"PRON", "DET", "ADP", "ADV", "AUX", "CCONJ", "SCONJ"}

    # 3. Armamos la "Clase 3" de forma dinámica: la unión de todas las palabras LSM presentes en el diálogo
    bolsa_clase3 = set()
    
    for doc in nlpA + nlpB:
        for token in doc:
            if token.pos_ in CATEGORIAS_LSM and not token.is_punct or token.dep_ == "neg":
                bolsa_clase3.add(token.lemma_.lower())

    # 4. Calculamos las métricas usando esa bolsa específica del diálogo
    entr1 = 0.0
    entr2_dividend = 0.0
    entr2_divisor = 0.0
    
    for lemma_w in bolsa_clase3:
        # Contamos directamente usando el lemma ya extraído
        count_A_w = sum(1 for doc in nlpA for t in doc if t.lemma_.lower() == lemma_w)
        count_B_w = sum(1 for doc in nlpB for t in doc if t.lemma_.lower() == lemma_w)
        
        if ALL_A > 0 and ALL_B > 0:
            entr1 -= abs((count_A_w / ALL_A) - (count_B_w / ALL_B))
        
        entr2_dividend += abs(count_A_w - count_B_w)
        entr2_divisor += (count_A_w + count_B_w)
    
    res = {}
    res['entr1'] = entr1 if (ALL_A > 0 and ALL_B > 0) else None
    res['entr2'] = -(entr2_dividend / entr2_divisor) if entr2_divisor != 0.0 else None
    return res

###############################################################################

if __name__=="__main__":
    # Ejemplo de uso.
    textsA = ["Hello", "This is a test dialogue.", "These are the things the speaker said."]
    textsB = ["Good afternoon", "These are the sentences the other speaker said."]
    d:dict[str,float] = compute_ENTR(textsA, textsB, Word_class, lemmatize=True)
    print('ENTR1_stopwords: ' + str(d['entr1']))
    print('ENTR2_stopwords: ' + str(d['entr2']))

    MFWords = ["this", "is", "that", "speaker", "said"]

    d_mfw = compute_ENTR(textsA, textsB, MFWords, lemmatize=True)

    print('ENTR1_MFW: ' + str(d_mfw['entr1']))
    print('ENTR2_MFW: ' + str(d_mfw['entr2']))