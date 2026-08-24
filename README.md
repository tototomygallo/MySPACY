# My 🐔 SPACY 🌌


# Análisis de Alineamiento Lingüístico en Corpus Dialógicos

Este repositorio contiene el pipeline completo para la extracción, preprocesamiento, cálculo de métricas de alineamiento estilístico (**LSM - Language Style Matching**) corpus (`UBA-GC` Bloques 1 y 2, `Switchboard` y `SCOTUS`).

---

## 📁 Estructura del Repositorio

```text
CODIGO/
├── PreprocesarLIWC_SW.py       # Generación de resultados LSM LIWC para Switchboard
├── PreprocesarLIWC_SCOTUS.py       # Generación de resultados LSM LIWC para SCOTUS
├── PreprocesarLIWC_CGC.py       # Generación de resultados LSM LIWC para CGC
├── preprocesar_UBA_GC_B1.py       # Segmentación por tareas/sesión para UBA-GC Bloque 1
├── preprocesar_UBA_GC_B2.py       # Segmentación por tareas/sesión para UBA-GC Bloque 2
├── Preprocesar_swboard.py         # Formateo y limpieza de transcripciones Switchboard
├── procesar_spacy_sw.py           # Generación de resultados LSM para Switchboard
├── procesar_spacy_scotus.py       # Generación de resultados LSM para SCOTUS
├── procesar_spacy_cgc.py          # Generación de resultados LSM para CGC
├── procesar_spacy_ubagames.py     # Generación de resultados LSM para UBA Games (español)
├── Preprocesar_traducciones_uba_b1.py  # Traduce (ES→EN) las muestras de UBA-GC Bloque 1 vía OpenAI API
├── Preprocesar_traducciones_uba_b2.py  # Traduce (ES→EN) las muestras de UBA-GC Bloque 2 vía OpenAI API
├── procesar_spacy_ubagames_EN.py       # Calcula LSM (modelo inglés) sobre las traducciones de UBA-GC
├── main.py                        # Script de test LSM
├── muestras_UBA_CG_B1/            # Muestras procesadas salida Bloque 1 (español)
├── muestras_UBA_CG_B2/            # Muestras procesadas salida Bloque 2 (español)
├── B1_traducciones/               # Traducciones al inglés de muestras_UBA_CG_B1 (generadas por Preprocesar_traducciones_uba_b1.py)
├── B2_traducciones/                # Traducciones al inglés de muestras_UBA_CG_B2 (generadas por Preprocesar_traducciones_uba_b2.py)
├── Herramientas/
│   ├── parseo.py                  # Funciones I/O para iterar y cargar archivos .txt/.phrases
│   └── formato_liwc.py            # Limpieza con RegEx y formateo de pares A/B a .phrases
├── LSM/
│   ├── LSM_SPACY.py               # Algoritmo LSM nativo en inglés vía spaCy
│   ├── LSM_SPACY_ESPAÑOL.py       # Algoritmo LSM adaptado al español vía spaCy
│   └── LIWC.py                    # Wrapper CLI para integrar LIWC-22
└── entr/
    ├── procesar.py                # Implementación de métricas de Entropía (ENTR1 y ENTR2)
    ├── run_entr_sw.py             # Ejecución de ENTR sobre el corpus Switchboard
    ├── run_entr_scotus.py         # Ejecución de ENTR sobre el corpus SCOTUS
    ├── run_entr_scotus.py         # Ejecución de ENTR sobre el corpus CGC
    ├── csv_sw.py                  # Correlación LSM vs ENTR para Switchboard (innecesesario)
    └── csv_scotus.py              # Correlación LSM vs ENTR para SCOTUS (innecesario)
```

```text
GRAFICO/
└── plotter.ipynb                  # Notebook con todos las distribuciones y corelaciones de resultados de procesamiento
```

---

## ⚙️ Requisitos e Instalación

### Python

- Python **3.10+**

### Crear un entorno virtual e instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install spacy nltk pandas scipy openai
```

### Descargar modelos de spaCy y recursos de NLTK

```bash
python -m spacy download en_core_web_md
python -m spacy download es_core_news_md
python -c "import nltk; nltk.download('stopwords')"
```

### API key de OpenAI (para la traducción del corpus UBA-GC)

Los scripts `Preprocesar_traducciones_uba_b1.py` y `Preprocesar_traducciones_uba_b2.py` usan la API de OpenAI (`gpt-4o-mini`) para traducir las transcripciones. La key **nunca debe quedar hardcodeada en el código ni subida al repo** — se define como variable de entorno antes de correr los scripts:

```bash
export OPENAI_API_KEY="tu-key-aca"
```

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

## 1.5. Traducción del corpus UBA-GC (ES → EN)

El objetivo de este paso es comparar el LSM del corpus UBA-GC calculado
**en español** (`procesar_spacy_ubagames.py`, con `LSM_SPACY_ESPAÑOL.py`)
contra el LSM de las **mismas conversaciones traducidas al inglés**
(`procesar_spacy_ubagames_EN.py`, con `LSM_SPACY.py`), para ver si la
métrica varía según el idioma en el que se mide un mismo diálogo. Por eso
se traduce el corpus completo con la API de OpenAI, preservando turnos de
habla, oralidad y muletillas (ver el prompt de sistema dentro de cada
script) — la traducción busca ser lo más literal posible en estilo, para
que la comparación ES vs EN aísle el efecto del idioma y no introduzca
cambios de registro.

```bash
python CODIGO/Preprocesar_traducciones_uba_b1.py
python CODIGO/Preprocesar_traducciones_uba_b2.py
```

**Salida**

```
B1_traducciones/
B2_traducciones/
```

Ambos scripts son reanudables: si un archivo de salida ya existe, se
omite, así se puede cortar y retomar la corrida sin volver a gastar
llamadas a la API sobre archivos ya traducidos.

---

## 2. Procesamiento de Resultados por Corpus

Cada corpus posee un script independiente que calcula las métricas correspondientes.

> **⚠️ Configuración del modelo lingüístico**
>
> Actualmente la selección del modelo de spaCy se realiza directamente en el código. Antes de ejecutar cualquiera de los scripts `procesar_spacy_*.py`, debe comentarse/descomentarse las líneas de los imports para elegir `NLTK, SPACY, SPACY_MOD`

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

### UBA Games (español)

```bash
python CODIGO/procesar_spacy_ubagames.py
```

### UBA Games traducido al inglés

Calcula LSM con el modelo de spaCy en inglés (`LSM/LSM_SPACY.py`) sobre
las traducciones generadas en el paso 1.5, unificando B1 y B2 (50% de
sesiones de cada uno, mismo muestreo con seed fija) en un solo corpus.

```bash
python CODIGO/procesar_spacy_ubagames_EN.py
```

**Salida:** `LSM_SPACY_UBA_EN.csv` — pensado para compararse directamente
contra `LSM_SPACY_UBA.csv` (la versión en español de las mismas
conversaciones), y así evaluar el efecto del idioma sobre el LSM medido.

---

## 3. Métricas de Estilo (LSM) y Entropía (ENTR)

### LSM (Language Style Matching)

Mide la similitud estilística entre ambos hablantes utilizando ocho categorías de palabras funcionales (pronombres, artículos, preposiciones, conjunciones, verbos auxiliares, negaciones, etc.).

```text
LSM = 1 - |pct_A - pct_B| / (pct_A + pct_B + ε)
```

`calculo_LSM` devuelve `None` (no `0.0`) cuando el valor está indefinido
(menos de 2 hablantes, o algún hablante sin palabras contadas). Al filtrar
resultados en un DataFrame, usar `df[df["lsm"].notna()]`, no
`df[df["lsm"] > 0]`.

---

### ENTR1 y ENTR2 (Convergencia Informacional)

Calculan la distancia entre las distribuciones léxicas de ambos interlocutores utilizando tres clases de palabras:

1. **Clase 1:** Stopwords estándar.
2. **Clase 2:** Las 25 palabras de contenido más frecuentes del corpus completo.
3. **Clase 3:** Bolsa dinámica de palabras pertenecientes a las categorías funcionales empleadas por LSM_Spacy presentes en la conversación.

---

