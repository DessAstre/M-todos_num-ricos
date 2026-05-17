import tkinter as tk
from tkinter import ttk, messagebox
import math
from tkinter import font as tkfont


# -----------------------------
# Evaluar función de forma segura
def f(x, expr):
    try:
        funciones = {
            "x": x,
            "exp": math.exp,
            "log": math.log,
            "log10": math.log10,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "pi": math.pi,
            "e": math.e,
            "abs": abs
        }

        return eval(expr, {"__builtins__": None}, funciones)
    except:
        return None


# -----------------------------
# Aproximación
# -----------------------------
def aproximar(valor, dec, tipo):
    try:
        dec = int(dec)
    except:
        dec = 6

    if tipo == "Redondeo":
        return round(valor, dec)

    if tipo == "Truncamiento":
        factor = 10 ** dec
        if valor >= 0:
            return math.floor(valor * factor) / factor
        else:
            return math.ceil(valor * factor) / factor

    return valor


# -----------------------------
# Ventana de resultado: mostrar tabla completa
# -----------------------------
def mostrar_tabla_resultado(root, tabla_original, titulo="Resultados"):
    top = tk.Toplevel(root)
    top.title(titulo)
    top.geometry("900x420")

    cols = tabla_original["columns"]
    tree = ttk.Treeview(top, columns=cols, show="headings")

    # copiar encabezados y anchos
    for col in cols:
        tree.heading(col, text=col)
        try:
            w = tabla_original.column(col)["width"]
            tree.column(col, width=w)
        except:
            tree.column(col, width=100)

    # copiar filas
    for iid in tabla_original.get_children():
        vals = tabla_original.item(iid).get("values", [])
        tree.insert("", "end", values=vals)

    vsb = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(top, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.pack(fill="both", expand=True, side="top")
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    frm = tk.Frame(top)
    frm.pack(pady=6)

    def cerrar_todo():
        root.destroy()

    def reingresar():
        top.destroy()

    tk.Button(frm, text="Cerrar", bg="#b22222", fg="white", command=cerrar_todo).pack(side="left", padx=8)
    tk.Button(frm, text="Reingresar datos", command=reingresar).pack(side="left", padx=8)


# -----------------------------
# Implementación: Falsa posición
# -----------------------------
def ejecutar_falsa_posicion(entries, tabla, root):
    tabla.delete(*tabla.get_children())

    expr = entries['funcion'].get()
    try:
        a = float(entries['a'].get())
        b = float(entries['b'].get())
        tol = float(entries['tol'].get())
    except:
        messagebox.showerror("Error", "Datos inválidos")
        return

    dec = entries['dec'].get()
    tipo = entries['tipo'].get()

    fa = aproximar(f(a, expr), dec, tipo)
    fb = aproximar(f(b, expr), dec, tipo)

    if fa is None or fb is None:
        messagebox.showerror("Error", "Función inválida")
        return

    if fa * fb > 0:
        messagebox.showerror("Error",
                             f"No hay cambio de signo en el intervalo.\nf(a) = {fa}\nf(b) = {fb}")
        return

    if fa == 0:
        tabla.insert("", "end", values=(1, a, b, fa, fb, 0, a, "✔", fa))
        mostrar_tabla_resultado(root, tabla, titulo=f"Resultado: raíz {a}")
        return

    if fb == 0:
        tabla.insert("", "end", values=(1, a, b, fa, fb, 0, b, "✔", fb))
        mostrar_tabla_resultado(root, tabla, titulo=f"Resultado: raíz {b}")
        return

    i = 1
    while True:
        fa = aproximar(f(a, expr), dec, tipo)
        fb = aproximar(f(b, expr), dec, tipo)

        deltax = aproximar(((abs(fa)) * (b - a)) / (abs(fa) + abs(fb)), dec, tipo)
        x = aproximar(a + deltax, dec, tipo)
        fx = aproximar(f(x, expr), dec, tipo)

        cumple = "✔" if tol >= deltax else "✘"

        tabla.insert("", "end", values=(i, a, b, fa, fb, deltax, x, cumple, fx))

        if fx == 0:
            mostrar_tabla_resultado(root, tabla, titulo=f"Resultado: raíz {x}")
            break

        if tol >= deltax:
            mostrar_tabla_resultado(root, tabla, titulo=f"Resultado aproximado: {x}")
            break

        if fa * fx < 0:
            b = x
        else:
            a = x

        i += 1


# -----------------------------
# Implementación: Bisección
# -----------------------------
def signo(v):
    if v > 0:
        return "+"
    elif v < 0:
        return "-"
    else:
        return "0"


def ejecutar_biseccion(entries, tabla, root):
    tabla.delete(*tabla.get_children())

    expr = entries['funcion'].get()
    try:
        a = float(entries['a'].get())
        b = float(entries['b'].get())
        tol = float(entries['tol'].get())
    except:
        messagebox.showerror("Error", "Datos inválidos")
        return

    dec = entries['dec'].get()
    tipo = entries['tipo'].get()

    a = aproximar(a, dec, tipo)
    b = aproximar(b, dec, tipo)

    fa = aproximar(f(a, expr), dec, tipo)
    fb = aproximar(f(b, expr), dec, tipo)

    if fa == 0:
        tabla.insert("", "end", values=(1, a, b, fa, signo(fa), fb, signo(fb), 0, a, "✔", fa))
        mostrar_tabla_resultado(root, tabla, titulo=f"Resultado: raíz {a}")
        return

    if fb == 0:
        tabla.insert("", "end", values=(1, a, b, fa, signo(fa), fb, signo(fb), 0, b, "✔", fb))
        mostrar_tabla_resultado(root, tabla, titulo=f"Resultado: raíz {b}")
        return

    if fa * fb > 0:
        messagebox.showerror("Error",
                             f"No hay cambio de signo en el intervalo.\nf(a) = {fa}\nf(b) = {fb}\nNo existe raíz en ese intervalo.")
        return

    i = 1
    while True:
        fa = aproximar(f(a, expr), dec, tipo)
        fb = aproximar(f(b, expr), dec, tipo)

        c = aproximar((b - a) / 2, dec, tipo)
        x1 = aproximar(a + c, dec, tipo)

        fx = aproximar(f(x1, expr), dec, tipo)

        cumple = "✔" if tol >= c else "✘"

        tabla.insert("", "end", values=(i, a, b, fa, signo(fa), fb, signo(fb), c, x1, cumple, fx))

        if fx == 0:
            mostrar_tabla_resultado(root, tabla, titulo=f"Resultado: raíz {x1}")
            break

        if tol >= c:
            mostrar_tabla_resultado(root, tabla, titulo=f"Resultado aproximado: {x1}")
            break

        if fa * fx < 0:
            b = x1
        else:
            a = x1

        i += 1


def crear_pestana_biseccion(notebook, root):
    frame = ttk.Frame(notebook)

    # Inputs (estilizado)
    frm_inputs = tk.LabelFrame(frame, text="Entradas", padx=10, pady=10)
    frm_inputs.pack(fill="x", padx=10, pady=8)

    label_font = ("Segoe UI", 10)
    entry_font = ("Segoe UI", 10)

    tk.Label(frm_inputs, text="Función f(x)", font=label_font).grid(row=0, column=0, sticky="w", padx=4, pady=4)
    entrada_funcion = tk.Entry(frm_inputs, width=36, font=entry_font)
    entrada_funcion.grid(row=0, column=1, sticky="w", padx=4, pady=4)

    tk.Label(frm_inputs, text="Límite inferior (a)", font=label_font).grid(row=1, column=0, sticky="w", padx=4, pady=4)
    entrada_a = tk.Entry(frm_inputs, font=entry_font)
    entrada_a.grid(row=1, column=1, sticky="w", padx=4, pady=4)

    tk.Label(frm_inputs, text="Límite superior (b)", font=label_font).grid(row=2, column=0, sticky="w", padx=4, pady=4)
    entrada_b = tk.Entry(frm_inputs, font=entry_font)
    entrada_b.grid(row=2, column=1, sticky="w", padx=4, pady=4)

    tk.Label(frm_inputs, text="Tolerancia", font=label_font).grid(row=3, column=0, sticky="w", padx=4, pady=4)
    entrada_tol = tk.Entry(frm_inputs, font=entry_font)
    entrada_tol.grid(row=3, column=1, sticky="w", padx=4, pady=4)

    tk.Label(frm_inputs, text="Número de cifras", font=label_font).grid(row=4, column=0, sticky="w", padx=4, pady=4)
    entrada_dec = tk.Entry(frm_inputs, font=entry_font)
    entrada_dec.grid(row=4, column=1, sticky="w", padx=4, pady=4)

    tk.Label(frm_inputs, text="Tipo de aproximación", font=label_font).grid(row=5, column=0, sticky="w", padx=4, pady=4)
    tipo_aprox = ttk.Combobox(frm_inputs, values=["Redondeo", "Truncamiento"], width=18)
    tipo_aprox.grid(row=5, column=1, sticky="w", padx=4, pady=4)
    tipo_aprox.current(0)

    entries = {'funcion': entrada_funcion, 'a': entrada_a, 'b': entrada_b, 'tol': entrada_tol, 'dec': entrada_dec, 'tipo': tipo_aprox}

    btn = tk.Button(frm_inputs, text="Calcular Bisección", bg="#660016", fg="white", font=("Segoe UI", 10, "bold"),
                    command=lambda: ejecutar_biseccion(entries, tabla, root))
    btn.grid(row=6, column=0, columnspan=2, pady=8, ipadx=8)

    # Tabla
    columnas = ("i", "a", "b", "f(a)", "sgn f(a)", "f(b)", "sgn f(b)", "c", "x", "Tol", "f(x)")
    tabla = ttk.Treeview(frame, columns=columnas, show="headings")
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=90)
    tabla.pack(fill="both", expand=True, padx=6, pady=(0,6))

    return frame, entries


def crear_pestana_falsa(notebook, root):
    frame = ttk.Frame(notebook)
    frm_inputs = tk.LabelFrame(frame, text="Entradas", padx=10, pady=10)
    frm_inputs.pack(fill="x", padx=10, pady=8)

    label_font = ("Segoe UI", 10)
    entry_font = ("Segoe UI", 10)

    tk.Label(frm_inputs, text="Función f(x)", font=label_font).grid(row=0, column=0, sticky="w", padx=4, pady=4)
    entrada_funcion = tk.Entry(frm_inputs, width=36, font=entry_font)
    entrada_funcion.grid(row=0, column=1, sticky="w", padx=4, pady=4)

    tk.Label(frm_inputs, text="Límite inferior (a)", font=label_font).grid(row=1, column=0, sticky="w", padx=4, pady=4)
    entrada_a = tk.Entry(frm_inputs, font=entry_font)
    entrada_a.grid(row=1, column=1, sticky="w", padx=4, pady=4)

    tk.Label(frm_inputs, text="Límite superior (b)", font=label_font).grid(row=2, column=0, sticky="w", padx=4, pady=4)
    entrada_b = tk.Entry(frm_inputs, font=entry_font)
    entrada_b.grid(row=2, column=1, sticky="w", padx=4, pady=4)

    tk.Label(frm_inputs, text="Tolerancia", font=label_font).grid(row=3, column=0, sticky="w", padx=4, pady=4)
    entrada_tol = tk.Entry(frm_inputs, font=entry_font)
    entrada_tol.grid(row=3, column=1, sticky="w", padx=4, pady=4)

    tk.Label(frm_inputs, text="Número de cifras", font=label_font).grid(row=4, column=0, sticky="w", padx=4, pady=4)
    entrada_dec = tk.Entry(frm_inputs, font=entry_font)
    entrada_dec.grid(row=4, column=1, sticky="w", padx=4, pady=4)

    tk.Label(frm_inputs, text="Tipo de aproximación", font=label_font).grid(row=5, column=0, sticky="w", padx=4, pady=4)
    tipo_aprox = ttk.Combobox(frm_inputs, values=["Redondeo", "Truncamiento"], width=18)
    tipo_aprox.grid(row=5, column=1, sticky="w", padx=4, pady=4)
    tipo_aprox.current(0)

    entries = {'funcion': entrada_funcion, 'a': entrada_a, 'b': entrada_b, 'tol': entrada_tol, 'dec': entrada_dec, 'tipo': tipo_aprox}

    btn = tk.Button(frm_inputs, text="Calcular Falsa Posición", bg="#390855", fg="white", font=("Segoe UI", 10, "bold"),
                    command=lambda: ejecutar_falsa_posicion(entries, tabla, root))
    btn.grid(row=6, column=0, columnspan=2, pady=8, ipadx=6)

    columnas = ("i", "a", "b", "f(a)", "f(b)", "Δx", "x", "Tol", "f(x)")
    tabla = ttk.Treeview(frame, columns=columnas, show="headings")
    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, width=100)
    tabla.pack(fill="both", expand=True, padx=6, pady=(0,6))

    return frame, entries


def main():
    root = tk.Tk()
    root.title("Métodos de Raíces: Bisección y Falsa Posición")
    root.geometry("1920x1080")
    root.configure(bg="#f3f6f9")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=8, pady=8)

    frame_bis, entries_bis = crear_pestana_biseccion(notebook, root)
    frame_fal, entries_fal = crear_pestana_falsa(notebook, root)

    notebook.add(frame_bis, text="Bisección")
    notebook.add(frame_fal, text="Falsa Posición")

    # Ejemplo por defecto
    ejemplo_func = "x**3 - x - 2"
    entries_bis['funcion'].insert(0, ejemplo_func)
    entries_bis['a'].insert(0, "1")
    entries_bis['b'].insert(0, "2")
    entries_bis['tol'].insert(0, "0.0001")
    entries_bis['dec'].insert(0, "6")

    entries_fal['funcion'].insert(0, ejemplo_func)
    entries_fal['a'].insert(0, "1")
    entries_fal['b'].insert(0, "2")
    entries_fal['tol'].insert(0, "0.0001")
    entries_fal['dec'].insert(0, "6")

    root.mainloop()


if __name__ == '__main__':
    main()
