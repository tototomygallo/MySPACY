import os
import re
import xml.etree.ElementTree as ET

def limpiar_texto_pentocv(texto: str) -> str:
    """Limpia metadatos, marcas discursivas y caracteres sueltos de PentoCV."""
    if not texto:
        return ""
    texto = re.sub(r'<[^>]+>', '', texto)
    texto = re.sub(r'\{F\s+[^}]*\}', '', texto)
    texto = re.sub(r'\{[^}]*\}', '', texto)
    #texto = re.sub(r'\$[A-Z]\b', '', texto)
    texto = re.sub(r'\$[A-Za-z]+\b', '', texto)
    texto = re.sub(r'\(\([^)]*\)\)', '', texto)
    texto = re.sub(r'\([^)]*?\+?\s*(\'[a-z]+|[a-zA-ZäöüÄÖÜß]+)\)', r'\1', texto)
    texto = re.sub(r'\([^)]*\)', '', texto)
    texto = re.sub(r'[()\[\]{}]', '', texto)
    texto = re.sub(r'\s+\.\s+', ' ', texto)
    texto = re.sub(r'^\.\s+|\s+\.$', '', texto)
    return re.sub(r'\s+', ' ', texto).strip()


def eaf_a_dialogos_por_tarea(ruta_eaf: str) -> dict[str, list[str]]:
    """
    Parsea el .eaf dividiendo las intervenciones en tareas según la capa 'Part'.
    Devuelve un diccionario: {'1': ['A: ...', 'B: ...'], '2': [...]}
    """
    tree = ET.parse(ruta_eaf)
    root = tree.getroot()

    # 1. Mapa de Time Slots (ID -> Milisegundos)
    timeslots = {}
    for ts in root.findall(".//TIME_SLOT"):
        ts_id = ts.attrib.get("TIME_SLOT_ID")
        ts_val = ts.attrib.get("TIME_VALUE")
        if ts_id and ts_val:
            timeslots[ts_id] = int(ts_val)

    # 2. Mapas auxiliares para anotaciones
    ann_to_ts = {}
    ann_to_ref = {}

    for ann in root.findall(".//ANNOTATION/*"):
        ann_id = ann.attrib.get("ANNOTATION_ID")
        if not ann_id:
            continue
        if "TIME_SLOT_REF1" in ann.attrib:
            ann_to_ts[ann_id] = ann.attrib["TIME_SLOT_REF1"]
        if "ANNOTATION_REF" in ann.attrib:
            ann_to_ref[ann_id] = ann.attrib["ANNOTATION_REF"]

    def resolver_tiempo(ann_id: str) -> int:
        visited = set()
        curr = ann_id
        while curr and curr not in visited:
            visited.add(curr)
            if curr in ann_to_ts:
                ts_id = ann_to_ts[curr]
                return timeslots.get(ts_id, 0)
            curr = ann_to_ref.get(curr)
        return 0

    # 3. Extrae capa 'Part'
    intervalos_part = []
    tier_part = root.find(".//TIER[@TIER_ID='Part']")

    if tier_part is not None:
        for ann in tier_part.findall(".//ALIGNABLE_ANNOTATION"):
            val_elem = ann.find("ANNOTATION_VALUE")
            nombre_tarea = val_elem.text.strip() if val_elem is not None and val_elem.text else ""
            
            ts_start_id = ann.attrib.get("TIME_SLOT_REF1")
            ts_end_id = ann.attrib.get("TIME_SLOT_REF2")

            t_start = timeslots.get(ts_start_id, 0)
            t_end = timeslots.get(ts_end_id, float("inf"))

            if nombre_tarea:
                intervalos_part.append((t_start, t_end, nombre_tarea))

    # Ordena los intervalos por tiempo de inicio
    intervalos_part.sort(key=lambda x: x[0])

    # 4. Extrae todas las intervenciones de A-utts y B-utts
    intervenciones = []
    for tier in root.findall(".//TIER"):
        tier_id = tier.attrib.get("TIER_ID", "")
        if tier_id not in ["A-utts", "B-utts"]:
            continue

        hablante = "A" if tier_id.startswith("A") else "B"

        for ann in tier.findall(".//ANNOTATION/*"):
            ann_id = ann.attrib.get("ANNOTATION_ID")
            val_elem = ann.find("ANNOTATION_VALUE")
            val_text = val_elem.text if val_elem is not None else ""
            texto_limpio = limpiar_texto_pentocv(val_text or "")

            if texto_limpio:
                tiempo_ms = resolver_tiempo(ann_id)
                intervenciones.append((tiempo_ms, hablante, texto_limpio))

    intervenciones.sort(key=lambda x: x[0])

    # 5. Asignar cada intervención a su correspondiente intervalo de 'Part'
    tareas_dialogos = {}

    if not intervalos_part:
        # Si un archivo no tiene capa 'Part', se guarda todo en una sola tarea '1'
        tareas_dialogos["1"] = [f"{h}: {t}" for _, h, t in intervenciones]
        return tareas_dialogos

    for t_start, t_end, nombre_tarea in intervalos_part:
        dialogo_tarea = []
        for t_ms, hablante, texto in intervenciones:
            if t_start <= t_ms < t_end:
                dialogo_tarea.append(f"{hablante}: {texto}")
        
        if dialogo_tarea:
            # Limpiar el nombre de la tarea para usarlo como nombre de archivo seguro
            nombre_limpio = re.sub(r'[^\w\-]', '_', nombre_tarea)
            tareas_dialogos[nombre_limpio] = dialogo_tarea

    return tareas_dialogos


def guardar_dialogos_por_tarea(carpeta_origen: str, carpeta_destino: str):
    """
    Recorre los .eaf, extrae las tareas de la capa 'Part' y guarda
    archivos .txt individuales para cada tarea (ej: r1_part1.txt).
    """
    os.makedirs(carpeta_destino, exist_ok=True)

    for archivo in os.listdir(carpeta_origen):
        if archivo.endswith(".eaf"):
            ruta_eaf = os.path.join(carpeta_origen, archivo)
            base_nombre = os.path.splitext(archivo)[0]
            
            tareas = eaf_a_dialogos_por_tarea(ruta_eaf)

            for idx_tarea, (nombre_tarea, lineas_dialogo) in enumerate(tareas.items(), 1):
                nombre_txt = f"{base_nombre}_part{idx_tarea}_{nombre_tarea}.txt"
                ruta_txt = os.path.join(carpeta_destino, nombre_txt)

                with open(ruta_txt, "w", encoding="utf-8") as f:
                    f.write("\n".join(lineas_dialogo))

                print(f" Guardado: {ruta_txt}")


if __name__ == "__main__":
    CARPETA_EAF = "datos_aleman"
    CARPETA_TXT = "dialogos_por_tarea"

    guardar_dialogos_por_tarea(CARPETA_EAF, CARPETA_TXT)