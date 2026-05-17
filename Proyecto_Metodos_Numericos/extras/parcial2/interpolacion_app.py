"""Interfaz Tkinter para interpolación lineal (tema de interpolación.md)."""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

plt = None
FigureCanvasTkAgg = None
plt_error = None
try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except (ImportError, ModuleNotFoundError, RuntimeError, ValueError) as exc:
    plt = None
    FigureCanvasTkAgg = None
    plt_error = str(exc)

try:
    from code.Parcial2.interpolacion import (
        interpolacion_lineal_y,
        interpolacion_lineal_x,
        interpolacion_lineal_piecewise_y,
        interpolacion_lineal_piecewise_x,
        interpolacion_lagrange,
        calcular_pendiente,
        validar_puntos,
    )
except ImportError:
    from interpolacion import (  # type: ignore
        interpolacion_lineal_y,
        interpolacion_lineal_x,
        interpolacion_lineal_piecewise_y,
        interpolacion_lineal_piecewise_x,
        interpolacion_lagrange,
        calcular_pendiente,
        validar_puntos,
    )


def _clear_frame(container):
    for widget in container.winfo_children():
        widget.destroy()


class InterpolacionApp:
    BG_MENU = "#F7F7F7"
    BG_CONTENT = "#FFFDF8"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Métodos Numéricos - Interpolación Lineal")
        self.root.geometry("1100x730")
        self.root.minsize(900, 620)

        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        self.points_frame = None
        self.output = None
        self.results_window = None
        self.points_table = None
        self.summary_table = None
        self.results_frame = None
        self.plot_frame = None
        self.canvas_frame = None
        self.canvas_widget = None
        self.figure = None
        self.num_points = tk.IntVar(value=8)
        self.point_entries = []
        self.target_value = tk.StringVar(value="-3")
        self.mode = tk.StringVar(value="y")  # y dado x por defecto
        self.method = tk.StringVar(value="lagrange")  # usar Lagrange por defecto para el problema 1

        self._prepare_styles()
        self._show_menu()

    def _prepare_styles(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Calc.Treeview",
            font=("Segoe UI", 10),
            rowheight=24,
            background="#F8FBFF",
            fieldbackground="#F8FBFF",
            foreground="#1F2633",
            bordercolor="#D0D8E8",
            borderwidth=1,
        )
        style.configure(
            "Calc.Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#305D8A",
            foreground="#FFFFFF",
            relief="flat",
        )
        style.map(
            "Calc.Treeview.Heading",
            background=[("active", "#2B5274"), ("!active", "#305D8A")],
        )

    def _show_menu(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_MENU)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Universidad Autónoma de Chihuahua", font=("Georgia", 22, "bold"), bg=self.BG_MENU).pack(pady=(14, 2))
        tk.Label(frm, text="Facultad de Ingeniería", font=("Georgia", 17), bg=self.BG_MENU).pack(pady=(0, 12))

        tk.Label(frm, text="Interpolación Lineal", font=("Georgia", 26, "bold"), bg=self.BG_MENU).pack(pady=(0, 8))
        tk.Label(frm, text="Tema: Interpolación de datos y formulación de una recta", font=("Georgia", 14), bg=self.BG_MENU).pack(pady=(0, 10))

        tk.Label(frm, text="Integrantes del equipo:\n- Francisco Javier Ponce Saenz  325000", font=("Georgia", 12), bg=self.BG_MENU, justify="center").pack(pady=(0, 18))

        sep = ttk.Separator(frm, orient="horizontal")
        sep.pack(fill="x", padx=40, pady=7)

        btns = tk.Frame(frm, bg=self.BG_MENU)
        btns.pack(pady=16)

        tk.Button(btns, text="1. Presentación", width=20, font=("Arial", 12), bg="#4D7092", fg="white", command=self._show_intro).grid(row=0, column=0, padx=8, pady=5)
        tk.Button(btns, text="2. Teoría y fórmulas", width=20, font=("Arial", 12), bg="#4D7092", fg="white", command=self._show_formulas).grid(row=0, column=1, padx=8, pady=5)
        tk.Button(btns, text="3. Calculadora", width=20, font=("Arial", 12), bg="#4D7092", fg="white", command=self._show_calculadora).grid(row=0, column=2, padx=8, pady=5)

        tk.Button(frm, text="Salir", width=10, font=("Arial", 11, "bold"), bg="#D9534F", fg="white", command=self.root.quit).pack(pady=10)

    def _show_intro(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_CONTENT)
        frm.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(frm, text="Introducción a la Interpolación Lineal", font=("Georgia", 24, "bold"), bg=self.BG_CONTENT).pack(pady=22)

        texto = (
            "La interpolación lineal aproxima el valor de una función en un punto intermedio usando una línea recta\n"
            "que une dos puntos conocidos (x1,y1) y (x2,y2).\n\n"
            "Utilidades típicas:\n"
            "- Distancias y crecimiento económico en intervalos cortos.\n"
            "- Estimación de costos, renta o datos de consumo con incrementos ligeros.\n"
            "- Evaluar valores intermedios en gráficas con tendencia lineal local.\n\n"
            "Fórmula principal (y en función de x):\n"
            "y = y1 + ((x-x1)(y2-y1))/(x2-x1)\n"
            "Fórmula inversa (x en función de y):\n"
            "x = x1 + ((y-y1)(x2-x1))/(y2-y1)\n"
            "Sea cual sea el método, se debe asegurar que los puntos no definen una línea vertical o horizontal degenerada."
        )

        tk.Label(frm, text=texto, font=("Georgia", 14), bg=self.BG_CONTENT, justify="left", wraplength=980).pack(padx=16, pady=12)

        tk.Button(frm, text="← Menú", font=("Arial", 12), bg="#E1EBF5", command=self._show_menu).pack(pady=14)

    def _show_formulas(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_CONTENT)
        frm.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(frm, text="Fórmulas de interpolación", font=("Georgia", 24, "bold"), bg=self.BG_CONTENT).pack(pady=22)

        texto = (
            "Datos: (x1,y1) y (x2,y2), con x1 != x2 y y1 != y2.\n\n"
            "Pendiente: m = (y2 - y1) / (x2 - x1)\n"
            "Ecuación de la recta: y - y1 = m (x - x1)\n\n"
            "Interpolación hacia Y (para x conocido):\n"
            "y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)\n\n"
            "Interpolación hacia X (para y conocido):\n"
            "x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)\n\n"
            "Nota: estos cálculos suponen que la relación es aproximadamente lineal dentro del intervalo escogido."
        )

        tk.Label(frm, text=texto, font=("Georgia", 14), bg=self.BG_CONTENT, justify="left", wraplength=980).pack(padx=16, pady=12)

        tk.Button(frm, text="← Menú", font=("Arial", 12), bg="#E1EBF5", command=self._show_menu).pack(pady=14)

    def _build_point_table(self, frm, n):
        # destruir tabla anterior de puntos
        if hasattr(self, 'points_frame') and self.points_frame is not None:
            self.points_frame.destroy()

        self.points_frame = tk.Frame(frm, bg=self.BG_CONTENT)
        self.points_frame.grid(row=4, column=0, columnspan=4, pady=(4, 12), sticky="w")

        self.point_entries.clear()

        tk.Label(self.points_frame, text="Punto", font=("Arial", 11, "bold"), bg=self.BG_CONTENT, width=6).grid(row=0, column=0, padx=4)
        tk.Label(self.points_frame, text="x", font=("Arial", 11, "bold"), bg=self.BG_CONTENT, width=12).grid(row=0, column=1, padx=4)
        tk.Label(self.points_frame, text="y", font=("Arial", 11, "bold"), bg=self.BG_CONTENT, width=12).grid(row=0, column=2, padx=4)

        default_points = [
            (0, -3),
            (1, 0),
            (2, 5),
            (3, 12),
            (4, 21),
            (5, 32),
            (6, 45),
            (7, 50),
        ]

        for i in range(n):
            if i < len(default_points):
                xv = tk.StringVar(value=str(default_points[i][0]))
                yv = tk.StringVar(value=str(default_points[i][1]))
            else:
                xv = tk.StringVar(value="")
                yv = tk.StringVar(value="")

            tk.Label(self.points_frame, text=f"P{i+1}", font=("Arial", 11), bg=self.BG_CONTENT).grid(row=i+1, column=0, padx=4, pady=2)
            ent_x = tk.Entry(self.points_frame, width=12, textvariable=xv)
            ent_x.grid(row=i+1, column=1, padx=4, pady=2)
            ent_y = tk.Entry(self.points_frame, width=12, textvariable=yv)
            ent_y.grid(row=i+1, column=2, padx=4, pady=2)
            self.point_entries.append((ent_x, ent_y))

    def _create_treeview(self, parent, columns, height=6):
        frame = tk.Frame(parent, bg=self.BG_CONTENT, bd=1, relief="solid")
        frame.pack(fill="both", expand=True, pady=6)

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            style="Calc.Treeview",
            height=height,
            selectmode="none",
        )

        for i, col in enumerate(columns):
            tree.heading(col, text=col)
            tree.column(col, width=140 if i == 0 else 120, anchor="center", stretch=True)

        tree.tag_configure("oddrow", background="#FFFFFF")
        tree.tag_configure("evenrow", background="#EAF2FA")

        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=y_scroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        return tree

    def _clear_tables(self):
        for tree in (self.points_table, self.summary_table):
            if tree is not None:
                for item in tree.get_children():
                    tree.delete(item)

    def _clear_graph(self):
        if self.canvas_widget is not None:
            try:
                self.canvas_widget.get_tk_widget().destroy()
            except Exception:
                pass
            self.canvas_widget = None
        if self.figure is not None and plt is not None:
            try:
                plt.close(self.figure)
            except Exception:
                pass
            self.figure = None

    def _render_matplotlib_figure(self, fig):
        self._clear_graph()
        self.figure = fig
        if FigureCanvasTkAgg is None or self.canvas_frame is None:
            return

        try:
            self.canvas_widget = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            self.canvas_widget.draw()
            self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)
        except Exception:
            self.canvas_widget = None

    def _populate_points_table(self, points, extra_point=None):
        self._clear_tables()
        if self.points_table is None:
            return

        all_points = list(points)
        if extra_point is not None:
            all_points.append(extra_point)

        for idx, (x, y) in enumerate(all_points, start=1):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.points_table.insert("", "end", values=(f"P{idx}", f"{x:.6f}", f"{y:.6f}"), tags=(tag,))

    def _populate_summary_table(self, rows):
        if self.summary_table is None:
            return

        for item in self.summary_table.get_children():
            self.summary_table.delete(item)

        for idx, (label, value) in enumerate(rows, start=1):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.summary_table.insert("", "end", values=(label, value), tags=(tag,))

    def _show_results_window(self):
        if self.results_window is not None and self.results_window.winfo_exists():
            self.results_window.lift()
            return

        self.results_window = tk.Toplevel(self.root)
        self.results_window.title("Resultados de interpolación")
        self.results_window.geometry("1120x720")
        self.results_window.minsize(980, 620)
        self.results_window.configure(bg=self.BG_CONTENT)
        self.results_window.transient(self.root)
        self.results_window.protocol("WM_DELETE_WINDOW", self._close_results_window)

        container = tk.Frame(self.results_window, bg=self.BG_CONTENT)
        container.pack(fill="both", expand=True, padx=12, pady=10)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        left_panel = tk.Frame(container, bg=self.BG_CONTENT)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=6)
        right_panel = tk.Frame(container, bg=self.BG_CONTENT)
        right_panel.grid(row=0, column=1, sticky="nsew", pady=6)
        left_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=1)

        tk.Label(left_panel, text="Tabla de puntos", font=("Georgia", 14, "bold"), bg=self.BG_CONTENT, fg="#1F3A5A").pack(anchor="w", padx=6, pady=(4, 0))
        self.points_table = self._create_treeview(left_panel, ["Punto", "x", "y"], height=6)

        tk.Label(left_panel, text="Resumen de resultados", font=("Georgia", 14, "bold"), bg=self.BG_CONTENT, fg="#1F3A5A").pack(anchor="w", padx=6, pady=(8, 0))
        self.summary_table = self._create_treeview(left_panel, ["Concepto", "Valor"], height=6)

        right_panel.grid_rowconfigure(1, weight=0)
        self.plot_frame = tk.Frame(right_panel, bg="#FFFFFF", bd=1, relief="solid")
        self.plot_frame.pack(fill="both", expand=True, pady=6)
        tk.Label(self.plot_frame, text="Vista gráfica", font=("Georgia", 14, "bold"), bg="#FFFFFF", fg="#1F3A5A").pack(anchor="w", padx=8, pady=8)
        self.canvas_frame = tk.Frame(self.plot_frame, bg="#FFFFFF")
        self.canvas_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        bottom_panel = tk.Frame(self.results_window, bg=self.BG_CONTENT)
        bottom_panel.pack(fill="both", expand=False, padx=12, pady=(0, 10))
        tk.Label(bottom_panel, text="Salida", font=("Georgia", 14, "bold"), bg=self.BG_CONTENT, fg="#1F3A5A").pack(anchor="w", padx=6, pady=(4, 0))
        self.output = scrolledtext.ScrolledText(bottom_panel, width=135, height=8, font=("Consolas", 11))
        self.output.pack(fill="both", expand=True, padx=6, pady=4)
        self._on_limpiar()

    def _close_results_window(self):
        if self.results_window is not None and self.results_window.winfo_exists():
            self.results_window.destroy()
        self.results_window = None
        self.output = None

    def _show_lagrange_calculations_window(self):
        if not self.lagrange_steps:
            messagebox.showinfo("Cálculos Lagrange", "No hay cálculos de Lagrange disponibles. Primero calcule o grafique un caso de Lagrange.")
            return

        win = tk.Toplevel(self.root)
        win.title("Cálculos de Lagrange")
        win.geometry("900x640")
        win.minsize(760, 520)
        win.configure(bg=self.BG_CONTENT)

        tk.Label(win, text="Cálculos de Lagrange", font=("Georgia", 18, "bold"), bg=self.BG_CONTENT, fg="#1F3A5A").pack(anchor="w", padx=12, pady=(12, 6))
        txt = scrolledtext.ScrolledText(win, width=110, height=32, font=("Consolas", 11))
        txt.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        txt.insert(tk.END, self.lagrange_steps)
        txt.configure(state="disabled")

    def _get_points(self):
        points = []
        unknown = None

        for idx, (ex, ey) in enumerate(self.point_entries, start=1):
            x_raw = ex.get().strip()
            y_raw = ey.get().strip()

            if x_raw == "" and y_raw == "":
                continue

            if x_raw == "":
                if unknown is not None:
                    raise ValueError("Solo se permite un punto incompleto para calcular el valor faltante.")
                try:
                    y = float(y_raw)
                except ValueError:
                    raise ValueError(f"Fila {idx}: y debe ser un número válido")
                unknown = {"missing": "x", "known": y, "row": idx}
                continue

            if y_raw == "":
                if unknown is not None:
                    raise ValueError("Solo se permite un punto incompleto para calcular el valor faltante.")
                try:
                    x = float(x_raw)
                except ValueError:
                    raise ValueError(f"Fila {idx}: x debe ser un número válido")
                unknown = {"missing": "y", "known": x, "row": idx}
                continue

            try:
                x = float(x_raw)
                y = float(y_raw)
            except ValueError:
                raise ValueError(f"Fila {idx}: x e y deben ser números válidos")

            points.append((x, y))

        if unknown is not None and len(points) != 2:
            raise ValueError("Para calcular el valor faltante se requieren exactamente dos puntos completos")
        if unknown is None and len(points) < 2:
            raise ValueError("Se requieren al menos dos puntos completos para interpolar")

        return points, unknown

    def _compute_missing_point(self, points, unknown):
        if unknown is None:
            raise ValueError("No hay valor faltante para calcular.")

        (x1, y1), (x2, y2) = points
        validar_puntos(x1, y1, x2, y2)

        if unknown["missing"] == "y":
            x = unknown["known"]
            y = interpolacion_lineal_y(x1, y1, x2, y2, x)
            return x, y

        y = unknown["known"]
        x = interpolacion_lineal_x(x1, y1, x2, y2, y)
        return x, y

    def _show_calculadora(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_CONTENT)
        frm.pack(fill="both", expand=True, padx=12, pady=10)
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_columnconfigure(1, weight=1)
        frm.grid_columnconfigure(2, weight=1)
        frm.grid_columnconfigure(3, weight=1)

        tk.Label(frm, text="Calculadora de interpolación lineal", font=("Georgia", 24, "bold"), bg=self.BG_CONTENT).grid(row=0, column=0, columnspan=4, pady=12)

        tk.Label(frm, text="Cantidad de puntos:", font=("Arial", 12), bg=self.BG_CONTENT).grid(row=1, column=0, sticky="e", padx=4, pady=4)
        spin = tk.Spinbox(frm, from_=2, to=10, width=6, textvariable=self.num_points, command=lambda: self._build_point_table(frm, self.num_points.get()))
        spin.grid(row=1, column=1, sticky="w", padx=4, pady=4)

        tk.Button(frm, text="Rebuild tabla", font=("Arial", 11), bg="#6FA6D0", command=lambda: self._build_point_table(frm, self.num_points.get())).grid(row=1, column=2, sticky="w", padx=4, pady=4)

        tk.Label(frm, text="Valor objetivo:", font=("Arial", 12), bg=self.BG_CONTENT).grid(row=2, column=0, sticky="e", padx=4, pady=8)
        tk.Entry(frm, width=12, textvariable=self.target_value).grid(row=2, column=1, sticky="w", padx=4, pady=8)

        tipo_frame = tk.Frame(frm, bg=self.BG_CONTENT)
        tipo_frame.grid(row=2, column=2, columnspan=2, sticky="w", padx=4)
        tk.Radiobutton(tipo_frame, text="Calcular y (con x)", variable=self.mode, value="y", bg=self.BG_CONTENT, font=("Arial", 11)).pack(side="left", padx=8)
        tk.Radiobutton(tipo_frame, text="Calcular x (con y)", variable=self.mode, value="x", bg=self.BG_CONTENT, font=("Arial", 11)).pack(side="left", padx=8)

        method_frame = tk.Frame(frm, bg=self.BG_CONTENT)
        method_frame.grid(row=3, column=2, columnspan=2, sticky="w", padx=4, pady=(0,8))
        tk.Label(method_frame, text="Método:", font=("Arial", 11, "bold"), bg=self.BG_CONTENT).pack(side="left")
        tk.Radiobutton(method_frame, text="Lineal", variable=self.method, value="lineal", bg=self.BG_CONTENT, font=("Arial", 11)).pack(side="left", padx=8)
        tk.Radiobutton(method_frame, text="Lagrange", variable=self.method, value="lagrange", bg=self.BG_CONTENT, font=("Arial", 11)).pack(side="left", padx=8)

        self._build_point_table(frm, self.num_points.get())

        acciones = tk.Frame(frm, bg=self.BG_CONTENT)
        acciones.grid(row=4, column=0, columnspan=4, pady=6)

        tk.Button(acciones, text="Calcular", font=("Arial", 12, "bold"), bg="#5CB85C", fg="white", command=self._on_calcular).pack(side="left", padx=8)
        tk.Button(acciones, text="Graficar", font=("Arial", 12, "bold"), bg="#4096ee", fg="white", command=self._on_graficar).pack(side="left", padx=8)
        tk.Button(acciones, text="Ver cálculos Lagrange", font=("Arial", 12, "bold"), bg="#6F42C1", fg="white", command=self._show_lagrange_calculations_window).pack(side="left", padx=8)
        tk.Button(acciones, text="Limpiar", font=("Arial", 12), bg="#F0AD4E", command=self._on_limpiar).pack(side="left", padx=8)

        self._on_limpiar()

        tk.Button(frm, text="← Menú", font=("Arial", 12), bg="#E1EBF5", command=self._show_menu).grid(row=7, column=0, columnspan=4, pady=10)

    def _has_matplotlib(self):
        if plt is not None:
            return True
        msg = "[INFO] matplotlib no está disponible; no se puede graficar."
        if plt_error:
            msg += f"  Error de carga: {plt_error}."
        msg += f" Intérprete: {sys.executable}"
        self.output.insert(tk.END, msg + "\n")
        self.output.insert(tk.END, "sys.path: " + str(sys.path) + "\n")
        return False

    def _lineal_steps(self, points, target, mode):
        points_sorted = sorted(points, key=lambda p: p[0])
        if len(points) == 2:
            x1, y1 = points_sorted[0]
            x2, y2 = points_sorted[1]
            if mode == "y":
                slope = calcular_pendiente(x1, y1, x2, y2)
                y = interpolacion_lineal_y(x1, y1, x2, y2, target)
                steps = [
                    f"Puntos: ({x1}, {y1}), ({x2}, {y2})",
                    f"Pendiente m = (y2 - y1)/(x2 - x1) = ({y2} - {y1})/({x2} - {x1}) = {slope:.6f}",
                    "Fórmula: y = y1 + (x - x1)*m",
                    f"Sustituyendo x={target}: y = {y1} + ({target} - {x1})*{slope:.6f} = {y:.6f}",
                ]
                return y, "\n".join(steps)
            else:
                slope_inv = (x2 - x1) / (y2 - y1)
                x = interpolacion_lineal_x(x1, y1, x2, y2, target)
                steps = [
                    f"Puntos: ({x1}, {y1}), ({x2}, {y2})",
                    f"Pendiente inversa m' = (x2 - x1)/(y2 - y1) = ({x2} - {x1})/({y2} - {y1}) = {slope_inv:.6f}",
                    "Fórmula: x = x1 + (y - y1)*m'",
                    f"Sustituyendo y={target}: x = {x1} + ({target} - {y1})*{slope_inv:.6f} = {x:.6f}",
                ]
                return x, "\n".join(steps)

        # piecewise
        xs = [p[0] for p in points_sorted]
        if target <= xs[0]:
            i0, i1 = 0, 1
        elif target >= xs[-1]:
            i0, i1 = len(xs) - 2, len(xs) - 1
        else:
            i0 = max(i for i in range(len(xs) - 1) if xs[i] <= target)
            i1 = i0 + 1

        x1, y1 = points_sorted[i0]
        x2, y2 = points_sorted[i1]
        slope = calcular_pendiente(x1, y1, x2, y2)

        if mode == "y":
            y = interpolacion_lineal_y(x1, y1, x2, y2, target)
            steps = [
                f"Puntos usados: ({x1}, {y1}), ({x2}, {y2})",
                f"pendiente m = (y2 - y1)/(x2 - x1) = ({y2} - {y1})/({x2} - {x1}) = {slope:.6f}",
                "Fórmula en el segmento: y = y1 + (x - x1)*m",
                f"Sustituyendo x={target}: y = {y1} + ({target} - {x1})*{slope:.6f} = {y:.6f}",
            ]
            return y, "\n".join(steps)

        else:
            x = interpolacion_lineal_x(x1, y1, x2, y2, target)
            slope_inv = (x2 - x1) / (y2 - y1)
            steps = [
                f"Puntos usados: ({x1}, {y1}), ({x2}, {y2})",
                f"pendiente inversa m' = (x2 - x1)/(y2 - y1) = ({x2} - {x1})/({y2} - {y1}) = {slope_inv:.6f}",
                "Fórmula en el segmento: x = x1 + (y - y1)*m'",
                f"Sustituyendo y={target}: x = {x1} + ({target} - {y1})*{slope_inv:.6f} = {x:.6f}",
            ]
            return x, "\n".join(steps)

    def _plot_interpolacion(self, x1, y1, x2, y2, x_obj, y_obj):
        if not self._has_matplotlib():
            self._plot_canvas([x1, x2], [y1, y2], x_obj, y_obj, "Interpolación lineal")
            return

        pendiente = calcular_pendiente(x1, y1, x2, y2)
        x_min, x_max = min(x1, x2), max(x1, x2)
        x_span = x_max - x_min
        x_display = [x_min - 0.1 * x_span, x_max + 0.1 * x_span]

        y_display = [y1 + pendiente * (x - x1) for x in x_display]

        try:
            plt.figure("Interpolación Lineal")
            plt.clf()
            plt.plot([x1, x2], [y1, y2], "bo", label="Puntos conocidos")
            plt.plot(x_display, y_display, "-r", label="Recta interpolada")
            plt.plot(x_obj, y_obj, "gs", markersize=10, label="Punto interpolado")
            plt.xlabel("x")
            plt.ylabel("y")
            plt.title("Interpolación lineal: punto y línea")
            plt.legend()
            plt.grid(True)
            plt.axhline(0, color="black", linewidth=0.5)
            plt.axvline(0, color="black", linewidth=0.5)
            plt.show()
        except (ValueError, TypeError, RuntimeError, OverflowError, tk.TclError) as exc:
            self.output.insert(tk.END, f"[WARN] Matplotlib backend falló al graficar: {exc}. Usando canvas alternativo.\n")
            self._plot_canvas([x1, x2], [y1, y2], x_obj, y_obj, "Interpolación lineal (Canvas)")

    def _plot_piecewise(self, points, x_obj, y_obj, ops_text=None):
        if not self._has_matplotlib():
            px = [p[0] for p in points]
            py = [p[1] for p in points]
            self._plot_canvas(px, py, x_obj, y_obj, "Interpolación/Extrapolación lineal", ops_text=ops_text)
            return

        points_sorted = sorted(points, key=lambda p: p[0])
        xs = [p[0] for p in points_sorted]
        ys = [p[1] for p in points_sorted]

        try:
            fig = plt.figure("Interpolación Lineal")
            fig.clf()
            gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.4)

            ax = fig.add_subplot(gs[0])
            ax.plot(xs, ys, "-o", color="#1f77b4", label="Curva interpolada")
            ax.scatter(xs, ys, color="blue", s=45)
            ax.scatter([x_obj], [y_obj], color="red", marker="*", s=150, label="Punto interpolado")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_title("Interpolación/Extrapolación lineal por segmentos")
            ax.grid(True)
            ax.legend()
            ax.axhline(0, color="black", linewidth=0.5)
            ax.axvline(0, color="black", linewidth=0.5)

            ax2 = fig.add_subplot(gs[1])
            ax2.axis("off")
            text = ops_text or "Operaciones no disponibles"
            ax2.text(0.01, 0.99, text, fontsize=8, family="monospace", va="top")

            if FigureCanvasTkAgg is not None and self.canvas_frame is not None:
                self._render_matplotlib_figure(fig)
            else:
                plt.show()
        except (ValueError, TypeError, RuntimeError, OverflowError, tk.TclError) as exc:
            self.output.insert(tk.END, f"[WARN] Matplotlib backend falló al graficar: {exc}. Usando canvas alternativo.\n")
            self._plot_canvas(xs, ys, x_obj, y_obj, "Interpolación/Extrapolación lineal (Canvas)", ops_text=ops_text)

    def _plot_canvas(self, xs, ys, x_obj, y_obj, title, ops_text=None):
        # Fallback a Tkinter Canvas si matplotlib no está disponible.
        # Normalizamos espacio de datos a pixeles para dibujar en su propia ventana.
        all_x = list(xs)
        all_y = list(ys)
        if x_obj is not None and y_obj is not None:
            all_x.append(x_obj)
            all_y.append(y_obj)

        x_min, x_max = min(all_x), max(all_x)
        y_min, y_max = min(all_y), max(all_y)
        x_span = (x_max - x_min) or 1.0
        y_span = (y_max - y_min) or 1.0

        x_min -= x_span * 0.1
        x_max += x_span * 0.1
        y_min -= y_span * 0.1
        y_max += y_span * 0.1

        width, height = 760, 520
        margin = 50

        def to_canvas(x, y):
            cx = margin + (x - x_min) / (x_max - x_min) * (width - 2 * margin)
            cy = margin + (y_max - y) / (y_max - y_min) * (height - 2 * margin)
            return cx, cy

        win = tk.Toplevel(self.root)
        win.title(title + " (Canvas)")
        canvas = tk.Canvas(win, width=width, height=height, bg="white")
        canvas.pack(fill="both", expand=True)

        # Ejes
        axis_y = to_canvas(x_min, 0)[1]
        axis_x = to_canvas(0, y_min)[0]
        if y_min <= 0 <= y_max:
            canvas.create_line(margin, axis_y, width - margin, axis_y, fill="gray", width=1)
        if x_min <= 0 <= x_max:
            canvas.create_line(axis_x, margin, axis_x, height - margin, fill="gray", width=1)

        # Línea intermedia
        coords = []
        for x, y in zip(xs, ys):
            coords.append(to_canvas(x, y))
        for i in range(len(coords) - 1):
            canvas.create_line(coords[i][0], coords[i][1], coords[i+1][0], coords[i+1][1], fill="#1f77b4", width=2)

        # Puntos conocidos
        for x, y in zip(xs, ys):
            cx, cy = to_canvas(x, y)
            r = 4
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="blue", outline="black")

        # Punto interpolado
        if x_obj is not None and y_obj is not None:
            cx, cy = to_canvas(x_obj, y_obj)
            r = 6
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill="red", outline="black")

        canvas.create_text(70, 20, text=title, anchor="w", font=("Arial", 12, "bold"))

        if ops_text:
            ops_frame = tk.Frame(win, bg="white")
            ops_frame.pack(fill="both", expand=True, padx=8, pady=8)
            ops_textbox = scrolledtext.ScrolledText(ops_frame, width=95, height=10, font=("Consolas", 10))
            ops_textbox.pack(fill="both", expand=True)
            ops_textbox.insert(tk.END, ops_text)
            ops_textbox.configure(state="disabled")

    def _show_lagrange_steps(self, steps_text):
        win = tk.Toplevel(self.root)
        win.title("Operaciones Lagrange")
        txt = scrolledtext.ScrolledText(win, width=100, height=20, font=("Consolas", 11))
        txt.pack(fill="both", expand=True, padx=8, pady=8)
        txt.insert(tk.END, steps_text)
        txt.configure(state="disabled")

    def _plot_lagrange(self, points, x_obj, y_obj, ops_text):
        points_sorted = sorted(points, key=lambda p: p[0])
        xs = [p[0] for p in points_sorted]
        ys = [p[1] for p in points_sorted]

        # Mostrar operaciones en ventana alternativa siempre
        self._show_lagrange_steps(ops_text)

        if not self._has_matplotlib():
            self._plot_canvas(xs, ys, x_obj, y_obj, "Interpolación Lagrange", ops_text=ops_text)
            return

        try:
            x_min, x_max = min(xs), max(xs)
            span = (x_max - x_min) or 1.0
            x_plot = [x_min - 0.1*span + i*(1.2*span)/200 for i in range(201)]
            y_plot = [interpolacion_lagrange(points, xv) for xv in x_plot]

            fig = plt.figure("Interpolación Lagrange")
            fig.clf()
            gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.4)

            ax = fig.add_subplot(gs[0])
            ax.plot(x_plot, y_plot, "-r", label="Polinomio de Lagrange")
            ax.scatter(xs, ys, color="blue", s=45, label="Puntos conocidos")
            ax.scatter([x_obj], [y_obj], color="red", marker="*", s=150, label="Punto interpolado")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.set_title("Interpolación de Lagrange")
            ax.grid(True)
            ax.legend()
            ax.axhline(0, color="black", linewidth=0.5)
            ax.axvline(0, color="black", linewidth=0.5)

            ax2 = fig.add_subplot(gs[1])
            ax2.axis("off")
            ax2.text(0.01, 0.99, ops_text, fontsize=8, family="monospace", va="top", wrap=True)

            if FigureCanvasTkAgg is not None and self.canvas_frame is not None:
                self._render_matplotlib_figure(fig)
            else:
                plt.show()
        except (ValueError, TypeError, RuntimeError, OverflowError, tk.TclError) as exc:
            self.output.insert(tk.END, f"[WARN] Matplotlib backend falló al graficar Lagrange: {exc}. Usando canvas alternativo.\n")
            self._plot_canvas(xs, ys, x_obj, y_obj, "Interpolación Lagrange", ops_text=ops_text)

    def _on_calcular(self):
        try:
            points, unknown = self._get_points()
            self._show_results_window()
            self._clear_graph()
            self._clear_tables()

            if unknown is not None:
                if self.method.get() != "lineal":
                    raise ValueError("El cálculo de un valor faltante solo está disponible para el método lineal.")

                x_calculado, y_calculado = self._compute_missing_point(points, unknown)
                self._populate_points_table(points, (x_calculado, y_calculado))
                self._populate_summary_table([
                    ("Punto calculado", f"x={x_calculado:.6f}, y={y_calculado:.6f}"),
                    ("Fila incompleta", unknown['row']),
                    ("Método", "Lineal"),
                    ("Fórmula", "x = x1 + (y - y1)*(x2 - x1)/(y2 - y1)" if unknown['missing'] == 'x' else "y = y1 + (x - x1)*(y2 - y1)/(x2 - x1)"),
                ])
                self.output.insert(tk.END, f"Punto calculado (fila {unknown['row']}): x={x_calculado:.6f}, y={y_calculado:.6f}\n")
                self.output.insert(tk.END, f"Usando puntos: {points[0]} y {points[1]}\n")
                self.output.insert(tk.END, "-" * 90 + "\n")
                self.output.see(tk.END)
                return

            target = self.target_value.get().strip()
            if target == "":
                raise ValueError("Ingrese un valor objetivo para interpolar.")
            target = float(target)

            x1, y1 = points[0]
            x2, y2 = points[1]
            validar_puntos(x1, y1, x2, y2)
            pendiente = calcular_pendiente(x1, y1, x2, y2)
            self._populate_points_table(points)

            if self.method.get() == "lineal":
                self.lagrange_steps = None
                if self.mode.get() == "y":
                    result = interpolacion_lineal_y(x1, y1, x2, y2, target) if len(points) == 2 else interpolacion_lineal_piecewise_y(points, target)
                    formula = "y = y1 + (x - x1)*(y2 - y1)/(x2 - x1)"
                    self._populate_summary_table([
                        ("Método", "Lineal"),
                        ("Objetivo", f"x = {target}"),
                        ("Resultado", f"y = {result:.6f}"),
                        ("Pendiente", f"{pendiente:.6f}"),
                        ("Fórmula", formula),
                    ])
                    self.output.insert(tk.END, f"Interpolando Y para x={target}: y={result:.6f}\n")
                else:
                    result = interpolacion_lineal_x(x1, y1, x2, y2, target) if len(points) == 2 else interpolacion_lineal_piecewise_x(points, target)
                    formula = "x = x1 + (y - y1)*(x2 - x1)/(y2 - y1)"
                    self._populate_summary_table([
                        ("Método", "Lineal"),
                        ("Objetivo", f"y = {target}"),
                        ("Resultado", f"x = {result:.6f}"),
                        ("Pendiente", f"{pendiente:.6f}"),
                        ("Fórmula", formula),
                    ])
                    self.output.insert(tk.END, f"Interpolando X para y={target}: x={result:.6f}\n")
                self.output.insert(tk.END, f"Fórmula usada: {formula}\n")
                self.output.insert(tk.END, f"Conjunto de puntos: {points}\n")
            else:
                result, steps = interpolacion_lagrange(points, target, verbose=True)
                self.lagrange_steps = steps
                self._populate_summary_table([
                    ("Método", "Lagrange"),
                    ("Objetivo", f"x = {target}"),
                    ("Resultado", f"y = {result:.6f}"),
                    ("Puntos", ", ".join([f"({x},{y})" for x, y in points])),
                ])
                self.output.insert(tk.END, f"Interpolación de Lagrange para x={target}: y={result:.6f}\n")
                self.output.insert(tk.END, "Operaciones de Lagrange:\n")
                self.output.insert(tk.END, steps + "\n")
                self.output.insert(tk.END, f"Resultado: y={result:.6f}\n")
            self.output.insert(tk.END, "-" * 90 + "\n")
            self.output.see(tk.END)

        except ValueError as error:
            messagebox.showerror("Error de entrada", str(error))
        except (TypeError, RuntimeError, OverflowError) as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

    def _on_graficar(self):
        try:
            points, unknown = self._get_points()
            self._show_results_window()
            self._clear_graph()
            self._clear_tables()

            if unknown is not None:
                if self.method.get() != "lineal":
                    raise ValueError("El gráfico de un valor faltante solo está disponible para el método lineal.")

                x_calculado, y_calculado = self._compute_missing_point(points, unknown)
                self._populate_points_table(points, (x_calculado, y_calculado))
                self._populate_summary_table([
                    ("Punto calculado", f"x={x_calculado:.6f}, y={y_calculado:.6f}"),
                    ("Fila incompleta", unknown['row']),
                    ("Método", "Lineal"),
                    ("Acción", "Gráfica con punto completado"),
                ])
                self._plot_piecewise(points + [(x_calculado, y_calculado)], x_calculado, y_calculado,
                                     ops_text=f"Punto calculado en fila {unknown['row']}: ({x_calculado:.6f}, {y_calculado:.6f})")
                self.output.insert(tk.END, f"Graficando punto calculado: ({x_calculado:.6f}, {y_calculado:.6f})\n")
                self.output.insert(tk.END, "[OK] Gráfica generada.\n")
                self.output.see(tk.END)
                return

            target = self.target_value.get().strip()
            if target == "":
                raise ValueError("Ingrese un valor objetivo para graficar.")
            target = float(target)

            if len(points) < 2:
                raise ValueError("Se requieren al menos dos puntos para graficar")

            self._populate_points_table(points)

            if self.method.get() == "lineal":
                self.lagrange_steps = None
                if self.mode.get() == "y":
                    y = interpolacion_lineal_piecewise_y(points, target)
                    _, steps = self._lineal_steps(points, target, "y")
                    self._plot_piecewise(points, target, y, ops_text=steps)
                    self._populate_summary_table([
                        ("Método", "Lineal"),
                        ("Objetivo", f"x = {target}"),
                        ("Resultado", f"y = {y:.6f}"),
                        ("Tipo", "Interpolación por segmentos"),
                    ])
                    self.output.insert(tk.END, f"Graficando interpolación de y para x={target}: y={y:.6f}\n")
                else:
                    x = interpolacion_lineal_piecewise_x(points, target)
                    _, steps = self._lineal_steps(points, target, "x")
                    self._plot_piecewise(points, x, target, ops_text=steps)
                    self._populate_summary_table([
                        ("Método", "Lineal"),
                        ("Objetivo", f"y = {target}"),
                        ("Resultado", f"x = {x:.6f}"),
                        ("Tipo", "Interpolación por segmentos"),
                    ])
                    self.output.insert(tk.END, f"Graficando interpolación de x para y={target}: x={x:.6f}\n")
            else:
                y, steps = interpolacion_lagrange(points, target, verbose=True)
                self.lagrange_steps = steps
                self._populate_summary_table([
                    ("Método", "Lagrange"),
                    ("Objetivo", f"x = {target}"),
                    ("Resultado", f"y = {y:.6f}"),
                    ("Operaciones", "Ver ventana de pasos"),
                ])
                self._plot_lagrange(points, target, y, steps)
                self.output.insert(tk.END, f"Graficando interpolación de Lagrange para x={target}: y={y:.6f}\n")

            self.output.insert(tk.END, "[OK] Gráfica generada.\n")
            self.output.see(tk.END)

        except ValueError as error:
            messagebox.showerror("Error de entrada", str(error))
        except (TypeError, RuntimeError, OverflowError) as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

    def _on_limpiar(self):
        self._clear_graph()
        self._clear_tables()
        if self.output is not None:
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, "Resultado:\n")
            self.output.insert(tk.END, "Ingrese puntos válidos y seleccione el modo de interpolación.\n")


if __name__ == "__main__": 
    app = InterpolacionApp()
    app.root.mainloop()
