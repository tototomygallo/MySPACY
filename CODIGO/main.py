from LSM import compute_LSM_LIWC
from CODIGO.Herramientas.parseo.py import load_conversation_from_file

# --- TEST CON DATOS INVENTADOS (Lo que pidió el profe) ---
test_conv = [
    "GINS: before you proceed further...",
    "LUTH: Not directly like that...",
    "GINS: And did you present it?"
]

resultado_test = compute_LSM_LIWC(test_conv)
print(f"Test LSM: {resultado_test:.4f}")

# --- PROCESAMIENTO REAL ---
# archivo = "3_1_RoundC_all.txt"
# conv_real = load_conversation_from_file(archivo)
# print(f"LSM Archivo: {compute_LSM_LIWC(conv_real)}")