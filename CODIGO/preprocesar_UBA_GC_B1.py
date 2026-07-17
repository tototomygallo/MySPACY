from pathlib import Path
import re

INPUT_DIR = Path("/home/tgallo/Downloads/UBA-GC/b1-dialogue-phrases")
OUTPUT_DIR = Path("/home/tgallo/Documents/Proyecto_modular/CODIGO/muestras_UBA_CG")

OUTPUT_DIR.mkdir(exist_ok=True)

TAG_RE = re.compile(r"<[^>]+>")   # elimina <risa>, <tos>, etc.


def leer_archivo(path, hablante):
    eventos = []

    with open(path, encoding="utf8") as f:
        for linea in f:
            partes = linea.rstrip().split("\t")

            if len(partes) != 3:
                continue

            inicio, fin, texto = partes

            texto = texto.strip()

            # silencio
            if texto == "#":
                continue

            # elimina etiquetas
            texto = TAG_RE.sub("", texto).strip()

            if not texto:
                continue

            eventos.append(
                (float(inicio), hablante, texto)
            )

    return eventos


# encontrar todas las sesiones
sesiones = sorted({
    p.name.split(".A.")[0].split(".B.")[0]
    for p in INPUT_DIR.glob("*.phrases")
})

for sesion in sesiones:

    archivo_A = INPUT_DIR / f"{sesion}.A.phrases"
    archivo_B = INPUT_DIR / f"{sesion}.B.phrases"

    eventos = []

    if archivo_A.exists():
        eventos.extend(leer_archivo(archivo_A, "A"))

    if archivo_B.exists():
        eventos.extend(leer_archivo(archivo_B, "B"))

    eventos.sort(key=lambda x: x[0])

    salida = OUTPUT_DIR / f"{sesion}.txt"

    with open(salida, "w", encoding="utf8") as f:
        for _, hablante, texto in eventos:
            f.write(f"{hablante}: {texto}\n")

print("Listo.")