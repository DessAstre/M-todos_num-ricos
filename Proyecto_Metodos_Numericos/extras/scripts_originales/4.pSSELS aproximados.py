import math
import itertools
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from itertools import permutations


# ---------------- Relajaciones (adaptado a Frame) ----------------
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
    n = len(A)
    C = [[0.0] * n for _ in range(n)]
    R0 = [0.0] * n

    best_perm = None
    best_score = None

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
        const_term = apply_precision((-b[row_idx]) / scale, digits, mode)

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
    x = [0.0] * n
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

        t_col = [apply_precision(C[j][i] * pivot, digits, mode) for j in range(n)]

        R_before = R[:]
        x_before = x[:]

        x[i] = apply_precision(x[i] + pivot, digits, mode)
        for j in range(n):
            R[j] = apply_precision(R[j] + t_col[j], digits, mode)

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


class RelajacionesApp(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

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
                row.append(fmt_decimal(val, 8))
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


# ---------------- Gauss-Seidel (manteniendo lógica) ----------------
def aplicar_precision(valor, cifras, metodo):
    factor = 10 ** cifras
    if metodo == "truncamiento":
        if valor >= 0:
            return math.floor(valor * factor) / factor
        return math.ceil(valor * factor) / factor
    return round(valor, cifras)


def es_diagonal_dominante(A):
    n = len(A)
    for i in range(n):
        suma = sum(abs(A[i][j]) for j in range(n) if j != i)
        if abs(A[i][i]) < suma:
            return False
    return True


def norma_inf(v):
    return max(abs(x) for x in v)


def residuo_inf(A, b, x):
    residuos = []
    for i in range(len(A)):
        ax_i = sum(A[i][j] * x[j] for j in range(len(A[i])))
        residuos.append(ax_i - b[i])
    return norma_inf(residuos)


def gauss_seidel(A, b, x0=None, tol=1e-8, max_iter=100, cifras=8, metodo="redondeo"):
    n = len(A)

    if any(len(fila) != n for fila in A):
        raise ValueError("La matriz A debe ser cuadrada.")
    if len(b) != n:
        raise ValueError("El vector b debe tener el mismo tamano que A.")
    for i in range(n):
        if abs(A[i][i]) < 1e-15:
            raise ZeroDivisionError("Hay un cero en la diagonal de A.")

    A_num = [[aplicar_precision(float(A[i][j]), cifras, metodo) for j in range(n)] for i in range(n)]
    b_num = [aplicar_precision(float(b[i]), cifras, metodo) for i in range(n)]
    x = [0.0] * n if x0 is None else [aplicar_precision(float(v), cifras, metodo) for v in x0]
    historial = []

    for k in range(1, max_iter + 1):
        x_old = x.copy()

        for i in range(n):
            suma_izq = 0.0
            for j in range(i):
                prod = aplicar_precision(A_num[i][j] * x[j], cifras, metodo)
                suma_izq = aplicar_precision(suma_izq + prod, cifras, metodo)

            suma_der = 0.0
            for j in range(i + 1, n):
                prod = aplicar_precision(A_num[i][j] * x_old[j], cifras, metodo)
                suma_der = aplicar_precision(suma_der + prod, cifras, metodo)

            numerador = aplicar_precision(b_num[i] - suma_izq - suma_der, cifras, metodo)
            x[i] = aplicar_precision(numerador / A_num[i][i], cifras, metodo)

        error = norma_inf([x[i] - x_old[i] for i in range(n)])
        deltas = [abs(x[i] - x_old[i]) for i in range(n)]
        historial.append((k, x.copy(), error, deltas))

        if error < tol:
            return x, k, error, historial

    return x, max_iter, error, historial


def reordenar_sistema_por_columnas(A, b):
    n = len(A)
    pasos = []

    max_col_por_fila = []
    max_abs_por_fila = []
    for i in range(n):
        col_max = max(range(n), key=lambda j: abs(A[i][j]))
        max_col_por_fila.append(col_max)
        max_abs_por_fila.append(abs(A[i][col_max]))

    mejor_perm = None
    mejor_score = None

    if n <= 8:
        for perm in itertools.permutations(range(n)):
            aciertos = 0
            suma_diag = 0.0
            for pos in range(n):
                fila = perm[pos]
                diag_abs = abs(A[fila][pos])
                suma_diag += diag_abs
                if math.isclose(diag_abs, max_abs_por_fila[fila], rel_tol=1e-12, abs_tol=1e-12):
                    aciertos += 1

            score = (aciertos, suma_diag)
            if mejor_score is None or score > mejor_score:
                mejor_score = score
                mejor_perm = perm
    else:
        usadas = set()
        perm = []
        aciertos = 0
        suma_diag = 0.0

        for pos in range(n):
            candidatos = [fila for fila in range(n) if fila not in usadas]
            if not candidatos:
                break

            fila = max(candidatos, key=lambda f: abs(A[f][pos]))
            usadas.add(fila)
            perm.append(fila)

            diag_abs = abs(A[fila][pos])
            suma_diag += diag_abs
            if math.isclose(diag_abs, max_abs_por_fila[fila], rel_tol=1e-12, abs_tol=1e-12):
                aciertos += 1

        if len(perm) == n:
            mejor_perm = tuple(perm)
            mejor_score = (aciertos, suma_diag)

    if mejor_perm is None:
        raise ValueError("No se pudo reordenar el sistema para construir una diagonal util.")

    orden = list(mejor_perm)
    A2 = [A[i][:] for i in orden]
    b2 = [b[i] for i in orden]

    for pos, fila in enumerate(orden):
        col_max = max_col_por_fila[fila]
        diag_abs = abs(A[fila][pos])
        max_abs = max_abs_por_fila[fila]
        marca = "✔" if math.isclose(diag_abs, max_abs, rel_tol=1e-12, abs_tol=1e-12) else "✘"
        pasos.append(
            f"Ecuacion {fila + 1} colocada en fila {pos + 1}: |diag|={diag_abs:.6g}, max(|coef| de su ecuacion)={max_abs:.6g} (columna {col_max + 1}) {marca}"
        )

    exacto = mejor_score[0] == n
    return A2, b2, orden, pasos, exacto


class GaussSeidelApp:
    def __init__(self, parent):
        # parent can be a Toplevel/Tk or a Frame; guard title/geometry calls
        self.root = parent
        if hasattr(self.root, "title"):
            try:
                self.root.title("Metodo de Gauss-Seidel")
            except Exception:
                pass
        if hasattr(self.root, "geometry"):
            try:
                self.root.geometry("860x650")
            except Exception:
                pass

        self.matrix_entries = []
        self.b_entries = []
        self.x0_entries = []
        self.table = None
        self.table_cols = ()
        self.proc_text = None
        self.detail_window = None
        self.detail_text = None
        self.detail_table = None

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self.root, padx=12, pady=12)
        top.pack(fill="x")

        tk.Label(top, text="Numero de variables (n):").grid(row=0, column=0, sticky="w")
        self.n_var = tk.StringVar(value="3")
        tk.Entry(top, textvariable=self.n_var, width=8).grid(row=0, column=1, padx=8)
        tk.Button(top, text="Generar campos", command=self.generar_campos).grid(row=0, column=2, padx=6)

        tk.Label(top, text="Tolerancia:").grid(row=0, column=3, padx=(20, 0), sticky="w")
        self.tol_var = tk.StringVar(value="1e-8")
        tk.Entry(top, textvariable=self.tol_var, width=12).grid(row=0, column=4, padx=6)

        tk.Label(top, text="Max iter:").grid(row=0, column=5, sticky="w")
        self.max_iter_var = tk.StringVar(value="100")
        tk.Entry(top, textvariable=self.max_iter_var, width=10).grid(row=0, column=6, padx=6)

        tk.Label(top, text="Cifras:").grid(row=0, column=7, padx=(16, 0), sticky="w")
        self.cifras_var = tk.StringVar(value="8")
        tk.Spinbox(top, from_=1, to=12, textvariable=self.cifras_var, width=6).grid(row=0, column=8, padx=6)

        tk.Label(top, text="Metodo:").grid(row=0, column=9, sticky="w")
        self.metodo_var = tk.StringVar(value="redondeo")
        ttk.Combobox(
            top,
            textvariable=self.metodo_var,
            values=("redondeo", "truncamiento"),
            state="readonly",
            width=13,
        ).grid(row=0, column=10, padx=6)

        self.auto_reordenar_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            top,
            text="Reordenar ecuaciones (como en clase)",
            variable=self.auto_reordenar_var,
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(8, 0))

        self.inputs_frame = tk.LabelFrame(self.root, text="Datos de entrada", padx=10, pady=10)
        self.inputs_frame.pack(fill="x", padx=12, pady=(0, 8))

        actions = tk.Frame(self.root, padx=12)
        actions.pack(fill="x")
        tk.Button(actions, text="Resolver", command=self.resolver, bg="#198754", fg="white").pack(side="left")
        tk.Button(actions, text="Limpiar", command=self.limpiar_salida).pack(side="left", padx=8)
        tk.Button(actions, text="Ejemplo 3x3", command=self.cargar_ejemplo).pack(side="left")

        self.info_var = tk.StringVar(value="Resultado: pendiente")
        tk.Label(self.root, textvariable=self.info_var, anchor="w", padx=12).pack(fill="x")

        self.proc_text = scrolledtext.ScrolledText(self.root, wrap="word", height=8)
        self.proc_text.pack(fill="x", padx=12, pady=(8, 0))

        table_wrap = tk.Frame(self.root, padx=12, pady=12)
        table_wrap.pack(fill="both", expand=True)

        self.table = ttk.Treeview(table_wrap, show="headings")
        v_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.table.yview)
        h_scroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.table.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)

        self.generar_campos()

    # El resto de métodos se mantienen sin cambios de lógica
    def _nombres_variables(self, n):
        base = ["x", "y", "z", "w", "v", "u", "t", "s", "r", "q"]
        if n <= len(base):
            return base[:n]
        extras = [f"x{i+1}" for i in range(n - len(base))]
        return base + extras

    def _construir_tabla(self, historial, x0, tol, cifras):
        self._poblar_tabla_en(self.table, historial, x0, tol, cifras)

    def _poblar_tabla_en(self, target_table, historial, x0, tol, cifras):
        n = len(x0)
        iter_count = len(historial)

        columnas = ["Var", "V0"]
        for k in range(1, iter_count + 1):
            columnas.append(f"{k}a")
            columnas.append("T")

        target_table.delete(*target_table.get_children())
        self.table_cols = tuple(columnas)
        target_table["columns"] = self.table_cols

        for idx, col in enumerate(self.table_cols):
            ancho = 90 if idx < 2 else 110
            if col.startswith("Tol"):
                ancho = 60
            target_table.heading(col, text=col)
            target_table.column(col, width=ancho, anchor="center", stretch=False)

        nombres = self._nombres_variables(n)
        for i in range(n):
            fila = [nombres[i], f"{x0[i]:.{cifras}f}"]
            for _, xk, _, deltas in historial:
                fila.append(f"{xk[i]:.{cifras}f}")
                fila.append("✔" if deltas[i] < tol else "✘")
            target_table.insert("", tk.END, values=fila)

        errores = ["error_inf", "-"]
        for _, _, err_k, _ in historial:
            errores.append(f"{err_k:.3e}")
            errores.append("✔" if err_k < tol else "✘")
        target_table.insert("", tk.END, values=errores)

    def _texto_despeje(self, A, b):
        n = len(A)
        nombres = self._nombres_variables(n)
        lineas = ["Despeje de ecuaciones:"]

        for i in range(n):
            aii = A[i][i]
            if abs(aii) < 1e-15:
                lineas.append(f"- {nombres[i]}: no se puede despejar (a_ii=0)")
                continue

            terminos = []
            for j in range(n):
                if j == i:
                    continue
                terminos.append(f"({A[i][j]:.6g}*{nombres[j]})")

            if terminos:
                rhs = f"{b[i]:.6g} - " + " - ".join(terminos)
            else:
                rhs = f"{b[i]:.6g}"

            lineas.append(f"- {nombres[i]} = ({rhs}) / ({aii:.6g})")

        return "\n".join(lineas)

    def _mostrar_ventana_detalle(self, A, b, historial, x0, tol, cifras):
        if self.detail_window is not None:
            try:
                self.detail_window.destroy()
            except tk.TclError:
                pass

        self.detail_window = tk.Toplevel(self.root)
        self.detail_window.title("Despeje e Iteraciones")
        self.detail_window.geometry("1100x620")

        wrap = tk.Frame(self.detail_window, padx=10, pady=10)
        wrap.pack(fill="both", expand=True)

        self.detail_text = scrolledtext.ScrolledText(wrap, wrap="word", height=8)
        self.detail_text.pack(fill="x", pady=(0, 8))
        self.detail_text.insert(tk.END, self._texto_despeje(A, b))
        self.detail_text.configure(state="disabled")

        table_wrap = tk.Frame(wrap)
        table_wrap.pack(fill="both", expand=True)

        self.detail_table = ttk.Treeview(table_wrap, show="headings")
        v_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.detail_table.yview)
        h_scroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.detail_table.xview)
        self.detail_table.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.detail_table.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)

        self._poblar_tabla_en(self.detail_table, historial, x0, tol, cifras)

    def generar_campos(self):
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()

        self.matrix_entries = []
        self.b_entries = []
        self.x0_entries = []

        try:
            n = int(self.n_var.get())
        except ValueError:
            messagebox.showerror("Error", "n debe ser un entero.")
            return

        if n <= 0 or n > 11:
            messagebox.showerror("Error", "Usa un n entre 1 y 11 para una vista comoda.")
            return

        tk.Label(self.inputs_frame, text="Matriz A").grid(row=0, column=0, columnspan=n, pady=(0, 4))
        tk.Label(self.inputs_frame, text="Vector b").grid(row=0, column=n + 1, pady=(0, 4))
        tk.Label(self.inputs_frame, text="x0").grid(row=0, column=n + 2, pady=(0, 4))

        for i in range(n):
            row_entries = []
            for j in range(n):
                e = tk.Entry(self.inputs_frame, width=8, justify="center")
                e.grid(row=i + 1, column=j, padx=2, pady=2)
                row_entries.append(e)
            self.matrix_entries.append(row_entries)

            b_entry = tk.Entry(self.inputs_frame, width=8, justify="center")
            b_entry.grid(row=i + 1, column=n + 1, padx=10)
            self.b_entries.append(b_entry)

            x0_entry = tk.Entry(self.inputs_frame, width=8, justify="center")
            x0_entry.grid(row=i + 1, column=n + 2, padx=2)
            x0_entry.insert(0, "0")
            self.x0_entries.append(x0_entry)

    def _leer_datos(self):
        n = int(self.n_var.get())

        A = []
        for i in range(n):
            fila = []
            for j in range(n):
                valor = float(self.matrix_entries[i][j].get())
                fila.append(valor)
            A.append(fila)

        b = [float(self.b_entries[i].get()) for i in range(n)]
        x0 = [float(self.x0_entries[i].get()) for i in range(n)]
        tol = float(self.tol_var.get())
        max_iter = int(self.max_iter_var.get())
        cifras = int(self.cifras_var.get())
        metodo = self.metodo_var.get().strip().lower()

        return A, b, x0, tol, max_iter, cifras, metodo

    def resolver(self):
        try:
            A, b, x0, tol, max_iter, cifras, metodo = self._leer_datos()
            pasos = []
            exacto = True
            if cifras <= 0:
                raise ValueError("El numero de cifras debe ser mayor a cero.")
            if metodo not in ("redondeo", "truncamiento"):
                raise ValueError("Metodo invalido. Usa redondeo o truncamiento.")
            if self.auto_reordenar_var.get():
                A, b, orden, pasos, exacto = reordenar_sistema_por_columnas(A, b)
                pasos.insert(0, "Paso 1: Reordenar ecuaciones para fortalecer la diagonal principal.")
                pasos.append("Paso 2: Despejar x, y, z, ... de cada ecuacion diagonal.")
                pasos.append("Paso 3: Iterar con Gauss-Seidel usando V0.")
            x, iters, err, historial = gauss_seidel(
                A,
                b,
                x0=x0,
                tol=tol,
                max_iter=max_iter,
                cifras=cifras,
                metodo=metodo,
            )
            resid = residuo_inf(A, b, x)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        if es_diagonal_dominante(A):
            aviso = "A es diagonalmente dominante."
        else:
            aviso = "A NO es diagonalmente dominante (puede no converger)."

        self._construir_tabla(historial, x0, tol, cifras)
        self._mostrar_ventana_detalle(A, b, historial, x0, tol, cifras)
        marca = "✔" if err < tol and resid < tol else "✘"
        self.info_var.set(
            f"Resultado: iteraciones={iters} | error_iter={err:.3e} | residuo={resid:.3e} | tolerancia={tol:.3e} | cifras={cifras} | metodo={metodo} {marca} | {aviso}"
        )

        self.proc_text.delete("1.0", tk.END)
        nombres = self._nombres_variables(len(x))
        self.proc_text.insert(tk.END, "Resultados finales por variable:\n")
        for i, nombre in enumerate(nombres):
            delta_final = historial[-1][3][i] if historial else 0.0
            marca_var = "✔" if delta_final < tol else "✘"
            self.proc_text.insert(
                tk.END,
                f"- {nombre} = {x[i]:.{cifras}f}   |delta|={delta_final:.3e} {marca_var}\n",
            )

        if self.auto_reordenar_var.get():
            orden_str = ", ".join(str(i + 1) for i in orden)
            self.proc_text.insert(tk.END, f"\nOrden de ecuaciones usado: [{orden_str}]\n")

    def limpiar_salida(self):
        self.table.delete(*self.table.get_children())
        self.info_var.set("Resultado: pendiente")
        self.proc_text.delete("1.0", tk.END)

    def cargar_ejemplo(self):
        self.n_var.set("3")
        self.generar_campos()

        A_ej = [
            [4.0, 1.0, 2.0],
            [3.0, 5.0, 1.0],
            [1.0, 1.0, 3.0],
        ]
        b_ej = [4.0, 7.0, 3.0]

        for i in range(3):
            for j in range(3):
                self.matrix_entries[i][j].delete(0, tk.END)
                self.matrix_entries[i][j].insert(0, str(A_ej[i][j]))

            self.b_entries[i].delete(0, tk.END)
            self.b_entries[i].insert(0, str(b_ej[i]))

            self.x0_entries[i].delete(0, tk.END)
            self.x0_entries[i].insert(0, "0")

        self.tol_var.set("1e-8")
        self.max_iter_var.set("100")


def main():
    root = tk.Tk()
    root.title("SSELS aproximados")
    root.geometry("1350x850")

    nb = ttk.Notebook(root)
    nb.pack(fill="both", expand=True)

    frame1 = ttk.Frame(nb)
    frame2 = ttk.Frame(nb)

    nb.add(frame1, text="Relajaciones")
    nb.add(frame2, text="Gauss-Seidel")

    # Instanciar las aplicaciones dentro de cada pestaña
    rel_app = RelajacionesApp(frame1)
    rel_app.pack(fill="both", expand=True)

    gs_app = GaussSeidelApp(frame2)

    root.mainloop()


if __name__ == "__main__":
    main()
