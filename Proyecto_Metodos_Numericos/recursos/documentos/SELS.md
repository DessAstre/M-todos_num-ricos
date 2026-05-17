S.S.E.L.S
Metodos Aproximados
Gauss-seidel

Procedimiento
Cumplir requisitos:

{Que la "Diagonal" de la [A] sea mayor en su linea

1) 
{ estos son los despejes para los valores de x , y , z, ya que comenzaremos con valores inicales en 0.
 x= 6+y-z
    ------
       6
 y= 4-2x+z
    -------
      3
 z= 4-3x+5z
    -------
       6
Se verifica renglon por renglon cual es el mayor valor de cada variable x, y, z

}

^
^
^
2x+[3y]-z=4 ------------------------ 
[6x]-y +z=6
-3x+5y-[6z]=-4

[6x]-y+z=6
2x+[3y]-z=4
-3x+5y-[6z]=-4

     x    y   z
[A]= [2] [3] [-1]
     [6] [-1] [1]
     [-3] [5] [-6]



}
2) Despejar la Variavle de la "D"
3) Armar cuadro con Vo= 0
Se inician iteraciones y se termina cuando se cumpla la Tol >= |Va-Vn| en todas las variables siendo Tol=0.01


Cuadro de calculo para SELS por gauss-seidel

_Var_|_Vo_|_1ra iteracion_ |_Tol_|_2da Iteracion_ |_Tol_ |_3ra Iteracion_ |_Tol_|_n Iteracion_|
   x | 0  |                |     |                |      |                |     |             |
   y | 0  |                |     |                |      |                |     |             |
   z | 0  |                |     |                |      |                |     |             |

Siendo que que en los despejes de las ecuaciones lineales creadas, quedan en valor de x, y , z es decir para encontrar primero x se sustituye el valor de y=0 y z=0 para la primera iteracion, esto hast a cumplir Tol >=|Vn-Va| Siendo Vn= Valor nuevo encontrado en la iteracion para esa varible  y Va= Valor anterior encontrado en la iteracion para esa variable

Relajaciones
1) Cumplir los requisitos (Igual que en gauss-Seidel)
2) Igualar a 0 la SELS
3) "Diagonal mayor" en su linea coefiente igual=-1

    2x-5y+4z=3
    -x+3y-6z=-5
    -4x-y-z=-10

    Se necesita hacer -1 su diagonal mayor, entonces se divide entre la constante que acompana a la variable con la constante mayor (Encerrada en [] para tomar de ejemplo cual es el que tiene la constante mayor con su variable)

    2x-[5y]+4z-3=0 ------- {5}
    -x+3y-[6z]+5=0---------{6}
    -[4x]-y-z+10=0----------{4}

    Ya acomodando la diagonal mayor con la division de su numero mayor para hacer -1 la diagonal mayor

    -x - 025y - 0.25z + 2.5=0
    0.4x - y  + 0.8z  - 0.6=0
    -0.166x + 0.5y - z + 0.833=0

    4) Armar cuadro base
        _Var\Ecuaci_|_X_   |_Y_ |_Z_   |_R_  |
        ------------|----  |-----|---- |-----|
            I       | -1   |-0.25|-0.25| 2.5 |
            II      |  0.4 | -1  | 0.8 |-0.6 |
            III     |-0.166| 0.5 | -1  |0.833|

   5) Armar registros T:
      1 x C\variable
      D= Variable
      H=resiudo

   Aqui son las iteraciones
      x|R1                       
      -|-
       |2.5
    2.5|-2.5
      -|----
       | 0    ajustando a 0.

       y|R
        |-0.6
        |1
        |-
        |0.4

        z|R
         |0.833
         |-0.415
         |------
         |0.418

   6) Seleccionar Residuo mas alejado de 0, se coloca en el lado de la Variable(Pivote)
   7) El pivote se multiplica por cada uno de los coeficientes de la tabla de la variable que corresponde
   8) Ajustar cada Residuo, el residuo es la tolerancia. Todos los residuos deben de cumplir con la Tol >=|Residuos|( es condicional para terminar segun el metodo de relajaciones, es necesario agregar mas)



   Tarea para dia de examen de entrando de vacaciones:
   Traer El primer jueves entrando de vacaiones, dos aplicaciones de una solucion de un SSELS
    una aplicacion en general
    Aplicacion a nuestra carrera
