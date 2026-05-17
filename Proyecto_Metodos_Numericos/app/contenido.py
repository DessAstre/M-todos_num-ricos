"""Definiciones de contenido: métodos, agrupaciones, ejemplos y datos del equipo."""

from __future__ import annotations


TITULO_APP = "Métodos Numéricos · Presentación Final"
SUBTITULO_PORTADA = "Compendio académico — Facultad de Ingeniería · UACh"

INTEGRANTES = [
    ("Aryam Desiree Méndez Sánchez", "373025"),
    ("Francisco Javier Ponce Saenz", "325000"),
]


# ---------------------------------------------------------------------------
#  Agrupación de temas (orden en menú e índice)
# ---------------------------------------------------------------------------

GRUPOS_TEMARIO = [
    ("Métodos cerrados",        ["Bisección", "Falsa Posición"]),
    ("Métodos abiertos",        ["Newton-Raphson"]),
    ("SSEL exactos",            ["Gauss", "Gauss-Jordan", "Inversa", "Cramer"]),
    ("SSEL aproximados",        ["Gauss-Seidel"]),
    ("Interpolación",           ["Interpolación"]),
    ("Integración definida",    ["Integración Definida"]),
    ("Ajuste de curvas",        ["Ajuste de Curvas"]),
]


# ---------------------------------------------------------------------------
#  Contenido didáctico de cada método
# ---------------------------------------------------------------------------

METODOS = {
    "Bisección": {
        "tipo": "raices",
        "nombre": "Método de Bisección",
        "capitulo": "Capítulo 1 · Raíces de Ecuaciones",
        "tema": (
            "¿Para qué sirve?\n"
            "El método de bisección sirve para encontrar de manera aproximada las raíces "
            "de una ecuación no lineal, es decir, los valores de x que hacen que f(x)=0.\n"
            "Se utiliza cuando la ecuación no se puede resolver fácilmente de forma algebraica.\n\n"
            "Aplicaciones\n"
            "Sus aplicaciones son muy comunes en ingeniería, física y matemáticas aplicadas, "
            "especialmente en problemas donde aparecen ecuaciones con exponentes, logaritmos "
            "o funciones trigonométricas que no se pueden despejar fácilmente."
        ),
        "formulas": (
            "Fórmulas del Método de Bisección:\n"
            "  δx = (b − a) / 2          (semiancho)\n"
            "  x  = a + δx               (punto medio)\n"
            "Condición de paro: |δx| ≤ tolerancia"
        ),
    },
    "Falsa Posición": {
        "tipo": "raices",
        "nombre": "Método de Falsa Posición",
        "capitulo": "Capítulo 1 · Raíces de Ecuaciones",
        "tema": (
            "¿Para qué sirve?\n"
            "El método de la falsa posición sirve para encontrar de manera aproximada las raíces "
            "de una ecuación no lineal. Mejora a la bisección al considerar el peso de los valores "
            "de la función en los extremos del intervalo.\n\n"
            "Aplicaciones\n"
            "Se usa en problemas de circuitos eléctricos, transferencia de calor, mecánica de "
            "fluidos, termodinámica y modelos matemáticos en programación."
        ),
        "formulas": (
            "Fórmulas del Método de Falsa Posición:\n"
            "  Δx = |f(a)|·(b − a) / (|f(a)| + |f(b)|)\n"
            "  x  = a + Δx       (equivalente a (a·f(b) − b·f(a)) / (f(b) − f(a)))\n"
            "Condición: |b − a| ≤ tolerancia"
        ),
    },
    "Newton-Raphson": {
        "tipo": "raices",
        "nombre": "Método de Newton-Raphson",
        "capitulo": "Capítulo 1 · Raíces de Ecuaciones",
        "tema": (
            "¿Para qué sirve?\n"
            "El método de Newton-Raphson utiliza la derivada de la función para encontrar raíces "
            "de forma más rápida que bisección o falsa posición. Converge cuadráticamente cuando "
            "la estimación inicial es adecuada.\n\n"
            "Aplicaciones\n"
            "Se usa extensamente en optimización, análisis estructural, dinámica de fluidos "
            "computacional, diseño de sistemas de control y, en general, cuando se requiere "
            "convergencia rápida."
        ),
        "formulas": (
            "Fórmulas del Método de Newton-Raphson:\n"
            "  Clásico:    x_{n+1} = x_n − f(x_n) / f'(x_n)\n"
            "  Mejorado (Halley):\n"
            "      h  = f / f'\n"
            "      Δx = h / (1 − 0.5·f·f'' / f'²)\n"
            "      x_{n+1} = x_n − Δx\n"
            "Condición de paro: |Δx| ≤ tolerancia"
        ),
    },
    "Gauss": {
        "tipo": "ssel",
        "nombre": "Eliminación Gaussiana",
        "capitulo": "Capítulo 2 · Sistemas de Ecuaciones Lineales",
        "tema": (
            "¿Para qué sirve?\n"
            "La eliminación gaussiana resuelve sistemas lineales (A·x = b) reduciendo la matriz "
            "aumentada a forma triangular superior y aplicando sustitución regresiva.\n\n"
            "Aplicaciones\n"
            "Ingeniería estructural, circuitos eléctricos, programación lineal y simulaciones "
            "numéricas en general."
        ),
        "formulas": (
            "Fórmulas:\n"
            "  Multiplicador:  m(i,k) = a(i,k) / a(k,k)\n"
            "  Fila i ← F_i − m(i,k)·F_k\n"
            "  X_n = b_n / a_nn\n"
            "  X_i = (b_i − Σ_{j>i} a_ij · x_j) / a_ii"
        ),
    },
    "Gauss-Jordan": {
        "tipo": "ssel",
        "nombre": "Método de Gauss-Jordan",
        "capitulo": "Capítulo 2 · Sistemas de Ecuaciones Lineales",
        "tema": (
            "¿Para qué sirve?\n"
            "Gauss-Jordan transforma la matriz a forma reducida (identidad), permitiendo leer la "
            "solución directamente sin sustitución regresiva. Sirve también para calcular la "
            "inversa de una matriz."
        ),
        "formulas": (
            "Fórmulas:\n"
            "  Normalizar pivote: F_k ← F_k / a_kk\n"
            "  Eliminar columna en todas las filas: F_i ← F_i − a_ik·F_k   (i ≠ k)\n"
            "  Resultado:  [I | solución]"
        ),
    },
    "Inversa": {
        "tipo": "ssel",
        "nombre": "Solución por Inversa de Matriz",
        "capitulo": "Capítulo 2 · Sistemas de Ecuaciones Lineales",
        "tema": (
            "¿Para qué sirve?\n"
            "Permite resolver A·x = b como x = A⁻¹·b cuando se necesita resolver varios vectores "
            "b con la misma matriz A. Útil también en análisis sensitivo."
        ),
        "formulas": (
            "Fórmulas:\n"
            "  A⁻¹ = (1 / det A) · adj(A)        (método por cofactores)\n"
            "  o bien Gauss-Jordan sobre [A | I] → [I | A⁻¹]\n"
            "  Solución:  x = A⁻¹ · b"
        ),
    },
    "Cramer": {
        "tipo": "ssel",
        "nombre": "Regla de Cramer",
        "capitulo": "Capítulo 2 · Sistemas de Ecuaciones Lineales",
        "tema": (
            "¿Para qué sirve?\n"
            "Resuelve sistemas lineales cuadrados usando determinantes. Es didáctica y útil para "
            "sistemas pequeños donde se desea relacionar la solución con el determinante."
        ),
        "formulas": (
            "Fórmulas de Cramer:\n"
            "  D    = det(A)\n"
            "  D_i  = det(A_i)        (sustituyendo la columna i por b)\n"
            "  x_i  = D_i / D\n"
            "Condición:  D ≠ 0"
        ),
    },
    "Gauss-Seidel": {
        "tipo": "iterativo",
        "nombre": "Gauss-Seidel y Relajaciones",
        "capitulo": "Capítulo 2 · Métodos Iterativos",
        "tema": (
            "¿Para qué sirve?\n"
            "Gauss-Seidel construye una hoja de iteraciones V0, V1, … utilizando los valores "
            "actualizados de x_i durante la misma iteración. Las Relajaciones trabajan con "
            "residuos y pivotes hasta cumplir la tolerancia."
        ),
        "formulas": (
            "Fórmulas:\n"
            "  Gauss-Seidel:\n"
            "      x_i^{k+1} = (1/a_ii) · [ b_i − Σ_{j<i} a_ij·x_j^{k+1} − Σ_{j>i} a_ij·x_j^k ]\n\n"
            "  Relajaciones (por residuos):\n"
            "      H_nuevo = H_anterior + pivote · C_columna_pivote\n\n"
            "  Forma SOR:\n"
            "      x_i^{k+1} = (1 − ω)·x_i^k + ω · x_i^{GS}"
        ),
    },
    "Interpolación": {
        "tipo": "interpolacion",
        "nombre": "Interpolación Lineal y de Lagrange",
        "capitulo": "Capítulo 3 · Interpolación",
        "tema": (
            "¿Para qué sirve?\n"
            "Estima valores intermedios cuando se conocen algunos puntos discretos. La forma "
            "lineal une dos puntos vecinos; Lagrange ajusta un polinomio que pasa por todos los "
            "puntos dados.\n\n"
            "Aplicaciones\n"
            "Tablas experimentales, pronósticos cortos, calibración de sensores y estimación de "
            "valores no medidos."
        ),
        "formulas": (
            "Fórmulas:\n"
            "  Interpolación lineal:  y = y1 + (x − x1)(y2 − y1)/(x2 − x1)\n"
            "  Interpolación inversa: x = x1 + (y − y1)(x2 − x1)/(y2 − y1)\n"
            "  Lagrange:              P(x) = Σ y_i · L_i(x)"
        ),
    },
    "Integración Definida": {
        "tipo": "integracion",
        "nombre": "Integración Definida (Cuadratura Numérica)",
        "capitulo": "Capítulo 4 · Integración Numérica",
        "tema": (
            "¿Para qué sirve?\n"
            "Aproxima ∫ₐᵇ f(x)dx cuando f es difícil o imposible de integrar analíticamente. "
            "Permite calcular áreas, momentos, trabajo, energía, etc.\n\n"
            "Aplicaciones\n"
            "Mecánica de fluidos (caudal y presión), transferencia de calor (energía absorbida), "
            "análisis estructural (momentos y deformaciones) y probabilidad continua."
        ),
        "formulas": (
            "Regla Trapecial:\n"
            "  I_t = (h/2)·[ f(a) + 2·Σ f(x_i) + f(b) ]\n\n"
            "Simpson 1/3   (N par):\n"
            "  I_s = (h/3)·[ f(a) + 4·Σ f(impares) + 2·Σ f(pares) + f(b) ]\n\n"
            "Regla 3/8     (N múltiplo de 3):\n"
            "  I_{3/8} = (3h/8)·[ f(a) + 3·Σ f(no múltiplos de 3) + 2·Σ f(múltiplos de 3) + f(b) ]\n\n"
            "Regla 2/45    (N múltiplo de 4):\n"
            "  I_{2/45} = (2h/45)·[ 7f(a) + 32Σ f(impar) + 12Σ f(par) + 14Σ f(múlt 4) + 7f(b) ]\n\n"
            "Extrapolación de Richardson / Romberg:\n"
            "  I_LDR = I_h + (I_k − I_h)·h² / (h² − k²)"
        ),
    },
    "Ajuste de Curvas": {
        "tipo": "ajuste",
        "nombre": "Ajuste de Curvas · Mínimos Cuadrados",
        "capitulo": "Capítulo 5 · Ajuste de Datos Experimentales",
        "tema": (
            "¿Para qué sirve?\n"
            "Encuentra el polinomio p(x) = K₀ + K₁x + K₂x² + … que minimiza el error cuadrático "
            "respecto de un conjunto de puntos (xᵢ, yᵢ). Útil cuando los datos contienen ruido y "
            "no pasan exactamente por un polinomio.\n\n"
            "Aplicaciones\n"
            "Regresión de datos experimentales, modelado de tendencias, calibración, "
            "ajustes de curvas en estadística y física aplicada."
        ),
        "formulas": (
            "Ecuaciones normales (grado g, n puntos):\n"
            "  Aᵀ · A · K = Aᵀ · y          (A: matriz de Vandermonde)\n\n"
            "Coeficientes resueltos por eliminación Gaussiana:\n"
            "  K = [K₀, K₁, K₂, …, K_g]\n\n"
            "Polinomio ajustado:\n"
            "  Y(x) = K₀ + K₁x + K₂x² + … + K_g · x^g\n\n"
            "Calidad del ajuste:\n"
            "  RSS = Σᵢ ( y_i − Y(x_i) )²      → se elige el grado con menor RSS"
        ),
    },
}


# Subtopics por tipo (orden de los selectores dentro de cada calculadora).
SUBTEMAS_POR_TIPO = {
    "raices":         ["Bisección", "Falsa Posición", "Newton-Raphson"],
    "ssel":           ["Gauss", "Gauss-Jordan", "Inversa", "Cramer"],
    "iterativo":      ["Gauss-Seidel"],
    "interpolacion":  ["Interpolación"],
    "integracion":    ["Integración Definida"],
    "ajuste":         ["Ajuste de Curvas"],
}


# ---------------------------------------------------------------------------
#  Ejemplos para cada bloque
# ---------------------------------------------------------------------------

EJEMPLOS = {
    "raices": (
        "Función: f(x) = x**3 - 2*x - 5\n"
        "Bisección / Falsa Posición:  a = 2, b = 3, tolerancia = 1e-6\n"
        "Newton-Raphson:               x₀ = 2, tolerancia = 1e-6\n"
        "Este ejemplo converge rápidamente y es fácil de seguir paso a paso."
    ),
    "ssel": (
        "Sistema 3x3:\n"
        "   2x +  y −  z =  8\n"
        "  −3x −  y + 2z = −11\n"
        "  −2x +  y + 2z = −3\n"
        "Solución esperada:  x = 2,  y = 3,  z = −1\n"
        "Determinante distinto de cero → Cramer también funciona."
    ),
    "iterativo": (
        "Sistema diagonalmente dominante:\n"
        "  10x −  y + 2z =   6\n"
        "  −x + 11y −  z =  25\n"
        "   2x −  y + 10z = −11\n"
        "Solución esperada:  x ≈ 1,  y ≈ 2,  z ≈ −1"
    ),
    "interpolacion": (
        "Puntos: (1, 2), (3, 6), (5, 12)\n"
        "Estimar y cuando x = 2 (lineal)  →  resultado ≈ 4\n"
        "Lagrange con los tres puntos: polinomio cuadrático que pasa por todos."
    ),
    "integracion": (
        "Función: f(x) = x**2\n"
        "Intervalo: a = 0, b = 1\n"
        "N = 4 subintervalos\n"
        "Resultado exacto: 1/3 ≈ 0.333333"
    ),
    "ajuste": (
        "Puntos: (0,1), (1,3), (2,5), (3,7), (4,9)\n"
        "Tendencia esperada: y ≈ 2x + 1 (grado 1)\n"
        "RSS prácticamente cero → ajuste perfecto a una recta."
    ),
}
