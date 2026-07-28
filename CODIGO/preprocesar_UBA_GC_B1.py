from pathlib import Path
import re

# Rutas de entrada y salida
PHRASES_DIR = Path("/home/tgallo/Downloads/UBA-GC/b1-dialogue-phrases")
TASKS_DIR = Path("/home/tgallo/Downloads/UBA-GC/b1-dialogue-tasks")
OUTPUT_DIR = Path("/home/tgallo/Documents/Proyecto_modular/CODIGO/muestras_UBA_CG_B1")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TAG_RE = re.compile(r"<[^>]+>")


def cargar_tareas(task_path):
    intervalos = []
    if not task_path.exists():
        return intervalos

    with open(task_path, encoding="utf8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue

            partes = linea.split(maxsplit=2)
            if len(partes) < 3:
                continue

            inicio, fin, info = partes

            if info.strip() == "#":
                continue

            try:
                intervalos.append((float(inicio), float(fin), info.strip()))
            except ValueError:
                continue

    return intervalos


def leer_phrases(path, hablante):
    eventos = []
    if not path.exists():
        return eventos

    with open(path, encoding="utf8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue

            partes = linea.split(maxsplit=2)
            if len(partes) < 3:
                continue

            inicio, fin, texto = partes
            texto = texto.strip()

            if texto == "#":
                continue

            texto = TAG_RE.sub("", texto).strip()
            if not texto:
                continue

            try:
                eventos.append((float(inicio), hablante, texto))
            except ValueError:
                continue

    return eventos


task_files = sorted(TASKS_DIR.glob("*.tasks"))

for task_file in task_files:
    # Obtener prefijo tipo "s01.objects" desde el nombre "s01.objects.1.tasks"
    nombre_base = task_file.name.replace(".tasks", "")
    partes_nombre = task_file.name.split(".")
    
    sesion_id = partes_nombre[0]  # Ej: 's01'
    
    # Construir el prefijo base: 's01.objects' (o 's01' si no contiene la palabra 'objects')
    if len(partes_nombre) > 1 and partes_nombre[1] != "tasks":
        prefijo_salida = f"{sesion_id}.{partes_nombre[1]}"
    else:
        prefijo_salida = f"{sesion_id}.objects"

    tareas = cargar_tareas(task_file)
    if not tareas:
        continue

    archivo_A = PHRASES_DIR / f"{sesion_id}.A.phrases"
    archivo_B = PHRASES_DIR / f"{sesion_id}.B.phrases"

    if not archivo_A.exists():
        archivo_A = PHRASES_DIR / f"{nombre_base}.A.phrases"
        archivo_B = PHRASES_DIR / f"{nombre_base}.B.phrases"

    eventos = []
    eventos.extend(leer_phrases(archivo_A, "A"))
    eventos.extend(leer_phrases(archivo_B, "B"))

    if not eventos:
        continue

    eventos.sort(key=lambda x: x[0])

    guardados = 0
    for i, (t_inicio, t_fin, info) in enumerate(tareas, start=1):
        frases_tarea = [
            (h, txt) for inicio, h, txt in eventos if t_inicio <= inicio < t_fin
        ]

        if not frases_tarea:
            continue

        # Nombramiento en formato tipo: s21.objects.03.txt
        nombre_salida = f"{prefijo_salida}.{i:02d}.txt"
        salida_path = OUTPUT_DIR / nombre_salida

        with open(salida_path, "w", encoding="utf8") as f:
            for hablante, texto in frases_tarea:
                f.write(f"{hablante}: {texto}\n")

        guardados += 1

    print(f"Sesión {prefijo_salida}: {guardados} tareas creadas.")

print("\n¡Listo!")