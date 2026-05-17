"""Programa unificado de Métodos Numéricos para raíces.

Integra las presentaciones de Bisección, Falsa Posición y Newton-Raphson,
con navegación entre ventanas y el programa principal de cálculo.
"""

# pylint: disable=C0301,W0123

import math
import os

# Las bibliotecas de interfaz gráfica pueden no estar disponibles
# en entornos sin pantalla (headless) o con instalación mínima.
# rodeamos las importaciones para que el módulo pueda importarse
# (p. ej. durante pruebas) y agregamos comentarios de pylint
# para silenciar diagnósticos falsos.
try:
    import tkinter as tk  # pylint: disable=import-error
    from tkinter import ttk, scrolledtext, messagebox  # pylint: disable=import-error
except ImportError:  # pragma: no cover - código de GUI inalcanzable
    tk = None
    ttk = None
    scrolledtext = None
    messagebox = None

try:
    from PIL import Image, ImageTk  # pylint: disable=import-error
except ImportError:  # pragma: no cover - Pillow no instalado o sin soporte Tk
    Image = None
    ImageTk = None

try:
    from Parcial1.metodos_raices import (
        biseccion,
        falsa_posicion,
        newton_raphson,
        newton_mejorado,
        obtener_entorno_trig,
    )
except ImportError:
    from metodos_raices import (  # type: ignore
        biseccion,
        falsa_posicion,
        newton_raphson,
        newton_mejorado,
        obtener_entorno_trig,
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

class App:
    """Aplicación unificada con menú principal y sub-secciones."""

    BG_BISECCION = "cadetblue"
    FG_BISECCION = "midnightblue"
    BTN_BISECCION = "OliveDrab2"

    BG_FALSA = "mediumpurple"
    FG_FALSA = "midnightblue"
    BTN_FALSA = "Darkorchid4"
    BTN_FG_FALSA = "white"

    BG_NEWTON = "#2E4057"
    FG_NEWTON = "white"
    BTN_NEWTON = "#4A90D9"
    BTN_FG_NEWTON = "white"

    BG_MENU = "#F0F0F0"

    # tamaño de los logos de la cabecera (píxeles)
    LOGO_SIZE = 300  # un poco mayor que antes; mantiene el texto centrado

    def __init__(self):
        if tk is None:
            # tkinter falló al importarse más arriba; mostramos un mensaje claro
            # en lugar de que el programa se bloquee con AttributeError al crear
            # la ventana raíz.
            raise RuntimeError(
                "tkinter no está disponible. "
                "Instale el paquete de sistema (e.g. python3-tk) y ejecute de nuevo."
            )

        self.root = tk.Tk()
        self.root.title("Métodos Numéricos – Tarea Para Parcial 1")
        self.root.geometry("1150x700")
        self.root.minsize(900, 550)

        # Contenedor donde se montan todas las "páginas"
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        # Variables del calculador (se usan en la sección de cálculo)
        self.method_var = tk.StringVar(value="biseccion")
        self.newton_variant_var = tk.StringVar(value="clasico")
        self.x0_var = tk.StringVar()
        self.deriv_expr_var = tk.StringVar()
        self.deriv2_expr_var = tk.StringVar()
        # variable de selección de función ya no se usa; sólo entrada personalizada
        # kept for compatibility but default ignored
        self.func_var = tk.StringVar()
        self.custom_expr = tk.StringVar()
        self.use_degrees = tk.BooleanVar(value=False)
        self.a_var = tk.StringVar()
        self.b_var = tk.StringVar()
        self.tol_var = tk.StringVar(value="1e-6")
        self.max_iter_var = tk.StringVar(value="50")
        self.red_mode_var = tk.StringVar(value="D")
        self.decimals_var = tk.StringVar(value="6")

        # Widgets de la calculadora (se crean en _show_calculadora)
        self.custom_entry = None
        self.calc_a_label = None
        self.calc_a_entry = None
        self.calc_b_entry = None
        self.calc_x0_label = None
        self.calc_x0_entry = None
        self.calc_variant_label = None
        self.calc_variant_menu = None
        self.calc_deriv_label = None
        self.calc_deriv_entry = None
        self.calc_deriv2_label = None
        self.calc_deriv2_entry = None
        self.expr_buttons_frame = None
        self.preview_label = None
        self.preview_img = None
        self.preview_target = None
        self._img_fing = None
        self._img_uach = None

        self._show_main_menu()

    # =================================================================
    #  MENÚ PRINCIPAL
    # =================================================================

    def _add_header(self, parent, bg_color, fg=None):
        """Dibuja los logos y el texto de la universidad/facultad en una
        cabecera horizontal.

        *parent* es el contenedor donde se empacará el marco de la cabecera.
        El color de fondo **bg_color** se aplica a todos los widgets dentro de
        la cabecera. Opcionalmente se puede pasar **fg** para fijar un color de
        primer plano en las etiquetas de texto (si no se especifica se usa el
        valor por defecto).
        """
        header = tk.Frame(parent, bg=bg_color)
        header.pack(pady=(30, 5))
        base = os.path.dirname(os.path.abspath(__file__))
        # las imágenes están en resources/images, no en el mismo directorio de código
        images_dir = os.path.normpath(os.path.join(base, "..", "resources", "images"))

        # logo izquierdo – Facultad de Ingeniería
        self._img_fing = None
        fing_path = os.path.join(images_dir, "fing.png")
        try:
            # preferir Pillow cuando ImageTk esté disponible (permite redimensionar)
            if Image is None or ImageTk is None:
                raise ImportError
            img_fing = Image.open(fing_path)
            img_fing = img_fing.resize((self.LOGO_SIZE, self.LOGO_SIZE), Image.Resampling.LANCZOS)
            self._img_fing = ImageTk.PhotoImage(img_fing)
        except Exception:  # pylint: disable=broad-exception-caught
            # recurrir a PhotoImage de Tk simple (sin PIL)
            try:
                img = tk.PhotoImage(file=fing_path)
                # reducir tamaño si es necesario
                w, h = img.width(), img.height()
                if w > self.LOGO_SIZE or h > self.LOGO_SIZE:
                    factor = max(w/self.LOGO_SIZE, h/self.LOGO_SIZE)
                    # ensure at least 1 and round up so we actually shrink
                    factor_i = max(1, math.ceil(factor))
                    img = img.subsample(factor_i, factor_i)
                self._img_fing = img
            except (OSError, ValueError, tk.TclError):
                self._img_fing = None
        if self._img_fing is not None:
            tk.Label(header, image=self._img_fing, bg=bg_color).pack(side="left", padx=15)

        # centre text
        centre = tk.Frame(header, bg=bg_color)
        centre.pack(side="left", padx=10)
        fgcol = fg if fg is not None else "black"
        tk.Label(centre, text="Universidad Autónoma de Chihuahua",
                 font=("Georgia", 22, "bold"), bg=bg_color, fg=fgcol).pack()
        tk.Label(centre, text="Facultad de Ingeniería",
                 font=("Georgia", 16), bg=bg_color, fg=fgcol).pack()

        # logo derecho – UACH
        self._img_uach = None
        uach_path = os.path.join(images_dir, "uach.png")
        try:
            if Image is None or ImageTk is None:
                raise ImportError
            img_uach = Image.open(uach_path)
            img_uach = img_uach.resize((self.LOGO_SIZE, self.LOGO_SIZE), Image.Resampling.LANCZOS)
            self._img_uach = ImageTk.PhotoImage(img_uach)
        except Exception:  # pylint: disable=broad-exception-caught
            try:
                img = tk.PhotoImage(file=uach_path)
                w, h = img.width(), img.height()
                if w > self.LOGO_SIZE or h > self.LOGO_SIZE:
                    factor = max(w/self.LOGO_SIZE, h/self.LOGO_SIZE)
                    factor_i = max(1, math.ceil(factor))
                    img = img.subsample(factor_i, factor_i)
                self._img_uach = img
            except (OSError, ValueError, tk.TclError):
                self._img_uach = None
        if self._img_uach is not None:
            tk.Label(header, image=self._img_uach, bg=bg_color).pack(side="left", padx=15)

    def _show_main_menu(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_MENU)
        frm.pack(fill="both", expand=True)

        # ---- Logos + títulos ----
        self._add_header(frm, self.BG_MENU)

        tk.Label(frm, text="Métodos Numéricos – Raíces de Ecuaciones",
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
            ("1. Método de Bisección – Presentación", self._show_biseccion_portada, self.BTN_BISECCION, "black"),
            ("2. Método de Falsa Posición – Presentación", self._show_falsa_portada, self.BTN_FALSA, self.BTN_FG_FALSA),
            ("3. Método de Newton-Raphson – Presentación", self._show_newton_portada, self.BTN_NEWTON, self.BTN_FG_NEWTON),
            ("4. Programa de Cálculo (todos los métodos)", self._show_calculadora, "#228B22", "white"),
        ]

        for texto, cmd, bg, fg in botones:
            tk.Button(btn_frame, text=texto, font=("Georgia", 13, "bold"),
                      width=48, bg=bg, fg=fg, activebackground=bg,
                      command=cmd).pack(pady=8)

        tk.Button(frm, text="Salir", font=("Georgia", 11), bg="firebrick", fg="white",
                  command=self.root.quit).pack(pady=20)

    # =================================================================
    #  BISECCIÓN – presentación (4 ventanas)
    # =================================================================

    def _show_biseccion_portada(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_BISECCION)
        frm.pack(fill="both", expand=True)

        # cabecera con logos y texto de la institución
        self._add_header(frm, self.BG_BISECCION, fg=self.FG_BISECCION)

        tk.Label(frm, text="MÉTODO DE BISECCIÓN",
                 font=("Georgia", 24, "bold"), bg=self.BG_BISECCION, fg=self.FG_BISECCION).pack(pady=40)
        tk.Label(frm, text="Programa – Métodos Numéricos\n\nIntegrantes del equipo:\n"
                 "- Aryam Desiree Méndez Sánchez  373025\n"
                 "- Francisco Javier Ponce Saenz  325000",
                 font=("Georgia", 12), bg=self.BG_BISECCION, fg=self.FG_BISECCION).pack(pady=10)

        nav = tk.Frame(frm, bg=self.BG_BISECCION)
        nav.pack(pady=20)
        tk.Button(nav, text="← Menú", bg="gray70", command=self._show_main_menu).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_BISECCION,
                  command=self._show_biseccion_capitulo).pack(side="left", padx=10)

    def _show_biseccion_capitulo(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_BISECCION)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Capítulo 1: Raíces de polinomios",
                 font=("Georgia", 20, "bold"), bg=self.BG_BISECCION, fg=self.FG_BISECCION).pack(pady=80)
        tk.Label(frm, text="Tema: Método de Bisección",
                 font=("Georgia", 20, "bold"), bg=self.BG_BISECCION, fg=self.FG_BISECCION).pack(pady=50)

        nav = tk.Frame(frm, bg=self.BG_BISECCION)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_biseccion_portada).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_BISECCION,
                  command=self._show_biseccion_tema).pack(side="left", padx=10)

    def _show_biseccion_tema(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_BISECCION)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Tema: Método de Bisección",
                 font=("Georgia", 25, "bold"), bg=self.BG_BISECCION, fg=self.FG_BISECCION).pack(pady=30)
        tk.Label(frm, text="¿Para qué sirve?",
                 font=("Georgia", 17, "bold"), bg=self.BG_BISECCION, fg=self.FG_BISECCION).pack(pady=15)
        tk.Label(frm, text=(
            "El método de bisección sirve para encontrar de manera aproximada las raíces de\n"
            "una ecuación no lineal, es decir, los valores de x que hacen que f(x)=0.\n"
            "Se utiliza cuando la ecuación no se puede resolver fácilmente de forma algebraica."),
            font=("Georgia", 12), bg=self.BG_BISECCION, fg=self.FG_BISECCION).pack(pady=10)

        tk.Label(frm, text="Aplicaciones",
                 font=("Georgia", 17, "bold"), bg=self.BG_BISECCION, fg=self.FG_BISECCION).pack(pady=15)
        tk.Label(frm, text=(
            "Sus aplicaciones son muy comunes en ingeniería, física y matemáticas aplicadas,\n"
            "especialmente en problemas donde aparecen ecuaciones con exponentes, logaritmos\n"
            "o funciones trigonométricas que no se pueden despejar fácilmente.\n"
            "Se usa en cálculos de equilibrio, análisis de circuitos eléctricos,\n"
            "transferencia de calor, mecánica de fluidos y simulaciones numéricas."),
            font=("Georgia", 12), bg=self.BG_BISECCION, fg=self.FG_BISECCION).pack(pady=10)

        nav = tk.Frame(frm, bg=self.BG_BISECCION)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_biseccion_capitulo).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_BISECCION,
                  command=self._show_biseccion_formulas).pack(side="left", padx=10)

    def _show_biseccion_formulas(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_BISECCION)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Fórmulas del Método de Bisección",
                 font=("Georgia", 20, "bold"), bg=self.BG_BISECCION, fg=self.FG_BISECCION).pack(pady=80)
        tk.Label(frm, text="δx = (b - a) / 2  (semiancho)\nx = a + δx  (punto medio)\nCondición de paro: tolerancia ≥ |δx| (o |b - a| ≤ tolerancia)",
                 font=("Georgia", 15), bg=self.BG_BISECCION, fg=self.FG_BISECCION).pack(pady=50)

        nav = tk.Frame(frm, bg=self.BG_BISECCION)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_biseccion_tema).pack(side="left", padx=10)
        tk.Button(nav, text="Menú principal", bg="gray70",
                  command=self._show_main_menu).pack(side="left", padx=10)
        tk.Button(nav, text="Ir al Programa ▶", bg=self.BTN_BISECCION,
                  command=lambda: self._show_calculadora("biseccion")).pack(side="left", padx=10)

    # =================================================================
    #  FALSA POSICIÓN – presentación (4 ventanas)
    # =================================================================

    def _show_falsa_portada(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_FALSA)
        frm.pack(fill="both", expand=True)

        # cabecera con logos y texto de la institución
        self._add_header(frm, self.BG_FALSA)

        tk.Label(frm, text="MÉTODO DE FALSA POSICIÓN",
                 font=("Times", 20, "bold"), bg=self.BG_FALSA).pack(pady=40)
        tk.Label(frm, text="Programa – Métodos Numéricos\n\nIntegrantes del equipo:\n"
                 "- Aryam Desiree Méndez Sánchez  373025\n"
                 "- Francisco Javier Ponce Saenz  325000",
                 font=("Times", 14), bg=self.BG_FALSA).pack(pady=10)

        nav = tk.Frame(frm, bg=self.BG_FALSA)
        nav.pack(pady=20)
        tk.Button(nav, text="← Menú", bg="gray70", command=self._show_main_menu).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_FALSA, fg=self.BTN_FG_FALSA,
                  command=self._show_falsa_capitulo).pack(side="left", padx=10)

    def _show_falsa_capitulo(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_FALSA)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Capítulo 1: Raíces de polinomios",
                 font=("Times", 20, "bold"), bg=self.BG_FALSA).pack(pady=80)
        tk.Label(frm, text="Tema: Método de la Falsa Posición",
                 font=("Times", 20, "bold"), bg=self.BG_FALSA).pack(pady=50)

        nav = tk.Frame(frm, bg=self.BG_FALSA)
        nav.pack(side="bottom", fill="x", pady=10)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_falsa_portada).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_FALSA, fg=self.BTN_FG_FALSA,
                  command=self._show_falsa_tema).pack(side="right", padx=10)

    def _show_falsa_tema(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_FALSA)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Método de Falsa Posición",
                 font=("Times", 20, "bold"), bg=self.BG_FALSA).pack(pady=30)
        tk.Label(frm, text="¿Para qué sirve?",
                 font=("Times", 15, "bold"), bg=self.BG_FALSA).pack(pady=15)
        tk.Label(frm, text=(
            "El método de la falsa posición sirve para encontrar de manera aproximada\n"
            "las raíces de una ecuación no lineal, es decir, los valores de x que hacen\n"
            "que f(x)=0. Se utiliza cuando la ecuación no se puede resolver fácilmente\n"
            "de forma algebraica, por ejemplo cuando incluye exponentes, logaritmos o\n"
            "funciones trigonométricas."),
            font=("Times", 12), bg=self.BG_FALSA).pack(pady=10)

        tk.Label(frm, text="Aplicaciones",
                 font=("Times", 15, "bold"), bg=self.BG_FALSA).pack(pady=15)
        tk.Label(frm, text=(
            "Se usa para calcular valores en problemas de circuitos eléctricos,\n"
            "transferencia de calor, mecánica de fluidos, termodinámica y\n"
            "modelos matemáticos en programación."),
            font=("Times", 12), bg=self.BG_FALSA).pack(pady=10)

        nav = tk.Frame(frm, bg=self.BG_FALSA)
        nav.pack(side="bottom", fill="x", pady=10)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_falsa_capitulo).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_FALSA, fg=self.BTN_FG_FALSA,
                  command=self._show_falsa_formulas).pack(side="right", padx=10)

    def _show_falsa_formulas(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_FALSA)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Fórmulas del Método de Falsa Posición",
                 font=("Times", 20, "bold"), bg=self.BG_FALSA).pack(pady=80)
        tk.Label(frm, text="Δx = |f(a)|·(b-a) / (|f(a)| + |f(b)|)\n"  
                 "x = a + Δx  (equiv. a·f(b) - b·f(a) / (f(b) - f(a)))\n"  
                 "Condición: |b - a| ≤ tolerancia",
                 font=("Times", 15, "bold"), bg=self.BG_FALSA).pack(pady=50)

        nav = tk.Frame(frm, bg=self.BG_FALSA)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_falsa_tema).pack(side="left", padx=10)
        tk.Button(nav, text="Menú principal", bg="gray70",
                  command=self._show_main_menu).pack(side="left", padx=10)
        tk.Button(nav, text="Ir al Programa ▶", bg=self.BTN_FALSA, fg=self.BTN_FG_FALSA,
                  command=lambda: self._show_calculadora("falsa")).pack(side="left", padx=10)

    # =================================================================
    #  NEWTON-RAPHSON – presentación (4 ventanas)
    # =================================================================

    def _show_newton_portada(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_NEWTON)
        frm.pack(fill="both", expand=True)

        # cabecera con logos y texto de la institución
        self._add_header(frm, self.BG_NEWTON, fg=self.FG_NEWTON)

        tk.Label(frm, text="MÉTODO DE NEWTON-RAPHSON",
                 font=("Georgia", 24, "bold"), bg=self.BG_NEWTON, fg=self.FG_NEWTON).pack(pady=40)
        tk.Label(frm, text="Programa – Métodos Numéricos\n\nIntegrantes del equipo:\n"
                 "- Aryam Desiree Méndez Sánchez  373025\n"
                 "- Francisco Javier Ponce Saenz  325000",
                 font=("Georgia", 12), bg=self.BG_NEWTON, fg=self.FG_NEWTON).pack(pady=10)

        nav = tk.Frame(frm, bg=self.BG_NEWTON)
        nav.pack(pady=20)
        tk.Button(nav, text="← Menú", bg="gray70", command=self._show_main_menu).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_NEWTON, fg=self.BTN_FG_NEWTON,
                  command=self._show_newton_capitulo).pack(side="left", padx=10)

    def _show_newton_capitulo(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_NEWTON)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Capítulo 1: Raíces de polinomios",
                 font=("Georgia", 20, "bold"), bg=self.BG_NEWTON, fg=self.FG_NEWTON).pack(pady=80)
        tk.Label(frm, text="Tema: Método de Newton-Raphson (Tangentes)",
                 font=("Georgia", 20, "bold"), bg=self.BG_NEWTON, fg=self.FG_NEWTON).pack(pady=50)

        nav = tk.Frame(frm, bg=self.BG_NEWTON)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_newton_portada).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_NEWTON, fg=self.BTN_FG_NEWTON,
                  command=self._show_newton_tema).pack(side="left", padx=10)

    def _show_newton_tema(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_NEWTON)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Método de Newton-Raphson",
                 font=("Georgia", 25, "bold"), bg=self.BG_NEWTON, fg=self.FG_NEWTON).pack(pady=30)
        tk.Label(frm, text="¿Para qué sirve?",
                 font=("Georgia", 17, "bold"), bg=self.BG_NEWTON, fg=self.FG_NEWTON).pack(pady=15)
        tk.Label(frm, text=(
            "El método de Newton-Raphson utiliza la derivada de la función para\n"
            "encontrar raíces de forma más rápida que bisección o falsa posición.\n"
            "Converge cuadráticamente si la estimación inicial es buena."),
            font=("Georgia", 12), bg=self.BG_NEWTON, fg=self.FG_NEWTON).pack(pady=10)

        tk.Label(frm, text="Aplicaciones",
                 font=("Georgia", 17, "bold"), bg=self.BG_NEWTON, fg=self.FG_NEWTON).pack(pady=15)
        tk.Label(frm, text=(
            "Se usa extensamente en optimización, análisis estructural,\n"
            "dinámica de fluidos computacional, diseño de sistemas de control\n"
            "y en cualquier problema donde se necesite convergencia rápida."),
            font=("Georgia", 12), bg=self.BG_NEWTON, fg=self.FG_NEWTON).pack(pady=10)

        nav = tk.Frame(frm, bg=self.BG_NEWTON)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_newton_capitulo).pack(side="left", padx=10)
        tk.Button(nav, text="Siguiente →", bg=self.BTN_NEWTON, fg=self.BTN_FG_NEWTON,
                  command=self._show_newton_formulas).pack(side="left", padx=10)

    def _show_newton_formulas(self):
        _clear_frame(self.container)
        frm = tk.Frame(self.container, bg=self.BG_NEWTON)
        frm.pack(fill="both", expand=True)

        tk.Label(frm, text="Fórmulas del Método de Newton-Raphson",
                 font=("Georgia", 20, "bold"), bg=self.BG_NEWTON, fg=self.FG_NEWTON).pack(pady=60)
        tk.Label(frm, text=(
            "Clásico:\n"
            "  x_{n+1} = x_n - f(x_n) / f'(x_n)\n\n"
            "Mejorado (Halley):\n"
            "  h = f / f'\n"
            "  Δx = h / (1 - 0.5·f·f'' / f'²)\n"
            "  x_{n+1} = x_n - Δx\n\n"
            "Condición: |Δx| ≤ tolerancia"),
            font=("Georgia", 14), bg=self.BG_NEWTON, fg=self.FG_NEWTON, justify="left").pack(pady=30)

        nav = tk.Frame(frm, bg=self.BG_NEWTON)
        nav.pack(pady=20)
        tk.Button(nav, text="← Anterior", bg="gray70",
                  command=self._show_newton_tema).pack(side="left", padx=10)
        tk.Button(nav, text="Menú principal", bg="gray70",
                  command=self._show_main_menu).pack(side="left", padx=10)
        tk.Button(nav, text="Ir al Programa ▶", bg=self.BTN_NEWTON, fg=self.BTN_FG_NEWTON,
                  command=lambda: self._show_calculadora("newton")).pack(side="left", padx=10)

    # =================================================================
    #  CALCULADORA (todos los métodos)
    # =================================================================

    def _show_calculadora(self, metodo_preseleccionado=None):
        """Muestra la interfaz de cálculo con los 3 métodos."""
        _clear_frame(self.container)

        if metodo_preseleccionado:
            self.method_var.set(metodo_preseleccionado)

        top_bar = tk.Frame(self.container, bg="#333")
        top_bar.pack(fill="x")
        tk.Button(top_bar, text="← Menú principal", bg="gray70",
                  command=self._show_main_menu).pack(side="left", padx=10, pady=5)
        tk.Label(top_bar, text="Programa de Cálculo – Raíces",
                 font=("Georgia", 14, "bold"), bg="#333", fg="white").pack(side="left", padx=20)

        frm = ttk.Frame(self.container, padding=10)
        frm.pack(fill="both", expand=True)

        # Estilo para campos de entrada resaltados
        entry_cfg = dict(
            bg="white", fg="black",
            relief="solid", bd=2,
            highlightbackground="#4A90D9",
            highlightcolor="#E8443A",
            highlightthickness=2,
            font=("Consolas", 11),
            insertbackground="black",
        )

        # ---- Método ----
        ttk.Label(frm, text="Método:").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(frm, text="Bisección", variable=self.method_var,
                        value="biseccion", command=self._update_calc_fields).grid(row=0, column=1)
        ttk.Radiobutton(frm, text="Falsa posición", variable=self.method_var,
                        value="falsa", command=self._update_calc_fields).grid(row=0, column=2)
        ttk.Radiobutton(frm, text="Newton", variable=self.method_var,
                        value="newton", command=self._update_calc_fields).grid(row=0, column=3)

        # ---- Función ----
        ttk.Label(frm, text="Función:").grid(row=1, column=0, sticky="w")
        # sólo entrada personalizada; siempre habilitada
        self.custom_entry = tk.Entry(frm, textvariable=self.custom_expr, width=30, **entry_cfg)
        self.custom_entry.grid(row=2, column=1, columnspan=2, sticky="we")
        # eventos para vista previa dinámica
        self.custom_entry.bind("<FocusIn>", lambda e: self._set_preview_target(self.custom_entry))
        self.custom_entry.bind("<KeyRelease>", lambda e: self._update_preview(self.custom_entry.get()))
        # activar siempre el campo personalizado
        self.custom_entry.configure(state="normal")

        # soporte de botones para construir expresiones; el mismo panel se
        # utiliza para función principal y derivadas (el texto se insertará en
        # el entry que tenga el foco). mostramos una guía de uso encima.
        tk.Label(frm, text="Haga clic en la casilla que desea editar y use los botones:",
                 font=("Consolas", 9)).grid(row=4, column=1, columnspan=2, sticky="w")
        self.expr_buttons_frame = tk.Frame(frm)
        self.expr_buttons_frame.grid(row=5, column=1, columnspan=2, pady=(0, 5))
        # vista previa dinámica de la expresión en entrada activa
        self.preview_label = tk.Label(frm, text="", bg="white", relief="solid", bd=1,
                                      anchor="w", justify="left")
        # permitir que el recuadro crezca cuando la ventana se redimensione
        frm.rowconfigure(6, weight=1)
        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(2, weight=1)
        self.preview_label.grid(row=6, column=1, columnspan=2, sticky="nsew", pady=(0,5))
        self.preview_img = None  # referencia para que Pillow no recoja el gif
        self.preview_target = None
        def make_button(label, insert):
            return tk.Button(self.expr_buttons_frame, text=label,
                             command=lambda i=insert: self._insert_expr(i),
                             width=4)

        # botones útiles; se añaden en fila, puede ampliarse si se desea
        for lbl, ins in [
            ("x", "x"), ("+", "+"), ("-", "-"), ("*", "*"), ("/", "/"),
            ("^", "^"), ("(", "("), (")", ")"),
            ("sin", "sin("), ("cos", "cos("), ("tan", "tan("),
            ("log", "log("), ("exp", "exp("), ("sqrt", "sqrt("),
        ]:
            make_button(lbl, ins).pack(side="left", padx=1, pady=1)

        # no mostrar leyenda de funciones predefinidas

        # ---- Grados ----
        ttk.Checkbutton(frm, text="Trig en grados", variable=self.use_degrees).grid(row=7, column=1, columnspan=2, sticky="w")

        # ---- Intervalo / x0 ----
        self.calc_a_label = ttk.Label(frm, text="Intervalo [a, b]:")
        self.calc_a_label.grid(row=8, column=0, sticky="w")
        self.calc_a_entry = tk.Entry(frm, textvariable=self.a_var, width=10, **entry_cfg)
        self.calc_a_entry.grid(row=8, column=1, sticky="w")
        self.calc_b_entry = tk.Entry(frm, textvariable=self.b_var, width=10, **entry_cfg)
        self.calc_b_entry.grid(row=8, column=2, sticky="w")

        self.calc_x0_label = ttk.Label(frm, text="Valor inicial x0:")
        self.calc_x0_entry = tk.Entry(frm, textvariable=self.x0_var, width=10, **entry_cfg)

        self.calc_variant_label = ttk.Label(frm, text="Variante Newton:")
        self.calc_variant_menu = ttk.OptionMenu(frm, self.newton_variant_var,
                                                 "clasico", "clasico", "mejorado")

        self.calc_deriv_label = ttk.Label(frm, text="Derivada f'(x) (opcional; vacío aprox. numéricamente, útil con expresiones muy complejas):")
        self.calc_deriv_entry = tk.Entry(frm, textvariable=self.deriv_expr_var, width=20, **entry_cfg)
        self.calc_deriv_entry.bind("<FocusIn>", lambda e: self._set_preview_target(self.calc_deriv_entry))
        self.calc_deriv_entry.bind("<KeyRelease>", lambda e: self._update_preview(self.calc_deriv_entry.get()))

        self.calc_deriv2_label = ttk.Label(frm, text="Segunda derivada f''(x) (opcional; vacío aprox. numéricamente si es complejo):")
        self.calc_deriv2_entry = tk.Entry(frm, textvariable=self.deriv2_expr_var, width=20, **entry_cfg)
        self.calc_deriv2_entry.bind("<FocusIn>", lambda e: self._set_preview_target(self.calc_deriv2_entry))
        self.calc_deriv2_entry.bind("<KeyRelease>", lambda e: self._update_preview(self.calc_deriv2_entry.get()))

        # ---- Tolerancia / iteraciones ----
        ttk.Label(frm, text="Tolerancia:").grid(row=11, column=0, sticky="w")
        tk.Entry(frm, textvariable=self.tol_var, width=12, **entry_cfg).grid(row=11, column=1, sticky="w")
        ttk.Label(frm, text="Máx iter:").grid(row=11, column=2, sticky="w")
        tk.Entry(frm, textvariable=self.max_iter_var, width=8, **entry_cfg).grid(row=11, column=3, sticky="w")

        # ---- Redondeo ----
        ttk.Label(frm, text="Redondeo:").grid(row=12, column=0, sticky="w")
        ttk.OptionMenu(frm, self.red_mode_var, self.red_mode_var.get(), "D", "T").grid(row=12, column=1, sticky="w")
        ttk.Label(frm, text="Cifras:").grid(row=12, column=2, sticky="w")
        tk.Entry(frm, textvariable=self.decimals_var, width=5, **entry_cfg).grid(row=12, column=3, sticky="w")

        # ---- Botón calcular ----
        ttk.Button(frm, text="Calcular", command=self._on_calcular).grid(row=11, column=0, columnspan=4, pady=10)

        for child in frm.winfo_children():
            child.grid_configure(padx=5, pady=3)

        # listener para variante Newton
        self.newton_variant_var.trace_add("write", lambda *_: self._update_calc_fields())
        # ya no usamos func_var pero la mantenemos por compatibilidad

        # inicializar vista previa con campo personalizado vacío
        self._update_custom_entry(None)
        self._update_calc_fields()

    # -- helpers de la calculadora --

    def _update_custom_entry(self, _choice):
        # con sólo entrada libre, siempre habilitamos el campo y no borramos
        # nada; el parámetro *choice* se ignora.
        self.custom_entry.configure(state="normal")

    def _update_calc_fields(self):
        method = self.method_var.get()
        if method in ("biseccion", "falsa"):
            # intervalo en la fila 6
            self.calc_a_label.grid()
            self.calc_a_entry.grid()
            self.calc_b_entry.grid()
            # apartar los campos de Newton
            self.calc_x0_label.grid_remove()
            self.calc_x0_entry.grid_remove()
            self.calc_variant_label.grid_remove()
            self.calc_variant_menu.grid_remove()
            self.calc_deriv_label.grid_remove()
            self.calc_deriv_entry.grid_remove()
            self.calc_deriv2_label.grid_remove()
            self.calc_deriv2_entry.grid_remove()
        else:
            self.calc_a_label.grid_remove()
            self.calc_a_entry.grid_remove()
            self.calc_b_entry.grid_remove()
            # colocar los elementos de Newton en la fila donde antes estaba el
            # intervalo (fila 7 tras el último ajuste)
            self.calc_x0_label.grid(row=8, column=0, sticky="w")
            self.calc_x0_entry.grid(row=8, column=1, sticky="w")
            self.calc_variant_label.grid(row=8, column=2, sticky="w")
            self.calc_variant_menu.grid(row=8, column=3, sticky="w")
            # los campos de derivada son opcionales; se calcularán numéricamente si están vacíos
            self.calc_deriv_label.grid(row=9, column=0, sticky="w")
            self.calc_deriv_entry.grid(row=9, column=1, columnspan=2, sticky="we")
            if self.newton_variant_var.get() == "mejorado":
                self.calc_deriv2_label.grid(row=10, column=0, sticky="w")
                self.calc_deriv2_entry.grid(row=10, column=1, columnspan=2, sticky="we")
            else:
                self.calc_deriv2_label.grid_remove()
                self.calc_deriv2_entry.grid_remove()

    def _parse_number(self, text, cast=float):
        if text is None:
            raise ValueError("texto vacío")
        cleaned = text.split("#", 1)[0].strip()
        if cleaned == "":
            raise ValueError("texto vacío")
        return cast(cleaned)

    def _set_preview_target(self, entry_widget):
        """Designa *entry_widget* como destino de la vista previa."""
        self.preview_target = entry_widget
        self._update_preview(entry_widget.get())

    def _format_preview_unicode(self, expr: str) -> str:
        """Devuelve una versión 'bonita' de *expr* usando caracteres Unicode.

        - convierte exponentes numéricos a superíndices
        - si hay una sola barra '/', construye una fracción apilada básica
        """
        import re
        # superíndices para dígitos, letras y signos
        supmap = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵',
                  '6':'⁶','7':'⁷','8':'⁸','9':'⁹','+':'⁺','-':'⁻',
                  'x':'ˣ','y':'ʸ','n':'ⁿ','i':'ⁱ','e':'ᵉ'}
        def sup(m):
            s = m.group(1)
            return ''.join(supmap.get(ch, ch) for ch in s)
        # números después de ^
        expr = re.sub(r'\^(\d+)', sup, expr)
        # letra simple tras ^
        expr = re.sub(r'\^([A-Za-z])', lambda m: supmap.get(m.group(1), m.group(1)), expr)
        # (optional) exponente entre paréntesis: ^(expr) – aplicar superíndices caract a caract
        expr = re.sub(
            r"\^\(([^)]+)\)",
            lambda m: ''.join(supmap.get(ch, ch) for ch in m.group(1)),
            expr,
        )
        # fracción apilada si existe una sola '/'
        if expr.count('/') == 1:
            num, den = expr.split('/', 1)
            line = '-' * max(len(num), len(den))
            expr = f"{num}\n{line}\n{den}"
        return expr

    def _update_preview(self, expr):
        """Actualiza el widget de vista previa con la expresión *expr*.

        Se usa un formato Unicode simple para evitar dependencias opcionales
        y mantener la vista previa robusta en cualquier entorno.
        """
        expr = expr.strip()
        if not expr:
            self.preview_label.config(image="", text="")
            self.preview_img = None
            return
        pretty = self._format_preview_unicode(expr)
        self.preview_label.config(image="", text=pretty)
        self.preview_img = None
        self._adjust_preview_size(pretty)

    def _adjust_preview_size(self, text):
        """Calcula ancho/alto necesarios para la etiqueta de vista previa."""
        lines = text.split("\n")
        maxlen = max(len(l) for l in lines)
        # ancho en unidades de caracteres, altura en líneas
        self.preview_label.config(width=maxlen + 2, height=len(lines))

    def _insert_expr(self, text):
        """Inserta *text* en la entrada de texto que tenga el foco.

        Esto permite usar el mismo conjunto de botones para la función
        principal y para las derivadas. Después de la inserción se actualiza
        la vista previa si corresponde.
        """
        w = self.root.focus_get()
        # solo actuamos sobre widgets de tipo Entry
        if not isinstance(w, tk.Entry):
            return
        try:
            idx = w.index(tk.INSERT)
        except tk.TclError:  # widget podría no soportar index
            return
        w.insert(idx, text)
        if text.endswith("("):
            try:
                w.icursor(idx + len(text))
            except tk.TclError:
                pass
        # actualizar vista previa del contenido del entry enfocado
        if w is self.preview_target:
            self._update_preview(w.get())

    def _on_calcular(self):
        method = self.method_var.get()
        a = b = x0 = None
        try:
            if method in ("biseccion", "falsa"):
                a = self._parse_number(self.a_var.get(), float)
                b = self._parse_number(self.b_var.get(), float)
            else:
                x0 = self._parse_number(self.x0_var.get(), float)
            tol = self._parse_number(self.tol_var.get(), float)
            max_it = self._parse_number(self.max_iter_var.get(), int)
            decs = self._parse_number(self.decimals_var.get(), int)
        except ValueError as ve:
            messagebox.showerror("Error", f"Valores numéricos inválidos: {ve}")
            return

        if method in ("biseccion", "falsa") and a is not None and b is not None and a >= b:
            messagebox.showerror("Error", "Intervalo inválido: a debe ser menor que b")
            return
        if method == "newton" and max_it <= 0:
            messagebox.showerror("Error", "Número de iteraciones debe ser positivo")
            return

        # entorno trigonométrico
        ent = obtener_entorno_trig(self.use_degrees.get())

        # función ingresada por el usuario
        expr = self.custom_expr.get()
        # sustituir notación habitual por sintaxis Python
        expr = self._sanitize_expr(expr)
        # actualizar el contenido del entry con la versión saneada para
        # que el usuario vea el símbolo '-' correcto y expresiones limpias
        self.custom_expr.set(expr)
        env = {"x": 0, "log": math.log, "log10": math.log10,
               "exp": math.exp, "sqrt": math.sqrt, "pi": math.pi,
               "e": math.e, "abs": abs, **ent}

        eval_errors = (
            ValueError,
            TypeError,
            ZeroDivisionError,
            OverflowError,
            ArithmeticError,
            NameError,
            SyntaxError,
        )

        def func(x, _expr=expr, _env=env):
            return eval(_expr, {"__builtins__": {}, **_env, "x": x})
        # validar evaluando en un punto de prueba para detectar errores
        try:
            _ = func((a if a is not None else 1.0))
        except eval_errors as exc:
            messagebox.showerror("Error",
                                 f"Expresión inválida: {exc}\n"
                                 "Corrija la sintaxis o utilice los botones de ayuda.")
            return
        # envoltorio seguro que añade contexto a las excepciones de evaluación
        orig_func = func
        def safe_func(x, _orig=orig_func):
            try:
                return _orig(x)
            except eval_errors as exc:
                raise ValueError(f"función inválida en x={x}: {exc}") from exc

        func = safe_func
        # comprobar dominio inicial para detectar rápidamente errores
        sample_points = []
        if a is not None:
            sample_points.append(a)
        if b is not None:
            sample_points.append(b)
        if x0 is not None:
            sample_points.append(x0)
        for sp in sample_points:
            try:
                _ = func(sp)
            except eval_errors as exc:
                messagebox.showerror(
                    "Error",
                    f"La función no se puede evaluar en el punto {sp}: {exc}\n"
                    "Revise los valores iniciales o la expresión."
                )
                return

        # preparar funciones de derivada automáticas (numéricas) en caso de que
        # el usuario deje los campos de derivada vacíos; se usan diferencias
        # centradas
        def _auto_df(x):
            # paso adaptativo para mejorar la aproximación
            h = 1e-8 * (1 + abs(x))
            try:
                # usar paso complejo si la función lo permite
                return (func(x + h * 1j).imag) / h
            except (TypeError, ValueError, ZeroDivisionError, OverflowError, ArithmeticError):
                return (func(x + h) - func(x - h)) / (2 * h)

        def _auto_d2f(x):
            h = 1e-5
            return (func(x + h) - 2 * func(x) + func(x - h)) / (h * h)

        # ventana de resultados
        win = tk.Toplevel(self.root)
        win.title("Proceso – Resultados")
        txt = scrolledtext.ScrolledText(win, width=120, height=30, font=("Consolas", 10))
        txt.pack(fill="both", expand=True)

        def logger(line):
            txt.insert(tk.END, line + "\n")
            txt.see(tk.END)

        try:
            if method == "biseccion":
                biseccion(func, a, b, tol, max_it, self.red_mode_var.get(), decs, logger)
            elif method == "falsa":
                falsa_posicion(func, a, b, tol, max_it, self.red_mode_var.get(), decs, logger)
            else:
                # make derivative functions; user may supply expressions but we
                # fall back to automatic numeric differentiation if the field
                # is empty or invalid.
                deriv = self._make_eval_func(self.deriv_expr_var.get(), ent)
                if deriv is None:
                    deriv = _auto_df
                else:
                    # validate sample evaluation, using x0 or midpoint if
                    # available
                    sample_x = x0 if x0 is not None else (a + b) / 2 if a is not None and b is not None else 1.0
                    try:
                        _ = deriv(sample_x)
                    except (ValueError, TypeError, ZeroDivisionError, OverflowError, ArithmeticError) as exc:
                        messagebox.showerror("Error",
                                             f"Expresión de derivada inválida: {exc}")
                        return
                deriv2 = None
                if self.newton_variant_var.get() == "mejorado":
                    deriv2 = self._make_eval_func(self.deriv2_expr_var.get(), ent)
                    if deriv2 is None:
                        deriv2 = _auto_d2f
                    else:
                        sample_x = x0 if x0 is not None else (a + b) / 2 if a is not None and b is not None else 1.0
                        try:
                            _ = deriv2(sample_x)
                        except (ValueError, TypeError, ZeroDivisionError, OverflowError, ArithmeticError) as exc:
                            messagebox.showerror("Error",
                                                 f"Expresión de segunda derivada inválida: {exc}")
                            return
                # chequear condiciones iniciales de Newton antes de ejecutar
                if x0 is not None:
                    try:
                        d0 = deriv(x0)
                        if d0 == 0:
                            messagebox.showerror("Error",
                                                 "Derivada evaluada en x0 es cero; el método de Newton falla.")
                            return
                    except (ValueError, TypeError, ZeroDivisionError, OverflowError, ArithmeticError) as exc:
                        messagebox.showerror("Error",
                                             f"No se pudo evaluar la derivada en x0: {exc}")
                        return
                    if self.newton_variant_var.get() == "mejorado":
                        try:
                            f0 = func(x0)
                            d2_0 = deriv2(x0)
                            denom = 1 - 0.5 * f0 * d2_0 / (d0 * d0)
                            if denom == 0:
                                messagebox.showerror("Error",
                                                     "Denominador de variante mejorada nulo en x0; el método falla.")
                                return
                        except (ValueError, TypeError, ZeroDivisionError, OverflowError, ArithmeticError) as exc:
                            messagebox.showerror("Error",
                                                 f"Error al evaluar derivadas en x0: {exc}")
                            return
                # finalmente invocar el algoritmo correspondiente
                if self.newton_variant_var.get() == "mejorado":
                    newton_mejorado(
                        func, deriv, deriv2, x0, tol, max_it,
                        self.red_mode_var.get(), decs, logger,
                    )
                else:
                    newton_raphson(
                        func, deriv, x0, tol, max_it,
                        self.red_mode_var.get(), decs, logger,
                    )
        except (ValueError, TypeError, ZeroDivisionError, OverflowError, ArithmeticError, RuntimeError) as err:
            messagebox.showerror(
                "Error",
                f"Error al evaluar la función: {err}\n"
                "Revise sintaxis o use los botones de entrada para construir la ecuación."
            )

    @staticmethod
    def _make_eval_func(raw_expr, ent):
        """Devuelve una función evaluable o None si la expresión está vacía.

        El campo *raw_expr* puede contener notación más amigable (^ para
        potencia, 2x sin operador, etc.) y será sanitizado antes de usar
        ``eval``. Si la cadena está vacía o solo contiene comentarios, se
        devuelve ``None`` para que el código del llamador pueda decidir usar
        derivadas numéricas.
        """
        expr = raw_expr.split("#", 1)[0].strip()
        if not expr:
            return None
        expr = App._sanitize_expr(expr)
        env = {
            "x": 0, "log": math.log, "log10": math.log10,
            "exp": math.exp, "sqrt": math.sqrt, "pi": math.pi,
            "e": math.e, "abs": abs, **ent,
        }
        def _fn(x, _expr=expr, _env=env):
            return eval(_expr, {"__builtins__": {}, **_env, "x": x})
        return _fn


    # helper de saneamiento de expresiones --------------------------------

    @staticmethod
    def _sanitize_expr(expr: str) -> str:
        """Convierte la expresión introducida a sintaxis válida de Python.

        - reemplaza '^' por '**'
        - transforma multiplicaciones implícitas (2x, x(, )x) en formato
          con '*'
        - sustituye superíndices comunes por potencias
        - quita espacios innecesarios
        """
        import re
        # normalizar signos de resta/menos e–dash/em–dash
        expr = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2212]", "-", expr)
        # convertir notación de logaritmo natural a nombre Python
        expr = re.sub(r"\bln\b", "log", expr)
        # sustituciones de superíndices
        for sup, replacement in {
            "²": "**2", "³": "**3", "⁴": "**4", "⁵": "**5", "⁶": "**6",
            "⁷": "**7", "⁸": "**8", "⁹": "**9",
        }.items():
            expr = expr.replace(sup, replacement)
        expr = expr.replace("^", "**")
        # insertar operador * cuando falte entre número/variable/cierre paréntesis
        # y letra, número o paréntesis abierto siguiente.
        expr = re.sub(r"(?<=[0-9\)])(?=[A-Za-z\(])", "*", expr)
        expr = re.sub(r"(?<=[A-Za-z\)])(?=[0-9\(])", "*", expr)
        # la sustitución anterior inserta '*' también entre nombres de funciones
        # conocidas y el paréntesis de llamada; lo corregimos aquí
        for fn in ("sin", "cos", "tan", "log", "exp", "sqrt", "abs"):
            expr = re.sub(rf"{fn}\*\(", fn + "(", expr)
        return expr.strip()

    # =================================================================
    #  Run
    # =================================================================

    def run(self):
        """Inicia el bucle principal de la aplicación."""
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
