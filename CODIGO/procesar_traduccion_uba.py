import os
import random
from pathlib import Path
from openai import OpenAI

# ==========================
# Configuración
# ==========================
API_KEY = "TU_API_KEY_AQUI"
client = OpenAI(api_key=API_KEY)

# Directorios de origen
DIR_B1 = Path("/home/tgallo/Documents/Proyecto_modular/CODIGO/muestras_UBA_CG_B1")
DIR_B2 = Path("/home/tgallo/Documents/Proyecto_modular/CODIGO/muestras_UBA_CG_B2")

# Carpeta de salida para las traducciones
DIR_TRADUCIDO = Path("/home/tgallo/Documents/Proyecto_modular/muestras_UBA_100porc_traducidas_EN")

PORCENTAJE_MUESTRA = 1  # 100%
SEED = 42
MODELO = "gpt-4o-mini"


# ==========================
# Prompt (Se envía en CADA llamada)
# ==========================
PROMPT_SISTEMA = """
Sos un traductor experto en lingüística computacional y transcripciones de habla espontánea.
Tu tarea es traducir el siguiente diálogo del español al inglés.

REGLAS ESTRICTAS:
1. Mantén intactos los identificadores de hablante o turnos si existen (ej: "A:", "B:").
2. Conserva la oralidad, muletillas, pausas, interjecciones y estilo informal propio de la conversación hablada.
3. NO corrijas errores gramaticales ni formalices el lenguaje.
4. Devuelve ÚNICAMENTE el texto traducido con exactamente el mismo formato de saltos de línea y estructura original.
"""


# ==========================
# Funciones de Muestreo
# ==========================
def obtener_sesion(nombre_archivo: str) -> str:
    """Extrae la sesión del nombre del archivo (ej: s01.objects.1.txt -> s01)."""
    return nombre_archivo.split(".")[0]


def seleccionar_sesiones_batch(dir_batch: Path, porcentaje: float, seed: int):
    """
    Selecciona el % de las sesiones únicas utilizando su propia instancia de la semilla.
    Devuelve TODOS los archivos/tareas pertenecientes a las sesiones elegidas.
    """
    rng = random.Random(seed)
    
    sesiones_dict = {}
    archivos = sorted(dir_batch.glob("*.txt"))
    
    for archivo in archivos:
        sesion = obtener_sesion(archivo.name)
        if sesion not in sesiones_dict:
            sesiones_dict[sesion] = []
        sesiones_dict[sesion].append(archivo)
        
    sesiones_unicas = sorted(sesiones_dict.keys())
    cantidad_a_tomar = max(1, int(len(sesiones_unicas) * porcentaje))
    
    sesiones_elegidas = sorted(rng.sample(sesiones_unicas, cantidad_a_tomar))
    
    archivos_seleccionados = []
    for sesion in sesiones_elegidas:
        archivos_seleccionados.extend(sesiones_dict[sesion])
        
    return archivos_seleccionados, sesiones_elegidas


# ==========================
# Función de Traducción
# ==========================
def traducir_texto(texto: str) -> str:
    """Envía el texto y el System Prompt a la API en cada llamada."""
    response = client.chat.completions.create(
        model=MODELO,
        messages=[
            {"role": "system", "content": PROMPT_SISTEMA},
            {"role": "user", "content": texto}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()


# ==========================
# Pipeline Principal
# ==========================
def ejecutar_traduccion_corpus():
    DIR_TRADUCIDO.mkdir(parents=True, exist_ok=True)
    
    # 1. Obtener la muestra exacta del 50% por sesiones completas
    archivos_b1, sesiones_b1 = seleccionar_sesiones_batch(DIR_B1, PORCENTAJE_MUESTRA, SEED)
    archivos_b2, sesiones_b2 = seleccionar_sesiones_batch(DIR_B2, PORCENTAJE_MUESTRA, SEED)
    
    todos_los_archivos = archivos_b1 + archivos_b2
    total = len(todos_los_archivos)
    
    print("=== Muestreo y Traducción UBA (ES -> EN) ===")
    print(f"Sesiones B1 ({len(sesiones_b1)}): {', '.join(sesiones_b1)}")
    print(f"Sesiones B2 ({len(sesiones_b2)}): {', '.join(sesiones_b2)}")
    print(f"Total de archivos/tareas a traducir: {total}\n")
    
    # 2. Procesar y traducir cada archivo
    for i, file_orig in enumerate(todos_los_archivos, start=1):
        file_dest = DIR_TRADUCIDO / file_orig.name
        
        # Sistema de caché: si ya existe el traducido, lo omite
        if file_dest.exists():
            print(f"[{i}/{total}] ⏭️ Saltado (ya traducido): {file_orig.name}")
            continue
            
        print(f"[{i}/{total}] 🌐 Traduciendo: {file_orig.name}...")
        
        try:
            with open(file_orig, "r", encoding="utf8") as f:
                texto_original = f.read()
                
            texto_traducido = traducir_texto(texto_original)
            
            with open(file_dest, "w", encoding="utf8") as f:
                f.write(texto_traducido)
                
            print(f"   ✓ Guardado en {file_dest.name}")
            
        except Exception as e:
            print(f"   ✗ Error en {file_orig.name}: {e}")
            
    print("\n==============================")
    print(f"Traducciones finalizadas. Archivos guardados en:\n👉 {DIR_TRADUCIDO.resolve()}")


if __name__ == "__main__":
    ejecutar_traduccion_corpus()