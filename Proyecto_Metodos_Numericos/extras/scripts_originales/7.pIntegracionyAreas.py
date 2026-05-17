import tkinter as tk
from tkinter import ttk, messagebox

try:
	import sympy as sp
except ImportError:
	sp = None

try:
	from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
	from matplotlib.figure import Figure
except ImportError:
	FigureCanvasTkAgg = None
	Figure = None


class IntegracionApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Integrales definidas y método trapecial")
		self.root.geometry("1920x1080")
		self.root.minsize(900, 650)

		self.bg_color = "#f5e6ea"

		self.x = sp.symbols("x") if sp else None

		self._build_ui()

	def _build_ui(self):
		self.root.configure(bg=self.bg_color)

		style = ttk.Style(self.root)
		try:
			style.theme_use("clam")
		except tk.TclError:
			pass
		style.configure("App.TFrame", background=self.bg_color)
		style.configure("App.TLabelframe", background=self.bg_color)
		style.configure("App.TLabelframe.Label", background=self.bg_color, foreground="#4b4b4b")
		style.configure("App.TLabel", background=self.bg_color, foreground="#4b4b4b")
		style.configure("App.TButton", padding=(10, 6), font=("Segoe UI", 9, "bold"))
		style.configure("App.TCheckbutton", background=self.bg_color, foreground="#4b4b4b")
		style.configure("Summary.TLabelframe", background=self.bg_color)
		style.configure("Summary.TLabelframe.Label", background=self.bg_color, foreground="#254a74")
		style.configure("SummaryValue.TLabel", background=self.bg_color, foreground="#2f2f2f", font=("Segoe UI", 10, "bold"))
		style.configure("SummaryName.TLabel", background=self.bg_color, foreground="#234e7a", font=("Segoe UI", 10, "bold"))

		main = ttk.Frame(self.root, padding=18, style="App.TFrame")
		main.pack(fill="both", expand=True)

		title = tk.Label(
			main,
			text="Método trapecial",
			font=("Segoe UI", 20, "bold"),
			bg=self.bg_color,
			fg="#8b2f1d",
		)
		title.pack(anchor="w", pady=(0, 14))

		subtitle = tk.Label(
			main,
			text="Escribe la función con x, los límites y el número de trapecios. Ejemplo: 0.1*x**2 - x*log(x)",
			font=("Segoe UI", 10),
			bg=self.bg_color,
			fg="#3f3f3f",
		)
		subtitle.pack(anchor="w", pady=(0, 18))

		panel = ttk.LabelFrame(main, text="Datos de entrada", padding=14, style="App.TLabelframe")
		panel.pack(fill="x")

		panel.columnconfigure(0, weight=5)
		panel.columnconfigure(1, weight=1)
		panel.rowconfigure(0, weight=1)

		self.expr_var = tk.StringVar(value="0.1*x**2 - x*log(x)")
		self.a_var = tk.StringVar(value="1")
		self.b_var = tk.StringVar(value="7")
		self.n_var = tk.StringVar(value="6")
		self.preview_var = tk.StringVar(value="Escribe una función para verla aquí.")
		self.aprox_var = tk.StringVar(value="-")
		self.paso_var = tk.StringVar(value="-")
		self.exacta_var = tk.StringVar(value="-")
		self.error_var = tk.StringVar(value="-")
		self.calcular_exacta_var = tk.BooleanVar(value=False)

		inputs_frame = ttk.Frame(panel, padding=(0, 0, 12, 0), style="App.TFrame")
		inputs_frame.grid(row=0, column=0, sticky="nsew")
		inputs_frame.columnconfigure(0, weight=1)
		inputs_frame.columnconfigure(1, weight=1)
		inputs_frame.columnconfigure(2, weight=1)

		func_frame = ttk.Frame(inputs_frame, style="App.TFrame")
		func_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 18))
		ttk.Label(func_frame, text="f(x):", style="SummaryName.TLabel").pack(side="left", padx=(0, 10))
		func_entry = ttk.Entry(func_frame, textvariable=self.expr_var)
		func_entry.pack(side="left", fill="x", expand=True)
		func_entry.bind("<FocusOut>", self._on_func_change)
		func_entry.bind("<Return>", self._on_func_change)

		limits_frame = ttk.Frame(inputs_frame, style="App.TFrame")
		limits_frame.grid(row=1, column=0, columnspan=3, sticky="ew")
		limits_frame.columnconfigure(0, weight=1)
		limits_frame.columnconfigure(1, weight=1)

		ttk.Label(limits_frame, text="Límite inferior a:", style="SummaryName.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 4))
		ttk.Label(limits_frame, text="Límite superior b:", style="SummaryName.TLabel").grid(row=0, column=1, sticky="w", pady=(0, 4))

		lower_frame = ttk.Frame(limits_frame, style="App.TFrame")
		lower_frame.grid(row=1, column=0, sticky="ew", padx=(0, 8))
		ttk.Entry(lower_frame, textvariable=self.a_var).pack(fill="x")

		upper_frame = ttk.Frame(limits_frame, style="App.TFrame")
		upper_frame.grid(row=1, column=1, sticky="ew")
		ttk.Entry(upper_frame, textvariable=self.b_var).pack(fill="x")

		n_frame = ttk.Frame(inputs_frame, style="App.TFrame")
		n_frame.grid(row=2, column=0, columnspan=3, sticky="w", pady=(18, 0))
		ttk.Label(n_frame, text="Número de trapecios N:", style="SummaryName.TLabel").pack(side="left", padx=(0, 10))
		ttk.Entry(n_frame, textvariable=self.n_var, width=12).pack(side="left")

		exact_frame = ttk.Frame(inputs_frame, style="App.TFrame")
		exact_frame.grid(row=3, column=0, columnspan=3, sticky="w", pady=(12, 0))
		ttk.Checkbutton(
			exact_frame,
			text="Calcular integral exacta",
			variable=self.calcular_exacta_var,
			style="App.TCheckbutton",
		).pack(side="left")

		preview_box = ttk.LabelFrame(panel, text="Vista previa", padding=10, style="App.TLabelframe")
		preview_box.grid(row=0, column=1, sticky="ne")
		preview_box.configure(width=320, height=150)
		preview_box.grid_propagate(False)
		preview_box.columnconfigure(0, weight=1)
		preview_box.rowconfigure(0, weight=1)
		self.preview_container = ttk.Frame(preview_box, style="App.TFrame")
		self.preview_container.grid(row=0, column=0, sticky="nsew")
		self.preview_container.columnconfigure(0, weight=1)
		self.preview_container.rowconfigure(0, weight=1)
		self.preview_message = tk.StringVar(value=self.preview_var.get())
		self.preview_canvas = None
		self.preview_widget = None
		self._render_preview(self.preview_var.get())

		button_row = ttk.Frame(main, style="App.TFrame")
		button_row.pack(fill="x", pady=16)

		ttk.Button(button_row, text="Calcular", command=self.calcular, style="App.TButton").pack(side="left")
		ttk.Button(button_row, text="Integral exacta", command=self.calcular_integral_exacta, style="App.TButton").pack(side="left", padx=10)
		ttk.Button(button_row, text="Limpiar", command=self.limpiar, style="App.TButton").pack(side="left", padx=10)
		ttk.Button(button_row, text="Ejemplo", command=self.ejemplo, style="App.TButton").pack(side="left", padx=10)

		result_box = ttk.LabelFrame(main, text="Resultados", padding=12, style="Summary.TLabelframe")
		result_box.pack(fill="both", expand=True)
		result_box.columnconfigure(0, weight=1)
		result_box.columnconfigure(1, weight=1)
		result_box.columnconfigure(2, weight=1)
		result_box.columnconfigure(3, weight=1)

		self._summary_cell(result_box, 0, "Aproximación trapecial:", self.aprox_var)
		self._summary_cell(result_box, 1, "Paso h:", self.paso_var)
		self._summary_cell(result_box, 2, "Integral exacta:", self.exacta_var)
		self._summary_cell(result_box, 3, "Error absoluto:", self.error_var)

		table_box = ttk.LabelFrame(main, text="Tabla de valores", padding=10, style="Summary.TLabelframe")
		table_box.pack(fill="both", expand=True, pady=(12, 0))

		self.result_text = tk.Text(
			table_box,
			wrap="word",
			height=12,
			font=("Consolas", 10),
			bg="#fffdfd",
			relief="solid",
			bd=1,
		)
		self.result_text.pack(side="left", fill="both", expand=True)

		scroll = ttk.Scrollbar(table_box, orient="vertical", command=self.result_text.yview)
		scroll.pack(side="right", fill="y")
		self.result_text.configure(yscrollcommand=scroll.set)
		self.result_text.insert("end", "Aquí aparecerán los puntos x, f(x) y la suma usada en la fórmula.\n")
		self.result_text.configure(state="disabled")

	def _summary_cell(self, parent, column, label_text, variable):
		cell = ttk.Frame(parent, style="App.TFrame", padding=(6, 6, 6, 6))
		cell.grid(row=0, column=column, sticky="nsew")
		ttk.Label(cell, text=label_text, style="SummaryName.TLabel").grid(row=0, column=0, sticky="w")
		ttk.Label(cell, textvariable=variable, style="SummaryValue.TLabel").grid(row=0, column=1, sticky="w", padx=(6, 0))

	def _update_preview(self, *args):
		self._render_preview(self.expr_var.get().strip())

	def _on_func_change(self, event=None):
		self._update_preview()

	def _render_preview(self, expression_text):
		if self.preview_widget is not None:
			self.preview_widget.get_tk_widget().destroy()
			self.preview_widget = None
			self.preview_canvas = None

		if FigureCanvasTkAgg is None or Figure is None:
			label = ttk.Label(self.preview_container, text=expression_text or self.preview_message.get(), style="App.TLabel", anchor="center", justify="center")
			label.grid(row=0, column=0, sticky="nsew")
			self.preview_widget = label
			return

		texto = expression_text or self.preview_message.get()
		try:
			if sp is not None and expression_text:
				expr = sp.sympify(
					expression_text,
					locals={
						"x": self.x,
						"sin": sp.sin,
						"cos": sp.cos,
						"tan": sp.tan,
						"csc": sp.csc,
						"sec": sp.sec,
						"cot": sp.cot,
						"asin": sp.asin,
						"acos": sp.acos,
						"atan": sp.atan,
						"acsc": sp.acsc,
						"asec": sp.asec,
						"acot": sp.acot,
						"log": sp.log,
						"ln": sp.log,
						"log10": lambda v: sp.log(v, 10),
						"exp": sp.exp,
						"sqrt": sp.sqrt,
						"pi": sp.pi,
						"e": sp.E,
						"E": sp.E,
						"abs": sp.Abs,
					},
				)
				latex_expr = sp.latex(expr)
				formula = rf"$f(x) = {latex_expr}$"
			else:
				formula = rf"$f(x) = {texto}$"
		except Exception:
			formula = rf"$f(x) = {texto}$"

		fig = Figure(figsize=(3.0, 0.82), dpi=120)
		fig.patch.set_facecolor("#fdfbf8")
		ax = fig.add_subplot(111)
		ax.set_axis_off()
		ax.text(0.5, 0.5, formula, ha="center", va="center", fontsize=12)
		fig.tight_layout(pad=0.15)

		canvas = FigureCanvasTkAgg(fig, master=self.preview_container)
		canvas.draw()
		widget = canvas.get_tk_widget()
		widget.grid(row=0, column=0, sticky="nsew")
		self.preview_canvas = canvas
		self.preview_widget = canvas

	def limpiar(self):
		self.expr_var.set("0.1*x**2 - x*log(x)")
		self.a_var.set("1")
		self.b_var.set("7")
		self.n_var.set("6")
		self.calcular_exacta_var.set(False)
		self.aprox_var.set("-")
		self.paso_var.set("-")
		self.exacta_var.set("-")
		self.error_var.set("-")
		self.result_text.configure(state="normal")
		self.result_text.delete("1.0", "end")
		self.result_text.insert("end", "Aquí aparecerán los puntos x, f(x) y la suma usada en la fórmula.\n")
		self.result_text.configure(state="disabled")
		self._update_preview()

	def ejemplo(self):
		self.expr_var.set("2*x**2 - 5*x + 7")
		self.a_var.set("0")
		self.b_var.set("3")
		self.n_var.set("6")
		self.calcular_exacta_var.set(False)
		self._update_preview()

	def ayuda(self):
		messagebox.showinfo(
			"Ayuda",
			"Usa sintaxis compatible con SymPy. Ejemplos: x**2, sin(x), cos(x), tan(x), csc(x), sec(x), cot(x), asin(x), acos(x), atan(x), log(x), exp(x), e**x o E**x.\n"
			"Para la función usa x explícitamente."
		)

	def _write_result(self, text):
		self.result_text.configure(state="normal")
		self.result_text.delete("1.0", "end")
		self.result_text.insert("end", text)
		self.result_text.configure(state="disabled")

	def _parse_inputs(self):
		if sp is None:
			raise RuntimeError("Falta instalar sympy. Instala 'sympy' para usar este programa.")

		try:
			expr = sp.sympify(
				self.expr_var.get(),
				locals={
					"x": self.x,
					"sin": sp.sin,
					"cos": sp.cos,
					"tan": sp.tan,
					"csc": sp.csc,
					"sec": sp.sec,
					"cot": sp.cot,
					"asin": sp.asin,
					"acos": sp.acos,
					"atan": sp.atan,
					"acsc": sp.acsc,
					"asec": sp.asec,
					"acot": sp.acot,
					"log": sp.log,
					"ln": sp.log,
					"log10": lambda v: sp.log(v, 10),
					"exp": sp.exp,
					"sqrt": sp.sqrt,
					"pi": sp.pi,
					"e": sp.E,
					"E": sp.E,
					"abs": sp.Abs,
				},
			)
		except Exception as exc:
			raise ValueError(f"No se pudo interpretar la función: {exc}") from exc

		try:
			a = float(sp.N(sp.sympify(self.a_var.get())))
			b = float(sp.N(sp.sympify(self.b_var.get())))
			n = int(float(sp.N(sp.sympify(self.n_var.get()))))
		except Exception as exc:
			raise ValueError(f"Límites o N inválidos: {exc}") from exc

		if n <= 0:
			raise ValueError("N debe ser un entero mayor que 0.")
		if a == b:
			raise ValueError("Los límites no pueden ser iguales.")

		if b < a:
			a, b = b, a

		return expr, a, b, n

	def calcular_integral_exacta(self):
		self.calcular_exacta_var.set(True)
		self.calcular()

	def _eval_f(self, expr, value):
		result = sp.N(expr.subs(self.x, value))
		if result.has(sp.zoo) or result.has(sp.oo) or result.has(-sp.oo):
			raise ValueError(f"La función no está definida en x = {value}.")
		return float(result)

	def calcular(self):
		try:
			expr, a, b, n = self._parse_inputs()
			requiere_exacta = bool(self.calcular_exacta_var.get())
			result_text, step_text = self._calcular_con_pasos(expr, a, b, n, requiere_exacta)
			self._update_summary(result_text)
			self._write_result(result_text)
			self._show_step_window(step_text)
		except Exception as exc:
			messagebox.showerror("Error", str(exc))

	def _update_summary(self, result_text):
		lines = result_text.splitlines()
		aprox = "-"
		paso = "-"
		exacta = "No calculada"
		error = "No calculado"
		for line in lines:
			if line.startswith("I_t = ") and "h/2" not in line:
				aprox = line.replace("I_t = ", "")
			elif line.startswith("h = "):
				paso = line.split("=", 1)[1].strip()
			elif line.startswith("Integral exacta = "):
				exacta = line.replace("Integral exacta = ", "")
			elif line.startswith("Error absoluto de la integral = "):
				error = line.replace("Error absoluto de la integral = ", "")
		self.aprox_var.set(aprox)
		self.paso_var.set(paso)
		self.exacta_var.set(exacta)
		self.error_var.set(error)

	def _calcular_con_pasos(self, expr, a, b, n, requiere_exacta=False):
		h = (b - a) / n
		xs = [a + i * h for i in range(n + 1)]
		fx = [self._eval_f(expr, value) for value in xs]

		exacta = None
		exacta_expr = None
		exacta_text = "No calculada."
		if requiere_exacta and sp is not None:
			try:
				exacta_expr = sp.integrate(expr, (self.x, a, b))
				exacta = float(sp.N(exacta_expr))
				exacta_text = f"Integral exacta = {sp.N(exacta_expr, 10)}"
			except Exception:
				exacta = None
				exacta_expr = None
		elif requiere_exacta:
			exacta_text = "No se pudo calcular simbólicamente."

		integral_trap = (h / 2.0) * (fx[0] + 2.0 * sum(fx[1:-1]) + fx[-1])
		area_trap = (h / 2.0) * (abs(fx[0]) + 2.0 * sum(abs(v) for v in fx[1:-1]) + abs(fx[-1]))

		# Newton-Cotes composite methods: Simpson 1/3, Simpson 3/8, Boole (2/45)
		def _simpson_13(fx_list, h_val, n_val):
			if n_val % 2 != 0:
				raise ValueError("N debe ser múltiplo de 2 para Simpson 1/3.")
			s_odd = sum(fx_list[i] for i in range(1, n_val, 2))
			s_even = sum(fx_list[i] for i in range(2, n_val, 2)) if n_val > 2 else 0.0
			return (h_val / 3.0) * (fx_list[0] + 4.0 * s_odd + 2.0 * s_even + fx_list[-1])

		def _simpson_38(fx_list, h_val, n_val):
			if n_val % 3 != 0:
				raise ValueError("N debe ser múltiplo de 3 para la regla 3/8.")
			s = fx_list[0] + fx_list[-1]
			for i in range(1, n_val):
				if i % 3 == 0:
					s += 2.0 * fx_list[i]
				else:
					s += 3.0 * fx_list[i]
			return (3.0 * h_val / 8.0) * s

		def _boole_245(fx_list, h_val, n_val):
			if n_val % 4 != 0:
				raise ValueError("N debe ser múltiplo de 4 para la regla 2/45 (Boole).")
			coef_sum = 0.0
			for i in range(0, n_val + 1):
				if i == 0 or i == n_val:
					c = 7
				elif i % 4 == 0:
					c = 14
				elif i % 4 == 2:
					c = 12
				else:
					c = 32
				coef_sum += c * fx_list[i]
			return (2.0 * h_val / 45.0) * coef_sum

		# calcular integrales y áreas por Newton-Cotes cuando aplique
		simpson_val = None
		simpson_area = None
		simpson38_val = None
		simpson38_area = None
		boole_val = None
		boole_area = None

		# Simpson 1/3
		try:
			simpson_val = _simpson_13(fx, h, n)
		except Exception:
			simpson_val = None

		if simpson_val is not None:
			simpson_area = _simpson_13([abs(v) for v in fx], h, n)

		# Simpson 3/8
		try:
			simpson38_val = _simpson_38(fx, h, n)
		except Exception:
			simpson38_val = None

		if simpson38_val is not None:
			simpson38_area = _simpson_38([abs(v) for v in fx], h, n)

		# Boole (2/45)
		try:
			boole_val = _boole_245(fx, h, n)
		except Exception:
			boole_val = None

		if boole_val is not None:
			boole_area = _boole_245([abs(v) for v in fx], h, n)

		if requiere_exacta and exacta is not None:
			error_integral = abs(exacta - integral_trap)
			error_area = abs(abs(exacta) - area_trap)
		else:
			error_integral = None
			error_area = None

		def _format_num(value):
			return f"{value:.6g}"

		def _rule_tables(title, base_values):
			rows = []
			trap_sum = 0.0
			simp_sum = 0.0
			r38_sum = 0.0
			r245_sum = 0.0
			trap_sum_pure = 0.0
			simp_sum_pure = 0.0
			r38_sum_pure = 0.0
			r245_sum_pure = 0.0

			for index, (value, fx_value) in enumerate(zip(xs, base_values)):
				trap_coef = 1.0 if index in (0, n) else 2.0
				simp_coef = 1.0 if index in (0, n) else (4.0 if index % 2 == 1 else 2.0)
				r38_coef = 1.0 if index in (0, n) else (2.0 if index % 3 == 0 else 3.0)
				if index in (0, n):
					r245_coef = 7.0
				elif index % 4 == 0:
					r245_coef = 14.0
				elif index % 4 == 2:
					r245_coef = 12.0
				else:
					r245_coef = 32.0

				trap_sum_pure += trap_coef * fx_value
				simp_sum_pure += simp_coef * fx_value
				r38_sum_pure += r38_coef * fx_value
				r245_sum_pure += r245_coef * fx_value

				trap_val = (h / 2.0) * trap_coef * fx_value
				simp_val = (h / 3.0) * simp_coef * fx_value
				r38_val = (3.0 * h / 8.0) * r38_coef * fx_value
				r245_val = (2.0 * h / 45.0) * r245_coef * fx_value

				trap_sum += trap_val
				simp_sum += simp_val
				r38_sum += r38_val
				r245_sum += r245_val

				rows.append(
					[
						_format_num(value),
						_format_num(fx_value),
						_format_num(trap_val),
						_format_num(simp_val) if simpson_val is not None else "N/A",
						_format_num(r38_val) if simpson38_val is not None else "N/A",
						_format_num(r245_val) if boole_val is not None else "N/A",
					]
				)

			return (
				rows,
				trap_sum,
				simp_sum if simpson_val is not None else None,
				r38_sum if simpson38_val is not None else None,
				r245_sum if boole_val is not None else None,
				trap_sum_pure,
				simp_sum_pure if simpson_val is not None else None,
				r38_sum_pure if simpson38_val is not None else None,
				r245_sum_pure if boole_val is not None else None,
			)

		def _build_table_text(title, base_values):
			rows, trap_sum, simp_sum, r38_sum, r245_sum, trap_pure, simp_pure, r38_pure, r245_pure = _rule_tables(title, base_values)
			headers = ["x", "f(x)", "Trap", "Simp", "R3/8", "R2/45"]
			widths = [10, 14, 14, 14, 14, 14]
			lines = [title]
			lines.append(" ".join(header.ljust(width) for header, width in zip(headers, widths)))
			lines.append("-" * (sum(widths) + len(widths) - 1))
			for row in rows:
				lines.append(" ".join(cell.ljust(width) for cell, width in zip(row, widths)))
			lines.append("-" * (sum(widths) + len(widths) - 1))
			lines.append(
				"Sumatoria: "
				+ f"Trap={trap_pure:.10g}"
				+ (
					f" | Simp={simp_pure:.10g}" if simp_pure is not None else " | Simp=N/A"
				)
				+ (
					f" | R3/8={r38_pure:.10g}" if r38_pure is not None else " | R3/8=N/A"
				)
				+ (
					f" | R2/45={r245_pure:.10g}" if r245_pure is not None else " | R2/45=N/A"
				)
			)
			return "\n".join(lines)

		def _build_area_table_text(title, abs_values):
			rows, trap_sum, simp_sum, r38_sum, r245_sum, trap_pure, simp_pure, r38_pure, r245_pure = _rule_tables(title, abs_values)
			headers = ["x", "|f(x)|", "Trap", "Simp", "R3/8", "R2/45"]
			widths = [10, 14, 14, 14, 14, 14]
			lines = [title]
			lines.append(" ".join(header.ljust(width) for header, width in zip(headers, widths)))
			lines.append("-" * (sum(widths) + len(widths) - 1))
			for row in rows:
				lines.append(" ".join(cell.ljust(width) for cell, width in zip(row, widths)))
			lines.append("-" * (sum(widths) + len(widths) - 1))
			lines.append(
				"Sumatoria: "
				+ f"Trap={trap_pure:.10g}"
				+ (
					f" | Simp={simp_pure:.10g}" if simp_pure is not None else " | Simp=N/A"
				)
				+ (
					f" | R3/8={r38_pure:.10g}" if r38_pure is not None else " | R3/8=N/A"
				)
				+ (
					f" | R2/45={r245_pure:.10g}" if r245_pure is not None else " | R2/45=N/A"
				)
			)
			return "\n".join(lines)

		result_lines = []
		result_lines.append("DATOS DE ENTRADA")
		result_lines.append(f"f(x) = {sp.sstr(expr)}")
		result_lines.append(f"a = {a}")
		result_lines.append(f"b = {b}")
		result_lines.append(f"N = {n}")
		result_lines.append(f"h = (b - a)/N = ({b} - {a})/{n} = {h}")
		result_lines.append("")
		result_lines.append("TABLA DE PUNTOS")
		for value, fvalue in zip(xs, fx):
			result_lines.append(f"x = {value:.6g}    f(x) = {fvalue:.6g}")
		result_lines.append("")
		result_lines.append("MÉTODO TRAPECIAL")
		result_lines.append("I_t = h/2 [f(a) + 2Σf(x_i) + f(b)]")
		result_lines.append(f"I_t = {h}/2 [{fx[0]:.6g} + 2({sum(fx[1:-1]):.6g}) + {fx[-1]:.6g}]")
		result_lines.append(f"I_t = {integral_trap:.10g}")
		result_lines.append("")
		result_lines.append("ÁREA POR TRAPECIOS")
		result_lines.append("A_t = h/2 [|f(a)| + 2Σ|f(x_i)| + |f(b)|]")
		result_lines.append(f"A_t = {area_trap:.10g}")
		result_lines.append("")
		result_lines.append(exacta_text)
		result_lines.append("")
		# Simpson 1/3
		result_lines.append("MÉTODO SIMPSON 1/3")
		result_lines.append("I_s = h/3 [f(a) + 4Σf(x_odd) + 2Σf(x_even) + f(b)]  (N múltiplo de 2)")
		if simpson_val is None:
			result_lines.append("I_s = No aplica (N no es múltiplo de 2)")
		else:
			result_lines.append(f"I_s = {simpson_val:.10g}")
			result_lines.append(f"A_s = {simpson_area:.10g}")
			if requiere_exacta and exacta is not None:
				result_lines.append(f"Error absoluto Simpson = {abs(exacta - simpson_val):.10g}")
		result_lines.append("")

		# Simpson 3/8
		result_lines.append("REGLA 3/8 (Simpson 3/8)")
		result_lines.append("I_3/8 = 3h/8 [f(a) + 3Σf(x_{i not mult of 3}) + 2Σf(x_{i mult of 3}) + f(b)]  (N múltiplo de 3)")
		if simpson38_val is None:
			result_lines.append("I_3/8 = No aplica (N no es múltiplo de 3)")
		else:
			result_lines.append(f"I_3/8 = {simpson38_val:.10g}")
			result_lines.append(f"A_3/8 = {simpson38_area:.10g}")
			if requiere_exacta and exacta is not None:
				result_lines.append(f"Error absoluto 3/8 = {abs(exacta - simpson38_val):.10g}")
		result_lines.append("")

		# Boole (2/45)
		result_lines.append("REGLA 2/45 (Boole)")
		result_lines.append("I_2/45 = 2h/45 [7f0 + 32f1 + 12f2 + 32f3 + 14f4 + ... + 7fN]  (N múltiplo de 4)")
		if boole_val is None:
			result_lines.append("I_2/45 = No aplica (N no es múltiplo de 4)")
		else:
			result_lines.append(f"I_2/45 = {boole_val:.10g}")
			result_lines.append(f"A_2/45 = {boole_area:.10g}")
			if requiere_exacta and exacta is not None:
				result_lines.append(f"Error absoluto 2/45 = {abs(exacta - boole_val):.10g}")
		result_lines.append("")
		if requiere_exacta and error_integral is not None:
			result_lines.append(f"Error absoluto de la integral = {error_integral:.10g}")
			result_lines.append(f"Error absoluto del área = {error_area:.10g}")

		step_lines = []
		step_lines.append("PROCESO PASO A PASO")
		step_lines.append("")
		step_lines.append(f"1) Se toma la función: f(x) = {sp.sstr(expr)}")
		step_lines.append(f"2) Límites: a = {a}, b = {b}, N = {n}")
		step_lines.append(f"3) Se calcula el paso: h = (b - a)/N = ({b} - {a})/{n} = {h}")
		step_lines.append("")
		step_lines.append(_build_table_text("4) Tabla para la integral", fx))
		step_lines.append("")
		step_lines.append(_build_area_table_text("5) Tabla para el área", [abs(v) for v in fx]))
		step_lines.append("")
		def _append_method_section(title, integral_formula, integral_value, area_formula, area_value, restriction=None):
			step_lines.append(title)
			step_lines.append("   Integral")
			step_lines.append(f"   Fórmula: {integral_formula}")
			if integral_value is None:
				step_lines.append(f"   Resultado: No aplica{f' ({restriction})' if restriction else ''}")
			else:
				step_lines.append(f"   Resultado: I = {integral_value:.10g}")
			step_lines.append("   Área")
			step_lines.append(f"   Fórmula: {area_formula}")
			if area_value is None:
				step_lines.append(f"   Resultado: No aplica{f' ({restriction})' if restriction else ''}")
			else:
				step_lines.append(f"   Resultado: A = {area_value:.10g}")
			step_lines.append("")

		_append_method_section(
			"6) Procedimiento de la integral definida y del área (método trapecial):",
			"I = h/2 [f(a) + 2(f(x1) + ... + f(xN-1)) + f(b)]",
			integral_trap,
			"A = h/2 [|f(a)| + 2(|f(x1)| + ... + |f(xN-1)|) + |f(b)|]",
			area_trap,
		)
		_append_method_section(
			"7) Procedimiento de la integral definida y del área (Simpson 1/3):",
			"I = h/3 [f(a) + 4Σf(x_impares) + 2Σf(x_pares) + f(b)]",
			simpson_val,
			"A = h/3 [|f(a)| + 4Σ|f(x_impares)| + 2Σ|f(x_pares)| + |f(b)|]",
			simpson_area,
			"N debe ser múltiplo de 2",
		)
		_append_method_section(
			"8) Procedimiento de la integral definida y del área (Regla 3/8):",
			"I = 3h/8 [f(a) + 3Σf(x_no múltiplos de 3) + 2Σf(x_múltiplos de 3) + f(b)]",
			simpson38_val,
			"A = 3h/8 [|f(a)| + 3Σ|f(x_no múltiplos de 3)| + 2Σ|f(x_múltiplos de 3)| + |f(b)|]",
			simpson38_area,
			"N debe ser múltiplo de 3",
		)
		_append_method_section(
			"9) Procedimiento de la integral definida y del área (Regla 2/45 o Boole):",
			"I = 2h/45 [7f0 + 32f1 + 12f2 + 32f3 + 14f4 + ... + 7fN]",
			boole_val,
			"A = 2h/45 [7|f0| + 32|f1| + 12|f2| + 32|f3| + 14|f4| + ... + 7|fN|]",
			boole_area,
			"N debe ser múltiplo de 4",
		)
		if requiere_exacta and exacta is not None and exacta_expr is not None:
			step_lines.append("")
			step_lines.append(f"10) Integral exacta simbólica: {sp.N(exacta_expr, 10)}")
			step_lines.append(f"   Error integral = |I_exacta - Trap| = {error_integral:.10g}")
			step_lines.append(f"   Error área = ||I_exacta| - Trap| = {error_area:.10g}")

		return "\n".join(result_lines), "\n".join(step_lines)

	def _show_step_window(self, text):
		win = tk.Toplevel(self.root)
		win.title("Proceso paso a paso")
		win.geometry("820x620")
		win.transient(self.root)
		win.grab_set()

		header = tk.Label(
			win,
			text="Desarrollo paso a paso",
			font=("Segoe UI", 15, "bold"),
			pady=10,
		)
		header.pack(anchor="w", padx=14)

		container = ttk.Frame(win, padding=(14, 0, 14, 14))
		container.pack(fill="both", expand=True)

		txt = tk.Text(container, wrap="word", font=("Consolas", 11), bg="#fffdfd", relief="flat")
		txt.pack(side="left", fill="both", expand=True)
		yscroll = ttk.Scrollbar(container, orient="vertical", command=txt.yview)
		yscroll.pack(side="right", fill="y")
		txt.configure(yscrollcommand=yscroll.set)
		txt.insert("end", text)
		txt.configure(state="disabled")


def main():
	root = tk.Tk()
	IntegracionApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()
