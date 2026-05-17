# Ajuste de Curvas por Mínimos Cuadrados
## Objetivo
- Dado un conjunto de datos (x_i, y_i), encontrar el polinomio f(x) de grado 1, 2 o 3 que minimice la desviación (SSE).
- Usar el método de eliminaicón de Gauss en SSELS para resolver K0, K1, K2, K3.
- Generar evidencia tipo PDF con:
  - tabla de sumas (Σx, Σx^2, Σx^3, Σx^4, Σxy, Σx^2y, Σx^3y)
  - SSELS 4x4 (grado 3)
  - pasos de Gauss (operaciones e iteraciones)
  - validación de la mejor curva por RSS

## Datos de ejemplo (tabla de entrada)
| X  | Y  |
|:--:|:--:|
| -3 | 21 |
| -2 | 14 |
| -1 | 9  |
| 0  | 6  |
| 1  | 5  |
| 2  | 6  |
| 3  | 9  |

## Cálculo de sumas necesarias
- ΣX = 0
- ΣY = 70
- ΣX^2 = 28
- ΣX^3 = 0
- ΣX^4 = 196
- ΣXY = -56
- ΣX^2Y = 364
- ΣX^3Y = -392
- n = 7

## Sistema normal (SSELS 4x4) para grado 3
A =
```
[ 7   0  28   0 ]
[ 0  28   0 196 ]
[28   0 196   0 ]
[ 0 196   0 1588]
```

b = [70, -56, 364, -392]^T

## Resolución de Gauss
- K0 = 6.0
- K1 = -2.0
- K2 = 1.0
- K3 = 0.0

Curvas obtenidas:
- Y1 (grado 1): 6 - 2x
- Y2 (grado 2): 6 - 2x + x^2
- Y3 (grado 3): 6 - 2x + x^2 (K3=0)

## Desviaciones (RSS)
- S1 = 196
- S2 = 0
- S3 = 0

**Curva más exacta: grado 2 (Y2), porque RSS mínimo**

## Tabla de verificación (margen de error)
| X  | Y | Y1 | (Y-Y1)^2 | Y2 | (Y-Y2)^2 |
|:--:|:-:|:--:|:--------:|:--:|:--------:|
| -3 |21 |12  |81        |21  |0         |
| -2 |14 |10  |16        |14  |0         |
| -1 |9  |8   |1         |9   |0         |
| 0  |6  |6   |0         |6   |0         |
| 1  |5  |4   |1         |5   |0         |
| 2  |6  |2   |16        |6   |0         |
| 3  |9  |0   |81        |9   |0         |
| Σ  |   |    |196       |    |0         |

## Valores solicitados (aplicar Y2)
| X  | Y (grado 2) |
|:--:|:-----------:|
| -5 | 41          |
| -4 | 30          |
| 5  | 21          |
| 6  | 30          |

## Instrucciones de uso con el programa
1. Ejecutar: `python3 code/ajuste_curvas_app.py`
2. Ingresar los datos en la tabla X/Y (sin preguntas, solo valores).
3. Elegir grado o modo automático.
4. `Calcular`: muestra K, fórmula, RSS, extremos y validación.
5. `Mostrar SSELS 4x4`: muestra el sistema 4x4 (matriz + vector) en ventana nueva.
6. `Graficar Funciones`: abre otra ventana con las gráficas.

---
*Este documento ahora está alineado con el PDF de Ajuste de Curvas y es evidencia de entrega.*