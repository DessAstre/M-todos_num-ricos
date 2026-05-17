"""Métodos numéricos de integración definida (versión Python puro).

Incluye la regla del trapecio, Simpson 1/3, Simpson 3/8, regla de los 2/45
(Newton-Cotes grado 4) y la extrapolación de Richardson/Romberg.

Esta versión NO depende de numpy ni de matplotlib: ejecuta los algoritmos
sobre listas y devuelve flotantes nativos. Las funciones se invocan
escalar por escalar — es decir, `f(x_i)` debe aceptar un float.
"""

from __future__ import annotations

from typing import Callable, List, Tuple

Function = Callable[[float], float]


# ---------------------------------------------------------------------------
#  Utilidades
# ---------------------------------------------------------------------------

def h_step(a: float, b: float, n: int) -> float:
    """Ancho de subintervalo h = (b − a) / n."""
    if n <= 0:
        raise ValueError("N debe ser mayor que cero")
    return (b - a) / n


def _nodes(a: float, b: float, n: int) -> List[float]:
    """Genera n+1 nodos equiespaciados en [a, b]."""
    h = h_step(a, b, n)
    return [a + i * h for i in range(n + 1)]


def _evaluate(f: Function, nodes: List[float]) -> List[float]:
    """Evalúa f en cada nodo y devuelve la lista de imágenes (en float)."""
    return [float(f(x)) for x in nodes]


# ---------------------------------------------------------------------------
#  Reglas básicas
# ---------------------------------------------------------------------------

def trapezoidal_rule(f: Function, a: float, b: float, n: int) -> float:
    """Regla compuesta del trapecio."""
    h = h_step(a, b, n)
    xs = _nodes(a, b, n)
    ys = _evaluate(f, xs)
    interior = sum(ys[1:-1])
    return h * (0.5 * ys[0] + interior + 0.5 * ys[-1])


def simpson_one_third(f: Function, a: float, b: float, n: int) -> float:
    """Simpson 1/3 compuesta (N debe ser múltiplo de 2)."""
    if n % 2 != 0:
        raise ValueError("El número de subintervalos N debe ser par para Simpson 1/3")
    h = h_step(a, b, n)
    ys = _evaluate(f, _nodes(a, b, n))
    impares = sum(ys[i] for i in range(1, n, 2))
    pares = sum(ys[i] for i in range(2, n, 2))
    return (h / 3.0) * (ys[0] + 4 * impares + 2 * pares + ys[-1])


def simpson_three_eighths(f: Function, a: float, b: float, n: int) -> float:
    """Simpson 3/8 compuesta (N debe ser múltiplo de 3)."""
    if n % 3 != 0:
        raise ValueError("El número de subintervalos N debe ser múltiplo de 3 para Simpson 3/8")
    h = h_step(a, b, n)
    ys = _evaluate(f, _nodes(a, b, n))

    coef = [1] + [3] * (n - 1) + [1]  # base
    # Las posiciones múltiplos de 3 (interiores) tienen coeficiente 2.
    for i in range(3, n, 3):
        coef[i] = 2

    s = sum(c * y for c, y in zip(coef, ys))
    return (3.0 * h / 8.0) * s


# ---------------------------------------------------------------------------
#  Newton-Cotes compuesta (grados 2, 3, 4)
# ---------------------------------------------------------------------------

NEWTON_COTES_DATA = {
    2: {
        "name": "Regla de Simpson 1/3",
        "coefs": [1, 4, 1],
        "factor": 1 / 3,
        "factor_str": "h/3",
        "req": 2,
        "restriction": "N par (múltiplo de 2)",
        "error_order": "O(h⁵) por segmento  →  O(h⁴) global",
    },
    3: {
        "name": "Regla de los 3/8",
        "coefs": [1, 3, 3, 1],
        "factor": 3 / 8,
        "factor_str": "3h/8",
        "req": 3,
        "restriction": "N múltiplo de 3",
        "error_order": "O(h⁵) por segmento  →  O(h⁴) global",
    },
    4: {
        "name": "Regla de los 2/45 (Boole)",
        "coefs": [7, 32, 12, 32, 7],
        "factor": 2 / 45,
        "factor_str": "2h/45",
        "req": 4,
        "restriction": "N múltiplo de 4",
        "error_order": "O(h⁷) por segmento  →  O(h⁶) global",
    },
}


def newton_cotes_composite_coefficients(N: int, degree: int) -> List[float]:
    """Coeficientes compuestos Newton-Cotes para N subintervalos."""
    if degree not in NEWTON_COTES_DATA:
        raise ValueError(f"Grado {degree} no soportado. Use 2, 3 o 4.")
    if N % degree != 0:
        raise ValueError(
            f"N={N} debe ser múltiplo de {degree} para Newton-Cotes grado {degree}"
        )
    basicos = NEWTON_COTES_DATA[degree]["coefs"]
    comp = [0.0] * (N + 1)
    for inicio in range(0, N, degree):
        for i, c in enumerate(basicos):
            comp[inicio + i] += c
    return comp


def newton_cotes(f: Function, a: float, b: float, N: int, degree: int) -> float:
    """Aplica la fórmula compuesta de Newton-Cotes de grado `degree`."""
    h = h_step(a, b, N)
    comp = newton_cotes_composite_coefficients(N, degree)
    ys = _evaluate(f, _nodes(a, b, N))
    factor = NEWTON_COTES_DATA[degree]["factor"]
    return float(h * factor * sum(c * y for c, y in zip(comp, ys)))


# ---------------------------------------------------------------------------
#  Extrapolación de Richardson (tabla de Romberg)
# ---------------------------------------------------------------------------

def richardson_extrapolation(
    f: Function, a: float, b: float, n_base: int, levels: int,
) -> Tuple[List[List[float]], float]:
    """Extrapolación de Richardson sobre la regla del trapecio.

    R[k][0] = trapecio con n_base · 2^k subintervalos.
    R[k][j] = (4^j · R[k][j-1] − R[k-1][j-1]) / (4^j − 1)   para j ≥ 1, k ≥ j.

    Devuelve (tabla, mejor_estimado).
    """
    if levels < 1:
        raise ValueError("El número de niveles debe ser al menos 1")
    size = levels + 1
    R: List[List[float]] = [[0.0] * size for _ in range(size)]
    for k in range(size):
        R[k][0] = trapezoidal_rule(f, a, b, n_base * (2 ** k))
    for j in range(1, size):
        factor = 4 ** j
        for k in range(j, size):
            R[k][j] = (factor * R[k][j - 1] - R[k - 1][j - 1]) / (factor - 1)
    return R, R[levels][levels]
