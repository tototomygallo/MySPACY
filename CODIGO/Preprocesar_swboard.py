import os
import random
from Herramientas.formato_liwc import find_pairs, convert_pair

def ejecutar_muestreo_aleatorio(root_dir, output_base, porcentaje=0.1):
    todos_los_pares = []

    # 1. Caminar por todo el árbol de directorios
    print("Escaneando directorios para encontrar diálogos...")
    for root, dirs, files in os.walk(root_dir):
        # Solo buscamos en carpetas que tengan archivos, evitando niveles superiores
        if any(f.endswith('.text') for f in files):
            pares = find_pairs(root)
            for key, file_a, file_b in pares:
                todos_los_pares.append({
                    'input_dir': root,
                    'key': key,
                    'file_a': file_a,
                    'file_b': file_b
                })

    if not todos_los_pares:
        print("No se encontraron pares en ninguna carpeta.")
        return

    # 2. Seleccionar el 10% aleatorio
    cantidad_a_procesar = max(1, int(len(todos_los_pares) * porcentaje))
    seleccionados = random.sample(todos_los_pares, cantidad_a_procesar)
    
    print(f"Total encontrado: {len(todos_los_pares)} pares.")
    print(f"Procesando muestra aleatoria del {porcentaje*100}% ({cantidad_a_procesar} archivos)...")

    # 3. Procesar y guardar
    for item in seleccionados:
        # Limpiamos el nombre para el .phrases (como hacías en tu main)
        import re
        out_name = re.sub(r'[-_]trans$', '', os.path.splitext(item['key'])[0]) + '.phrases'
        
        convert_pair(
            item['input_dir'], 
            item['file_a'], 
            item['file_b'], 
            output_base, 
            out_name
        )
        print(f"  ✓ Generado: {out_name}")

if __name__ == "__main__":
    # Ajustá estas rutas a tu conveniencia
    RUTA_DATOS = os.path.expanduser("~/Downloads/switchboard_word_alignments/swb_ms98_transcriptions")
    RUTA_SALIDA = "./SW_PROCESSED"
    
    ejecutar_muestreo_aleatorio(RUTA_DATOS, RUTA_SALIDA, porcentaje=0.1)