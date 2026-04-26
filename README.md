# MySPACY

## CODIGO
### /LIWC.py
    Es un codigo que recibe un archivo y un directorio de output y calcula media cmd el valor LSM utilizando 100% LIWC

### /myspacy.py
    Este código analiza una conversación entre dos personas y mide qué tan parecido es su estilo al escribir o hablar, usando algo llamado LSM (Language Style Matching).

    Primero, la función conteo_categorias recibe un texto y lo procesa con spaCy. Ahí va palabra por palabra viendo qué tipo de función cumple cada una (pronombres, artículos, preposiciones, negaciones, adverbios, etc.). Con eso va armando un conteo de cuántas veces aparece cada categoría en el texto y también devuelve cuántas palabras totales tiene ese fragmento.
    
    Después, calculo_LSM recibe la conversación completa como una lista de strings tipo "USER: texto". Ahí separa lo que dice cada usuario y va acumulando dos cosas: por un lado user_data, que guarda los conteos de categorías por persona, y por otro user_wc, que guarda cuántas palabras totales dijo cada uno.
    
    Con eso, calcula porcentajes de uso de cada categoría (por ejemplo, qué proporción de sus palabras son pronombres o artículos) y compara esos porcentajes entre los dos usuarios. Para cada categoría saca un score que mide qué tan parecidos son, y después promedia todos esos scores.
    
    El resultado final es un número entre 0 y 1: valores cercanos a 1 significan que ambos tienen estilos de lenguaje muy similares, y valores cercanos a 0 indican que hablan bastante distinto.
