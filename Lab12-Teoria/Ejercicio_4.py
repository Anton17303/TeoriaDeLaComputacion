colores = ['rojo', 'verde', 'azul', 'amarillo', 'gris', 'blanco', 'negro']

borrar = ['amarillo', 'café', 'blanco']

resultado = list(filter(lambda c: c not in borrar, colores))

print(resultado)