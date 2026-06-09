from LIWC import computar_LSM_LIWC

# --- CONFIGURACIÓN ---
archivo_de_prueba = "/home/tgallo/Documents/Proyecto_modular/archivos_unitest/3_1_RoundC_all.txt" # Ajustá esta ruta a un archivo real

# --- TEST ---
print("--- TESTEANDO MOTOR LIWC ---")
resultado = computar_LSM_LIWC(archivo_de_prueba,"tests")

if resultado is not None:
    print(f"✅ ¡Éxito! El LSM según LIWC es: {resultado}")
else:
    print("Safamos... algo falló. Revisá la consola.")