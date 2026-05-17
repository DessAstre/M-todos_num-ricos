"""Programa de Métodos Numéricos – SSEL (Métodos Exactos).

Interfaz gráfica en Tkinter para resolver Sistemas de Ecuaciones Lineales
Simultáneas mediante:
  1. Eliminación Gaussiana
  2. Gauss-Jordan
  3. Inversa de Matriz

Basado en la estructura de programa_principal.py.
"""

# pylint: disable=C0301

import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Any

try:
    from PIL import Image, ImageTk
except ImportError:  # Pillow no instalado o sin soporte Tk
    Image = None
    ImageTk = None

try:
    from Parcial1.metodos_ssel import (
        gauss,
        gauss_jordan,
        inversa_matriz,
        inversa_cofactores,
        cramer,
    )
except ImportError:
    from metodos_ssel import (  # type: ignore
        gauss,
        gauss_jordan,
        inversa_matriz,
        inversa_cofactores,
        cramer,
    )


# =====================================================================
#  Helpers
# =====================================================================

def _clear_frame(container):
    """Destruye todos los widgets hijos de un contenedor."""
    for w in container.winfo_children():
        w.destroy()


# =====================================================================
#  Clase principal
# =====================================================================

class SSELApp:
    """Aplicación unificada para SSEL con menú principal y sub-secciones."""

    # Colores por método
    BG_GAUSS = "#1B4332"
    FG_GAUSS = "#D8F3DC"
    BTN_GAUSS = "#2D6A4F"
    BTN_FG_GAUSS = "white"

    BG_JORDAN = "#1B3A4B"
    FG_JORDAN = "#CAF0F8"
    BTN_JORDAN = "#168AAD"
    BTN_FG_JORDAN = "white"

    BG_INVERSA = "#3C1361"
    FG_INVERSA = "#E0AAFF"
    BTN_INVERSA = "#7B2CBF"
    BTN_FG_INVERSA = "white"

    BG_MENU = "#F0F0F0"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Métodos Numéricos – SSEL Métodos Exactos (Parcial 2)")
        self.root.geometry("1150x750")
        self.root.minsize(950, 600)

        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        # Variables de la calculadora
        self.method_var = tk.StringVar(value="gauss")
        self.inversa_method_var = tk.StringVar(value="identidad")
        self.method_var.trace_add("write", self._update_inversa_method_state)
        self._inv_gauss_rb = None
        self._inv_gauss_jordan_rb = None
        self.size_var = tk.StringVar(value="3")
        self.red_mode_var = tk.StringVar(value="D")
        self.decimals_var = tk.StringVar(value="6")
        self.show_inverse_solution_var = tk.BooleanVar(value=True)
        self._inv_show_solution_cb = None
        self.result_txt = None

        # Almacén de entries de la matriz
        self.matrix_entries = []
        self.matrix_frame = None

        self._show_main_menu()

    def _update_inversa_method_state(self, *_):
        """Activa/desactiva opciones de cálculo de la inversa según el método."""
        estado = "normal" if self.method_var.get() == "inversa" else "disabled"
        if self._inv_gauss_rb is not None:
            self._inv_gauss_rb.configure(state=estado)
        if self._inv_gauss_jordan_rb is not None:
            self._inv_gauss_jordan_rb.configure(state=estado)
        if self._inv_show_solution_cb is not None:
            self._inv_show_solution_cb.configure(state=estado)

    # =================================================================
    #  MENÚ PRINCIPAL
    # =================================================================

    def _show_main_menu(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_MENU)
        frm.pack(fill="both", expand=True)

        # ---- Logos + títulos ----
        header = tk.Frame(frm, bg=self.BG_MENU)
        header.pack(pady=(30, 5))

        base = os.path.dirname(os.path.abspath(__file__))

        if Image is not None and ImageTk is not None:
            try:
                img_fing = Image.open(os.path.join(base, "fing.png"))
                img_fing = img_fing.resize((100, 100), Image.Resampling.LANCZOS)
                self._img_fing = ImageTk.PhotoImage(img_fing)
                tk.Label(header, image=self._img_fing,
                         bg=self.BG_MENU).pack(side="left", padx=15)
            except (OSError, ValueError, tk.TclError):
                pass

        center = tk.Frame(header, bg=self.BG_MENU)
        center.pack(side="left", padx=10)
        tk.Label(center, text="Universidad Autónoma de Chihuahua",
                 font=("Georgia", 22, "bold"), bg=self.BG_MENU).pack()
        tk.Label(center, text="Facultad de Ingeniería",
                 font=("Georgia", 16), bg=self.BG_MENU).pack()

        if Image is not None and ImageTk is not None:
            try:
                img_uach = Image.open(os.path.join(base, "uach.png"))
                img_uach = img_uach.resize((100, 100), Image.Resampling.LANCZOS)
                self._img_uach = ImageTk.PhotoImage(img_uach)
                tk.Label(header, image=self._img_uach,
                         bg=self.BG_MENU).pack(side="left", padx=15)
            except (OSError, ValueError, tk.TclError):
                pass

        tk.Label(frm, text="Métodos Numéricos – SSEL Métodos Exactos",
                 font=("Georgia", 20, "bold"), bg=self.BG_MENU).pack(pady=(20, 5))
        tk.Label(frm, text="Integrantes del equipo:\n"
                 "- Aryam Desiree Méndez Sánchez  373025\n"
                 "- Francisco Javier Ponce Saenz  325000",
                 font=("Georgia", 12), bg=self.BG_MENU, justify="center").pack(pady=15)

        sep = ttk.Separator(frm, orient="horizontal")
        sep.pack(fill="x", padx=40, pady=10)

        btn_frame = tk.Frame(frm, bg=self.BG_MENU)
        btn_frame.pack(pady=10)

        botones = [
            ("1. Eliminación Gaussiana – Presentación", self._show_gauss_portada, self.BTN_GAUSS, self.BTN_FG_GAUSS),
            ("2. Gauss-Jordan – Presentación", self._show_jordan_portada, self.BTN_JORDAN, self.BTN_FG_JORDAN),
            ("3. Inversa de Matriz – Presentación", self._show_inversa_portada, self.BTN_INVERSA, self.BTN_FG_INVERSA),
            ("4. Programa de Cálculo (todos los métodos)", self._show_calculadora, "#228B22", "white"),
        ]

        for texto, cmd, bg, fg in botones:
            tk.Button(btn_frame, text=texto, font=("Georgia", 13, "bold"),
                      width=48, bg=bg, fg=fg, activebackground=bg,
                      command=cmd).pack(pady=8)

        tk.Button(frm, text="Salir", font=("Georgia", 11), bg="firebrick", fg="white",
                  command=self.root.quit).pack(pady=20)

    # =================================================================
    #  GAUSS – presentación (4 ventanas)
    # =================================================================

    def _show_gauss_portada(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_GAUSS)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Universidad Autónoma de Chihuahua",
                 font=("Georgia", 20, "bold"), bg=self.BG_GAUSS, fg=self.FG_GAUSS).pack(pady=40)
        tk.Label(frm, text="Facultad de Ingeniería",
                 font=("Georgia", 15, "bold"), bg=self.BG_GAUSS, fg=self.FG_GAUSS).pack(pady=5)
        tk.Label(frm, text="ELIMINACIÓN GAUSSIANA",
                 font=("Georgia", 24, "bold"), bg=self.BG_GAUSS, fg=self.FG_GAUSS).pack(pady=40)
        tk.Label(frm, text="Programa – Métodos Numéricos\n\nIntegrantes del equipo:\n"
                 "- Aryam Desiree Méndez Sánchez  373025\n"
                 "- Francisco Javier Ponce Saenz  325000",
                 font=("Georgia", 12), bg=self.BG_GAUSS, fg=self.FG_GAUSS).pack(pady=10)

        nav = tk.Frame(frm, bg=self.BG_GAUSS)
        nav.pack(pady=20)
        tk.Button(nav, text="← Menú", bg="gray70", command=self._show_main_menu).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_GAUSS, fg=self.BTN_FG_GAUSS,
                  command=self._show_gauss_capitulo).pack(side="left", padx=10)

    def _show_gauss_capitulo(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_GAUSS)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Capítulo 2: Sistemas de Ecuaciones Lineales",
                 font=("Georgia", 20, "bold"), bg=self.BG_GAUSS, fg=self.FG_GAUSS).pack(pady=80)
        tk.Label(frm, text="Tema: Eliminación Gaussiana",
                 font=("Georgia", 20, "bold"), bg=self.BG_GAUSS, fg=self.FG_GAUSS).pack(pady=50)

        nav = tk.Frame(frm, bg=self.BG_GAUSS)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_gauss_portada).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_GAUSS, fg=self.BTN_FG_GAUSS,
                  command=self._show_gauss_tema).pack(side="left", padx=10)

    def _show_gauss_tema(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_GAUSS)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Eliminación Gaussiana",
                 font=("Georgia", 25, "bold"), bg=self.BG_GAUSS, fg=self.FG_GAUSS).pack(pady=30)
        tk.Label(frm, text="¿Para qué sirve?",
                 font=("Georgia", 17, "bold"), bg=self.BG_GAUSS, fg=self.FG_GAUSS).pack(pady=15)
        tk.Label(frm, text=(
            "La eliminación gaussiana es un método para resolver sistemas de ecuaciones\n"
            "lineales simultáneas (SSEL). Transforma la matriz aumentada en una forma\n"
            "triangular superior y luego aplica sustitución regresiva para encontrar\n"
            "las incógnitas del sistema."),
            font=("Georgia", 12), bg=self.BG_GAUSS, fg=self.FG_GAUSS).pack(pady=10)

        tk.Label(frm, text="Aplicaciones",
                 font=("Georgia", 17, "bold"), bg=self.BG_GAUSS, fg=self.FG_GAUSS).pack(pady=15)
        tk.Label(frm, text=(
            "Se utiliza en ingeniería estructural para resolver sistemas de fuerzas,\n"
            "en circuitos eléctricos (leyes de Kirchhoff), balanceo de ecuaciones\n"
            "químicas, análisis de redes y problemas de programación lineal.\n"
            "Es uno de los métodos más utilizados en álgebra lineal computacional."),
            font=("Georgia", 12), bg=self.BG_GAUSS, fg=self.FG_GAUSS).pack(pady=10)

        nav = tk.Frame(frm, bg=self.BG_GAUSS)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_gauss_capitulo).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_GAUSS, fg=self.BTN_FG_GAUSS,
                  command=self._show_gauss_formulas).pack(side="left", padx=10)

    def _show_gauss_formulas(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_GAUSS)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Fórmulas de la Eliminación Gaussiana",
                 font=("Georgia", 20, "bold"), bg=self.BG_GAUSS, fg=self.FG_GAUSS).pack(pady=50)
        tk.Label(frm, text=(
            "Fase 1 – Triangulación (eliminación hacia adelante):\n\n"
            "  Multiplicador:   m(i,k) = a(i,k) / a(k,k)\n\n"
            "  Nueva fila:      Fᵢ = Fᵢ - m(i,k) × Fₖ\n\n\n"
            "Fase 2 – Sustitución regresiva:\n\n"
            "  xₙ = bₙ / aₙₙ\n\n"
            "  xᵢ = (bᵢ - Σ aᵢⱼ·xⱼ) / aᵢᵢ    para i = n-1, ..., 1"),
            font=("Georgia", 14), bg=self.BG_GAUSS, fg=self.FG_GAUSS, justify="left").pack(pady=20)

        nav = tk.Frame(frm, bg=self.BG_GAUSS)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_gauss_tema).pack(side="left", padx=10)
        tk.Button(nav, text="Menú principal", bg="gray70",
                  command=self._show_main_menu).pack(side="left", padx=10)
        tk.Button(nav, text="Ir al Programa ▶", bg=self.BTN_GAUSS, fg=self.BTN_FG_GAUSS,
                  command=lambda: self._show_calculadora("gauss")).pack(side="left", padx=10)

    # =================================================================
    #  GAUSS-JORDAN – presentación (4 ventanas)
    # =================================================================

    def _show_jordan_portada(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_JORDAN)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Universidad Autónoma de Chihuahua",
                 font=("Georgia", 20, "bold"), bg=self.BG_JORDAN, fg=self.FG_JORDAN).pack(pady=40)
        tk.Label(frm, text="Facultad de Ingeniería",
                 font=("Georgia", 15, "bold"), bg=self.BG_JORDAN, fg=self.FG_JORDAN).pack(pady=5)
        tk.Label(frm, text="MÉTODO DE GAUSS-JORDAN",
                 font=("Georgia", 24, "bold"), bg=self.BG_JORDAN, fg=self.FG_JORDAN).pack(pady=40)
        tk.Label(frm, text="Programa – Métodos Numéricos\n\nIntegrantes del equipo:\n"
                 "- Aryam Desiree Méndez Sánchez  373025\n"
                 "- Francisco Javier Ponce Saenz  325000",
                 font=("Georgia", 12), bg=self.BG_JORDAN, fg=self.FG_JORDAN).pack(pady=10)

        nav = tk.Frame(frm, bg=self.BG_JORDAN)
        nav.pack(pady=20)
        tk.Button(nav, text="← Menú", bg="gray70", command=self._show_main_menu).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_JORDAN, fg=self.BTN_FG_JORDAN,
                  command=self._show_jordan_capitulo).pack(side="left", padx=10)

    def _show_jordan_capitulo(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_JORDAN)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Capítulo 2: Sistemas de Ecuaciones Lineales",
                 font=("Georgia", 20, "bold"), bg=self.BG_JORDAN, fg=self.FG_JORDAN).pack(pady=80)
        tk.Label(frm, text="Tema: Método de Gauss-Jordan",
                 font=("Georgia", 20, "bold"), bg=self.BG_JORDAN, fg=self.FG_JORDAN).pack(pady=50)

        nav = tk.Frame(frm, bg=self.BG_JORDAN)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_jordan_portada).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_JORDAN, fg=self.BTN_FG_JORDAN,
                  command=self._show_jordan_tema).pack(side="left", padx=10)

    def _show_jordan_tema(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_JORDAN)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Método de Gauss-Jordan",
                 font=("Georgia", 25, "bold"), bg=self.BG_JORDAN, fg=self.FG_JORDAN).pack(pady=30)
        tk.Label(frm, text="¿Para qué sirve?",
                 font=("Georgia", 17, "bold"), bg=self.BG_JORDAN, fg=self.FG_JORDAN).pack(pady=15)
        tk.Label(frm, text=(
            "El método de Gauss-Jordan es una extensión de la eliminación gaussiana.\n"
            "En lugar de solo triangular, reduce la matriz a la forma escalonada\n"
            "reducida por filas (identidad), eliminando elementos tanto por debajo\n"
            "como por encima del pivote. No requiere sustitución regresiva."),
            font=("Georgia", 12), bg=self.BG_JORDAN, fg=self.FG_JORDAN).pack(pady=10)

        tk.Label(frm, text="Aplicaciones",
                 font=("Georgia", 17, "bold"), bg=self.BG_JORDAN, fg=self.FG_JORDAN).pack(pady=15)
        tk.Label(frm, text=(
            "Se utiliza para encontrar la inversa de matrices, resolver múltiples\n"
            "sistemas con la misma matriz de coeficientes, y en aplicaciones de\n"
            "criptografía, gráficos por computadora y análisis de datos.\n"
            "Es muy utilizado en ingeniería y ciencias computacionales."),
            font=("Georgia", 12), bg=self.BG_JORDAN, fg=self.FG_JORDAN).pack(pady=10)

        nav = tk.Frame(frm, bg=self.BG_JORDAN)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_jordan_capitulo).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_JORDAN, fg=self.BTN_FG_JORDAN,
                  command=self._show_jordan_formulas).pack(side="left", padx=10)

    def _show_jordan_formulas(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_JORDAN)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Fórmulas del Método de Gauss-Jordan",
                 font=("Georgia", 20, "bold"), bg=self.BG_JORDAN, fg=self.FG_JORDAN).pack(pady=50)
        tk.Label(frm, text=(
            "Para cada columna k (k = 1, 2, …, n):\n\n"
            "  1. Normalizar fila pivote:\n"
            "     Fₖ = Fₖ / a(k,k)\n\n"
            "  2. Eliminar en TODAS las demás filas (i ≠ k):\n"
            "     Fᵢ = Fᵢ - a(i,k) × Fₖ\n\n"
            "Resultado: la matriz queda como [I | solución]"),
            font=("Georgia", 14), bg=self.BG_JORDAN, fg=self.FG_JORDAN, justify="left").pack(pady=20)

        nav = tk.Frame(frm, bg=self.BG_JORDAN)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_jordan_tema).pack(side="left", padx=10)
        tk.Button(nav, text="Menú principal", bg="gray70",
                  command=self._show_main_menu).pack(side="left", padx=10)
        tk.Button(nav, text="Ir al Programa ▶", bg=self.BTN_JORDAN, fg=self.BTN_FG_JORDAN,
                  command=lambda: self._show_calculadora("gauss_jordan")).pack(side="left", padx=10)

    # =================================================================
    #  INVERSA DE MATRIZ – presentación (4 ventanas)
    # =================================================================

    def _show_inversa_portada(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_INVERSA)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Universidad Autónoma de Chihuahua",
                 font=("Georgia", 20, "bold"), bg=self.BG_INVERSA, fg=self.FG_INVERSA).pack(pady=40)
        tk.Label(frm, text="Facultad de Ingeniería",
                 font=("Georgia", 15, "bold"), bg=self.BG_INVERSA, fg=self.FG_INVERSA).pack(pady=5)
        tk.Label(frm, text="INVERSA DE MATRIZ",
                 font=("Georgia", 24, "bold"), bg=self.BG_INVERSA, fg=self.FG_INVERSA).pack(pady=40)
        tk.Label(frm, text="Programa – Métodos Numéricos\n\nIntegrantes del equipo:\n"
                 "- Aryam Desiree Méndez Sánchez  373025\n"
                 "- Francisco Javier Ponce Saenz  325000",
                 font=("Georgia", 12), bg=self.BG_INVERSA, fg=self.FG_INVERSA).pack(pady=10)

        nav = tk.Frame(frm, bg=self.BG_INVERSA)
        nav.pack(pady=20)
        tk.Button(nav, text="← Menú", bg="gray70", command=self._show_main_menu).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_INVERSA, fg=self.BTN_FG_INVERSA,
                  command=self._show_inversa_capitulo).pack(side="left", padx=10)

    def _show_inversa_capitulo(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_INVERSA)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Capítulo 2: Sistemas de Ecuaciones Lineales",
                 font=("Georgia", 20, "bold"), bg=self.BG_INVERSA, fg=self.FG_INVERSA).pack(pady=80)
        tk.Label(frm, text="Tema: Resolución por Inversa de Matriz",
                 font=("Georgia", 20, "bold"), bg=self.BG_INVERSA, fg=self.FG_INVERSA).pack(pady=50)

        nav = tk.Frame(frm, bg=self.BG_INVERSA)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_inversa_portada).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_INVERSA, fg=self.BTN_FG_INVERSA,
                  command=self._show_inversa_tema).pack(side="left", padx=10)

    def _show_inversa_tema(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_INVERSA)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Inversa de Matriz",
                 font=("Georgia", 25, "bold"), bg=self.BG_INVERSA, fg=self.FG_INVERSA).pack(pady=30)
        tk.Label(frm, text="¿Para qué sirve?",
                 font=("Georgia", 17, "bold"), bg=self.BG_INVERSA, fg=self.FG_INVERSA).pack(pady=15)
        tk.Label(frm, text=(
            "El método de la inversa permite resolver un sistema Ax = b\n"
            "calculando la inversa de la matriz A, de modo que x = A⁻¹·b.\n"
            "Es especialmente útil cuando se necesita resolver varios sistemas\n"
            "con la misma matriz A pero distintos vectores b."),
            font=("Georgia", 12), bg=self.BG_INVERSA, fg=self.FG_INVERSA).pack(pady=10)

        tk.Label(frm, text="Aplicaciones",
                 font=("Georgia", 17, "bold"), bg=self.BG_INVERSA, fg=self.FG_INVERSA).pack(pady=15)
        tk.Label(frm, text=(
            "Se utiliza en control automático, procesamiento de señales,\n"
            "modelos econométricos, transformaciones geométricas en 3D,\n"
            "análisis de circuitos y simulaciones numéricas donde la misma\n"
            "matriz aparece repetidamente con distintas condiciones."),
            font=("Georgia", 12), bg=self.BG_INVERSA, fg=self.FG_INVERSA).pack(pady=10)

        nav = tk.Frame(frm, bg=self.BG_INVERSA)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_inversa_capitulo).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_INVERSA, fg=self.BTN_FG_INVERSA,
                  command=self._show_inversa_formulas).pack(side="left", padx=10)

    def _show_inversa_formulas(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_INVERSA)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Fórmulas del Método de la Inversa",
                 font=("Georgia", 20, "bold"), bg=self.BG_INVERSA, fg=self.FG_INVERSA).pack(pady=50)
        tk.Label(frm, text=(
            "Dado el sistema  Ax = b:\n\n"
            "  1. Construir la matriz aumentada [A | I]\n\n"
            "  2. Aplicar Gauss-Jordan para obtener [I | A⁻¹]\n\n"
            "  3. La solución es:  x = A⁻¹ · b\n\n"
            "Condición: A debe ser no singular (det(A) ≠ 0)"),
            font=("Georgia", 14), bg=self.BG_INVERSA, fg=self.FG_INVERSA, justify="left").pack(pady=20)

        nav = tk.Frame(frm, bg=self.BG_INVERSA)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_inversa_tema).pack(side="left", padx=10)
        tk.Button(nav, text="Menú principal", bg="gray70",
                  command=self._show_main_menu).pack(side="left", padx=10)
        tk.Button(nav, text="Ir al Programa ▶", bg=self.BTN_INVERSA, fg=self.BTN_FG_INVERSA,
                  command=lambda: self._show_calculadora("inversa")).pack(side="left", padx=10)

    # =================================================================
    #  CALCULADORA
    # =================================================================

    def _show_calculadora(self, metodo_preseleccionado=None):
        """Muestra la interfaz de cálculo para SSEL."""
        _clear_frame(self.container)

        if metodo_preseleccionado:
            self.method_var.set(metodo_preseleccionado)

        # Barra superior
        top_bar = tk.Frame(self.container, bg="#333")
        top_bar.pack(fill="x")
        tk.Button(top_bar, text="← Menú principal", bg="gray70",
                  command=self._show_main_menu).pack(side="left", padx=10, pady=5)
        tk.Label(top_bar, text="Programa de Cálculo – SSEL Métodos Exactos",
                 font=("Georgia", 14, "bold"), bg="#333", fg="white").pack(side="left", padx=20)

        # Frame principal con scroll
        main_frame = tk.Frame(self.container)
        main_frame.pack(fill="both", expand=True)

        # Panel izquierdo – configuración
        left_panel = tk.Frame(main_frame, padx=15, pady=10)
        left_panel.pack(side="left", fill="y")

        entry_cfg: dict[str, Any] = dict(
            bg="white", fg="black",
            relief="solid", bd=2,
            highlightbackground="#4A90D9",
            highlightcolor="#E8443A",
            highlightthickness=2,
            font=("Consolas", 11),
            insertbackground="black",
        )

        # ---- Método ----
        ttk.Label(left_panel, text="Método:", font=("Georgia", 11, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 5), columnspan=5)

        ttk.Radiobutton(left_panel, text="Gauss", variable=self.method_var,
                        value="gauss").grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(left_panel, text="Gauss-Jordan", variable=self.method_var,
                        value="gauss_jordan").grid(row=1, column=1, sticky="w")
        ttk.Radiobutton(left_panel, text="Inversa", variable=self.method_var,
                        value="inversa").grid(row=1, column=2, sticky="w")
        ttk.Radiobutton(left_panel, text="Determinante", variable=self.method_var,
                        value="determinante").grid(row=1, column=3, sticky="w")
        ttk.Radiobutton(left_panel, text="Cramer (determinantes)", variable=self.method_var,
                        value="cramer").grid(row=1, column=4, sticky="w")

        # ---- Método para inversa ----
        ttk.Label(left_panel, text="Método para inversa:", font=("Georgia", 10)).grid(
            row=2, column=0, sticky="w", pady=(10, 0), columnspan=3)
        self._inv_gauss_rb = ttk.Radiobutton(left_panel, text="Cofactores",
                                             variable=self.inversa_method_var,
                                             value="cofactores")
        self._inv_gauss_rb.grid(row=3, column=0, sticky="w")
        self._inv_gauss_jordan_rb = ttk.Radiobutton(
            left_panel, text="Identidad", variable=self.inversa_method_var,
            value="identidad")
        self._inv_gauss_jordan_rb.grid(row=3, column=1, sticky="w")

        self._inv_show_solution_cb = ttk.Checkbutton(
            left_panel,
            text="Mostrar valores de x (A⁻¹·b)",
            variable=self.show_inverse_solution_var,
            onvalue=True,
            offvalue=False,
        )
        self._inv_show_solution_cb.grid(row=4, column=0, columnspan=3, sticky="w", pady=(3, 0))

        # Asegurar que las opciones de inversa se habiliten/deshabiliten según el método
        self._update_inversa_method_state()

        # ---- Tamaño ----
        ttk.Label(left_panel, text="Tamaño del sistema (n):", font=("Georgia", 10)).grid(
            row=5, column=0, sticky="w", pady=(15, 0), columnspan=2)
        size_combo = ttk.Combobox(left_panel, textvariable=self.size_var,
                                   values=["2", "3", "4", "5", "6"],
                                   width=5, state="readonly")
        size_combo.grid(row=5, column=2, sticky="w", pady=(15, 0))
        size_combo.bind("<<ComboboxSelected>>", lambda e: self._rebuild_matrix_grid())

        # ---- Redondeo ----
        ttk.Label(left_panel, text="Redondeo:", font=("Georgia", 10)).grid(
            row=5, column=0, sticky="w", pady=(10, 0))
        ttk.OptionMenu(left_panel, self.red_mode_var, self.red_mode_var.get(),
                        "D", "T").grid(row=5, column=1, sticky="w", pady=(10, 0))

        ttk.Label(left_panel, text="Cifras:", font=("Georgia", 10)).grid(
            row=6, column=0, sticky="w", pady=(5, 0))
        tk.Entry(left_panel, textvariable=self.decimals_var, width=5, **entry_cfg).grid(
            row=6, column=1, sticky="w", pady=(5, 0))

        # Leyenda
        ttk.Label(left_panel, text="D = redondear\nT = truncar",
                  font=("Consolas", 8), foreground="gray").grid(
            row=7, column=0, columnspan=3, sticky="w", pady=(5, 0))

        # ---- Botones ----
        btn_frame = tk.Frame(left_panel)
        btn_frame.grid(row=8, column=0, columnspan=3, pady=20)

        tk.Button(btn_frame, text="Resolver", font=("Georgia", 12, "bold"),
                  bg="#228B22", fg="white", width=15, command=self._on_resolver).pack(pady=5)
        tk.Button(btn_frame, text="Limpiar", font=("Georgia", 10),
                  bg="#CC5500", fg="white", width=15, command=self._limpiar_matriz).pack(pady=5)

        # Panel derecho – grilla de la matriz
        right_panel = tk.Frame(main_frame, padx=15, pady=10)
        right_panel.pack(side="left", fill="both", expand=True)

        ttk.Label(right_panel, text="Matriz aumentada [A | b]:",
                  font=("Georgia", 12, "bold")).pack(anchor="w", pady=(0, 5))
        ttk.Label(right_panel,
                  text="Ingrese los coeficientes de cada fila y el término independiente (última columna).",
                  font=("Georgia", 9), foreground="gray").pack(anchor="w", pady=(0, 10))

        self.matrix_frame = tk.Frame(right_panel)
        self.matrix_frame.pack(anchor="nw")

        self._rebuild_matrix_grid()

        # Panel de resultados (muestra transformaciones y procedimientos)
        ttk.Label(right_panel, text="Procedimiento:",
                  font=("Georgia", 12, "bold")).pack(anchor="w", pady=(10, 5))
        self.result_txt = scrolledtext.ScrolledText(right_panel, width=110, height=18,
                                                    font=("Consolas", 10),
                                                    bg="#1E1E1E", fg="#D4D4D4",
                                                    insertbackground="white")
        self.result_txt.pack(fill="both", expand=True, padx=5, pady=5)

    def _rebuild_matrix_grid(self):
        """Reconstruye la grilla de entradas según el tamaño seleccionado."""
        if self.matrix_frame is None:
            return

        # Guardar valores actuales por si el tamaño cambia
        old_values = []
        for row in self.matrix_entries:
            old_values.append([e.get() for e in row])

        for w in self.matrix_frame.winfo_children():
            w.destroy()

        try:
            n = int(self.size_var.get())
        except ValueError:
            n = 3

        if n < 2:
            n = 2
        if n > 6:
            n = 6

        entry_cfg: dict[str, Any] = dict(
            bg="white", fg="black",
            relief="solid", bd=2,
            highlightbackground="#4A90D9",
            highlightcolor="#E8443A",
            highlightthickness=2,
            font=("Consolas", 12),
            insertbackground="black",
        )

        # Encabezados de columna
        for j in range(n):
            tk.Label(self.matrix_frame, text=f"x{j + 1}",
                     font=("Georgia", 10, "bold"), fg="#333").grid(row=0, column=j + 1, padx=3)
        tk.Label(self.matrix_frame, text="│", font=("Consolas", 12, "bold"),
                 fg="#999").grid(row=0, column=n + 1)
        tk.Label(self.matrix_frame, text="b", font=("Georgia", 10, "bold"),
                 fg="#C00").grid(row=0, column=n + 2, padx=3)

        self.matrix_entries = []
        for i in range(n):
            # Etiqueta de fila
            tk.Label(self.matrix_frame, text=f"F{i + 1}",
                     font=("Georgia", 10, "bold"), fg="#333").grid(row=i + 1, column=0, padx=(0, 5))
            row_entries = []
            for j in range(n + 1):
                e = tk.Entry(self.matrix_frame, width=7, justify="center", **entry_cfg)
                if j == n:
                    # Separador visual antes de b
                    tk.Label(self.matrix_frame, text="│", font=("Consolas", 14, "bold"),
                             fg="#999").grid(row=i + 1, column=j + 1)
                    e.grid(row=i + 1, column=j + 2, padx=3, pady=3)
                else:
                    e.grid(row=i + 1, column=j + 1, padx=3, pady=3)

                # Restaurar valores previos si existen
                if i < len(old_values) and j < len(old_values[i]):
                    e.insert(0, old_values[i][j])

                row_entries.append(e)
            self.matrix_entries.append(row_entries)

    def _limpiar_matriz(self):
        """Limpia todos los campos de la matriz."""
        for row in self.matrix_entries:
            for e in row:
                e.delete(0, tk.END)

    def _on_resolver(self):
        """Lee la matriz, valida, y resuelve con el método seleccionado."""
        try:
            n = int(self.size_var.get())
        except ValueError:
            messagebox.showerror("Error", "Tamaño de sistema inválido.")
            return

        try:
            cifras = int(self.decimals_var.get())
            if cifras < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Número de cifras decimales inválido.")
            return

        modo = self.red_mode_var.get()
        metodo = self.method_var.get()
        metodo_inversa = self.inversa_method_var.get() if metodo == "inversa" else None

        if metodo == "inversa":
            metodo_display = (
                f"Inversa ({'Cofactores' if metodo_inversa == 'cofactores' else 'Identidad'})"
            )
        elif metodo == "determinante":
            metodo_display = "Determinante (inversa por cofactores)"
        elif metodo == "cramer":
            metodo_display = "Cramer (determinantes)"
        else:
            metodo_display = metodo.replace("_", "-").title()

        # Leer la matriz
        matrix = []
        for i in range(n):
            fila = []
            for j in range(n + 1):
                texto = self.matrix_entries[i][j].get().strip()
                if texto == "":
                    messagebox.showerror(
                        "Error",
                        f"Campo vacío en fila {i + 1}, columna {j + 1}.\n"
                        "Todos los campos deben tener un valor numérico."
                    )
                    return
                try:
                    # Soportar fracciones simples como "1/3"
                    if "/" in texto:
                        partes = texto.split("/")
                        valor = float(partes[0]) / float(partes[1])
                    else:
                        valor = float(texto)
                except (ValueError, ZeroDivisionError):
                    messagebox.showerror(
                        "Error",
                        f"Valor no numérico en fila {i + 1}, columna {j + 1}: '{texto}'"
                    )
                    return
                fila.append(valor)
            matrix.append(fila)

        # Limpiar resultados previos
        if hasattr(self, "result_txt") and self.result_txt is not None:
            self.result_txt.delete("1.0", tk.END)

        def logger(line):
            if hasattr(self, "result_txt") and self.result_txt is not None:
                self.result_txt.insert(tk.END, line + "\n")
                self.result_txt.see(tk.END)

        logger(f"Resultados – {metodo_display}")
        logger("" )

        show_solution = self.show_inverse_solution_var.get()
        try:
            if metodo == "gauss":
                gauss(matrix, cifras, modo, logger)
            elif metodo == "gauss_jordan":
                gauss_jordan(matrix, cifras, modo, logger)
            elif metodo == "inversa":
                if metodo_inversa == "cofactores":
                    inversa_cofactores(matrix, cifras, modo, logger, mostrar_solucion=show_solution)
                else:
                    inversa_matriz(matrix, cifras, modo, logger, mostrar_solucion=show_solution)
            elif metodo == "determinante":
                # Mostrar el determinante y luego resolver por inversa (cofactores)
                inversa_cofactores(matrix, cifras, modo, logger, mostrar_solucion=True)
            elif metodo == "cramer":
                cramer(matrix, cifras, modo, logger)
            else:
                messagebox.showerror("Error", f"Método desconocido: {metodo}")
        except ValueError as ve:
            logger(f"\n⚠ ERROR: {ve}")
            messagebox.showwarning("Sistema Inválido", str(ve))
        except (TypeError, RuntimeError, OverflowError, ArithmeticError) as err:
            logger(f"\n⚠ ERROR INESPERADO: {err}")
            messagebox.showerror("Error", f"Error inesperado: {err}")

    # =================================================================
    #  Run
    # =================================================================

    def run(self):
        """Inicia el bucle principal de la aplicación."""
        self.root.mainloop()


if __name__ == "__main__":
    SSELApp().run()
