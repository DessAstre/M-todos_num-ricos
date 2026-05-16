import tkinter as tk
from tkinter import ttk, messagebox


# Ajuste de curvas por minimos cuadrados (grado configurable 3, 4 o 5)
# Metodo: ecuaciones normales + eliminacion de Gauss

def evaluar_polinomio(coefs, x):
    y = 0.0
    pot = 1.0
    for c in coefs:
        y += c * pot
        pot *= x
    return y


def construir_sistema_normal(xs, ys, grado):
    n = len(xs)

    # Sumas de potencias de x: Σx^k, k=0..2*grado
    sum_x = []
    for k in range(2 * grado + 1):
        s = 0.0
        for x in xs:
            s += x ** k
        sum_x.append(s)

    # Sumas Σx^k * y, k=0..grado
    sum_xy = []
    for k in range(grado + 1):
        s = 0.0
        for i in range(n):
            s += (xs[i] ** k) * ys[i]
        sum_xy.append(s)

    # Matriz A y vector b del sistema A*k = b
    # A[i][j] = Σx^(i+j), b[i] = Σx^i*y
    A = []
    for i in range(grado + 1):
        fila = []
        for j in range(grado + 1):
            fila.append(sum_x[i + j])
        A.append(fila)

    b = sum_xy[:]
    return A, b


def gauss_eliminacion(A, b):
    n = len(A)
    M = [fila[:] for fila in A]
    v = b[:]

    # Eliminacion hacia adelante con normalizacion de pivotes
    for k in range(n):
        if abs(M[k][k]) == 0:
            pivote = None
            for i in range(k + 1, n):
                if abs(M[i][k]) != 0:
                    pivote = i
                    break

            if pivote is None:
                raise ValueError("Sistema singular: no hay solucion unica.")

            M[k], M[pivote] = M[pivote], M[k]
            v[k], v[pivote] = v[pivote], v[k]

        pivote = M[k][k]
        if pivote == 0:
            raise ValueError("Sistema singular: no hay solucion unica.")

        for j in range(k, n):
            M[k][j] /= pivote
        v[k] /= pivote

        for i in range(k + 1, n):
            factor = M[i][k]
            for j in range(k, n):
                M[i][j] -= factor * M[k][j]
            v[i] -= factor * v[k]

    # Sustitucion hacia atras
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        suma = 0.0
        for j in range(i + 1, n):
            suma += M[i][j] * x[j]
        x[i] = v[i] - suma

    return x


def gauss_eliminacion_detallado(A, b):
    n = len(A)
    M = [fila[:] for fila in A]
    v = b[:]
    pasos = []

    pasos.append("Matriz aumentada inicial:")
    pasos.append(matriz_resuelta_gauss_a_texto(M, v))

    # Eliminacion hacia adelante con normalizacion de pivotes
    for k in range(n):
        if abs(M[k][k]) == 0:
            pivote = None
            for i in range(k + 1, n):
                if abs(M[i][k]) != 0:
                    pivote = i
                    break

            if pivote is None:
                raise ValueError("Sistema singular: no hay solucion unica.")

            M[k], M[pivote] = M[pivote], M[k]
            v[k], v[pivote] = v[pivote], v[k]
            pasos.append(f"Intercambio de filas F{k + 1} <-> F{pivote + 1} porque el pivote era cero:")
            pasos.append(matriz_resuelta_gauss_a_texto(M, v))

        pivote = M[k][k]
        if pivote == 0:
            raise ValueError("Sistema singular: no hay solucion unica.")

        for j in range(k, n):
            M[k][j] /= pivote
        v[k] /= pivote
        pasos.append(f"Normalizacion de la fila F{k + 1} para hacer 1 el pivote:")
        pasos.append(matriz_resuelta_gauss_a_texto(M, v))

        for i in range(k + 1, n):
            factor = M[i][k]
            for j in range(k, n):
                M[i][j] -= factor * M[k][j]
            v[i] -= factor * v[k]

        pasos.append(f"Despues de eliminar la columna {k + 1}:")
        pasos.append(matriz_resuelta_gauss_a_texto(M, v))

    # Sustitucion hacia atras
    x = [0.0] * n
    pasos.append("Sustitucion hacia atras:")
    for i in range(n - 1, -1, -1):
        suma = 0.0
        for j in range(i + 1, n):
            suma += M[i][j] * x[j]
        x[i] = v[i] - suma
        pasos.append(
            f"K{i} = {v[i]:.4f} - {suma:.4f} = {x[i]:.4f}"
        )

    return M, v, x, pasos


def formatear_polinomio(coefs):
    partes = []
    for i, c in enumerate(coefs):
        if i == 0:
            partes.append(f"{c:.4f}")
        elif i == 1:
            partes.append(f"{c:.4f}*x")
        else:
            partes.append(f"{c:.4f}*x^{i}")
    return " + ".join(partes)


def ajuste_por_grado(xs, ys, grado):
    A, b = construir_sistema_normal(xs, ys, grado)
    M_gauss, v_gauss, coefs, pasos_gauss = gauss_eliminacion_detallado(A, b)

    yc = []
    S = 0.0
    for i in range(len(xs)):
        yci = evaluar_polinomio(coefs, xs[i])
        yc.append(yci)
        S += (yci - ys[i]) ** 2

    return {
        "grado": grado,
        "A": A,
        "b": b,
        "M_gauss": M_gauss,
        "v_gauss": v_gauss,
        "pasos_gauss": pasos_gauss,
        "coefs": coefs,
        "yc": yc,
        "S": S,
    }


def construir_resultado_desde_coef(xs, ys, grado, coefs):
    yc = []
    S = 0.0
    for i in range(len(xs)):
        yci = evaluar_polinomio(coefs, xs[i])
        yc.append(yci)
        S += (yci - ys[i]) ** 2

    A, b = construir_sistema_normal(xs, ys, grado)
    return {
        "grado": grado,
        "A": A,
        "b": b,
        "coefs": coefs[:],
        "yc": yc,
        "S": S,
    }


def matriz_a_texto(A, b):
    lineas = []
    n = len(A)
    for i in range(n):
        fila = "  ".join(f"{A[i][j]:10.4f}" for j in range(n))
        lineas.append(f"[{fila}]   [{b[i]:10.4f}]")
    return "\n".join(lineas)


def matriz_resuelta_gauss_a_texto(M, v):
    lineas = []
    n = len(M)
    for i in range(n):
        fila = "  ".join(f"{M[i][j]:10.4f}" for j in range(n))
        lineas.append(f"[{fila}]   [{v[i]:10.4f}]")
    return "\n".join(lineas)


def construir_tabla_procedimiento(xs, ys, grado_max):
    filas = []
    for x, y in zip(xs, ys):
        fila = {"x": x, "y": y}
        for k in range(2, 2 * grado_max + 1):
            fila[f"x{k}"] = x ** k
        for k in range(1, grado_max + 1):
            fila[f"x{k}y"] = (x ** k) * y
        filas.append(fila)

    suma = {"x": sum(f["x"] for f in filas), "y": sum(f["y"] for f in filas)}
    for k in range(2, 2 * grado_max + 1):
        clave = f"x{k}"
        suma[clave] = sum(f[clave] for f in filas)
    for k in range(1, grado_max + 1):
        clave = f"x{k}y"
        suma[clave] = sum(f[clave] for f in filas)

    return filas, suma


def tabla_procedimiento_a_texto(filas, suma, grado_max):
    encabezados = ["X", "Y"]
    encabezados.extend([f"X{k}" for k in range(2, 2 * grado_max + 1)])
    encabezados.extend(["XY"] + [f"X{k}Y" for k in range(2, grado_max + 1)])
    ancho = 12
    sep = ""
    for h in encabezados:
        sep += h.rjust(ancho)

    lineas = [sep]
    for f in filas:
        partes = [f"{f['x']:>{ancho}.4f}", f"{f['y']:>{ancho}.4f}"]
        for k in range(2, 2 * grado_max + 1):
            partes.append(f"{f[f'x{k}']:>{ancho}.4f}")
        for k in range(1, grado_max + 1):
            partes.append(f"{f[f'x{k}y']:>{ancho}.4f}")
        lineas.append("".join(partes))

    lineas.append("-" * (ancho * len(encabezados)))
    partes_suma = [f"{suma['x']:>{ancho}.4f}", f"{suma['y']:>{ancho}.4f}"]
    for k in range(2, 2 * grado_max + 1):
        partes_suma.append(f"{suma[f'x{k}']:>{ancho}.4f}")
    for k in range(1, grado_max + 1):
        partes_suma.append(f"{suma[f'x{k}y']:>{ancho}.4f}")
    lineas.append("".join(partes_suma))

    return "\n".join(lineas)


def texto_modelo(grado, coefs):
    partes = [f"{coefs[0]:.4f}"]
    for i in range(1, grado + 1):
        if i == 1:
            partes.append(f"({coefs[i]:.4f})X")
        else:
            partes.append(f"({coefs[i]:.4f})X^{i}")
    return f"Y{grado} = " + " + ".join(partes)


def parsear_datos(texto):
    xs = []
    ys = []
    lineas = texto.strip().splitlines()
    if not lineas:
        raise ValueError("No ingresaste datos.")

    for num_linea, ln in enumerate(lineas, start=1):
        ln = ln.strip()
        if not ln:
            continue
        ln = ln.replace(",", " ")
        partes = ln.split()
        if len(partes) != 2:
            raise ValueError(f"Linea {num_linea}: usa formato x y")
        x = float(partes[0])
        y = float(partes[1])
        xs.append(x)
        ys.append(y)

    if len(xs) < 2:
        raise ValueError("Se requieren al menos 2 puntos.")
    return xs, ys


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Ajuste de Curvas - Minimos Cuadrados")
        self.root.geometry("1920x1080")
        self.root.minsize(900, 620)

        cont = ttk.Frame(root, padding=10)
        cont.pack(fill="both", expand=True)

        top = ttk.LabelFrame(cont, text="Ingreso de datos")
        top.pack(fill="x", pady=(0, 8))

        size_frame = ttk.Frame(top)
        size_frame.grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        ttk.Label(size_frame, text="Cantidad de puntos:").pack(side="left")
        self.n_puntos_var = tk.IntVar(value=7)
        self.n_puntos_spin = tk.Spinbox(
            size_frame,
            from_=2,
            to=50,
            width=5,
            textvariable=self.n_puntos_var,
            font=("Consolas", 10),
        )
        self.n_puntos_spin.pack(side="left", padx=6)
        ttk.Button(size_frame, text="Aplicar tamano", command=self.aplicar_tamano_tabla).pack(side="left")

        self.table_frame = ttk.Frame(top)
        self.table_frame.grid(row=1, column=0, rowspan=3, sticky="w", padx=8, pady=6)
        self.table_entries = []
        self._crear_tabla(7)

        botones = ttk.Frame(top)
        botones.grid(row=1, column=1, sticky="nw", padx=12, pady=6)

        ttk.Label(botones, text="Grado:").pack(side="left", padx=(0, 4))
        self.grado_var = tk.IntVar(value=3)
        self.grado_combo = ttk.Combobox(
            botones,
            width=5,
            state="readonly",
            textvariable=self.grado_var,
            values=(3, 4, 5),
        )
        self.grado_combo.pack(side="left", padx=(0, 8))
        self.grado_combo.current(0)

        ttk.Button(botones, text="Calcular ajuste", command=self.calcular).pack(side="left", padx=(0, 8))
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="left")
        ttk.Button(botones, text="Ver resultados en ventana", command=self.abrir_ventana_resultados).pack(side="left", padx=(8, 0))

        puntos_eval_frame = ttk.LabelFrame(top, text="Puntos a encontrar")
        puntos_eval_frame.grid(row=3, column=1, sticky="nw", padx=12, pady=(0, 8))

        cantidad_frame = ttk.Frame(puntos_eval_frame)
        cantidad_frame.pack(anchor="w", padx=8, pady=(6, 4))
        ttk.Label(cantidad_frame, text="Cantidad de puntos:").pack(side="left")
        self.n_puntos_eval_var = tk.IntVar(value=3)
        self.n_puntos_eval_spin = tk.Spinbox(
            cantidad_frame,
            from_=1,
            to=20,
            width=5,
            textvariable=self.n_puntos_eval_var,
            font=("Consolas", 10),
        )
        self.n_puntos_eval_spin.pack(side="left", padx=6)
        ttk.Button(cantidad_frame, text="Aplicar", command=self.aplicar_tamano_tabla_eval).pack(side="left")

        self.puntos_eval_frame = ttk.Frame(puntos_eval_frame)
        self.puntos_eval_frame.pack(fill="x", padx=8, pady=(0, 8))
        self.puntos_eval_entries = []
        self._crear_tabla_eval(3)

        top.columnconfigure(1, weight=1)

        bottom = ttk.LabelFrame(cont, text="Resultados")
        bottom.pack(fill="both", expand=True)

        salida_frame = ttk.Frame(bottom)
        salida_frame.pack(fill="both", expand=True, padx=8, pady=8)

        self.txt_salida = tk.Text(salida_frame, wrap="none", font=("Consolas", 9))
        y_scroll = ttk.Scrollbar(salida_frame, orient="vertical", command=self.txt_salida.yview)
        x_scroll = ttk.Scrollbar(salida_frame, orient="horizontal", command=self.txt_salida.xview)
        self.txt_salida.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.txt_salida.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        salida_frame.columnconfigure(0, weight=1)
        salida_frame.rowconfigure(0, weight=1)

        self.resultados = []
        self.mejor = None
        self.ventana_resultados = None
        self.txt_resultados_win = None
        self.txt_procedimiento_win = None
        self.texto_procedimiento = ""

        

    def escribir(self, texto):
        self.txt_salida.insert("end", texto + "\n")
        self.txt_salida.see("end")

    def _crear_tabla(self, n_filas, valores_previos=None):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        self.table_entries = []

        tk.Label(self.table_frame, text="Punto", width=8, font=("Arial", 10, "bold"), borderwidth=1, relief="solid").grid(row=0, column=0)
        tk.Label(self.table_frame, text="X", width=12, font=("Arial", 10, "bold"), borderwidth=1, relief="solid").grid(row=0, column=1)
        tk.Label(self.table_frame, text="Y", width=12, font=("Arial", 10, "bold"), borderwidth=1, relief="solid").grid(row=0, column=2)

        defaults = [(-3, 21), (-2, 14), (-1, 9), (0, 6), (1, 5), (2, 6), (3, 9)]
        for i in range(1, n_filas + 1):
            tk.Label(self.table_frame, text=str(i), width=8, font=("Arial", 10), borderwidth=1, relief="solid").grid(row=i, column=0)

            x_ent = tk.Entry(self.table_frame, width=12, font=("Arial", 10), borderwidth=1, relief="solid")
            y_ent = tk.Entry(self.table_frame, width=12, font=("Arial", 10), borderwidth=1, relief="solid")

            if valores_previos and i <= len(valores_previos):
                x_txt, y_txt = valores_previos[i - 1]
                x_ent.insert(0, x_txt)
                y_ent.insert(0, y_txt)
            elif i <= len(defaults):
                x_ent.insert(0, str(defaults[i - 1][0]))
                y_ent.insert(0, str(defaults[i - 1][1]))

            x_ent.grid(row=i, column=1)
            y_ent.grid(row=i, column=2)
            self.table_entries.append((x_ent, y_ent))

    def _crear_tabla_eval(self, n_filas, valores_previos=None):
        for widget in self.puntos_eval_frame.winfo_children():
            widget.destroy()

        self.puntos_eval_entries = []

        tk.Label(self.puntos_eval_frame, text="Punto", width=8, font=("Arial", 10, "bold"), borderwidth=1, relief="solid").grid(row=0, column=0)
        tk.Label(self.puntos_eval_frame, text="X", width=12, font=("Arial", 10, "bold"), borderwidth=1, relief="solid").grid(row=0, column=1)

        for i in range(1, n_filas + 1):
            tk.Label(self.puntos_eval_frame, text=str(i), width=8, font=("Arial", 10), borderwidth=1, relief="solid").grid(row=i, column=0)
            x_ent = tk.Entry(self.puntos_eval_frame, width=12, font=("Arial", 10), borderwidth=1, relief="solid")

            if valores_previos and i <= len(valores_previos):
                x_ent.insert(0, valores_previos[i - 1])

            x_ent.grid(row=i, column=1)
            self.puntos_eval_entries.append(x_ent)

    def aplicar_tamano_tabla_eval(self):
        try:
            n = int(self.n_puntos_eval_var.get())
        except Exception:
            messagebox.showerror("Error", "La cantidad de puntos debe ser un numero entero.")
            return

        if n < 1 or n > 20:
            messagebox.showerror("Error", "La cantidad de puntos debe estar entre 1 y 20.")
            return

        previos = [x_ent.get().strip() for x_ent in self.puntos_eval_entries]
        self._crear_tabla_eval(n, valores_previos=previos)

    def leer_puntos_a_evaluar(self):
        xs = []
        for i, x_ent in enumerate(self.puntos_eval_entries, start=1):
            x_txt = x_ent.get().strip()
            if x_txt == "":
                raise ValueError(f"Punto a encontrar {i}: completa el valor de X")
            try:
                x = float(x_txt)
            except ValueError:
                raise ValueError(f"Punto a encontrar {i}: usa valores numericos")
            xs.append(x)
        return xs

    def aplicar_tamano_tabla(self):
        try:
            n = int(self.n_puntos_var.get())
        except Exception:
            messagebox.showerror("Error", "La cantidad de puntos debe ser un numero entero.")
            return

        if n < 2 or n > 50:
            messagebox.showerror("Error", "La cantidad de puntos debe estar entre 2 y 50.")
            return

        previos = [(x_ent.get().strip(), y_ent.get().strip()) for x_ent, y_ent in self.table_entries]
        self._crear_tabla(n, valores_previos=previos)

    def leer_datos_tabla(self):
        xs, ys = [], []
        for i, (x_ent, y_ent) in enumerate(self.table_entries, start=1):
            x_txt = x_ent.get().strip()
            y_txt = y_ent.get().strip()

            if x_txt == "" and y_txt == "":
                raise ValueError(f"Fila {i}: completa X y Y")
            if x_txt == "" or y_txt == "":
                raise ValueError(f"Fila {i}: la fila esta incompleta")

            try:
                x = float(x_txt)
                y = float(y_txt)
            except ValueError:
                raise ValueError(f"Fila {i}: usa valores numericos")

            xs.append(x)
            ys.append(y)

        return xs, ys

    def limpiar(self):
        self.txt_salida.delete("1.0", "end")
        self.resultados = []
        self.mejor = None
        self.texto_procedimiento = ""
        if self.ventana_resultados is not None and self.ventana_resultados.winfo_exists():
            self.ventana_resultados.destroy()
        self.ventana_resultados = None
        self.txt_resultados_win = None
        self.txt_procedimiento_win = None

    def abrir_ventana_resultados(self):
        texto = self.txt_salida.get("1.0", "end-1c")
        if not texto.strip():
            messagebox.showinfo("Info", "Primero calcula los resultados.")
            return

        if self.ventana_resultados is not None and self.ventana_resultados.winfo_exists():
            self.ventana_resultados.lift()
            self.ventana_resultados.focus_force()
            if self.txt_resultados_win is not None:
                self.txt_resultados_win.delete("1.0", "end")
                self.txt_resultados_win.insert("1.0", texto)
                self.txt_resultados_win.see("1.0")
            if self.txt_procedimiento_win is not None:
                self.txt_procedimiento_win.delete("1.0", "end")
                self.txt_procedimiento_win.insert("1.0", self.texto_procedimiento)
                self.txt_procedimiento_win.see("1.0")
            return

        win = tk.Toplevel(self.root)
        win.title("Resultados completos")
        win.geometry("1100x750")
        win.minsize(900, 600)
        self.ventana_resultados = win

        cont = ttk.Frame(win, padding=8)
        cont.pack(fill="both", expand=True)

        notebook = ttk.Notebook(cont)
        notebook.pack(fill="both", expand=True)

        resultados_tab = ttk.Frame(notebook)
        procedimiento_tab = ttk.Frame(notebook)
        notebook.add(resultados_tab, text="Resultados")
        notebook.add(procedimiento_tab, text="Gauss")

        txt_frame = ttk.Frame(resultados_tab)
        txt_frame.pack(fill="both", expand=True)

        txt = tk.Text(txt_frame, wrap="none", font=("Consolas", 9))
        y_scroll = ttk.Scrollbar(txt_frame, orient="vertical", command=txt.yview)
        x_scroll = ttk.Scrollbar(txt_frame, orient="horizontal", command=txt.xview)
        txt.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.txt_resultados_win = txt

        txt.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        txt_frame.columnconfigure(0, weight=1)
        txt_frame.rowconfigure(0, weight=1)

        txt.insert("1.0", texto)
        txt.see("1.0")

        proc_frame = ttk.Frame(procedimiento_tab)
        proc_frame.pack(fill="both", expand=True)

        txt_proc = tk.Text(proc_frame, wrap="none", font=("Consolas", 9))
        y_scroll_proc = ttk.Scrollbar(proc_frame, orient="vertical", command=txt_proc.yview)
        x_scroll_proc = ttk.Scrollbar(proc_frame, orient="horizontal", command=txt_proc.xview)
        txt_proc.configure(yscrollcommand=y_scroll_proc.set, xscrollcommand=x_scroll_proc.set)
        self.txt_procedimiento_win = txt_proc

        txt_proc.grid(row=0, column=0, sticky="nsew")
        y_scroll_proc.grid(row=0, column=1, sticky="ns")
        x_scroll_proc.grid(row=1, column=0, sticky="ew")
        proc_frame.columnconfigure(0, weight=1)
        proc_frame.rowconfigure(0, weight=1)

        txt_proc.insert("1.0", self.texto_procedimiento)
        txt_proc.see("1.0")

        def cerrar():
            self.ventana_resultados = None
            self.txt_resultados_win = None
            self.txt_procedimiento_win = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", cerrar)

    def calcular(self):
        self.limpiar()
        try:
            xs, ys = self.leer_datos_tabla()
        except Exception as e:
            messagebox.showerror("Error en datos", str(e))
            return

        try:
            grado_objetivo = int(self.grado_var.get())
        except Exception:
            messagebox.showerror("Error", "Selecciona un grado valido (3, 4 o 5).")
            return

        if grado_objetivo not in [3, 4, 5]:
            messagebox.showerror("Error", "Solo se permite ajuste de grado 3, 4 o 5.")
            return

        if len(xs) < grado_objetivo + 1:
            messagebox.showerror(
                "Error",
                f"Para grado {grado_objetivo} se requieren al menos {grado_objetivo + 1} puntos.",
            )
            return

        n = len(xs)
        filas, suma = construir_tabla_procedimiento(xs, ys, grado_objetivo)

        self.escribir("AJUSTE DE CURVAS POR MINIMOS CUADRADOS")
        self.escribir("Procedimiento completo: tabla de apoyo + ecuaciones normales + Gauss")
        self.escribir(f"n = numero de puntos conocidos = {n}\n")
        self.escribir(f"Grado seleccionado = {grado_objetivo}\n")

        self.escribir("TABLA DEL PROCEDIMIENTO:")
        self.escribir(tabla_procedimiento_a_texto(filas, suma, grado_objetivo))
        self.escribir("")

        try:
            resultado_base = ajuste_por_grado(xs, ys, grado_objetivo)
        except Exception as e:
            self.escribir(f"No se pudo resolver el sistema por Gauss para grado {grado_objetivo}: {e}")
            self.mejor = None
            self.resultados = []
            self.texto_procedimiento = ""
            return

        resultados = {}
        for grado in range(1, grado_objetivo + 1):
            coefs_truncados = resultado_base["coefs"][: grado + 1]
            if grado > 1 and abs(coefs_truncados[-1]) <= 1e-12:
                continue
            resultados[grado] = construir_resultado_desde_coef(xs, ys, grado, coefs_truncados)

        self.escribir("")
        self.escribir("MATRICES DE ECUACIONES NORMALES:")
        self.escribir(f"Sistema resuelto por Gauss para grado {grado_objetivo}: A*K = b")
        self.escribir(matriz_a_texto(resultado_base["A"], resultado_base["b"]))
        self.escribir("")
        self.escribir("Matriz aumentada despues de la eliminacion de Gauss:")
        self.escribir(matriz_resuelta_gauss_a_texto(resultado_base["M_gauss"], resultado_base["v_gauss"]))
        self.escribir("")
        self.escribir(
            "Coeficientes obtenidos: "
            + ", ".join(f"K{i} = {k:.4f}" for i, k in enumerate(resultado_base["coefs"]))
        )
        self.escribir("K0..Kn se obtienen de este sistema y Y1..Yn se forman truncando esos coeficientes.")
        self.escribir("")

        self.texto_procedimiento = "\n".join(resultado_base["pasos_gauss"])

        self.escribir("TABLA DE DESVIACIONES:")
        columnas = [("X", 10), ("Y", 10)]
        for grado in range(1, grado_objetivo + 1):
            if grado in resultados:
                columnas.append((f"Y{grado}", 12))
                columnas.append((f"S{grado}", 12))

        encabezado = "".join(f"{titulo:>{ancho}}" for titulo, ancho in columnas)
        self.escribir(encabezado)
        self.escribir("-" * len(encabezado))

        for i in range(n):
            partes = [f"{xs[i]:>10.4f}", f"{ys[i]:>10.4f}"]
            for grado in range(1, grado_objetivo + 1):
                if grado not in resultados:
                    continue
                yc = resultados[grado]["yc"][i]
                yp = ys[i]
                sp = (yc - yp) ** 2
                partes.append(f"{yc:>12.4f}")
                partes.append(f"{sp:>12.4f}")
            self.escribir("".join(partes))

        self.escribir("-" * len(encabezado))
        resumen = [f"{'SUMA':>10}", f"{'':>10}"]
        for grado in range(1, grado_objetivo + 1):
            if grado not in resultados:
                continue
            resumen.append(f"{'':>12}")
            resumen.append(f"{resultados[grado]['S']:>12.4f}")
        self.escribir("".join(resumen))

        self.escribir("")
        self.escribir("RESULTADOS (INCISOS):")
        literal = ord("a")

        for grado in range(grado_objetivo, 0, -1):
            if grado in resultados:
                self.escribir(f"{chr(literal)}) {texto_modelo(grado, resultados[grado]['coefs'])}")
            else:
                self.escribir(f"{chr(literal)}) Y{grado} = No existe ya que K{grado} es igual a cero")
            literal += 1

        for grado in range(grado_objetivo, 0, -1):
            if grado in resultados:
                self.escribir(f"{chr(literal)}) S{grado} = {resultados[grado]['S']:.6f}")
            else:
                self.escribir(f"{chr(literal)}) S{grado} = No existe por no haber Y{grado}")
            literal += 1

        mejor = min(resultados.values(), key=lambda rr: rr["S"])
        self.escribir(
            f"{chr(literal)}) Se elige Y{mejor['grado']} porque tiene el menor margen de error "
            f"(S{mejor['grado']} = {mejor['S']:.6f})."
        )
        literal += 1

        self.mejor = mejor
        self.resultados = resultados

        try:
            xs_eval = self.leer_puntos_a_evaluar()
        except Exception as e:
            messagebox.showerror("Error en puntos a encontrar", str(e))
            return

        self.escribir("")
        self.escribir(f"{chr(literal)}) Puntos a encontrar:")
        self.escribir("    No.           X           Y")
        self.escribir("    -------------------------------")
        coefs_redondeados = [round(k, 4) for k in mejor["coefs"]]
        for i, x_eval in enumerate(xs_eval, start=1):
            y_eval = evaluar_polinomio(coefs_redondeados, x_eval)
            self.escribir(f"    {i:>2}   {x_eval:>10.4f}   {y_eval:>10.4f}")

        self.abrir_ventana_resultados()


def main():
    root = tk.Tk()
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()