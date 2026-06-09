import unittest
import os
import numpy as np
from LSM.myspacy import calculo_LSM  # Tu función oficial
from Herramientas.parseo import cargar_de_archivo  # Para cargar los archivos de testeo


class TestLSM(unittest.TestCase):
    
    def setUp(self):
        # ACÁ CARGO TUS CÁLCULOS MANUALES
        # Formato: "nombre_archivo": valor_manual
        self.CASOS_TEST = {
            "archivos_unitest/3_1_RoundC_all.txt": 0.8021,
            "archivos_unitest/4_3_RoundB_all.txt": 0.5495,
            "archivos_unitest/3_1_IDENTICOS.txt": 1.0000,
            "archivos_unitest/3_1_DISTINTOS.txt": 0.4153,
            "archivos_unitest/bot_vs_personita.txt": 0.6015 
        }
        self.tolerancia = 0.001 # Margen por redondeo manual

    def test_lsm_variantes(self):
        print("\n" + "="*50)
        print("INICIANDO TESTING DE LSM - VALIDACIÓN MANUAL")
        print("="*50)
        
        for archivo, valor_esperado in self.CASOS_TEST.items():
            with self.subTest(archivo=archivo):
                if not os.path.exists(archivo):
                    print(f"Saltando {archivo}: No existe el archivo.")
                    continue
                
                conversacion = cargar_de_archivo(archivo)
                valor_codigo = calculo_LSM(conversacion)
                
                print(f"\n Archivo: {archivo}")
                print(f"   - Esperado (Manual): {valor_esperado:.4f}")
                print(f"   - Obtenido (Código): {valor_codigo:.4f}")
                
                self.assertAlmostEqual(
                    valor_codigo, 
                    valor_esperado, 
                    delta=self.tolerancia,
                    msg=f"Error en {archivo}: La diferencia excede la tolerancia."
                )
                print("   ✅ Resultado: COINCIDE")

if __name__ == "__main__":
    unittest.main()