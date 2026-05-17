import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk


def interpolacion_lineal(x0, y0, x1, y1, x):
    if x1 == x0:
        raise ValueError("x0 y x1 no pueden ser iguales.")
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def interpolacion_lineal_inversa(x0, y0, x1, y1, y):
    if y1 == y0:
        raise ValueError("y0 y y1 no pueden ser iguales para calcular x.")
    return x0 + (x1 - x0) * (y - y0) / (y1 - y0)


def resolver_p3_lineal(x0, y0, x1, y1, x3_texto, y3_texto):
    x3_vacio = x3_texto.strip() == ""
    y3_vacio = y3_texto.strip() == ""

    if x3_vacio and y3_vacio:
        raise ValueError("En P3 debes ingresar una coordenada y dejar la otra en blanco.")
    if (not x3_vacio) and (not y3_vacio):
        raise ValueError("En P3 deja vacia solo la coordenada que quieres calcular.")

    if y3_vacio:
        x3 = float(x3_texto)
        y3, detalle = desarrollo_lineal(x0, y0, x1, y1, x3)
        return x3, y3, detalle

    y3 = float(y3_texto)
    x3, detalle = desarrollo_lineal_inverso(x0, y0, x1, y1, y3)
    return x3, y3, detalle


def interpolacion_lagrange(xs, ys, x):
    if len(xs) != len(ys):
        raise ValueError("Las listas xs y ys deben tener la misma longitud.")
    if len(xs) < 2:
        raise ValueError("Debes proporcionar al menos dos puntos.")
    if len(set(xs)) != len(xs):
        raise ValueError("Los valores de xs no pueden repetirse.")

    n = len(xs)
    resultado = 0.0
    for i in range(n):
        termino = ys[i]
        for j in range(n):
            if i != j:
                termino *= (x - xs[j]) / (xs[i] - xs[j])
        resultado += termino
    return resultado


def formatear_numero(valor):
    if abs(valor - round(valor)) < 1e-12:
        return str(int(round(valor)))
    return f"{valor:.6g}"


def desarrollo_lineal(x0, y0, x1, y1, x):
    y = interpolacion_lineal(x0, y0, x1, y1, x)
    pendiente = (y1 - y0) / (x1 - x0)

    lineas = [
        "Interpolacion lineal (como en clase)",
        "",
        f"P1 = ({formatear_numero(x0)}, {formatear_numero(y0)})",
        f"P2 = ({formatear_numero(x1)}, {formatear_numero(y1)})",
        f"x = {formatear_numero(x)}",
        "",
        "Formula:",
        "y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)",
        "",
        "Sustituyendo:",
        f"y = {formatear_numero(y0)} + ({formatear_numero(y1)} - {formatear_numero(y0)}) * "
        f"({formatear_numero(x)} - {formatear_numero(x0)}) / ({formatear_numero(x1)} - {formatear_numero(x0)})",
        f"m = (y1 - y0) / (x1 - x0) = {formatear_numero(pendiente)}",
        "",
        f"Resultado: y({formatear_numero(x)}) = {formatear_numero(y)}",
    ]
    return y, "\n".join(lineas)


def desarrollo_lineal_inverso(x0, y0, x1, y1, y):
    x = interpolacion_lineal_inversa(x0, y0, x1, y1, y)
    pendiente_inv = (x1 - x0) / (y1 - y0)

    lineas = [
        "Interpolacion lineal inversa (como en clase)",
        "",
        f"P1 = ({formatear_numero(x0)}, {formatear_numero(y0)})",
        f"P2 = ({formatear_numero(x1)}, {formatear_numero(y1)})",
        f"y = {formatear_numero(y)}",
        "",
        "Formula:",
        "x = x0 + (x1 - x0) * (y - y0) / (y1 - y0)",
        "",
        "Sustituyendo:",
        f"x = {formatear_numero(x0)} + ({formatear_numero(x1)} - {formatear_numero(x0)}) * "
        f"({formatear_numero(y)} - {formatear_numero(y0)}) / ({formatear_numero(y1)} - {formatear_numero(y0)})",
        f"m_inv = (x1 - x0) / (y1 - y0) = {formatear_numero(pendiente_inv)}",
        "",
        f"Resultado: x({formatear_numero(y)}) = {formatear_numero(x)}",
    ]
    return x, "\n".join(lineas)


def _segmento_por_x(points, x_objetivo):
    ordenados = sorted(points, key=lambda p: p[0])
    xs = [p[0] for p in ordenados]
    if len(set(xs)) != len(xs):
        raise ValueError("No se permiten valores de x repetidos para interpolar y en funcion de x.")

    if x_objetivo <= xs[0]:
        i0, i1 = 0, 1
    elif x_objetivo >= xs[-1]:
        i0, i1 = len(xs) - 2, len(xs) - 1
    else:
        i0 = 0
        for i in range(len(xs) - 1):
            if xs[i] <= x_objetivo <= xs[i + 1]:
                i0 = i
                break
        i1 = i0 + 1

    return ordenados, i0, i1


def _segmento_por_y(points, y_objetivo):
    ordenados = sorted(points, key=lambda p: p[1])
    ys = [p[1] for p in ordenados]
    if len(set(ys)) != len(ys):
        raise ValueError("No se permiten valores de y repetidos para interpolar x en funcion de y.")

    if y_objetivo <= ys[0]:
        i0, i1 = 0, 1
    elif y_objetivo >= ys[-1]:
        i0, i1 = len(ys) - 2, len(ys) - 1
    else:
        i0 = 0
        for i in range(len(ys) - 1):
            if ys[i] <= y_objetivo <= ys[i + 1]:
                i0 = i
                break
        i1 = i0 + 1

    return ordenados, i0, i1


def desarrollo_lineal_segmentado(points, objetivo, modo):
    if len(points) < 2:
        raise ValueError("Debes proporcionar al menos dos puntos.")

    if modo == "y":
        ordenados, i0, i1 = _segmento_por_x(points, objetivo)
        x0, y0 = ordenados[i0]
        x1, y1 = ordenados[i1]
        y, detalle_base = desarrollo_lineal(x0, y0, x1, y1, objetivo)
        encabezado = [
            "Interpolacion lineal por segmentos",
            f"Variable objetivo: y (dado x={formatear_numero(objetivo)})",
            "",
            "Puntos dados (ordenados por x): "
            + ", ".join(
                f"({formatear_numero(px)}, {formatear_numero(py)})" for px, py in ordenados
            ),
            (
                "Segmento usado: "
                f"P{i0 + 1}=({formatear_numero(x0)}, {formatear_numero(y0)}) y "
                f"P{i1 + 1}=({formatear_numero(x1)}, {formatear_numero(y1)})"
            ),
            "Este segmento contiene el valor objetivo (o es el mas cercano para extrapolar).",
            "",
            "--- Desarrollo del calculo ---",
            detalle_base,
        ]
        return y, "\n".join(encabezado)

    ordenados, i0, i1 = _segmento_por_y(points, objetivo)
    x0, y0 = ordenados[i0]
    x1, y1 = ordenados[i1]
    x, detalle_base = desarrollo_lineal_inverso(x0, y0, x1, y1, objetivo)
    encabezado = [
        "Interpolacion lineal por segmentos",
        f"Variable objetivo: x (dado y={formatear_numero(objetivo)})",
        "",
        "Puntos dados (ordenados por y): "
        + ", ".join(
            f"({formatear_numero(px)}, {formatear_numero(py)})" for px, py in ordenados
        ),
        (
            "Segmento usado: "
            f"P{i0 + 1}=({formatear_numero(x0)}, {formatear_numero(y0)}) y "
            f"P{i1 + 1}=({formatear_numero(x1)}, {formatear_numero(y1)})"
        ),
        "Este segmento contiene el valor objetivo (o es el mas cercano para extrapolar).",
        "",
        "--- Desarrollo del calculo ---",
        detalle_base,
    ]
    return x, "\n".join(encabezado)


def desarrollo_lagrange(xs, ys, valor_objetivo, variable_independiente="x", variable_dependiente="y"):
    resultado = interpolacion_lagrange(xs, ys, valor_objetivo)
    n = len(xs)

    lineas = [
        "Interpolacion de Lagrange (como en clase)",
        "",
        f"n = {n} puntos, grado = {n - 1}",
        f"{variable_independiente} evaluado = {formatear_numero(valor_objetivo)}",
        "",
        "Formula:",
        f"P({variable_independiente}) = sum( {variable_dependiente}i * Li({variable_independiente}) )",
        f"Li({variable_independiente}) = prod( ({variable_independiente} - {variable_independiente}j)/"
        f"({variable_independiente}i - {variable_independiente}j) ), j != i",
        "",
        "Desarrollo por termino:",
    ]

    suma = 0.0
    for i in range(n):
        xi = xs[i]
        yi = ys[i]
        num_factores = []
        den_factores = []
        num_eval = 1.0
        den_eval = 1.0

        for j in range(n):
            if i == j:
                continue
            xj = xs[j]
            num_factores.append(f"({variable_independiente} - {formatear_numero(xj)})")
            den_factores.append(f"({formatear_numero(xi)} - {formatear_numero(xj)})")
            num_eval *= (valor_objetivo - xj)
            den_eval *= (xi - xj)

        li = num_eval / den_eval
        termino = yi * li
        suma += termino

        lineas.append(
            f"L{i}({variable_independiente}) = {' * '.join(num_factores)} / {' * '.join(den_factores)}"
        )
        lineas.append(
            f"L{i}({formatear_numero(valor_objetivo)}) = {formatear_numero(num_eval)} / "
            f"{formatear_numero(den_eval)} = {formatear_numero(li)}"
        )
        lineas.append(
            f"Termino {i}: {variable_dependiente}{i} * L{i} = {formatear_numero(yi)} * "
            f"{formatear_numero(li)} = {formatear_numero(termino)}"
        )
        lineas.append("")

    lineas.append(f"P({formatear_numero(valor_objetivo)}) = {formatear_numero(suma)}")
    lineas.append(
        f"Resultado: {variable_dependiente}({formatear_numero(valor_objetivo)}) = "
        f"{formatear_numero(resultado)}"
    )
    return resultado, "\n".join(lineas)


class AppInterpolacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interpolacion Lineal y de Lagrange")
        self.geometry("1920x1080")
        self.resizable(True, True)
        self._crear_interfaz()

    def _crear_interfaz(self):
        contenedor = ttk.Frame(self, padding=12)
        contenedor.pack(fill="both", expand=True)

        titulo = ttk.Label(
            contenedor,
            text="Calculadora de Interpolacion",
            font=("Segoe UI", 14, "bold"),
        )
        titulo.pack(pady=(0, 10))

        tabs = ttk.Notebook(contenedor)
        tabs.pack(fill="both", expand=True)

        self._crear_tab_lineal(tabs)
        self._crear_tab_lagrange(tabs)

    def _crear_tab_lineal(self, notebook):
        tab = ttk.Frame(notebook, padding=12)
        notebook.add(tab, text="Lineal")

        controles = ttk.LabelFrame(tab, text="Configuracion", padding=8)
        controles.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))

        ttk.Label(controles, text="Cantidad de puntos dados:").grid(row=0, column=0, sticky="w")
        self.cantidad_lineal = tk.IntVar(value=3)
        self.spin_lineal = tk.Spinbox(
            controles,
            from_=2,
            to=12,
            width=6,
            textvariable=self.cantidad_lineal,
            command=self._reconstruir_tabla_lineal,
        )
        self.spin_lineal.grid(row=0, column=1, padx=(6, 12), sticky="w")

        ttk.Button(controles, text="Rebuild tabla", command=self._reconstruir_tabla_lineal).grid(
            row=0,
            column=2,
            sticky="w",
        )

        ttk.Label(controles, text="Variable a calcular:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.modo_lineal = tk.StringVar(value="y")
        ttk.Radiobutton(controles, text="Calcular y (con x)", variable=self.modo_lineal, value="y").grid(
            row=1,
            column=1,
            sticky="w",
            pady=(8, 0),
        )
        ttk.Radiobutton(controles, text="Calcular x (con y)", variable=self.modo_lineal, value="x").grid(
            row=1,
            column=2,
            sticky="w",
            pady=(8, 0),
        )

        ttk.Label(controles, text="Valor objetivo:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.objetivo_lineal_entry = ttk.Entry(controles, width=16)
        self.objetivo_lineal_entry.grid(row=2, column=1, sticky="w", pady=(8, 0))
        self.objetivo_lineal_entry.insert(0, "4")

        self.tabla_lineal_frame = ttk.LabelFrame(tab, text="Puntos (x, y)", padding=8)
        self.tabla_lineal_frame.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.entradas_lineales = []
        self._reconstruir_tabla_lineal()

        ttk.Button(tab, text="Calcular interpolacion lineal", command=self.calcular_lineal).grid(
            row=2,
            column=0,
            columnspan=2,
            pady=8,
            sticky="ew",
        )

        ttk.Button(tab, text="Limpiar", command=self.limpiar_lineal).grid(
            row=2,
            column=2,
            padx=(8, 0),
            pady=8,
            sticky="ew",
        )

        self.resultado_lineal = ttk.Label(tab, text="Resultado: -", font=("Segoe UI", 10, "bold"))
        self.resultado_lineal.grid(row=3, column=0, columnspan=3, sticky="w")

        self.detalle_lineal = scrolledtext.ScrolledText(tab, height=14, wrap="word")
        self.detalle_lineal.grid(row=4, column=0, columnspan=3, pady=(8, 0), sticky="nsew")
        self._actualizar_detalle(self.detalle_lineal, "Aqui aparecera el procedimiento paso a paso.")

        for c in range(3):
            tab.columnconfigure(c, weight=1)
        tab.rowconfigure(4, weight=1)

    def _reconstruir_tabla_lineal(self):
        for widget in self.tabla_lineal_frame.winfo_children():
            widget.destroy()

        cantidad = self.cantidad_lineal.get()
        self.entradas_lineales = []

        ttk.Label(self.tabla_lineal_frame, text="Punto", width=8).grid(row=0, column=0, padx=4, sticky="w")
        ttk.Label(self.tabla_lineal_frame, text="x", width=16).grid(row=0, column=1, padx=4, sticky="w")
        ttk.Label(self.tabla_lineal_frame, text="y", width=16).grid(row=0, column=2, padx=4, sticky="w")

        ejemplos = [(1, 3), (2, 7), (-1, 1), (3, 9), (4, 11)]

        for i in range(cantidad):
            ttk.Label(self.tabla_lineal_frame, text=f"P{i + 1}").grid(row=i + 1, column=0, padx=4, pady=2, sticky="w")

            ex = ttk.Entry(self.tabla_lineal_frame, width=16)
            ey = ttk.Entry(self.tabla_lineal_frame, width=16)
            ex.grid(row=i + 1, column=1, padx=4, pady=2, sticky="w")
            ey.grid(row=i + 1, column=2, padx=4, pady=2, sticky="w")

            if i < len(ejemplos):
                ex.insert(0, str(ejemplos[i][0]))
                ey.insert(0, str(ejemplos[i][1]))

            self.entradas_lineales.append((ex, ey))

    def _crear_tab_lagrange(self, notebook):
        tab = ttk.Frame(notebook, padding=12)
        notebook.add(tab, text="Lagrange")

        controles = ttk.LabelFrame(tab, text="Configuracion", padding=8)
        controles.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))

        ttk.Label(controles, text="Cantidad de puntos dados:").grid(row=0, column=0, sticky="w")
        self.cantidad_lagrange = tk.IntVar(value=3)
        self.spin_lagrange = tk.Spinbox(
            controles,
            from_=2,
            to=12,
            width=6,
            textvariable=self.cantidad_lagrange,
            command=self._reconstruir_tabla_lagrange,
        )
        self.spin_lagrange.grid(row=0, column=1, padx=(6, 12), sticky="w")

        ttk.Button(controles, text="Rebuild tabla", command=self._reconstruir_tabla_lagrange).grid(
            row=0,
            column=2,
            sticky="w",
        )

        ttk.Label(controles, text="Variable a calcular:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.modo_lagrange = tk.StringVar(value="y")
        ttk.Radiobutton(controles, text="Calcular y (con x)", variable=self.modo_lagrange, value="y", command=self._actualizar_modo_lagrange).grid(
            row=1,
            column=1,
            sticky="w",
            pady=(8, 0),
        )
        ttk.Radiobutton(controles, text="Calcular x (con y)", variable=self.modo_lagrange, value="x", command=self._actualizar_modo_lagrange).grid(
            row=1,
            column=2,
            sticky="w",
            pady=(8, 0),
        )

        self.lbl_objetivo_lagrange = ttk.Label(controles, text="Valor objetivo:")
        self.lbl_objetivo_lagrange.grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.x_lagrange_entry = ttk.Entry(controles, width=16)
        self.x_lagrange_entry.grid(row=2, column=1, sticky="w", pady=(8, 0))
        self.x_lagrange_entry.insert(0, "1.5")

        self.tabla_lagrange_frame = ttk.LabelFrame(tab, text="Puntos (x, y)", padding=8)
        self.tabla_lagrange_frame.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.entradas_lagrange = []
        self._reconstruir_tabla_lagrange()

        ttk.Button(tab, text="Calcular interpolacion de Lagrange", command=self.calcular_lagrange).grid(
            row=2,
            column=0,
            columnspan=2,
            pady=8,
            sticky="ew",
        )

        ttk.Button(tab, text="Limpiar", command=self.limpiar_lagrange).grid(
            row=2,
            column=2,
            padx=(8, 0),
            pady=8,
            sticky="ew",
        )

        self.resultado_lagrange = ttk.Label(tab, text="Resultado: -", font=("Segoe UI", 10, "bold"))
        self.resultado_lagrange.grid(row=3, column=0, columnspan=3, sticky="w")

        self.detalle_lagrange = scrolledtext.ScrolledText(tab, height=14, wrap="word")
        self.detalle_lagrange.grid(row=4, column=0, columnspan=3, pady=(8, 0), sticky="nsew")
        self._actualizar_detalle(self.detalle_lagrange, "Aqui aparecera el procedimiento paso a paso.")

        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.columnconfigure(2, weight=0)
        tab.rowconfigure(4, weight=1)

    def _reconstruir_tabla_lagrange(self):
        for widget in self.tabla_lagrange_frame.winfo_children():
            widget.destroy()

        cantidad = self.cantidad_lagrange.get()
        self.entradas_lagrange = []

        ttk.Label(self.tabla_lagrange_frame, text="Punto", width=8).grid(row=0, column=0, padx=4, sticky="w")
        ttk.Label(self.tabla_lagrange_frame, text="x", width=16).grid(row=0, column=1, padx=4, sticky="w")
        ttk.Label(self.tabla_lagrange_frame, text="y", width=16).grid(row=0, column=2, padx=4, sticky="w")

        ejemplos = [(0, 1), (1, 2), (2, 5), (3, 10), (-1, 0), (1.5, 3.5)]

        for i in range(cantidad):
            ttk.Label(self.tabla_lagrange_frame, text=f"P{i + 1}").grid(row=i + 1, column=0, padx=4, pady=2, sticky="w")

            ex = ttk.Entry(self.tabla_lagrange_frame, width=16)
            ey = ttk.Entry(self.tabla_lagrange_frame, width=16)
            ex.grid(row=i + 1, column=1, padx=4, pady=2, sticky="w")
            ey.grid(row=i + 1, column=2, padx=4, pady=2, sticky="w")

            if i < len(ejemplos):
                ex.insert(0, str(ejemplos[i][0]))
                ey.insert(0, str(ejemplos[i][1]))

            self.entradas_lagrange.append((ex, ey))

    def _actualizar_modo_lagrange(self):
        if self.modo_lagrange.get() == "y":
            self.lbl_objetivo_lagrange.config(text="Evaluar en x:")
        else:
            self.lbl_objetivo_lagrange.config(text="Evaluar en y:")

    @staticmethod
    def _fila_campo(contenedor, texto, fila):
        etiqueta = ttk.Label(contenedor, text=texto)
        etiqueta.grid(row=fila, column=0, padx=(0, 8), pady=4, sticky="w")

        entrada = ttk.Entry(contenedor, width=20)
        entrada.grid(row=fila, column=1, pady=4, sticky="ew")
        contenedor.columnconfigure(1, weight=1)
        return entrada

    def _mostrar_detalle_en_ventana(self, titulo, detalle):
        # Reutiliza una sola ventana para no abrir multiples copias del mismo desarrollo.
        if getattr(self, "ventana_detalle", None) is None or not self.ventana_detalle.winfo_exists():
            self.ventana_detalle = tk.Toplevel(self)
            self.ventana_detalle.geometry("820x560")

            self.texto_ventana_detalle = scrolledtext.ScrolledText(
                self.ventana_detalle,
                wrap="word",
                font=("Consolas", 11),
            )
            self.texto_ventana_detalle.pack(fill="both", expand=True, padx=8, pady=8)

            def _al_cerrar():
                self.ventana_detalle.destroy()
                self.ventana_detalle = None
                self.texto_ventana_detalle = None

            self.ventana_detalle.protocol("WM_DELETE_WINDOW", _al_cerrar)

        self.ventana_detalle.title(titulo)
        self.texto_ventana_detalle.config(state="normal")
        self.texto_ventana_detalle.delete("1.0", tk.END)
        self.texto_ventana_detalle.insert("1.0", detalle)
        self.texto_ventana_detalle.config(state="disabled")
        self.ventana_detalle.lift()
        self.ventana_detalle.focus_force()

    def calcular_lineal(self):
        try:
            puntos = []
            for idx, (ex, ey) in enumerate(self.entradas_lineales, start=1):
                x_txt = ex.get().strip()
                y_txt = ey.get().strip()
                if x_txt == "" or y_txt == "":
                    raise ValueError(f"El punto P{idx} debe tener x e y.")
                try:
                    x_val = float(x_txt)
                    y_val = float(y_txt)
                except ValueError:
                    raise ValueError(f"El punto P{idx} tiene valores no numericos.")
                puntos.append((x_val, y_val))

            objetivo_txt = self.objetivo_lineal_entry.get().strip()
            if objetivo_txt == "":
                raise ValueError("Ingresa un valor objetivo.")

            objetivo = float(objetivo_txt)
            modo = self.modo_lineal.get()
            resultado, detalle = desarrollo_lineal_segmentado(puntos, objetivo, modo)

            if modo == "y":
                self.resultado_lineal.config(
                    text=f"Resultado: y({formatear_numero(objetivo)}) = {formatear_numero(resultado)}"
                )
            else:
                self.resultado_lineal.config(
                    text=f"Resultado: x({formatear_numero(objetivo)}) = {formatear_numero(resultado)}"
                )

            self._actualizar_detalle(self.detalle_lineal, detalle)
            self._mostrar_detalle_en_ventana("Desarrollo - Interpolacion Lineal", detalle)
        except ValueError as error:
            messagebox.showerror("Error", str(error))

    def calcular_lagrange(self):
        try:
            puntos = []
            for idx, (ex, ey) in enumerate(self.entradas_lagrange, start=1):
                x_txt = ex.get().strip()
                y_txt = ey.get().strip()
                if x_txt == "" or y_txt == "":
                    raise ValueError(f"El punto P{idx} debe tener x e y.")
                try:
                    x_val = float(x_txt)
                    y_val = float(y_txt)
                except ValueError:
                    raise ValueError(f"El punto P{idx} tiene valores no numericos.")
                puntos.append((x_val, y_val))

            if len(puntos) < 2:
                raise ValueError("Debes proporcionar al menos dos puntos.")

            objetivo_txt = self.x_lagrange_entry.get().strip()
            if objetivo_txt == "":
                raise ValueError("Ingresa un valor objetivo.")

            objetivo = float(objetivo_txt)
            modo = self.modo_lagrange.get()

            xs = [p[0] for p in puntos]
            ys = [p[1] for p in puntos]

            if modo == "y":
                if len(set(xs)) != len(xs):
                    raise ValueError("Para calcular y con Lagrange no se permiten valores de x repetidos.")
                y, detalle = desarrollo_lagrange(xs, ys, objetivo, "x", "y")
                self.resultado_lagrange.config(
                    text=f"Resultado: y({formatear_numero(objetivo)}) = {formatear_numero(y)}"
                )
            else:
                if len(set(ys)) != len(ys):
                    raise ValueError("Para calcular x con Lagrange no se permiten valores de y repetidos.")
                x, detalle = desarrollo_lagrange(ys, xs, objetivo, "y", "x")
                self.resultado_lagrange.config(
                    text=f"Resultado: x({formatear_numero(objetivo)}) = {formatear_numero(x)}"
                )

            self._actualizar_detalle(self.detalle_lagrange, detalle)
            self._mostrar_detalle_en_ventana("Desarrollo - Interpolacion de Lagrange", detalle)
        except ValueError as error:
            messagebox.showerror("Error", str(error))

    @staticmethod
    def _actualizar_detalle(widget, texto):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", texto)
        widget.config(state="disabled")

    def limpiar_lineal(self):
        for ex, ey in self.entradas_lineales:
            ex.delete(0, tk.END)
            ey.delete(0, tk.END)
        self.objetivo_lineal_entry.delete(0, tk.END)
        self.objetivo_lineal_entry.insert(0, "4")
        self.modo_lineal.set("y")
        self.cantidad_lineal.set(3)
        self._reconstruir_tabla_lineal()

        self.resultado_lineal.config(text="Resultado: -")
        self._actualizar_detalle(self.detalle_lineal, "Aqui aparecera el procedimiento paso a paso.")

    def limpiar_lagrange(self):
        for ex, ey in self.entradas_lagrange:
            ex.delete(0, tk.END)
            ey.delete(0, tk.END)
        self.x_lagrange_entry.delete(0, tk.END)
        self.x_lagrange_entry.insert(0, "1.5")
        self.modo_lagrange.set("y")
        self._actualizar_modo_lagrange()
        self.cantidad_lagrange.set(3)
        self._reconstruir_tabla_lagrange()
        self.resultado_lagrange.config(text="Resultado: -")
        self._actualizar_detalle(self.detalle_lagrange, "Aqui aparecera el procedimiento paso a paso.")


if __name__ == "__main__":
    app = AppInterpolacion()
    app.mainloop()
