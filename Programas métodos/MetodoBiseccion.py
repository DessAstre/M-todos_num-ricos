import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
import math

x = sp.symbols('x')

def aproximar(valor):

    dec = int(entrada_dec.get())
    tipo = tipo_aprox.get()

    if tipo == "Redondeo":
        return round(valor, dec)

    if tipo == "Truncamiento":

        factor = 10**dec

        if valor >= 0:
            return math.floor(valor*factor)/factor
        else:
            return math.ceil(valor*factor)/factor


def signo(v):

    if v > 0:
        return "+"
    elif v < 0:
        return "-"
    else:
        return "0"


def biseccion():

    try:

        funcion = entrada_funcion.get()
        a = float(entrada_a.get())
        b = float(entrada_b.get())
        tol = float(entrada_tol.get())

        f = sp.sympify(funcion)
        f_num = sp.lambdify(x,f)

    except:
        messagebox.showerror("Error","Datos inválidos")
        return

    tabla.delete(*tabla.get_children())

    a = aproximar(a)
    b = aproximar(b)

    fa = aproximar(f_num(a)) #f_numb es la función evaluada numéricamente, con la aproximación aplicada
    fb = aproximar(f_num(b))

    if fa == 0:
        messagebox.showinfo("Resultado",f"Raíz exacta: {a}")
        #mostrar tabla con una sola fila
        tabla.insert("", "end", values=(
            1,a,b,fa,fb,a,"✔",fa
        ))
        return

    if fb == 0:
        messagebox.showinfo("Resultado",f"Raíz exacta: {b}")
        #mostrar tabla con una sola fila
        tabla.insert("", "end", values=(
            1,a, b,fa,fb,b,"✔",fb
        ))
        return

    if fa*fb > 0:
        messagebox.showerror("Error",
        f"No hay cambio de signo en el intervalo.\nf(a) = {fa}\nf(b) = {fb}\nNo existe raíz en ese intervalo.")
        return

    i = 1

    while True:

        fa = aproximar(f_num(a))
        fb = aproximar(f_num(b))

        c = aproximar((b-a)/2)
        x1 = aproximar(a + c)

        fx = aproximar(f_num(x1))

        cumple = "✔" if tol >= c else "✘"

        tabla.insert("", "end", values=(
            i,
            a,
            b,
            fa,
            signo(fa),
            fb,
            signo(fb),
            c,
            x1,
            cumple,
            fx
        ))

        if fx == 0:
            messagebox.showinfo("Resultado",
            f"Raíz exacta encontrada: {x1}")
            
            break

        if tol >= c:
            messagebox.showinfo("Resultado",
            f"Raíz aproximada: {x1}")
            break

        if fa*fx < 0:
            b = x1
        else:
            a = x1

        i += 1


ventana = tk.Tk()
ventana.title("Método de Bisección")
ventana.geometry("1200x520")
ventana.configure(bg="#fcdada")

tk.Label(ventana,text="Función f(x)", bg="#fcdada").pack()

entrada_funcion = tk.Entry(ventana,width=30)
entrada_funcion.pack()

tk.Label(ventana,text="Límite inferior (a)", bg="#fcdada").pack()
entrada_a = tk.Entry(ventana)
entrada_a.pack()

tk.Label(ventana,text="Límite superior (b)", bg="#fcdada").pack()
entrada_b = tk.Entry(ventana)
entrada_b.pack()

tk.Label(ventana,text="Tolerancia", bg="#fcdada").pack()
entrada_tol = tk.Entry(ventana)
entrada_tol.pack()


tk.Label(ventana,text="Número de cifras", bg="#fcdada").pack()
entrada_dec = tk.Entry(ventana)
entrada_dec.pack()

tk.Label(ventana,text="Tipo de aproximación", bg="#fcdada").pack()

tipo_aprox = ttk.Combobox(
    ventana,
    values=["Redondeo","Truncamiento"]
)
tipo_aprox.pack()
tipo_aprox.current(0)

tk.Button(
    ventana,
    text="Calcular Bisección", bg="#660016", fg="white",
    command=biseccion
).pack(pady=10)

columnas = (
"i","a","b",
"f(a)","sgn f(a)",
"f(b)","sgn f(b)",
"c","x","Tol","f(x)"
)

tabla = ttk.Treeview(
    ventana,
    columns=columnas,
    show="headings"
)

for col in columnas:
    tabla.heading(col,text=col)
    tabla.column(col,width=100)

tabla.pack(fill="both",expand=True)

ventana.mainloop()