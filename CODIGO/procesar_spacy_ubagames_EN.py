import random
from pathlib import Path
import pandas as pd

from LSM.LSM_SPACY import calculo_LSM


# ==========================
# Configuración
# ==========================

DIR_B1 = Path("/home/tgallo/Documents/Proyecto_modular/B1_traducciones")
DIR_B2 = Path("/home/tgallo/Documents/Proyecto_modular/B2_traducciones")

OUTPUT_CSV = "LSM_SPACY_UBA_EN.csv"

SEED = 42


# ==========================
# Funciones
# ==========================

def leer_archivo(path: Path) -> list[str]:
    with open(path, "r", encoding="utf8") as f:
        return [line.strip() for line in f if line.strip()]


def obtener_sesion(path: Path) -> str:
    """
    Ejemplos:
    s01.objects.1.txt -> s01
    s29.objects.21.txt -> s29
    """
    return path.name.split(".")[0]


def seleccionar_mitad_sesiones(archivos: list[Path], rng: random.Random):
    """
    Agrupa los archivos por sesión, selecciona el 50% de las sesiones
    disponibles y retorna TODOS los archivos pertenecientes a esas sesiones.
    """
    sesiones = {}
    for archivo in archivos:
        sesion = obtener_sesion(archivo)
        if sesion not in sesiones:
            sesiones[sesion] = []
        sesiones[sesion].append(archivo)

    sesiones_disponibles = sorted(sesiones.keys())
    cantidad = len(sesiones_disponibles) // 2

    sesiones_elegidas = sorted(rng.sample(sesiones_disponibles, cantidad))

    seleccionados = []
    for sesion in sesiones_elegidas:
        seleccionados.extend(sesiones[sesion])

    return seleccionados, sesiones_elegidas


def seleccionar_muestra_50_50(dir_b1: Path, dir_b2: Path, seed: int):
    rng = random.Random(seed)

    archivos_b1 = sorted(dir_b1.glob("*.txt"))
    archivos_b2 = sorted(dir_b2.glob("*.txt"))

    # 50% de las sesiones de B1
    muestra_b1, sesiones_b1 = seleccionar_mitad_sesiones(archivos_b1, rng)

    # 50% de las sesiones de B2
    muestra_b2, sesiones_b2 = seleccionar_mitad_sesiones(archivos_b2, rng)

    # Control de superposición
    repetidas = set(sesiones_b1) & set(sesiones_b2)
    if repetidas:
        raise ValueError(f"Atención: hay sesiones presentes en ambos batches: {repetidas}")

    # Estructuramos la lista unificada
    muestra_unificada = []
    for f in muestra_b1:
        muestra_unificada.append((f, "b1"))
    for f in muestra_b2:
        muestra_unificada.append((f, "b2"))

    # Ordenamos por nombre para mantener determinismo
    muestra_unificada.sort(key=lambda item: item[0].name)

    return muestra_unificada, sesiones_b1, sesiones_b2


# ==========================
# Pipeline
# ==========================

def ejecutar_pipeline():

    muestra, sesiones_b1, sesiones_b2 = seleccionar_muestra_50_50(
        DIR_B1, DIR_B2, SEED
    )

    print("=== Muestreo (50% B1 + 50% B2) ===")
    print(f"\nB1 sesiones seleccionadas ({len(sesiones_b1)}):", ", ".join(sesiones_b1))
    print(f"B2 sesiones seleccionadas ({len(sesiones_b2)}):", ", ".join(sesiones_b2))

    print(f"\nTotal de archivos a procesar como un solo corpus: {len(muestra)}")

    resultados = []

    print("\nProcesando calculo LSM...")

    for archivo, batch in muestra:
        try:
            contenido = leer_archivo(archivo)
            lsm = calculo_LSM(contenido)

            resultados.append(
                {
                    "archivo": archivo.name,
                    "sesion": obtener_sesion(archivo),
                    "batch": batch,
                    "corpus": "UBA",
                    "idioma": "es",
                    "lsm": lsm,
                }
            )

        # Imprimir de forma segura según si lsm es flotante o None
            if lsm is not None:
                print(f"✓ [{batch.upper()}] {archivo.name}: {lsm:.4f}")
            else:
                print(f"⚠️ [{batch.upper()}] {archivo.name}: Indefinido (None)")

        except Exception as e:
            print(f"✗ Error en {archivo.name}: {e}")

    df = pd.DataFrame(resultados)

    # Filtrar diálogos donde LSM no pudo calcularse
    df = df[df["lsm"] > 0]

    df.to_csv(OUTPUT_CSV, index=False)

    print("\n==============================")
    print(f"Conversaciones procesadas exitosamente: {len(df)}")
    print(f"CSV guardado en: {OUTPUT_CSV}")


if __name__ == "__main__":
    ejecutar_pipeline()