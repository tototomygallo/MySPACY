from LSM.myspacy import conteo_categorias
from Herramientas.parseo import cargar_de_archivo
from LSM.myspacy import calculo_LSM  

def main():
    # --- ESCENARIO 1: IGUALES (Sincronía Total) ---
    # Usan exactamente las mismas palabras 
    iguales = [
        "USER1: I am in the house.",
        "USER2: I am in the house."
    ]

    # --- ESCENARIO 2: TOTALMENTE DISTINTOS ---
    # Uno habla mas que el otro y el otro casi nada
    distintos = [
        "USER1: I will go to the office with my boss today.", 
        "USER2: Working."                                     # Nada
    ]

    # --- ESCENARIO 3: PARECIDOS (Alta Sincronía) ---

    parecidos = [
        "USER1: I think that we should go to the park.",
        "USER2: I believe that it is a good idea for us."
    ]

    # --- ESCENARIO 4: UN POCO MENOS PARECIDOS ---

    menos_parecidos = [
        "USER1: The very big dog is here now.", # Artículos y adverbios
        "USER2: he is here bro."                     # Solo sustantivo y verbo
    ]

    print("=== RESULTADOS DE TESTEO LSM ===")
    print(f"1. Iguales:           {calculo_LSM(iguales):.4f}")
    print(f"2. Distintos:         {calculo_LSM(distintos):.4f}")
    print(f"3. Parecidos:         {calculo_LSM(parecidos):.4f}")
    print(f"4. Menos Parecidos:   {calculo_LSM(menos_parecidos):.4f}")

    # --- PROCESAMIENTO REAL ---
    #archivo = "/home/tgallo/Documents/Proyecto_labo_IA/3_1_IDENTICOS.txt"
    #conv_real = cargar_de_archivo(archivo)


    #print(f"LSM Archivo: {calculo_LSM(conv_real)}")

if __name__ == "__main__":
    main()