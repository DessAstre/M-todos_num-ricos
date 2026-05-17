"""Interfaz Tkinter para métodos de integración definida."""

import math
import re
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from typing import Optional

import numpy as np

try:
    from PIL import Image as _PILImage, ImageTk as _ImageTk
except ImportError:
    _PILImage = None
    _ImageTk = None

try:
    from Parcial3.integracion_definida import (
        h_step,
        trapezoidal_rule,
        trapezoidal_absolute_rule,
        midpoint_rule,
        simpson_one_third,
        simpson_three_eighths,
        richardson_extrapolation,
        exact_integral_quad,
        NEWTON_COTES_DATA,
        newton_cotes_composite_coefficients,
        newton_cotes,
        plot_function_and_area,
        plot_trapezoids,
        plot_simpson_approximation,
        plot_richardson_convergence,
        reference_integral,
        is_entirely_below_x_axis,
    )
except ImportError:
    from integracion_definida import (
        h_step,
        trapezoidal_rule,
        trapezoidal_absolute_rule,
        midpoint_rule,
        simpson_one_third,
        simpson_three_eighths,
        richardson_extrapolation,
        exact_integral_quad,
        NEWTON_COTES_DATA,
        newton_cotes_composite_coefficients,
        newton_cotes,
        plot_function_and_area,
        plot_trapezoids,
        plot_simpson_approximation,
        plot_richardson_convergence,
        reference_integral,
        is_entirely_below_x_axis,
    )


# ─── Helpers de expresión ────────────────────────────────────────────────────

def _clear_frame(container: tk.Widget) -> None:
    for widget in container.winfo_children():
        widget.destroy()


def _normalize_expression(expr: str) -> str:
    expr = expr.strip()
    expr = expr.replace("^", "**")
    function_names = "sin|cos|tan|csc|sec|cot|exp|log10|log|ln|sqrt|abs"
    expr = re.sub(rf"\b({function_names})\s*\(\s*([^)]+?)\s*\)", r"\1(\2)", expr)
    expr = re.sub(rf"\b({function_names})\s+([A-Za-z0-9_.*]+)", r"\1(\2)", expr)
    expr = re.sub(r"(?<=[0-9])\s*(?=[A-Za-z(])", "*", expr)
    expr = re.sub(r"(?<=[A-Za-z_])\s*(?=[0-9])", "*", expr)
    expr = re.sub(r"(?<=\))\s*(?=[A-Za-z(0-9])", "*", expr)
    expr = re.sub(r"(?<=[A-Za-z0-9_])\s+(?=[A-Za-z(])", "*", expr)
    return expr


def _safe_eval_function(expr: str):
    expr = expr.strip()
    if not expr:
        raise ValueError("Expresión vacía")
    expr = _normalize_expression(expr)
    safe_globals = {
        "__builtins__": {},
        "math": math,
        "np": __import__("numpy"),
        "sin": __import__("numpy").sin,
        "cos": __import__("numpy").cos,
        "tan": __import__("numpy").tan,
        "csc": lambda x: 1 / __import__("numpy").sin(x),
        "sec": lambda x: 1 / __import__("numpy").cos(x),
        "cot": lambda x: 1 / __import__("numpy").tan(x),
        "exp": __import__("numpy").exp,
        "log": __import__("numpy").log10,   # log base 10 (convención de cálculo numérico)
        "log10": __import__("numpy").log10,
        "ln": __import__("numpy").log,      # logaritmo natural explícito
        "sqrt": __import__("numpy").sqrt,
        "abs": __import__("numpy").abs,
        "pi": math.pi,
        "e": math.e,
    }

    def f(x):
        return eval(expr, safe_globals, {"x": x})

    return f


def _check_function_domain(f, a: float, b: float) -> tuple[bool, str]:
    xs = np.linspace(a, b, 400)
    with np.errstate(all="ignore", divide="ignore", invalid="ignore", over="ignore"):
        ys = f(xs)
    if np.iscomplexobj(ys):
        return False, "f(x) devuelve valores complejos en el intervalo."
    if not np.all(np.isfinite(ys)):
        return False, "f(x) no es finita en todo [a,b] (log/raiz/division)."
    return True, ""


# ─── Formateo de números ──────────────────────────────────────────────────────

def _truncate_val(value: float, digits: int) -> float:
    """Trunca (hacia cero) value a `digits` decimales."""
    if not math.isfinite(value):
        return value
    factor = 10 ** digits
    return math.trunc(value * factor) / factor


def _format_value(value: float, mode: str, digits: int = 4) -> str:
    if mode == "Truncamiento":
        t = _truncate_val(value, digits)
        return f"{t:.{digits}f}"
    return f"{value:.10f}"


def _format_by_mode(value: float, mode: str, digits: int = 4) -> str:
    return _format_value(value, mode, digits)


def _format_optional(value: Optional[float], mode: str, digits: int = 4, default: str = "N/A") -> str:
    if value is None:
        return default
    if isinstance(value, float) and not math.isfinite(value):
        return default
    return _format_value(value, mode, digits)


# ─── Tablas de desarrollo ─────────────────────────────────────────────────────

def _build_table_lines(xs, ys, mode: str, digits: int = 4) -> list[str]:
    lines = ["Tabla de desarrollo:", "      x_i      |      f(x_i)", "-----------------------------"]
    for x_i, y_i in zip(xs, ys):
        lines.append(f"{_format_by_mode(x_i, mode, digits):>12} | {_format_by_mode(y_i, mode, digits):>12}")
    return lines


def _build_spreadsheet_lines(xs, ys, mode: str, digits: int = 4, title: str = "Hoja de cálculo:") -> list[str]:
    lines = [title, "      x      |      f(x)", "-----------------------------"]
    for x_i, y_i in zip(xs, ys):
        lines.append(f"{_format_by_mode(x_i, mode, digits):>12} | {_format_by_mode(y_i, mode, digits):>12}")
    return lines


def _build_method_spreadsheet(f, a, b, N, method: str, mode: str, digits: int = 4) -> list[str]:
    h = h_step(a, b, N)
    if method == "Punto Medio":
        xs = a + (np.arange(N) + 0.5) * h
        title = f"Hoja de cálculo de {method} (x = a + (i+1/2)h):"
    else:
        xs = np.linspace(a, b, N + 1)
        title = f"Hoja de cálculo de {method} (x = a + i h):"
    ys = f(xs)
    return _build_spreadsheet_lines(xs, ys, mode, digits, title)


def _build_md_style_table(f, a, b, N, mode: str, digits: int = 4) -> list[str]:
    xs    = np.linspace(a, b, N + 1)
    ys    = f(xs)
    ys_abs = np.abs(ys)
    h     = h_step(a, b, N)

    # ── Coeficientes compuestos ───────────────────────────────────────────────
    trap_coefs = np.ones(N + 1); trap_coefs[1:-1] = 2
    simp_coefs = newton_cotes_composite_coefficients(N, 2) if N % 2 == 0 else None
    r38_coefs  = newton_cotes_composite_coefficients(N, 3) if N % 3 == 0 else None
    r245_coefs = newton_cotes_composite_coefficients(N, 4) if N % 4 == 0 else None

    # ── Anchos de columna ─────────────────────────────────────────────────────
    w_i = 4                     # índice i
    w_v = max(digits + 6, 12)   # valores numéricos (x, f(x))
    w_c = 5                     # coeficiente (×1 … ×32)

    # Encabezados de las 4 columnas de métodos
    _MCOLS = [
        ("Trap",  trap_coefs, "h/2",  0.5,  "—"),
        ("Simp",  simp_coefs, "h/3",  1/3,  f"N no múltiplo de 2"),
        ("3/8",   r38_coefs,  "3/8",  3/8,  f"N no múltiplo de 3"),
        ("2/45",  r245_coefs, "2/45", 2/45, f"N no múltiplo de 4"),
    ]
    _MFULL = ["Trapecio", "Simpson 1/3", "Regla 3/8", "Regla 2/45"]

    # Ancho de cada columna de sumatoria/resultado (nombre completo + margen)
    w_s = max(digits + 8, 16)

    def _cfmt(coefs, i):
        """Celda de coeficiente: '×2', '×4', '—' …"""
        if coefs is None:
            return f"{'—':^{w_c}}"
        return f"{'×'+str(int(coefs[i])):^{w_c}}"

    def _vfmt(v):
        """Valor numérico alineado a la derecha, o 'No aplica'."""
        if v is None:
            return "No aplica"
        return _format_by_mode(v, mode, digits)

    # ── Separadores ───────────────────────────────────────────────────────────
    row_width = 2 + w_i + 3 + w_v + 3 + w_v + (3 + w_c) * 4 + 2
    sep_dbl = "  " + "═" * row_width
    sep_sng = "  " + "─" * row_width
    sep_mid = "  " + "┄" * row_width

    # ── Título y leyenda ──────────────────────────────────────────────────────
    lines: list[str] = [
        sep_dbl,
        f"  HOJA DE CÁLCULO  —  N = {N}   h = {_format_by_mode(h, mode, digits)}   [{a}, {b}]",
        sep_dbl,
        f"  Restricciones:  Trap = sin restricción │ Simp N%2=0 │ 3/8 N%3=0 │ 2/45 N%4=0",
        sep_sng,
    ]

    # ── Encabezado de la tabla ────────────────────────────────────────────────
    hdr = (
        f"  {'i':^{w_i}} │ {'xᵢ':^{w_v}} │ {'f(xᵢ)':^{w_v}}"
        + "".join(f" │ {h_:^{w_c}}" for h_, *_ in _MCOLS)
    )
    lines += [hdr, sep_sng]

    # ── Filas de datos ────────────────────────────────────────────────────────
    for i, (xi, yi) in enumerate(zip(xs, ys)):
        row = (
            f"  {i:^{w_i}} │ {_format_by_mode(xi, mode, digits):>{w_v}}"
            f" │ {_format_by_mode(yi, mode, digits):>{w_v}}"
            + "".join(f" │ {_cfmt(c, i)}" for _, c, *_ in _MCOLS)
        )
        lines.append(row)

    # ── Pie: sumatorias e integrales ──────────────────────────────────────────
    lines.append(sep_sng)

    # Pre-calcular valores para cada método
    _vals: dict = {}
    for short, coefs, f_str, factor, _ in _MCOLS:
        if coefs is None:
            _vals[short] = dict(si=None, sa=None, intg=None, area=None, f_str=f_str)
        else:
            si   = abs(float(np.dot(coefs, ys)))
            sa   = abs(float(np.dot(coefs, ys_abs)))
            intg = abs(h * factor * si)
            area = abs(h * factor * sa)
            _vals[short] = dict(si=si, sa=sa, intg=intg, area=area, f_str=f_str)

    _shorts = [s for s, *_ in _MCOLS]

    def _summary_row(label, key):
        cells = "  ".join(f"{_vfmt(_vals[s].get(key)):>{w_s}}" for s in _shorts)
        return f"  {label:<14}  {cells}"

    # Nombres completos como encabezado del bloque de sumatorias
    lines.append(
        f"  {'':14}  " + "  ".join(f"{n:>{w_s}}" for n in _MFULL)
    )
    lines.append("  " + "─" * (14 + 2 + (w_s + 2) * 4))
    lines.append(_summary_row("Σ Integral",  "si"))
    lines.append(_summary_row("Σ Área",      "sa"))
    lines.append("  " + "─" * (14 + 2 + (w_s + 2) * 4))
    lines.append(
        f"  {'Factor':<14}  " + "  ".join(f"{_vals[s]['f_str']:>{w_s}}" for s in _shorts)
    )
    lines.append(_summary_row("Integral",    "intg"))
    lines.append(_summary_row("Área",        "area"))
    lines.append(sep_dbl)

    return lines


# ─── Desarrollo paso a paso por método ───────────────────────────────────────

def _development_trapezoid(f, a, b, N, mode, digits=4):
    h = h_step(a, b, N)
    x = np.linspace(a, b, N + 1)
    y = f(x)
    fa, fb = y[0], y[-1]
    interior_sum = y[1:-1].sum()
    weighted_sum = fa + 2 * interior_sum + fb   # suma con factores ×1/×2/×1
    approx = (h / 2) * weighted_sum

    # Tabla con coeficientes explícitos (notación del método)
    table_lines = [
        "Tabla de desarrollo:",
        f"  {'x_i':>14}  {'f(x_i)':>14}  Coef.",
        "  " + "─" * 46,
    ]
    for i, (xi, yi) in enumerate(zip(x, y)):
        if i == 0 or i == N:
            coef = "×1"
        else:
            coef = "×2"
        table_lines.append(
            f"  {_format_by_mode(xi, mode, digits):>14}  {_format_by_mode(yi, mode, digits):>14}  {coef}"
        )
    table_lines.append(f"  {'Factor':>14}  {'h/2':>14}")
    table_lines.append(f"  {'h/2':>14}  {_format_by_mode(h / 2, mode, digits):>14}")
    table_lines.append(f"  {'Restricción':>14}  {'Sin restricción':>14}")

    double_interior = 2 * interior_sum
    lines = [
        f"Método: Trapecio,  N = {N}",
        f"h = (b - a) / N = ({b} - {a}) / {N} = {_format_by_mode(h, mode, digits)}",
        f"Fórmula: It = (h/2) · (f(a) + 2·Σf(xᵢ) + f(b))",
        f"         It = (h/2) · (f(a) + 2·[f(x1)+...+f(x_{{N-1}})] + f(b))",
        f"Equivalente a: It = h · (½·f(a) + Σf(xᵢ) + ½·f(b))",
    ]
    lines.extend(table_lines)
    lines.extend([
        "",
        f"Suma ponderada = f(a) + 2·Σf(xᵢ) + f(b)",
        f"              = {_format_by_mode(fa, mode, digits)} + 2·{_format_by_mode(interior_sum, mode, digits)} + {_format_by_mode(fb, mode, digits)}",
        f"              = {_format_by_mode(fa, mode, digits)} + {_format_by_mode(double_interior, mode, digits)} + {_format_by_mode(fb, mode, digits)}",
        f"              = {_format_by_mode(weighted_sum, mode, digits)}",
        f"It = (h/2) · Σpond = ({_format_by_mode(h, mode, digits)}/2) · {_format_by_mode(weighted_sum, mode, digits)}",
        f"It = {_format_by_mode(h / 2, mode, digits)} · {_format_by_mode(weighted_sum, mode, digits)}",
        f"It = {_format_by_mode(approx, mode, digits)}",
    ])
    return lines, approx


def _development_midpoint(f, a, b, N, mode, digits=4):
    h = h_step(a, b, N)
    x_mid = a + (np.arange(N) + 0.5) * h
    y_mid = f(x_mid)
    approx = h * y_mid.sum()
    lines = [
        "Método: Punto Medio",
        f"h = {_format_by_mode(h, mode, digits)}",
        f"Incremento h = {h:.10f}",
        f"Fórmula: A ≈ h · Σ f(a + (i + 1/2)h)",
    ]
    lines.extend(_build_table_lines(x_mid, y_mid, mode, digits))
    lines.extend([
        f"Área encontrada = {_format_by_mode(approx, mode, digits)}",
    ])
    return lines, approx


def _development_simpson_one_third(f, a, b, N, mode, digits=4):
    h = h_step(a, b, N)
    x = np.linspace(a, b, N + 1)
    y = f(x)
    odd_sum = y[1:-1:2].sum()
    even_sum = y[2:-1:2].sum()
    approx = h / 3 * (y[0] + y[-1] + 4 * odd_sum + 2 * even_sum)
    lines = [
        "Método: Simpson 1/3",
        f"h = {_format_by_mode(h, mode, digits)}",
        f"Incremento h = {h:.10f}",
        f"Fórmula: A ≈ h/3 · [f(a) + f(b) + 4·Σ f(x_impar) + 2·Σ f(x_par)]",
    ]
    lines.extend(_build_table_lines(x, y, mode, digits))
    lines.extend([
        f"Suma impares = {_format_by_mode(odd_sum, mode, digits)}",
        f"Suma pares = {_format_by_mode(even_sum, mode, digits)}",
        f"Área encontrada = {_format_by_mode(approx, mode, digits)}",
    ])
    return lines, approx


def _development_simpson_three_eighths(f, a, b, N, mode, digits=4):
    h = h_step(a, b, N)
    x = np.linspace(a, b, N + 1)
    y = f(x)
    coef3 = y[1:-1][(np.arange(1, N) % 3 != 0)].sum()
    coef2 = y[3:-1:3].sum()
    approx = 3 * h / 8 * (y[0] + y[-1] + 3 * coef3 + 2 * coef2)
    lines = [
        "Método: Simpson 3/8",
        f"h = {_format_by_mode(h, mode, digits)}",
        f"Incremento h = {h:.10f}",
        f"Fórmula: A ≈ 3h/8 · [f(a) + f(b) + 3·Σ f(x_no_mult3) + 2·Σ f(x_mult3)]",
    ]
    lines.extend(_build_table_lines(x, y, mode, digits))
    lines.extend([
        f"Suma coef.3 = {_format_by_mode(coef3, mode, digits)}",
        f"Suma coef.2 = {_format_by_mode(coef2, mode, digits)}",
        f"Área encontrada = {_format_by_mode(approx, mode, digits)}",
    ])
    return lines, approx


def _development_richardson(f, a, b, n_base, levels, mode, digits=4):
    """Construye y muestra la tabla completa de Richardson/Romberg.

    Usa la fórmula del límite diferido de Richardson (I_ldr) para el primer
    nivel y la recursión de Romberg para los niveles superiores.
    """
    R, best = richardson_extrapolation(f, a, b, n_base, levels)

    # Paso h para nivel base y nivel siguiente (k = h/2)
    h0 = (b - a) / n_base
    k0 = h0 / 2
    h0_sq = h0 ** 2
    k0_sq = k0 ** 2
    factor_ldr = h0_sq / (h0_sq - k0_sq)  # = 4/3 cuando k=h/2
    Ih = R[0][0]
    Ik = R[1][0] if levels >= 1 else Ih

    col_w = digits + 10

    header_parts = [f"{'k':>3}", f"{'N_k':>8}", f"{'h_k':>14}"]
    for j in range(levels + 1):
        lbl = "Ih / T(N_k)" if j == 0 else f"R[k,{j}] / Ildr" if j == 1 else f"R[k,{j}]"
        header_parts.append(f"{lbl:>{col_w}}")
    header = "  ".join(header_parts)
    separator = "─" * len(header)

    lines = [
        "Método: Richardson (Límite Diferido de Richardson — ILDR)",
        f"N base = {n_base}  |  Niveles = {levels}",
        "",
        "─" * 65,
        "FÓRMULA DEL LÍMITE DIFERIDO DE RICHARDSON (md)",
        "─" * 65,
        "  Integral exacta ≈ Ih + error_truncamiento",
        "  Integral exacta ≈ Ih + C·h²",
        "  Integral exacta ≈ Ik + C·k²",
        "  Como las dos expresiones deben ser iguales (C₁=C₂):",
        "    Ih + C·h² = Ik + C·k²  →  C = (Ik − Ih) / (h² − k²)",
        "  Sustituyendo C:",
        "    I_ldr = Ih + (Ik − Ih) · [h² / (h² − k²)]",
        "  Con k = h/2  →  h²/(h²−k²) = h²/(h²−h²/4) = 4/3:",
        "    I_ldr = Ih + (Ik − Ih) · (4/3)  =  (4·Ik − Ih) / 3",
        "─" * 65,
        "",
        f"Valores del nivel base (j=1 — primer ILDR):",
        f"  h  = (b−a)/N_base = ({b}−{a})/{n_base} = {_format_by_mode(h0, mode, digits)}",
        f"  k  = h/2          = {_format_by_mode(k0, mode, digits)}",
        f"  h² = {_format_by_mode(h0_sq, mode, digits)}",
        f"  k² = {_format_by_mode(k0_sq, mode, digits)}",
        f"  h²−k² = {_format_by_mode(h0_sq - k0_sq, mode, digits)}",
        f"  h²/(h²−k²) = {_format_by_mode(factor_ldr, mode, digits)}  (= 4/3 ≈ 1.333...)",
        f"  Ih (N={n_base:>3}, h={_format_by_mode(h0, mode, digits)}) = {_format_by_mode(Ih, mode, digits)}",
        f"  Ik (N={n_base*2:>3}, k={_format_by_mode(k0, mode, digits)}) = {_format_by_mode(Ik, mode, digits)}",
        "",
        f"  I_ldr = Ih + (Ik − Ih) · [h² / (h² − k²)]",
        f"        = {_format_by_mode(Ih, mode, digits)} + ({_format_by_mode(Ik, mode, digits)} − {_format_by_mode(Ih, mode, digits)}) · {_format_by_mode(factor_ldr, mode, digits)}",
        f"        = {_format_by_mode(Ih, mode, digits)} + {_format_by_mode(Ik - Ih, mode, digits)} · {_format_by_mode(factor_ldr, mode, digits)}",
        f"        = {_format_by_mode(Ih, mode, digits)} + {_format_by_mode((Ik - Ih) * factor_ldr, mode, digits)}",
        f"        = {_format_by_mode(R[1][1], mode, digits)}",
        "",
        "─" * 65,
        "TABLA DE RICHARDSON / ROMBERG",
        "  Columna 0 = T(N_k) trapecio,  Columna j ≥ 1 = extrapolación",
        "  R[k,j] = (4ʲ·R[k,j-1] − R[k-1,j-1]) / (4ʲ−1)  (Romberg)",
        "─" * 65,
        header,
        separator,
    ]

    for k in range(levels + 1):
        n_k = n_base * (2 ** k)
        h_k = (b - a) / n_k
        row_parts = [f"{k:>3}", f"{n_k:>8}", f"{_format_by_mode(h_k, mode, digits):>14}"]
        for j in range(levels + 1):
            if j <= k:
                row_parts.append(f"{_format_by_mode(R[k][j], mode, digits):>{col_w}}")
            else:
                row_parts.append(f"{'':>{col_w}}")
        lines.append("  ".join(row_parts))

    lines.extend([separator, ""])

    if levels >= 2:
        lines.append("Cálculo explícito de niveles superiores (j ≥ 2, recursión Romberg):")
        for j in range(2, levels + 1):
            fac = 4 ** j
            lines.append(f"  j={j}  (4^{j}={fac},  divisor={fac-1}):")
            for k in range(j, levels + 1):
                lines.append(
                    f"    R[{k},{j}] = ({fac}·{_format_by_mode(R[k][j-1], mode, digits)}"
                    f" − {_format_by_mode(R[k-1][j-1], mode, digits)}) / {fac-1}"
                    f"  =  {_format_by_mode(R[k][j], mode, digits)}"
                )
        lines.append("")

    lines.extend([
        f"Mejor estimación  R[{levels},{levels}] = {_format_by_mode(best, mode, digits)}",
    ])
    return lines, best


def _nc_compat_table_lines(n_min: int, n_max: int) -> list[str]:
    """Genera la tabla de compatibilidad N vs método (✓/✗) para el rango dado.

    Palomita verde (✓) donde SÍ se puede usar.
    Tache rojo     (✗) donde NO se puede usar.
    """
    CHECK = "✓"
    CROSS = "✗"

    # Encabezado
    header = f"  {'N':>4}  {'Trapecio':^10}  {'Simpson (×2)':^13}  {'3/8 (×3)':^10}  {'2/45 (×4)':^10}"
    sep = "  " + "─" * (len(header) - 2)

    lines = [
        "TABLA DE COMPATIBILIDAD  N vs MÉTODO",
        "(✓ = se puede usar  |  ✗ = NO se puede usar)",
        "─" * len(header),
        header,
        sep,
    ]

    for N in range(n_min, n_max + 1):
        t   = CHECK                          # Trapecio: sin restricción
        s   = CHECK if N % 2 == 0 else CROSS # Simpson 1/3: N par
        r38 = CHECK if N % 3 == 0 else CROSS # 3/8: múltiplo de 3
        r245= CHECK if N % 4 == 0 else CROSS # 2/45: múltiplo de 4
        lines.append(
            f"  {N:>4}  {t:^10}  {s:^13}  {r38:^10}  {r245:^10}"
        )

    lines.extend([
        sep,
        "  Restricciones:",
        "  Trapecio    → sin restricción (cualquier N)",
        "  Simpson     → N múltiplo de 2",
        "  Regla 3/8   → N múltiplo de 3",
        "  Regla 2/45  → N múltiplo de 4",
        "  Nota: N=12 es el mínimo donde los 4 métodos se pueden usar.",
        "─" * len(header),
    ])
    return lines


def _nc_general_table_lines() -> list[str]:
    """Genera la tabla de referencia general de Newton-Cotes (los 3 grados)."""
    w_name = 28
    w_coef = 26
    w_fac  = 7
    header = f"  {'n':>3}  {'Nombre':<{w_name}}  {'Coeficientes':<{w_coef}}  {'Factor':>{w_fac}}  Restricción"
    sep    = "  " + "─" * (len(header) - 2)
    lines  = [
        "TABLA GENERAL DE NEWTON-COTES CERRADAS",
        "─" * len(header),
        header,
        sep,
    ]
    for deg, nc in NEWTON_COTES_DATA.items():
        coef_str = "  ".join(str(c) for c in nc["coefs"])
        lines.append(
            f"  {deg:>3}  {nc['name']:<{w_name}}  {coef_str:<{w_coef}}  {nc['factor_str']:>{w_fac}}  {nc['restriction']}"
        )
    lines.extend([
        sep,
        "  Fórmula elemental : I_seg = factor · (c₀·f(x₀) + c₁·f(x₁) + … + cₙ·f(xₙ))",
        "  Aplicación comp.  : dividir [a,b] en M segmentos de n subintervalos cada uno.",
        "  Puntos compartidos: los extremos de segmentos adyacentes acumulan coefs.",
        "─" * len(header),
    ])
    return lines


def _development_newton_cotes(f, a, b, N, degree, mode, digits=4):
    """Muestra la tabla elemental NC, los coeficientes compuestos y el desarrollo completo."""
    nc = NEWTON_COTES_DATA[degree]
    req = nc["req"]
    if N % req != 0:
        raise ValueError(
            f"N={N} no es múltiplo de {req} — necesario para Newton-Cotes grado {degree}"
        )

    h = h_step(a, b, N)
    M = N // degree                   # número de segmentos
    factor = nc["factor"]
    factor_str = nc["factor_str"]
    basic = nc["coefs"]

    x = np.linspace(a, b, N + 1)
    y = f(x)
    comp = newton_cotes_composite_coefficients(N, degree)
    weighted_sum = float(np.dot(comp, y))
    approx = h * factor * weighted_sum

    # ── Tabla elemental del grado seleccionado ────────────────────────────────
    basic_lines = [
        f"FÓRMULA ELEMENTAL  (n={degree} — {nc['name']})",
        "─" * 50,
        f"  I_seg = ({factor_str}) · ( " + " + ".join(
            f"{c}·f(x{i})" for i, c in enumerate(basic)
        ) + " )",
        "",
        f"  {'Índice':>7}  {'Punto':>8}  {'Coef.':>6}  Factor",
        "  " + "─" * 34,
    ]
    for i, c in enumerate(basic):
        shown_factor = factor_str if i == len(basic) // 2 else ""
        basic_lines.append(f"  {'i='+str(i):>7}  {'f(x'+str(i)+')':>8}  {c:>6}  {shown_factor}")
    basic_lines.extend([
        "  " + "─" * 34,
        f"  Restricción  : {nc['restriction']}",
        f"  Error        : {nc['error_order']}",
        "─" * 50,
    ])

    # ── Coeficientes compuestos ────────────────────────────────────────────────
    comp_int = [int(c) for c in comp]
    comp_str = "  ".join(str(c) for c in comp_int)

    comp_header_lines = [
        "",
        f"APLICACIÓN COMPUESTA  (N={N}, M={M} segmentos, h={_format_by_mode(h, mode, digits)})",
        f"  Coeficientes compuestos: [{comp_str}]",
        f"  Fórmula: I = ({factor_str}) · Σ(comp_i · f(x_i))",
        "",
    ]

    # ── Tabla punto a punto ───────────────────────────────────────────────────
    col = digits + 4
    table_header = (
        f"  {'i':>4}  {'x_i':>{col}}  {'f(x_i)':>{col}}  {'Coef':>5}"
        f"  {'Coef·f(x_i)':>{col}}"
    )
    table_lines = [table_header, "  " + "─" * (len(table_header) - 2)]

    running_total = 0.0
    for i, (xi, yi, ci) in enumerate(zip(x, y, comp)):
        contrib = ci * yi
        running_total += contrib
        table_lines.append(
            f"  {i:>4}  {_format_by_mode(xi, mode, digits):>{col}}"
            f"  {_format_by_mode(yi, mode, digits):>{col}}"
            f"  {int(ci):>5}"
            f"  {_format_by_mode(contrib, mode, digits):>{col}}"
        )
    table_lines.append("  " + "─" * (len(table_header) - 2))

    # ── Cálculo final ─────────────────────────────────────────────────────────
    # factor es el coeficiente numérico puro (sin h): 1/2, 1/3 o 3/8
    # approx = h · factor · weighted_sum
    _FACTOR_FRAC = {2: "1/3", 3: "3/8", 4: "2/45"}
    num_factor_str = _FACTOR_FRAC[degree]
    h_factor = h * factor
    calc_lines = [
        "",
        f"  Σ(comp_i · f(x_i))  =  {_format_by_mode(weighted_sum, mode, digits)}",
        f"  I  =  h · {num_factor_str} · Σ   =   ({factor_str}) · Σ",
        f"     =  {_format_by_mode(h, mode, digits)} · {num_factor_str} · {_format_by_mode(weighted_sum, mode, digits)}",
        f"     =  {_format_by_mode(h_factor, mode, digits)} · {_format_by_mode(weighted_sum, mode, digits)}",
        f"     =  {_format_by_mode(approx, mode, digits)}",
    ]

    lines = [
        f"Newton-Cotes Grado {degree} — {nc['name']}",
        f"Intervalo [{a}, {b}],  N={N},  M={M} segmentos",
        "",
    ]
    lines.extend(basic_lines)
    lines.extend(comp_header_lines)
    lines.extend(table_lines)
    lines.extend(calc_lines)
    return lines, approx


# ─── Clasificación de líneas para colorear la salida ─────────────────────────

_SEC_KEYWORDS = (
    "INTEGRAL EXACTA",
    "MÉTODO DE RICHARDSON",
    "TABLA RESUMEN DE VALIDADORES",
    "NEWTON-COTES GRADO",
    "HOJA DE CÁLCULO COMPLETA",
    "TABLA DE COMPATIBILIDAD",
    "TABLA GENERAL DE NEWTON-COTES",
    "FÓRMULA DEL LÍMITE DIFERIDO DE RICHARDSON",
    "TABLA DE RICHARDSON / ROMBERG",
    "FÓRMULA ELEMENTAL",
    "APLICACIÓN COMPUESTA",
)

_METHOD_PREFIXES = (
    "Método: Trapecio",
    "Método: Punto Medio",
    "Método: Simpson",
    "Método: Richardson",
    "Newton-Cotes Grado",
)

_RESULT_PREFIXES = (
    "It =",
    "Área encontrada =",
    "Mejor estimación",
    "I_ldr =",
    "  I_ldr =",
    "Suma ponderada =",
)


def _classify_line(line: str) -> str:
    s = line.strip()
    if not s:
        return "default"

    # Separadores principales (=====...)
    if len(s) >= 20 and all(c == "=" for c in s):
        return "main_sep"
    # Separadores secundarios (─────... o -----)
    if len(s) >= 5 and (all(c == "─" for c in s) or all(c == "-" for c in s)):
        return "sub_sep"

    # Títulos de sección
    for kw in _SEC_KEYWORDS:
        if kw in s:
            return "section_title"

    # Integral exacta de referencia
    if "∫f(x)dx" in s:
        return "exact"

    # Estado al final de línea (NO OK antes que OK para evitar falso positivo)
    if s.endswith("NO OK"):
        return "status_nok"
    if s.endswith("OK") and any(c.isdigit() for c in s):
        return "status_ok"

    # Estado inline
    if "Estado:" in s:
        if "NO OK" in s:
            return "status_nok"
        if "OK" in s:
            return "status_ok"

    # Encabezado de método
    for kw in _METHOD_PREFIXES:
        if s.startswith(kw):
            return "method_hdr"

    # Advertencias
    if "⚠" in s:
        return "warning"

    # Encabezados de tabla (patrones de columnas conocidos)
    if "Aproximación" in s and "Error" in s and "N" in s:
        return "table_hdr"
    if "N_k" in s and "h_k" in s:
        return "table_hdr"
    if "|" in s and ("x_i" in s or "f(x_i)" in s or "f(x)" in s):
        return "table_hdr"
    if "x_i" in s and "f(x_i)" in s and "Coef" in s:
        return "table_hdr"

    # Fórmulas
    if s.startswith("Fórmula:") or "FÓRMULA" in s:
        return "formula"
    if s.startswith("Equivalente a:"):
        return "formula"

    # Resultados finales
    for kw in _RESULT_PREFIXES:
        if s.startswith(kw):
            return "result"

    # Líneas de paso h/k
    if s.startswith("h =") or s.startswith("h=") or "Incremento h" in s:
        return "h_line"
    if s.startswith("k =") or s.startswith("k="):
        return "h_line"

    # Continuaciones de cálculo (líneas "        = valor")
    if line.startswith("        =") or (
        s.startswith("= ") and len(s.split()) <= 5 and "(" not in s
    ):
        return "step"

    return "default"


# ─── Aplicación principal ─────────────────────────────────────────────────────

class IntegracionDefinidaApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Métodos Numéricos - Integración Definida")
        self.root.geometry("1010x820")

        self.custom_expr = tk.StringVar(value="")
        self.a_var = tk.StringVar(value="0")
        self.b_var = tk.StringVar(value="3")
        self.n_min_var = tk.StringVar(value="1")
        self.n_max_var = tk.StringVar(value="12")
        self.tol_var = tk.StringVar(value="1e-4")
        self.result_format = tk.StringVar(value="Decimal")
        self.rich_levels_var = tk.StringVar(value="4")
        self.trunc_digits_var = tk.StringVar(value="4")
        self.nc_degree_var = tk.StringVar(value="2")   # 2=Simpson, 3=3/8, 4=2/45
        self.last_image = None

        self._build_interface()

    def _build_interface(self):
        main = tk.Frame(self.root, padx=10, pady=10)
        main.pack(fill="both", expand=True)

        header = tk.Frame(main)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="Integración Definida", font=("Georgia", 22, "bold")).pack(anchor="w")
        tk.Label(
            header,
            text="Trapecio · Punto Medio · Simpson 1/3 · Simpson 3/8 · Regla 2/45 · Richardson",
            font=("Arial", 12),
        ).pack(anchor="w", pady=(4, 8))

        input_frame = tk.LabelFrame(main, text="Parámetros de entrada", padx=10, pady=10)
        input_frame.pack(fill="x", pady=(0, 10))

        # Fila 0: expresión
        tk.Label(input_frame, text="Expresión f(x):", font=("Arial", 11)).grid(row=0, column=0, sticky="w")
        tk.Entry(input_frame, textvariable=self.custom_expr, width=62).grid(
            row=0, column=1, columnspan=5, sticky="w"
        )
        tk.Label(
            input_frame,
            text="Ejemplos: x^2 - 2x + 1,  sin(x) + 0.3*x^2,  exp(x)/sqrt(x+1),  log(x+1)*cos(x)",
            font=("Arial", 9),
            fg="#555555",
        ).grid(row=1, column=1, columnspan=5, sticky="w", pady=(2, 6))

        # Fila 2: a, b
        tk.Label(input_frame, text="a:", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=(6, 0))
        tk.Entry(input_frame, textvariable=self.a_var, width=12).grid(row=2, column=1, sticky="w", pady=(6, 0))
        tk.Label(input_frame, text="b:", font=("Arial", 11)).grid(row=2, column=2, sticky="w", pady=(6, 0), padx=(14, 0))
        tk.Entry(input_frame, textvariable=self.b_var, width=12).grid(row=2, column=3, sticky="w", pady=(6, 0))

        # Fila 3: N mínimo, N máximo
        tk.Label(input_frame, text="N mínimo:", font=("Arial", 11)).grid(row=3, column=0, sticky="w", pady=(6, 0))
        tk.Entry(input_frame, textvariable=self.n_min_var, width=12).grid(row=3, column=1, sticky="w", pady=(6, 0))
        tk.Label(input_frame, text="N máximo:", font=("Arial", 11)).grid(row=3, column=2, sticky="w", pady=(6, 0), padx=(14, 0))
        tk.Entry(input_frame, textvariable=self.n_max_var, width=12).grid(row=3, column=3, sticky="w", pady=(6, 0))

        # Fila 4: Tolerancia
        tk.Label(input_frame, text="Tolerancia:", font=("Arial", 11)).grid(row=4, column=0, sticky="w", pady=(6, 0))
        tk.Entry(input_frame, textvariable=self.tol_var, width=12).grid(row=4, column=1, sticky="w", pady=(6, 0))

        # Fila 5: modo resultado, dígitos truncamiento
        tk.Label(input_frame, text="Modo resultado:", font=("Arial", 11)).grid(row=5, column=0, sticky="w", pady=(6, 0))
        tk.OptionMenu(input_frame, self.result_format, "Decimal", "Truncamiento").grid(
            row=5, column=1, sticky="w", pady=(6, 0)
        )
        tk.Label(input_frame, text="Dígitos truncamiento:", font=("Arial", 11)).grid(
            row=5, column=2, sticky="w", pady=(6, 0), padx=(14, 0)
        )
        trunc_spin = tk.Spinbox(input_frame, textvariable=self.trunc_digits_var, from_=1, to=15, width=6)
        trunc_spin.grid(row=5, column=3, sticky="w", pady=(6, 0))
        tk.Label(input_frame, text="(aplica al modo Truncamiento)", font=("Arial", 9), fg="#555555").grid(
            row=5, column=4, sticky="w", padx=(6, 0)
        )

        # Fila 6: niveles Richardson
        tk.Label(input_frame, text="Niveles Richardson:", font=("Arial", 11)).grid(row=6, column=0, sticky="w", pady=(6, 0))
        rich_spin = tk.Spinbox(input_frame, textvariable=self.rich_levels_var, from_=1, to=12, width=6)
        rich_spin.grid(row=6, column=1, sticky="w", pady=(6, 0))
        tk.Label(
            input_frame,
            text="N se duplica en cada nivel: N, 2N, 4N, … (N = N mínimo)",
            font=("Arial", 9),
            fg="#555555",
        ).grid(row=6, column=2, columnspan=4, sticky="w", padx=(6, 0))

        # Botones
        buttons = tk.Frame(main)
        buttons.pack(fill="x", pady=(0, 10))
        tk.Button(buttons, text="Calcular", bg="#5CB85C", fg="white", font=("Arial", 11, "bold"),
                  command=self._calcular).pack(side="left", padx=6)

    # ─── Parsers ──────────────────────────────────────────────────────────────

    def _parse_float(self, value: str, name: str) -> float:
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Valor inválido para {name}: '{value}'")

    def _parse_int(self, value: str, name: str) -> int:
        try:
            parsed = int(value)
        except ValueError:
            raise ValueError(f"Valor inválido para {name}: '{value}'")
        if parsed <= 0:
            raise ValueError(f"{name} debe ser mayor que cero")
        return parsed

    def _parse_positive_float(self, value: str, name: str) -> float:
        parsed = self._parse_float(value, name)
        if parsed <= 0:
            raise ValueError(f"{name} debe ser mayor que cero")
        return parsed

    def _get_function(self):
        custom = self.custom_expr.get().strip()
        if not custom:
            raise ValueError("Ingrese una expresión de función para integrar.")
        return _safe_eval_function(custom), f"f(x) = {custom}", custom

    def _get_digits(self) -> int:
        try:
            d = int(self.trunc_digits_var.get())
            return max(1, min(d, 15))
        except ValueError:
            return 4

    # ─── Ventanas de resultados ───────────────────────────────────────────────

    def _show_results_window(self, title: str, lines: list[str]) -> None:
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("1200x820")
        win.minsize(900, 550)

        # Barra de título interna con fondo azul oscuro
        title_bar = tk.Frame(win, bg="#1A237E", pady=7)
        title_bar.pack(fill="x", side="top")
        tk.Label(
            title_bar, text=title,
            bg="#1A237E", fg="#FFFFFF",
            font=("Arial", 12, "bold"), padx=12,
        ).pack(side="left")

        # Scrollbar horizontal (se empaqueta antes para ocupar el borde inferior)
        hscroll = tk.Scrollbar(win, orient="horizontal")
        hscroll.pack(side="bottom", fill="x")

        # Marco para texto + scrollbar vertical
        txt_frame = tk.Frame(win)
        txt_frame.pack(fill="both", expand=True)

        vscroll = tk.Scrollbar(txt_frame, orient="vertical")
        vscroll.pack(side="right", fill="y")

        txt = tk.Text(
            txt_frame,
            font=("Consolas", 10),
            bg="#FFFFFF",
            fg="#1E1E2E",
            padx=10, pady=6,
            wrap=tk.NONE,
            relief="flat",
            borderwidth=0,
            yscrollcommand=vscroll.set,
            xscrollcommand=hscroll.set,
        )
        txt.pack(side="left", fill="both", expand=True)
        vscroll.config(command=txt.yview)
        hscroll.config(command=txt.xview)

        # ── Etiquetas de color y formato ───────────────────────────────
        _B   = ("Consolas", 10, "bold")
        _N   = ("Consolas", 10)
        _I   = ("Consolas", 10, "italic")
        _B11 = ("Consolas", 11, "bold")

        # Separador principal (=====)
        txt.tag_configure("main_sep",
            foreground="#1565C0", font=_B)
        # Título de sección (INTEGRAL EXACTA, TABLA RESUMEN, etc.)
        txt.tag_configure("section_title",
            foreground="#FFFFFF", background="#1A237E",
            font=_B11, spacing1=5, spacing3=5)
        # Separador secundario (─────)
        txt.tag_configure("sub_sep",
            foreground="#B0BEC5", font=_N)
        # Nombre del método
        txt.tag_configure("method_hdr",
            foreground="#4A148C", background="#F3E5F5",
            font=_B, spacing1=4, spacing3=4)
        # Encabezado de columnas de tabla
        txt.tag_configure("table_hdr",
            foreground="#01579B", background="#E3F2FD",
            font=_B)
        # Resultado final destacado
        txt.tag_configure("result",
            foreground="#1B5E20", background="#E8F5E9",
            font=_B, spacing1=3, spacing3=3)
        # Integral exacta de referencia
        txt.tag_configure("exact",
            foreground="#BF360C", background="#FFF8E1",
            font=_B, spacing1=3, spacing3=3)
        # Estado OK
        txt.tag_configure("status_ok",
            foreground="#2E7D32", font=_B)
        # Estado NO OK
        txt.tag_configure("status_nok",
            foreground="#B71C1C", font=_B)
        # Fórmula
        txt.tag_configure("formula",
            foreground="#6A1B9A", font=_I)
        # Advertencia
        txt.tag_configure("warning",
            foreground="#E65100", background="#FFF3E0",
            font=_I, spacing1=2, spacing3=2)
        # Líneas de paso h
        txt.tag_configure("h_line",
            foreground="#00695C", font=_N)
        # Pasos intermedios de cálculo
        txt.tag_configure("step",
            foreground="#607D8B", font=_N)
        # Texto por defecto
        txt.tag_configure("default",
            foreground="#1E1E2E", font=_N)

        # ── Insertar líneas con su etiqueta de color ───────────────────
        for line in lines:
            tag = _classify_line(line)
            txt.insert(tk.END, line + "\n", tag)

        txt.configure(state="disabled")

    def _open_image_window(self, path: Path) -> None:
        win = tk.Toplevel(self.root)
        win.title(path.name)
        try:
            image = tk.PhotoImage(file=path)
            label = tk.Label(win, image=image)
            label.image = image
            label.pack(fill="both", expand=True)
        except Exception as exc:
            tk.Label(
                win,
                text=f"No se pudo mostrar la imagen: {exc}\nArchivo: {path}",
                justify="left",
            ).pack(fill="both", expand=True, padx=10, pady=10)

    def _show_graficas_window(self, image_paths: list) -> None:
        """Muestra todas las gráficas en pestañas dentro de una sola ventana."""
        if not image_paths:
            return

        win = tk.Toplevel(self.root)
        win.title("Gráficas — Integración Definida")
        win.geometry("920x660")
        win.minsize(700, 480)

        title_bar = tk.Frame(win, bg="#1A237E", pady=7)
        title_bar.pack(fill="x", side="top")
        tk.Label(
            title_bar, text="Gráficas de Integración Definida",
            bg="#1A237E", fg="#FFFFFF",
            font=("Arial", 12, "bold"), padx=12,
        ).pack(side="left")

        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=6, pady=6)

        _TAB_NAMES = {
            "integracion_area.png":            "Área bajo f(x)",
            "integracion_trapecio_nmin.png":   "Trapecio — N mín",
            "integracion_trapecio_nmax.png":   "Trapecio — N máx",
            "integracion_simpson.png":         "Simpson 1/3",
            "integracion_richardson.png":      "Richardson",
        }

        for path in image_paths:
            tab = tk.Frame(notebook, bg="#FFFFFF")
            name = _TAB_NAMES.get(path.name, path.name)
            notebook.add(tab, text=name)

            canvas_frame = tk.Frame(tab, bg="#FFFFFF")
            canvas_frame.pack(fill="both", expand=True)

            try:
                if _PILImage is not None and _ImageTk is not None:
                    pil_img = _PILImage.open(path)

                    def _make_resize_handler(pil_src, lbl_widget):
                        def _on_resize(event):
                            resized = pil_src.copy()
                            resized.thumbnail((event.width, event.height), _PILImage.Resampling.LANCZOS)
                            photo = _ImageTk.PhotoImage(resized)
                            lbl_widget.configure(image=photo)
                            lbl_widget.image = photo
                        return _on_resize

                    photo = _ImageTk.PhotoImage(pil_img)
                    lbl = tk.Label(canvas_frame, image=photo, bg="#FFFFFF")
                    lbl.image = photo
                    lbl.pack(fill="both", expand=True)
                    canvas_frame.bind("<Configure>", _make_resize_handler(pil_img, lbl))
                else:
                    photo = tk.PhotoImage(file=str(path))
                    lbl = tk.Label(canvas_frame, image=photo, bg="#FFFFFF")
                    lbl.image = photo
                    lbl.pack(fill="both", expand=True)
            except Exception as exc:
                tk.Label(
                    canvas_frame,
                    text=f"No se pudo mostrar: {path.name}\n{exc}",
                    fg="red", bg="#FFFFFF", font=("Arial", 10),
                ).pack(padx=10, pady=10)

    # ─── Acción: Calcular ─────────────────────────────────────────────────────

    def _calcular(self):
        try:
            a = self._parse_float(self.a_var.get(), "a")
            b = self._parse_float(self.b_var.get(), "b")
            n_min = self._parse_int(self.n_min_var.get(), "N mínimo")
            n_max = self._parse_int(self.n_max_var.get(), "N máximo")
            tol = self._parse_positive_float(self.tol_var.get(), "Tolerancia")
            rich_levels = self._parse_int(self.rich_levels_var.get(), "Niveles Richardson")
            digits = self._get_digits()
            mode = self.result_format.get()

            if b <= a:
                raise ValueError("b debe ser mayor que a")
            if n_min > n_max:
                raise ValueError("N mínimo debe ser ≤ N máximo")
            if n_max - n_min > 100:
                raise ValueError("Rango de N demasiado grande (máx. 100 incrementos)")

            f, expr, _ = self._get_function()
            domain_ok, domain_msg = _check_function_domain(f, a, b)

            exact_val = None
            exact_method = "No disponible"
            if domain_ok:
                try:
                    exact_val, exact_method = exact_integral_quad(f, a, b)
                except Exception:
                    exact_val = None
                    exact_method = "No disponible"
            negative_area = False
            if domain_ok and exact_val is not None:
                negative_area = is_entirely_below_x_axis(f, a, b)
            exact_display = abs(exact_val) if (negative_area and exact_val is not None) else exact_val

            non_rich = ["Trapecio", "Punto Medio", "Simpson 1/3", "Simpson 3/8", "Regla 2/45"]
            sep = "=" * 70

            # ── Encabezado compartido ─────────────────────────────────────────
            _hdr: list[str] = [
                sep,
                "  INTEGRAL EXACTA DE REFERENCIA",
                f"  Método:  {exact_method}",
                (f"  ∫f(x)dx  =  {exact_display:.15f}" if exact_display is not None else "  ∫f(x)dx  =  N/A"),
                sep,
                "",
                f"Función  : {expr}",
                f"Intervalo: [{a},  {b}]",
                f"Tolerancia: {tol}",
                f"Modo: {mode}" + (f"  |  Dígitos: {digits}" if mode == "Truncamiento" else ""),
                "",
            ]
            _warn: list[str] = []
            if not domain_ok:
                _warn += [f"⚠ {domain_msg}", "  Se omiten cálculos que dependan de valores no definidos.", ""]
            if negative_area:
                _warn += ["⚠ La función es completamente negativa en [a,b].", "  El área se muestra en valor absoluto.", ""]

            # ── VENTANA 1: TABLAS ─────────────────────────────────────────────
            lt: list[str] = list(_hdr) + list(_warn)

            lt += [
                "Resultados por N:",
                f"{'N':>3}  {'h':>12}  {'Método':<16}  {'Aproximación':>18}  {'Error':>14}  Estado",
                "─" * 80,
            ]
            for N in range(n_min, n_max + 1):
                h = h_step(a, b, N)
                for method in non_rich:
                    if not domain_ok:
                        lt.append(f"{N:>3}  {h:>12.8f}  {method:<16}  {'ERROR':>18}  {'─':>14}  {domain_msg}")
                        continue
                    try:
                        approx = self._compute_method(f, a, b, N, method)
                        if negative_area:
                            approx = abs(approx)
                        error = abs(approx - exact_display) if exact_display is not None else None
                        status = "OK" if (error is not None and error <= tol) else "NO OK"
                        if error is None:
                            status = "N/A"
                        lt.append(
                            f"{N:>3}  {h:>12.8f}  {method:<16}"
                            f"  {_format_value(approx, mode, digits):>18}"
                            f"  {_format_optional(error, mode, digits):>14}  {status}"
                        )
                    except ValueError as exc:
                        lt.append(f"{N:>3}  {h:>12.8f}  {method:<16}  {'ERROR':>18}  {'─':>14}  {exc}")

            # Resultados de integral, área y sumatoria por método
            if domain_ok:
                # (degree, nombre, factor_str, factor_num, req)
                _M = [
                    (1, "Trapecio",    "h/2",   0.5,      1),
                    (2, "Simpson 1/3", "h/3",   1/3,      2),
                    (3, "Regla 3/8",   "3h/8",  3/8,      3),
                    (4, "Regla 2/45",  "2h/45", 2/45,     4),
                ]
                wM, wF, wV = 14, 7, digits + 8   # anchos de columnas

                sep_row  = "  " + "─" * (wM + wF + 4 * wV + 18)
                sep_main = "  " + "═" * (wM + wF + 4 * wV + 18)
                hdr_row  = (
                    f"  {'Método':<{wM}}  {'Factor':>{wF}}"
                    f"  {'Σ Integral':>{wV}}"
                    f"  {'Σ Área':>{wV}}"
                    f"  {'Integral':>{wV}}"
                    f"  {'Área':>{wV}}"
                )

                lt += ["", sep_main, "  RESULTADOS POR MÉTODO — INTEGRAL, ÁREA Y SUMATORIA", sep_main]

                for N in sorted(set([n_min, n_max])):
                    h = h_step(a, b, N)
                    xs = np.linspace(a, b, N + 1)
                    ys = f(xs)
                    ys_abs = np.abs(ys)

                    lt += [
                        "",
                        f"  N = {N}   h = {_format_value(h, mode, digits)}",
                        sep_row, hdr_row, sep_row,
                    ]

                    for deg, m_name, f_str, factor_num, req in _M:
                        if N % req != 0:
                            no_aplica = f"No aplica (N no es múltiplo de {req})"
                            lt.append(
                                f"  {m_name:<{wM}}  {f_str:>{wF}}"
                                f"  {no_aplica:>{wV}}"
                                f"  {'─':>{wV}}"
                                f"  {'─':>{wV}}"
                                f"  {'─':>{wV}}"
                            )
                            continue
                        try:
                            if deg == 1:
                                coefs = np.ones(N + 1)
                                coefs[1:-1] = 2
                            else:
                                coefs = newton_cotes_composite_coefficients(N, deg)

                            suma      = float(np.dot(coefs, ys))
                            suma_abs  = float(np.dot(coefs, ys_abs))
                            integral  = h * factor_num * suma
                            area      = h * factor_num * suma_abs
                            if negative_area:
                                integral = abs(integral)

                            lt.append(
                                f"  {m_name:<{wM}}  {f_str:>{wF}}"
                                f"  {_format_value(suma,     mode, digits):>{wV}}"
                                f"  {_format_value(suma_abs, mode, digits):>{wV}}"
                                f"  {_format_value(integral, mode, digits):>{wV}}"
                                f"  {_format_value(area,     mode, digits):>{wV}}"
                            )
                        except Exception as exc:
                            lt.append(f"  {m_name:<{wM}}  ERROR: {exc}")

                    lt.append(sep_row)

                lt += ["", sep_main, ""]

            # Hoja de cálculo estilo md (coeficientes por punto)
            lt += [""]
            if domain_ok:
                lt += _build_md_style_table(f, a, b, n_min, mode, digits)
                if n_max != n_min:
                    lt += [""]
                    lt += _build_md_style_table(f, a, b, n_max, mode, digits)
            else:
                lt.append(f"  {domain_msg}")

            # Tabla resumen de validadores
            lt += [
                "",
                sep,
                "  TABLA RESUMEN DE VALIDADORES  (vs integral exacta)",
                sep,
                (f"  Integral exacta = {exact_display:.15f}" if exact_display is not None else "  Integral exacta = N/A"),
                f"  Fuente         : {exact_method}",
                "",
                f"  {'Método':<22}  {'N':>5}  {'Aproximación':>20}  {'Error':>16}  {'≤ Tol':>6}  Estado",
                "  " + "─" * 80,
            ]
            for method in non_rich:
                for N in [n_min, n_max]:
                    if not domain_ok:
                        lt.append(f"  {method:<22}  {N:>5}  {'ERROR':>20}  {'─':>16}  {'─':>6}  {domain_msg}")
                        continue
                    try:
                        approx = self._compute_method(f, a, b, N, method)
                        if negative_area:
                            approx = abs(approx)
                        error = abs(approx - exact_display) if exact_display is not None else None
                        status = "OK" if (error is not None and error <= tol) else "NO OK"
                        within = "Sí" if (error is not None and error <= tol) else "No"
                        if error is None:
                            status = "N/A"
                            within = "N/A"
                        lt.append(
                            f"  {method:<22}  {N:>5}"
                            f"  {_format_value(approx, mode, digits):>20}"
                            f"  {_format_optional(error, mode, digits):>16}"
                            f"  {within:>6}  {status}"
                        )
                    except ValueError:
                        lt.append(f"  {method:<22}  {N:>5}  {'N/A':>20}  {'─':>16}  {'─':>6}  SKIP")

            if domain_ok:
                try:
                    _, rich_best_v = richardson_extrapolation(f, a, b, n_min, rich_levels)
                    if negative_area:
                        rich_best_v = abs(rich_best_v)
                    rich_err_v = abs(rich_best_v - exact_display) if exact_display is not None else None
                    rich_stat_v = "OK" if (rich_err_v is not None and rich_err_v <= tol) else "NO OK"
                    rich_within = "Sí" if (rich_err_v is not None and rich_err_v <= tol) else "No"
                    if rich_err_v is None:
                        rich_stat_v = "N/A"
                        rich_within = "N/A"
                    lt.append(
                        f"  {'Richardson (L='+str(rich_levels)+')':<22}  {n_min:>5}*"
                        f"  {_format_value(rich_best_v, mode, digits):>20}"
                        f"  {_format_optional(rich_err_v, mode, digits):>16}"
                        f"  {rich_within:>6}  {rich_stat_v}"
                    )
                    lt.append(f"  * N base; se usan hasta N={n_min * 2**rich_levels}")
                except Exception as exc:
                    lt.append(f"  Richardson: ERROR — {exc}")
            else:
                lt.append(f"  Richardson: ERROR — {domain_msg}")

            lt.append(f"\nNota: h = (b − a) / N")

            # ── VENTANA 2: PROCEDIMIENTOS ─────────────────────────────────────
            lp: list[str] = list(_hdr) + list(_warn)

            # Desarrollo Trapecio
            if domain_ok:
                lp.append(f"Detalle paso a paso — Trapecio  (N={n_min}):")
                lp += _development_trapezoid(f, a, b, n_min, mode, digits)[0]
                if n_max != n_min:
                    lp += ["", f"Detalle paso a paso — Trapecio  (N={n_max}):"]
                    lp += _development_trapezoid(f, a, b, n_max, mode, digits)[0]

            # Richardson completo
            lp += [
                "",
                "─" * 70,
                "  MÉTODO DE RICHARDSON / ROMBERG",
                f"  N base = {n_min}  |  Niveles = {rich_levels}",
                "─" * 70,
                "",
            ]
            if domain_ok:
                rich_dev_lines, rich_best = _development_richardson(f, a, b, n_min, rich_levels, mode, digits)
                lp += rich_dev_lines
                if negative_area:
                    rich_best = abs(rich_best)
                rich_error = abs(rich_best - exact_display) if exact_display is not None else None
                rich_status = "OK" if (rich_error is not None and rich_error <= tol) else "NO OK"
                if rich_error is None:
                    rich_status = "N/A"
                lp += [
                    "",
                    f"  Error vs integral exacta: {_format_optional(rich_error, mode, digits)}",
                    f"  Tolerancia:               {tol}",
                    f"  Estado:                   {rich_status}",
                    "",
                    "Hojas de cálculo por nivel de Richardson (trapecio en cada N_k):",
                ]
                for k in range(rich_levels + 1):
                    n_k = n_min * (2 ** k)
                    lp.append(f"\n  Nivel k={k},  N={n_k},  h={(b-a)/n_k:.10f}:")
                    lp += _build_method_spreadsheet(f, a, b, n_k, "Trapecio", mode, digits)
            else:
                lp.append(f"  {domain_msg}")

            # Hojas de cálculo por método a N_max
            lp += ["", f"Hojas de cálculo para N = {n_max}  (h = {h_step(a, b, n_max):.10f}):"]
            if domain_ok:
                for method in non_rich:
                    if method == "Simpson 1/3" and n_max % 2 != 0:
                        lp.append(f"  [{method}] requiere N par — omitido para N={n_max}")
                        continue
                    if method == "Simpson 3/8" and n_max % 3 != 0:
                        lp.append(f"  [{method}] requiere N múltiplo de 3 — omitido para N={n_max}")
                        continue
                    if method == "Regla 2/45" and n_max % 4 != 0:
                        lp.append(f"  [{method}] requiere N múltiplo de 4 — omitido para N={n_max}")
                        continue
                    try:
                        lp += _build_method_spreadsheet(f, a, b, n_max, method, mode, digits)
                        lp.append("")
                    except Exception as exc:
                        lp.append(f"  Error en hoja de cálculo para {method}: {exc}")
            else:
                lp.append(f"  {domain_msg}")

            # ── VENTANA 3: GRÁFICAS ───────────────────────────────────────────
            plot_paths: list[Path] = []
            if domain_ok:
                try:
                    plot_paths.append(plot_function_and_area(f, a, b, "integracion_area.png", f"Área bajo {expr}"))
                    plot_paths.append(plot_trapezoids(f, a, b, n_min, "integracion_trapecio_nmin.png"))
                    if n_max != n_min:
                        plot_paths.append(plot_trapezoids(f, a, b, n_max, "integracion_trapecio_nmax.png"))
                    if n_max % 2 == 0:
                        plot_paths.append(plot_simpson_approximation(f, a, b, n_max, "integracion_simpson.png"))
                    plot_paths.append(
                        plot_richardson_convergence(f, a, b, n_min, rich_levels, "integracion_richardson.png")
                    )
                except Exception as exc:
                    lp += ["", f"⚠ No se pudieron generar todas las gráficas: {exc}"]

            # ── Abrir las 3 ventanas ──────────────────────────────────────────
            self._show_results_window("Tablas de Resultados", lt)
            self._show_results_window("Procedimientos — Paso a Paso", lp)
            if plot_paths:
                self._show_graficas_window(plot_paths)

        except (ValueError, SyntaxError, NameError, TypeError, ZeroDivisionError) as exc:
            messagebox.showerror("Error", str(exc))

    # ─── Método auxiliar de cómputo ───────────────────────────────────────────

    @staticmethod
    def _compute_method(f, a, b, N, method, nc_degree: int = 2):
        if method == "Trapecio":
            return trapezoidal_rule(f, a, b, N)
        if method == "Punto Medio":
            return midpoint_rule(f, a, b, N)
        if method == "Simpson 1/3":
            if N % 2 != 0:
                raise ValueError("N debe ser par para Simpson 1/3")
            return simpson_one_third(f, a, b, N)
        if method == "Simpson 3/8":
            if N % 3 != 0:
                raise ValueError("N debe ser múltiplo de 3 para Simpson 3/8")
            return simpson_three_eighths(f, a, b, N)
        if method == "Regla 2/45":
            if N % 4 != 0:
                raise ValueError("N debe ser múltiplo de 4 para la regla 2/45")
            return newton_cotes(f, a, b, N, 4)
        if method == "Newton-Cotes":
            return newton_cotes(f, a, b, N, nc_degree)
        raise ValueError(f"Método desconocido: {method}")

    # ─── Acciones de gráficas ─────────────────────────────────────────────────

    def _graficar_area(self):
        try:
            a = self._parse_float(self.a_var.get(), "a")
            b = self._parse_float(self.b_var.get(), "b")
            n_min = self._parse_int(self.n_min_var.get(), "N mínimo")
            n_max = self._parse_int(self.n_max_var.get(), "N máximo")
            if b <= a:
                raise ValueError("b debe ser mayor que a")
            f, expr, _ = self._get_function()
            path = plot_function_and_area(f, a, b, "integracion_area.png", f"Área bajo {expr}")
            self._open_image_window(path)
            lines = [
                f"Gráfica del área bajo la curva para {expr}",
                f"Intervalo: [{a}, {b}]",
                "",
                "Valores de h por N:",
            ]
            for N in range(n_min, n_max + 1):
                lines.append(f"  N = {N:>4},  h = {h_step(a, b, N):.10f}")
            self._show_results_window("Área bajo la curva", lines)
        except (ValueError, SyntaxError, NameError, TypeError, ZeroDivisionError) as exc:
            messagebox.showerror("Error", str(exc))

    def _graficar_trapecios(self):
        try:
            a = self._parse_float(self.a_var.get(), "a")
            b = self._parse_float(self.b_var.get(), "b")
            n_min = self._parse_int(self.n_min_var.get(), "N mínimo")
            n_max = self._parse_int(self.n_max_var.get(), "N máximo")
            if b <= a:
                raise ValueError("b debe ser mayor que a")
            f, expr, _ = self._get_function()
            path_min = plot_trapezoids(f, a, b, n_min, "integracion_trapecio_nmin.png")
            path_max = plot_trapezoids(f, a, b, n_max, "integracion_trapecio_nmax.png")
            self._open_image_window(path_min)
            self._open_image_window(path_max)
            mode = self.result_format.get()
            digits = self._get_digits()
            lines = [
                f"Trapecios para {expr}",
                f"Intervalo: [{a}, {b}]",
                f"N mínimo = {n_min},  h = {h_step(a, b, n_min):.10f}",
                f"N máximo = {n_max},  h = {h_step(a, b, n_max):.10f}",
                "",
                "Aproximaciones:",
                f"  Trapecio N={n_min}: {_format_value(trapezoidal_rule(f, a, b, n_min), mode, digits)}",
                f"  Trapecio N={n_max}: {_format_value(trapezoidal_rule(f, a, b, n_max), mode, digits)}",
            ]
            self._show_results_window("Trapecios", lines)
        except (ValueError, SyntaxError, NameError, TypeError, ZeroDivisionError) as exc:
            messagebox.showerror("Error", str(exc))

    def _graficar_simpson(self):
        try:
            a = self._parse_float(self.a_var.get(), "a")
            b = self._parse_float(self.b_var.get(), "b")
            n = self._parse_int(self.n_max_var.get(), "N máximo")
            if b <= a:
                raise ValueError("b debe ser mayor que a")
            if n % 2 != 0:
                raise ValueError("N debe ser par para graficar Simpson 1/3")
            f, expr, _ = self._get_function()
            path = plot_simpson_approximation(f, a, b, n, "integracion_simpson.png")
            self._open_image_window(path)
            mode = self.result_format.get()
            digits = self._get_digits()
            lines = [
                f"Simpson 1/3 para {expr}",
                f"Intervalo: [{a}, {b}]",
                f"N = {n},  h = {h_step(a, b, n):.10f}",
                f"Aproximación: {_format_value(simpson_one_third(f, a, b, n), mode, digits)}",
            ]
            self._show_results_window("Simpson", lines)
        except (ValueError, SyntaxError, NameError, TypeError, ZeroDivisionError) as exc:
            messagebox.showerror("Error", str(exc))

    def _graficar_richardson(self):
        try:
            a = self._parse_float(self.a_var.get(), "a")
            b = self._parse_float(self.b_var.get(), "b")
            n_min = self._parse_int(self.n_min_var.get(), "N mínimo")
            rich_levels = self._parse_int(self.rich_levels_var.get(), "Niveles Richardson")
            if b <= a:
                raise ValueError("b debe ser mayor que a")
            f, expr, _ = self._get_function()
            path = plot_richardson_convergence(
                f, a, b, n_min, rich_levels, "integracion_richardson.png"
            )
            self._open_image_window(path)
            mode = self.result_format.get()
            digits = self._get_digits()
            _, best = richardson_extrapolation(f, a, b, n_min, rich_levels)
            exact_val, exact_src = exact_integral_quad(f, a, b)
            lines = [
                f"Richardson/Romberg para {expr}",
                f"Intervalo: [{a}, {b}]",
                f"N base = {n_min},  Niveles = {rich_levels}",
                f"Mejor estimación R[{rich_levels},{rich_levels}]: {_format_value(best, mode, digits)}",
                f"Integral exacta ({exact_src}): {exact_val:.15f}",
                f"Error: {_format_value(abs(best - exact_val), mode, digits)}",
            ]
            self._show_results_window("Richardson — Convergencia", lines)
        except (ValueError, SyntaxError, NameError, TypeError, ZeroDivisionError) as exc:
            messagebox.showerror("Error", str(exc))

    def _mostrar_tabla_nc(self):
        """Muestra la tabla Newton-Cotes con el desarrollo completo para el grado seleccionado."""
        try:
            a = self._parse_float(self.a_var.get(), "a")
            b = self._parse_float(self.b_var.get(), "b")
            n_min = self._parse_int(self.n_min_var.get(), "N mínimo")
            n_max = self._parse_int(self.n_max_var.get(), "N máximo")
            tol = self._parse_positive_float(self.tol_var.get(), "Tolerancia")
            nc_degree = int(self.nc_degree_var.get())
            mode = self.result_format.get()
            digits = self._get_digits()
            if b <= a:
                raise ValueError("b debe ser mayor que a")

            f, expr, _ = self._get_function()
            exact_val, exact_method = exact_integral_quad(f, a, b)
            negative_area = is_entirely_below_x_axis(f, a, b)
            exact_display = abs(exact_val) if negative_area else exact_val
            nc_info = NEWTON_COTES_DATA[nc_degree]

            sep = "=" * 70
            lines: list[str] = [
                sep,
                "  INTEGRAL EXACTA DE REFERENCIA",
                f"  Método : {exact_method}",
                f"  ∫f(x)dx = {exact_display:.15f}",
                sep,
                "",
                f"Función   : {expr}",
                f"Intervalo : [{a}, {b}]",
                f"Tolerancia: {tol}",
                "",
            ]

            # Tabla general de referencia
            lines.extend(_nc_general_table_lines())
            lines.append("")

            # Tabla de compatibilidad N vs método
            lines.extend(_nc_compat_table_lines(n_min, n_max))
            lines.append("")

            # Desarrollo para cada N válido en el rango
            req = nc_info["req"]
            ns_validos = [N for N in range(n_min, n_max + 1) if N % req == 0]
            if not ns_validos:
                lines.append(
                    f"No hay ningún N en [{n_min},{n_max}] que sea múltiplo de {req}."
                )
            else:
                lines.extend([
                    f"Resumen de aproximaciones para grado {nc_degree} ({nc_info['name']}):",
                    f"  {'N':>4}  {'h':>14}  {'Aproximación':>18}  {'Error':>14}  Estado",
                    "  " + "─" * 66,
                ])
                for N in ns_validos:
                    try:
                        approx = newton_cotes(f, a, b, N, nc_degree)
                        if negative_area:
                            approx = abs(approx)
                        error = abs(approx - exact_display)
                        status = "OK" if error <= tol else "NO OK"
                        lines.append(
                            f"  {N:>4}  {h_step(a,b,N):>14.10f}"
                            f"  {_format_value(approx, mode, digits):>18}"
                            f"  {_format_value(error, mode, digits):>14}  {status}"
                        )
                    except Exception as exc:
                        lines.append(f"  {N:>4}  ERROR: {exc}")

                lines.append("")
                # Desarrollo detallado para N_min y N_max válidos
                for N in sorted(set([ns_validos[0], ns_validos[-1]])):
                    lines.extend([
                        "─" * 70,
                        f"  HOJA DE CÁLCULO COMPLETA — N={N}",
                        "─" * 70,
                    ])
                    try:
                        nc_lines, nc_approx = _development_newton_cotes(
                            f, a, b, N, nc_degree, mode, digits
                        )
                        lines.extend(nc_lines)
                        if negative_area:
                            nc_approx = abs(nc_approx)
                        nc_error = abs(nc_approx - exact_display)
                        nc_status = "OK" if nc_error <= tol else "NO OK"
                        lines.extend([
                            "",
                            f"  Integral exacta            : {_format_value(exact_display, mode, digits)}",
                            f"  Aproximación Newton-Cotes  : {_format_value(nc_approx, mode, digits)}",
                            f"  Error                      : {_format_value(nc_error, mode, digits)}",
                            f"  Estado                     : {nc_status}",
                        ])
                    except ValueError as exc:
                        lines.append(f"  ERROR: {exc}")

            self._show_results_window(
                f"Newton-Cotes Grado {nc_degree} — {nc_info['name']}", lines
            )
        except (ValueError, SyntaxError, NameError, TypeError, ZeroDivisionError) as exc:
            messagebox.showerror("Error", str(exc))

    def _limpiar(self):
        self.last_image = None

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = IntegracionDefinidaApp()
    app.run()
