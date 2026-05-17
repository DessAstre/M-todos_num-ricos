import tkinter as tk
from tkinter import ttk, messagebox
import sympy as sp
import math


class NRNFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ffbebe")
        self._build_ui()

    # --- Funciones de Precisión ---
    def aplicar_precision(self, valor, decimales, metodo):
        if metodo == "Redondeo":
            return round(valor, decimales)
        else:  # Truncamiento
            factor = 10 ** decimales
            return math.trunc(valor * factor) / factor

    def calcular(self):
        # Limpiar tabla previa
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        try:
            # Leer entradas
            txt_f = self.entry_f.get()
            x_n = float(self.entry_x0.get())
            tol_objetivo = float(self.entry_tol.get())
            prec = int(self.entry_prec.get())
            metodo_p = self.combo_metodo.get()

            # Preparar SymPy
            x = sp.symbols('x')
            f_expr = sp.sympify(txt_f)
            df_expr = sp.diff(f_expr, x)

            f = sp.lambdify(x, f_expr)
            df = sp.lambdify(x, df_expr)

            for i in range(1, 51):  # Máximo 50 iteraciones
                # Aplicar precisión al x_n inicial de la iteración
                x_n = self.aplicar_precision(x_n, prec, metodo_p)

                val_f = self.aplicar_precision(f(x_n), prec, metodo_p)
                val_df = self.aplicar_precision(df(x_n), prec, metodo_p)

                if val_df == 0:
                    messagebox.showerror("Error", "Derivada es cero.")
                    break

                delta_x = self.aplicar_precision(-(val_f / val_df), prec, metodo_p)
                x_next = self.aplicar_precision(x_n + delta_x, prec, metodo_p)
                val_f_next = self.aplicar_precision(f(x_next), prec, metodo_p)

                # Verificación de tolerancia
                error_actual = abs(x_next - x_n)
                cumple = "✓" if error_actual < tol_objetivo else "✗"

                # Insertar en tabla
                self.tabla.insert("", "end", values=(
                    i, x_n, val_f, val_df, delta_x, x_next, cumple, val_f_next
                ))

                if error_actual < tol_objetivo:
                    break

                x_n = x_next

        except Exception as e:
            messagebox.showerror("Error", f"Error en los datos: {e}")
            return

        # Mostrar ventana de resultados al terminar
        self.show_results_window()

    def clear_inputs(self):
        # Restaurar valores por defecto y limpiar tabla
        self.entry_f.delete(0, tk.END)
        self.entry_f.insert(0, "x**3 - x - 1")
        self.entry_x0.delete(0, tk.END)
        self.entry_x0.insert(0, "1")
        self.entry_tol.delete(0, tk.END)
        self.entry_tol.insert(0, "0.01")
        self.entry_prec.delete(0, tk.END)
        self.entry_prec.insert(0, "3")
        self.combo_metodo.current(0)
        for item in self.tabla.get_children():
            self.tabla.delete(item)

    def show_results_window(self):
        win = tk.Toplevel(self)
        win.title("Tabla de Resultados - Newton-Raphson 1D")
        win.geometry("800x400")

        cols = self.tabla["columns"]
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        tree.pack(fill="both", expand=True)

        for iid in self.tabla.get_children():
            vals = self.tabla.item(iid, "values")
            tree.insert("", "end", values=vals)

        btn_frame = tk.Frame(win)
        btn_frame.pack(fill="x", pady=6)

        def on_reenter():
            self.clear_inputs()
            win.destroy()

        btn_reenter = tk.Button(btn_frame, text="Volver a ingresar datos", command=on_reenter)
        btn_close = tk.Button(btn_frame, text="Cerrar programa", command=self.winfo_toplevel().destroy)
        btn_reenter.pack(side="left", padx=8)
        btn_close.pack(side="right", padx=8)

    def _build_ui(self):
        self.configure(bg="#ffbebe")
        title = tk.Label(
            self,
            text="Newton-Raphson",
            bg="#ffbebe",
            fg="#770909",
            font=("Arial", 16, "bold"),
        )
        title.pack(pady=(10, 0))

        frame_inputs = tk.Frame(self, pady=10, bg="#ffbebe")
        frame_inputs.pack()

        # Entradas
        tk.Label(frame_inputs, text="Función f(x):", bg="#ffbebe").pack()
        self.entry_f = tk.Entry(frame_inputs)
        self.entry_f.insert(0, "x**3 - x - 1")
        self.entry_f.pack()

        tk.Label(frame_inputs, text="Valor inicial (x0):", bg="#ffbebe").pack()
        self.entry_x0 = tk.Entry(frame_inputs, width=10)
        self.entry_x0.insert(0, "1")
        self.entry_x0.pack()

        tk.Label(frame_inputs, text="Tolerancia:", bg="#ffbebe").pack()
        self.entry_tol = tk.Entry(frame_inputs, width=10)
        self.entry_tol.insert(0, "0.01")
        self.entry_tol.pack()

        tk.Label(frame_inputs, text="Número de cifras:", bg="#ffbebe").pack()
        self.entry_prec = tk.Entry(frame_inputs, width=10)
        self.entry_prec.insert(0, "3")
        self.entry_prec.pack()

        tk.Label(frame_inputs, text="Tipo de aproximación:", bg="#ffbebe").pack()
        self.combo_metodo = ttk.Combobox(frame_inputs, values=["Redondeo", "Truncamiento"], width=12)
        self.combo_metodo.current(0)
        self.combo_metodo.pack()

        btn_calc = tk.Button(frame_inputs, text="Calcular", command=self.calcular, bg="#770909", fg="white")
        btn_calc.pack(pady=10)

        # --- Tabla de Resultados ---
        cols = ("i", "x0", "f(x0)", "f'(x0)", "Δx", "x1", "Tol", "f(x1)")
        self.tabla = ttk.Treeview(self, columns=cols, show="headings")

        for col in cols:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100, anchor="center")

        # Ajuste específico para columnas pequeñas
        self.tabla.column("i", width=40)
        self.tabla.column("Tol", width=50)

        self.tabla.pack(pady=10, fill="both", expand=True)


class NRMFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#fda9a9")
        self.x_sym = sp.symbols('x')
        self._build_ui()

    def aproximar(self, valor):
        dec = int(self.entrada_cifras.get())
        tipo = self.tipo_aprox.get()

        if tipo == "Redondeo":
            return round(valor, dec)
        elif tipo == "Truncamiento":
            factor = 10 ** dec
            return math.trunc(valor * factor) / factor
        return valor

    def calcular(self):
        try:
            self.tabla.delete(*self.tabla.get_children())

            # Lectura de datos
            funcion = sp.sympify(self.entrada_funcion.get())
            x0 = float(self.entrada_x0.get())
            tolerancia = float(self.entrada_tol.get())

            # Derivadas
            f = funcion
            f1 = sp.diff(f, self.x_sym)
            f2 = sp.diff(f1, self.x_sym)

            f_num = sp.lambdify(self.x_sym, f, "math")
            f1_num = sp.lambdify(self.x_sym, f1, "math")
            f2_num = sp.lambdify(self.x_sym, f2, "math")

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

                self.tabla.insert("", "end", values=(
                    iteracion,
                    self.aproximar(x0),
                    self.aproximar(fx0),
                    self.aproximar(f1x0),
                    self.aproximar(f2x0),
                    self.aproximar(delta),
                    self.aproximar(x1),
                    tol,
                    self.aproximar(fx1)
                ))

                if abs(delta) < tolerancia:
                    break

                x0 = x1
                iteracion += 1

        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Mostrar ventana de resultados al terminar
        self.show_results_window()

    def clear_inputs(self):
        # Restaurar valores por defecto y limpiar tabla
        self.entrada_funcion.delete(0, tk.END)
        self.entrada_funcion.insert(0, "x**3 - x - 1")
        self.entrada_x0.delete(0, tk.END)
        self.entrada_x0.insert(0, "1")
        self.entrada_tol.delete(0, tk.END)
        self.entrada_tol.insert(0, "0.01")
        self.entrada_cifras.delete(0, tk.END)
        self.entrada_cifras.insert(0, "3")
        self.tipo_aprox.current(0)
        for item in self.tabla.get_children():
            self.tabla.delete(item)

    def show_results_window(self):
        win = tk.Toplevel(self)
        win.title("Tabla de Resultados - Newton-Raphson Mejorado")
        win.geometry("900x420")

        cols = self.tabla["columns"]
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        tree.pack(fill="both", expand=True)

        for iid in self.tabla.get_children():
            vals = self.tabla.item(iid, "values")
            tree.insert("", "end", values=vals)

        btn_frame = tk.Frame(win)
        btn_frame.pack(fill="x", pady=6)

        def on_reenter():
            self.clear_inputs()
            win.destroy()

        btn_reenter = tk.Button(btn_frame, text="Volver a ingresar datos", command=on_reenter)
        btn_close = tk.Button(btn_frame, text="Cerrar programa", command=self.winfo_toplevel().destroy)
        btn_reenter.pack(side="left", padx=8)
        btn_close.pack(side="right", padx=8)

    def _build_ui(self):
        title = tk.Label(
            self,
            text="Newton-Raphson Mejorado",
            bg="#fda9a9",
            fg="#490202",
            font=("Arial", 16, "bold"),
        )
        title.pack(pady=(10, 4))

        frame = tk.Frame(self, bg="#fda9a9")
        frame.pack(pady=(0, 10))

        tk.Label(frame, text="Función f(x):", bg="#fda9a9").pack()
        self.entrada_funcion = tk.Entry(frame, width=25)
        self.entrada_funcion.insert(0, "x**3 - x - 1")
        self.entrada_funcion.pack()

        tk.Label(frame, text="Valor inicial x0:", bg="#fda9a9").pack()
        self.entrada_x0 = tk.Entry(frame)
        self.entrada_x0.insert(0, "1")
        self.entrada_x0.pack()

        tk.Label(frame, text="Tolerancia:", bg="#fda9a9").pack()
        self.entrada_tol = tk.Entry(frame)
        self.entrada_tol.insert(0, "0.01")
        self.entrada_tol.pack()

        tk.Label(frame, text="Cifras decimales:", bg="#fda9a9").pack()
        self.entrada_cifras = tk.Entry(frame)
        self.entrada_cifras.insert(0, "3")
        self.entrada_cifras.pack()

        tk.Label(frame, text="Tipo de aproximación:", bg="#fda9a9").pack()
        self.tipo_aprox = ttk.Combobox(frame, values=["Redondeo", "Truncamiento"])
        self.tipo_aprox.pack()
        self.tipo_aprox.current(0)

        # Botón Calcular
        btn = tk.Button(self, text="Calcular", bg="#490202", fg="white", command=self.calcular)
        btn.pack(pady=10)

        # Tabla
        columnas = ("It", "x0", "f(x0)", "f'(x0)", "f''(x0)", "Δx", "x1", "Tol", "f(x1)")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings")

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100, anchor="center")

        self.tabla.pack(fill="both", expand=True)


def main():
    root = tk.Tk()
    root.title("Métodos_Cerrados")
    root.geometry("1920x1080")

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True)

    frame1 = ttk.Frame(nb)
    frame2 = ttk.Frame(nb)

    nb.add(frame1, text="Newton-Raphson (1D)")
    nb.add(frame2, text="Newton Mejorado")

    nrn = NRNFrame(frame1)
    nrn.pack(fill="both", expand=True)

    nrm = NRMFrame(frame2)
    nrm.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    main()
