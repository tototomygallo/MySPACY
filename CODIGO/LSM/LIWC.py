import subprocess
import pandas as pd
import os

def compute_LSM_LIWC(file_path: str, output_dir: str) -> float:
    """Ejecuta LIWC-22-cli y extrae el valor de LSM."""
    
    # Creamos el comando tal cual lo usas en terminal
    command = [
        "/opt/liwc-22/bin/LIWC-22-cli",
        "-m", "lsm",
        "-i", file_path,
        "-o", output_dir,
        "-gc", "0", "-pc", "1", "-tc", "2", "-ot", "2", "-clsm", "3",
        "-delim", ":", "-expo"
    ]
    
    try:
        # Ejecutar comando
        subprocess.run(command, check=True, capture_output=True)
        
        # LIWC genera un archivo de salida, usualmente un .csv o .txt 
        # Debes leer el archivo generado para extraer el número del LSM
        # Ajusta el nombre del archivo según lo que genere LIWC-22
        output_file =  "tests/LSM-Group-Pairwise.csv"
        df = pd.read_csv(output_file, sep=":")  # Ajusta el separador si es necesario
        print(df)
        # Retornamos el valor de la columna LSM (ajustar nombre de columna según LIWC)
        return float(df['LSM'].iloc[0])
    except Exception as e:
        print(f"Error en LIWC para {file_path}: {e}")
        return None