X = [
    [1, 2, 3, 1],
    [4, 5, 6, 0],
    [7, 8, 9, -1]
]


Y = list(map(lambda *filas: list(filas), *X))

print(Y)
