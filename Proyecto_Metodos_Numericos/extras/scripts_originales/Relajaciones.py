import tkinter as tk
from tkinter import ttk, messagebox
from itertools import permutations
import math


def fmt_decimal(value, decimals=10):
    text = f"{value:.{decimals}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text if text else "0"


def apply_precision(value, digits, mode):
    factor = 10 ** digits
    if mode == "truncamiento":
        if value >= 0:
            return math.floor(value * factor) / factor
        return math.ceil(value * factor) / factor
    return round(value, digits)


def build_base_table_from_class_method(A, b, digits, mode):
    """
    Metodo segun apuntes:
    1) Llevar Ax=b a Ax-b=0.
    2) Buscar diagonal mayor en valor absoluto (sin signo), asignando una fila por variable.
    3) Dividir cada fila por ese valor absoluto y forzar coeficiente diagonal -1.
    4) Construir cuadro base: -x_i + sum(c_ij x_j) + R_i = 0.
    """
    n = len(A)
    C = [[0.0] * n for _ in range(n)]
    R0 = [0.0] * n

    best_perm = None
    best_score = None

    # perm[var] = fila original elegida para la variable var.
    for perm in permutations(range(n)):
        score = 0.0
        valid = True
        for var in range(n):
            coeff = A[perm[var]][var]
            if abs(coeff) < 1e-15:
                valid = False
                break
            score += abs(coeff)
        if not valid:
            continue
        if best_score is None or score > best_score:
            best_score = score
            best_perm = perm

    if best_perm is None:
        raise ValueError("No se pudo formar una diagonal mayor valida. Reordena o cambia el sistema.")

    order_info = []
    for var in range(n):
        row_idx = best_perm[var]
        diag_coeff = A[row_idx][var]
        scale = abs(diag_coeff)

        row_coeffs = [apply_precision(A[row_idx][j] / scale, digits, mode) for j in range(n)]
        const_term = apply_precision((-b[row_idx]) / scale, digits, mode)  # Ax-b=0

        # Se fuerza diagonal -1 para coincidir con el metodo del cuaderno.
        if row_coeffs[var] > 0:
            row_coeffs = [apply_precision(-v, digits, mode) for v in row_coeffs]
            const_term = apply_precision(-const_term, digits, mode)

        for j in range(n):
            C[var][j] = apply_precision(row_coeffs[j], digits, mode)

        R0[var] = apply_precision(const_term, digits, mode)
        order_info.append((var, row_idx, diag_coeff, scale))

    return C, R0, order_info


def relaxation_with_t_register(C, R0, tol, max_iter, digits, mode, pivot_mode="auto", manual_pivot=None):
    n = len(C)
    x = [0.0] * n  # suma de pivotes por variable
    R = [apply_precision(v, digits, mode) for v in R0]
    history = []

    for k in range(1, max_iter + 1):
        err = max(abs(v) for v in R)

        if err <= tol:
            break

        if pivot_mode == "auto":
            i = max(range(n), key=lambda idx: abs(R[idx]))
        else:
            if manual_pivot is None or manual_pivot < 0 or manual_pivot >= n:
                raise ValueError("La variable de pivote manual esta fuera de rango.")
            i = manual_pivot

        pivot = apply_precision(R[i], digits, mode)

        # Registro T: efecto del pivote sobre cada residuo.
        t_col = [apply_precision(C[j][i] * pivot, digits, mode) for j in range(n)]

        R_before = R[:]
        x_before = x[:]

        x[i] = apply_precision(x[i] + pivot, digits, mode)
        for j in range(n):
            R[j] = apply_precision(R[j] + t_col[j], digits, mode)

        # En la fila pivote debe quedar 0 idealmente, lo fijamos por estabilidad numerica.
        R[i] = 0.0
        R_after = R[:]

        history.append({
            "iter": k,
            "pivot_var": i,
            "pivot": pivot,
            "x_before": x_before,
            "x_after": x[:],
            "R_before": R_before,
            "T_col": t_col,
            "R_after": R_after,
            "err_before": err,
        })

    converged = max(abs(v) for v in R) <= tol
    return x, R, history, converged


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Método de Relajaciones (Residuos y Pivotes)")
        self.geometry("1350x850")

        self.n_var = tk.IntVar(value=3)
        self.tol_var = tk.StringVar(value="0.000001")
        self.max_iter_var = tk.StringVar(value="200")
        self.cifras_var = tk.StringVar(value="6")
        self.aprox_mode_var = tk.StringVar(value="redondeo")

        self.a_entries = []
        self.b_entries = []
        self.base_tree = None
        self.tree = None
        self.t_window = None
        self.t_tree = None

        self._build_ui()
        self.build_matrix_inputs()

    def _build_ui(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Numero de variables:").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(top, from_=2, to=11, textvariable=self.n_var, width=5).grid(row=0, column=1, padx=4)
        ttk.Button(top, text="Crear matriz", command=self.build_matrix_inputs).grid(row=0, column=2, padx=6)

        ttk.Label(top, text="Tolerancia:").grid(row=0, column=3, sticky="w")
        ttk.Entry(top, textvariable=self.tol_var, width=12).grid(row=0, column=4, padx=4)

        ttk.Label(top, text="Max iter:").grid(row=0, column=5, sticky="w")
        ttk.Entry(top, textvariable=self.max_iter_var, width=10).grid(row=0, column=6, padx=4)

        ttk.Label(top, text="Cifras:").grid(row=0, column=7, sticky="w")
        ttk.Spinbox(top, from_=1, to=12, textvariable=self.cifras_var, width=5).grid(row=0, column=8, padx=4)

        ttk.Label(top, text="Metodo:").grid(row=0, column=9, sticky="w")
        ttk.Combobox(
            top,
            textvariable=self.aprox_mode_var,
            values=("redondeo", "truncamiento"),
            width=12,
            state="readonly",
        ).grid(row=0, column=10, padx=4)

        ttk.Button(top, text="Ejemplo 3x3", command=self.load_class_example).grid(row=0, column=11, padx=6)
        ttk.Button(top, text="Resolver", command=self.solve).grid(row=0, column=12, padx=6)

        self.matrix_frame = ttk.LabelFrame(self, text="Sistema Ax = b", padding=10)
        self.matrix_frame.pack(fill="x", padx=10, pady=8)

        out = ttk.LabelFrame(self, text="Resultados", padding=10)
        out.pack(fill="both", expand=True, padx=10, pady=8)

        self.result_text = tk.Text(out, height=5, font=("Consolas", 10), bg="#f8f9fa")
        self.result_text.pack(fill="x", pady=(0, 8))

        base_label = ttk.Label(out, text="Cuadro Base (-x_i + sum(c_ij x_j) + R_i = 0):", font=("Arial", 10, "bold"))
        base_label.pack(fill="x", pady=(4, 4))

        self.base_tree = ttk.Treeview(out, show="headings", height=4)
        self.base_tree.pack(fill="x", pady=(0, 8))

        iter_label = ttk.Label(out, text="Registros de iteración (Residuos y Pivotes):", font=("Arial", 10, "bold"))
        iter_label.pack(fill="x", pady=(0, 4))

        tree_frame = ttk.Frame(out)
        tree_frame.pack(fill="both", expand=True, pady=(0, 0))

        self.tree = ttk.Treeview(tree_frame, show="headings", height=10)
        self.tree.pack(fill="both", expand=True, side="left")

        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

    def build_matrix_inputs(self):
        for w in self.matrix_frame.winfo_children():
            w.destroy()

        n = self.n_var.get()
        self.a_entries = []
        self.b_entries = []

        ttk.Label(self.matrix_frame, text="Coeficientes A").grid(row=0, column=0, columnspan=n, pady=(0, 6))
        ttk.Label(self.matrix_frame, text="b").grid(row=0, column=n + 1, pady=(0, 6))

        for i in range(n):
            row_e = []
            for j in range(n):
                e = ttk.Entry(self.matrix_frame, width=8, justify="center")
                e.grid(row=i + 1, column=j, padx=2, pady=2)
                row_e.append(e)
            self.a_entries.append(row_e)

            eb = ttk.Entry(self.matrix_frame, width=8, justify="center")
            eb.grid(row=i + 1, column=n + 1, padx=8, pady=2)
            self.b_entries.append(eb)

    def load_class_example(self):
        self.n_var.set(3)
        self.build_matrix_inputs()

        A = [
            [2, -5, 4],
            [-1, 3, -6],
            [-4, -1, -1],
        ]
        b = [3, -5, -10]

        for i in range(3):
            for j in range(3):
                self.a_entries[i][j].delete(0, tk.END)
                self.a_entries[i][j].insert(0, str(A[i][j]))
            self.b_entries[i].delete(0, tk.END)
            self.b_entries[i].insert(0, str(b[i]))

        self.tol_var.set("0.000001")
        self.max_iter_var.set("200")
        self.cifras_var.set("6")
        self.aprox_mode_var.set("redondeo")

    def read_system(self):
        n = self.n_var.get()
        A = [[0.0] * n for _ in range(n)]
        b = [0.0] * n

        for i in range(n):
            for j in range(n):
                A[i][j] = float(self.a_entries[i][j].get())
            b[i] = float(self.b_entries[i].get())

        return A, b

    def run_relaxation(self, C, R0, tol, max_iter):
        n = len(C)
        x = [0.0] * n
        R = R0[:]
        hist = []

        for k in range(1, max_iter + 1):
            err = max(abs(v) for v in R)

            if self.pivot_mode.get() == "auto":
                i = max(range(n), key=lambda idx: abs(R[idx]))
            else:
                i_manual = int(self.manual_pivot_var.get()) - 1
                if i_manual < 0 or i_manual >= n:
                    raise ValueError("La variable de pivote manual esta fuera de rango.")
                i = i_manual

            p = R[i]

            hist.append({
                "iter": k,
                "pivot_var": i,
                "pivot": p,
                "x": x[:],
                "R": R[:],
                "err": err,
            })

            if err <= tol:
                return x, R, hist, True

            x[i] += p

            for j in range(n):
                R[j] += C[j][i] * p

            R[i] = 0.0

        err = max(abs(v) for v in R)
        return x, R, hist, err <= tol

    def solve(self):
        try:
            A, b = self.read_system()
            tol = float(self.tol_var.get())
            max_iter = int(self.max_iter_var.get())
            digits = int(self.cifras_var.get())
            mode = self.aprox_mode_var.get().strip().lower()

            if tol <= 0:
                raise ValueError("La tolerancia debe ser positiva.")
            if max_iter <= 0:
                raise ValueError("Max iter debe ser positivo.")
            if digits <= 0:
                raise ValueError("El numero de cifras debe ser mayor a 0.")
            if mode not in ("redondeo", "truncamiento"):
                raise ValueError("El metodo numerico debe ser redondeo o truncamiento.")

            A = [[apply_precision(v, digits, mode) for v in row] for row in A]
            b = [apply_precision(v, digits, mode) for v in b]

            C, R0, order_info = build_base_table_from_class_method(A, b, digits, mode)

            x, Rf, hist, converged = relaxation_with_t_register(
                C,
                R0,
                tol,
                max_iter,
                digits,
                mode,
                pivot_mode="auto",
                manual_pivot=None,
            )

        except ValueError as e:
            messagebox.showerror("Datos invalidos", str(e))
            return
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.result_text.delete("1.0", tk.END)
        lines = []
        lines.append("Aproximacion de variables (suma de pivotes):")
        for i, xi in enumerate(x, start=1):
            lines.append(f"x{i} = {fmt_decimal(xi, digits)}")

        lines.append("")
        lines.append(f"Convergencia: {'SI' if converged else 'NO'}")
        lines.append(f"Iteraciones usadas: {len(hist)}")
        self.result_text.insert(tk.END, "\n".join(lines))

        self.fill_base_table(C, R0)
        self.fill_table(hist)
        self.fill_t_table(hist)

    def fill_base_table(self, C, R0):
        n = len(C)
        cols = ["Ecuación"]
        for j in range(n):
            cols.append(f"x{j+1}")
        cols.append("= R")

        self.base_tree.delete(*self.base_tree.get_children())
        self.base_tree["columns"] = cols

        for c in cols:
            self.base_tree.heading(c, text=c)
            if c == "Ecuación":
                ancho = 50
            elif c == "= R":
                ancho = 65
            else:
                ancho = 64
            self.base_tree.column(c, width=ancho, anchor="center", stretch=False)

        # Aplicar estilos
        style = ttk.Style()
        style.configure("Base.Treeview", rowheight=22, font=("Arial", 9))
        style.configure("Base.Treeview.Heading", font=("Arial", 9, "bold"))
        self.base_tree.configure(style="Base.Treeview")

        romanos = [
            "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
            "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"
        ]

        for i in range(n):
            etiqueta = romanos[i] if i < len(romanos) else f"I{i+1}"
            row = [etiqueta]
            for j in range(n):
                val = C[i][j]
                # Solo mostrar el valor sin "xj" al lado
                row.append(fmt_decimal(val, 8))
            # Mostrar R con formato más legible
            r_val = fmt_decimal(R0[i], 8)
            row.append(r_val)
            self.base_tree.insert("", tk.END, values=row)

    def fill_table(self, hist):
        n = self.n_var.get()
        cols = ["Iter", "Var Pivote", "Pivote"]
        for i in range(n):
            cols.append(f"x{i+1}")
            cols.append(f"R{i+1}")
        cols += ["Error", "Tipo"]

        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = cols

        # Aplicar estilos
        style = ttk.Style()
        style.configure("Iter.Treeview", rowheight=23, font=("Arial", 9))
        style.configure("Iter.Treeview.Heading", font=("Arial", 9, "bold"))
        self.tree.configure(style="Iter.Treeview")

        for c in cols:
            self.tree.heading(c, text=c)
            if c in ["Iter", "Var Pivote"]:
                ancho = 70
            elif c in ["Error", "Tipo"]:
                ancho = 85
            else:
                ancho = 95
            self.tree.column(c, width=ancho, anchor="center", stretch=False)

        for s in hist:
            row = [s["iter"], f"x{s['pivot_var'] + 1}", fmt_decimal(s["pivot"], 10)]
            for i in range(n):
                row.append(fmt_decimal(s["x_after"][i], int(self.cifras_var.get())))
                row.append(fmt_decimal(s["R_after"][i], int(self.cifras_var.get())))
            row.append(fmt_decimal(s["err_before"], int(self.cifras_var.get())))
            row.append(f"col x{s['pivot_var'] + 1}")
            self.tree.insert("", tk.END, values=row)

    def fill_t_table(self, hist):
        if self.t_window is not None:
            try:
                self.t_window.destroy()
            except tk.TclError:
                pass

        self.t_window = tk.Toplevel(self)
        self.t_window.title("Registros T")
        self.t_window.geometry("1100x420")

        frame = ttk.Frame(self.t_window, padding=10)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(frame, text="Registros T completos", font=("Arial", 10, "bold"))
        title.pack(fill="x", pady=(0, 6))

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True)

        self.t_tree = ttk.Treeview(tree_frame, show="headings")
        self.t_tree.grid(row=0, column=0, sticky="nsew")

        y_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.t_tree.yview)
        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.t_tree.xview)
        self.t_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        n = self.n_var.get()
        cols = ["Iter", "Var Pivote", "Pivote"]
        for i in range(n):
            cols.append(f"x{i+1}")
            cols.append(f"R{i+1}")
        cols += ["Error", "Tipo"]

        self.t_tree["columns"] = cols

        style = ttk.Style()
        style.configure("TReg.Treeview", rowheight=23, font=("Arial", 9))
        style.configure("TReg.Treeview.Heading", font=("Arial", 9, "bold"))
        self.t_tree.configure(style="TReg.Treeview")

        for c in cols:
            self.t_tree.heading(c, text=c)
            if c in ["Iter", "Var Pivote"]:
                ancho = 70
            elif c in ["Error", "Tipo"]:
                ancho = 85
            else:
                ancho = 95
            self.t_tree.column(c, width=ancho, anchor="center", stretch=False)

        for s in hist:
            row = [s["iter"], f"x{s['pivot_var'] + 1}", fmt_decimal(s["pivot"], int(self.cifras_var.get()))]
            for i in range(n):
                row.append(fmt_decimal(s["x_after"][i], int(self.cifras_var.get())))
                row.append(fmt_decimal(s["R_after"][i], int(self.cifras_var.get())))
            row.append(fmt_decimal(s["err_before"], int(self.cifras_var.get())))
            row.append(f"col x{s['pivot_var'] + 1}")
            self.t_tree.insert("", tk.END, values=row)


if __name__ == "__main__":
    app = App()
    app.mainloop()
