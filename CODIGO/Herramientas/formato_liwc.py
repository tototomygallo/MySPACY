"""
Convierte pares de archivos de transcripción (A y B) al formato .phrases.

Uso:
    python convert_to_phrases.py --input_dir ./transcripts --output_dir ./output

Los archivos deben seguir el patrón:
    sw2095A-ms98-a-trans.text  (hablante A)
    sw2095B-ms98-a-trans.text  (hablante B)

El script detecta automáticamente los pares y genera un archivo .phrases por par.
"""

import re
import os
import argparse
from collections import defaultdict


def parsear_archivo(filepath, speaker):
    segments = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(' ', 3)
            if len(parts) < 4:
                continue
            seg_id, start, end, text = parts
            try:
                start = float(start)
            except ValueError:
                continue

            # Eliminar anotaciones de silencio/ruido/risa
            clean = re.sub(r'\[silence\]|\[noise\]|\[laughter[^\]]*\]|\[vocalized-noise\]', '', text).strip()
            if not clean:
                continue
            # Eliminar cualquier otra anotación entre corchetes
            clean = re.sub(r'\[[^\]]*\]', '', clean).strip()
            if not clean:
                continue

            segments.append((start, speaker, clean))
    return segments


def encontrar_hablantes(input_dir):
    """
    Detecta automáticamente pares A/B en el directorio.
    Soporta patrones como:
        sw2095A-ms98-a-trans.text / sw2095B-ms98-a-trans.text
    """
    files = os.listdir(input_dir)
    groups = defaultdict(dict)

    for fname in files:
        # Busca archivos con A o B como identificador de hablante
        match = re.match(r'^(.+?)(A|B)(-ms98-a-trans)(\.text)$', fname)
        if match:
            prefix = match.group(1)
            speaker = match.group(2)
            suffix = (match.group(3) or '') + match.group(4)
            key = prefix + suffix
            groups[key][speaker] = fname

    pairs = []
    for key, speakers in groups.items():
        if 'A' in speakers and 'B' in speakers:
            pairs.append((key, speakers['A'], speakers['B']))
        else:
            print(f"  [AVISO] Par incompleto, se omite: {speakers}")

    return pairs


def convert_pares(input_dir, file_a, file_b, output_dir, output_name):
    path_a = os.path.join(input_dir, file_a)
    path_b = os.path.join(input_dir, file_b)

    a_segs = parsear_archivo(path_a, 'A')
    b_segs = parsear_archivo(path_b, 'B')

    all_segs = sorted(a_segs + b_segs, key=lambda x: x[0])
    lines = [f"{speaker}: {text}" for _, speaker, text in all_segs]

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, output_name)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    return out_path


def main():
    parser = argparse.ArgumentParser(description='Convierte pares A/B de transcripciones a formato .phrases')
    parser.add_argument('--input_dir', default='.', help='Directorio con los archivos de transcripción')
    parser.add_argument('--output_dir', default='./output', help='Directorio de salida para los .phrases')
    args = parser.parse_args()

    print(f"\nBuscando pares en: {args.input_dir}")
    pairs = encontrar_hablantes(args.input_dir)

    if not pairs:
        print("No se encontraron pares A/B. Verificá que los archivos sigan el patrón correcto.")
        return

    print(f"Se encontraron {len(pairs)} par(es):\n")
    for key, file_a, file_b in pairs:
        # Generar nombre de salida basado en la clave del par
        out_name = re.sub(r'[-_]trans$', '', os.path.splitext(key)[0]) + '.txt'
        out_path = convert_pares(args.input_dir, file_a, file_b, args.output_dir, out_name)
        print(f"  ✓ {file_a} + {file_b}  →  {out_path}")

    print(f"\n¡Listo! {len(pairs)} archivo(s) generado(s) en '{args.output_dir}'")


if __name__ == '__main__':
    main()