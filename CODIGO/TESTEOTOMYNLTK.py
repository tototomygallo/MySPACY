
import nltk


"""

Sigla,Significado en Inglés,Tu categoría LSM
PRP | PRP$, (Personal | Possessive Pronoun,ppron)
WP | WP$,"Wh-pronoun (Who, Whose)",ipron
DT,Determiner,article (si es the/a) o ipron
IN,Preposition / Subordinating Conj.,prep o conj (según palabra)
CC,Coordinating Conjunction,conj
MD,"Modal (can, could, should)",auxverb
RB,Adverb,"adverb (o negate si es ""not"")"
VB...,Verb (distintas formas),"auxverb (solo si es be, have, do)"
TO
"""

#tokens = nltk.word_tokenize("Well, um. You chose to negotiate, you had 1200, and I was leaving with 200. What were you planning to do? It's 1800 pesos. To split. To split, it's 1800 pesos. Right. Do you accept 700 and I take 1100? Can we settle at 1000? I mean, you 1000 and me 800.Yes.Yeah? Okay. So X receives 1000 and I get 800.")
#tokens = nltk.word_tokenize("So how are you")
# [('The', 'DT'), ('cat', 'NN'), ('sat', 'VBD'), ...]
#tags = nltk.pos_tag(tokens)

#print(tags)


import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("I do not eat fish never. i have to go to the store. I can do it. I will do it. I should do it. I would do it. I might do it. I must do it. I need to do it.")

for token in doc:
    print(token.text, token.pos_, token.dep_)