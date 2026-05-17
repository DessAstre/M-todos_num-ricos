"""Aplicación GUI para ajuste de curvas por mínimos cuadrados.

Este código utiliza el módulo `ajuste_curvas.py` con operaciones matemáticas.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

try:
    from Parcial3.ajuste_curvas import (
        coeficientes_polinomio_con_pasos,
        evaluar_polinomio,
        normal_equations,
        rss,
        mejor_ajuste,
        extremos_polinomio,
        sistema_normal_texto,
        ssel_4x4_text,
        formato_ecuacion,
        sumas_ajuste,
    )
except ImportError:
    from ajuste_curvas import (  # type: ignore
        coeficientes_polinomio_con_pasos,
        evaluar_polinomio,
        normal_equations,
        rss,
        mejor_ajuste,
        extremos_polinomio,
        sistema_normal_texto,
        ssel_4x4_text,
        formato_ecuacion,
        sumas_ajuste,
    )


class AjusteCurvasApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Métodos Numéricos - Ajuste de Curvas")
        self.root.geometry("900x700")

        frame = tk.Frame(self.root, padx=12, pady=12)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame, text="Datos de entrada (tabla X Y)",
                 font=("Georgia", 14, "bold")).pack(anchor="w")
        tk.Label(
            frame,
            text="Valores a encontrar: Coeficientes del polinomio, Ecuación, RSS, Extremos locales y Predicción.",
            font=("Arial", 11, "italic"),
            fg="darkgreen",
        ).pack(anchor="w", pady=(0, 8))

        count_frame = tk.Frame(frame)
        count_frame.pack(fill="x", pady=(0, 8))
        tk.Label(count_frame, text="Número de puntos:", font=("Arial", 12)).pack(side="left")
        self.num_points_var = tk.IntVar(value=7)
        tk.Spinbox(count_frame, from_=2, to=20, width=4, textvariable=self.num_points_var, font=("Arial", 11)).pack(side="left", padx=6)
        tk.Button(count_frame, text="Generar tabla", font=("Arial", 11), command=self._regenerate_tables).pack(side="left", padx=12)
        tk.Button(count_frame, text="Cargar examen", font=("Arial", 11), fg="darkblue", command=self._cargar_datos_examen).pack(side="left", padx=4)

        main_tables_row = tk.Frame(frame)
        main_tables_row.pack(fill="x", pady=8)

        self.table_frame = tk.Frame(main_tables_row)
        self.table_frame.pack(side="left", anchor="n")

        self.requested_panel = tk.LabelFrame(main_tables_row, text="Evaluación exacta", padx=8, pady=8)
        self.requested_panel.pack(side="left", anchor="n", padx=20)

        header_requested = tk.Frame(self.requested_panel)
        header_requested.pack(fill="x", pady=(0, 6))
        tk.Label(header_requested, text="Cantidad de valores:", font=("Arial", 11)).pack(side="left")
        self.num_requested_var = tk.IntVar(value=4)
        tk.Spinbox(header_requested, from_=1, to=20, width=4, textvariable=self.num_requested_var, font=("Arial", 11), command=self._regenerate_tables).pack(side="left", padx=6)

        self.requested_table_wrap = tk.Frame(self.requested_panel)
        self.requested_table_wrap.pack(fill="both", expand=True)

        tk.Label(self.requested_panel, text="Ingrese los valores X que desea evaluar con la ecuación más exacta.", font=("Arial", 10), wraplength=230, justify="left").pack(anchor="w", pady=(4, 6))

        eval_frame = tk.Frame(self.requested_panel)
        eval_frame.pack(fill="x", pady=(8, 0))
        tk.Button(eval_frame, text="Evaluar exacta", width=14, font=("Arial", 11), command=self.evaluar_ecuacion_exacta).pack(side="left", padx=(0, 8))
        self.eval_result_label = tk.Label(eval_frame, text="Ingrese valores X propios y presione Calcular.", font=("Arial", 10), fg="blue", wraplength=220, justify="left")
        self.eval_result_label.pack(side="left", padx=(0, 8))

        self.table_entries = []
        self.requested_entries = []
        self._build_point_table(self.num_points_var.get())
        self._build_requested_table(self.num_requested_var.get())

        opt_frame = tk.Frame(frame)
        opt_frame.pack(fill="x", pady=8)

        self.grado_var = tk.IntVar(value=3)
        tk.Label(opt_frame, text="Hasta grado:", font=("Arial", 12)).pack(side="left")
        tk.Spinbox(opt_frame, from_=1, to=20, width=4, textvariable=self.grado_var, font=("Arial", 12)).pack(side="left", padx=6)

        self.auto_var = tk.BooleanVar(value=False)
        tk.Checkbutton(opt_frame, text="Elegir mejor grado automáticamente", variable=self.auto_var, font=("Arial", 12)).pack(side="left", padx=20)

        pred_frame = tk.Frame(frame)
        pred_frame.pack(fill="x", pady=6)

        tk.Label(pred_frame, text="Función ajustada mostrada según inciso:", font=("Arial", 12)).pack(side="left")

        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", pady=10)

        tk.Button(btn_frame, text="Calcular", width=12, font=("Arial", 12, "bold"), command=self.calcular).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Hoja de cálculo", width=14, font=("Arial", 12), command=self.mostrar_hoja_calculo).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Limpiar", width=12, font=("Arial", 12), command=self.limpiar).pack(side="left", padx=4)

        self.ultimo_sistema_normal = ""
        self.ultimo_resultados = None
        self.ultimo_data = None
        try:
            import matplotlib.pyplot as plt
            self.has_matplotlib = True
        except ImportError:
            self.has_matplotlib = False

        self._cargar_datos_examen()

    def parse_points(self):
        x_vals, y_vals = [], []
        for i, (x_ent, y_ent) in enumerate(self.table_entries, start=1):
            x_raw = x_ent.get().strip()
            y_raw = y_ent.get().strip()
            if x_raw == "" or y_raw == "":
                continue
            try:
                x = float(x_raw)
                y = float(y_raw)
            except ValueError as exc:
                raise ValueError(f"Fila {i}: valores deben ser numéricos") from exc
            x_vals.append(x)
            y_vals.append(y)

        if len(x_vals) < 2:
            raise ValueError("Se requieren al menos 2 puntos")

        return x_vals, y_vals

    def _clear_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def _build_point_table(self, count: int):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        tk.Label(
            self.table_frame,
            text="Punto",
            width=8,
            font=("Arial", 11, "bold"),
            borderwidth=1,
            relief="solid",
        ).grid(row=0, column=0)
        tk.Label(
            self.table_frame,
            text="X",
            width=12,
            font=("Arial", 11, "bold"),
            borderwidth=1,
            relief="solid",
        ).grid(row=0, column=1)
        tk.Label(
            self.table_frame,
            text="Y",
            width=12,
            font=("Arial", 11, "bold"),
            borderwidth=1,
            relief="solid",
        ).grid(row=0, column=2)

        self.table_entries = []
        for i in range(count):
            tk.Label(
                self.table_frame,
                text=f"{i+1}",
                width=8,
                font=("Arial", 11),
                borderwidth=1,
                relief="solid",
            ).grid(row=i + 1, column=0)
            x_ent = tk.Entry(self.table_frame, width=12, font=("Arial", 11), borderwidth=1, relief="solid")
            x_ent.grid(row=i + 1, column=1)
            y_ent = tk.Entry(self.table_frame, width=12, font=("Arial", 11), borderwidth=1, relief="solid")
            y_ent.grid(row=i + 1, column=2)
            self.table_entries.append((x_ent, y_ent))

    def _build_requested_table(self, count: int):
        for widget in self.requested_table_wrap.winfo_children():
            widget.destroy()

        tk.Label(
            self.requested_table_wrap,
            text="X propio",
            width=12,
            font=("Arial", 11, "bold"),
            borderwidth=1,
            relief="solid",
        ).grid(row=0, column=0)

        self.requested_entries = []
        for i in range(count):
            x_req = tk.Entry(self.requested_table_wrap, width=14, font=("Arial", 11), borderwidth=1, relief="solid")
            x_req.grid(row=i + 1, column=0, padx=(0, 2), pady=2)
            self.requested_entries.append(x_req)

    def _regenerate_tables(self):
        self._build_point_table(self.num_points_var.get())
        self._build_requested_table(self.num_requested_var.get())

    def _parse_requested_entries(self):
        requested = []
        for i, x_ent in enumerate(self.requested_entries, start=1):
            x_raw = x_ent.get().strip()
            if x_raw == "":
                continue
            try:
                x_val = float(x_raw)
            except ValueError as exc:
                raise ValueError(f"Fila solicitada {i}: punto debe ser numérico") from exc
            requested.append(x_val)
        return requested

    def _format_table_header(self, headers, width=10):
        return "  ".join(f"{h:>{width}}" for h in headers)

    def _format_table_separator(self, count, width=10):
        return "  ".join("-" * width for _ in range(count))

    def _format_table_row(self, values, width=10, decimals=4):
        cells = []
        for value in values:
            if isinstance(value, (int, float)):
                cells.append(f"{value:>{width}.{decimals}f}")
            else:
                cells.append(f"{str(value):>{width}}")
        return "  ".join(cells)

    def _build_procedure_table_text(self, x_vals, y_vals, grado):
        headers = ["X", "Y"]
        headers.extend([f"X{p}" for p in range(2, 2 * grado + 1)])
        headers.append("XY")
        headers.extend([f"X{p}Y" for p in range(2, grado + 1)])

        width = 10
        lines = ["TABLA DEL PROCEDIMIENTO:"]
        lines.append(self._format_table_header(headers, width=width))
        lines.append(self._format_table_separator(len(headers), width=width))

        sums = [0.0 for _ in headers]
        for x, y in zip(x_vals, y_vals):
            row = [x, y]
            row.extend([x ** p for p in range(2, 2 * grado + 1)])
            row.append(x * y)
            row.extend([x ** p * y for p in range(2, grado + 1)])
            for idx, val in enumerate(row):
                sums[idx] += val
            lines.append(self._format_table_row(row, width=width, decimals=4))

        lines.append("")
        lines.append("SUMA")
        lines.append(self._format_table_row(sums, width=width, decimals=4))
        return lines, sums

    def _build_desviaciones_table_text(self, x_vals, y_vals, ajustes, max_grado):
        headers = ["X", "Y"]
        for grado in range(1, max_grado + 1):
            headers.extend([f"Y{grado}", f"S{grado}"])

        width = 10
        lines = ["TABLA DE DESVIACIONES:"]
        lines.append(self._format_table_header(headers, width=width))
        lines.append(self._format_table_separator(len(headers), width=width))

        totales = [0.0 for _ in range(max_grado)]
        for x, y in zip(x_vals, y_vals):
            row = [x, y]
            for grado in range(1, max_grado + 1):
                coef_grado = ajustes.get(grado, (None, None, None))[0]
                if coef_grado is None:
                    row.extend(["", ""])
                    continue
                y_fit = sum(coef_grado[i] * (x ** i) for i in range(grado + 1))
                err = (y - y_fit) ** 2
                row.extend([y_fit, err])
                totales[grado - 1] += err
            lines.append(self._format_table_row(row, width=width, decimals=4))

        lines.append("")
        lines.append("SUMA")
        sum_row = []
        for header in headers:
            if header.startswith("S"):
                idx = int(header[1:]) - 1
                sum_row.append(totales[idx])
            else:
                sum_row.append("")
        lines.append(self._format_table_row(sum_row, width=width, decimals=4))
        return lines, totales

    def _gauss_elimination_upper(self, A, b):
        n = len(A)
        M = [row[:] for row in A]
        c = b[:]
        for k in range(n - 1):
            pivot = max(range(k, n), key=lambda i, col=k: abs(M[i][col]))
            if abs(M[pivot][k]) < 1e-15:
                raise ValueError("Sistema singular o mal condicionado")
            if pivot != k:
                M[k], M[pivot] = M[pivot], M[k]
                c[k], c[pivot] = c[pivot], c[k]

            for i in range(k + 1, n):
                factor = M[i][k] / M[k][k]
                for j in range(k, n):
                    M[i][j] -= factor * M[k][j]
                c[i] -= factor * c[k]
        return M, c

    def _format_matrix_rows(self, A, b=None, width=10, decimals=4):
        lines = []
        for i, row in enumerate(A):
            left = " ".join(f"{val:>{width}.{decimals}f}" for val in row)
            if b is None:
                lines.append(f"[ {left} ]")
            else:
                right = f"{b[i]:>{width}.{decimals}f}"
                lines.append(f"[ {left} ] [ {right} ]")
        return lines

    def _build_matrices_normales_text(self, x_vals, y_vals, grado):
        A, b = normal_equations(x_vals, y_vals, grado)
        lines = ["MATRICES DE ECUACIONES NORMALES:"]
        lines.append(f"Sistema resuelto por Gauss para grado {grado}: A*K = b")
        lines.extend(self._format_matrix_rows(A, b))
        try:
            A_up, b_up = self._gauss_elimination_upper(A, b)
            lines.append("")
            lines.append("Matriz aumentada despues de la eliminacion de Gauss:")
            lines.extend(self._format_matrix_rows(A_up, b_up))
        except ValueError:
            pass
        return lines

    def _format_polynomial_trunc(self, coef, grado):
        parts = [f"{coef[0]:.6f}"]
        for i in range(1, grado + 1):
            sign = "+" if coef[i] >= 0 else "-"
            abs_c = abs(coef[i])
            if i == 1:
                parts.append(f" {sign} ({abs_c:.6f})X")
            else:
                parts.append(f" {sign} ({abs_c:.6f})X^{i}")
        return "".join(parts)

    def _build_inciso_text(self, x_vals, y_vals, coef, requested=None, ajustes=None):
        max_grado = len(coef) - 1
        lines = ["RESULTADOS (INCISOS):"]
        letter = ord("a")
        sse_vals = []
        coef_por_grado = {}

        for grado in range(1, max_grado + 1):
            coef_g = ajustes[grado][0] if (ajustes and grado in ajustes) else coef[: grado + 1]
            coef_por_grado[grado] = coef_g
            eq_text = self._format_polynomial_trunc(coef_g, grado)
            nota = ""
            if abs(coef_g[grado]) < 1e-9:
                nota = (
                    f"  [ADVERTENCIA: K{grado} ≈ 0 → "
                    f"ajuste de grado {grado} es idéntico al de grado {grado - 1}]"
                )
            lines.append(f"{chr(letter)}) Y{grado} = {eq_text}{nota}")
            letter += 1

        for grado in range(1, max_grado + 1):
            coef_g = coef_por_grado[grado]
            sse_val = rss(x_vals, y_vals, coef_g)
            sse_vals.append(sse_val)
            lines.append(f"{chr(letter)}) S{grado} = {sse_val:.6f}")
            letter += 1

        best_idx = min(range(len(sse_vals)), key=lambda i: sse_vals[i])
        best_grado = best_idx + 1
        lines.append(
            f"{chr(letter)}) Se elige Y{best_grado} porque tiene el menor margen de error (S{best_grado} = {sse_vals[best_idx]:.6f})."
        )
        letter += 1

        if requested:
            lines.append("")
            lines.append(f"{chr(letter)}) Puntos a encontrar:")
            lines.append(self._format_table_header(["No.", "X", "Y"], width=8))
            best_coef = coef_por_grado[best_grado]
            for idx, x_val in enumerate(requested, start=1):
                y_val = evaluar_polinomio(best_coef, x_val)
                lines.append(self._format_table_row([idx, x_val, y_val], width=8, decimals=4))

        return lines

    def _mostrar_sums_window(self, sumas):
        win = tk.Toplevel(self.root)
        win.title("Sumatorias - Ajuste de Curvas")

        header = tk.Label(win, text="Sumatorias necesarias para el ajuste de curvas", font=("Arial", 12, "bold"))
        header.pack(anchor="w", padx=8, pady=(8, 0))

        explanation = tk.Label(
            win,
            text=(
                "Para un ajuste de grado g se requieren Σx^k para k=0..2g y Σx^p y para p=0..g.",
            ),
            font=("Arial", 10),
            justify="left",
        )
        explanation.pack(anchor="w", padx=8, pady=(0, 8))

        table = self._create_treeview(win, ["sum", "value"], ["Sumatoria", "Valor"], height=max(8, len(sumas)))
        x_power_keys = [int(key[5:]) for key in sumas if key.startswith("sum_x") and key[5:].isdigit()]
        max_x_power = max(x_power_keys) if x_power_keys else 1

        xy_power_keys = []
        for key in sumas:
            if key == "sum_xy":
                xy_power_keys.append(1)
            elif key.startswith("sum_x") and key.endswith("y") and key[5:-1].isdigit():
                xy_power_keys.append(int(key[5:-1]))
        max_xy_power = max(xy_power_keys) if xy_power_keys else 1

        table.insert("", "end", values=("n", str(sumas["n"])))
        table.insert("", "end", values=("Σx", f"{sumas['sum_x']:.6f}"))
        table.insert("", "end", values=("Σy", f"{sumas['sum_y']:.6f}"))

        for p in range(2, max_x_power + 1):
            key = f"sum_x{p}"
            if key in sumas:
                table.insert("", "end", values=(f"Σx^{p}", f"{sumas[key]:.6f}"))

        for p in range(1, max_xy_power + 1):
            key = "sum_xy" if p == 1 else f"sum_x{p}y"
            if key in sumas:
                etiqueta = "Σxy" if p == 1 else f"Σx^{p}y"
                table.insert("", "end", values=(etiqueta, f"{sumas[key]:.6f}"))

        note = tk.Label(
            win,
            text="Los valores en la tabla corresponden a las sumatorias necesarias para construir las ecuaciones normales.",
            font=("Arial", 10, "italic"),
            justify="left",
        )
        note.pack(anchor="w", padx=8, pady=(4, 8))

    def _mostrar_verificacion_window(self, x_vals, y_vals, coef, ajustes=None):
        win = tk.Toplevel(self.root)
        win.title("Desviación - Ajuste de Curvas")

        header = tk.Label(win, text="Tabla de desviación y comparación de valores", font=("Arial", 12, "bold"))
        header.pack(anchor="w", padx=8, pady=(8, 0))

        description = tk.Label(
            win,
            text="Se muestran las predicciones de cada grado y el cuadrado de la desviación entre el valor real y el valor ajustado.",
            font=("Arial", 10),
            justify="left",
        )
        description.pack(anchor="w", padx=8, pady=(0, 8))

        grados, rows, totals = self._build_verification_rows(x_vals, y_vals, coef, ajustes=ajustes)
        columns = ["x", "y"]
        headings = ["X", "Y"]
        for grado in grados:
            columns.append(f"y{grado}")
            columns.append(f"err{grado}")
            headings.append(f"Y{grado}")
            headings.append(f"(Y-Y{grado})^2")

        table = self._create_treeview(win, columns, headings, height=max(8, len(rows) + 1))
        for row in rows:
            table.insert("", "end", values=row)

        summary_text = "Totales de desviación"
        for idx, grado in enumerate(grados):
            summary_text += f" | grado {grado}: {totals[idx]:.6f}"

        summary = tk.Label(win, text=summary_text, font=("Arial", 10, "italic"), justify="left")
        summary.pack(anchor="w", padx=8, pady=(4, 8))

    def _mostrar_requested_window(self, requested, coef, title: str = "Valores solicitados - Ajuste de Curvas"):
        win = tk.Toplevel(self.root)
        win.title(title)

        header = tk.Label(win, text="Evaluación de puntos solicitados sobre la función más exacta", font=("Arial", 12, "bold"))
        header.pack(anchor="w", padx=8, pady=(8, 0))

        table = self._create_treeview(win, ["x", "y"], ["X", "Y"], height=max(6, len(requested)))
        for x_eval in requested:
            y_eval = evaluar_polinomio(coef, x_eval)
            table.insert("", "end", values=(f"{x_eval:.6f}", f"{y_eval:.6f}"))

    def mostrar_sumatorias(self):
        if not self.ultimo_data:
            messagebox.showinfo("Info", "Primero calcule para ver las sumatorias.")
            return
        grado = self.ultimo_resultados["grado"] if self.ultimo_resultados else 1
        self._mostrar_sums_window(
            sumas_ajuste(
                self.ultimo_data["x_vals"],
                self.ultimo_data["y_vals"],
                max_x_power=2 * grado,
                max_xy_power=grado,
            )
        )

    def mostrar_valores_solicitados(self):
        if not self.ultimo_data:
            messagebox.showinfo("Info", "Primero calcule para ver los valores solicitados.")
            return
        if not self.ultimo_data.get("requested"):
            messagebox.showinfo("Info", "No hay puntos solicitados para evaluar.")
            return
        self._mostrar_requested_window(self.ultimo_data["requested"], self.ultimo_resultados["coef"])

    def evaluar_ecuacion_exacta(self):
        if not self.ultimo_resultados:
            messagebox.showinfo("Info", "Primero calcule para poder evaluar la ecuación más exacta.")
            return
        requested = self._parse_requested_entries()
        if not requested:
            messagebox.showinfo("Info", "Ingrese al menos un valor de X para evaluar en la ecuación más exacta.")
            return

        coef = self.ultimo_resultados["coef"]
        results = [f"x={x:.6f} => y={evaluar_polinomio(coef, x):.6f}" for x in requested]
        self.eval_result_label.configure(text=f"Última evaluación: {len(results)} valor(es)")
        self.ultimo_data["requested"] = requested
        self._mostrar_requested_window(requested, coef, title="Evaluación exacta")

    def mostrar_verificacion(self):
        if not self.ultimo_data:
            messagebox.showinfo("Info", "Primero calcule para ver la Desviacion.")
            return
        coef = self.ultimo_resultados["coef"]
        self._mostrar_verificacion_window(
            self.ultimo_data["x_vals"],
            self.ultimo_data["y_vals"],
            coef,
            ajustes=self.ultimo_data.get("ajustes"),
        )

    def mostrar_incisos(self):
        if not self.ultimo_data:
            messagebox.showinfo("Info", "Primero calcule para ver los incisos.")
            return
        incisos = self._build_inciso_text(
            self.ultimo_data["x_vals"],
            self.ultimo_data["y_vals"],
            self.ultimo_resultados["coef"],
            self.ultimo_data.get("requested"),
            ajustes=self.ultimo_data.get("ajustes"),
        )
        self._mostrar_inciso_window(incisos)

    def _mostrar_inciso_window(self, lines):
        win = tk.Toplevel(self.root)
        win.title("Resultados de incisos - Ajuste de Curvas")
        txt = scrolledtext.ScrolledText(win, width=100, height=24, font=("Consolas", 10))
        txt.pack(fill="both", expand=True, padx=8, pady=8)
        txt.insert(tk.END, "Resultados de incisos:\n")
        txt.insert(tk.END, "#" * 60 + "\n")

        for line in lines:
            txt.insert(tk.END, f"{line}\n")

        txt.configure(state="disabled")

    def calcular(self):
        try:
            x_vals, y_vals = self.parse_points()

            ajustes = {}
            max_grado = self.grado_var.get()
            for grado in range(1, max_grado + 1):
                try:
                    coef_grado, pasos_grado = coeficientes_polinomio_con_pasos(x_vals, y_vals, grado)
                    ajustes[grado] = (coef_grado, rss(x_vals, y_vals, coef_grado), pasos_grado)
                except ValueError:
                    continue

            if not ajustes:
                raise RuntimeError("No se pudo calcular ningún ajuste con los datos proporcionados")

            max_grado = self.grado_var.get()
            grado_best, coef_best, error_best = mejor_ajuste(x_vals, y_vals, max_grado=max_grado)
            grado = grado_best
            coef = coef_best
            error = error_best
            pasos = ajustes[grado_best][2]
            mejor_text = f"La mejor curva encontrada es grado {grado_best} con RSS={error_best:.6f}."

            if not self.auto_var.get():
                grado_usuario = self.grado_var.get()
                if grado_usuario in ajustes:
                    coef_usuario, error_usuario, pasos_usuario = ajustes[grado_usuario]
                    if grado_usuario != grado_best:
                        mejor_text = (
                            f"ATENCIÓN: el grado seleccionado ({grado_usuario}) no es el de mínima desviación. "
                            f"Mejor grado = {grado_best} con RSS={error_best:.6f}."
                        )
                        pasos = pasos_usuario + "\n\n-- Mejor ajuste detectado --\n" + pasos
                        coef = coef_best
                        error = error_best
                        grado = grado_best
                    else:
                        grado = grado_usuario
                        coef = coef_usuario
                        error = error_usuario
                        pasos = pasos_usuario
                        mejor_text = f"El grado seleccionado ({grado}) es el de mínima desviación con RSS={error:.6f}."
                else:
                    mejor_text = f"El grado {grado_usuario} no es viable con estos datos. Usando mejor grado {grado_best}."

            sistema = sistema_normal_texto(x_vals, y_vals, grado)
            requested = self._parse_requested_entries()

            self.ultimo_data = {
                "x_vals": x_vals,
                "y_vals": y_vals,
                "ajustes": ajustes,
                "requested": requested,
                "mejor_grado": grado_best,
            }

            self.ultimo_sistema_normal = sistema
            self.ultimo_resultados = {
                "grado": grado,
                "coef": coef,
                "error": error,
                "mejor_text": mejor_text,
                "pasos": pasos,
                "sistema": sistema,
            }
            messagebox.showinfo("Cálculo completo", "Cálculo completado. Ahora seleccione qué desea ver.")

        except (ValueError, TypeError, OverflowError, ArithmeticError, RuntimeError) as exc:
            messagebox.showerror("Error", str(exc))

    def _mostrar_resultados_k(self, grado, coef, error, mejor_text):
        win = tk.Toplevel(self.root)
        win.title(f"Resultados de K - Grado {grado}")
        txt = scrolledtext.ScrolledText(win, width=80, height=24, font=("Consolas", 11))
        txt.pack(fill="both", expand=True, padx=8, pady=8)

        txt.insert(tk.END, f"Resultados de K para grado {grado}\n")
        txt.insert(tk.END, "#" * 55 + "\n")
        txt.insert(tk.END, "Coeficientes del polinomio (K):\n")
        for i, c in enumerate(coef):
            txt.insert(tk.END, f"K{i} = {c:.6f}\n")
        txt.insert(tk.END, "\n")
        txt.insert(tk.END, f"Ecuación: y = {formato_ecuacion(coef)}\n")
        txt.insert(tk.END, f"RSS (desviación): {error:.6f}\n")
        txt.insert(tk.END, f"{mejor_text}\n")
        txt.configure(state="disabled")

    def _mostrar_pasos_operaciones(self, grado, resultado, pasos, sistema=None):
        win = tk.Toplevel(self.root)
        win.title(f"Operaciones e iteraciones (Grado {grado})")
        txt = scrolledtext.ScrolledText(win, width=100, height=36, font=("Consolas", 10))
        txt.pack(fill="both", expand=True, padx=8, pady=8)

        txt.insert(tk.END, "Resumen de resultado:\n")
        txt.insert(tk.END, "\n".join(resultado) + "\n\n")
        if sistema:
            txt.insert(tk.END, "Sistema normal basado en derivadas parciales (∂S/∂Ki=0):\n")
            txt.insert(tk.END, sistema + "\n\n")

        txt.insert(tk.END, "Pasos de cálculo (eliminación de Gauss y demás):\n")
        txt.insert(tk.END, pasos)
        txt.configure(state="disabled")

    def mostrar_ssels(self):
        try:
            x_vals, y_vals = self.parse_points()
            if len(x_vals) < 4:
                raise ValueError("Se requieren al menos 4 puntos para mostrar el SSELS 4x4")

            A, b = normal_equations(x_vals, y_vals, 3)
            win = tk.Toplevel(self.root)
            win.title("SSELS 4x4 - Ajuste de Curvas")

            header = tk.Label(win, text="SSELS 4x4", font=("Arial", 12, "bold"))
            header.pack(anchor="w", padx=8, pady=(8, 0))

            txt = scrolledtext.ScrolledText(win, width=100, height=18, font=("Consolas", 11))
            txt.pack(fill="both", expand=True, padx=8, pady=8)
            txt.insert(tk.END, "Pasos de solución del SSELS 4x4:\n")
            txt.insert(tk.END, ssel_4x4_text(x_vals, y_vals))
            txt.configure(state="disabled")
        except (ValueError, TypeError, OverflowError, ArithmeticError, RuntimeError) as exc:
            messagebox.showerror("Error", str(exc))

    def _build_points_table_text(self, x_vals, y_vals):
        lines = ["Tabla de puntos de entrada:", "     X         Y", "------------------------"]
        for x, y in zip(x_vals, y_vals):
            lines.append(f"{x:12.6f}  {y:12.6f}")
        return "\n".join(lines)

    def _build_verification_text(self, x_vals, y_vals, coef):
        max_grado = self.grado_var.get()
        lines, _ = self._build_desviaciones_table_text(x_vals, y_vals, self.ultimo_data["ajustes"], max_grado)
        return "\n".join(lines)

    def _build_procedure_text(self):
        x_vals = self.ultimo_data["x_vals"]
        y_vals = self.ultimo_data["y_vals"]
        results = self.ultimo_resultados
        coef = results["coef"]
        grado = results["grado"]
        max_grado = self.grado_var.get()
        requested = self.ultimo_data.get("requested", [])

        lines = [f"Grado seleccionado = {grado}", ""]
        proc_lines, _ = self._build_procedure_table_text(x_vals, y_vals, max_grado)
        lines.extend(proc_lines)
        lines.append("")
        desv_lines, _ = self._build_desviaciones_table_text(x_vals, y_vals, self.ultimo_data["ajustes"], max_grado)
        lines.extend(desv_lines)
        lines.append("")
        lines.extend(self._build_matrices_normales_text(x_vals, y_vals, grado))
        lines.append("")
        lines.append(
            "Coeficientes obtenidos: "
            + ", ".join(f"K{i} = {c:.6f}" for i, c in enumerate(coef))
        )
        lines.append("")
        lines.extend(self._build_inciso_text(
            x_vals, y_vals, coef, requested,
            ajustes=self.ultimo_data.get("ajustes"),
        ))

        return "\n".join(lines)

    def _create_treeview(self, parent, columns, headings=None, height=8):
        frame = tk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=4, pady=4)

        tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
        for i, col in enumerate(columns):
            tree.heading(col, text=headings[i] if headings else col)
            tree.column(col, anchor="center", width=120)

        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=y_scroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        return tree

    def _build_verification_rows(self, x_vals, y_vals, coef, ajustes=None):
        grados = list(range(1, len(coef)))
        rows = []
        totals = [0.0 for _ in grados]
        for xi, yi in zip(x_vals, y_vals):
            values = [f"{xi:10.4f}", f"{yi:10.4f}"]
            for index, grado in enumerate(grados):
                coef_g = ajustes[grado][0] if (ajustes and grado in ajustes) else coef[: grado + 1]
                y_fit = evaluar_polinomio(coef_g, xi)
                err = (yi - y_fit) ** 2
                values.append(f"{y_fit:10.4f}")
                values.append(f"{err:10.4f}")
                totals[index] += err
            rows.append(values)

        return grados, rows, totals

    def mostrar_hoja_calculo(self):
        if not self.ultimo_data:
            messagebox.showinfo("Info", "Primero calcule para ver la hoja de cálculo.")
            return

        x_vals = self.ultimo_data["x_vals"]
        y_vals = self.ultimo_data["y_vals"]
        ajustes = self.ultimo_data["ajustes"]
        win = tk.Toplevel(self.root)
        win.title("Hoja de cálculo - Ajuste de Curvas")
        win.geometry("980x680")

        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True)

        tab_puntos = tk.Frame(notebook)
        tab_sumas = tk.Frame(notebook)
        tab_verif = tk.Frame(notebook)
        tab_grafica = tk.Frame(notebook)
        tab_incisos = tk.Frame(notebook)
        tab_ssels = tk.Frame(notebook)
        tab_eval = tk.Frame(notebook)

        notebook.add(tab_puntos, text="Datos de entrada")
        notebook.add(tab_sumas, text="Tabla del procedimiento")
        notebook.add(tab_verif, text="Tabla de desviaciones")
        notebook.add(tab_grafica, text="Gráfica")
        notebook.add(tab_eval, text="Evaluación exacta")
        notebook.add(tab_incisos, text="Incisos")
        notebook.add(tab_ssels, text="SSELS")

        puntos_tree = self._create_treeview(tab_puntos, ["x", "y"], ["X", "Y"], height=10)
        for x, y in zip(x_vals, y_vals):
            puntos_tree.insert("", "end", values=(f"{x:.6f}", f"{y:.6f}"))

        proc_text = scrolledtext.ScrolledText(tab_sumas, width=110, height=26, font=("Consolas", 10))
        proc_text.pack(fill="both", expand=True, padx=8, pady=8)
        proc_lines, _ = self._build_procedure_table_text(x_vals, y_vals, self.grado_var.get())
        proc_text.insert(tk.END, "\n".join(proc_lines))
        proc_text.configure(state="disabled")

        coef = self.ultimo_resultados["coef"]
        verif_text = scrolledtext.ScrolledText(tab_verif, width=110, height=26, font=("Consolas", 10))
        verif_text.pack(fill="both", expand=True, padx=8, pady=8)
        verif_lines, _ = self._build_desviaciones_table_text(x_vals, y_vals, self.ultimo_data["ajustes"], self.grado_var.get())
        verif_text.insert(tk.END, "\n".join(verif_lines))
        verif_text.configure(state="disabled")

        eval_header = tk.Label(tab_eval, text="Evaluación de la ecuación más exacta", font=("Arial", 12, "bold"))
        eval_header.pack(anchor="w", padx=8, pady=(8, 0))
        if self.ultimo_data.get("requested"):
            eval_tree = self._create_treeview(tab_eval, ["x", "y"], ["X", "Y"], height=max(6, len(self.ultimo_data["requested"])))
            for x in self.ultimo_data["requested"]:
                y_eval = evaluar_polinomio(coef, x)
                eval_tree.insert("", "end", values=(f"{x:.6f}", f"{y_eval:.6f}"))
        else:
            tk.Label(tab_eval, text="No hay valores para evaluar. Ingrese datos en el panel principal y presione 'Calcular'.", font=("Arial", 10), justify="left", wraplength=920).pack(anchor="w", padx=8, pady=8)

        incisos_text = self._build_inciso_text(
            x_vals,
            y_vals,
            coef,
            self.ultimo_data.get("requested"),
            ajustes=ajustes,
        )
        incisos_widget = scrolledtext.ScrolledText(tab_incisos, width=100, height=32, font=("Consolas", 10))
        incisos_widget.pack(fill="both", expand=True, padx=8, pady=8)
        incisos_widget.insert(tk.END, "\n".join(incisos_text))
        incisos_widget.configure(state="disabled")

        tk.Label(tab_ssels, text="SSELS 4x4", font=("Arial", 12, "bold")).pack(anchor="w", padx=8, pady=(8, 0))
        ssel_steps = scrolledtext.ScrolledText(tab_ssels, width=100, height=18, font=("Consolas", 10))
        ssel_steps.pack(fill="both", expand=True, padx=8, pady=8)
        ssel_steps.insert(tk.END, ssel_4x4_text(x_vals, y_vals))
        ssel_steps.configure(state="disabled")

        if self.has_matplotlib:
            try:
                import matplotlib.pyplot as plt
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

                min_x, max_x = min(x_vals), max(x_vals)
                span = (max_x - min_x) or 1.0
                xs = [min_x - 0.2 * span + i * (1.4 * span) / 300 for i in range(301)]

                fig = plt.Figure(dpi=100)
                ax = fig.add_subplot(1, 1, 1)
                for grado, ajuste in sorted(ajustes.items()):
                    coef_plot = ajuste[0]
                    formula = formato_ecuacion(coef_plot)
                    y_fit_plot = [evaluar_polinomio(coef_plot, xi) for xi in xs]
                    ax.plot(xs, y_fit_plot, label=f"grado {grado}: y = {formula}")
                ax.scatter(x_vals, y_vals, label="Datos originales", color="black", zorder=5)
                ax.set_title("Ajuste de curvas")
                ax.set_xlabel("x")
                ax.set_ylabel("y")
                ax.legend(fontsize=8)
                ax.grid(True)
                fig.tight_layout()

                canvas = FigureCanvasTkAgg(fig, master=tab_grafica)
                canvas.draw()
                canvas_widget = canvas.get_tk_widget()
                canvas_widget.pack(fill="both", expand=True, padx=8, pady=8)

                def _resize_graph(event):
                    fig.set_size_inches(event.width / fig.dpi, event.height / fig.dpi, forward=True)
                    fig.tight_layout()
                    canvas.draw_idle()

                tab_grafica.bind("<Configure>", _resize_graph)
            except Exception as exc:
                tk.Label(tab_grafica, text=f"No se pudo mostrar la gráfica: {exc}", fg="red").pack(fill="both", expand=True, padx=8, pady=8)
        else:
            tk.Label(tab_grafica, text="matplotlib no está disponible. No se puede mostrar la gráfica.", fg="red").pack(fill="both", expand=True, padx=8, pady=8)


    def mostrar_k_y_pasos(self):
        if not self.ultimo_resultados:
            messagebox.showinfo("Info", "Primero calcule para generar los resultados de K y los pasos.")
            return
        self._mostrar_resultados_k(
            self.ultimo_resultados["grado"],
            self.ultimo_resultados["coef"],
            self.ultimo_resultados["error"],
            self.ultimo_resultados["mejor_text"],
        )
        resumen = [
            f"Grado seleccionado: {self.ultimo_resultados['grado']}",
            "Coeficientes: " + str([round(c, 6) for c in self.ultimo_resultados["coef"]]),
            f"RSS: {self.ultimo_resultados['error']:.6f}",
            self.ultimo_resultados["mejor_text"],
        ]
        self._mostrar_pasos_operaciones(
            self.ultimo_resultados["grado"],
            resumen,
            self.ultimo_resultados["pasos"],
            self.ultimo_resultados["sistema"],
        )

    def graficar_funciones(self):
        try:
            x_vals, y_vals = self.parse_points()

            ajustes = {}
            max_grado = self.grado_var.get()
            for grado_plot in range(1, max_grado + 1):
                try:
                    coef_plot, _ = coeficientes_polinomio_con_pasos(x_vals, y_vals, grado_plot)
                    ajustes[grado_plot] = coef_plot
                except ValueError:
                    continue

            if self.auto_var.get():
                grado, coef, error = mejor_ajuste(x_vals, y_vals)
                pasos = coeficientes_polinomio_con_pasos(x_vals, y_vals, grado)[1]
                mejor_text = f"(modo auto: mejor grado encontrado = {grado})"
            else:
                grado = self.grado_var.get()
                coef, pasos = coeficientes_polinomio_con_pasos(x_vals, y_vals, grado)
                error = rss(x_vals, y_vals, coef)
                grado_best, _, error_best = mejor_ajuste(x_vals, y_vals)
                if grado_best != grado:
                    mejor_text = f"ATENCIÓN: el mejor grado es {grado_best} con RSS={error_best:.6f}, pero se eligió {grado}."
                else:
                    mejor_text = f"El grado seleccionado ({grado}) es el de mínima desviación con RSS={error:.6f}."

            min_x, max_x = min(x_vals), max(x_vals)
            span = (max_x - min_x) or 1.0
            xs = [min_x - 0.2 * span + i * (1.4 * span) / 300 for i in range(301)]

            sistema = self.ultimo_sistema_normal or sistema_normal_texto(x_vals, y_vals, grado)

            if hasattr(__import__("matplotlib"), "pyplot"):
                import matplotlib.pyplot as plt

                fig = plt.figure("Ajuste de Curvas - Grafica")
                fig.clf()
                ax = fig.add_subplot(1, 1, 1)
                for grado_plot, coef_plot in ajustes.items():
                    formula = formato_ecuacion(coef_plot)
                    y_fit_plot = [evaluar_polinomio(coef_plot, xi) for xi in xs]
                    ax.plot(xs, y_fit_plot, label=f"grado {grado_plot}: y = {formula}")
                ax.scatter(x_vals, y_vals, label="Puntos originales", color="black", zorder=5)
                ax.set_title("Funciones y ajustes por grado")
                ax.set_xlabel("x")
                ax.set_ylabel("y")
                ax.legend(fontsize=8)
                ax.grid(True)

                plt.tight_layout()
                plt.show()
            else:
                messagebox.showinfo("Aviso", "matplotlib no está disponible. No se puede graficar.")

        except (ValueError, TypeError, OverflowError, ArithmeticError, RuntimeError) as exc:
            messagebox.showerror("Error", str(exc))

    def _cargar_datos_examen(self):
        _X = [-4, -3, -2, -1, 0, 1, 2]
        _Y = [-3, 11, 13, 9, 5, 7, 21]
        _REQUESTED = [-5, 3, 4, 5]

        self.num_points_var.set(len(_X))
        self.num_requested_var.set(len(_REQUESTED))
        self._build_point_table(len(_X))
        self._build_requested_table(len(_REQUESTED))
        self.grado_var.set(3)

        for (x_ent, y_ent), xv, yv in zip(self.table_entries, _X, _Y):
            x_ent.delete(0, "end")
            y_ent.delete(0, "end")
            x_ent.insert(0, str(xv))
            y_ent.insert(0, str(yv))

        for x_ent, xv in zip(self.requested_entries, _REQUESTED):
            x_ent.delete(0, "end")
            x_ent.insert(0, str(xv))

    def limpiar(self):
        for x_ent, y_ent in self.table_entries:
            x_ent.delete(0, "end")
            y_ent.delete(0, "end")
        for x_ent in self.requested_entries:
            x_ent.delete(0, "end")

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    app = AjusteCurvasApp()
    app.run()
