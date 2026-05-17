"""Módulo de métodos exactos para resolver Sistemas de Ecuaciones Lineales.

Incluye:
- Eliminación Gaussiana (con sustitución regresiva)
- Gauss-Jordan (reducción a forma escalonada reducida)
- Inversa de Matriz (A⁻¹·b)

Cada función recibe la matriz aumentada como lista de listas y un callback
``logger`` para imprimir cada paso del procedimiento.
"""

import copy
import math
from decimal import Decimal, localcontext


# =====================================================================
#  Utilidades
# =====================================================================

def _redondear(valor, cifras, modo):
    """Redondea (modo 'D') o trunca (modo 'T') a *cifras* decimales."""
    if modo == "T":
        factor = 10 ** cifras
        if valor >= 0:
            return math.floor(valor * factor) / factor
        else:
            return math.ceil(valor * factor) / factor
    return round(valor, cifras)


def _fmt(valor, cifras):
    """Formatea un número para visualización con *cifras* decimales."""
    return f"{valor:.{cifras}f}"


def _copiar_matriz(m):
    """Devuelve una copia profunda de la matriz."""
    return copy.deepcopy(m)


def _validar_matriz(matrix, n):
    """Valida que la matriz aumentada tenga dimensiones correctas.

    Devuelve ``True`` si es válida, de lo contrario lanza ``ValueError``.
    """
    if len(matrix) != n:
        raise ValueError(
            f"Se esperaban {n} filas, se recibieron {len(matrix)}."
        )
    for i, fila in enumerate(matrix):
        if len(fila) != n + 1:
            raise ValueError(
                f"Fila {i + 1} tiene {len(fila)} columnas; se esperaban {n + 1}."
            )
    return True


def _format_matrix_lines(matrix, cifras, sep_index=None):
    """Devuelve las líneas de texto de una matriz con columnas alineadas.

    Cuando *sep_index* no es None, se agrega un separador vertical `|` entre
    las columnas `sep_index - 1` y `sep_index` (útil para matrices aumentadas).
    """
    if not matrix:
        return []

    # Determinar el número máximo de columnas (por si hay filas irregulares).
    n_cols = max(len(row) for row in matrix)

    # Formatear valores y calcular anchos por columna.
    formatted = []
    for row in matrix:
        formatted.append([_fmt(row[j], cifras) if j < len(row) else "" for j in range(n_cols)])

    col_widths = [0] * n_cols
    for row in formatted:
        for j, val in enumerate(row):
            col_widths[j] = max(col_widths[j], len(val))

    lines = []
    for row in formatted:
        padded = [row[j].rjust(col_widths[j]) for j in range(n_cols)]
        if sep_index is not None and 0 < sep_index < n_cols:
            left = " ".join(padded[:sep_index])
            right = " ".join(padded[sep_index:])
            lines.append(f"  [ {left} | {right} ]")
        else:
            lines.append(f"  [ {' '.join(padded)} ]")
    return lines


def _imprimir_matriz(matrix, cifras, logger, titulo=None):
    """Imprime la matriz aumentada con un estilo de matriz alineada."""
    if titulo:
        logger(titulo)
    if not matrix:
        logger("")
        return
    sep_index = len(matrix[0]) - 1 if matrix and len(matrix[0]) > 1 else None
    for line in _format_matrix_lines(matrix, cifras, sep_index=sep_index):
        logger(line)
    logger("")


def _imprimir_matriz_cuadrada(matrix, cifras, logger, titulo=None):
    """Imprime una matriz cuadrada (sin columna b)."""
    if titulo:
        logger(titulo)
    for line in _format_matrix_lines(matrix, cifras, sep_index=None):
        logger(line)
    logger("")


def _imprimir_matriz_extendida(matrix, n, cifras, logger, titulo=None):
    """Imprime la matriz extendida [A | I] de tamaño n × 2n."""
    if titulo:
        logger(titulo)
    for line in _format_matrix_lines(matrix, cifras, sep_index=n):
        logger(line)
    logger("")


def _matriz_menor(matrix, fila, col):
    """Devuelve la submatriz sin la fila y columna especificadas."""
    return [
        [valor for j, valor in enumerate(row) if j != col]
        for i, row in enumerate(matrix) if i != fila
    ]


def _determinante(matrix, cifras, modo):
    """Calcula el determinante de una matriz cuadrada (método recursivo)."""
    n = len(matrix)
    if n == 0:
        return 1.0

    rd_out = lambda v: _redondear(v, cifras, modo)

    if n == 1:
        return rd_out(matrix[0][0])

    if n == 2:
        return rd_out(matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0])

    det = 0.0
    for j in range(n):
        signo = -1.0 if j % 2 else 1.0
        sub = _matriz_menor(matrix, 0, j)
        det = rd_out(det + rd_out(signo * matrix[0][j] * _determinante(sub, cifras, modo)))
    return det


def _matriz_cofactores(matrix, cifras, modo):
    """Devuelve la matriz de cofactores de una matriz cuadrada."""
    n = len(matrix)
    rd_out = lambda v: _redondear(v, cifras, modo)
    cofactores = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            menor = _matriz_menor(matrix, i, j)
            signo = -1.0 if (i + j) % 2 else 1.0
            cofactores[i][j] = rd_out(signo * _determinante(menor, cifras, modo))
    return cofactores


# =====================================================================
#  Eliminación Gaussiana
# =====================================================================

def gauss(matrix, cifras, modo, logger):
    """Resuelve el sistema por Eliminación Gaussiana con pivoteo parcial.

    Parameters
    ----------
    matrix : list[list[float]]
        Matriz aumentada [A|b] de tamaño n × (n+1).
    cifras : int
        Número de cifras decimales.
    modo : str
        'D' para redondear, 'T' para truncar.
    logger : callable
        Función callback para imprimir cada línea del procedimiento.
    """
    m = _copiar_matriz(matrix)
    n = len(m)
    _validar_matriz(m, n)

    # Internamente usamos float de doble precisión y aplicamos redondeo/truncado
    # únicamente al mostrar resultados finales. Esto estabiliza el resultado entre
    # diferentes metodologías (Gauss vs Inversa) al evitar redondeos acumulados.
    rd_out = lambda v: _redondear(v, cifras, modo)

    logger("=" * 70)
    logger("  ELIMINACIÓN GAUSSIANA")
    logger("=" * 70)
    _imprimir_matriz(m, cifras, logger, "\nMatriz aumentada inicial [A|b]:")

    # --- Triangulación ---
    logger("─" * 70)
    logger("FASE 1: Triangulación (eliminación hacia adelante)")
    logger("─" * 70)

    for k in range(n - 1):
        # Pivoteo parcial
        max_val = abs(m[k][k])
        max_row = k
        for i in range(k + 1, n):
            if abs(m[i][k]) > max_val:
                max_val = abs(m[i][k])
                max_row = i
        if max_row != k:
            m[k], m[max_row] = m[max_row], m[k]
            logger(f"  ↔ Intercambio F{k + 1} ↔ F{max_row + 1} (pivoteo parcial)")
            _imprimir_matriz(m, cifras, logger)

        if abs(m[k][k]) < 1e-12:
            raise ValueError(
                f"El sistema es singular (pivote ≈ 0 en columna {k + 1})."
            )

        logger(f"  Pivote en posición ({k + 1},{k + 1}) = {_fmt(m[k][k], cifras)}")

        for i in range(k + 1, n):
            if m[i][k] == 0:
                continue
            factor = m[i][k] / m[k][k]
            logger(f"  m({i + 1},{k + 1}) = {_fmt(m[i][k], cifras)} / {_fmt(m[k][k], cifras)} = {_fmt(factor, cifras)}")
            logger(f"  F{i + 1} = F{i + 1} - ({_fmt(factor, cifras)}) × F{k + 1}")
            for j in range(k, n + 1):
                m[i][j] = m[i][j] - factor * m[k][j]
            line = _format_matrix_lines([m[i]], cifras, sep_index=n)[0].strip()
            logger(f"  → F{i + 1} = {line}")
            logger("")

        _imprimir_matriz(m, cifras, logger, f"Matriz después de eliminar columna {k + 1}:")

    # --- Sustitución regresiva ---
    logger("─" * 70)
    logger("FASE 2: Sustitución regresiva")
    logger("─" * 70)

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        suma = sum(m[i][j] * x[j] for j in range(i + 1, n))
        x[i] = (m[i][n] - suma) / m[i][i]

        # Mostrar detalle (usamos valores con redondeo para mostrar, pero no para calcular)
        terminos = " - ".join(
            f"({_fmt(m[i][j], cifras)}×{_fmt(rd_out(x[j]), cifras)})"
            for j in range(i + 1, n)
        )
        if terminos:
            logger(f"  x{i + 1} = ({_fmt(m[i][n], cifras)} - {terminos}) / {_fmt(m[i][i], cifras)}")
        else:
            logger(f"  x{i + 1} = {_fmt(m[i][n], cifras)} / {_fmt(m[i][i], cifras)}")

        x_rounded = rd_out(x[i])
        logger(f"  x{i + 1} = {_fmt(x_rounded, cifras)}")
        logger("")

    # Redondear el resultado final para que sea consistente con el formato mostrado
    x = [rd_out(xi) for xi in x]

    logger("=" * 70)
    logger("  SOLUCIÓN FINAL")
    logger("=" * 70)
    for i in range(n):
        logger(f"  x{i + 1} = {_fmt(x[i], cifras)}")
    logger("")

    return x


# =====================================================================
#  Gauss-Jordan
# =====================================================================

def gauss_jordan(matrix, cifras, modo, logger):
    """Resuelve el sistema por el método de Gauss-Jordan.

    Parameters
    ----------
    matrix : list[list[float]]
        Matriz aumentada [A|b] de tamaño n × (n+1).
    cifras : int
        Número de cifras decimales.
    modo : str
        'D' para redondear, 'T' para truncar.
    logger : callable
        Función callback para imprimir cada línea del procedimiento.
    """
    m = _copiar_matriz(matrix)
    n = len(m)
    _validar_matriz(m, n)

    # Internamente usamos float de doble precisión y solo aplicamos redondeo/truncado
    # al mostrar resultados finales. Esto ayuda a que los distintos métodos entreguen
    # los mismos resultados cuando se usan las mismas cifras.
    rd_out = lambda v: _redondear(v, cifras, modo)

    logger("=" * 70)
    logger("  MÉTODO DE GAUSS-JORDAN")
    logger("=" * 70)
    _imprimir_matriz(m, cifras, logger, "\nMatriz aumentada inicial [A|b]:")

    for k in range(n):
        logger("─" * 70)
        logger(f"PASO {k + 1}: Pivote en posición ({k + 1},{k + 1})")
        logger("─" * 70)

        # Pivoteo parcial
        max_val = abs(m[k][k])
        max_row = k
        for i in range(k + 1, n):
            if abs(m[i][k]) > max_val:
                max_val = abs(m[i][k])
                max_row = i
        if max_row != k:
            m[k], m[max_row] = m[max_row], m[k]
            logger(f"  ↔ Intercambio F{k + 1} ↔ F{max_row + 1} (pivoteo parcial)")
            _imprimir_matriz(m, cifras, logger)

        if abs(m[k][k]) < 1e-12:
            raise ValueError(
                f"El sistema es singular (pivote ≈ 0 en columna {k + 1})."
            )

        # Normalizar fila pivote
        pivote = m[k][k]
        logger(f"  Normalizar F{k + 1}: F{k + 1} = F{k + 1} / {_fmt(pivote, cifras)}")
        for j in range(n + 1):
            m[k][j] = m[k][j] / pivote
        line = _format_matrix_lines([m[k]], cifras, sep_index=n)[0].strip()
        logger(f"  → F{k + 1} = {line}")
        logger("")

        # Eliminar en todas las demás filas (arriba y abajo)
        for i in range(n):
            if i == k:
                continue
            if m[i][k] == 0:
                continue
            factor = m[i][k]
            logger(f"  F{i + 1} = F{i + 1} - ({_fmt(factor, cifras)}) × F{k + 1}")
            for j in range(n + 1):
                m[i][j] = m[i][j] - factor * m[k][j]
            line = _format_matrix_lines([m[i]], cifras, sep_index=n)[0].strip()
            logger(f"  → F{i + 1} = {line}")
            logger("")

        _imprimir_matriz(m, cifras, logger, f"Matriz después del paso {k + 1}:")

    # Solución (redondeamos/truncamos al final para mantener consistencia)
    x = [m[i][n] for i in range(n)]
    x = [rd_out(xi) for xi in x]

    logger("=" * 70)
    logger("  SOLUCIÓN FINAL")
    logger("=" * 70)
    for i in range(n):
        logger(f"  x{i + 1} = {_fmt(x[i], cifras)}")
    logger("")

    return x


# =====================================================================
#  Inversa de Matriz
# =====================================================================

def inversa_gauss(matrix, cifras, modo, logger, mostrar_solucion=True):
    """Calcula la inversa de A usando el método de Eliminación Gaussiana.

    Se resuelve A·x = e_i para cada vector canónico e_i (columna i de I),
    construyendo así la matriz inversa A⁻¹. Finalmente se multiplica A⁻¹·b.

    Parameters
    ----------
    mostrar_solucion : bool
        Si es True, muestra el cálculo de x = A⁻¹·b y la solución final.
    """
    n = len(matrix)
    _validar_matriz(matrix, n)

    # Internamente usamos float de doble precisión y solo aplicamos redondeo/truncado
    # en los resultados finales. Esto ayuda a que Gauss e Inversa concuerden.
    rd_out = lambda v: _redondear(v, cifras, modo)

    # Separar A y b
    A = [[matrix[i][j] for j in range(n)] for i in range(n)]
    b = [matrix[i][n] for i in range(n)]

    logger("=" * 70)
    logger("  MÉTODO DE LA INVERSA DE MATRIZ (A⁻¹·b) - GAUSS")
    logger("=" * 70)
    _imprimir_matriz_cuadrada(A, cifras, logger, "\nMatriz A:")
    logger("Vector b:")
    logger(f"  [{', '.join(_fmt(bi, cifras) for bi in b)}]")
    logger("")

    # Calcular A⁻¹ resolviendo A·x = e_i para cada columna i
    A_inv = [[0.0] * n for _ in range(n)]
    for col in range(n):
        e = [1.0 if i == col else 0.0 for i in range(n)]
        logger("─" * 70)
        logger(f"Resolviendo A·x = e{col + 1} (columna {col + 1} de I)")
        logger("─" * 70)
        aug = [A[i] + [e[i]] for i in range(n)]
        x = gauss(aug, cifras, modo, logger)

        for i in range(n):
            A_inv[i][col] = x[i]

    _imprimir_matriz_cuadrada(A_inv, cifras, logger, "Matriz A⁻¹:")

    if mostrar_solucion:
        # Multiplicar A⁻¹ · b
        logger("─" * 70)
        logger("Cálculo de x = A⁻¹ · b")
        logger("─" * 70)

        x = [0.0] * n
        for i in range(n):
            suma = 0.0
            terminos = []
            for j in range(n):
                prod = A_inv[i][j] * b[j]
                suma += prod
                terminos.append(f"({_fmt(A_inv[i][j], cifras)} × {_fmt(b[j], cifras)})")
            x[i] = suma
            x_rounded = rd_out(x[i])
            logger(f"  x{i + 1} = {' + '.join(terminos)}")
            logger(f"  x{i + 1} = {_fmt(x_rounded, cifras)}")
            logger("")

        # Redondear el resultado final para que sea consistente con lo mostrado
        x = [rd_out(xi) for xi in x]

        logger("=" * 70)
        logger("  SOLUCIÓN FINAL")
        logger("=" * 70)
        for i in range(n):
            logger(f"  x{i + 1} = {_fmt(x[i], cifras)}")
        logger("")
    else:
        # Aún calculamos x para devolverlo, pero no lo mostramos.
        x = [0.0] * n
        for i in range(n):
            suma = 0.0
            for j in range(n):
                suma += A_inv[i][j] * b[j]
            x[i] = suma
        x = [rd_out(xi) for xi in x]

    return x


def inversa_gauss_jordan(matrix, cifras, modo, logger, mostrar_solucion=True):
    """Resuelve el sistema calculando A⁻¹ y multiplicando A⁻¹·b usando Gauss-Jordan.

    Este es el método clásico que extiende A con la identidad y reduce con
    Gauss-Jordan para obtener [I | A⁻¹].

    Parameters
    ----------
    mostrar_solucion : bool
        Si es True, muestra el cálculo de x = A⁻¹·b y la solución final.
    """
    n = len(matrix)
    _validar_matriz(matrix, n)

    # Internamente usamos float de doble precisión y solo redondeamos/truncamos
    # al mostrar resultados finales.
    rd_out = lambda v: _redondear(v, cifras, modo)

    # Separar A y b
    A = [[matrix[i][j] for j in range(n)] for i in range(n)]
    b = [matrix[i][n] for i in range(n)]

    logger("=" * 70)
    logger("  MÉTODO DE LA INVERSA DE MATRIZ (A⁻¹·b) - GAUSS-JORDAN")
    logger("=" * 70)
    _imprimir_matriz_cuadrada(A, cifras, logger, "\nMatriz A:")
    logger("Vector b:")
    logger(f"  [{', '.join(_fmt(bi, cifras) for bi in b)}]")
    logger("")

    # Construir [A | I]
    aug = []
    for i in range(n):
        fila = [A[i][j] for j in range(n)]
        for j in range(n):
            fila.append(1.0 if i == j else 0.0)
        aug.append(fila)

    _imprimir_matriz_extendida(aug, n, cifras, logger, "Matriz aumentada [A | I]:")

    # Gauss-Jordan sobre [A | I]
    logger("─" * 70)
    logger("Reducción de [A | I] → [I | A⁻¹] por Gauss-Jordan")
    logger("─" * 70)

    for k in range(n):
        logger(f"\n  --- Pivote ({k + 1},{k + 1}) ---")

        # Pivoteo parcial
        max_val = abs(aug[k][k])
        max_row = k
        for i in range(k + 1, n):
            if abs(aug[i][k]) > max_val:
                max_val = abs(aug[i][k])
                max_row = i
        if max_row != k:
            aug[k], aug[max_row] = aug[max_row], aug[k]
            logger(f"  ↔ Intercambio F{k + 1} ↔ F{max_row + 1}")

        if abs(aug[k][k]) < 1e-12:
            raise ValueError(
                f"La matriz es singular (pivote ≈ 0 en columna {k + 1}). No tiene inversa."
            )

        # Normalizar
        pivote = aug[k][k]
        logger(f"  Normalizar F{k + 1} / {_fmt(pivote, cifras)}")
        for j in range(2 * n):
            aug[k][j] = aug[k][j] / pivote

        # Eliminar
        for i in range(n):
            if i == k:
                continue
            if aug[i][k] == 0:
                continue
            factor = aug[i][k]
            logger(f"  F{i + 1} = F{i + 1} - ({_fmt(factor, cifras)}) × F{k + 1}")
            for j in range(2 * n):
                aug[i][j] = aug[i][j] - factor * aug[k][j]

        _imprimir_matriz_extendida(aug, n, cifras, logger)

    # Extraer A⁻¹
    A_inv = [[aug[i][j + n] for j in range(n)] for i in range(n)]
    _imprimir_matriz_cuadrada(A_inv, cifras, logger, "Matriz A⁻¹:")

    # Multiplicar A⁻¹ · b (con mayor precisión para minimizar errores de punto flotante)
    with localcontext() as ctx:
        ctx.prec = max(50, cifras + 10)
        A_inv_dec = [[Decimal(str(val)) for val in row] for row in A_inv]
        b_dec = [Decimal(str(val)) for val in b]

        x_dec = []
        for i in range(n):
            s = Decimal(0)
            for j in range(n):
                s += A_inv_dec[i][j] * b_dec[j]
            x_dec.append(s)

    x = [rd_out(float(val)) for val in x_dec]

    if mostrar_solucion:
        logger("─" * 70)
        logger("Cálculo de x = A⁻¹ · b")
        logger("─" * 70)

        for i in range(n):
            terminos = []
            for j in range(n):
                prod = A_inv[i][j] * b[j]
                terminos.append(f"({_fmt(A_inv[i][j], cifras)} × {_fmt(b[j], cifras)})")
            logger(f"  x{i + 1} = {' + '.join(terminos)}")
            logger(f"  x{i + 1} = {_fmt(x[i], cifras)}")
            logger("")

        logger("=" * 70)
        logger("  SOLUCIÓN FINAL")
        logger("=" * 70)
        for i in range(n):
            logger(f"  x{i + 1} = {_fmt(x[i], cifras)}")
        logger("")

    return x

def inversa_cofactores(matrix, cifras, modo, logger, mostrar_solucion=True):
    """Calcula la inversa usando la matriz de cofactores (adjunta).

    El método calcula A⁻¹ = (1/det(A))·adj(A) y luego resuelve x = A⁻¹·b.

    Parameters
    ----------
    mostrar_solucion : bool
        Si es True, muestra el cálculo de x = A⁻¹·b y la solución final.
    """
    n = len(matrix)
    _validar_matriz(matrix, n)

    # Internamente usamos float de doble precisión y solo aplicamos redondeo/truncado
    # al mostrar resultados finales.
    rd_out = lambda v: _redondear(v, cifras, modo)

    # Separar A y b
    A = [[matrix[i][j] for j in range(n)] for i in range(n)]
    b = [matrix[i][n] for i in range(n)]

    logger("=" * 70)
    logger("  MÉTODO DE LA INVERSA DE MATRIZ (A⁻¹·b) - COFACTORES")
    logger("=" * 70)
    _imprimir_matriz_cuadrada(A, cifras, logger, "\nMatriz A:")
    logger("Vector b:")
    logger(f"  [{', '.join(_fmt(bi, cifras) for bi in b)}]")
    logger("")

    detA = _determinante(A, cifras, modo)
    logger(f"Determinante det(A) = {_fmt(detA, cifras)}")
    if abs(detA) < 1e-12:
        raise ValueError("La matriz es singular (determinante ≈ 0). No tiene inversa.")

    cofactores = _matriz_cofactores(A, cifras, modo)
    _imprimir_matriz_cuadrada(cofactores, cifras, logger, "Matriz de cofactores:")

    # adj(A) = cofactores^T
    adj = [[cofactores[j][i] for j in range(n)] for i in range(n)]
    _imprimir_matriz_cuadrada(adj, cifras, logger, "Adjunta (transpuesta de cofactores):")

    # A⁻¹ = adj(A) / det(A)
    A_inv = [[rd_out(adj[i][j] / detA) for j in range(n)] for i in range(n)]
    _imprimir_matriz_cuadrada(A_inv, cifras, logger, "Matriz A⁻¹:")

    # Multiplicar A⁻¹ · b (usando Decimal para minimizar errores de punto flotante)
    with localcontext() as ctx:
        ctx.prec = max(50, cifras + 10)
        A_inv_dec = [[Decimal(str(val)) for val in row] for row in A_inv]
        b_dec = [Decimal(str(val)) for val in b]

        x_dec = []
        for i in range(n):
            s = Decimal(0)
            for j in range(n):
                s += A_inv_dec[i][j] * b_dec[j]
            x_dec.append(s)

    x = [rd_out(float(val)) for val in x_dec]

    if mostrar_solucion:
        logger("─" * 70)
        logger("Cálculo de x = A⁻¹ · b")
        logger("─" * 70)

        for i in range(n):
            terminos = []
            for j in range(n):
                prod = A_inv[i][j] * b[j]
                terminos.append(f"({_fmt(A_inv[i][j], cifras)} × {_fmt(b[j], cifras)})")
            logger(f"  x{i + 1} = {' + '.join(terminos)}")
            logger(f"  x{i + 1} = {_fmt(x[i], cifras)}")
            logger("")

        logger("=" * 70)
        logger("  SOLUCIÓN FINAL")
        logger("=" * 70)
        for i in range(n):
            logger(f"  x{i + 1} = {_fmt(x[i], cifras)}")
        logger("")

    return x


def determinante(matrix, cifras, modo, logger):
    """Calcula el determinante de la matriz A (parte izquierda de [A|b])."""
    n = len(matrix)
    _validar_matriz(matrix, n)

    A = [[matrix[i][j] for j in range(n)] for i in range(n)]
    rd_out = lambda v: _redondear(v, cifras, modo)

    logger("=" * 70)
    logger("  DETERMINANTE DE LA MATRIZ A")
    logger("=" * 70)
    _imprimir_matriz_cuadrada(A, cifras, logger, "\nMatriz A:")

    detA = rd_out(_determinante(A, cifras, modo))
    logger(f"Determinante det(A) = {_fmt(detA, cifras)}")
    logger("")

    return detA


def cramer(matrix, cifras, modo, logger):
    """Resuelve el sistema usando el método de Cramer (determinantes).

    x_i = det(A_i) / det(A), donde A_i reemplaza la columna i de A por b.
    """
    n = len(matrix)
    _validar_matriz(matrix, n)

    rd_out = lambda v: _redondear(v, cifras, modo)

    # Separar A y b
    A = [[matrix[i][j] for j in range(n)] for i in range(n)]
    b = [matrix[i][n] for i in range(n)]

    logger("=" * 70)
    logger("  MÉTODO DE CRAMER (DETERMINANTES)")
    logger("=" * 70)
    _imprimir_matriz_cuadrada(A, cifras, logger, "\nMatriz A:")
    logger("Vector b:")
    logger(f"  [{', '.join(_fmt(bi, cifras) for bi in b)}]")
    logger("")

    detA = _determinante(A, cifras, modo)
    logger(f"Determinante det(A) = {_fmt(detA, cifras)}")
    if abs(detA) < 1e-12:
        raise ValueError("La matriz es singular (determinante ≈ 0). No tiene solución única.")

    x = [0.0] * n
    for j in range(n):
        # Construir A_j reemplazando la columna j por el vector b
        Aj = [[A[i][k] if k != j else b[i] for k in range(n)] for i in range(n)]
        _imprimir_matriz_cuadrada(Aj, cifras, logger, f"Matriz A_{j + 1} (reemplaza columna {j + 1} con b):")

        detAj = _determinante(Aj, cifras, modo)
        logger(f"det(A_{j + 1}) = {_fmt(detAj, cifras)}")

        xj = rd_out(detAj / detA)
        x[j] = xj
        logger(
            f"x{j + 1} = det(A_{j + 1}) / det(A) = {_fmt(detAj, cifras)} / {_fmt(detA, cifras)} = {_fmt(xj, cifras)}\n"
        )

    logger("=" * 70)
    logger("  SOLUCIÓN FINAL")
    logger("=" * 70)
    for i in range(n):
        logger(f"  x{i + 1} = {_fmt(x[i], cifras)}")
    logger("")

    return x


# Compatibilidad: inversa_matriz queda como alias de la implementación Gauss-Jordan.
inversa_matriz = inversa_gauss_jordan
