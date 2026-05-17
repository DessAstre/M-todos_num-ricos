# Examen parcial 2 (1)
Universidad Autonoma de Chihuahua
Facultad de ingenieria
Francisco Javier Ponce Saenz
a325000
Metodos numericos

## 1) Método de relajaciones
Resolver el siguiente sistema de ecuaciones lineales simultaneas por el método de relajaciones, tomando en cuenta que la tolerancia es de 0.01 y un máximo de 8 iteraciones:

- 4x + 3y - 6z = 5
- 2x + 5y + z = 10
- -4x + y - z = -4

### Solución por relajaciones
Se normalizó el sistema para forzar diagonal = -1 y se aplicaron los registros T con pivote elegido por mayor residual.

- Vector final después de 8 iteraciones: x ≈ 1.274, y ≈ 1.515, z ≈ 0.417
- Criterio de convergencia: Tol = 0.01
- Resultado: no se alcanzó tolerancia en el máximo de 8 iteraciones

### Cuadro base (diagonal = -1)
| Ecu | x | y | z | R |
| --- | --- | --- | --- | --- |
| I | -1.000 | 0.250 | -0.250 | 1.000 |
| II | -0.400 | -1.000 | -0.200 | 2.000 |
| III | 0.666 | 0.500 | -1.000 | -0.833 |

### Evidencia
A continuación se muestran las capturas nuevas de relajaciones tomadas del programa:

![Relajaciones 1](relajaciones1.png)

![Relajaciones 2](relajaciones2.png)

![Relajaciones 3](relajaciones3.png)

## 2) Método de Gauss-Seidel
Resolver el sistema de ecuaciones lineales simultaneas por el método de Gauss-Seidel, tomando en cuenta que la tolerancia es de 0.001 y un máximo de 12 iteraciones:

- 6x + 3y - 5z = 5
- -2x - y + 6z = 7
- 4x - 7y + 2z = 5

### Solución por Gauss-Seidel
Se reordenaron las ecuaciones para mejorar el pivoteo y se calcularon los despejes correspondientes. El método convergió en 7 iteraciones con el siguiente resultado aproximado:

- Vector final: x ≈ 2.000, y ≈ 0.999, z ≈ 1.999
- Criterio de convergencia: Tol = 0.001
- Resultado: todas las variables cumplen la tolerancia en la iteración 7

### Matrices usadas
#### Matriz inicial
| Ecu | x | y | z | b |
| --- | --- | --- | --- | --- |
| I | 6.000 | 3.000 | -5.000 | 5.000 |
| II | -2.000 | -1.000 | 6.000 | 7.000 |
| III | 4.000 | -7.000 | 2.000 | 5.000 |

#### Matriz ordenada para iteración
| Ecu | x | y | z | b |
| --- | --- | --- | --- | --- |
| I | 6.000 | 3.000 | -5.000 | 5.000 |
| II | 4.000 | -7.000 | 2.000 | 5.000 |
| III | -2.000 | -1.000 | 6.000 | 7.000 |

#### Despejes
- x = (5 - 3y + 5z) / 6
- y = (-5 + 4x + 2z) / 7
- z = (7 + 2x + y) / 6

### Iteraciones Gauss-Seidel
| Var | V0 | 1a | T | 2a | T | 3a | T | 4a | T | 5a | T | 6a | T | 7a | T |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| x | 0.000 | 0.833 | NO | 2.122 | NO | 2.069 | NO | 2.001 | NO | 1.996 | NO | 1.999 | NO | 2.000 | OK |
| y | 0.000 | -0.238 | NO | 0.899 | NO | 1.046 | NO | 1.009 | NO | 0.998 | NO | 0.998 | OK | 0.999 | OK |
| z | 0.000 | 1.404 | NO | 2.023 | NO | 2.030 | NO | 2.001 | NO | 1.998 | NO | 1.999 | OK | 1.999 | OK |

### Evidencia
A continuación se muestran las capturas nuevas de Gauss-Seidel tomadas del programa:

![Gauss-Seidel 1](gaussseidel1.png)

![Gauss-Seidel 2](gaussseidel2.png)

![Gauss-Seidel 3](gaussseidel3.png)

---

Archivo PDF generado: `ExamenParcial2.pdf`
    
