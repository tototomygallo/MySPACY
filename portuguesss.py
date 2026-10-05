import os
import re

# --- CONFIGURACIÓN DE RUTAS ---
DIRECTORIO_ENTRADA = (
    "/home/tgallo/Downloads/2. Textual Corpus"  # Cambiar según tu carpeta
)
DIRECTORIO_SALIDA = "CORPUS_LIMPIO_DIADICO"


# --- 1. FUNCIÓN DE LIMPIEZA C-ORAL-BRASIL ---
def limpiar_linea_coralla(linea: str):
    linea = linea.strip()
    if not linea or not linea.startswith("*"):
        return None, None

    # 1. Separar Hablante y Texto
    partes = linea[1:].split(":", 1)
    if len(partes) < 2:
        return None, None

    hablante = partes[0].strip()
    texto = partes[1].strip()

    # 2. ELIMINAR NÚMEROS DE ENUNCIADO ENTRE CORCHETES: [1], [39], [106]
    texto = re.sub(r"\[\d+\]", "", texto)

    # 3. Eliminar marcas de reformulación/solapamiento específicas de C-ORAL si las hubiera [/1]
    texto = re.sub(r"\[/\d+\]", "", texto)

    # 4. Eliminar vacilaciones / palabras truncadas que empiezan con '&' (ej: &he, &s, &ba)
    texto = re.sub(r"&\w+", "", texto)

    # 5. Preservar palabras dentro de overlaps < >
    texto = re.sub(r"[<>]", "", texto)

    # 6. Eliminar marcas prosódicas //, / y el signo de interrupción +
    texto = re.sub(r"[//\+]", "", texto)

    # 7. Eliminar marcadores ininteligibles / no léxicos (yyyy, xxx, hhh)
    texto = re.sub(
        r"\b(yyyy|xxx|hhh)\b", "", texto, flags=re.IGNORECASE
    )

    # 8. Limpiar espacios múltiples y bordes
    texto = re.sub(r"\s+", " ", texto).strip()

    if not texto:
        return None, None

    return hablante, texto

# --- 2. PIPELINE DE PREPROCESAMIENTO Y EXPORTACIÓN ---
def preprocesar_corpus():
    # Crear carpeta de salida si no existe
    if not os.path.exists(DIRECTORIO_SALIDA):
        os.makedirs(DIRECTORIO_SALIDA)

    archivos_guardados = 0
    archivos_omitidos = 0

    print("Iniciando preprocesamiento de archivos C-ORAL-BRASIL...")

    for root, _, files in os.walk(DIRECTORIO_ENTRADA):
        for file in sorted(files):
            if file.endswith(".txt"):
                ruta_entrada = os.path.join(root, file)

                with open(
                    ruta_entrada, "r", encoding="utf-8", errors="ignore"
                ) as f:
                    lineas = f.readlines()

                # Paso A: Detectar hablantes únicos en el archivo
                hablantes_detectados = set()
                for linea in lineas:
                    hab, _ = limpiar_linea_coralla(linea)
                    if hab:
                        hablantes_detectados.add(hab)

                # Paso B: Filtrar de forma estricta (SOLO exactamente 2 hablantes)
                if len(hablantes_detectados) != 2:
                    archivos_omitidos += 1
                    continue

                # Paso C: Generar las líneas limpias
                lineas_limpias = []
                for linea in lineas:
                    hab, txt = limpiar_linea_coralla(linea)
                    if hab and txt:
                        lineas_limpias.append(f"{hab}: {txt}\n")

                # Paso D: Guardar el archivo limpio si contiene texto válido
                if lineas_limpias:
                    ruta_salida = os.path.join(DIRECTORIO_SALIDA, file)
                    with open(ruta_salida, "w", encoding="utf-8") as f_out:
                        f_out.writelines(lineas_limpias)

                    archivos_guardados += 1

    print("\n¡Preprocesamiento completado!")
    print(
        f" - Archivos diádicos guardados en '{DIRECTORIO_SALIDA}': {archivos_guardados}"
    )
    print(
        f" - Archivos omitidos (monólogos o 3+ hablantes): {archivos_omitidos}"
    )


if __name__ == "__main__":
    preprocesar_corpus()