"""
gauss_seidel_relajaciones.py

Implementacion de metodos iterativos para resolver sistemas lineales:
- Gauss-Seidel
- SOR (Successive Over-Relaxation / Relajacion)

Tambien incluye funciones para generar una hoja de calculo estilo examen:
- Tabla de iteraciones para Gauss-Seidel
- Cuadro base y registros T para Relajaciones
"""

import itertools
from typing import Any, Dict, List, Optional, Tuple


def _is_diagonal_dominant(A: List[List[float]]) -> bool:
    n = len(A)
    for i in range(n):
        diagonal = abs(A[i][i])
        off_diag_sum = sum(abs(A[i][j]) for j in range(n) if j != i)
        if diagonal < off_diag_sum:
            return False
    return True


def _check_square(A: List[List[float]], b: List[float]) -> None:
    n = len(A)
    if any(len(row) != n for row in A):
        raise ValueError("Matriz A debe ser cuadrada (n x n).")
    if len(b) != n:
        raise ValueError("Vector b debe tener longitud n.")


def _row_signature(row: List[float], rhs: float, decimals: int = 12) -> Tuple[float, ...]:
    return tuple(round(v, decimals) for v in row) + (round(rhs, decimals),)


def _reorder_rows_for_iterative_methods(
    A: List[List[float]], b: List[float]
) -> Tuple[List[List[float]], List[float], List[int]]:
    # Regla aplicada:
    # - En cada ecuacion (renglon), el pivote debe ser su coeficiente de mayor magnitud.
    # - Se busca una asignacion unica de renglones a variables (diagonal).
    # - Si no se puede, se detiene con error (regla de clase: "si no se cumple, no se puede").
    _check_square(A, b)
    n = len(A)

    if n <= 1:
        return [row.copy() for row in A], b.copy(), list(range(n))

    eps = 1e-14

    # Para cada renglon, columnas donde el coeficiente es maximo en magnitud.
    row_best_columns: List[List[int]] = []
    for i in range(n):
        row_max = abs(A[i][0])
        for j in range(1, n):
            cand = abs(A[i][j])
            if cand > row_max:
                row_max = cand
        if row_max <= eps:
            raise ValueError(
                "No se puede formar pivote: existe una ecuacion con todos los coeficientes en 0."
            )

        cols_i: List[int] = []
        for j in range(n):
            if abs(abs(A[i][j]) - row_max) <= eps:
                cols_i.append(j)
        row_best_columns.append(cols_i)

    best_perm: Optional[Tuple[int, ...]] = None
    best_signature: Optional[Tuple[Tuple[float, ...], ...]] = None

    for perm in itertools.permutations(range(n)):
        valid = True
        for j in range(n):
            row_idx = perm[j]
            if j not in row_best_columns[row_idx]:
                valid = False
                break
        if not valid:
            continue

        signature = tuple(_row_signature(A[idx], b[idx]) for idx in perm)
        if best_perm is None or signature < best_signature:
            best_perm = perm
            best_signature = signature

    if best_perm is None:
        raise ValueError(
            "No se puede formar una diagonal con pivote mayor en su linea para todas las variables. "
            "(Si no se cumple la regla de pivote mayor, no se puede continuar.)"
        )

    A_ordered = [A[idx].copy() for idx in best_perm]
    b_ordered = [b[idx] for idx in best_perm]
    return A_ordered, b_ordered, list(best_perm)


def _default_variable_names(n: int) -> List[str]:
    base = ["x", "y", "z", "t", "u", "v", "w"]
    if n <= len(base):
        return base[:n]
    extra = [f"x{i}" for i in range(len(base) + 1, n + 1)]
    return base + extra


def _fmt_number(value: float, decimals: int = 3) -> str:
    limit = 0.5 * (10 ** (-decimals))
    if abs(value) < limit:
        value = 0.0
    return f"{value:.{decimals}f}"


def _truncate_number(value: float, decimals: int) -> float:
    factor = 10 ** decimals
    if value >= 0:
        return int(value * factor) / factor
    return -int(abs(value) * factor) / factor


def _apply_step_precision(value: float, decimals: Optional[int]) -> float:
    if decimals is None:
        return value
    return _truncate_number(value, decimals)


def _num_expr(value: float, decimals: int = 6) -> str:
    if abs(value) < 1e-14:
        return "0"
    rounded = round(value)
    if abs(value - rounded) < 1e-12:
        return str(int(rounded))
    text = f"{value:.{decimals}f}".rstrip("0").rstrip(".")
    return "0" if text in {"-0", ""} else text


def _build_despejes_gauss_seidel(
    A: List[List[float]], b: List[float], var_names: List[str], decimals: int = 6
) -> List[str]:
    n = len(A)
    despejes: List[str] = []

    for i in range(n):
        diag = A[i][i]
        if abs(diag) < 1e-14:
            raise ZeroDivisionError(f"A[{i},{i}] es 0, no puede despejarse.")

        sign_factor = -1.0 if diag < 0 else 1.0
        diag_show = diag * sign_factor
        expr = _num_expr(b[i] * sign_factor, decimals)
        for j in range(n):
            if j == i:
                continue

            coeff = (-A[i][j]) * sign_factor
            if abs(coeff) < 1e-14:
                continue

            coeff_abs = abs(coeff)
            if abs(coeff_abs - 1.0) < 1e-12:
                term = var_names[j]
            else:
                term = f"{_num_expr(coeff_abs, decimals)}{var_names[j]}"

            if coeff > 0:
                expr += f" + {term}"
            else:
                expr += f" - {term}"

        despejes.append(f"{var_names[i]} = ({expr}) / {_num_expr(diag_show, decimals)}")

    return despejes


def _build_matrix_block(
    title: str,
    A: List[List[float]],
    b: List[float],
    var_names: List[str],
    decimals: int = 3,
) -> List[str]:
    n = len(A)
    lines: List[str] = [title]
    headers = ["Ecu", *var_names, "b"]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for i in range(n):
        row = [_roman(i + 1)]
        row.extend(_fmt_number(A[i][j], decimals) for j in range(n))
        row.append(_fmt_number(b[i], decimals))
        lines.append("| " + " | ".join(row) + " |")
    return lines


def _roman(num: int) -> str:
    romans = [
        "I",
        "II",
        "III",
        "IV",
        "V",
        "VI",
        "VII",
        "VIII",
        "IX",
        "X",
    ]
    if 1 <= num <= len(romans):
        return romans[num - 1]
    return str(num)


def gauss_seidel(
    A: List[List[float]],
    b: List[float],
    x0: List[float] = None,
    tol: float = 1e-8,
    max_iter: int = 100,
    verbose: bool = False,
) -> Tuple[List[float], int]:
    """Resuelve Ax = b usando el método de Gauss-Seidel."""
    _check_square(A, b)
    n = len(A)
    A_work, b_work, row_order = _reorder_rows_for_iterative_methods(A, b)

    if x0 is None:
        x = [0.0] * n
    else:
        if len(x0) != n:
            raise ValueError("x0 debe tener longitud n.")
        x = x0.copy()

    if row_order != list(range(n)) and verbose:
        print(
            "Info: ecuaciones reordenadas automaticamente para iterar "
            f"(nuevo orden usa renglones originales {[idx + 1 for idx in row_order]})."
        )

    if not _is_diagonal_dominant(A_work) and verbose:
        print("Advertencia: A no es diagonal dominante. Convergencia no garantizada.")

    for k in range(1, max_iter + 1):
        x_new = x.copy()

        for i in range(n):
            if abs(A_work[i][i]) < 1e-14:
                raise ZeroDivisionError(f"A[{i},{i}] es 0, no puede dividirse.")

            sum_before = sum(A_work[i][j] * x_new[j] for j in range(i))
            sum_after = sum(A_work[i][j] * x[j] for j in range(i + 1, n))
            x_new[i] = (b_work[i] - sum_before - sum_after) / A_work[i][i]

        err = max(abs(x_new[i] - x[i]) for i in range(n))

        if verbose:
            print(f"iter {k:3d}: x = {[round(v, 10) for v in x_new]}, Δ = {err:.3e}")

        x = x_new

        if err < tol:
            return x, k

    return x, max_iter


def gauss_seidel_hoja(
    A: List[List[float]],
    b: List[float],
    x0: Optional[List[float]] = None,
    tol: float = 1e-2,
    max_iter: int = 50,
    step_decimals: Optional[int] = 3,
) -> Dict[str, Any]:
    """Genera la hoja de calculo de Gauss-Seidel (V0, iteraciones y T)."""
    _check_square(A, b)
    n = len(A)
    A_work, b_work, row_order = _reorder_rows_for_iterative_methods(A, b)

    if x0 is None:
        x_prev = [0.0] * n
    else:
        if len(x0) != n:
            raise ValueError("x0 debe tener longitud n.")
        x_prev = x0.copy()

    values = [x_prev.copy()]  # V0, V1, V2, ...
    deltas: List[List[float]] = []
    checks: List[List[bool]] = []
    converged = False

    for _ in range(1, max_iter + 1):
        x_new = x_prev.copy()

        for i in range(n):
            if abs(A_work[i][i]) < 1e-14:
                raise ZeroDivisionError(f"A[{i},{i}] es 0, no puede dividirse.")

            sum_before = sum(A_work[i][j] * x_new[j] for j in range(i))
            sum_after = sum(A_work[i][j] * x_prev[j] for j in range(i + 1, n))
            raw_value = (b_work[i] - sum_before - sum_after) / A_work[i][i]
            x_new[i] = _apply_step_precision(raw_value, step_decimals)

        delta_iter = [
            _apply_step_precision(abs(x_new[i] - x_prev[i]), step_decimals)
            for i in range(n)
        ]
        check_iter = [delta <= (tol + 1e-12) for delta in delta_iter]

        values.append(x_new.copy())
        deltas.append(delta_iter)
        checks.append(check_iter)

        x_prev = x_new

        if all(check_iter):
            converged = True
            break

    return {
        "n": n,
        "tol": tol,
        "values": values,
        "deltas": deltas,
        "checks": checks,
        "iterations": len(checks),
        "converged": converged,
        "x": x_prev,
        "row_order": row_order,
        "A_input": [row.copy() for row in A],
        "b_input": b.copy(),
        "A_work": [row.copy() for row in A_work],
        "b_work": b_work.copy(),
    }


def obtener_despejes_gauss_seidel(
    reporte: Dict[str, Any], variable_names: Optional[List[str]] = None
) -> List[str]:
    """Devuelve ecuaciones despejadas de la hoja de Gauss-Seidel."""
    n = reporte["n"]
    var_names = variable_names or _default_variable_names(n)
    A_work = reporte.get("A_work")
    b_work = reporte.get("b_work")
    if A_work is None or b_work is None:
        return []
    return _build_despejes_gauss_seidel(A_work, b_work, var_names, decimals=6)


def formatear_hoja_gauss_seidel(
    reporte: Dict[str, Any],
    variable_names: Optional[List[str]] = None,
    decimals: int = 3,
) -> str:
    """Formatea la hoja de calculo de Gauss-Seidel en una tabla Markdown."""
    n = reporte["n"]
    values = reporte["values"]
    checks = reporte["checks"]
    iterations = reporte["iterations"]
    tol = reporte["tol"]
    converged = reporte["converged"]
    row_order = reporte.get("row_order", list(range(n)))
    A_input = reporte.get("A_input")
    b_input = reporte.get("b_input")
    A_work = reporte.get("A_work")
    b_work = reporte.get("b_work")

    var_names = variable_names or _default_variable_names(n)
    if len(var_names) < n:
        raise ValueError("variable_names no tiene suficientes nombres.")

    headers = ["Var", "V0"]
    for k in range(1, iterations + 1):
        headers.extend([f"{k}a", "T"])

    lines = []
    if A_input is not None and b_input is not None:
        lines.extend(_build_matrix_block("Matriz inicial (capturada)", A_input, b_input, var_names, decimals))
        lines.append("")

    if A_work is not None and b_work is not None:
        lines.extend(_build_matrix_block("Matriz ordenada por variables", A_work, b_work, var_names, decimals))
        lines.append("")

    if A_work is not None and b_work is not None:
        lines.append("Despejes (V de la D)")
        for eq in _build_despejes_gauss_seidel(A_work, b_work, var_names, decimals=6):
            lines.append(f"- {eq}")
        lines.append("")

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for i in range(n):
        row = [var_names[i], _fmt_number(values[0][i], decimals)]
        for k in range(iterations):
            row.append(_fmt_number(values[k + 1][i], decimals))
            row.append("OK" if checks[k][i] else "NO")
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append(f"Criterio: Tol >= |Va - Vn|, con Tol = {_fmt_number(tol, decimals)}")
    if converged:
        lines.append(f"Resultado: todas las variables cumplen en la iteracion {iterations}.")
    else:
        lines.append("Resultado: no todas las variables cumplieron dentro del maximo de iteraciones.")

    if row_order != list(range(n)):
        reorder_msg = ", ".join([f"E{i + 1}<-R{row_order[i] + 1}" for i in range(n)])
        lines.append(f"Reordenamiento automatico aplicado: {reorder_msg}")

    return "\n".join(lines)


def _normalizar_ecuaciones_relajaciones(
    A: List[List[float]], b: List[float], step_decimals: Optional[int]
) -> Tuple[List[List[float]], List[float], List[int]]:
    """Construye el cuadro base con diagonal -1 y residuo inicial R.

     Regla usada (adaptada para calculadora):
     1) Se reordenan automaticamente los renglones para que cada pivote diagonal
         sea el mayor coeficiente (en magnitud) de su variable/columna.
     2) Se toma el coeficiente diagonal como pivote de cada ecuacion.
    3) Se escala cada renglon para forzar diagonal = -1.

    Esto reduce la dependencia del orden en que el usuario capture las ecuaciones.
    """
    _check_square(A, b)
    n = len(A)
    A_ordered, b_ordered, row_order = _reorder_rows_for_iterative_methods(A, b)

    for i in range(n):
        pivot_coeff = A_ordered[i][i]
        if abs(pivot_coeff) < 1e-14:
            raise ValueError(f"No se puede normalizar el renglon {i + 1}: coeficiente pivote es 0.")

    base_A = [[0.0] * n for _ in range(n)]
    base_R = [0.0] * n
    source_row = row_order.copy()

    for i in range(n):
        scale = -1.0 / A_ordered[i][i]
        base_A[i] = [
            _apply_step_precision(A_ordered[i][j] * scale, step_decimals)
            for j in range(n)
        ]
        base_R[i] = _apply_step_precision(-b_ordered[i] * scale, step_decimals)

    return base_A, base_R, source_row


def relajaciones_hoja(
    A: List[List[float]],
    b: List[float],
    tol: float = 1e-2,
    max_iter: int = 50,
    step_decimals: Optional[int] = 3,
) -> Dict[str, Any]:
    """Genera cuadro base y registros T para el metodo de Relajaciones."""
    base_A, base_R, source_row = _normalizar_ecuaciones_relajaciones(A, b, step_decimals)
    n = len(A)

    residual = base_R.copy()
    x = [0.0] * n
    records: List[Dict[str, Any]] = []

    converged = max(abs(v) for v in residual) <= tol

    for _ in range(1, max_iter + 1):
        if converged:
            break

        pivot_idx = 0
        pivot_abs = abs(residual[0])
        for idx in range(1, n):
            cand = abs(residual[idx])
            if cand > pivot_abs:
                pivot_abs = cand
                pivot_idx = idx
        pivot_value = residual[pivot_idx]
        pivot_column = [base_A[i][pivot_idx] for i in range(n)]

        adjustments = [
            _apply_step_precision(pivot_value * pivot_column[i], step_decimals)
            for i in range(n)
        ]
        residual_next = [
            _apply_step_precision(residual[i] + adjustments[i], step_decimals)
            for i in range(n)
        ]

        x[pivot_idx] = _apply_step_precision(x[pivot_idx] + pivot_value, step_decimals)

        max_abs_after = max(abs(v) for v in residual_next)
        ok_after = max_abs_after <= tol

        records.append(
            {
                "pivot_index": pivot_idx,
                "pivot_value": pivot_value,
                "residual_before": residual.copy(),
                "column_coeffs": pivot_column,
                "adjustments": adjustments,
                "residual_after": residual_next.copy(),
                "x_after": x.copy(),
                "max_abs_after": max_abs_after,
                "ok_after": ok_after,
            }
        )

        residual = residual_next
        converged = ok_after

    return {
        "n": n,
        "tol": tol,
        "base_A": base_A,
        "base_R": base_R,
        "source_row": source_row,
        "records": records,
        "iterations": len(records),
        "converged": converged,
        "x": x,
        "residual": residual,
    }


def formatear_hoja_relajaciones(
    reporte: Dict[str, Any],
    variable_names: Optional[List[str]] = None,
    decimals: int = 3,
    max_registros: Optional[int] = None,
) -> str:
    """Formatea cuadro base y registros T en tabla Markdown."""
    n = reporte["n"]
    tol = reporte["tol"]
    base_A = reporte["base_A"]
    base_R = reporte["base_R"]
    records = reporte["records"]
    source_row = reporte.get("source_row", list(range(n)))

    var_names = variable_names or _default_variable_names(n)
    if len(var_names) < n:
        raise ValueError("variable_names no tiene suficientes nombres.")

    lines: List[str] = []
    lines.append("Cuadro base (diagonal = -1)")

    headers_base = ["Ecu", *var_names, "R"]
    lines.append("| " + " | ".join(headers_base) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers_base)) + " |")
    for i in range(n):
        row = [_roman(i + 1)]
        row.extend(_fmt_number(base_A[i][j], decimals) for j in range(n))
        row.append(_fmt_number(base_R[i], decimals))
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append("Registros T")
    lines.append("Formato: H_anterior, pivote*C_columna_pivote y H_nuevo (sumando por columna del pivote).")

    if source_row != list(range(n)):
        reorder_msg = ", ".join([f"E{i + 1}<-R{source_row[i] + 1}" for i in range(n)])
        lines.append(f"Reordenamiento automatico aplicado: {reorder_msg}")

    to_show = records if max_registros is None else records[:max_registros]
    for idx, rec in enumerate(to_show, start=1):
        piv_var = var_names[rec["pivot_index"]]
        piv_val = _fmt_number(rec["pivot_value"], decimals)
        lines.append(f"Iteracion {idx}: pivote {piv_var} = {piv_val}")
        var_headers = [f"{var_names[i]}/R{i+1}" for i in range(n)]
        lines.append("| Concepto | " + " | ".join(var_headers) + " |")
        lines.append("| " + " | ".join(["---"] * (n + 1)) + " |")
        lines.append(
            "| H_anterior | "
            + " | ".join(_fmt_number(v, decimals) for v in rec["residual_before"])
            + " |"
        )
        lines.append(
            "| C_col pivote | "
            + " | ".join(_fmt_number(v, decimals) for v in rec["column_coeffs"])
            + " |"
        )
        lines.append(
            "| pivote*Ccol | "
            + " | ".join(_fmt_number(v, decimals) for v in rec["adjustments"])
            + " |"
        )
        lines.append(
            "| H_nuevo | "
            + " | ".join(_fmt_number(v, decimals) for v in rec["residual_after"])
            + " |"
        )
        lines.append("")

    if max_registros is not None and len(records) > max_registros:
        lines.append(f"... {len(records) - max_registros} registro(s) omitidos ...")
        lines.append("")

    lines.append("Resumen por iteracion")
    headers_res = ["Iter", "Pivote", "Valor pivote", *[f"H_{v}" for v in var_names], "max|H|", "Tol"]
    lines.append("| " + " | ".join(headers_res) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers_res)) + " |")
    for idx, rec in enumerate(records, start=1):
        row = [
            str(idx),
            var_names[rec["pivot_index"]],
            _fmt_number(rec["pivot_value"], decimals),
            *[_fmt_number(v, decimals) for v in rec["residual_after"]],
            _fmt_number(rec["max_abs_after"], decimals),
            "OK" if rec["ok_after"] else "NO",
        ]
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    lines.append(f"Criterio: Tol >= |H_i| para todo i, con Tol = {_fmt_number(tol, decimals)}")
    if reporte["converged"]:
        lines.append(f"Resultado: residuos dentro de tolerancia en la iteracion {reporte['iterations']}.")
    else:
        lines.append("Resultado: no se alcanzo tolerancia en el maximo de iteraciones.")

    return "\n".join(lines)


def sor(
    A: List[List[float]],
    b: List[float],
    omega: float = 1.0,
    x0: List[float] = None,
    tol: float = 1e-8,
    max_iter: int = 100,
    verbose: bool = False,
) -> Tuple[List[float], int]:
    """Resuelve Ax = b usando SOR (relajación sucesiva)."""
    if not (0 < omega < 2):
        raise ValueError("Relaxación ω debe estar en (0, 2).")

    _check_square(A, b)
    n = len(A)
    A_work, b_work, _ = _reorder_rows_for_iterative_methods(A, b)

    if x0 is None:
        x = [0.0] * n
    else:
        if len(x0) != n:
            raise ValueError("x0 debe tener longitud n.")
        x = x0.copy()

    if not _is_diagonal_dominant(A_work) and verbose:
        print("Advertencia: A no es diagonal dominante. Convergencia no garantizada.")

    for k in range(1, max_iter + 1):
        x_new = x.copy()

        for i in range(n):
            if abs(A_work[i][i]) < 1e-14:
                raise ZeroDivisionError(f"A[{i},{i}] es 0, no puede dividirse.")

            sum_before = sum(A_work[i][j] * x_new[j] for j in range(i))
            sum_after = sum(A_work[i][j] * x[j] for j in range(i + 1, n))
            x_gs = (b_work[i] - sum_before - sum_after) / A_work[i][i]
            x_new[i] = (1 - omega) * x[i] + omega * x_gs

        err = max(abs(x_new[i] - x[i]) for i in range(n))

        if verbose:
            print(
                f"iter {k:3d}: x = {[round(v, 10) for v in x_new]}, Δ = {err:.3e}, ω = {omega}"
            )

        x = x_new

        if err < tol:
            return x, k

    return x, max_iter


def _ejemplo() -> None:
    A = [
        [4.0, -1.0, 0.0, 0.0],
        [-1.0, 4.0, -1.0, 0.0],
        [0.0, -1.0, 4.0, -1.0],
        [0.0, 0.0, -1.0, 3.0],
    ]
    b = [15.0, 10.0, 10.0, 10.0]
    x0 = [0.0, 0.0, 0.0, 0.0]

    print("== Gauss-Seidel ==")
    xs_gs, it_gs = gauss_seidel(A, b, x0=x0, tol=1e-10, max_iter=200, verbose=True)
    print(f"Solución GS: {xs_gs} en {it_gs} iteraciones\n")

    print("== Hoja Gauss-Seidel (Tol=0.01) ==")
    rep_gs = gauss_seidel_hoja(A, b, x0=x0, tol=1e-2, max_iter=25)
    print(formatear_hoja_gauss_seidel(rep_gs))
    print()

    print("== SOR ω=1.0 (Gauss-Seidel) ==")
    xs_sor1, it_sor1 = sor(A, b, omega=1.0, x0=x0, tol=1e-10, max_iter=200, verbose=True)
    print(f"Solución SOR(1.0): {xs_sor1} en {it_sor1} iteraciones\n")

    print("== SOR ω=1.25 ==")
    xs_sor125, it_sor125 = sor(A, b, omega=1.25, x0=x0, tol=1e-10, max_iter=200, verbose=True)
    print(f"Solución SOR(1.25): {xs_sor125} en {it_sor125} iteraciones\n")

    print("== Relajaciones (ejemplo 3x3 de apuntes) ==")
    A_rel = [
        [2.0, -5.0, 4.0],
        [-1.0, 3.0, -6.0],
        [-4.0, -1.0, -1.0],
    ]
    b_rel = [3.0, -5.0, -10.0]
    rep_rel = relajaciones_hoja(A_rel, b_rel, tol=1e-2, max_iter=30)
    print(formatear_hoja_relajaciones(rep_rel))


if __name__ == "__main__":
    _ejemplo()
