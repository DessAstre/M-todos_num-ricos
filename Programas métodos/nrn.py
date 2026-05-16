import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
import math

# --- Funciones de Precisión ---
def aplicar_precision(valor, decimales, metodo):
    if metodo == "Redondeo":
        return round(valor, decimales)
    else: # Truncamiento
        factor = 10 ** decimales
        return math.trunc(valor * factor) / factor

def calcular():
    # Limpiar tabla previa
    for item in tabla.get_children():
        tabla.delete(item)
    
    try:
        # Leer entradas
        txt_f = entry_f.get()
        x_n = float(entry_x0.get())
        tol_objetivo = float(entry_tol.get())
        prec = int(entry_prec.get())
        metodo_p = combo_metodo.get()
        
        # Preparar SymPy
        x = sp.symbols('x')
        f_expr = sp.sympify(txt_f)
        df_expr = sp.diff(f_expr, x)
        
        f = sp.lambdify(x, f_expr)
        df = sp.lambdify(x, df_expr)
        
        for i in range(1, 51): # Máximo 50 iteraciones
            # Aplicar precisión al x_n inicial de la iteración
            x_n = aplicar_precision(x_n, prec, metodo_p)
            
            val_f = aplicar_precision(f(x_n), prec, metodo_p)
            val_df = aplicar_precision(df(x_n), prec, metodo_p)
            
            if val_df == 0:
                messagebox.showerror("Error", "Derivada es cero.")
                break
                
            delta_x = aplicar_precision(-(val_f / val_df), prec, metodo_p)
            x_next = aplicar_precision(x_n + delta_x, prec, metodo_p)
            val_f_next = aplicar_precision(f(x_next), prec, metodo_p)
            
            # Verificación de tolerancia
            error_actual = abs(x_next - x_n)
            cumple = "✓" if error_actual < tol_objetivo else "✗"
            
            # Insertar en tabla
            tabla.insert("", "end", values=(
                i, x_n, val_f, val_df, delta_x, x_next, cumple, val_f_next
            ))
            
            if error_actual < tol_objetivo:
                break
            
            x_n = x_next

    except Exception as e:
        messagebox.showerror("Error", f"Error en los datos: {e}")

# --- Interfaz Gráfica ---
root = tk.Tk()
root.title("Newton-Raphson 1D")
root.geometry("900x550")
root.configure(bg="#bee5ff")

frame_inputs = tk.Frame(root, pady=10, bg="#bee5ff")
frame_inputs.pack()

# Entradas
tk.Label(frame_inputs, text="Función f(x):", bg="#bee5ff").pack()
entry_f = tk.Entry(frame_inputs)
entry_f.insert(0, "x**3 - x - 1")
entry_f.pack()

tk.Label(frame_inputs, text="Valor inicial (x0):", bg="#bee5ff").pack()
entry_x0 = tk.Entry(frame_inputs, width=10)
entry_x0.insert(0, "1")
entry_x0.pack()

tk.Label(frame_inputs, text="Tolerancia:", bg="#bee5ff").pack()
entry_tol = tk.Entry(frame_inputs, width=10)
entry_tol.insert(0, "0.01")
entry_tol.pack()

tk.Label(frame_inputs, text="Número de cifras:", bg="#bee5ff").pack()
entry_prec = tk.Entry(frame_inputs, width=10)
entry_prec.insert(0, "3")
entry_prec.pack()

tk.Label(frame_inputs, text="Tipo de aproximación:", bg="#bee5ff").pack()
combo_metodo = ttk.Combobox(frame_inputs, values=["Redondeo", "Truncamiento"], width=12)
combo_metodo.current(0)
combo_metodo.pack()

btn_calc = tk.Button(frame_inputs, text="Calcular", command=calcular, bg="#094577", fg="white")
btn_calc.pack(pady=10)

# --- Tabla de Resultados ---
cols = ("i", "x0", "f(x0)", "f'(x0)", "Δx", "x1", "Tol", "f(x1)")
tabla = ttk.Treeview(root, columns=cols, show="headings")

for col in cols:
    tabla.heading(col, text=col)
    tabla.column(col, width=100, anchor="center")

# Ajuste específico para columnas pequeñas
tabla.column("i", width=40)
tabla.column("Tol", width=50)

tabla.pack(pady=10, fill="both", expand=True)

root.mainloop()