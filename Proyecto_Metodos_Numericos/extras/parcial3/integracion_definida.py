"""Métodos numéricos de integración definida.

Incluye reglas del trapecio, punto medio, Simpson 1/3, Simpson 3/8 y Richardson/Romberg.
Guarda gráficos de la función y del área bajo la curva en resources/images.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Callable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

IMAGE_DIR = Path(__file__).resolve().parents[2] / "resources" / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

Function = Callable[[np.ndarray], np.ndarray]


def h_step(a: float, b: float, n: int) -> float:
    """Calcula el ancho de subintervalo h = (b - a) / N."""
    if n <= 0:
        raise ValueError("N debe ser mayor que cero")
    return (b - a) / n


def trapezoidal_rule(f: Function, a: float, b: float, n: int) -> float:
    h = h_step(a, b, n)
    x = np.linspace(a, b, n + 1)
    y = f(x)
    return h * (0.5 * y[0] + y[1:-1].sum() + 0.5 * y[-1])


def trapezoidal_absolute_rule(f: Function, a: float, b: float, n: int) -> float:
    h = h_step(a, b, n)
    x = np.linspace(a, b, n + 1)
    y = np.abs(f(x))
    return h * (0.5 * y[0] + y[1:-1].sum() + 0.5 * y[-1])


def midpoint_rule(f: Function, a: float, b: float, n: int) -> float:
    h = h_step(a, b, n)
    x_mid = a + (np.arange(n) + 0.5) * h
    return h * f(x_mid).sum()


def simpson_one_third(f: Function, a: float, b: float, n: int) -> float:
    if n % 2 != 0:
        raise ValueError("El número de subintervalos N debe ser par para Simpson 1/3")
    h = h_step(a, b, n)
    x = np.linspace(a, b, n + 1)
    y = f(x)
    return h / 3 * (y[0] + y[-1] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum())


def simpson_three_eighths(f: Function, a: float, b: float, n: int) -> float:
    if n % 3 != 0:
        raise ValueError("El número de subintervalos N debe ser múltiplo de 3 para Simpson 3/8")
    h = h_step(a, b, n)
    x = np.linspace(a, b, n + 1)
    y = f(x)
    coeffs = np.ones(n + 1)
    coeffs[1:-1] = 3
    coeffs[3:-1:3] = 2
    coeffs[3::3] = 2
    coeffs[0] = 1
    coeffs[-1] = 1
    return 3 * h / 8 * (coeffs * y).sum()


# ─── Newton-Cotes cerradas ────────────────────────────────────────────────────

NEWTON_COTES_DATA: dict[int, dict] = {
    2: {
        "name": "Regla de Simpson",
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


def newton_cotes_composite_coefficients(N: int, degree: int) -> np.ndarray:
    """Devuelve el array de coeficientes compuestos Newton-Cotes para N subintervalos.

    Aplica la fórmula elemental de grado `degree` en segmentos consecutivos.
    El punto compartido entre dos segmentos acumula las contribuciones de ambos.
    """
    if degree not in NEWTON_COTES_DATA:
        raise ValueError(f"Grado {degree} no soportado. Use 2, 3 o 4.")
    if N % degree != 0:
        raise ValueError(
            f"N={N} debe ser múltiplo de {degree} para Newton-Cotes grado {degree}"
        )
    basic = NEWTON_COTES_DATA[degree]["coefs"]
    comp = np.zeros(N + 1)
    for start in range(0, N, degree):
        for i, c in enumerate(basic):
            comp[start + i] += c
    return comp


def newton_cotes(f: Function, a: float, b: float, N: int, degree: int) -> float:
    """Aplica la fórmula compuesta de Newton-Cotes de grado `degree` sobre [a,b] con N subintervalos."""
    h = h_step(a, b, N)
    comp = newton_cotes_composite_coefficients(N, degree)
    x = np.linspace(a, b, N + 1)
    y = f(x)
    factor = NEWTON_COTES_DATA[degree]["factor"]
    return float(h * factor * np.dot(comp, y))


def richardson_extrapolation(
    f: Function, a: float, b: float, n_base: int, levels: int
) -> tuple[list[list[float]], float]:
    """Aplica la extrapolación de Richardson (tabla de Romberg).

    R[k][0] = Regla del trapecio con n_base × 2^k subintervalos.
    R[k][j] = (4^j · R[k][j-1] − R[k-1][j-1]) / (4^j − 1)   para j ≥ 1, k ≥ j.

    Devuelve (R_tabla, mejor_estimado) donde mejor_estimado = R[levels][levels].
    """
    if levels < 1:
        raise ValueError("El número de niveles debe ser al menos 1")
    size = levels + 1
    R: list[list[float]] = [[0.0] * size for _ in range(size)]
    for k in range(size):
        R[k][0] = trapezoidal_rule(f, a, b, n_base * (2 ** k))
    for j in range(1, size):
        factor = 4 ** j
        for k in range(j, size):
            R[k][j] = (factor * R[k][j - 1] - R[k - 1][j - 1]) / (factor - 1)
    return R, R[levels][levels]


def exact_integral_quad(f: Function, a: float, b: float) -> tuple[float, str]:
    """Calcula la integral más exacta posible.

    Usa scipy.integrate.quad si está disponible; si no, aplica Romberg interno
    con n=1 y 15 niveles (≈32 768 intervalos + extrapolación) como respaldo.
    """
    try:
        from scipy.integrate import quad  # type: ignore
        result, _ = quad(f, a, b)
        return float(result), "scipy.integrate.quad"
    except Exception:
        pass
    # Fallback: Romberg interno con alta resolución
    try:
        R_ref, best = richardson_extrapolation(f, a, b, n_base=1, levels=15)
        return best, "Romberg interno (n=1, 15 niveles ≈ 32768 intervalos)"
    except Exception:
        x_ref = np.linspace(a, b, 1_000_001)
        y_ref = f(x_ref)
        result = float(np.trapz(y_ref, x_ref))
        return result, "trapecio alta resolución (n=1 000 000)"


def reference_integral(f: Function, a: float, b: float) -> float:
    """Genera una referencia numérica con alta resolución para comparar errores.

    Si la función se evalúa totalmente por debajo del eje x en [a, b],
    devuelve el valor absoluto para representar el área positiva.
    """
    x_ref = np.linspace(a, b, 20001)
    y_ref = f(x_ref)
    h_ref = x_ref[1] - x_ref[0]
    integral = np.sum((y_ref[:-1] + y_ref[1:]) * h_ref / 2)
    if np.all(y_ref <= 0):
        return abs(integral)
    return integral


def is_entirely_below_x_axis(f: Function, a: float, b: float, samples: int = 400) -> bool:
    """Devuelve True si f(x) está completamente por debajo del eje x en [a,b]."""
    x = np.linspace(a, b, samples)
    y = f(x)
    return np.all(y <= 0)


def plot_function_and_area(f: Function, a: float, b: float, filename: str, title: str) -> Path:
    x = np.linspace(a, b, 400)
    y = f(x)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, y, label="f(x)", color="#0b5394")
    ax.fill_between(x, y, where=(x >= a) & (x <= b), alpha=0.25, color="#6fa8dc")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title(title)
    ax.legend()
    path = IMAGE_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_trapezoids(f: Function, a: float, b: float, n: int, filename: str) -> Path:
    x = np.linspace(a, b, 400)
    y = f(x)
    x_nodes = np.linspace(a, b, n + 1)
    y_nodes = f(x_nodes)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, y, label="f(x)", color="#2e75b6")
    for i in range(n):
        xs = [x_nodes[i], x_nodes[i], x_nodes[i + 1], x_nodes[i + 1]]
        ys = [0, y_nodes[i], y_nodes[i + 1], 0]
        ax.fill(xs, ys, alpha=0.2, edgecolor="black", facecolor="#ffd966")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title(f"Regla del trapecio con N={n}")
    ax.legend()
    path = IMAGE_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_simpson_approximation(f: Function, a: float, b: float, n: int, filename: str) -> Path:
    x = np.linspace(a, b, 400)
    y = f(x)
    x_nodes = np.linspace(a, b, n + 1)
    y_nodes = f(x_nodes)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, y, label="f(x)", color="#2e75b6")
    for i in range(0, n, 2):
        xs = np.linspace(x_nodes[i], x_nodes[i + 2], 100)
        coeffs = np.polyfit(x_nodes[i:i + 3], y_nodes[i:i + 3], 2)
        ys = np.polyval(coeffs, xs)
        ax.fill_between(xs, ys, alpha=0.2, color="#b6d7a8")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_title(f"Regla de Simpson 1/3 con N={n}")
    ax.legend()
    path = IMAGE_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def plot_richardson_convergence(
    f: Function, a: float, b: float, n_base: int, levels: int, filename: str
) -> Path:
    """Grafica la convergencia de la tabla de Richardson/Romberg."""
    R, _ = richardson_extrapolation(f, a, b, n_base, levels)
    exact, _ = exact_integral_quad(f, a, b)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Subplot 1: valor por diagonal (R[k,k])
    diag_vals = [R[k][k] for k in range(levels + 1)]
    ns = [n_base * (2 ** k) for k in range(levels + 1)]
    axes[0].plot(range(levels + 1), diag_vals, "o-", color="#2e75b6", label="R[k,k]")
    axes[0].axhline(exact, color="#d9534f", linestyle="--", label=f"Exacta ≈ {exact:.6f}")
    axes[0].set_xlabel("Nivel k")
    axes[0].set_ylabel("Valor")
    axes[0].set_title("Convergencia diagonal R[k,k]")
    axes[0].legend()
    axes[0].set_xticks(range(levels + 1))
    axes[0].set_xticklabels([f"k={k}\nN={ns[k]}" for k in range(levels + 1)], fontsize=8)

    # Subplot 2: error de cada R[k,k]
    errors = [abs(R[k][k] - exact) + 1e-16 for k in range(levels + 1)]
    axes[1].semilogy(range(levels + 1), errors, "s-", color="#f0ad4e", label="|Error|")
    axes[1].set_xlabel("Nivel k")
    axes[1].set_ylabel("|Error| (escala log)")
    axes[1].set_title("Error de convergencia (log)")
    axes[1].legend()
    axes[1].set_xticks(range(levels + 1))

    fig.suptitle(f"Richardson/Romberg — N base={n_base}, {levels} niveles", fontsize=12)
    fig.tight_layout()
    path = IMAGE_DIR / filename
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def validate_method(name: str, approx: float, exact: float, tol: float) -> str:
    error = abs(approx - exact)
    return (
        f"{name}: aproximación={approx:.10f}, exacta={exact:.10f}, "
        f"error={error:.10f}, tol={tol}, {'OK' if error <= tol else 'NO OK'}"
    )


def example_function(x: np.ndarray) -> np.ndarray:
    return np.sin(x) + 0.3 * x**2


def polynomial_example(x: np.ndarray) -> np.ndarray:
    return x**2 - 2 * x + 1


def main() -> None:
    a, b = 0.0, 3.0
    n = 12
    tol = 1e-4

    exact_polynomial = 3.0
    approx_trap = trapezoidal_rule(polynomial_example, a, b, n)
    approx_mid = midpoint_rule(polynomial_example, a, b, n)
    approx_simp = simpson_one_third(polynomial_example, a, b, n)

    print(validate_method("Trapecio", approx_trap, exact_polynomial, tol))
    print(validate_method("Punto medio", approx_mid, exact_polynomial, tol))
    print(validate_method("Simpson 1/3", approx_simp, exact_polynomial, tol))

    reference = reference_integral(example_function, a, b)
    print(f"Referencia numérica de ejemplo: {reference:.10f}")

    exact_val, exact_src = exact_integral_quad(example_function, a, b)
    print(f"Integral exacta ({exact_src}): {exact_val:.15f}")

    R, best = richardson_extrapolation(example_function, a, b, n_base=4, levels=4)
    print(f"Richardson/Romberg (N=4, 4 niveles): {best:.15f}")

    plot_function_and_area(example_function, a, b, "integracion_area.png", "Área bajo f(x)")
    plot_trapezoids(example_function, a, b, n, "integracion_trapecio.png")
    plot_simpson_approximation(example_function, a, b, n, "integracion_simpson.png")
    plot_richardson_convergence(example_function, a, b, 4, 4, "integracion_richardson.png")

    print(f"Imágenes guardadas en: {IMAGE_DIR}")


if __name__ == "__main__":
    main()
