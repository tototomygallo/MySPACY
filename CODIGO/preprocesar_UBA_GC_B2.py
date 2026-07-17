from pathlib import Path
import re
import random


INPUT_DIR = Path("/home/tgallo/Downloads/UBA-GC/b2-dialogue-phrases")
OUTPUT_DIR = Path("/home/tgallo/Documents/Proyecto_modular/CODIGO/muestras_UBA_CG_B2")

OUTPUT_DIR.mkdir(exist_ok=True)

SEED = 42

MIN_TURNOS = 3
MIN_PALABRAS = 100


TAG_RE = re.compile(r"<[^>]+>")


def leer_archivo(path, hablante):

    eventos = []

    with open(path, encoding="utf8") as f:

        for linea in f:

            partes = linea.rstrip().split("\t")

            if len(partes) != 3:
                continue

            inicio, fin, texto = partes

            texto = texto.strip()

            if texto == "#":
                continue

            texto = TAG_RE.sub("", texto).strip()

            if not texto:
                continue

            eventos.append(
                (float(inicio), hablante, texto)
            )

    return eventos


def tiene_suficiente_dialogo(eventos):

    turnos = {
        "A": 0,
        "B": 0
    }

    palabras = {
        "A": 0,
        "B": 0
    }


    for _, hablante, texto in eventos:

        turnos[hablante] += 1
        palabras[hablante] += len(texto.split())


    return (
        turnos["A"] >= MIN_TURNOS and
        turnos["B"] >= MIN_TURNOS and
        palabras["A"] >= MIN_PALABRAS and
        palabras["B"] >= MIN_PALABRAS
    )


def obtener_sesion(nombre):

    return re.match(r"(s\d+)", nombre).group(1)



# -------------------------
# Leer todas las tareas
# -------------------------

conversaciones_validas = []


archivos = list(INPUT_DIR.glob("*.phrases"))


for archivo in archivos:

    nombre = archivo.name


    if "channel1" not in nombre:
        continue


    archivo_A = archivo

    archivo_B = INPUT_DIR / nombre.replace(
        "channel1",
        "channel2"
    )


    if not archivo_B.exists():
        continue


    eventos = []

    eventos.extend(
        leer_archivo(archivo_A, "A")
    )

    eventos.extend(
        leer_archivo(archivo_B, "B")
    )


    eventos.sort(key=lambda x: x[0])


    if tiene_suficiente_dialogo(eventos):

        conversaciones_validas.append(
            {
                "sesion": obtener_sesion(nombre),
                "nombre": nombre.replace(
                    ".channel1.phrases",
                    ""
                ),
                "eventos": eventos
            }
        )


print(
    "Conversaciones válidas:",
    len(conversaciones_validas)
)


# -------------------------
# Guardar las válidas
# -------------------------

for conv in conversaciones_validas:

    salida = OUTPUT_DIR / f"{conv['nombre']}.txt"

    with open(salida, "w", encoding="utf8") as f:

        for _, hablante, texto in conv["eventos"]:

            f.write(
                f"{hablante}: {texto}\n"
            )


    print(
        "Generado:",
        salida.name
    )


print("Listo.")