import random
from pathlib import Path

import pandas as pd

from LSM.LSM_SPACY_ESPAÑOL import calculo_LSM


# ==========================
# Configuración
# ==========================

DIR_B1 = Path("/home/tgallo/Documents/Proyecto_modular/CODIGO/muestras_UBA_CG_B1")
DIR_B2 = Path("/home/tgallo/Documents/Proyecto_modular/CODIGO/muestras_UBA_CG_B2")

OUTPUT_CSV = "LSM_SPACY_UBA.csv"

SEED = 42


# ==========================
# Funciones
# ==========================

def leer_archivo(path: Path) -> list[str]:
    with open(path, "r", encoding="utf8") as f:
        return [line.strip() for line in f if line.strip()]


def obtener_sesion(path: Path):
    """
    Ejemplos:
    s01.objects.1.txt -> s01
    s29.objects.21.txt -> s29
    """
    return path.name.split(".")[0]


def seleccionar_por_sesion(archivos, rng):

    # agrupar archivos por sesión
    sesiones = {}

    for archivo in archivos:
        sesion = obtener_sesion(archivo)

        if sesion not in sesiones:
            sesiones[sesion] = []

        sesiones[sesion].append(archivo)


    sesiones_disponibles = sorted(sesiones.keys())


    # 50% de las sesiones
    cantidad = len(sesiones_disponibles) // 2


    sesiones_elegidas = rng.sample(
        sesiones_disponibles,
        cantidad
    )


    seleccionados = []

    for sesion in sesiones_elegidas:
        seleccionados.extend(
            sesiones[sesion]
        )


    return sorted(
        seleccionados,
        key=lambda p: p.name
    ), sesiones_elegidas



def seleccionar_muestra():

    rng = random.Random(SEED)


    archivos_b1 = sorted(
        DIR_B1.glob("*.txt")
    )

    archivos_b2 = sorted(
        DIR_B2.glob("*.txt")
    )


    muestra_b1, sesiones_b1 = seleccionar_por_sesion(
        archivos_b1,
        rng
    )


    muestra_b2, sesiones_b2 = seleccionar_por_sesion(
        archivos_b2,
        rng
    )


    # control: que no haya sesiones repetidas
    repetidas = set(sesiones_b1) & set(sesiones_b2)

    if repetidas:
        raise ValueError(
            f"Sesiones presentes en ambos batches: {repetidas}"
        )


    return (
        muestra_b1,
        muestra_b2,
        sesiones_b1,
        sesiones_b2
    )


# ==========================
# Pipeline
# ==========================

def ejecutar_pipeline():

    (
        muestra_b1,
        muestra_b2,
        sesiones_b1,
        sesiones_b2
    ) = seleccionar_muestra()


    print("=== Sesiones seleccionadas ===")


    print("\nB1 sesiones:")
    for s in sorted(sesiones_b1):
        print(" ", s)


    print("\nB2 sesiones:")
    for s in sorted(sesiones_b2):
        print(" ", s)



    print("\n=== Archivos ===")


    print("\nB1")
    for archivo in muestra_b1:
        print(" ", archivo.name)


    print("\nB2")
    for archivo in muestra_b2:
        print(" ", archivo.name)



    resultados = []


    for batch, archivos in [
        ("b1", muestra_b1),
        ("b2", muestra_b2)
    ]:

        print(f"\nProcesando {batch}...")


        for archivo in archivos:

            try:

                contenido = leer_archivo(
                    archivo
                )


                lsm = calculo_LSM(
                    contenido
                )


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


                print(
                    f"✓ {archivo.name}: {lsm:.4f}"
                )


            except Exception as e:

                print(
                    f"✗ Error en {archivo.name}: {e}"
                )



    df = pd.DataFrame(resultados)


    # sacar diálogos donde LSM no pudo calcularse
    df = df[df["lsm"] > 0]


    df.to_csv(
        OUTPUT_CSV,
        index=False
    )


    print("\n==============================")
    print(
        f"Conversaciones procesadas: {len(df)}"
    )
    print(
        f"CSV guardado en: {OUTPUT_CSV}"
    )


if __name__ == "__main__":
    ejecutar_pipeline()