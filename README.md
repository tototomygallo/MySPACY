# My SPACY — Análisis de alineamiento lingüístico

Este proyecto calcula Language Style Matching (LSM) con LIWC-22, NLTK y spaCy, y métricas de entropía (ENTR1/ENTR2) sobre corpus dialogados. El punto de llegada del análisis es **`GRAFICO/PLOTTER_FINAL.ipynb`**.

Esta guía describe el flujo que necesita ese notebook: datos originales → conversaciones procesadas → bases LIWC → resultados LSM/ENTR → gráficos. Los scripts `CODIGO/Pipeline_CGC.py`, `CODIGO/Pipeline_SCOTUS.py` y `CODIGO/Pipeline_muchos_archivos.py` son versiones anteriores y **no se ejecutan en este flujo**.

## 1. Preparar el entorno

Ejecutar todos los comandos desde la raíz del repositorio, donde está este README. Las salidas con rutas relativas se escriben respecto del directorio de trabajo, no respecto del script.

Se recomienda Python 3.10 o 3.11 para preparar el entorno. No hay versiones de dependencias fijadas en el repositorio; estos comandos no garantizan reproducir exactamente un entorno histórico.

En Windows / PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install spacy nltk pandas numpy scipy matplotlib seaborn jupyterlab openai
```

En Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install spacy nltk pandas numpy scipy matplotlib seaborn jupyterlab openai
```

Recursos utilizados por los scripts del flujo final:

```bash
python -m spacy download en_core_web_md
python -m spacy download es_core_news_md
python -m spacy download pt_core_news_md
python -m spacy download de_core_news_sm
python -c "import nltk; [nltk.download(r) for r in ['stopwords', 'punkt', 'punkt_tab', 'averaged_perceptron_tagger', 'averaged_perceptron_tagger_eng']]"
```

`PRUEBA_ALEMAN.py`, que genera el CSV de PENTO leído por el notebook, usa `de_core_news_sm`. El script alternativo `procesar_spacy_aleman.py` usa `de_core_news_md`, pero produce otro CSV y no es necesario para este flujo. La variante NLTK también carga `en_core_web_md` al importar su módulo.

Para regenerar las bases LIWC se necesita una instalación habilitada de **LIWC-22 CLI**. Para regenerar las traducciones UBA se necesita una clave de la API de OpenAI; no se necesita para leer traducciones o CSV ya generados.

## 2. Ajustar las rutas antes de ejecutar

Los scripts y el notebook contienen rutas absolutas de la máquina original (`/home/tgallo/Documents/Proyecto_modular` y `/home/tgallo/Downloads`). Deben editarse para apuntar a la ubicación real del repositorio y de los corpus. No hay un argumento de línea de comandos que reemplace esas constantes.

En Windows se pueden escribir rutas como `Path("C:/Users/usuario/Documents/MySPACY/...")` o cadenas con `/`. Mantener los nombres de las carpetas procesadas: algunos gráficos filtran por su nombre.

| Etapa | Archivo y variables que se deben revisar |
| --- | --- |
| Switchboard | `CODIGO/Preprocesar_swboard.py`: `RUTA_DATOS`, `RUTA_SALIDA` |
| CGC | `CODIGO/cgcdiezporciento.py`: `RUTA_CGC`, `RUTA_MUESTRA` |
| SCOTUS | `CODIGO/scotusdiezprcnto.py`: `RUTA_SCOTUS`, `RUTA_MUESTRA` |
| Bases LIWC | `CODIGO/PreprocesarLIWC_SW.py` y `PreprocesarLIWC_CGC.py`: `DIRECTORIO_SW`; `PreprocesarLIWC_SCOTUS.py`: `RUTA_MUESTRA` |
| LSM inglés | `CODIGO/procesar_spacy_sw.py` y `procesar_spacy_cgc.py`: `DIRECTORIO_SW`; `procesar_spacy_scotus_vfinal.py`: `RUTA_SCOTUS_100` |
| UBA B1 | `CODIGO/preprocesar_UBA_GC_B1.py`: `PHRASES_DIR`, `TASKS_DIR`, `OUTPUT_DIR` |
| UBA B2 | `CODIGO/preprocesar_UBA_GC_B2.py`: `INPUT_DIR`, `OUTPUT_DIR` |
| UBA español | `CODIGO/procesar_spacy_ubagames.py`: `DIR_B1`, `DIR_B2` |
| Traducciones | `CODIGO/Preprocesar_traduccion_uba_B1.py` y `Preprocesar_traduccion_uba_B2.py`: `DIR_ENTRADA`, `DIR_SALIDA` |
| UBA inglés | `CODIGO/procesar_spacy_ubagames_EN.py`: `DIR_B1`, `DIR_B2` |
| Portugués | `portuguesss.py`: `DIRECTORIO_ENTRADA`, `DIRECTORIO_SALIDA`; `CODIGO/procesar_spacy_portugues.py`: `DIRECTORIO_PORTUGUES` |
| PENTO | `CODIGO/pento.py`: `CARPETA_EAF`, `CARPETA_TXT`; `CODIGO/PRUEBA_ALEMAN.py`: `DIRECTORIO_ALEMAN` |
| Entropía | `CODIGO/entr/run_entr_sw.py` y `run_entr_cgc.py`: `DIRECTORIO_SW`; `run_entr_scotus.py`: `RUTA_MUESTRA` |

Para CGC, la ruta existente en esta copia es `CGC-transcripts-v2/out`; el script todavía menciona `CGC-transcripts-v2 (1)/out`. Ajustarla al directorio que realmente se tenga.

## 3. Generar las conversaciones de entrada

Las conversaciones procesadas usan una intervención por línea, con el formato `hablante: texto`. Los corpus originales son entradas del proyecto, no resultados de los scripts: deben obtenerse por separado si no están disponibles. Esta copia incluye carpetas de CGC, SCOTUS y Switchboard procesado, pero no todas las entradas externas necesarias para regenerar las demás ramas.

### 3.1. Switchboard

Entrada: transcripciones alineadas por palabra en `swb_ms98_transcriptions`, con archivos `.text` de ambos canales. `Herramientas/formato_liwc.py` es un módulo auxiliar llamado por el preprocesador; no se ejecuta con `--input_dir` o `--output_dir`.

```bash
python CODIGO/Preprocesar_swboard.py
```

El script busca pares de hablantes, toma el **10% de los pares** y los convierte en conversaciones `.phrases` dentro de `SW_PROCESSED/`. Usa `random.sample` sin semilla fija: volver a generar la muestra puede cambiar los archivos seleccionados. Para reproducir los resultados existentes, conservar `SW_PROCESSED/`; para una nueva corrida reproducible, fijar una semilla antes del muestreo y conservar la muestra resultante.

### 3.2. CGC

Entrada: conversaciones `.phrases` ya preparadas en `CGC-transcripts-v2/out/`.

```bash
python CODIGO/cgcdiezporciento.py
```

Agrupa los archivos por sesión (prefijo anterior al primer punto), selecciona sesiones con semilla 42 y copia todas sus tareas a `muestra_cgc/`. El valor actual `PORCENTAJE_MUESTRA = 1` selecciona **100% de las sesiones**, aunque el nombre del script y algunos comentarios mencionen otros porcentajes.

### 3.3. SCOTUS

Entrada: transcripciones `.txt` con líneas `hablante: texto` en `scotus-transcripts/out/`.

```bash
python CODIGO/scotusdiezprcnto.py
```

Copia las transcripciones a `muestra_scotus/`. El valor actual `PORCENTAJE_MUESTRA = 1` selecciona **100% de los archivos**, con semilla 42.

Los scripts de copia no vacían las carpetas de salida. Si se cambia la selección, usar una carpeta de destino limpia para evitar mezclar muestras de corridas anteriores.

## 4. Generar las bases LIWC una sola vez por muestra

Antes de ejecutar, revisar `CODIGO/LSM/LIWC.py`:

- Cambiar `/opt/liwc-22/bin/LIWC-22-cli` por la ruta real del ejecutable.
- Mantener `OUTPUT_LIWC = "tests/"` en los preprocesadores: el wrapper lee explícitamente `tests/LSM-Speaker-Pairwise.csv` con separador `:`.
- Comprobar que la instalación de LIWC produzca ese archivo y la columna `LSM` con las opciones del wrapper.
- La última línea del módulo es una llamada de prueba a `computar_LSM_LIWC(...)` que se ejecuta al importarlo. Comentar esa línea antes de regenerar bases para evitar una llamada extra con una ruta de prueba antigua.

Crear `tests/` si no existe y ejecutar las bases de forma secuencial: comparten los nombres de salida temporal de LIWC.

```bash
python CODIGO/PreprocesarLIWC_SW.py
python CODIGO/PreprocesarLIWC_CGC.py
python CODIGO/PreprocesarLIWC_SCOTUS.py
```

| Entrada | Base producida en la raíz | Columnas |
| --- | --- | --- |
| `SW_PROCESSED/` | `LIWC_SW_BASE.csv` | `archivo`, `lsm_liwc` |
| `muestra_cgc/` | `LIWC_CGC_BASE.csv` | `archivo`, `lsm_liwc` |
| `muestra_scotus/` | `LIWC_SCOTUS_BASE.csv` | `id_virtual`, `lsm_liwc` |

Para SW y CGC se crea una entrada temporal con encabezado `id:text`. Para SCOTUS se eligen hasta los tres hablantes con más intervenciones, se forman sus pares y se exige un mínimo de seis intervenciones por hablante. La clave de cada par es `<nombre_sin_txt>_<hablante1>_vs_<hablante2>` (`id_virtual`). Las entradas temporales se eliminan al terminar cada intento; las bases maestras se conservan.

Si ya se dispone de bases válidas para la misma muestra, se puede omitir esta etapa. Si cambia la muestra o la selección de pares, regenerar las bases.

## 5. Generar los nueve CSV de comparación contra LIWC

Cada procesador calcula LSM local y hace un cruce interno con su base LIWC. Los archivos que no coinciden o tienen métricas inválidas quedan fuera del resultado. La implementación actual también elimina LSM local igual a cero.

Ejecutar **tres veces cada script**. En cada ejecución, dejar activo un único import de `calculo_LSM` y cambiar también el nombre del archivo de salida para guardar el resultado de cada modelo en un CSV distinto.

| Modelo | Import activo | Prefijo de salida |
| --- | --- | --- |
| NLTK | `from LSM.LSM_NLTK import calculo_LSM` | `LSM_NLTK_` |
| spaCy | `from LSM.LSM_SPACY import calculo_LSM` | `LSM_SPACY_` |
| spaCy Mod | `from LSM.LSM_SPACY_mod import calculo_LSM` | `LSM_SPACY_MOD_` |

| Corpus | Script | Variable de salida | Nombres finales |
| --- | --- | --- | --- |
| SW | `CODIGO/procesar_spacy_sw.py` | `OUTPUT_FINAL` | `LSM_NLTK_SW.csv`, `LSM_SPACY_SW.csv`, `LSM_SPACY_MOD_SW.csv` |
| CGC | `CODIGO/procesar_spacy_cgc.py` | `OUTPUT_FINAL` | `LSM_NLTK_CGC.csv`, `LSM_SPACY_CGC.csv`, `LSM_SPACY_MOD_CGC.csv` |
| SCOTUS | `CODIGO/procesar_spacy_scotus_vfinal.py` | `OUTPUT_FINAL_SCOTUS` | `LSM_NLTK_SCOTUS.csv`, `LSM_SPACY_SCOTUS.csv`, `LSM_SPACY_MOD_SCOTUS.csv` |

Después de configurar cada variante:

```bash
python CODIGO/procesar_spacy_sw.py
python CODIGO/procesar_spacy_cgc.py
python CODIGO/procesar_spacy_scotus_vfinal.py
```

Para SCOTUS se usa aquí `procesar_spacy_scotus_vfinal.py` porque implementa la misma selección de pares que la base LIWC y el cálculo ENTR. No mezclar sus salidas con CSV históricos calculados con otra unidad de análisis.

Esquema esperado: `archivo, lsm_model, grupo, lsm_liwc` en SW/CGC; `id_virtual, lsm_model, grupo, lsm_liwc` en SCOTUS. Los valores de `grupo` deben ser exactamente `SW_PROCESSED`, `muestra_cgc` y `SCOTUS`, respectivamente, porque el notebook filtra por ellos. El primer gráfico acepta también CSV antiguos con `lsm_spacy`, pero la sección ENTR exige `lsm_model`.

## 6. Generar UBA Games en español e inglés

### 6.1. Preprocesamiento de B1 y B2

Entradas externas:

- B1: carpetas `b1-dialogue-phrases/` y `b1-dialogue-tasks/`, con los canales A/B y los intervalos temporales de tareas.
- B2: carpeta `b2-dialogue-phrases/`, con pares `channel1` / `channel2` separados por tabulaciones.

```bash
python CODIGO/preprocesar_UBA_GC_B1.py
python CODIGO/preprocesar_UBA_GC_B2.py
```

B1 elimina etiquetas, ordena intervenciones por tiempo y divide cada sesión por los intervalos `.tasks`. Produce `CODIGO/muestras_UBA_CG_B1/*.txt`, con nombres como `s21.objects.03.txt`.

B2 elimina etiquetas y combina los canales cronológicamente. Conserva conversaciones con al menos **3 turnos y 100 palabras por hablante** y produce `CODIGO/muestras_UBA_CG_B2/*.txt`. No utiliza archivos `.tasks` para dividir las conversaciones.

### 6.2. LSM del original español

```bash
python CODIGO/procesar_spacy_ubagames.py
```

Lee el 100% de los `.txt` procesados de B1 y B2 y usa `LSM_SPACY_ESPAÑOL.py`. Produce `LSM_SPACY_UBA.csv` con `archivo, sesion, batch, corpus, idioma, lsm`. Las filas sin LSM válido o con LSM igual a cero se excluyen.

### 6.3. Traducción al inglés

Los scripts que alimentan directamente el procesador inglés son los siguientes (respetar estos nombres):

```bash
python CODIGO/Preprocesar_traduccion_uba_B1.py
python CODIGO/Preprocesar_traduccion_uba_B2.py
```

Definir primero la variable de entorno, sin guardar la clave en el código:

```powershell
# PowerShell
$env:OPENAI_API_KEY = "tu-clave"
```

```bash
# Linux / macOS
export OPENAI_API_KEY="tu-clave"
```

Cada script traduce sus `.txt` con el modelo configurado `gpt-4o-mini` y temperatura 0.3, preservando identificadores de hablante, saltos de línea y estilo oral. Escribe `B1_traducciones/` o `B2_traducciones/` en la raíz, con el sufijo `_EN.txt`. Si el archivo traducido existe, lo omite: se puede retomar una corrida sin repetir esas llamadas. Las llamadas a la API pueden generar costos.

`procesar_traduccion_uba.py` es una ruta alternativa que escribe una carpeta unificada; no alimenta las dos carpetas que espera este flujo.

### 6.4. LSM de las traducciones

```bash
python CODIGO/procesar_spacy_ubagames_EN.py
```

Lee `B1_traducciones/` y `B2_traducciones/`, usa `LSM_SPACY.py` y produce `LSM_SPACY_UBA_EN.csv`, con el mismo esquema del español. El código actual selecciona **100% de las sesiones de ambos bloques**, aunque algunas funciones se llamen `seleccionar_mitad_sesiones`. Excluye LSM igual a cero o indefinido.

La columna `idioma` de este script quedó escrita como `es`; para interpretar o reutilizar la metadata del CSV traducido, corregir ese literal a `en`. El gráfico ES/EN compara `lsm` y une por `archivo` después de quitar `_EN`; no usa `idioma`. Preservar los nombres originales permite emparejar ambos idiomas. El procesador inglés rechaza sesiones presentes en ambos bloques.

## 7. Generar PENTO en alemán

Entrada externa: archivos ELAN `.eaf` de las rondas r1 a r8, ubicados en `datos_aleman/` (o en la ruta configurada). Los nombres deben permitir que los resultados comiencen con `r1_`, ..., `r8_`.

```bash
python CODIGO/pento.py
python CODIGO/PRUEBA_ALEMAN.py
```

`pento.py` lee la capa `Part`, resuelve los tiempos de las anotaciones, limpia las transcripciones y genera un `.txt` por tarea dentro de `dialogos_por_tarea/`.

`PRUEBA_ALEMAN.py` concatena las tareas de cada ronda y calcula LSM con el modelo alemán pequeño y categorías STTS. Produce **`LSM_RONDAS_AGREGADAS_R1_R8.csv`**, con `ronda`, `lsm_global`, conteos de palabras, número de tareas y LSM por categoría. La unidad del gráfico es una ronda agregada, no una tarea; se esperan hasta ocho filas si están disponibles las ocho rondas.

`procesar_spacy_aleman.py` genera `LSM_GERMAN_R1_R8.csv` por tarea. Ese archivo no sustituye al CSV agregado que lee el notebook final.

## 8. Generar C-ORAL-BRASIL en portugués

Entrada externa: transcripciones `.txt` de C-ORAL-BRASIL, con intervenciones del tipo `*HABLANTE: texto`. Configurar `DIRECTORIO_ENTRADA` en el script de la raíz.

```bash
python portuguesss.py
python CODIGO/procesar_spacy_portugues.py
```

`portuguesss.py` recorre la entrada, limpia marcas de transcripción y conserva únicamente conversaciones con exactamente dos hablantes. Genera `CORPUS_LIMPIO_DIADICO/*.txt` con líneas `hablante: texto`.

`procesar_spacy_portugues.py` usa `LSM_SPACY_PORTUGUES.py` y produce `LSM_SPACY_PORTUGUES.csv` con `archivo, lsm_spacy_pt, grupo`. El multiplicador actual es `1`: procesa **100% de los archivos limpios**, aunque sus comentarios y mensajes digan 10%.

El notebook compara este resultado con hasta 100 filas de `LSM_SPACY_SW.csv`, muestreadas con `random_state=42` cuando SW tiene más de 100 filas.

## 9. Generar las métricas ENTR

Usar las mismas carpetas procesadas que en las bases LIWC y los resultados LSM:

```bash
python CODIGO/entr/run_entr_sw.py
python CODIGO/entr/run_entr_scotus.py
python CODIGO/entr/run_entr_cgc.py
```

No es necesario ejecutar `csv_sw.py`, `csv_scotus.py` ni `csv_cgc.py`: el notebook hace el cruce directamente.

| Entrada | Salida en la raíz | Clave de cruce con LSM |
| --- | --- | --- |
| `SW_PROCESSED/` | `ENTR_SPACY_SW.csv` | `archivo` |
| `muestra_scotus/` | `ENTR_SPACY_SCOTUS.csv` | `id_virtual` |
| `muestra_cgc/` | `ENTR_SPACY_CGC.csv` | `archivo` |

Cada salida contiene seis métricas: `entr1_clase1`, `entr2_clase1`, `entr1_clase2`, `entr2_clase2`, `entr1_clase3`, `entr2_clase3`.

- Clase 1: stopwords inglesas de NLTK.
- Clase 2: las 25 palabras de contenido más frecuentes, calculadas sobre el corpus cargado.
- Clase 3: conjunto dinámico de palabras de las categorías funcionales de LSM presentes en la conversación.

SW y CGC separan intervenciones por los prefijos `A:` y `B:`; SCOTUS conserva la selección de pares de los tres hablantes principales y el mínimo de seis intervenciones por hablante. Mantener exactamente los mismos identificadores que en LSM para que el cruce no quede vacío.

## 10. Archivos necesarios para el notebook final

Todos los CSV de esta tabla deben estar en la raíz configurada para los resultados:

| Sección del notebook | CSV que consume |
| --- | --- |
| Modelos contra LIWC | `LSM_NLTK_SW.csv`, `LSM_SPACY_SW.csv`, `LSM_SPACY_MOD_SW.csv`; `LSM_NLTK_SCOTUS.csv`, `LSM_SPACY_SCOTUS.csv`, `LSM_SPACY_MOD_SCOTUS.csv`; `LSM_NLTK_CGC.csv`, `LSM_SPACY_CGC.csv`, `LSM_SPACY_MOD_CGC.csv` |
| UBA / CGC / PENTO | `LSM_SPACY_UBA.csv`, `LSM_SPACY_CGC.csv`, `LSM_RONDAS_AGREGADAS_R1_R8.csv` |
| Portugués / SW | `LSM_SPACY_PORTUGUES.csv`, `LSM_SPACY_SW.csv` |
| UBA español / inglés | `LSM_SPACY_UBA.csv`, `LSM_SPACY_UBA_EN.csv` |
| LSM / ENTR | `LSM_SPACY_SW.csv`, `LSM_SPACY_SCOTUS.csv`, `LSM_SPACY_CGC.csv`, `ENTR_SPACY_SW.csv`, `ENTR_SPACY_SCOTUS.csv`, `ENTR_SPACY_CGC.csv` |

Son **16 CSV distintos**. Las bases `LIWC_*_BASE.csv` son intermediarios necesarios para regenerar los nueve resultados de la primera sección; el notebook no las lee directamente.

Esta copia no contiene los 16 CSV completos. Algunos resultados presentes son históricos: por ejemplo, `LSM_NLTK_SCOTUS.csv` tiene `archivo` y `lsm_spacy`, mientras que el flujo de pares final usa `id_virtual` y `lsm_model`. Regenerar las variantes SCOTUS con el mismo procesador final evita comparar muestras y claves diferentes.

## 11. Configurar y ejecutar `PLOTTER_FINAL.ipynb`

Si ya se dispone de los 16 CSV con los esquemas anteriores, se pueden omitir las etapas de generación.

### 11.1. Cambiar las rutas de todas las secciones

En el notebook, ajustar `BASE_PATH`, `UBA_CSV`, `CGC_CSV`, `PENTO_CSV`, `PT_CSV`, `SW_CSV`, `RUTA_CSV_ES`, `RUTA_CSV_EN` y `CARPETA`. Todos deben apuntar a la misma raíz de resultados.

Ejemplo para la primera sección:

```python
BASE_PATH = "C:/ruta/al/repositorio/MySPACY"
```

Para las demás rutas usar esa misma base, por ejemplo `UBA_CSV = f"{BASE_PATH}/LSM_SPACY_UBA.csv"` y `CARPETA = BASE_PATH`.

### 11.2. Adaptar la columna de UBA en el gráfico UBA / CGC / PENTO

El generador actual de UBA escribe `lsm`. La celda del boxplot busca solamente `lsm_model` o `lsm_spacy`, por lo que debe reemplazarse la asignación de `col_uba` por:

```python
col_uba = next(c for c in ("lsm", "lsm_model", "lsm_spacy") if c in df_uba.columns)
```

El resto de esa celda puede conservarse. No renombrar permanentemente `lsm` en el CSV UBA: el gráfico posterior ES/EN necesita esa columna y `batch` en el CSV español.

### 11.3. Abrir y ejecutar

```bash
python -m jupyterlab GRAFICO/PLOTTER_FINAL.ipynb
```

Seleccionar el kernel del entorno donde se instalaron las dependencias, reiniciarlo y ejecutar todas las celdas en orden.

El notebook guarda estas figuras en el directorio de trabajo del kernel:

- `matriz_validacion_liwc_vs_modelos.png`.
- `boxplot_LSM_UBA_CGC_PENTO.png`.
- `boxplot_LSM_PT_vs_SW_muestra100.png`.

La comparación UBA ES/EN y las grillas LSM/ENTR se muestran en pantalla; sus celdas actuales no las guardan automáticamente. La sección ENTR completa muestra seis grillas de seis subgráficos cada una.

### 11.4. Comprobación de entradas

Ejecutar esta celda antes de los gráficos, usando la raíz configurada:

```python
from pathlib import Path
import pandas as pd

raiz = Path(BASE_PATH)
esquemas = {}
for corpus in ("SW", "SCOTUS", "CGC"):
    for modelo in ("NLTK", "SPACY", "SPACY_MOD"):
        esquemas[f"LSM_{modelo}_{corpus}.csv"] = {"grupo", "lsm_liwc"}
    clave = "id_virtual" if corpus == "SCOTUS" else "archivo"
    esquemas[f"LSM_SPACY_{corpus}.csv"] |= {clave, "lsm_model"}
    esquemas[f"ENTR_SPACY_{corpus}.csv"] = {clave} | {
        f"entr{metrica}_clase{clase}"
        for metrica in (1, 2) for clase in (1, 2, 3)
    }
esquemas["LSM_SPACY_UBA.csv"] = {"archivo", "batch", "lsm"}
esquemas["LSM_SPACY_UBA_EN.csv"] = {"archivo", "lsm"}
esquemas["LSM_SPACY_PORTUGUES.csv"] = {"archivo", "lsm_spacy_pt"}
esquemas["LSM_RONDAS_AGREGADAS_R1_R8.csv"] = {"ronda", "lsm_global"}

for nombre, columnas in esquemas.items():
    ruta = raiz / nombre
    assert ruta.is_file(), f"Falta {ruta}"
    df = pd.read_csv(ruta)
    assert not df.empty, f"CSV vacío: {nombre}"
    assert columnas <= set(df.columns), f"Columnas faltantes en {nombre}: {columnas - set(df.columns)}"
    if nombre.startswith("LSM_") and nombre.endswith(("_SW.csv", "_SCOTUS.csv", "_CGC.csv")):
        assert {"lsm_model", "lsm_spacy"} & set(df.columns), f"Falta columna del modelo: {nombre}"
print(f"Entradas verificadas: {len(esquemas)} CSV")
```

La comprobación valida presencia y esquema básico; revisar también que los grupos coincidan, que los cruces tengan datos y que cada correlación tenga al menos dos pares numéricos válidos. Pearson requiere variación en ambas variables para dar una correlación definida.

## 12. Problemas habituales y alcance de reproducción

| Síntoma | Qué revisar |
| --- | --- |
| `FileNotFoundError` | Rutas absolutas antiguas, corpus externo ausente, etapa anterior pendiente o ejecución desde otra carpeta |
| Mensaje sobre `precomputar_liwc.py` | Es un mensaje antiguo: ejecutar el `PreprocesarLIWC_*.py` del corpus correspondiente |
| `KeyError: lsm_spacy` en UBA / CGC / PENTO | Aplicar el ajuste de `col_uba` descrito arriba |
| `KeyError: id_virtual` o `lsm_model` | Se está usando un CSV histórico; regenerar con el esquema del flujo final |
| Gráfico vacío o cruce vacío | Revisar nombres de archivo, sufijo `_EN`, `grupo`, selección de pares y coherencia entre muestras |
| Fallo de LIWC o scores nulos | Ruta del ejecutable, instalación habilitada, formato de entrada y salida `tests/LSM-Speaker-Pairwise.csv` |
| `LookupError` de NLTK | Descargar el recurso indicado por el error en el mismo entorno del proceso |
| Modelo spaCy ausente | Descargar el modelo que carga el módulo seleccionado |

Las muestras, las traducciones y las versiones de los modelos forman parte de la reproducción del análisis. Conservar las conversaciones procesadas, los CSV y las traducciones evita que un nuevo muestreo o una nueva traducción cambien los resultados. No hay que asumir que un comentario que diga 10% o 50% describe el comportamiento actual: esta guía recoge los valores ejecutados por el código.

Los archivos `Pipeline_*.py`, el notebook anterior `GRAFICO/plotter.ipynb`, los `datos_para_plotear*.csv` y los scripts auxiliares de cruces ENTR no se necesitan para ejecutar el notebook final. Se conservan como material histórico; no es necesario borrarlos para seguir este pipeline.
