# My 🐔 SPACY 🌌


# Análisis de Alineamiento Lingüístico y Entropía en Corpus Dialógicos

Este repositorio contiene el pipeline completo para la extracción, preprocesamiento, cálculo de métricas de alineamiento estilístico (**LSM - Language Style Matching**) y convergencia informacional/entropía (**ENTR1**, **ENTR2**) sobre diversos corpora dialógicos (`UBA-GC` Bloques 1 y 2, `Switchboard` y `SCOTUS`).

---

## 📁 Estructura del Repositorio

```text
CODIGO/
├── preprocesar_UBA_GC_B1.py       # Segmentación por tareas/sesión para UBA-GC Bloque 1
├── preprocesar_UBA_GC_B2.py       # Segmentación por tareas/sesión para UBA-GC Bloque 2
├── Preprocesar_swboard.py         # Formateo y limpieza de transcripciones Switchboard
├── procesar_spacy_sw.py           # Generación de resultados LSM/ENTR para Switchboard
├── procesar_spacy_scotus.py       # Generación de resultados LSM/ENTR para SCOTUS
├── procesar_spacy_cgc.py          # Generación de resultados LSM/ENTR para CGC
├── procesar_spacy_ubagames.py     # Generación de resultados LSM/ENTR para UBA Games
├── main.py                        # Script orquestador principal
├── muestras_UBA_CG_B1/            # Muestras procesadas salida Bloque 1
├── muestras_UBA_CG_B2/            # Muestras procesadas salida Bloque 2
├── Herramientas/
│   ├── parseo.py                  # Funciones I/O para iterar y cargar archivos .txt/.phrases
│   └── formato_liwc.py            # Limpieza con RegEx y formateo de pares A/B a .phrases
├── LSM/
│   ├── LSM_SPACY.py               # Algoritmo LSM nativo en inglés vía spaCy
│   ├── LSM_SPACY_ESPAÑOL.py       # Algoritmo LSM adaptado al español vía spaCy
│   ├── LIWC.py                    # Wrapper CLI para integrar LIWC-22
│   └── myspacy_elegir_modelo.py   # Helper de carga dinámica de modelos spaCy
└── entr/
    ├── procesar.py                # Implementación de métricas de Entropía (ENTR1 y ENTR2)
    ├── run_entr_sw.py             # Ejecución de ENTR sobre el corpus Switchboard
    ├── run_entr_scotus.py         # Ejecución de ENTR sobre el corpus SCOTUS
    ├── csv_sw.py                  # Correlación LSM vs ENTR para Switchboard
    └── csv_scotus.py              # Correlación LSM vs ENTR para SCOTUS
```

```text
GRAFICO/
├── plotter.ipynb                  # Notebook con todos las distribuciones y corelaciones de resultados de procesamiento

```

---

## ⚙️ Requisitos e Instalación

### Python

- Python **3.10+**

### Crear un entorno virtual e instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install spacy nltk pandas scipy
```

### Descargar modelos de spaCy y recursos de NLTK

```bash
python -m spacy download en_core_web_md
python -m spacy download es_core_news_md
python -c "import nltk; nltk.download('stopwords')"
```

### Opcional

Instalar **LIWC-22 CLI** en el sistema para la ejecución mediante `LSM/LIWC.py`.

---

# 🚀 Flujo de Trabajo (Pipeline)

## 1. Preprocesamiento de los Corpora

Transforma las transcripciones crudas o archivos multi-sesión en diálogos estructurados por intervención o tarea.

### UBA-GC (Bloques 1 y 2)

Los scripts toman los diálogos `.phrases` junto con los rangos temporales `.tasks` para dividir cada sesión en subtareas etiquetadas.

```bash
python CODIGO/preprocesar_UBA_GC_B1.py
python CODIGO/preprocesar_UBA_GC_B2.py
```

**Salida**

```
muestras_UBA_CG_B1/
muestras_UBA_CG_B2/
```

### Switchboard / SCOTUS

```bash
python CODIGO/Herramientas/formato_liwc.py \
    --input_dir ./transcripts \
    --output_dir ./SW_PROCESSED
```

---

## 2. Procesamiento de Resultados por Corpus

Cada corpus posee un script independiente que calcula las métricas correspondientes.

> **⚠️ Configuración del modelo lingüístico**
>
> Actualmente la selección del modelo de spaCy se realiza directamente en el código. Antes de ejecutar cualquiera de los scripts `procesar_spacy_*.py`, debe comentarse/descomentarse la línea correspondiente al modelo (`en_core_web_md`, `es_core_news_md`, etc.) y configurar el idioma apropiado para el corpus a procesar.

### Switchboard

```bash
python CODIGO/procesar_spacy_sw.py
```

### SCOTUS

```bash
python CODIGO/procesar_spacy_scotus.py
```

### CGC

```bash
python CODIGO/procesar_spacy_cgc.py
```

### UBA Games

```bash
python CODIGO/procesar_spacy_ubagames.py
```

---

## 3. Métricas de Estilo (LSM) y Entropía (ENTR)

### LSM (Language Style Matching)

Mide la similitud estilística entre ambos hablantes utilizando ocho categorías de palabras funcionales (pronombres, artículos, preposiciones, conjunciones, verbos auxiliares, negaciones, etc.).

```text
LSM = 1 - |pct_A - pct_B| / (pct_A + pct_B + ε)
```

---

### ENTR1 y ENTR2 (Convergencia Informacional)

Calculan la distancia entre las distribuciones léxicas de ambos interlocutores utilizando tres clases de palabras:

1. **Clase 1:** Stopwords estándar.
2. **Clase 2:** Las 25 palabras de contenido más frecuentes del corpus completo.
3. **Clase 3:** Bolsa dinámica de palabras pertenecientes a las categorías funcionales empleadas por LSM presentes en la conversación.

---

## 4. Análisis Estadístico y Correlación

Finalmente se comparan las métricas de **LSM** y **ENTR** mediante correlación de Pearson.

```bash
python CODIGO/entr/csv_scotus.py
python CODIGO/entr/csv_sw.py
```