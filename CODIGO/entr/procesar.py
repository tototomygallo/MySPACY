import spacy   # https://spacy.io/
from spacy.tokens.doc import Doc
#from spacy.lang.es import SpanishDefaults
from spacy.lang.en.stop_words import STOP_WORDS


Word_class = list(STOP_WORDS)
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
    nlpA:list[Doc] = [NLP(t) for t in textsA]
    nlpB:list[Doc] = [NLP(t) for t in textsB]

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