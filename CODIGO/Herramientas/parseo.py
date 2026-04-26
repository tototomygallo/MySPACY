import os

def cargar_de_archivo(filepath: str) -> list[str]:
    """Lee un archivo y devuelve una lista de líneas."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def cargar_de_lista(directory: str):
    """Generador que entrega conversaciones de una carpeta."""
    for filename in sorted(os.listdir(directory)):
        if filename.endswith((".txt", ".phrases")):
            yield filename, cargar_de_archivo(os.path.join(directory, filename))