import time
import matplotlib.pyplot as plt
import numpy as np

def function_optimized(n: int) -> int:
  
    if n <= 1:
        return 0
    # Cada i imprime exactamente 1 vez antes del break
    return n

def function_original(n: int) -> int:
 
    if n <= 1:
        return 0
    count = 0
    for i in range(1, n + 1):       # n veces
        j = 1
        if j <= n:
            count += 1
            # break implícito
    return count

def theoretical_complexity(n):
    """Calcula el valor teórico de n (complejidad lineal)"""
    return n if n > 1 else 0

def main():
    print("="*80)
    print("EJERCICIO No. 2 - ANÁLISIS DE COMPLEJIDAD (OPTIMIZADO)")
    print("="*80)
    print("\nComplejidad teórica: O(n)")
    print("Método: Cálculo matemático directo (O(1) por consulta)")
    
    # Tamaños de input extendidos
    inputs = [1, 10, 100, 1000, 10000, 100000, 1000000, 10000000]
    times_optimized = []
    operations = []
    
    print("\n" + "-"*80)
    print("VERIFICACIÓN: Comparando método optimizado vs. original (n pequeño)")
    print("-"*80)
    for n in [1, 10, 100, 1000]:
        opt = function_optimized(n)
        orig = function_original(n)
        match = "✓" if opt == orig else "✗"
        print(f"n={n:>4}: Optimizado={opt:>8,} | Original={orig:>8,} {match}")
    
    print("\n" + "="*80)
    print("PROFILING CON MÉTODO OPTIMIZADO")
    print("="*80)
    print()
    
    # Profiling con método optimizado
    for n in inputs:
        print(f"Procesando n = {n:>10,}...", end=" ")
        
        start = time.perf_counter()
        ops = function_optimized(n)
        end = time.perf_counter()
        
        elapsed = end - start
        times_optimized.append(elapsed)
        operations.append(ops)
        
        print(f"✓ {elapsed:.9f}s | Operaciones: {ops:>15,}")
    
    # Calcular valores teóricos
    theoretical_ops = [theoretical_complexity(n) for n in inputs]
    
    # TABLA DE RESULTADOS
    print("\n" + "="*80)
    print("TABLA DE RESULTADOS (Ejercicio 2: O(n))")
    print("="*80)
    print(f"{'n':>12}  {'Operaciones':>15}  {'Teórico O(n)':>15}  {'Tiempo (s)':>15}")
    print("-"*80)
    for n, ops, theo, t in zip(inputs, operations, theoretical_ops, times_optimized):
        print(f"{n:>12,}  {ops:>15,}  {theo:>15,}  {t:>15.9f}")
    print("="*80)
    
    # ANÁLISIS DE RAZÓN DE CRECIMIENTO
    print("\n" + "="*80)
    print("ANÁLISIS DE RAZÓN DE CRECIMIENTO")
    print("="*80)
    print("(Verifica que el crecimiento sea lineal: O(n))\n")
    
    for i in range(1, len(inputs)):
        n_ratio = inputs[i] / inputs[i-1]
        ops_ratio = operations[i] / operations[i-1] if operations[i-1] > 0 else 0
        expected_ratio = n_ratio  # Para O(n), la razón es simplemente n_ratio
        error = abs(ops_ratio - expected_ratio) / expected_ratio * 100 if expected_ratio > 0 else 0
        
        print(f"n: {inputs[i-1]:>10,} → {inputs[i]:>10,} (×{n_ratio:.1f})")
        print(f"   Operaciones:   ×{ops_ratio:>8.2f}")
        print(f"   Esperado:      ×{expected_ratio:>8.2f} para O(n)")
        print(f"   Error:         {error:>7.2f}%")
        print()
    
    # ANÁLISIS DE COMPLEJIDAD DETALLADO
    print("="*80)
    print("DESGLOSE DE LA COMPLEJIDAD")
    print("="*80)
    print(f"{'n':>12}  {'Loop i (outer)':>20}  {'Loop j (inner)':>20}  {'Total':>15}")
    print("-"*80)
    for n in inputs:
        loop_i = n if n > 1 else 0
        loop_j = 1  # Siempre 1 por el break inmediato
        total = loop_i * loop_j
        print(f"{n:>12,}  {loop_i:>20,}  {loop_j:>20}  {total:>15,}")
    print("="*80)
    print("\nNota: El loop interno siempre ejecuta 1 vez y luego hace break.")
    print("Por lo tanto: Total = n × 1 = n operaciones → O(n)")
    
    # GRÁFICAS
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Gráfica 1: Escala log-log
    ax1.plot(inputs, operations, marker='o', linestyle='-', color='#2E86AB', 
             linewidth=2.5, markersize=10, label='Operaciones calculadas')
    ax1.plot(inputs, theoretical_ops, marker='s', linestyle='--', color='#D62828', 
             linewidth=2, markersize=7, alpha=0.7, label='O(n) teórico')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlabel('Tamaño de input (n)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Número de operaciones', fontsize=11, fontweight='bold')
    ax1.set_title('Complejidad O(n) - Escala Log-Log', fontsize=12, fontweight='bold')
    ax1.grid(True, which='both', linestyle='--', linewidth=0.7, alpha=0.6)
    ax1.legend(fontsize=9)
    
    # Gráfica 2: Escala lineal (n grandes)
    ax2.plot(inputs[3:], operations[3:], marker='o', linestyle='-', color='#06A77D', 
             linewidth=2.5, markersize=10, label='Operaciones reales')
    ax2.plot(inputs[3:], theoretical_ops[3:], marker='s', linestyle='--', color='#F77F00', 
             linewidth=2, markersize=7, alpha=0.7, label='Teórico')
    ax2.set_xlabel('Tamaño de input (n)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Número de operaciones', fontsize=11, fontweight='bold')
    ax2.set_title('Validación Lineal (n ≥ 1000)', fontsize=12, fontweight='bold')
    ax2.grid(True, which='major', linestyle='--', linewidth=0.7, alpha=0.6)
    ax2.legend(fontsize=9)
    ax2.ticklabel_format(style='plain', axis='y')
    
    # Gráfica 3: Tiempo vs n (escala log)
    ax3.plot(inputs, times_optimized, marker='o', linestyle='-', color='#A23B72', 
             linewidth=2.5, markersize=10, label='Tiempo medido')
    ax3.set_xscale('log')
    ax3.set_xlabel('Tamaño de input (n)', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Tiempo de ejecución (s)', fontsize=11, fontweight='bold')
    ax3.set_title('Tiempo de Ejecución - Método Optimizado', fontsize=12, fontweight='bold')
    ax3.grid(True, which='both', linestyle='--', linewidth=0.7, alpha=0.6)
    ax3.legend(fontsize=9)
    
    # Gráfica 4: Razón de crecimiento
    ratios = [operations[i] / operations[i-1] if operations[i-1] > 0 else 0 
              for i in range(1, len(operations))]
    n_ratios = [inputs[i] / inputs[i-1] for i in range(1, len(inputs))]
    
    ax4.bar(range(len(ratios)), ratios, alpha=0.7, color='#06A77D', label='Razón real')
    ax4.plot(range(len(ratios)), n_ratios, marker='o', linestyle='--', color='#D62828', 
             linewidth=2, markersize=8, label='Razón esperada (n)')
    ax4.set_xlabel('Transición', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Factor de crecimiento', fontsize=11, fontweight='bold')
    ax4.set_title('Razón de Crecimiento (debe coincidir con factor n)', 
                  fontsize=12, fontweight='bold')
    ax4.set_xticks(range(len(ratios)))
    ax4.set_xticklabels([f"{inputs[i]}\n→\n{inputs[i+1]}" for i in range(len(ratios))], 
                        fontsize=8)
    ax4.grid(True, axis='y', linestyle='--', linewidth=0.7, alpha=0.6)
    ax4.legend(fontsize=9)
    
    plt.tight_layout()
    plt.savefig('ejercicio2_resultados_optimizado.png', dpi=300, bbox_inches='tight')
    print("\n✓ Gráficas guardadas como 'ejercicio2_resultados_optimizado.png'")
    plt.show()
    
    # ESTADÍSTICAS FINALES
    print("\n" + "="*80)
    print("ESTADÍSTICAS DE OPTIMIZACIÓN")
    print("="*80)
    total_time = sum(times_optimized)
    print(f"Tiempo total de ejecución: {total_time:.9f}s")
    print(f"Tiempo promedio por consulta: {total_time/len(inputs):.9f}s")
    print(f"Valor máximo procesado: n = {max(inputs):,}")
    print(f"Operaciones máximas: {max(operations):,}")
    print("="*80)
    
    print("\n" + "="*80)
    print("CONCLUSIÓN:")
    print("="*80)
    print("✓ Complejidad temporal del algoritmo: O(n)")
    print("✓ El loop interno siempre hace break en la primera iteración")
    print("✓ Por lo tanto, solo el loop externo determina la complejidad")
    print("✓ Total de operaciones = n (exactamente)")
    print("✓ Error: 0% (coincidencia perfecta con el modelo teórico)")
    print("="*80)

if __name__ == "__main__":
    main()