import os
import time
from pathlib import Path
from openai import OpenAI

# ==========================
# Configuración
# ==========================

# Se recomienda definir la API key como variable de entorno o asignarla a esta variable
API_KEY = os.getenv("OPENAI_API_KEY", "TU_API_KEY_AQUI")

# Carpetas de Origen y Destino
DIR_ENTRADA = Path("/home/tgallo/Documents/Proyecto_modular/CODIGO/muestras_UBA_CG_B1")
DIR_SALIDA = Path("./B1_traducciones")

MODELO = "gpt-4o-mini"
TEMPERATURE = 0.3

# ==========================
# Prompt de Traducción
# ==========================

PROMPT_SISTEMA = """
Sos un traductor experto en lingüística computacional y transcripciones de habla espontánea.
Tu tarea es traducir el siguiente diálogo del español al inglés.

REGLAS ESTRICTAS:
1. Mantén intactos los identificadores de hablante o turnos si existen (ej: "A:", "B:").
2. Conserva la oralidad, muletillas, pausas, interjecciones y estilo informal propio de la conversación hablada.
3. NO corrijas errores gramaticales ni formalices el lenguaje.
4. Devuelve ÚNICAMENTE el texto traducido con exactamente el mismo formato de saltos de línea y estructura original. NO agregues introducciones, notas ni explicaciones.
"""


def traducir_corpus():
    # Instanciamos el cliente
    client = OpenAI(api_key=API_KEY)

    # Crear carpeta de destino si no existe
    DIR_SALIDA.mkdir(parents=True, exist_ok=True)

    # Obtener y ordenar todos los archivos .txt de la carpeta de entrada
    archivos = sorted(DIR_ENTRADA.glob("*.txt")) # Limitar a los primeros 5 archivos para pruebas
    total_archivos = len(archivos)

    if total_archivos == 0:
        print(f"✗ No se encontraron archivos .txt en {DIR_ENTRADA}")
        return

    print(f"=== Inicio de Traducción de Corpus ===")
    print(f"Directorio Origen:  {DIR_ENTRADA}")
    print(f"Directorio Destino: {DIR_SALIDA}")
    print(f"Total de archivos a procesar: {total_archivos}\n")

    exitos = 0
    omitidos = 0
    errores = 0

    for i, file_orig in enumerate(archivos, start=1):
        # Mismo nombre de archivo pero con sufijo _EN
        file_dest = DIR_SALIDA / f"{file_orig.stem}_EN.txt"

        # 1. Chequeo de Caché: si el archivo traducido ya existe, lo saltamos
        if file_dest.exists():
            print(f"[{i}/{total_archivos}] ⏭️ Omitido (ya traducido): {file_orig.name}")
            omitidos += 1
            continue

        print(f"[{i}/{total_archivos}] 🌐 Traduciendo: {file_orig.name}...")

        try:
            # 2. Leer contenido original
            with open(file_orig, "r", encoding="utf8") as f:
                texto_original = f.read().strip()

            if not texto_original:
                print(f"   ⚠️ Archivo vacío: {file_orig.name}. Saltando...")
                continue

            # 3. Llamada a la API enviando el PROMPT_SISTEMA en CADA solicitud
            response = client.chat.completions.create(
                model=MODELO,
                messages=[
                    {"role": "system", "content": PROMPT_SISTEMA},
                    {"role": "user", "content": texto_original}
                ],
                temperature=TEMPERATURE
            )

            texto_traducido = response.choices[0].message.content.strip()

            # 4. Guardar archivo traducido en la carpeta destino
            with open(file_dest, "w", encoding="utf8") as f:
                f.write(texto_traducido)

            print(f"   ✓ Guardado en: {file_dest.name}")
            exitos += 1

            # Pausa pequeña para no exceder los límites de la API
            time.sleep(0.5)

        except Exception as e:
            print(f"   ✗ Error al procesar {file_orig.name}: {e}")
            errores += 1

    print("\n==========================================")
    print("Resumen de Ejecución:")
    print(f"  • Traducidos con éxito: {exitos}")
    print(f"  • Omitidos (ya existían): {omitidos}")
    print(f"  • Errores:               {errores}")
    print(f"Archivos guardados en: {DIR_SALIDA.resolve()}")


if __name__ == "__main__":
    traducir_corpus()