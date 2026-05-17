import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
import math

x = sp.symbols('x')

# -------------------------
# Función de aproximación
# -------------------------
def aproximar(valor):

    dec = int(entrada_dec.get())
    tipo = tipo_aprox.get()

    if tipo == "Redondeo":
        return round(valor, dec)

    if tipo == "Truncamiento":
        factor = 10**dec
        return math.trunc(valor*factor)/factor

    return valor


# -------------------------
# NEWTON-RAPHSON NORMAL
# -------------------------
def newton():

    try:
        funcion = entrada_funcion.get()
        x0 = float(entrada_x0.get())
        tol = float(entrada_tol.get())

        f = sp.sympify(funcion)
        f1 = sp.diff(f,x)

        f_num = sp.lambdify(x,f)
        f1_num = sp.lambdify(x,f1)

    except:
        messagebox.showerror("Error","Datos inválidos")
        return

    tabla.delete(*tabla.get_children())

    # columnas SIN segunda derivada
    columnas = ("i","x0","f(x0)","f'(x0)","Δx","x1","Tol","f(x1)")
    tabla["columns"] = columnas

    for col in columnas:
        tabla.heading(col,text=col)
        tabla.column(col,width=120)

    i = 1

    while True:

        fx0 = aproximar(f_num(x0))
        fpx0 = aproximar(f1_num(x0))

        if fpx0 == 0:
            messagebox.showerror("Error","Derivada = 0")
            return

        delta = aproximar(-fx0/fpx0)
        x1 = aproximar(x0 + delta)
        fx1 = aproximar(f_num(x1))

        cumple = "✔" if abs(delta) < tol else "✘"

        tabla.insert("", "end", values=(
            i,x0,fx0,fpx0,delta,x1,cumple,fx1
        ))

        if abs(delta) < tol:
            break

        x0 = x1
        i += 1


# -------------------------
# NEWTON-RAPHSON MEJORADO
# -------------------------
def newton_mejorado():

    try:
        funcion = entrada_funcion.get()
        x0 = float(entrada_x0.get())
        tol = float(entrada_tol.get())

        f = sp.sympify(funcion)
        f1 = sp.diff(f,x)
        f2 = sp.diff(f1,x)

        f_num = sp.lambdify(x,f)
        f1_num = sp.lambdify(x,f1)
        f2_num = sp.lambdify(x,f2)

    except:
        messagebox.showerror("Error","Datos inválidos")
        return

    tabla.delete(*tabla.get_children())

    # columnas CON segunda derivada
    columnas = (
    "i","x0","f(x0)","f'(x0)","f''(x0)",
    "Δx","x1","Tol","f(x1)"
    )

    tabla["columns"] = columnas

    for col in columnas:
        tabla.heading(col,text=col)
        tabla.column(col,width=110)

    i = 1

    while True:

        fx0 = aproximar(f_num(x0))
        fpx0 = aproximar(f1_num(x0))
        fppx0 = aproximar(f2_num(x0))

        delta = aproximar(
            1 / ((-(fpx0 / fx0)) + 0.5 * (fppx0 / fpx0))
        )

        x1 = aproximar(x0 + delta)
        fx1 = aproximar(f_num(x1))

        cumple = "✔" if abs(delta) < tol else "✘"

        tabla.insert("", "end", values=(
            i,x0,fx0,fpx0,fppx0,delta,x1,cumple,fx1
        ))

        if abs(delta) < tol:
            break

        x0 = x1
        i += 1


# -------------------------
# INTERFAZ
# -------------------------
ventana = tk.Tk()
ventana.title("Método Newton-Raphson")
ventana.geometry("1100x520")

tk.Label(ventana,text="Función f(x)").pack()
entrada_funcion = tk.Entry(ventana,width=30)
entrada_funcion.pack()

tk.Label(ventana,text="Valor inicial x0").pack()
entrada_x0 = tk.Entry(ventana)
entrada_x0.pack()

tk.Label(ventana,text="Tolerancia").pack()
entrada_tol = tk.Entry(ventana)
entrada_tol.pack()

tk.Label(ventana,text="Tipo de aproximación").pack()

tipo_aprox = ttk.Combobox(
    ventana,
    values=["Redondeo","Truncamiento"]
)
tipo_aprox.pack()
tipo_aprox.current(0)

tk.Label(ventana,text="Número de decimales").pack()
entrada_dec = tk.Entry(ventana)
entrada_dec.pack()

tk.Button(
    ventana,
    text="Newton-Raphson",
    command=newton
).pack(pady=5)

tk.Button(
    ventana,
    text="Newton-Raphson Mejorado",
    command=newton_mejorado
).pack(pady=5)

tabla = ttk.Treeview(
    ventana,
    show="headings"
)

tabla.pack(fill="both",expand=True)

ventana.mainloop()