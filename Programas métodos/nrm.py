import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
import math

x = sp.symbols('x')

# -------------------------
# Función de aproximación
# -------------------------
def aproximar(valor):
    dec = int(entrada_cifras.get())
    tipo = tipo_aprox.get()

    if tipo == "Redondeo":
        return round(valor, dec)
    elif tipo == "Truncamiento":
        factor = 10 ** dec
        return math.trunc(valor * factor) / factor
    return valor


# -------------------------
# Método Newton-Raphson Mejorado
# -------------------------
def calcular():
    try:

        tabla.delete(*tabla.get_children())

        # Lectura de datos
        funcion = sp.sympify(entrada_funcion.get())
        x0 = float(entrada_x0.get())
        tolerancia = float(entrada_tol.get())

        # Derivadas
        f = funcion
        f1 = sp.diff(f, x)
        f2 = sp.diff(f1, x)

        f_num = sp.lambdify(x, f, "math")
        f1_num = sp.lambdify(x, f1, "math")
        f2_num = sp.lambdify(x, f2, "math")

        iteracion = 1

        while True:

            fx0 = f_num(x0)
            f1x0 = f1_num(x0)
            f2x0 = f2_num(x0)

            # Fórmula corregida
            delta = 1 / ((-(f1x0 / fx0)) + 0.5 * (f2x0 / f1x0))

            x1 = x0 + delta
            fx1 = f_num(x1)

            tol = "✔" if abs(delta) < tolerancia else "✘"

            tabla.insert("", "end", values=(

                iteracion,
                aproximar(x0),
                aproximar(fx0),
                aproximar(f1x0),
                aproximar(f2x0),
                aproximar(delta),
                aproximar(x1),
                tol,
                aproximar(fx1)

            ))

            if abs(delta) < tolerancia:
                break

            x0 = x1
            iteracion += 1

    except Exception as e:
        messagebox.showerror("Error", str(e))


# -------------------------
# Interfaz gráfica
# -------------------------
ventana = tk.Tk()
ventana.title("Método de Newton-Raphson Mejorado 2D")
ventana.geometry("950x500")
ventana.configure(bg="#fdf5a9")

frame = tk.Frame(ventana, bg="#fdf5a9")
frame.pack(pady=10)

tk.Label(frame, text="Función f(x):", bg="#fdf5a9").pack()
entrada_funcion = tk.Entry(frame, width=25)
entrada_funcion.pack()

tk.Label(frame, text="Valor inicial x0:", bg="#fdf5a9").pack()
entrada_x0 = tk.Entry(frame)
entrada_x0.pack()

tk.Label(frame, text="Tolerancia:", bg="#fdf5a9").pack()
entrada_tol = tk.Entry(frame)
entrada_tol.pack()

tk.Label(frame, text="Cifras decimales:", bg="#fdf5a9").pack()
entrada_cifras = tk.Entry(frame)
entrada_cifras.pack()

tk.Label(frame, text="Tipo de aproximación:", bg="#fdf5a9").pack()
tipo_aprox = ttk.Combobox(frame, values=["Redondeo", "Truncamiento"])
tipo_aprox.pack()
tipo_aprox.current(0)

# Botón Calcular
btn = tk.Button(ventana, text="Calcular", bg="#492D02", fg="white", command=calcular)
btn.pack(pady=10)

# Tabla
columnas = ("It", "x0", "f(x0)", "f'(x0)", "f''(x0)", "Δx", "x1", "Tol", "f(x1)")
tabla = ttk.Treeview(ventana, columns=columnas, show="headings")

for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=100, anchor="center")

tabla.pack(fill="both", expand=True)

ventana.mainloop()