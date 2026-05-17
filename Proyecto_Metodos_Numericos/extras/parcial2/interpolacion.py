"""Módulo de interpolación lineal para Métodos Numéricos.

Incluye funciones de interpolación directa y regresiva (x -> y, y -> x)
con validaciones de entradas.
"""


def interpolacion_lineal_y(x1, y1, x2, y2, x):
    """Interpolación lineal: calcula y en un x dado.

    Usa la fórmula:
      y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)

    Requiere x1 != x2.
    """
    validar_puntos(x1, y1, x2, y2)

    pendiente = (y2 - y1) / (x2 - x1)
    return y1 + (x - x1) * pendiente


def interpolacion_lineal_x(x1, y1, x2, y2, y):
    """Interpolación lineal inversa: calcula x en un y dado.

    Usa la fórmula:
      x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)

    Requiere y1 != y2.
    """
    validar_puntos(x1, y1, x2, y2)

    pendiente_inversa = (x2 - x1) / (y2 - y1)
    return x1 + (y - y1) * pendiente_inversa


def calcular_pendiente(x1, y1, x2, y2):
    """Calcula la pendiente de la recta que pasa por dos puntos."""
    if x2 == x1:
        raise ValueError("Los puntos no definen pendiente finita (x1 == x2)")

    return (y2 - y1) / (x2 - x1)


def validar_puntos(x1, y1, x2, y2):
    """Valida que los puntos sean válidos y distintivos."""
    if x1 == x2 and y1 == y2:
        raise ValueError("Los puntos no pueden ser idénticos")
    if x1 == x2:
        raise ValueError("x1 y x2 no pueden ser iguales para una función lineal única")
    if y1 == y2:
        raise ValueError("y1 y y2 no pueden ser iguales para una función lineal única")

    return True


def interpolacion_lineal_piecewise_y(points, x):
    """Interpola y para un x dado usando varios puntos ordenados por x.

    - points: lista de tuplas (x, y), al menos 2.
    - x: valor para interpolar.

    Para fuera del rango, extrapola con el segmento extremo correspondiente.
    """
    if len(points) < 2:
        raise ValueError("Se requieren al menos 2 puntos para interpolación")

    # ordenar y validar que no haya x repetidos.
    points_sorted = sorted(points, key=lambda p: p[0])
    xs = [p[0] for p in points_sorted]

    # validar puntos lineales
    for i in range(1, len(xs)):
        if xs[i] == xs[i - 1]:
            raise ValueError(f"Puntos con x repetido no permitidos: {xs[i]}")

    # buscar segmento contenedor
    if x <= xs[0]:
        i0, i1 = 0, 1
    elif x >= xs[-1]:
        i0, i1 = len(xs) - 2, len(xs) - 1
    else:
        i0 = max(i for i in range(len(xs) - 1) if xs[i] <= x)
        i1 = i0 + 1

    x0, y0 = points_sorted[i0]
    x1, y1 = points_sorted[i1]
    return interpolacion_lineal_y(x0, y0, x1, y1, x)


def interpolacion_lineal_piecewise_x(points, y):
    """Interpola x para un y dado usando varios puntos ordenados por y."""
    if len(points) < 2:
        raise ValueError("Se requieren al menos 2 puntos para interpolación")

    points_sorted = sorted(points, key=lambda p: p[1])
    ys = [p[1] for p in points_sorted]

    for i in range(1, len(ys)):
        if ys[i] == ys[i - 1]:
            raise ValueError(f"Puntos con y repetido no permitidos: {ys[i]}")

    if y <= ys[0]:
        i0, i1 = 0, 1
    elif y >= ys[-1]:
        i0, i1 = len(ys) - 2, len(ys) - 1
    else:
        i0 = max(i for i in range(len(ys) - 1) if ys[i] <= y)
        i1 = i0 + 1

    x0, y0 = points_sorted[i0]
    x1, y1 = points_sorted[i1]
    return interpolacion_lineal_x(x0, y0, x1, y1, y)


def interpolacion_lagrange(points, x, verbose=False):
    """Interpola y en x usando polinomio de Lagrange para un conjunto de puntos."""
    if len(points) < 2:
        raise ValueError("Se requieren al menos 2 puntos para interpolación")

    xs = [p[0] for p in points]
    if len(set(xs)) != len(xs):
        dup = [v for v in xs if xs.count(v) > 1]
        raise ValueError(f"Puntos con x repetido no permitidos: {set(dup)}")

    y = 0.0
    steps = []

    for i, (xi, yi) in enumerate(points):
        Li = 1.0
        line_num = []
        line_den = []
        for j, (xj, _) in enumerate(points):
            if i == j:
                continue
            Li *= (x - xj) / (xi - xj)
            line_num.append(f"(x - {xj})")
            line_den.append(f"({xi} - {xj})")

        contrib = yi * Li
        y += contrib

        if verbose:
            steps.append(f"L_{i}(x) = {' * '.join(line_num)} / {' * '.join(line_den)}")
            steps.append(f"L_{i}({x}) = {Li:.6f}")
            steps.append(f"contribución {i}: {yi} * {Li:.6f} = {contrib:.6f}")

    if verbose:
        steps.append(f"Resultado: y({x}) = {y:.6f}")
        return y, "\n".join(steps)

    return y

