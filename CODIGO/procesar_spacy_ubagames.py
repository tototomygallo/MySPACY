import os
from pathlib import Path
import pandas as pd

from LSM.LSM_SPACY_ESPAÑOL import calculo_LSM

# ==========================
# Configuración
# ==========================

DIR_B1 = Path("/home/tgallo/Documents/Proyecto_modular/CODIGO/muestras_UBA_CG_B1")
DIR_B2 = Path("/home/tgallo/Documents/Proyecto_modular/CODIGO/muestras_UBA_CG_B2")

OUTPUT_CSV = "LSM_SPACY_UBA.csv"


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


def cargar_100_por_ciento(dir_b1: Path, dir_b2: Path):
    """Carga TODOS los archivos de B1 y B2 sin realizar muestreo."""
    archivos_b1 = sorted(dir_b1.glob("*.txt"))
    archivos_b2 = sorted(dir_b2.glob("*.txt"))

    # Estructuramos la lista unificada
    muestra_unificada = []
    for f in archivos_b1:
        muestra_unificada.append((f, "b1"))
    for f in archivos_b2:
        muestra_unificada.append((f, "b2"))

    # Ordenamos por nombre de archivo para mantener determinismo
    muestra_unificada.sort(key=lambda item: item[0].name)

    return muestra_unificada


# ==========================
# Pipeline
# ==========================

def ejecutar_pipeline():
    muestra = cargar_100_por_ciento(DIR_B1, DIR_B2)

    print("=== Procesando 100% de UBA Games (B1 + B2) ===")
    print(f"Total de archivos a procesar: {len(muestra)}")

    resultados = []

    print("\nProcesando cálculo LSM...")

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

    # Filtrar diálogos donde LSM no pudo calcularse o fue Nulo
    df = df.dropna(subset=["lsm"])
    df = df[df["lsm"] > 0]

    df.to_csv(OUTPUT_CSV, index=False)

    print("\n==============================")
    print(f"Conversaciones procesadas exitosamente: {len(df)}")
    print(f"CSV guardado en: {OUTPUT_CSV}")


if __name__ == "__main__":
    ejecutar_pipeline()