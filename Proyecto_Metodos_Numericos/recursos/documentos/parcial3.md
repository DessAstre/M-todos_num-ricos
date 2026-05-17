# Gauss-Seidel

## Explicación sencilla (principiante)

Cuando vemos un sistema lineal de ecuaciones con varias incógnitas, como:

    4x1 - x2       = 15
    -x1 + 4x2 - x3 = 10
    -x2 + 4x3 - x4 = 10
    -x3 + 3x4     = 10

queremos encontrar los números (x1, x2, x3, x4) que hacen verdad cada ecuación.

En lugar de resolverlo directamente con matrices inversas, el método de Gauss-Seidel genera una solución aproximada con repetición:

1. Parte de un valor inicial (por ejemplo, x=(0,0,0,0)).
2. Actualiza cada x_i una por una, usando siempre los valores ya actualizados en esa iteración.
3. Repite el ciclo hasta que el cambio entre una iteración y la siguiente sea muy pequeño.

Esta técnica es fácil de programar y adecuada cuando el sistema es grande o complejo.

## Tabla de iteraciones (Gauss-Seidel)

| iter | x1     | x2     | x3     | x4     | Δ (inf)    |
|------|--------|--------|--------|--------|------------|
| 1    | 3.7500 | 5.9375 | 5.5469 | 5.1823 | 5.9375     |
| 2    | 5.2344 | 6.6101 | 6.0954 | 5.6312 | 1.3125     |
| 3    | 5.8467 | 6.8095 | 6.2885 | 5.8511 | 0.6346     |
| 4    | 6.0342 | 6.8989 | 6.3606 | 5.9370 | 0.1875     |
| 5    | 6.0716 | 6.9241 | 6.3823 | 5.9664 | 0.0374     |
| 6    | 6.0836 | 6.9310 | 6.3893 | 5.9781 | 0.0121     |
| 7    | 6.0878 | 6.9331 | 6.3914 | 5.9819 | 0.0051     |

> Notas:
> - Se usó el sistema de prueba:
> > 4x1 - x2        = 15
> > -x1 + 4x2 - x3  = 10
> > -x2 + 4x3 - x4  = 10
> > -x3 + 3x4      = 10
> - `Δ (inf)` es el máximo cambio absoluto entre iteraciones.

# Relajaciones

## Hoja de cálculo de iteraciones (SOR — forma de T)

| iter | x1     | x2     | x3     | x4     |   | R1       | R2       | R3       | R4       | ‖R‖_∞  |
|------|--------|--------|--------|--------|---|----------|----------|----------|----------|--------|
| 1    | 3.7500 | 5.9375 | 5.5469 | 5.1823 | T | 5.9375   | -4.4531  | -1.0678  | 0.0000   | 5.9375 |
| 2    | 5.3641 | 6.6683 | 6.2066 | 5.7046 | T | 0.2119   | -5.1025  | -2.4535  | -0.9072  | 5.1025 |
| 3    | 5.6628 | 6.8518 | 6.3834 | 5.9286 | T | -0.7994  | -5.3610  | -2.7532  | -1.4024  | 5.3610 |
| 4    | 5.7698 | 6.9062 | 6.4303 | 5.9914 | T | -1.1730  | -5.4247  | -2.8236  | -1.5439  | 5.4247 |
| 5    | 5.8090 | 6.9305 | 6.4511 | 6.0219 | T | -1.3055  | -5.4619  | -2.8520  | -1.6146  | 5.4619 |
| 6    | 5.8237 | 6.9391 | 6.4591 | 6.0334 | T | -1.3557  | -5.4736  | -2.8639  | -1.6411  | 5.4736 |
| 7    | 5.8292 | 6.9435 | 6.4631 | 6.0392 | T | -1.3733  | -5.4817  | -2.8697  | -1.6545  | 5.4817 |

> Notas:
> - El símbolo `T` separa la parte izquierda (variables x) y la derecha (residuales R). 
> - Residual: `R = b - A x` (cada fila) y ‖R‖_∞ = max(|R_i|).
> - El ejercicio se basa en el mismo sistema de prueba del apartado Gauss-Seidel.

## Validadores de tema (verificación de condiciones previas)

- **Matriz cuadrada** (`_check_square`): requiere que A sea n×n y b dimensión n.
- **Dominancia diagonal** (`_is_diagonal_dominant`): si se cumple, la convergencia está garantizada en Gauss-Seidel/SOR (aunque el código admite no dominante mostrando advertencia en `verbose`).
- **Omega válido** (`sor`): comprueba `0 < ω < 2`.
- **Ningún elemento diagonal cero**: protege contra división por cero en iteración.

> Dato de verificación: En `gauss_seidel_relajaciones.py` hay funciones de validación activas y llamadas desde ambos métodos.