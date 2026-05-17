# Integración definida

- ***Integración definida*** es el proceso de calcular el valor de una integral definida, que representa el área bajo la curva de una función entre dos puntos específicos en el eje x. La integral definida se denota comúnmente como:

$$\int_{a}^{b} f(x) \, dx$$

donde:
- \(f(x)\) es la función que se está integrando.
- \(a\) es el límite inferior de integración.
- \(b\) es el límite superior de integración.

La integral definida mide el área entre la curva de la función y el eje x, entre los puntos \(a\) y \(b\).

## Teoría básica

Para métodos numéricos de integración es fundamental la fórmula del paso:

$$h = \frac{b - a}{N}$$

Donde:
- \(N\) es el número de subintervalos.
- \(h\) es el ancho de cada subintervalo.
- Los puntos de partición se calculan como:

$$x_i = a + i \cdot h \quad \text{para } i = 0, 1, \dots, N$$

Esto es equivalente a la fórmula que falta: \(h = \frac{b - a}{N}\), no "h + b-a/N".

## Métodos numéricos de integración

### 1. Método del trapecio

El método del trapecio aproximada el área bajo la curva por trapecios.

$$\int_{a}^{b} f(x) \, dx \approx \frac{h}{2} \left[ f(a) + 2 \sum_{i=1}^{N-1} f(a + i h) + f(b) \right]$$

- \(h = \frac{b - a}{N}\)
- Los nodos son \(x_0 = a\), \(x_N = b\) y \(x_i = a + i h\).

El error del trapecio es del orden \(O(h^2)\) si la función es suave.

### 2. Método del punto medio

El método del punto medio usa el valor de la función en el centro de cada subintervalo.

$$\int_{a}^{b} f(x) \, dx \approx h \sum_{i=0}^{N-1} f\left(a + \left(i + \tfrac{1}{2}\right) h\right)$$

Este método es muy útil cuando se quiere una aproximación con menos evaluación de puntos.

### 3. Método de Simpson 1/3

Simpson 1/3 combina trapecios y puntos impares para mejorar la precisión.

$$\int_{a}^{b} f(x) \, dx \approx \frac{h}{3} \left[ f(a) + 4 \sum_{i=1}^{N/2} f(a + (2i - 1) h) + 2 \sum_{i=1}^{N/2 - 1} f(a + 2 i h) + f(b) \right]$$

Este método requiere \(N\) par y su error es del orden \(O(h^4)\).

### 4. Método de Simpson 3/8

Simpson 3/8 usa bloques de tres subintervalos:

$$\int_{a}^{b} f(x) \, dx \approx \frac{3h}{8} \left[ f(a) + f(b) + 3 \sum_{i=1}^{N-1,\, i \not\equiv 0\, (\text{mod }3)} f(a + i h) + 2 \sum_{i=3,\, i\equiv 0\, (\text{mod }3)}^{N-3} f(a + i h) \right]$$

Para Simpson 3/8 se requiere que \(N\) sea múltiplo de 3.

## Validadores y tolerancias

En los programas de métodos numéricos se usan diferentes tolerancias según el problema:

- Tolerancia típica para raíces y bisección: \(10^{-6}\) o \(10^{-8}\).
- Tolerancia típica para Gauss-Seidel y relajaciones: \(10^{-2}\) o \(10^{-3}\).
- Tolerancia en integración numérica: comparar con una referencia fina o con integrales exactas cuando exista.

### Comparación de tolerancias de otros programas

| Programa | Método | Tolerancia típica | Criterio de paro |
|---|---|---|---|
| Parcial 1 | Bisección | \(10^{-6}\) | \(|b-a| \le \text{tol}\) |
| Parcial 1 | Newton-Raphson | \(10^{-6}\) | \(|\Delta x| \le \text{tol}\) |
| Parcial 2 | Gauss-Seidel | \(0.01\) | Tol ≥ |Va - Vn| |
| Parcial 2 | Relajaciones | \(0.01\) | Tol ≥ |residuos| |

## Ejemplo de funciones y gráficas

A continuación hay ejemplos de funciones que se pueden integrar con los métodos anteriores.

1. Función polinómica sencilla:

$$f(x) = x^2 - 2x + 1$$

2. Función con seno y crecimiento cuadrático:

$$g(x) = \sin(x) + 0.3 x^2$$

3. Función compleja con fracción, cosecante, exponencial y raíz:

$$h(x) = \frac{e^{x} \sqrt{x^2}}{\csc(x)} + \frac{\sqrt{x}}{x + 1}$$

Un ejemplo de integral para esta función es:

$$\int_{0}^{6} \frac{e^{x} \sqrt{x^2}}{\csc(x) + \sqrt{x}} \, dx$$

> Nota: esta función incluye cosecante, raíz y fracciones, por lo que las aproximaciones numéricas deben usarse con cuidado en intervalos donde el denominador se acerca a cero.

### Gráfica de la función y el área bajo la curva

![Área bajo la curva](../resources/images/integracion_area.png)

En el gráfico se muestra el área bajo la curva entre \(a\) y \(b\). Esto ayuda a entender por qué una integral definida representa un área.

### Aproximación con la regla del trapecio

![Regla del trapecio](../resources/images/integracion_trapecio.png)

El trapecio se dibuja como una serie de zonas trapezoidales que suman el área bajo \(f(x)\).

### Aproximación con Simpson 1/3

![Simpson 1/3](../resources/images/integracion_simpson.png)

Simpson 1/3 aproxima cada par de subintervalos con una parábola.

## Código en Parcial 3

El código de este tema se encuentra en `code/Parcial3/integracion_definida.py`.
También hay una interfaz gráfica disponible en `code/Parcial3/integracion_definida_app.py`.

El programa incluye:
- `trapezoidal_rule(f, a, b, N)`
- `midpoint_rule(f, a, b, N)`
- `simpson_one_third(f, a, b, N)`
- `simpson_three_eighths(f, a, b, N)`
- `plot_function_and_area(...)` para graficar el área bajo la curva
- `plot_trapezoids(...)` y `plot_simpson_approximation(...)` para dibujar cómo se aproximan las regiones

### Validadores de integración

Para validar los resultados se comparan las aproximaciones contra una referencia numérica o contra la integral exacta cuando existe. El error se define como:

$$\text{error} = |I_{aprox} - I_{exacta}|$$

Y el criterio de tolerancia es:

$$\text{error} \le \text{tol}$$

## Fórmulas importantes que se agregaron

- Paso de partición: \(h = \frac{b - a}{N}\)
- Punto de partición: \(x_i = a + i h\)
- Trapecio: \(A = \frac{h}{2} \left[f(x_0) + 2 \sum_{i=1}^{N-1} f(x_i) + f(x_N)\right]\)
- Punto medio: \(A = h \sum_{i=0}^{N-1} f\left(x_i + \frac{h}{2}\right)\)
- Simpson 1/3: \(A = \frac{h}{3} \left[f(x_0) + 4 f(x_1) + 2 f(x_2) + \cdots + 4 f(x_{N-1}) + f(x_N)\right]\)
- Simpson 3/8: \(A = \frac{3h}{8} \left[f(x_0) + 3 f(x_1) + 3 f(x_2) + 2 f(x_3) + \cdots + f(x_N)\right]\)
