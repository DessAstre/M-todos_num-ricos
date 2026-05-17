"""Genera imágenes de todos los cuadros de la hoja de cálculo para el parcialito 3."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import numpy as np

try:
    from Parcial3.ajuste_curvas import (
        coeficientes_polinomio, rss, evaluar_polinomio,
        formato_ecuacion, normal_equations, sumas_ajuste,
        _solve_gauss_jordan, ssel_4x4_text,
    )
except ImportError:
    from ajuste_curvas import (  # type: ignore
        coeficientes_polinomio, rss, evaluar_polinomio,
        formato_ecuacion, normal_equations, sumas_ajuste,
        _solve_gauss_jordan, ssel_4x4_text,
    )

OUT = os.path.join(os.path.dirname(__file__), "capturas")
os.makedirs(OUT, exist_ok=True)

X = [-4, -3, -2, -1, 0, 1, 2]
Y = [-3, 11, 13, 9, 5, 7, 21]

COEF = {g: coeficientes_polinomio(X, Y, g) for g in [1, 2, 3]}
RSS  = {g: rss(X, Y, COEF[g]) for g in [1, 2, 3]}

HEADER_COLOR  = "#2c4a7c"
HEADER_TEXT   = "white"
ODD_COLOR     = "#f0f4fa"
EVEN_COLOR    = "white"
SUM_COLOR     = "#d6e4f0"
TITLE_COLOR   = "#1a2f50"

def _save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  guardado: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Datos de entrada
# ─────────────────────────────────────────────────────────────────────────────
def fig_datos():
    fig, ax = plt.subplots(figsize=(4.5, 3.4))
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(0.5, 0.97, "Datos de entrada", ha="center", va="top",
            fontsize=13, fontweight="bold", color=TITLE_COLOR,
            transform=ax.transAxes)

    rows = [["Punto", "X", "Y"]] + [[str(i+1), str(x), str(y)]
                                     for i, (x, y) in enumerate(zip(X, Y))]
    n_rows, n_cols = len(rows), 3
    col_w = [0.22, 0.22, 0.22]
    x0, y0, row_h = 0.08, 0.88, 0.08

    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cx = x0 + sum(col_w[:c]) + col_w[c] / 2
            cy = y0 - r * row_h
            bg = HEADER_COLOR if r == 0 else (ODD_COLOR if r % 2 else EVEN_COLOR)
            fc = HEADER_TEXT if r == 0 else "black"
            rect = plt.Rectangle(
                (x0 + sum(col_w[:c]) - 0.005, cy - row_h / 2 + 0.005),
                col_w[c] - 0.005, row_h - 0.005,
                transform=ax.transAxes, color=bg, zorder=0, clip_on=False
            )
            ax.add_patch(rect)
            ax.text(cx, cy, val, ha="center", va="center",
                    fontsize=10, color=fc, fontweight=("bold" if r == 0 else "normal"),
                    transform=ax.transAxes)

    _save(fig, "01_datos.png")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Tabla del procedimiento
# ─────────────────────────────────────────────────────────────────────────────
def fig_procedimiento():
    sumas = sumas_ajuste(X, Y, max_x_power=6, max_xy_power=3)
    headers = ["X", "Y", "X²", "X³", "X⁴", "X⁵", "X⁶", "XY", "X²Y", "X³Y"]

    def row_vals(x, y):
        return [x, y, x**2, x**3, x**4, x**5, x**6, x*y, x**2*y, x**3*y]

    data_rows = [row_vals(x, y) for x, y in zip(X, Y)]
    sum_row   = [sum(r[i] for r in data_rows) for i in range(len(headers))]

    n_data = len(data_rows)
    n_total = n_data + 2  # +header +sum
    n_cols = len(headers)
    col_w = 0.092
    row_h = 0.072
    fig_w = 11
    fig_h = 3.8

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(0.5, 0.97, "Tabla del procedimiento", ha="center", va="top",
            fontsize=12, fontweight="bold", color=TITLE_COLOR,
            transform=ax.transAxes)

    x0, y0 = 0.03, 0.87
    all_rows = [headers] + data_rows + [sum_row]
    labels   = [""] * (1 + n_data) + ["Σ"]

    for r, row in enumerate(all_rows):
        if r == 0:
            bg, fc, fw = HEADER_COLOR, HEADER_TEXT, "bold"
        elif r == len(all_rows) - 1:
            bg, fc, fw = SUM_COLOR, TITLE_COLOR, "bold"
        else:
            bg, fc, fw = (ODD_COLOR if r % 2 else EVEN_COLOR), "black", "normal"

        for c, val in enumerate(row):
            cx = x0 + c * col_w + col_w / 2
            cy = y0 - r * row_h
            rect = plt.Rectangle(
                (x0 + c * col_w, cy - row_h / 2 + 0.006),
                col_w - 0.003, row_h - 0.006,
                transform=ax.transAxes, color=bg, zorder=0, clip_on=False
            )
            ax.add_patch(rect)
            txt = val if isinstance(val, str) else f"{val:g}"
            ax.text(cx, cy, txt, ha="center", va="center",
                    fontsize=8.5, color=fc, fontweight=fw,
                    transform=ax.transAxes)

        # Etiqueta de fila
        if labels[r]:
            ax.text(x0 - 0.01, y0 - r * row_h, labels[r],
                    ha="right", va="center", fontsize=8.5,
                    color=TITLE_COLOR, fontweight="bold",
                    transform=ax.transAxes)

    _save(fig, "02_procedimiento.png")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Tabla de desviaciones
# ─────────────────────────────────────────────────────────────────────────────
def fig_desviaciones():
    headers = ["X", "Y", "Y₁", "(Y-Y₁)²", "Y₂ ⚠", "(Y-Y₂)²", "Y₃", "(Y-Y₃)²"]
    rows = []
    totals = [0.0, 0.0, 0.0]
    for x, y in zip(X, Y):
        r = [x, y]
        for g in [1, 2, 3]:
            yf = evaluar_polinomio(COEF[g], x)
            err = (y - yf) ** 2
            r += [yf, err]
            totals[g-1] += err
        rows.append(r)

    sum_row = ["", ""] + [v for t in totals for v in ("", f"{t:.4f}")]

    n_cols = len(headers)
    col_w  = 0.105
    row_h  = 0.072
    fig_w  = 10
    fig_h  = 4.2

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(0.5, 0.97, "Tabla de desviaciones", ha="center", va="top",
            fontsize=12, fontweight="bold", color=TITLE_COLOR,
            transform=ax.transAxes)
    # Warning note under title
    ax.text(0.5, 0.92,
            "⚠  Y₂ ≡ Y₁  porque K₂ = 0  (ajuste de 2do orden NO aporta información nueva)",
            ha="center", va="top", fontsize=9, color="#b85c00",
            fontweight="bold", transform=ax.transAxes)

    # Columns 4-5 (Y₂ and (Y-Y₂)²) are highlighted in orange to signal they are redundant
    WARN_COLOR = "#fff3cd"

    x0, y0 = 0.02, 0.83
    all_rows = [headers] + rows + [sum_row]

    for r_idx, row in enumerate(all_rows):
        if r_idx == 0:
            base_bg, fc, fw = HEADER_COLOR, HEADER_TEXT, "bold"
        elif r_idx == len(all_rows) - 1:
            base_bg, fc, fw = SUM_COLOR, TITLE_COLOR, "bold"
        else:
            base_bg, fc, fw = (ODD_COLOR if r_idx % 2 else EVEN_COLOR), "black", "normal"

        for c, val in enumerate(row):
            cx = x0 + c * col_w + col_w / 2
            cy = y0 - r_idx * row_h
            # Highlight Y₂ columns
            if c in (4, 5):
                bg = "#e8891a" if r_idx == 0 else WARN_COLOR
                txt_color = "white" if r_idx == 0 else "#7a4500"
            else:
                bg = base_bg
                txt_color = fc
            rect = plt.Rectangle(
                (x0 + c * col_w, cy - row_h / 2 + 0.006),
                col_w - 0.003, row_h - 0.006,
                transform=ax.transAxes, color=bg, zorder=0, clip_on=False
            )
            ax.add_patch(rect)
            if isinstance(val, str):
                txt = val
            elif isinstance(val, float) and val != 0:
                txt = f"{val:.4f}"
            elif isinstance(val, (int, float)):
                txt = f"{val:g}"
            else:
                txt = str(val)
            ax.text(cx, cy, txt, ha="center", va="center",
                    fontsize=8.5, color=txt_color, fontweight=fw,
                    transform=ax.transAxes)

    _save(fig, "03_desviaciones.png")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Gráfica
# ─────────────────────────────────────────────────────────────────────────────
def fig_grafica():
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("white")

    xs = np.linspace(-5.5, 3.5, 400)
    colors = ["#e07b39", "#2d7abf", "#1fa347"]
    styles = ["--", "-.", "-"]

    for g, color, ls in zip([1, 2, 3], colors, styles):
        ys = [evaluar_polinomio(COEF[g], xi) for xi in xs]
        label = f"Y{g} = {formato_ecuacion(COEF[g])}  (RSS={RSS[g]:.4f})"
        ax.plot(xs, ys, color=color, linestyle=ls, linewidth=1.8, label=label)

    ax.scatter(X, Y, color="black", zorder=5, s=60, label="Datos originales")
    for xi, yi in zip(X, Y):
        ax.annotate(f"({xi},{yi})", (xi, yi), textcoords="offset points",
                    xytext=(5, 6), fontsize=8, color="#333")

    ax.set_title("Ajuste de curvas por mínimos cuadrados", fontsize=13,
                 fontweight="bold", color=TITLE_COLOR)
    ax.set_xlabel("x", fontsize=11)
    ax.set_ylabel("y", fontsize=11)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(True, alpha=0.35)
    ax.set_xlim(-5.5, 3.5)
    ax.set_ylim(-50, 90)

    fig.tight_layout()
    _save(fig, "04_grafica.png")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Evaluación exacta
# ─────────────────────────────────────────────────────────────────────────────
def fig_evaluacion():
    requested = [-5, 3, 4, 5]
    best_coef = COEF[3]

    fig, ax = plt.subplots(figsize=(4.5, 2.8))
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(0.5, 0.97, "Evaluación exacta  (Y₃ = 5 − 2x + 3x² + x³)",
            ha="center", va="top", fontsize=11, fontweight="bold",
            color=TITLE_COLOR, transform=ax.transAxes)

    rows = [["X", "Y₃(x)"]] + [[str(xv), f"{evaluar_polinomio(best_coef, xv):.6f}"]
                                 for xv in requested]
    col_w = [0.25, 0.35]
    x0, y0, row_h = 0.2, 0.84, 0.11

    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cx = x0 + sum(col_w[:c]) + col_w[c] / 2
            cy = y0 - r * row_h
            bg = HEADER_COLOR if r == 0 else (ODD_COLOR if r % 2 else EVEN_COLOR)
            fc = HEADER_TEXT if r == 0 else "black"
            rect = plt.Rectangle(
                (x0 + sum(col_w[:c]), cy - row_h / 2 + 0.01),
                col_w[c] - 0.005, row_h - 0.01,
                transform=ax.transAxes, color=bg, zorder=0, clip_on=False
            )
            ax.add_patch(rect)
            ax.text(cx, cy, val, ha="center", va="center",
                    fontsize=10.5, color=fc,
                    fontweight=("bold" if r == 0 else "normal"),
                    transform=ax.transAxes)

    _save(fig, "05_evaluacion.png")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Incisos (resumen)
# ─────────────────────────────────────────────────────────────────────────────
def fig_incisos():
    # (is_bold, text, fontsize, color_override)
    WARN = "#b85c00"
    lines = [
        (True,  "Resultados — Incisos", 13, None),
        (False, "", 4, None),
        (True,  "a)  Y₁ = 11.000000 + 2.000000·x", 11, None),
        (False, "    S₁ = RSS₁ = 216.000000", 10, None),
        (False, "", 4, None),
        (True,  "b)  Y₂ = 11.000000 + 2.000000·x + 0.000000·x²", 11, WARN),
        (False, "    ⚠ K₂ = 0  →  Y₂ ≡ Y₁.  El ajuste de 2do orden NO es posible:", 10, WARN),
        (False, "       no aporta información nueva.  S₂ = 216.000000  (= S₁)", 10, WARN),
        (False, "", 4, None),
        (True,  "c)  Y₃ = 5.000000 − 2.000000·x + 3.000000·x² + 1.000000·x³", 11, None),
        (False, "    S₃ = RSS₃ = 0.000000  ← ajuste EXACTO", 10, "#1a7a3c"),
        (False, "", 4, None),
        (True,  "d)  Comparación (Y₂ descartada por K₂ = 0):", 11, None),
        (False, "    S₁ = 216  vs  S₃ = 0  →  Se elige Y₃", 10, None),
        (False, "    Y₃ pasa exactamente por los 7 puntos.", 10, None),
        (False, "", 4, None),
        (True,  "e)  Valores solicitados (usando Y₃):", 11, None),
        (False, "    x = -5  →  y = -35.000000", 10, None),
        (False, "    x =  3  →  y =  53.000000", 10, None),
        (False, "    x =  4  →  y = 109.000000", 10, None),
        (False, "    x =  5  →  y = 195.000000", 10, None),
    ]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # Orange warning band behind inciso b lines
    warn_y_top = 0.96 - 4 * (11 * 0.013 + 0.01) - 0.02 - 0.005
    warn_height = 3 * (10 * 0.013 + 0.01) + 0.015
    warn_rect = plt.Rectangle((0.01, warn_y_top - warn_height),
                               0.97, warn_height + 0.005,
                               transform=ax.transAxes,
                               color="#fff3cd", zorder=0, clip_on=False)
    ax.add_patch(warn_rect)

    y_cur = 0.96
    for is_bold, txt, fs, color_ov in lines:
        if not txt:
            y_cur -= 0.02
            continue
        fw = "bold" if is_bold else "normal"
        color = color_ov if color_ov else (TITLE_COLOR if is_bold else "#222")
        ax.text(0.04, y_cur, txt, ha="left", va="top",
                fontsize=fs, fontweight=fw, color=color,
                transform=ax.transAxes,
                fontfamily="monospace" if not is_bold else "sans-serif")
        y_cur -= fs * 0.013 + 0.01

    _save(fig, "06_incisos.png")


# ─────────────────────────────────────────────────────────────────────────────
# 7. SSELS 4×4 con Gauss-Jordan
# ─────────────────────────────────────────────────────────────────────────────
def fig_ssels():
    A, b = normal_equations(X, Y, 3)
    headers = ["K₀", "K₁", "K₂", "K₃", "b"]

    # Initial augmented matrix
    init_rows = [[A[i][j] for j in range(4)] + [b[i]] for i in range(4)]

    # Gauss-Jordan steps (collect each pivot step)
    M = [row[:] for row in A]
    c = b[:]
    steps = []  # list of (label, matrix_snapshot)

    for k in range(4):
        # pivot selection
        pivot = max(range(k, 4), key=lambda i: abs(M[i][k]))
        if pivot != k:
            M[k], M[pivot] = M[pivot], M[k]
            c[k], c[pivot] = c[pivot], c[k]
        pv = M[k][k]
        M[k] = [v / pv for v in M[k]]
        c[k] /= pv
        for i in range(4):
            if i == k:
                continue
            f = M[i][k]
            c[i] -= f * c[k]
            M[i] = [M[i][j] - f * M[k][j] for j in range(4)]
        steps.append((f"Paso {k+1}: pivote columna {k}",
                      [[M[i][j] for j in range(4)] + [c[i]] for i in range(4)]))

    sol = c[:]

    # Draw figure
    n_matrices = 1 + len(steps)  # initial + each step
    fig_h = 2.4 * n_matrices
    fig, axes = plt.subplots(n_matrices, 1, figsize=(10, fig_h))
    if n_matrices == 1:
        axes = [axes]
    fig.patch.set_facecolor("white")
    fig.suptitle("SSELS 4×4 — Eliminación de Gauss-Jordan", fontsize=12,
                 fontweight="bold", color=TITLE_COLOR, y=1.0)

    matrix_sets = [("Matriz aumentada inicial [A|b]", init_rows)] + list(steps)

    for ax, (label, mat) in zip(axes, matrix_sets):
        ax.axis("off")
        ax.text(0.02, 0.95, label, transform=ax.transAxes,
                fontsize=10, fontweight="bold", color=TITLE_COLOR, va="top")

        n_rows, n_cols = 4, 5
        col_w = 0.17
        row_h = 0.19
        x0, y0 = 0.05, 0.75

        for r in range(n_rows + 1):
            for c in range(n_cols):
                cx = x0 + c * col_w + col_w / 2
                cy = y0 - r * row_h

                if r == 0:
                    bg, fc, fw = HEADER_COLOR, HEADER_TEXT, "bold"
                    txt = headers[c]
                else:
                    val = mat[r-1][c]
                    bg = (ODD_COLOR if r % 2 else EVEN_COLOR)
                    # highlight last column
                    if c == n_cols - 1:
                        bg = "#e8f5e9"
                    fc, fw = "black", "normal"
                    txt = f"{val:.4f}"

                rect = plt.Rectangle(
                    (x0 + c * col_w + 0.002, cy - row_h / 2 + 0.02),
                    col_w - 0.004, row_h - 0.03,
                    transform=ax.transAxes, color=bg, zorder=0, clip_on=False
                )
                ax.add_patch(rect)
                ax.text(cx, cy, txt, ha="center", va="center",
                        fontsize=9, color=fc, fontweight=fw,
                        transform=ax.transAxes)

    # Solution row at bottom of last axis
    ax_last = axes[-1]
    sol_txt = "  →  Solución:  " + "   ".join(
        f"K{i} = {v:.6f}" for i, v in enumerate(sol))
    ax_last.text(0.05, -0.08, sol_txt, transform=ax_last.transAxes,
                 fontsize=10, fontweight="bold", color="#1a7a3c", va="top",
                 fontfamily="monospace")

    fig.tight_layout(rect=[0, 0, 1, 0.99])
    _save(fig, "07_ssels.png")


# ─────────────────────────────────────────────────────────────────────────────
# 8. Sistema normal (ecuaciones normales)
# ─────────────────────────────────────────────────────────────────────────────
def fig_sistema_normal():
    sumas = sumas_ajuste(X, Y, max_x_power=6, max_xy_power=3)

    labels_sumas = [
        ("n", sumas["n"]),
        ("Σx", sumas["sum_x"]),
        ("Σy", sumas["sum_y"]),
        ("Σx²", sumas["sum_x2"]),
        ("Σx³", sumas["sum_x3"]),
        ("Σx⁴", sumas["sum_x4"]),
        ("Σx⁵", sumas["sum_x5"]),
        ("Σx⁶", sumas["sum_x6"]),
        ("Σxy", sumas["sum_xy"]),
        ("Σx²y", sumas["sum_x2y"]),
        ("Σx³y", sumas["sum_x3y"]),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    fig.patch.set_facecolor("white")
    fig.suptitle("Sistema normal — Ecuaciones normales (grado 3)",
                 fontsize=12, fontweight="bold", color=TITLE_COLOR)

    # Left: sumas table
    ax = axes[0]
    ax.axis("off")
    ax.text(0.5, 0.97, "Sumas necesarias", ha="center", va="top",
            fontsize=11, fontweight="bold", color=TITLE_COLOR,
            transform=ax.transAxes)

    col_w = [0.42, 0.38]
    x0, y0, row_h = 0.06, 0.86, 0.075
    for r, (lbl, val) in enumerate([("Sumatoria", "Valor")] + labels_sumas):
        for c, txt in enumerate([lbl, (str(val) if r == 0 else f"{val:g}")]):
            cx = x0 + sum(col_w[:c]) + col_w[c] / 2
            cy = y0 - r * row_h
            bg = HEADER_COLOR if r == 0 else (ODD_COLOR if r % 2 else EVEN_COLOR)
            fc = HEADER_TEXT if r == 0 else "black"
            rect = plt.Rectangle(
                (x0 + sum(col_w[:c]), cy - row_h / 2 + 0.005),
                col_w[c] - 0.003, row_h - 0.005,
                transform=ax.transAxes, color=bg, zorder=0, clip_on=False
            )
            ax.add_patch(rect)
            ax.text(cx, cy, txt, ha="center", va="center",
                    fontsize=9, color=fc,
                    fontweight=("bold" if r == 0 else "normal"),
                    transform=ax.transAxes)

    # Right: normal equations matrix
    ax2 = axes[1]
    ax2.axis("off")
    ax2.text(0.5, 0.97, "Ecuaciones normales A·K = b", ha="center", va="top",
             fontsize=11, fontweight="bold", color=TITLE_COLOR,
             transform=ax2.transAxes)

    A, b_vec = normal_equations(X, Y, 3)
    hdrs = ["K₀", "K₁", "K₂", "K₃", "b"]
    mat = [[A[i][j] for j in range(4)] + [b_vec[i]] for i in range(4)]

    col_w2 = 0.175
    row_h2 = 0.13
    x02, y02 = 0.04, 0.84

    for r in range(5):
        for c in range(5):
            cx = x02 + c * col_w2 + col_w2 / 2
            cy = y02 - r * row_h2
            if r == 0:
                bg, fc, fw = HEADER_COLOR, HEADER_TEXT, "bold"
                txt = hdrs[c]
            else:
                val = mat[r-1][c]
                bg = (ODD_COLOR if r % 2 else EVEN_COLOR)
                if c == 4:
                    bg = "#e8f5e9"
                fc, fw = "black", "normal"
                txt = f"{val:g}"
            rect = plt.Rectangle(
                (x02 + c * col_w2 + 0.003, cy - row_h2 / 2 + 0.01),
                col_w2 - 0.006, row_h2 - 0.015,
                transform=ax2.transAxes, color=bg, zorder=0, clip_on=False
            )
            ax2.add_patch(rect)
            ax2.text(cx, cy, txt, ha="center", va="center",
                     fontsize=9, color=fc, fontweight=fw,
                     transform=ax2.transAxes)

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    _save(fig, "08_sistema_normal.png")


if __name__ == "__main__":
    print("Generando capturas...")
    fig_datos()
    fig_procedimiento()
    fig_desviaciones()
    fig_grafica()
    fig_evaluacion()
    fig_incisos()
    fig_ssels()
    fig_sistema_normal()
    print("Listo. Todas las imágenes guardadas en:", OUT)
