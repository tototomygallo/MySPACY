# MySPACY

## /CODIGO

### /Herramientas/parseo.py
Script que convierte un archivo a lista de strings (cargar_de_archivo) y tiene la opcion de procesar muchos archivos (cargar_de_lista)

### /LSM/LIWC.py
Es un codigo que recibe un archivo y un directorio de output y calcula media cmd el valor LSM utilizando 100% LIWC


### /LSM/myspacy.py
Este código analiza una conversación entre dos personas y mide qué tan parecido es su estilo al hablar usando LSM (Language Style Matching). Primero, la función `conteo_categorias` procesa un texto con spaCy palabra por palabra para identificar categorías funcionales como pronombres, artículos o preposiciones, devolviendo el conteo de estas y el total de palabras.

Luego, `calculo_LSM` recibe la charla completa y organiza la información en dos diccionarios clave: **user_wc**, que funciona como un contador simple de palabras totales por usuario, y **user_data**, que es como un archivador con cajones donde cada hablante tiene sus propias carpetas con los conteos de sus categorías. Al usar `defaultdict`, el código crea estos cajones automáticamente apenas aparece un usuario nuevo, evitando errores y manteniendo todo ordenado.

Finalmente, el sistema calcula qué porcentaje del habla de cada persona corresponde a cada categoría y compara esos números. Al promediar estas diferencias, genera un resultado entre 0 y 1, donde 1 es sincronía total. Lo más importante es que estos diccionarios se crean y se borran en cada llamada, asegurando que cada archivo se procese de forma independiente sin mezclar datos de distintas conversaciones.

### /main.py
archivo de main

### /Pipeline_muchos_archivos.py
Codigo que procesa los archivos de los distintos corpus y devuelve un csv con los resultados de liwc y spacy para cada uno
