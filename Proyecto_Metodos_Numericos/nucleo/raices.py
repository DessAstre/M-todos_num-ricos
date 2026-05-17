"""Módulo interactivo de métodos numéricos para encontrar raíces.

Incluye bisección, falsa posición y Newton-Raphson (tangentes).
Proporciona un menú que solicita al usuario el método, la función,
los parámetros de intervalo o punto inicial, preferencias de
redondeo y configuración para trigonometría. Incluye utilidades para
truncar o redondear valores y manejar grados/radianes en las funciones
trigonométricas.
"""

import math

# pylint: disable=missing-function-docstring,invalid-name,C0301

# Utilidades de redondeo y truncamientos

def aplicar_redondeo(valor, modo, num_cifras):
    """Devuelve el valor redondeado o truncado según el modo.

    modo = 'T' para truncamiento, 'D' para redondeo decimal.
    num_cifras indica el número de cifras decimales.
    """
    if modo.upper() == "T":
        factor = 10 ** num_cifras
        return math.trunc(valor * factor) / factor
    else:
        # redondeo normal
        return round(valor, num_cifras)


def truncar_significativas(valor, cifras):
    """Trunca *significativamente* un número a un número fijo de cifras.

    La función del ejemplo de clase se utilizaba para truncar no sólo los
    valores impresos, sino también el cálculo del error relativo. El
    comportamiento coincide con el de la versión del script proporcionado:
        - 0.0009 con 3 cifras → 0.000  (termina)
        - 0.001  con 3 cifras → 0.001  (no termina)
    """
    if valor == 0:
        return 0.0
    signo = -1 if valor < 0 else 1
    abs_val = abs(valor)
    exp = math.floor(math.log10(abs_val))          # orden de magnitud
    factor = 10 ** (cifras - 1 - exp)
    return signo * math.trunc(abs_val * factor) / factor


def calcular_error_truncamiento(x_nuevo, x_anterior, cifras):
    """Error relativo truncado a *cifras* cifras significativas.

    Se utiliza el mismo cálculo que en el guion de ejemplo:
        error = |x_nuevo - x_anterior| / |x_nuevo|
    y a continuación se trunca el resultado a *cifras* cifras
    significativas. Se retorna 0.0 cuando x_nuevo == 0 para evitar
    divisiones por cero.
    """
    if x_nuevo == 0:
        return 0.0
    error = abs(x_nuevo - x_anterior) / abs(x_nuevo)
    return truncar_significativas(error, cifras)


def obtener_entorno_trig(usargeo):
    """Construye un diccionario con las funciones trigonométricas
    que aceptan grados si usargeo es True, o radianes en caso
    contrario. Se conservan el resto de las funciones matemáticas.
    """
    if usargeo:
        # envolver cada función trig en la conversión correspondiente
        return {
            "sin": lambda x: math.sin(math.radians(x)),
            "cos": lambda x: math.cos(math.radians(x)),
            "tan": lambda x: math.tan(math.radians(x)),
            "asin": lambda x: math.degrees(math.asin(x)),
            "acos": lambda x: math.degrees(math.acos(x)),
            "atan": lambda x: math.degrees(math.atan(x)),
        }
    else:
        # usar las funciones estándar de math (radianes)
        return {
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
        }


# Métodos

def biseccion(f, a_val, b_val, tolerance, max_iterations, modo_redondeo, decimals, logger=print):
    """Busca una raíz de `f` en [a_val, b_val] por el método de bisección.

    La variable clave en las iteraciones se llama **δx** o *delta* y se
    define como
        δx = (b - a) / 2
    el semiancho del intervalo. El punto donde se evalúa la función es
        c = a + δx
    (equivalente a la media (a+b)/2, pero separando los términos facilita
    el uso de la tolerancia). El siguiente orden de comprobaciones se
    aplica en cada paso:
      1. si tolerance ≥ |δx| → raíz aproximada (no se calcula f(x))
      2. si f(x) == 0          → raíz encontrada exacta
      3. actualizar el extremo cuyo signo coincide con f(x)

    El criterio de paro para el informe final utiliza el ancho del
    intervalo |b - a| (se imprime como "error").

    *logger* es una función que recibe una cadena y la muestra en la
    interfaz (por defecto usa *print*). Esto permite que el mismo
    algoritmo funcione en consola o en un *Text* de tkinter.
    """
    fa = f(a_val)
    fb = f(b_val)
    fa_fmt = aplicar_redondeo(fa, modo_redondeo, decimals)
    fb_fmt = aplicar_redondeo(fb, modo_redondeo, decimals)

    # comprobar raíces exactas en los extremos (valor mostrado o real)
    if fa_fmt == 0 or fa == 0:
        logger("\n# Fórmula: δx = (b - a)/2 ; c = a + δx")
        logger(
            f"\n{'Iter':>4} | {'a':>12} | {'b':>12} | {'s(a)':>3} | {'s(b)':>3} | {'C':>12} | {'x':>12} | {'err':>12} | {'tol':>12} | {'f(x)':>12}"
        )
        logger("-" * 96)
        a_f = aplicar_redondeo(a_val, modo_redondeo, decimals)
        b_f = aplicar_redondeo(b_val, modo_redondeo, decimals)
        sgn_fa = '+' if fa_fmt >= 0 else '-'
        sgn_fb = '+' if fb_fmt >= 0 else '-'
        zero = aplicar_redondeo(0.0, modo_redondeo, decimals)
        tol_f = aplicar_redondeo(tolerance, modo_redondeo, decimals)
        row = (
            f"{1:>4} | {a_f:>12.{decimals}f} | {b_f:>12.{decimals}f} | {sgn_fa:>3} | {sgn_fb:>3} | "
            f"{a_f:>12.{decimals}f} | {a_f:>12.{decimals}f} | {zero:>12.{decimals}f} | {tol_f:>12.{decimals}f} | {fa_fmt:>12.{decimals}f}"
        )
        logger(row)
        logger(f">>> Raíz (o aproximada) en a = {a_val}")
        return a_val
    if fb_fmt == 0 or fb == 0:
        logger("\n# Fórmula: δx = (b - a)/2 ; c = a + δx")
        logger(
            f"\n{'Iter':>4} | {'a':>12} | {'b':>12} | {'s(a)':>3} | {'s(b)':>3} | {'C':>12} | {'x':>12} | {'err':>12} | {'tol':>12} | {'f(x)':>12}"
        )
        logger("-" * 96)
        a_f = aplicar_redondeo(a_val, modo_redondeo, decimals)
        b_f = aplicar_redondeo(b_val, modo_redondeo, decimals)
        sgn_fa = '+' if fa_fmt >= 0 else '-'
        sgn_fb = '+' if fb_fmt >= 0 else '-'
        zero = aplicar_redondeo(0.0, modo_redondeo, decimals)
        tol_f = aplicar_redondeo(tolerance, modo_redondeo, decimals)
        row = (
            f"{1:>4} | {a_f:>12.{decimals}f} | {b_f:>12.{decimals}f} | {sgn_fa:>3} | {sgn_fb:>3} | "
            f"{b_f:>12.{decimals}f} | {b_f:>12.{decimals}f} | {zero:>12.{decimals}f} | {tol_f:>12.{decimals}f} | {fb_fmt:>12.{decimals}f}"
        )
        logger(row)
        logger(f">>> Raíz (o aproximada) en b = {b_val}")
        return b_val

    # sign test using displayed values
    if fa_fmt * fb_fmt > 0:
        logger("Error: f(a) y f(b) deben tener signos opuestos.")
        logger(f"  f({a_val}) = {fa_fmt}")
        logger(f"  f({b_val}) = {fb_fmt}")
        return None

    # encabezado simplificado: sólo signos para f(a) y f(b) según requerimiento
    # añadimos columna para error truncado si el usuario lo solicita (las
    # funciones de cálculo ya devuelven valor, pero solo se mostrará cuando el
    # logger reciba el string completo).
    logger("\n# Fórmula: δx = (b - a)/2 ; c = a + δx")
    logger(
        f"\n{'Iter':>4} | {'a':>12} | {'b':>12} | {'s(a)':>3} | {'s(b)':>3} | {'C':>12} | {'x':>12} | {'err':>12} | {'tol':>12} | {'f(x)':>12}"
    )
    logger("-" * 120)

    # preparaciones para criterio de cifras significativas
    x_prev = a_val
    for i in range(1, max_iterations + 1):
        # semiancho del intervalo y punto medio
        delta = (b_val - a_val) / 2.0        # δx = (b - a)/2
        x = a_val + delta                   # punto de evaluación
        fx = f(x)
        width = abs(b_val - a_val)

        # calcular error truncado relativo y formatearlo para mostrar
        trunc_err = calcular_error_truncamiento(x, x_prev, decimals)
        err_fmt = aplicar_redondeo(trunc_err, modo_redondeo, decimals)

        # aplicar redondeo/truncamiento a los demás valores que se imprimen
        a_fmt = aplicar_redondeo(a_val, modo_redondeo, decimals)
        b_fmt = aplicar_redondeo(b_val, modo_redondeo, decimals)
        fa_fmt = aplicar_redondeo(fa, modo_redondeo, decimals)
        fb_fmt = aplicar_redondeo(fb, modo_redondeo, decimals)
        sgn_fa = '+' if fa_fmt >= 0 else '-'
        sgn_fb = '+' if fb_fmt >= 0 else '-'
        x_fmt = aplicar_redondeo(x, modo_redondeo, decimals)
        tol_fmt = aplicar_redondeo(tolerance, modo_redondeo, decimals)
        fx_fmt = aplicar_redondeo(fx, modo_redondeo, decimals)
        width_fmt = aplicar_redondeo(width, modo_redondeo, decimals)

        c_fmt = aplicar_redondeo(delta, modo_redondeo, decimals)
        c_fmt = aplicar_redondeo(delta, modo_redondeo, decimals)
        row = (
            f"{i:>4} | {a_fmt:>12.{decimals}f} | {b_fmt:>12.{decimals}f} | {sgn_fa:>3} | {sgn_fb:>3} | "
            f"{c_fmt:>12.{decimals}f} | {x_fmt:>12.{decimals}f} | {err_fmt:>12.{decimals}f} | {tol_fmt:>12.{decimals}f} | {fx_fmt:>12.{decimals}f}"
        )
        logger(row)

        # detener si el error mostrado se hace cero (cifras significativas)
        if err_fmt == 0.0 and i > 1:
            logger(f"\n>>> Error truncado mostrado = {err_fmt:.{decimals}f}  →  0 (criterio de cifras)")
            logger(f">>> Iteraciones realizadas: {i}")
            logger(f">>> Error final |b - a| = {width_fmt:.{decimals}f}")
            return x

        # V2a: Δx se muestra como cero en pantalla
        if abs(delta) < 0.5 * 10**(-decimals) and i > 1:
            logger(f"\n>>> Δx mostrado = 0.{'0'*decimals}  →  V2a (umbral visual)")
            logger(f">>> Iteraciones realizadas: {i}")
            logger(f">>> Error final |b - a| = {width_fmt:.{decimals}f}")
            return x

        # guardar la aproximación anterior para calcular el siguiente error
        x_prev = x

        # criterio de paro según nueva especificación
        if tolerance >= abs(delta):
            logger(f"\n>>> Raíz aproximada: x = {x_fmt:.{decimals}f} (tol ≥ |δx|)")
            logger(f">>> Iteraciones realizadas: {i}")
            logger(f">>> Error final |b - a| = {width_fmt:.{decimals}f}")
            return x
        if fx == 0:
            logger(f"\n>>> Raíz encontrada: x = {x_fmt:.{decimals}f}")
            logger(f">>> Iteraciones realizadas: {i}")
            logger(f">>> Error final |b - a| = {width_fmt:.{decimals}f}")
            return x
        if fa * fx < 0:
            b_val = x
            fb = fx
        else:
            a_val = x
            fa = fx

    logger(f"\n>>> Se alcanzó el máximo de {max_iterations} iteraciones.")
    # usar la misma fórmula estable para el punto medio
    x = a_val + (b_val - a_val) / 2.0
    x_fmt = aplicar_redondeo(x, modo_redondeo, decimals)
    err_fmt = aplicar_redondeo(abs(b_val - a_val), modo_redondeo, decimals)
    logger(f">>> Mejor aproximación: x = {x_fmt:.{decimals}f}")
    logger(f">>> Error final |b - a| = {err_fmt:.{decimals}f}")
    return x


def falsa_posicion(f, a_val, b_val, tolerance, max_iterations, modo_redondeo, decimals, logger=print):
    """Calcula raíz de `f` con el método de falsa posición en [a_val,b_val].

    La iteración utiliza dos cantidades:
        Δx = |f(a)|·(b-a) / (|f(a)| + |f(b)|)
    que es el desplazamiento positivo desde el extremo izquierdo, y
    el punto de evaluación
        x = a + Δx  (equivalente a la fórmula clásica
            (a·f(b) - b·f(a)) / (f(b) - f(a)))
    El valor de Δx se muestra en la tabla junto con su fórmula para que
    quien observe las iteraciones vea cómo se calcula el paso.

    El parámetro `logger` permite redirigir la salida (por defecto `print`),
    lo que facilita el uso desde la consola o una interfaz gráfica.

    Los argumentos `modo_redondeo` (`'T'` truncar o `'D'` redondear) y
    `decimals` controlan cómo se muestran los valores en la tabla.
    Fabricar `f` con el entorno trig apropiado permite usar grados o
    radianes indistintamente; la función misma decide la unidad.
    """
    fa = f(a_val)
    fb = f(b_val)
    # valores mostrados (truncados/redondeados) que se usarán tanto en el
    # encabezado como en los validadores para emular el script de prueba.
    fa_fmt = aplicar_redondeo(fa, modo_redondeo, decimals)
    fb_fmt = aplicar_redondeo(fb, modo_redondeo, decimals)

    # validadores de extremos; si alguno es raíz exacta imprimimos una fila inicial
    if fa_fmt == 0 or fa == 0:
        # construir cabecera y primera fila mostrando a como x
        logger(
            f"\n{'Iter':>4} | {'a':>12} | {'b':>12} | {'fa':>12} | {'fb':>12} | {'Δx':>12} | {'x':>12} | {'err':>12} | {'tol':>12} | {'f(x)':>12}"
        )
        logger("-" * 108)
        a_fmt = aplicar_redondeo(a_val, modo_redondeo, decimals)
        b_fmt = aplicar_redondeo(b_val, modo_redondeo, decimals)
        fa_fmt2 = aplicar_redondeo(fa, modo_redondeo, decimals)
        fb_fmt2 = aplicar_redondeo(fb, modo_redondeo, decimals)
        # Δx and err are zero since no iteration
        zero_fmt = aplicar_redondeo(0.0, modo_redondeo, decimals)
        tol_fmt = aplicar_redondeo(tolerance, modo_redondeo, decimals)
        row = (
            f"{1:>4} | {a_fmt:>12.{decimals}f} | {b_fmt:>12.{decimals}f} | {fa_fmt2:>12.{decimals}f} | "
            f"{fb_fmt2:>12.{decimals}f} | {zero_fmt:>12.{decimals}f} | {zero_fmt:>12.{decimals}f} | "
            f"{tol_fmt:>12.{decimals}f} | {fa_fmt2:>12.{decimals}f}"
        )
        logger(row)
        logger(f">>> Raíz (o aproximada) en a = {a_val}")
        return a_val
    if fb_fmt == 0 or fb == 0:
        logger(
            f"\n{'Iter':>4} | {'a':>12} | {'b':>12} | {'fa':>12} | {'fb':>12} | {'Δx':>12} | {'x':>12} | {'err':>12} | {'tol':>12} | {'f(x)':>12}"
        )
        logger("-" * 108)
        a_fmt = aplicar_redondeo(a_val, modo_redondeo, decimals)
        b_fmt = aplicar_redondeo(b_val, modo_redondeo, decimals)
        fa_fmt2 = aplicar_redondeo(fa, modo_redondeo, decimals)
        fb_fmt2 = aplicar_redondeo(fb, modo_redondeo, decimals)
        zero_fmt = aplicar_redondeo(0.0, modo_redondeo, decimals)
        tol_fmt = aplicar_redondeo(tolerance, modo_redondeo, decimals)
        row = (
            f"{1:>4} | {a_fmt:>12.{decimals}f} | {b_fmt:>12.{decimals}f} | {fa_fmt2:>12.{decimals}f} | "
            f"{fb_fmt2:>12.{decimals}f} | {zero_fmt:>12.{decimals}f} | {zero_fmt:>12.{decimals}f} | "
            f"{tol_fmt:>12.{decimals}f} | {fb_fmt2:>12.{decimals}f}"
        )
        logger(row)
        logger(f">>> Raíz (o aproximada) en b = {b_val}")
        return b_val

    # sign-test using displayed values (V1)
    if fa_fmt * fb_fmt > 0:
        logger("Error: f(a) y f(b) deben tener signos opuestos.")
        logger(f"  f({a_val}) = {fa_fmt}")
        logger(f"  f({b_val}) = {fb_fmt}")
        return None

    if fa * fb > 0:
        logger("Error: f(a) y f(b) deben tener signos opuestos.")
        logger(f"  f({a_val}) = {fa}")
        logger(f"  f({b_val}) = {fb}")
        return None
    # fórmulas para revisar a lápiz
    logger("\n# Fórmulas: Δx = |f(a)|(b-a)/(|f(a)|+|f(b)|)   ,   x = a + Δx")    # cabecera con columna adicional para error truncado, más C
    logger(
        f"\n{'Iter':>4} | {'a':>12} | {'b':>12} | {'fa':>12} | {'fb':>12} | {'Δx':>12} | {'x':>12} | {'err':>12} | {'tol':>12} | {'f(x)':>12}"
    )
    logger("-" * 120)

    # valor anterior de x (para cálculo de error truncado)
    x_prev = a_val
    for i in range(1, max_iterations + 1):
        # cálculo de Δx y punto de evaluación según instrucción
        delta = abs(fa) * (b_val - a_val) / (abs(fa) + abs(fb))
        x = a_val + delta                 # ahora x=a+δx, equivalente a la fórmula clásica
        fx = f(x)

        # ancho del intervalo para mostrarlo más tarde si se quiere
        width = abs(b_val - a_val)

        a_fmt = aplicar_redondeo(a_val, modo_redondeo, decimals)
        b_fmt = aplicar_redondeo(b_val, modo_redondeo, decimals)
        fa_fmt = aplicar_redondeo(fa, modo_redondeo, decimals)
        fb_fmt = aplicar_redondeo(fb, modo_redondeo, decimals)
        delta_fmt = aplicar_redondeo(delta, modo_redondeo, decimals)
        x_fmt = aplicar_redondeo(x, modo_redondeo, decimals)
        tol_fmt = aplicar_redondeo(tolerance, modo_redondeo, decimals)
        fx_fmt = aplicar_redondeo(fx, modo_redondeo, decimals)
        width_fmt = aplicar_redondeo(width, modo_redondeo, decimals)

        # calcular error truncado relativo y formatearlo a la misma precisión
        trunc_err = calcular_error_truncamiento(x, x_prev, decimals)
        err_fmt = aplicar_redondeo(trunc_err, modo_redondeo, decimals)

        c_fmt = delta_fmt
        row = (
            f"{i:>4} | {a_fmt:>12.{decimals}f} | {b_fmt:>12.{decimals}f} | {fa_fmt:>12.{decimals}f} | "
            f"{fb_fmt:>12.{decimals}f} | {delta_fmt:>12.{decimals}f} | {c_fmt:>12.{decimals}f} | {x_fmt:>12.{decimals}f} | "
            f"{err_fmt:>12.{decimals}f} | {tol_fmt:>12.{decimals}f} | {fx_fmt:>12.{decimals}f}"
        )
        logger(row)
        # validadores de cada iteración: tolerancia vs Δx, error truncado, f(x) exacta o aproximada
        # V2a - Δx se muestra como cero en la tabla (umbral basado en decimales)
        if abs(delta) < 0.5 * 10**(-decimals) and i > 1:
            logger(f"\n>>> Δx mostrado = 0.{'0'*decimals}  →  V2a (umbral visual)")
            logger(f">>> Iteraciones realizadas: {i}")
            logger(f">>> Ancho final |b - a| = {width_fmt:.{decimals}f}")
            return x
        # si la versión mostrada del error es cero, damos por cumplido el
        # criterio de cifra significativa y detenemos el proceso.
        if err_fmt == 0.0 and i > 1:
            logger(f"\n>>> Error truncado mostrado = {err_fmt:.{decimals}f}  →  0 (criterio de cifras)")
            logger(f">>> Iteraciones realizadas: {i}")
            logger(f">>> Ancho final |b - a| = {width_fmt:.{decimals}f}")
            return x
        if tolerance >= abs(delta):
            logger(f"\n>>> Raíz aproximada: x = {x_fmt:.{decimals}f} (tol ≥ Δx)")
            logger(f">>> Iteraciones realizadas: {i}")
            logger(f">>> Ancho final |b - a| = {width_fmt:.{decimals}f}")
            return x
        if abs(fx) <= tolerance:
            logger(f"\n>>> Raíz encontrada (o aproximada) x = {x_fmt:.{decimals}f}")
            logger(f">>> Iteraciones realizadas: {i}")
            logger(f">>> Ancho final |b - a| = {width_fmt:.{decimals}f}")
            return x
        # antes de ajustar el intervalo guardamos x para el próximo cálculo
        x_prev = x
        if fa * fx < 0:
            b_val = x
            fb = fx
        else:
            a_val = x
            fa = fx

    logger(f"\n>>> Se alcanzó el máximo de {max_iterations} iteraciones.")
    x = (a_val * fb - b_val * fa) / (fb - fa)
    x_fmt = aplicar_redondeo(x, modo_redondeo, decimals)
    err_fmt = aplicar_redondeo(abs(b_val - a_val), modo_redondeo, decimals)
    logger(f">>> Mejor aproximación: x = {x_fmt:.{decimals}f}")
    logger(f">>> Error final |b - a| = {err_fmt:.{decimals}f}")
    return x


def newton_raphson(f, df, x0_init, tolerance, max_iterations, modo_redondeo, decimals, logger=print):
    """Método de Newton‑Raphson para encontrar raíz de `f` a partir de x0.

    df es la derivada de `f`; si es `None` se usa una aproximación
    numérica central. Los demás parámetros son análogos a los de
    bisección/falsa_posición.
    """
    def derivada(x):
        if df is not None:
            return df(x)
        # paso adaptativo según la magnitud de x
        h = 1e-8 * (1 + abs(x))
        try:
            # método de paso complejo para mayor estabilidad numérica
            return (f(x + h * 1j).imag) / h
        except Exception:
            # si no se pueden evaluar complejos, usar diferencia central real
            return (f(x + h) - f(x - h)) / (2 * h)

    x = x0_init
    fx = f(x)

    # encabezado con columna adicional para el error truncado
    logger("\n# Fórmula: Δx = -f(x0)/f'(x0) ; x1 = x0 + Δx")
    logger(
        f"\n{'Iter':>4} | {'x0':>12} | {'f(x0)':>12} | {'df(x0)':>12} | {'Δx':>12} | {'x1':>12} | {'err':>12} | {'tol':>12} | {'f(x1)':>12}"
    )
    logger("-" * 122)

    for i in range(1, max_iterations + 1):
        dfx = derivada(x)
        if dfx == 0:
            logger("Derivada cero, método falla.")
            return None
        dx = fx / dfx
        x_new = x - dx
        fx_new = f(x_new)
        error = abs(dx)

        x_fmt = aplicar_redondeo(x, modo_redondeo, decimals)
        fx_fmt = aplicar_redondeo(fx, modo_redondeo, decimals)
        dfx_fmt = aplicar_redondeo(dfx, modo_redondeo, decimals)
        dx_fmt = aplicar_redondeo(error, modo_redondeo, decimals)
        xnew_fmt = aplicar_redondeo(x_new, modo_redondeo, decimals)
        tol_fmt = aplicar_redondeo(tolerance, modo_redondeo, decimals)
        fxnew_fmt = aplicar_redondeo(fx_new, modo_redondeo, decimals)

        row = (
            f"{i:>4} | {x_fmt:>12.{decimals}f} | {fx_fmt:>12.{decimals}f} | {dfx_fmt:>12.{decimals}f} | "
            f"{dx_fmt:>12.{decimals}f} | {xnew_fmt:>12.{decimals}f} | {tol_fmt:>12.{decimals}f} | {fxnew_fmt:>12.{decimals}f}"
        )
        logger(row)

        if fx_new == 0 or error < tolerance:
            logger(f"\n>>> Raíz encontrada: x = {xnew_fmt:.{decimals}f}")
            logger(f">>> Iteraciones realizadas: {i}")
            return x_new

        x = x_new
        fx = fx_new

    logger(f"\n>>> Se alcanzó el máximo de {max_iterations} iteraciones.")
    x_fmt = aplicar_redondeo(x, modo_redondeo, decimals)
    logger(f">>> Mejor aproximación: x = {x_fmt:.{decimals}f}")
    return x


def newton_mejorado(f, df, d2f, x0_init, tolerance, max_iterations, modo_redondeo, decimals, logger=print):
    """Newton mejorado (Halley) usando primera y segunda derivada.

    Si df o d2f son None se aproximan numéricamente. Aplica la
    iteración:
        h = f/f' ; dx = h / (1 - 0.5 * f * f'' / f'**2)
    que corresponde a la fórmula de Halley (orden ≥2).
    """
    def derivada(x):
        if df is not None:
            return df(x)
        h = 1e-8 * (1 + abs(x))
        try:
            return (f(x + h * 1j).imag) / h
        except Exception:
            return (f(x + h) - f(x - h)) / (2 * h)

    def derivada2(x):
        if d2f is not None:
            return d2f(x)
        h = 1e-5 * (1 + abs(x))
        return (f(x + h) - 2 * f(x) + f(x - h)) / (h * h)

    x = x0_init
    fx = f(x)

    # encabezado con columna extra para error truncado
    logger("\n# Fórmula mejorada: 1/Δx = -f'/f + 1/2·f''/f'  ⇒  Δx = 1/(…)  ;  x1=x0+Δx")
    logger(
        f"\n{'Iter':>4} | {'x0':>12} | {'f(x0)':>12} | {'df(x0)':>12} | {'d2f(x0)':>12} | {'Δx':>12} | {'x1':>12} | {'err':>12} | {'tol':>12} | {'f(x1)':>12}"
    )
    logger("-" * 144)

    for i in range(1, max_iterations + 1):
        dfx = derivada(x)
        if dfx == 0:
            logger("Derivada primera cero, método falla.")
            return None
        d2fx = derivada2(x)
        h_val = fx / dfx
        denom = 1 - 0.5 * fx * d2fx / (dfx * dfx)
        dx = h_val / denom
        x_new = x - dx
        fx_new = f(x_new)
        error = abs(dx)

        x_fmt = aplicar_redondeo(x, modo_redondeo, decimals)
        fx_fmt = aplicar_redondeo(fx, modo_redondeo, decimals)
        dfx_fmt = aplicar_redondeo(dfx, modo_redondeo, decimals)
        d2fx_fmt = aplicar_redondeo(d2fx, modo_redondeo, decimals)
        dx_fmt = aplicar_redondeo(error, modo_redondeo, decimals)
        xnew_fmt = aplicar_redondeo(x_new, modo_redondeo, decimals)
        tol_fmt = aplicar_redondeo(tolerance, modo_redondeo, decimals)
        fxnew_fmt = aplicar_redondeo(fx_new, modo_redondeo, decimals)

        row = (
            f"{i:>4} | {x_fmt:>12.{decimals}f} | {fx_fmt:>12.{decimals}f} | {dfx_fmt:>12.{decimals}f} | "
            f"{d2fx_fmt:>12.{decimals}f} | {dx_fmt:>12.{decimals}f} | {xnew_fmt:>12.{decimals}f} | {tol_fmt:>12.{decimals}f} | {fxnew_fmt:>12.{decimals}f}"
        )
        logger(row)

        if fx_new == 0 or error < tolerance:
            logger(f"\n>>> Raíz encontrada: x = {xnew_fmt:.{decimals}f}")
            logger(f">>> Iteraciones realizadas: {i}")
            return x_new

        x = x_new
        fx = fx_new

    logger(f"\n>>> Se alcanzó el máximo de {max_iterations} iteraciones.")
    x_fmt = aplicar_redondeo(x, modo_redondeo, decimals)
    logger(f">>> Mejor aproximación: x = {x_fmt:.{decimals}f}")
    return x


# ---------------------------------
# Menú interactivo principal
# ---------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("   MÉTODOS DE BISECCIÓN / FALSA POSICIÓN / NEWTON")
    print("=" * 60)

    while True:
        print("\n" + "-" * 60)
        print("  1) Bisección")
        print("  2) Falsa posición")
        print("  3) Newton-Raphson")
        print("  4) Salir")
        op = input("\nMétodo: ").strip()
        # pylint: disable=invalid-name
        if op == "4":
            print("\n¡Hasta luego!")
            break

        if op not in ("1", "2", "3"):
            print("Opción inválida, intente de nuevo.")
            continue

        # selección de función
        print("\nElija la función a evaluar:")
        print("  1) x**3 - x - 2")
        print("  2) sin(x) - x/2")
        print("  3) ln(x) - 1")
        print("  4) exp(x) - 3*x")
        print("  5) Ingresar función personalizada")
        fop = input("Opción: ").strip()

        # en caso de Newton preguntar variante
        nopt = None
        if op == "3":
            print("\nVariante de Newton:")
            print("  1) Tangente (Newton clásico)")
            print("  2) Mejorado (segunda orden)")
            nopt = input("Opción: ").strip()
            if nopt not in ("1", "2"):
                nopt = "1"

        ent_trig = {}
        usar_degr = False
        if fop in ("2", "5"):
            respuesta = input("¿Usar grados para trigonometría? (s/n): ").strip().lower()
            usar_degr = respuesta.startswith("s")
            ent_trig = obtener_entorno_trig(usar_degr)

        if fop == "1":
            nombre_func = "x**3 - x - 2"
            func = lambda x: x**3 - x - 2  # pylint: disable=unnecessary-lambda-assignment
        elif fop == "2":
            nombre_func = "sin(x) - x/2"
            func = lambda x: ent_trig.get("sin", math.sin)(x) - x / 2  # pylint: disable=unnecessary-lambda-assignment
        elif fop == "3":
            nombre_func = "ln(x) - 1"
            func = lambda x: math.log(x) - 1  # pylint: disable=unnecessary-lambda-assignment
        elif fop == "4":
            nombre_func = "exp(x) - 3*x"
            func = lambda x: math.exp(x) - 3 * x  # pylint: disable=unnecessary-lambda-assignment
        else:
            expr = input("\nf(x) = ").strip()
            env = {
                "x": 0,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "sqrt": math.sqrt,
                "pi": math.pi,
                "e": math.e,
                "abs": abs,
                **ent_trig,
            }

            # pylint: disable=eval-used
            def func(x, _expr=expr, _env=env):
                """Evalúa la expresión personalizada."""
                return eval(_expr, {**_env, "x": x})

            nombre_func = expr
        print(f"\nFunción seleccionada: f(x) = {nombre_func}")

        # parámetros de acuerdo al método elegido
        a = b = x0 = None
        if op in ("1", "2"):
            a = float(input("Intervalo inferior a: "))
            b = float(input("Intervalo superior b: "))
        else:  # Newton
            x0 = float(input("Valor inicial x0: "))
        tol = float(input("Tolerancia (por ejemplo 1e-6): "))
        max_iter = int(input("Máximo de iteraciones: "))

        # opciones de redondeo
        modo_red_input = input("Redondear por truncamiento (T) o decimales (D)? ").strip().upper()
        if modo_red_input not in ("T", "D"):
            modo_red_input = "D"
        cifras = int(input("¿Cuántas cifras decimales desea mostrar? "))

        # llamar al método correspondiente
        if op == "1":
            biseccion(func, a, b, tol, max_iter, modo_red_input, cifras)
        elif op == "2":
            falsa_posicion(func, a, b, tol, max_iter, modo_red_input, cifras)
        else:  # Newton
            # obtener derivadas según variante
            df_func = None
            d2f_func = None
            if fop == "1":
                df_func = lambda x: 3 * x**2 - 1  # pylint: disable=unnecessary-lambda-assignment
                d2f_func = lambda x: 6 * x  # pylint: disable=unnecessary-lambda-assignment
            elif fop == "2":
                df_func = lambda x: ent_trig.get("cos", math.cos)(x) - 0.5  # pylint: disable=unnecessary-lambda-assignment
                d2f_func = lambda x: -ent_trig.get("sin", math.sin)(x)  # pylint: disable=unnecessary-lambda-assignment
            elif fop == "3":
                df_func = lambda x: 1 / x  # pylint: disable=unnecessary-lambda-assignment
                d2f_func = lambda x: -1 / (x * x)  # pylint: disable=unnecessary-lambda-assignment
            elif fop == "4":
                df_func = lambda x: math.exp(x) - 3  # pylint: disable=unnecessary-lambda-assignment
                d2f_func = math.exp
            else:
                deriv_expr = input("Derivada f'(x) (dejar vacío para aproximar): ").strip()
                if deriv_expr:
                    env_der = {
                        "x": 0,
                        "log": math.log,
                        "log10": math.log10,
                        "exp": math.exp,
                        "sqrt": math.sqrt,
                        "pi": math.pi,
                        "e": math.e,
                        "abs": abs,
                        **ent_trig,
                    }
                    # pylint: disable=eval-used,unnecessary-lambda-assignment
                    df_func = lambda x, _expr=deriv_expr, _env=env_der: eval(_expr, {**_env, "x": x})
                else:
                    df_func = None
            # si se pide variante mejorada solicitar segunda derivada
            if nopt == "2":
                if fop == "5":
                    deriv2_expr = input("Segunda derivada f''(x) (vacío para aproximar): ").strip()
                    if deriv2_expr:
                        env_d2 = {
                            "x": 0,
                            "log": math.log,
                            "log10": math.log10,
                            "exp": math.exp,
                            "sqrt": math.sqrt,
                            "pi": math.pi,
                            "e": math.e,
                            "abs": abs,
                            **ent_trig,
                        }
                        # pylint: disable=eval-used,unnecessary-lambda-assignment
                        d2f_func = lambda x, _expr=deriv2_expr, _env=env_d2: eval(_expr, {**_env, "x": x})
                    else:
                        d2f_func = None
                # para funciones predeterminadas d2f_func ya está asignado
            # elegir función
            if nopt == "2":
                newton_mejorado(func, df_func, d2f_func, x0, tol, max_iter, modo_red_input, cifras)
            else:
                newton_raphson(func, df_func, x0, tol, max_iter, modo_red_input, cifras)

        input("\nPresione Enter para volver al menú principal...")
