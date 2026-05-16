import tkinter as tk
from tkinter import ttk, messagebox
import math

# -----------------------------
# Evaluar función
# -----------------------------
def f(x, expr):

    try:

        funciones = {
            "x": x,
            "exp": math.exp, #función exponencial
            "log": math.log, #logaritmo natural
            "log10": math.log10, #logaritmo base 10
            "sqrt": math.sqrt, #raíz cuadrada
            "sin": math.sin, #función seno
            "cos": math.cos, #función coseno
            "tan": math.tan, #función tangente
            "pi": math.pi, #número pi
            "e": math.e, #número e
            "abs": abs #función de valor absoluto, no math.abs que no existe
        }

        return eval(expr, {"__builtins__": None}, funciones) #evitar que el usuario ejecute código malicioso

    except:
        return None


# -----------------------------
# Aproximación
# -----------------------------
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


# -----------------------------
# Método Falsa Posición
# -----------------------------
def falsa_posicion():

    tabla.delete(*tabla.get_children())

    expr = entrada_funcion.get()

    try:
        a = float(entrada_a.get())
        b = float(entrada_b.get())
        tol = float(entrada_tol.get())
    except:
        messagebox.showerror("Error","Datos inválidos")
        return

    fa = aproximar(f(a,expr))
    fb = aproximar(f(b,expr))

    if fa is None or fb is None:
        messagebox.showerror("Error","Función inválida")
        return

    if fa*fb > 0:
        messagebox.showerror("Error",
         f"No hay cambio de signo en el intervalo.\nf(a) = {fa}\nf(b) = {fb}"
        )
        return

    if fa == 0:
        messagebox.showinfo("Resultado",f"Raíz exacta: {a}")
        #mostrar tabla con una sola fila
        tabla.insert("", "end", values=(
            1,a,b,fa,fb,0,a,"✔",fa
        ))
        return

    if fb == 0:
        messagebox.showinfo("Resultado",f"Raíz exacta: {b}")
        #mostrar tabla con una sola fila
        tabla.insert("", "end", values=(
            1,a,b,fa,fb,0,b,"✔",fb
        ))
        return

    i = 1

    while True:

        fa = aproximar(f(a,expr))
        fb = aproximar(f(b,expr))

        deltax = aproximar(((abs(fa))*(b-a))/(abs(fa)+abs(fb)))

        x = aproximar(a + deltax)

        fx = aproximar(f(x,expr))

        cumple = "✔" if tol >= deltax else "✘"

        tabla.insert("", "end", values=(
            i,a,b,fa,fb,deltax,x,cumple,fx
        ))

        if fx == 0:
            messagebox.showinfo("Resultado",
            f"Raíz aproximada encontrada: {x}")
            break

        if tol >= deltax:
            messagebox.showinfo("Resultado",
            f"Raíz aproximada: {x}")
            break

        if fa*fx < 0:
            b = x
        else:
            a = x

        i += 1


# -----------------------------
# Interfaz
# -----------------------------
ventana = tk.Tk()
ventana.title("Método de Falsa Posición")
ventana.geometry("1100x520")
ventana.configure(bg="#e7beff")


tk.Label(ventana,text="Función f(x)", bg="#e7beff").pack()
entrada_funcion = tk.Entry(ventana,width=30)
entrada_funcion.pack()

tk.Label(ventana,text="Límite inferior (a)", bg="#e7beff").pack()
entrada_a = tk.Entry(ventana)
entrada_a.pack()

tk.Label(ventana,text="Límite superior (b)", bg="#e7beff").pack()
entrada_b = tk.Entry(ventana)
entrada_b.pack()

tk.Label(ventana,text="Tolerancia", bg="#e7beff").pack()
entrada_tol = tk.Entry(ventana)
entrada_tol.pack()


tk.Label(ventana,text="Número de cifras", bg="#e7beff").pack()
entrada_dec = tk.Entry(ventana)
entrada_dec.pack()

tk.Label(ventana,text="Tipo de aproximación", bg="#e7beff").pack()
tipo_aprox = ttk.Combobox(
    ventana,
    values=["Redondeo","Truncamiento"]
)

tipo_aprox.pack()
tipo_aprox.current(0)

tk.Button(
    ventana,
    text="Calcular Falsa Posición", bg="#390855", fg="white",
    command=falsa_posicion
).pack(pady=10)


# -----------------------------
# Tabla
# -----------------------------
columnas = (
"i","a","b","f(a)","f(b)",
"Δx","x","Tol","f(x)"
)

tabla = ttk.Treeview(
    ventana,
    columns=columnas,
    show="headings"
)

for col in columnas:
    tabla.heading(col,text=col)
    tabla.column(col,width=110)

tabla.pack(fill="both",expand=True)

ventana.mainloop()