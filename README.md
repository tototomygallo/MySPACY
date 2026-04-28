# My 🐔 SPACY 🌌


Este proyecto implementa un sistema de análisis de **Language Style Matching (LSM)** para medir la mimetización lingüística en conversaciones, comparando un desarrollo propio basado en **spaCy** con los resultados del software **LIWC-22**.

## Requerimientos e Instalación

Para ejecutar este proyecto, necesitas Python 3.8 o superior y las siguientes librerías:

1. **Instalar dependencias de Python:**
   ```bash
   pip install spacy pandas numpy

2. **Descargar el modelo de lenguaje de spaCy:**
   ```bash
   python -m spacy download en_core_web_md
   
3. **Software externo (LIWC-22):**
   Es necesario tener instalado el LIWC-22-cli y configurar la ruta correcta en los scripts de la carpeta /LSM.

## Estructura del proyecto

### /CODIGO

#### /Herramientas/parseo.py
Script que convierte un archivo a lista de strings (cargar_de_archivo) y tiene la opcion de procesar muchos archivos (cargar_de_lista)

#### /LSM/LIWC.py
Es un codigo que recibe un archivo y un directorio de output y calcula media cmd el valor LSM utilizando 100% LIWC


#### /LSM/myspacy.py
Este código analiza una conversación entre dos personas y mide qué tan parecido es su estilo al hablar usando LSM (Language Style Matching). Primero, la función `conteo_categorias` procesa un texto con spaCy palabra por palabra para identificar categorías funcionales como pronombres, artículos o preposiciones, devolviendo el conteo de estas y el total de palabras.

Luego, `calculo_LSM` recibe la charla completa y organiza la información en dos diccionarios clave: **contador_palabras_hablante**, que funciona como un contador simple de palabras totales por usuario, y **Data_hablante** donde cada hablante tiene sus propias claves ("categorias") con los conteos. Al usar `defaultdict`, el código crea estas claves automáticamente apenas aparece un usuario nuevo, evitando errores y manteniendo todo ordenado.

Finalmente, el sistema calcula qué porcentaje del habla de cada persona corresponde a cada categoría y compara esos números. Al promediar estas diferencias, genera un resultado entre 0 y 1, donde 1 es mimetización total. Lo más importante es que estos diccionarios se crean y se borran en cada llamada, asegurando que cada archivo se procese de forma independiente sin mezclar datos de distintas conversaciones.

#### /LSM/probar_LIWC_subprocess.py
Prueba de calcular LSM con cmd de LIWC de una conversacion pasada por parametro y una carpeta de output

#### /main.py
archivo de main para testear conversaciones inventadas

### /Pipeline_muchos_archivos.py
Codigo que procesa los archivos de los distintos corpus y devuelve un csv con los resultados de liwc y spacy para cada uno
