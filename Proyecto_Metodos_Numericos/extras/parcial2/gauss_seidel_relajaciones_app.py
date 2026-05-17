"""
Interfaz GUI para Gauss-Seidel y Relajaciones en estilo prueba de examen.
Este archivo es el programa principal y usa `gauss_seidel_relajaciones.py` como biblioteca.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from gauss_seidel_relajaciones import (
    formatear_hoja_gauss_seidel,
    formatear_hoja_relajaciones,
    gauss_seidel,
    gauss_seidel_hoja,
    obtener_despejes_gauss_seidel,
    relajaciones_hoja,
    sor,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)




def _clear_frame(container):
    for widget in container.winfo_children():
        widget.destroy()


def _parse_matrix(entries):
    n = len(entries)
    if n == 0:
        raise ValueError("No hay dimensiones de matriz configuradas")
    A = [[0.0] * n for _ in range(n)]
    for i in range(n):
        if len(entries[i]) != n:
            raise ValueError(f"Fila {i+1} de A no tiene longitud {n}")
        for j in range(n):
            raw = entries[i][j].get().strip()
            if raw == "":
                raise ValueError(f"Coeficiente A[{i+1},{j+1}] vacío")
            A[i][j] = float(raw)
    return A


def _parse_vector(entries):
    b = []
    for i, e in enumerate(entries):
        raw = e.get().strip()
        if raw == "":
            raise ValueError(f"b[{i+1}] vacío")
        b.append(float(raw))
    return b


def _parse_initial(entries):
    x0 = []
    for e in entries:
        raw = e.get().strip()
        x0.append(float(raw) if raw != "" else 0.0)
    return x0


def _fmt3(value):
    return f"{float(value):.3f}"


def _default_variable_names(n):
    base = ["x", "y", "z", "t", "u", "v", "w"]
    if n <= len(base):
        return base[:n]
    return base + [f"x{i}" for i in range(len(base) + 1, n + 1)]


def _roman(num):
    symbols = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
    if 1 <= num <= len(symbols):
        return symbols[num - 1]
    return str(num)


def _prepare_table_styles(master):
    style = ttk.Style(master)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Calc.TNotebook", background="#E7EEF6", borderwidth=0)
    style.configure(
        "Calc.TNotebook.Tab",
        font=("Segoe UI", 10, "bold"),
        padding=(12, 8),
    )
    style.map(
        "Calc.TNotebook.Tab",
        background=[("selected", "#FFFFFF"), ("!selected", "#D1E0EB")],
        foreground=[("selected", "#1F3A5A"), ("!selected", "#1F3A5A")],
    )

    style.configure(
        "Calc.Treeview",
        font=("Segoe UI", 10),
        rowheight=28,
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


def _build_table(parent, columns, rows, height=10):
    outer = tk.Frame(parent, bg="#F4F8FD", bd=1, relief="solid")
    outer.pack(fill="both", expand=True, padx=12, pady=10)

    table_wrap = tk.Frame(outer, bg="#F4F8FD")
    table_wrap.pack(fill="both", expand=True)
    table_wrap.grid_rowconfigure(0, weight=1)
    table_wrap.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(
        table_wrap,
        columns=columns,
        show="headings",
        style="Calc.Treeview",
        height=height,
        selectmode="browse",
    )

    for i, col in enumerate(columns):
        width = 160 if i == 0 else 110
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor="center", stretch=True)

    tree.tag_configure("oddrow", background="#FFFFFF")
    tree.tag_configure("evenrow", background="#EAF2FA")
    tree.tag_configure("separator", background="#D3DFED")

    for idx, row in enumerate(rows):
        tag = "separator" if any(str(cell).startswith("----") for cell in row) else ("evenrow" if idx % 2 else "oddrow")
        tree.insert("", "end", values=row, tags=(tag,))

    y_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=tree.yview)
    x_scroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

    tree.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")


def _show_report_window(parent, method_name, report):
    _prepare_table_styles(parent)

    win = tk.Toplevel(parent)
    win.transient(parent)
    win.lift()
    win.attributes("-topmost", True)
    win.after(100, lambda: win.attributes("-topmost", False))
    title = "Gauss-Seidel" if method_name == "GS" else "Relajaciones"
    win.title(f"Tablas de calculo - {title}")
    win.geometry("1220x760")
    win.minsize(980, 620)
    win.configure(bg="#E7EEF6")

    n = report.get("n", 0)

    header = tk.Frame(win, bg="#1F3A5A", padx=16, pady=12)
    header.pack(fill="x")
    tk.Label(
        header,
        text=f"Tablas de calculo ({title})",
        font=("Georgia", 18, "bold"),
        bg="#1F3A5A",
        fg="#FFFFFF",
    ).pack(side="left")

    state_text = "Convergente" if report.get("converged") else "Sin convergencia"
    tk.Label(
        header,
        text=f"Estado: {state_text}",
        font=("Segoe UI", 10, "bold"),
        bg="#1F3A5A",
        fg="#D9E7F6",
    ).pack(side="right")

    summary_frame = tk.Frame(win, bg="#FFFFFF", bd=1, relief="solid")
    summary_frame.pack(fill="x", padx=14, pady=(10, 4))
    summary_frame.grid_columnconfigure(0, weight=1)
    summary_frame.grid_columnconfigure(1, weight=1)
    summary_frame.grid_columnconfigure(2, weight=1)

    tk.Label(
        summary_frame,
        text=title,
        font=("Segoe UI", 14, "bold"),
        bg="#FFFFFF",
        fg="#1F3A5A",
    ).grid(row=0, column=0, sticky="w", padx=12, pady=10)

    tk.Label(
        summary_frame,
        text=f"Variables: {n}",
        font=("Segoe UI", 10),
        bg="#FFFFFF",
        fg="#1F3A5A",
    ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

    tk.Label(
        summary_frame,
        text=f"Tolerancia: {report.get('tol', '')}",
        font=("Segoe UI", 10),
        bg="#FFFFFF",
        fg="#1F3A5A",
    ).grid(row=1, column=1, sticky="w", padx=12, pady=(0, 10))

    tk.Label(
        summary_frame,
        text=f"Iteraciones: {report.get('iterations', 0)}",
        font=("Segoe UI", 10),
        bg="#FFFFFF",
        fg="#1F3A5A",
    ).grid(row=1, column=2, sticky="w", padx=12, pady=(0, 10))

    n = report.get("n", 0)
    identity_order = list(range(n))
    if method_name == "GS":
        row_order = report.get("row_order", identity_order)
    else:
        row_order = report.get("source_row", identity_order)

    if row_order != identity_order:
        reorder_msg = ", ".join([f"E{i + 1}<-R{row_order[i] + 1}" for i in range(n)])
        tk.Label(
            win,
            text=f"Reordenamiento automatico de ecuaciones: {reorder_msg}",
            font=("Arial", 10, "bold"),
            bg="#E7EEF6",
            fg="#1F3A5A",
            anchor="w",
            padx=14,
            pady=4,
        ).pack(fill="x")

    notebook = ttk.Notebook(win, style="Calc.TNotebook")
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    if method_name == "GS":
        n = report["n"]
        var_names = _default_variable_names(n)
        A_input = report.get("A_input", report.get("A_work"))
        b_input = report.get("b_input", report.get("b_work"))
        A_work = report.get("A_work")
        b_work = report.get("b_work")
        values = report["values"]
        checks = report["checks"]
        deltas = report["deltas"]
        iterations = report["iterations"]
        despejes = obtener_despejes_gauss_seidel(report, var_names)

        tab_matrices = tk.Frame(notebook, bg="#F4F8FD")
        tab_hoja = tk.Frame(notebook, bg="#F4F8FD")
        tab_despejes = tk.Frame(notebook, bg="#F4F8FD")
        tab_resumen = tk.Frame(notebook, bg="#F4F8FD")
        notebook.add(tab_matrices, text="Matrices")
        notebook.add(tab_hoja, text="Hoja principal")
        notebook.add(tab_despejes, text="Despejes")
        notebook.add(tab_resumen, text="Resumen de tolerancia")

        tk.Label(
            tab_matrices,
            text="Primero matriz inicial, luego matriz ordenada por variables",
            font=("Arial", 11, "bold"),
            bg="#F4F8FD",
            fg="#1F3A5A",
            anchor="w",
        ).pack(fill="x", padx=14, pady=(10, 4))

        cols_mat = ["Bloque", "Ecu", *var_names, "b"]
        rows_mat = []
        if A_input is not None and b_input is not None:
            for i in range(n):
                rows_mat.append(
                    ["Inicial", _roman(i + 1), *[_fmt3(A_input[i][j]) for j in range(n)], _fmt3(b_input[i])]
                )
        if A_work is not None and b_work is not None:
            for i in range(n):
                rows_mat.append(
                    ["Variables", _roman(i + 1), *[_fmt3(A_work[i][j]) for j in range(n)], _fmt3(b_work[i])]
                )

        _build_table(tab_matrices, cols_mat, rows_mat, height=max(8, 2 * n + 2))

        cols = ["Var", "V0"]
        for k in range(1, iterations + 1):
            cols.extend([f"{k}a", f"T{k}"])

        rows = []
        for i in range(n):
            row = [var_names[i], _fmt3(values[0][i])]
            for k in range(iterations):
                row.append(_fmt3(values[k + 1][i]))
                row.append("OK" if checks[k][i] else "NO")
            rows.append(row)

        _build_table(tab_hoja, cols, rows, height=max(7, n + 2))

        cols_res = ["Iter"] + [f"|d{v}|" for v in var_names] + ["Cumple"]
        rows_res = []
        for i in range(iterations):
            row = [str(i + 1)]
            row.extend(_fmt3(v) for v in deltas[i])
            row.append("OK" if all(checks[i]) else "NO")
            rows_res.append(row)
        _build_table(tab_resumen, cols_res, rows_res, height=max(7, min(16, iterations + 2)))

        tk.Label(
            tab_despejes,
            text="Despejes (V de la D)",
            font=("Arial", 12, "bold"),
            bg="#F4F8FD",
            fg="#1F3A5A",
        ).pack(anchor="w", padx=14, pady=(12, 4))

        if despejes:
            for eq in despejes:
                tk.Label(
                    tab_despejes,
                    text=eq,
                    font=("Consolas", 12),
                    bg="#F4F8FD",
                    fg="#243C57",
                    justify="left",
                    anchor="w",
                ).pack(fill="x", padx=20, pady=2)
        else:
            tk.Label(
                tab_despejes,
                text="No hay despejes disponibles para este reporte.",
                font=("Arial", 11),
                bg="#F4F8FD",
                fg="#243C57",
                justify="left",
                anchor="w",
            ).pack(fill="x", padx=20, pady=8)

    elif method_name == "RELAX":
        n = report["n"]
        var_names = _default_variable_names(n)
        base_A = report["base_A"]
        base_R = report["base_R"]
        records = report["records"]

        tab_base = tk.Frame(notebook, bg="#F4F8FD")
        tab_registros = tk.Frame(notebook, bg="#F4F8FD")
        tab_resumen = tk.Frame(notebook, bg="#F4F8FD")
        notebook.add(tab_base, text="Cuadro base")
        notebook.add(tab_registros, text="Registros T")
        notebook.add(tab_resumen, text="Resumen")

        cols_base = ["Ecu"] + var_names + ["R"]
        rows_base = []
        for i in range(n):
            rows_base.append([_roman(i + 1)] + [_fmt3(base_A[i][j]) for j in range(n)] + [_fmt3(base_R[i])])
        _build_table(tab_base, cols_base, rows_base, height=max(7, n + 2))

        help_text = (
            "Formato de clase: se toma el pivote (residuo más alejado de 0), "
            "se multiplica por la columna del pivote y se suma para obtener H_nuevo."
        )
        tk.Label(
            tab_registros,
            text=help_text,
            font=("Arial", 10, "italic"),
            bg="#F4F8FD",
            fg="#355171",
            justify="left",
            wraplength=1080,
        ).pack(anchor="w", padx=12, pady=(10, 4))

        tk.Label(
            tab_registros,
            text="Registros T en forma T (cada iteración muestra H_anterior, C_col pivote, pivote*Ccol y H_nuevo)",
            font=("Arial", 10, "bold"),
            bg="#F4F8FD",
            fg="#234264",
            justify="left",
            wraplength=1080,
        ).pack(anchor="w", padx=12, pady=(0, 6))

        cols_iter = ["Concepto"] + var_names
        rows_iter = []
        for idx, rec in enumerate(records, start=1):
            pivot_label = f"Iteración {idx}: pivote {var_names[rec['pivot_index']]} = {_fmt3(rec['pivot_value'])}"
            rows_iter.append([pivot_label] + ["" for _ in range(n)])
            rows_iter.append(["H_anterior"] + [_fmt3(v) for v in rec["residual_before"]])
            rows_iter.append(["C_col pivote"] + [_fmt3(v) for v in rec["column_coeffs"]])
            rows_iter.append(["pivote*Ccol"] + [_fmt3(v) for v in rec["adjustments"]])
            rows_iter.append(["H_nuevo"] + [_fmt3(v) for v in rec["residual_after"]])
            rows_iter.append(["----"] + ["----" for _ in range(n)])

        if records:
            col_sums = [sum(rec["residual_after"][i] for rec in records) for i in range(n)]
            rows_iter.append(["Sumatoria final"] + [_fmt3(v) for v in col_sums])

        _build_table(tab_registros, cols_iter, rows_iter, height=max(10, min(24, len(rows_iter) + 2)))

        cols_res = ["Iter", "Pivote", "Valor", *[f"H_{v}" for v in var_names], "max|H|", "Tol"]
        rows_res = []
        for idx, rec in enumerate(records, start=1):
            row = [str(idx), var_names[rec["pivot_index"]], _fmt3(rec["pivot_value"])]
            row.extend(_fmt3(v) for v in rec["residual_after"])
            row.append(_fmt3(rec["max_abs_after"]))
            row.append("OK" if rec["ok_after"] else "NO")
            rows_res.append(row)
        _build_table(tab_resumen, cols_res, rows_res, height=max(8, min(18, len(rows_res) + 3)))


def _show_text_window(parent, title, content):
    win = tk.Toplevel(parent)
    win.transient(parent)
    win.lift()
    win.attributes("-topmost", True)
    win.after(100, lambda: win.attributes("-topmost", False))
    win.title(title)
    win.geometry("860x620")
    win.minsize(600, 420)
    win.configure(bg="#E7EEF6")

    text_frame = tk.Frame(win, bg="#E7EEF6")
    text_frame.pack(fill="both", expand=True, padx=12, pady=10)

    text_widget = scrolledtext.ScrolledText(
        text_frame,
        wrap="word",
        font=("Segoe UI", 11),
        bg="#F7F9FC",
        fg="#172B45",
        relief="flat",
        bd=0,
        highlightthickness=0,
    )
    text_widget.pack(fill="both", expand=True)
    text_widget.insert("1.0", content)
    text_widget.config(state="disabled")


def _format_relax_t_records(report, var_names):
    lines = []
    records = report.get("records", [])
    if not records:
        lines.append("No hay registros T disponibles.")
        return "\n".join(lines)

    for idx, rec in enumerate(records, start=1):
        piv_var = var_names[rec["pivot_index"]]
        piv_val = _fmt3(rec["pivot_value"])
        lines.append(f"Iteración {idx}: pivote {piv_var} = {piv_val}")
        lines.append("H_anterior:")
        for i, v in enumerate(rec["residual_before"]):
            lines.append(f"  {var_names[i]}/R{i+1}: {_fmt3(v)}")
        lines.append("C_col pivote:")
        for i, v in enumerate(rec["column_coeffs"]):
            lines.append(f"  {var_names[i]}/R{i+1}: {_fmt3(v)}")
        lines.append("pivote*Ccol:")
        for i, v in enumerate(rec["adjustments"]):
            lines.append(f"  {var_names[i]}/R{i+1}: {_fmt3(v)}")
        lines.append("H_nuevo:")
        for i, v in enumerate(rec["residual_after"]):
            lines.append(f"  {var_names[i]}/R{i+1}: {_fmt3(v)}")
        lines.append("" )
        lines.append("-" * 80)
        lines.append("")

    return "\n".join(lines)


def _run_method(
    method_name,
    A_entries,
    b_entries,
    x0_entries,
    tol_entry,
    max_iter_entry,
    omega_entry,
    parent_window=None,
):
    try:
        A = _parse_matrix(A_entries)
        b = _parse_vector(b_entries)
        x0 = _parse_initial(x0_entries)
        tol = float(tol_entry.get().strip() or 1e-2)
        max_iter = int(max_iter_entry.get().strip() or 50)
        report = None

        if parent_window is None:
            raise RuntimeError("Parent window requerido para mostrar resultados.")

        if method_name == "GS":
            report = gauss_seidel_hoja(A, b, x0=x0, tol=tol, max_iter=max_iter)
            x = report["x"]
            it = report["iterations"]
            title = "Resumen Gauss-Seidel"
            report_title = "Gauss-Seidel"
            _show_report_window(parent_window, method_name, report)
            summary = [
                f"Gauss-Seidel (hoja) iteraciones: {it}",
                "Estado: cumple tolerancia en todas las variables." if report["converged"] else "Estado: no cumple tolerancia en todas las variables.",
            ]
        elif method_name == "RELAX":
            report = relajaciones_hoja(A, b, tol=tol, max_iter=max_iter)
            x = report["x"]
            it = report["iterations"]
            title = "Resumen Relajaciones"
            report_title = "Relajaciones"
            _show_report_window(parent_window, method_name, report)
            summary = [
                f"Relajaciones (hoja) iteraciones: {it}",
                "Estado: todos los residuos cumplen tolerancia." if report["converged"] else "Estado: residuos fuera de tolerancia al terminar max_iter.",
            ]
        elif method_name == "SOR":
            omega = float(omega_entry.get().strip() or 1.0)
            x, it = sor(A, b, omega=omega, x0=x0, tol=tol, max_iter=max_iter, verbose=False)
            title = "Resumen SOR"
            report_title = "SOR"
            summary = [f"SOR clasico (omega={omega}) convergio en {it} iteraciones."]
        else:
            x, it = gauss_seidel(A, b, x0=x0, tol=tol, max_iter=max_iter, verbose=False)
            title = "Resumen Gauss-Seidel"
            report_title = "Gauss-Seidel"
            summary = [f"Gauss-Seidel convergio en {it} iteraciones"]

        summary.append(f"Solución aproximada: {[('{:.6f}'.format(v)) for v in x]}")

        n = len(A)
        residuals = [b[i] - sum(A[i][j] * x[j] for j in range(n)) for i in range(n)]
        norm_r = max(abs(v) for v in residuals)
        residual_summary = f"Residuales R = {[round(v,6) for v in residuals]}, ||R||_inf = {norm_r:.6e}"
        summary.append(residual_summary)

        _show_text_window(parent_window, title, "\n".join(summary))

    except (ValueError, ZeroDivisionError, ArithmeticError) as exc:
        messagebox.showerror("Error", str(exc))


class GSORApp:
    BG_MENU = "#F7F7F7"
    BG_GS = "#2E446E"
    FG_GS = "#FFFFFF"
    BTN_GS = "#1E3A5F"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Métodos Numéricos - Gauss-Seidel y Relajaciones")
        self.root.geometry("1150x750")
        self.root.minsize(1050, 650)
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        self.size_var = tk.StringVar(value="4")
        self.A_entries = []
        self.b_entries = []
        self.x0_entries = []
        self.matrix_frame = None

        self._show_menu()

    def _show_menu(self):
        _clear_frame(self.container)

        frm = tk.Frame(self.container, bg=self.BG_MENU)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Universidad Autónoma de Chihuahua", font=("Georgia", 22, "bold"), bg=self.BG_MENU).pack(pady=(20, 5))
        tk.Label(frm, text="Facultad de Ingeniería", font=("Georgia", 17), bg=self.BG_MENU).pack(pady=(0, 15))

        tk.Label(frm, text="Métodos Numéricos - Gauss-Seidel y Relajaciones", font=("Georgia", 24, "bold"), bg=self.BG_MENU).pack(pady=5)
        tk.Label(frm, text="Parcial examen - Programa principal (interfaz)", font=("Georgia", 14), bg=self.BG_MENU).pack(pady=(0, 15))

        tk.Label(frm, text="Integrantes del equipo:\n- Aryam Desiree Méndez Sánchez  373025\n- Francisco Javier Ponce Saenz  325000", font=("Georgia", 12), bg=self.BG_MENU, justify="left").pack(pady=(0, 18))

        sep = ttk.Separator(frm, orient="horizontal")
        sep.pack(fill="x", padx=40, pady=8)

        btns = tk.Frame(frm, bg=self.BG_MENU)
        btns.pack(pady=20)

        tk.Button(btns, text="1. Presentación", width=22, font=("Arial", 12), bg="#4D7092", fg="white",
                  command=self._show_intro).grid(row=0, column=0, padx=10, pady=5)
        tk.Button(btns, text="2. Teoría y fórmulas", width=22, font=("Arial", 12), bg="#4D7092", fg="white",
                  command=self._show_formulas).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(btns, text="3. Calculadora práctica", width=22, font=("Arial", 12), bg="#4D7092", fg="white",
                  command=self._show_calculadora).grid(row=0, column=2, padx=10, pady=5)

        tk.Button(frm, text="Salir", width=10, font=("Arial", 11, "bold"), bg="#D9534F", fg="white",
                  command=self.root.quit).pack(pady=20)

    def _show_intro(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_GS)
        frm.pack(fill="both", expand=True)

        titulo = tk.Label(frm, text="Introducción a Gauss-Seidel y Relajaciones", font=("Georgia", 24, "bold"),
                          bg=self.BG_GS, fg=self.FG_GS)
        titulo.pack(pady=30)

        texto = (
            "Gauss-Seidel es un método iterativo para resolver sistemas de ecuaciones lineales. "
            "La idea es partir de V0 y actualizar x, y, z, ... en cascada para armar la hoja "
            "de calculo (iteracion por iteracion con prueba T).\n\n"
            "Relajaciones en este curso se trabaja por residuos: se forma el cuadro base con "
            "diagonal -1, se elige pivote como el residuo mas alejado de 0 y se construyen "
            "registros T hasta cumplir tolerancia en todos los residuos.\n\n"
            "La calculadora tambien conserva SOR clasico como referencia adicional."
        )

        tk.Label(frm, text=texto, font=("Georgia", 14), bg=self.BG_GS, fg=self.FG_GS, justify="left",
                 wraplength=980).pack(padx=20, pady=20)

        tk.Button(frm, text="← Menú", font=("Arial", 12), bg="#E1EBF5", command=self._show_menu).pack(pady=15)

    def _show_formulas(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_GS)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Fórmulas de Gauss-Seidel y Relajaciones", font=("Georgia", 24, "bold"),
                 bg=self.BG_GS, fg=self.FG_GS).pack(pady=30)

        formulas = (
            "Gauss-Seidel:\n"
            "x_i^(k+1) = (1/a_ii) [ b_i - Σ_{j<i} a_ij x_j^(k+1) - Σ_{j>i} a_ij x_j^(k) ]\n\n"
            "Relajaciones (residuos):\n"
            "1) Igualar cada ecuacion a 0.\n"
            "2) Normalizar para diagonal -1.\n"
            "3) H inicial = R (residuos).\n"
            "4) Pivote = residuo mas alejado de 0.\n"
            "5) Ajuste: H_nuevo = H_anterior + pivote * C_columna_pivote.\n"
            "6) Paro cuando Tol >= |H_i| para todas las variables.\n\n"
            "SOR clasico (referencia): x_i^(k+1) = (1 - omega) x_i^(k) + omega x_i^(GS)"
        )

        tk.Label(frm, text=formulas, font=("Georgia", 14), bg=self.BG_GS, fg=self.FG_GS, justify="left",
                 wraplength=980).pack(padx=20, pady=20)

        tk.Button(frm, text="← Menú", font=("Arial", 12), bg="#E1EBF5", command=self._show_menu).pack(pady=15)

    def _build_matrix_fields(self, n):
        n = int(n)
        self.A_entries = []
        self.b_entries = []
        self.x0_entries = []

        if self.matrix_frame is None:
            raise RuntimeError("matrix_frame no inicializado")

        # Encabezado de matriz
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()

        tk.Label(self.matrix_frame, text=f"Matriz A ({n}x{n})").grid(row=0, column=0, columnspan=n, sticky="w")
        for i in range(n):
            row = []
            for j in range(n):
                e = tk.Entry(self.matrix_frame, width=8)
                e.grid(row=1 + i, column=j, padx=2, pady=2)
                if i == j:
                    e.insert(0, "4")
                else:
                    e.insert(0, "-1" if abs(i - j) == 1 else "0")
                row.append(e)
            self.A_entries.append(row)

        tk.Label(self.matrix_frame, text="Vector b").grid(row=0, column=n + 1, sticky="w", padx=(20,0))
        for i in range(n):
            e = tk.Entry(self.matrix_frame, width=8)
            e.grid(row=1 + i, column=n + 1, padx=(20,2), pady=2)
            e.insert(0, "15" if i == 0 else "10")
            self.b_entries.append(e)

        tk.Label(self.matrix_frame, text="x0 inicial").grid(row=n + 2, column=0, columnspan=2, sticky="w", pady=(10,0))
        for i in range(n):
            e = tk.Entry(self.matrix_frame, width=8)
            e.grid(row=n + 3, column=i, padx=2, pady=2)
            e.insert(0, "0")
            self.x0_entries.append(e)

    def _show_calculadora(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        titulo = tk.Label(frm, text="Calculadora Gauss-Seidel / Relajaciones", font=("Georgia", 20, "bold"))
        titulo.grid(row=0, column=0, columnspan=6, pady=8)

        tk.Label(frm, text="Tamaño de matriz (n)").grid(row=1, column=0, sticky="w")
        # tamaño como variable de texto para compatibilidad con Combobox
        size_combo = ttk.Combobox(frm, textvariable=self.size_var, values=["2", "3", "4", "5", "6", "7", "8"], width=4, state="readonly")
        size_combo.grid(row=1, column=1, sticky="w")

        tk.Button(frm, text="Generar matriz", width=14, command=lambda: self._build_matrix_fields(self.size_var.get())).grid(row=1, column=2, padx=10)

        self.matrix_frame = tk.Frame(frm)
        self.matrix_frame.grid(row=2, column=0, columnspan=8, pady=5)

        self._build_matrix_fields(self.size_var.get())

        # Parámetros de iteración
        tk.Label(frm, text="Tolerancia").grid(row=3, column=0, sticky="w", pady=(15,0))
        tol_entry = tk.Entry(frm, width=12)
        tol_entry.grid(row=4, column=0, padx=2, pady=2)
        tol_entry.insert(0, "0.01")

        tk.Label(frm, text="Iteraciones max").grid(row=3, column=1, sticky="w", pady=(15,0))
        max_iter_entry = tk.Entry(frm, width=8)
        max_iter_entry.grid(row=4, column=1, padx=2, pady=2)
        max_iter_entry.insert(0, "50")

        tk.Label(frm, text="Omega (SOR)").grid(row=3, column=2, sticky="w", pady=(15,0))
        omega_entry = tk.Entry(frm, width=8)
        omega_entry.grid(row=4, column=2, padx=2, pady=2)
        omega_entry.insert(0, "1.25")

        btn_frame = tk.Frame(frm)
        btn_frame.grid(row=5, column=0, columnspan=8, pady=10)

        tk.Button(btn_frame, text="Gauss-Seidel (hoja)", width=22,
                  command=lambda: _run_method(
                      "GS",
                      self.A_entries,
                      self.b_entries,
                      self.x0_entries,
                      tol_entry,
                      max_iter_entry,
                      omega_entry,
                      parent_window=self.root,
                  )).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Relajaciones (hoja)", width=22,
              command=lambda: _run_method(
                  "RELAX",
                  self.A_entries,
                  self.b_entries,
                  self.x0_entries,
                  tol_entry,
                  max_iter_entry,
                  omega_entry,
                  parent_window=self.root,
              )).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="SOR clasico", width=18,
              command=lambda: _run_method(
                  "SOR",
                  self.A_entries,
                  self.b_entries,
                  self.x0_entries,
                  tol_entry,
                  max_iter_entry,
                  omega_entry,
                  parent_window=self.root,
              )).grid(row=0, column=2, padx=5)

        tk.Button(frm, text="← Menú", width=12, bg="#E1EBF5", command=self._show_menu).grid(row=6, column=0, pady=8)

    def run(self):        self.root.mainloop()


if __name__ == "__main__":
    GSORApp().run()
