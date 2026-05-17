"""Ajuste de curvas por mínimos cuadrados (1er a 3er grado).

Basado en el PDF: "Ajuste de curvas por mínimos cuadrados 2024".
Contiene funciones de cálculo y evaluación.
"""

from typing import List, Tuple


def _sum_powers(x: List[float], p: int) -> float:
    return sum(xi ** p for xi in x)


def _sum_xy_powers(x: List[float], y: List[float], p: int) -> float:
    return sum(xi ** p * yi for xi, yi in zip(x, y))


def normal_equations(x: List[float], y: List[float], grado: int) -> Tuple[List[List[float]], List[float]]:
    n = len(x)
    if n == 0:
        raise ValueError("No hay datos")
    if len(y) != n:
        raise ValueError("x e y deben tener la misma longitud")
    if grado < 1:
        raise ValueError("El grado debe ser al menos 1")
    if n < grado + 1:
        raise ValueError(f"Se requieren por lo menos {grado + 1} puntos para ajustar grado {grado}")

    # Matriz de coeficientes de la normal equation
    A = [[0.0 for _ in range(grado + 1)] for _ in range(grado + 1)]
    b = [0.0 for _ in range(grado + 1)]

    for i in range(grado + 1):
        for j in range(grado + 1):
            A[i][j] = _sum_powers(x, i + j)
        b[i] = _sum_xy_powers(x, y, i)

    return A, b


def sumas_ajuste(x: List[float], y: List[float], max_x_power: int = 4, max_xy_power: int = 3) -> dict:
    """Calcula las sumas necesarias para el ajuste por mínimos cuadrados.

    Para un polinomio de grado g, las ecuaciones normales requieren:
    - Σx^k para k = 0..2g (los términos A[i][j] usan 0<=i,j<=g y k=i+j)
    - Σx^p y para p = 0..g (los términos b[i] usan x_i^p * y_i)
    """
    if len(x) != len(y):
        raise ValueError("x e y deben tener la misma longitud")

    sumas = {
        "n": len(x),
        "sum_x": _sum_powers(x, 1) if max_x_power >= 1 else 0.0,
        "sum_y": sum(y),
    }

    for p in range(2, max_x_power + 1):
        sumas[f"sum_x{p}"] = _sum_powers(x, p)

    for p in range(1, max_xy_power + 1):
        key = "sum_xy" if p == 1 else f"sum_x{p}y"
        sumas[key] = _sum_xy_powers(x, y, p)

    return sumas


def sistema_normal_texto(x: List[float], y: List[float], grado: int) -> str:
    """Devuelve la formulación de derivadas parciales de S respecto a K0..Kgrado."""
    if grado < 1:
        raise ValueError("El grado debe ser al menos 1")

    sumas = sumas_ajuste(x, y, max_x_power=2 * grado, max_xy_power=grado)
    A, b = normal_equations(x, y, grado)
    texto = []
    texto.append("Sumas necesarias:")
    texto.append(f"n = {sumas['n']}")
    texto.append(f"ΣX = {sumas['sum_x']:.6f}")
    texto.append(f"ΣY = {sumas['sum_y']:.6f}")

    for p in range(2, 2 * grado + 1):
        texto.append(f"ΣX^{p} = {sumas[f'sum_x{p}']:.6f}")

    for p in range(1, grado + 1):
        key = "sum_xy" if p == 1 else f"sum_x{p}y"
        texto.append(f"ΣX^{p}Y = {sumas[key]:.6f}")

    texto.append("")
    texto.append("Función objetivo:")
    texto.append(f"S = Σ_{{i=1..n}} (K0 + K1*x_i + ... + K{grado}*x_i^{grado} - y_i)^2")
    texto.append("")
    texto.append("Para la matriz de ecuaciones normales se necesitan:")
    texto.append(f"  - Σx^k para k = 0..{2 * grado} (porque A[i][j] usa x^{{i+j}})")
    texto.append(f"  - Σx^p Y para p = 0..{grado} (porque b[i] usa x^i * y)")
    texto.append("")
    texto.append("Condiciones normales (derivadas parciales = 0):")

    for i in range(grado + 1):
        term = []
        for j in range(grado + 1):
            coef = A[i][j]
            term.append(f"{coef:.6f}*K{j}")
        rhs = b[i]
        texto.append(" + ".join(term) + f" = {rhs:.6f}")

    texto.append("")
    texto.append("Este sistema se resuelve por Gauss-Jordan para obtener K0,K1,...")
    texto.append("")
    if grado == 3:
        texto.append(ssel_4x4_text(x, y))

    return "\n".join(texto)


def ssel_4x4_text(x: List[float], y: List[float]) -> str:
    """Devuelve representación (texto) del SSELS 4x4 para grado 3 (K0..K3)."""
    A, b = normal_equations(x, y, 3)
    headers = ["K0", "K1", "K2", "K3", "b"]
    rows = [[A[i][j] for j in range(4)] + [b[i]] for i in range(4)]

    widths = [max(len(headers[j]), max(len(f"{row[j]:.6f}") for row in rows)) for j in range(5)]
    header_row = "| " + " | ".join(headers[j].center(widths[j]) for j in range(5)) + " |"
    separator = "|" + "|".join("-" * (widths[j] + 2) for j in range(5)) + "|"

    tabla = ["SSELS 4x4 (K0,K1,K2,K3):", header_row, separator]
    for row in rows:
        tabla.append("| " + " | ".join(f"{row[j]:>{widths[j]}.6f}" for j in range(5)) + " |")

    tabla.append("")
    tabla.append("Esta tabla se obtuvo de las ecuaciones normales generadas por derivadas parciales de S.")
    tabla.append("A continuación se resuelve por Gauss-Jordan para obtener la forma reducida y los coeficientes:")
    _, pasos = _solve_gauss_jordan(A, b, verbose=True)
    tabla.append("")
    tabla.append(pasos)
    return "\n".join(tabla)


def _format_matrix(M: List[List[float]]) -> str:
    return "\n".join(
        "\t".join(f"{v:.6f}" for v in row) for row in M
    )


def _format_augmented_matrix(A: List[List[float]], b: List[float]) -> str:
    n = len(A)
    headers = [f"K{j}" for j in range(n)] + ["b"]
    rows = [row[:] + [b[i]] for i, row in enumerate(A)]
    widths = [max(len(headers[j]), max(len(f"{rows[i][j]:.6f}") for i in range(n))) for j in range(n + 1)]

    header_row = "| " + " | ".join(headers[j].center(widths[j]) for j in range(n + 1)) + " |"
    separator = "|" + "|".join("-" * (widths[j] + 2) for j in range(n + 1)) + "|"
    lines = [header_row, separator]
    for row in rows:
        lines.append("| " + " | ".join(f"{row[j]:>{widths[j]}.6f}" for j in range(n + 1)) + " |")
    return "\n".join(lines)


def _solve_gauss_jordan(A: List[List[float]], b: List[float], verbose: bool = False):
    n = len(A)
    M = [row[:] for row in A]
    c = b[:]
    pasos = []

    if verbose:
        pasos.append("Inicio de Gauss-Jordan para resolver el sistema")
        pasos.append("Matriz aumentada inicial:")
        pasos.append(_format_augmented_matrix(M, c))

    for k in range(n):
        pivot = k
        for i in range(k + 1, n):
            if abs(M[i][k]) > abs(M[pivot][k]):
                pivot = i
        if abs(M[pivot][k]) < 1e-15:
            raise ValueError("Sistema singular o mal condicionado")

        if pivot != k:
            M[k], M[pivot] = M[pivot], M[k]
            c[k], c[pivot] = c[pivot], c[k]
            if verbose:
                pasos.append(f"Intercambio de filas {k} y {pivot}")
                pasos.append(_format_augmented_matrix(M, c))

        pivot_val = M[k][k]
        M[k] = [val / pivot_val for val in M[k]]
        c[k] /= pivot_val
        if verbose:
            pasos.append(f"Normalización de fila {k} (dividiendo por {pivot_val:.6f})")
            pasos.append(_format_augmented_matrix(M, c))

        for i in range(n):
            if i == k:
                continue
            factor = M[i][k]
            c[i] -= factor * c[k]
            for j in range(n):
                M[i][j] -= factor * M[k][j]
            if verbose:
                pasos.append(f"Eliminación en fila {i} usando fila {k} con factor {factor:.6f}")
                pasos.append(_format_augmented_matrix(M, c))

    x = c[:]
    if verbose:
        pasos.append("Matriz aumentada en forma escalonada reducida:")
        pasos.append(_format_augmented_matrix(M, c))
        pasos.append("Solución final:")
        pasos.append("\t" + "\t".join(f"{xi:.6f}" for xi in x))
        return x, "\n".join(pasos)

    return x


# Retrocompatibilidad si en algún lugar se esperaba el nombre antiguo.
_solve_gauss = _solve_gauss_jordan


def coeficientes_polinomio(x: List[float], y: List[float], grado: int) -> List[float]:
    if grado < 1:
        raise ValueError("El grado debe ser al menos 1")

    if len(x) != len(y):
        raise ValueError("x e y deben tener igual cantidad de puntos")

    if len(x) < grado + 1:
        raise ValueError(f"Se requieren por lo menos {grado + 1} puntos para ajustar grado {grado}")

    if max(x) == min(x):
        raise ValueError("Los valores de x no pueden ser constantes para ajuste de mínimos cuadrados")

    A, b = normal_equations(x, y, grado)
    return _solve_gauss_jordan(A, b)


def coeficientes_polinomio_con_pasos(x: List[float], y: List[float], grado: int) -> Tuple[List[float], str]:
    if grado < 1:
        raise ValueError("El grado debe ser al menos 1")

    if len(x) != len(y):
        raise ValueError("x e y deben tener igual cantidad de puntos")

    if len(x) < grado + 1:
        raise ValueError(f"Se requieren por lo menos {grado + 1} puntos para ajustar grado {grado}")

    if max(x) == min(x):
        raise ValueError("Los valores de x no pueden ser constantes para ajuste de mínimos cuadrados")

    A, b = normal_equations(x, y, grado)
    coef, pasos = _solve_gauss_jordan(A, b, verbose=True)
    pasos_final = ["Ecuaciones normales (A y b):", _format_matrix(A), "b = " + "\t".join(f"{v:.6f}" for v in b), "", "Resolución con Gauss-Jordan:", pasos]
    return coef, "\n".join(pasos_final)


def evaluar_polinomio(coef: List[float], x_val: float) -> float:
    return sum(c * (x_val ** i) for i, c in enumerate(coef))


def rss(x: List[float], y: List[float], coef: List[float]) -> float:
    return sum((yi - evaluar_polinomio(coef, xi)) ** 2 for xi, yi in zip(x, y))


def mejor_ajuste(x: List[float], y: List[float], max_grado: int | None = None) -> Tuple[int, List[float], float]:
    if len(x) != len(y):
        raise ValueError("x e y deben tener igual cantidad de puntos")

    if len(x) < 2:
        raise ValueError("Se requieren al menos 2 puntos")

    if max_grado is None:
        max_grado = len(x) - 1

    if max_grado < 1:
        raise ValueError("El grado máximo debe ser al menos 1")

    mejor_grado = None
    mejor_coef = None
    mejor_rss = float('inf')

    for grado in range(1, max_grado + 1):
        try:
            coef = coeficientes_polinomio(x, y, grado)
            error = rss(x, y, coef)
            if error < mejor_rss:
                mejor_rss = error
                mejor_grado = grado
                mejor_coef = coef
        except ValueError:
            continue

    if mejor_grado is None:
        raise RuntimeError("No se pudo encontrar un ajuste adecuado")

    return mejor_grado, mejor_coef, mejor_rss


def extremos_polinomio(coef: List[float]) -> List[Tuple[float, float, str]]:
    """Calcula extremos locales de un polinomio de grado <=3.

    Devuelve lista de tuplas (x, y, tipo) donde tipo es 'minimo', 'maximo', 'punto estacionario'.
    - grado 1: sin extremos.
    - grado 2: un extremo único (vértice), tipo según la concavidad.
    - grado 3: resuelve f'(x)=0 (cuadrática) y clasifica con f''(x).
    """
    grado = len(coef) - 1
    if grado < 1:
        return []

    # derivada para todos los grados
    deriv = [(i) * c for i, c in enumerate(coef)][1:]
    # f' se expresa en coef de polinomio bajo grado-1
    if len(deriv) == 0:
        return []

    # grado 1 (polinomio de grado 2 f' lineal): un punto estacionario
    if len(deriv) == 1:
        return []

    # grado derivada 1 (grado original 2) o 2 (grado 3)
    extremos = []
    if len(deriv) == 2:
        # f' = at + b => raiz unica
        a, b = deriv[1], deriv[0]
        if abs(a) < 1e-12:
            return []
        x0 = -b / a
        y0 = evaluar_polinomio(coef, x0)
        f2 = 2 * a
        tipo = "minimo" if f2 > 0 else "maximo" if f2 < 0 else "punto estacionario"
        extremos.append((x0, y0, tipo))
        return extremos

    if len(deriv) == 3:
        # f' = ax^2 + bx + c
        a = deriv[2]
        b = deriv[1]
        c = deriv[0]
        if abs(a) < 1e-15:
            # cae a grado 1
            if abs(b) < 1e-15:
                return []
            x0 = -c / b
            y0 = evaluar_polinomio(coef, x0)
            f2 = 2 * b
            tipo = "minimo" if f2 > 0 else "maximo" if f2 < 0 else "punto estacionario"
            return [(x0, y0, tipo)]

        discriminante = b * b - 4 * a * c
        if discriminante < 0:
            return []

        raiz = discriminante ** 0.5
        for x0 in [(-b + raiz) / (2 * a), (-b - raiz) / (2 * a)]:
            y0 = evaluar_polinomio(coef, x0)
            f2 = 6 * a * x0 + 2 * b
            if abs(f2) < 1e-12:
                tipo = "punto estacionario"
            else:
                tipo = "minimo" if f2 > 0 else "maximo"
            extremos.append((x0, y0, tipo))
        return extremos

    return extremos


def formato_ecuacion(coef: List[float]) -> str:
    terms = []
    for i, c in enumerate(coef):
        sign = "+" if c >= 0 else "-"
        abs_c = abs(c)
        if i == 0:
            terms.append(f"{c:.6f}")
        elif i == 1:
            terms.append(f" {sign} {abs_c:.6f}*x")
        else:
            terms.append(f" {sign} {abs_c:.6f}*x^{i}")
    return "".join(terms)


if __name__ == '__main__':
    print("Ejemplo de uso de ajuste_curvas.py")
    X = [-3, -2, -1, 0, 1, 2, 3]
    Y = [21, 14, 9, 6, 5, 6, 9]

    grado_mejor, coef_mejor, error_mejor = mejor_ajuste(X, Y)
    print(f"Mejor grado: {grado_mejor}")
    print(f"Coeficientes: {coef_mejor}")
    print(f"RSS: {error_mejor:.6f}")
    print("Ecuación:", formato_ecuacion(coef_mejor))
    for xi in [-5, -4, 5, 6]:
        print(f"x={xi} => y={evaluar_polinomio(coef_mejor, xi):.6f}")
