class PilaBalanceador:
    def __init__(self):
        self.pila = []
        self.pasos = []
    
    def push(self, elemento):
        """Agrega un elemento a la pila y registra el paso"""
        self.pila.append(elemento)
        self.pasos.append(f"PUSH '{elemento}' -> Pila: {self.pila}")
    
    def pop(self):
        """Remueve y retorna el elemento superior de la pila"""
        if not self.pila:
            self.pasos.append("POP -> Pila vacía, no se puede hacer POP")
            return None
        elemento = self.pila.pop()
        self.pasos.append(f"POP '{elemento}' -> Pila: {self.pila}")
        return elemento
    
    def is_empty(self):
        """Verifica si la pila está vacía"""
        return len(self.pila) == 0
    
    def peek(self):
        """Retorna el elemento superior sin removerlo"""
        if not self.pila:
            return None
        return self.pila[-1]
    
    def reset(self):
        """Reinicia la pila y los pasos"""
        self.pila = []
        self.pasos = []

def es_simbolo_apertura(caracter):
    """Verifica si el carácter es un símbolo de apertura"""
    return caracter in '([{'

def es_simbolo_cierre(caracter):
    """Verifica si el carácter es un símbolo de cierre"""
    return caracter in ')]}'

def son_pareja(apertura, cierre):
    """Verifica si los símbolos forman una pareja válida"""
    parejas = {'(': ')', '[': ']', '{': '}'}
    return parejas.get(apertura) == cierre

def balancear_expresion(expresion):
    """
    Verifica si una expresión está balanceada usando una pila
    Retorna (es_balanceada, pasos_detallados)
    """
    pila = PilaBalanceador()
    
    print(f"\n--- Procesando expresión: '{expresion}' ---")
    pila.pasos.append(f"Iniciando análisis de: '{expresion}'")
    pila.pasos.append("Pila inicial: []")
    
    for i, caracter in enumerate(expresion):
        if es_simbolo_apertura(caracter):
            pila.push(caracter)
            pila.pasos.append(f"Posición {i}: Encontrado símbolo de apertura '{caracter}'")
        
        elif es_simbolo_cierre(caracter):
            pila.pasos.append(f"Posición {i}: Encontrado símbolo de cierre '{caracter}'")
            
            if pila.is_empty():
                pila.pasos.append(f"ERROR: Símbolo de cierre '{caracter}' sin apertura correspondiente")
                return False, pila.pasos
            
            simbolo_apertura = pila.pop()
            
            if not son_pareja(simbolo_apertura, caracter):
                pila.pasos.append(f"ERROR: '{simbolo_apertura}' no hace pareja con '{caracter}'")
                return False, pila.pasos
            else:
                pila.pasos.append(f"OK: '{simbolo_apertura}' hace pareja con '{caracter}'")
    
    
    if not pila.is_empty():
        pila.pasos.append(f"ERROR: Símbolos sin cerrar en la pila: {pila.pila}")
        return False, pila.pasos
    else:
        pila.pasos.append("✓ Pila vacía - Expresión balanceada correctamente")
        return True, pila.pasos

def procesar_archivo(nombre_archivo):
    """
    Procesa un archivo línea por línea verificando el balanceo
    """
    try:
        print(f"=== PROCESANDO ARCHIVO: {nombre_archivo} ===\n")
        
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            lineas = archivo.readlines()
        
        print(f"Archivo leído exitosamente. Total de líneas: {len(lineas)}")
        print("Contenido del archivo:")
        print("-" * 50)
        for i, linea in enumerate(lineas, 1):
            print(f"Línea {i}: {linea.strip()}")
        print("-" * 50)
        
        resultados = []
        
        for numero_linea, linea in enumerate(lineas, 1):
            expresion = linea.strip()
            if expresion:  # Solo procesar líneas no vacías
                print(f"\n{'='*60}")
                print(f"LÍNEA {numero_linea}")
                print(f"{'='*60}")
                
                es_balanceada, pasos = balancear_expresion(expresion)
                
               
                print("\nPasos del algoritmo:")
                for i, paso in enumerate(pasos, 1):
                    print(f"  {i:2d}. {paso}")
                
                
                resultado = "BALANCEADA" if es_balanceada else "NO BALANCEADA"
                print(f"\n🔍 RESULTADO: La expresión está {resultado}")
                
                resultados.append({
                    'linea': numero_linea,
                    'expresion': expresion,
                    'balanceada': es_balanceada,
                    'resultado': resultado
                })
        
        
        print(f"\n{'='*60}")
        print("RESUMEN FINAL")
        print(f"{'='*60}")
        for resultado in resultados:
            print(f"Línea {resultado['linea']}: {resultado['resultado']}")
            print(f"  └── {resultado['expresion']}")
        
        balanceadas = sum(1 for r in resultados if r['balanceada'])
        print(f"\nTotal procesadas: {len(resultados)}")
        print(f"Balanceadas: {balanceadas}")
        print(f"No balanceadas: {len(resultados) - balanceadas}")
        
    except FileNotFoundError:
        print(f" ERROR: No se pudo encontrar el archivo '{nombre_archivo}'")
        print("Asegúrate de que el archivo existe en el directorio actual.")
    except Exception as e:
        print(f" ERROR al procesar el archivo: {e}")

def main():
    """
    Función principal del programa
    """
    print("🔧 ALGORITMO DE BALANCEO DE EXPRESIONES CON PILA")
    print("=" * 55)
    
   
    nombre_archivo = "prueba-ejercicio2.txt"
    
    
    procesar_archivo(nombre_archivo)
    
    print(f"\n{'='*60}")
    print("PROGRAMA FINALIZADO")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
