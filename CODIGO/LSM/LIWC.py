import subprocess
import pandas as pd
import os

def computar_LSM_LIWC(file_path: str, output_dir: str) -> float:
    """Ejecuta LIWC-22-cli y extrae el valor de LSM."""
    

    output_file = os.path.join(output_dir, "LSM-Group-Pairwise.csv")
    
    # LIMPIEZA PREVIA: Si el archivo existe del loop anterior, lo borramos
    if os.path.exists(output_file):
        os.remove(output_file)

    # Creo el comando tal cual lo uso en terminal
    comando = [
        "/opt/liwc-22/bin/LIWC-22-cli",
        "-m", "lsm",
        "-i", file_path,
        "-o", output_dir,
        "-gc", "0", "-pc", "1", "-tc", "2", "-ot", "2", "-clsm", "1",
        "-delim", ":", "-expo"
    ]
    
    try:
        # Ejecutar comando
        subprocess.run(comando, check=True, capture_output=True)
        
        output_file =  "tests/LSM-Speaker-Pairwise.csv" # accedo al archivo que tiene el lsm
        df = pd.read_csv(output_file, sep=":")  # Ajusto el separador
        print(df)
        # Retorno el valor de la columna LSM
        return float(df['LSM'].iloc[0])
    except Exception as e:
        print(f"Error en LIWC para {file_path}: {e}")
        return None