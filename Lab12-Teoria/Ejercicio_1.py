D = [
    {'make': 'Nokia',  'model': 216, 'color': 'Black'},
    {'make': 'Apple',  'model':   2, 'color': 'Silver'},
    {'make': 'Huawei', 'model':  50, 'color': 'Gold'},
    {'make': 'Samsung','model':   7, 'color': 'Blue'}
]

def ordenar_por(lista, clave, descendente=False):
    # Si alguna entrada no tiene la clave, se manda al final
    return sorted(lista, key=lambda d: d.get(clave, float('inf')), reverse=descendente)

# Ejemplo: ordenar por 'model' ascendente
res = ordenar_por(D, 'model')
print(res)