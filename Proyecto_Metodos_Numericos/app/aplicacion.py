"""Aplicación principal — Métodos Numéricos.

Aplica un tema clásico y elegante, soporta scroll vertical en todas las vistas
(rueda del ratón incluida), redimensionado correcto en pantalla completa y
selector de subtemas dentro de cada calculadora para cambiar de método sin
volver al menú.
"""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from . import tema
from . import widgets
from .contenido import (
    TITULO_APP,
    SUBTITULO_PORTADA,
    INTEGRANTES,
    GRUPOS_TEMARIO,
    METODOS,
    SUBTEMAS_POR_TIPO,
    EJEMPLOS,
)
from .evaluador import evaluar_expresion, construir_entorno_matematico

# ---------------------------------------------------------------------------
#  Imports de los algoritmos numéricos
# ---------------------------------------------------------------------------

try:
    from nucleo.raices import (
        biseccion, falsa_posicion, newton_raphson, obtener_entorno_trig,
    )
except ImportError:
    biseccion = falsa_posicion = newton_raphson = obtener_entorno_trig = None

try:
    from nucleo.ssel_exactos import gauss, gauss_jordan, inversa_matriz, cramer
except ImportError:
    gauss = gauss_jordan = inversa_matriz = cramer = None

try:
    from nucleo.ssel_iterativos import gauss_seidel_hoja
except ImportError:
    gauss_seidel_hoja = None

try:
    from nucleo.interpolacion import (
        interpolacion_lineal_piecewise_y, interpolacion_lagrange,
    )
except ImportError:
    interpolacion_lineal_piecewise_y = interpolacion_lagrange = None

try:
    from nucleo.integracion import (
        trapezoidal_rule, simpson_one_third, simpson_three_eighths,
        newton_cotes, richardson_extrapolation,
    )
except ImportError:
    trapezoidal_rule = simpson_one_third = simpson_three_eighths = None
    newton_cotes = richardson_extrapolation = None

try:
    from nucleo.ajuste_curvas import (
        coeficientes_polinomio_con_pasos, mejor_ajuste,
        evaluar_polinomio, rss, formato_ecuacion,
    )
except ImportError:
    coeficientes_polinomio_con_pasos = mejor_ajuste = None
    evaluar_polinomio = rss = formato_ecuacion = None


try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_IMAGENES = os.path.join(DIR_RAIZ, "recursos", "imagenes")


# ---------------------------------------------------------------------------
#  Aplicación
# ---------------------------------------------------------------------------

class AplicacionMetodosNumericos:
    """Aplicación principal."""

    # ----- Construcción ------------------------------------------------------

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(TITULO_APP)
        self.root.geometry("1280x800")
        self.root.minsize(960, 620)
        self.root.configure(bg=tema.COLOR_FONDO)

        # Estilos ttk (Combobox, Scrollbar)
        self._estilo = ttk.Style(self.root)
        tema.configurar_estilo_ttk(self._estilo)

        # Imágenes institucionales (se mantienen vivas para evitar GC)
        self._img_fing = None
        self._img_uach = None
        self._cargar_imagenes()

        # Estado actual
        self.metodo_activo: str = ""
        self._ventana_resultados: tk.Toplevel | None = None
        self._texto_resultados: scrolledtext.ScrolledText | None = None

        # Variables compartidas: se crean concretas en __init__ (nunca None)
        self._inicializar_estado_calculadora()

        # Acelerador: F11 alterna pantalla completa
        self._pantalla_completa = False
        self.root.bind("<F11>", self._alternar_pantalla_completa)
        self.root.bind("<Escape>", self._salir_pantalla_completa)

        self._mostrar_portada()

    def run(self):
        self.root.mainloop()

    # ----- Imágenes ----------------------------------------------------------

    def _cargar_imagenes(self):
        fing = os.path.join(DIR_IMAGENES, "fing.png")
        uach = os.path.join(DIR_IMAGENES, "uach.png")
        self._img_fing = self._cargar_imagen(fing, (110, 110))
        self._img_uach = self._cargar_imagen(uach, (110, 110))

    def _cargar_imagen(self, ruta: str, tamano=(110, 110)):
        if not os.path.isfile(ruta):
            return None
        if Image is not None and ImageTk is not None:
            try:
                img = Image.open(ruta)
                img.thumbnail(tamano, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            except (OSError, AttributeError):
                pass
        try:
            return tk.PhotoImage(file=ruta)
        except (OSError, tk.TclError):
            return None

    # ----- Helpers de ventana ------------------------------------------------

    def _limpiar_root(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _inicializar_estado_calculadora(self) -> None:
        """Crea una sola vez las variables Tk compartidas por las calculadoras.

        Cada calculadora reutiliza las mismas instancias y sólo modifica su
        valor con .set(). Los widgets que se construyen dentro de cada vista
        (matrices y áreas de texto) usan placeholders no visibles hasta que
        la calculadora los reemplaza.
        """
        # Frame y Text "placeholder" — nunca se empacan; se reemplazan en
        # cada calculadora. Su único propósito es ofrecer un objeto concreto
        # con la API esperada para el análisis estático.
        placeholder_frame: tk.Frame = tk.Frame(self.root)
        placeholder_text: tk.Text = tk.Text(self.root)

        # Raíces
        self.r_metodo = tk.StringVar(value="Bisección")
        self.r_expr = tk.StringVar(value="x**3 - 2*x - 5")
        self.r_a = tk.StringVar(value="2")
        self.r_b = tk.StringVar(value="3")
        self.r_x0 = tk.StringVar(value="2")
        self.r_tol = tk.StringVar(value="1e-6")
        self.r_iter = tk.StringVar(value="50")
        self.r_dec = tk.StringVar(value="6")
        self.r_grados = tk.BooleanVar(value=False)

        # SSEL exactos
        self.s_metodo = tk.StringVar(value="gauss")
        self.s_tam = tk.StringVar(value="3")
        self.s_dec = tk.StringVar(value="6")
        self.s_entradas: list[list[tk.Entry]] = []
        self.s_frame_matriz: tk.Frame = placeholder_frame

        # SSEL iterativo
        self.i_tam = tk.StringVar(value="3")
        self.i_tol = tk.StringVar(value="0.01")
        self.i_iter = tk.StringVar(value="50")
        self.i_entradas: list[list[tk.Entry]] = []
        self.i_frame_matriz: tk.Frame = placeholder_frame

        # Interpolación
        self.it_metodo = tk.StringVar(value="lineal")
        self.it_x = tk.StringVar(value="2")
        self.it_puntos: tk.Text = placeholder_text

        # Integración
        self.in_expr = tk.StringVar(value="x**2")
        self.in_a = tk.StringVar(value="0")
        self.in_b = tk.StringVar(value="1")
        self.in_n = tk.StringVar(value="4")
        self.in_metodo = tk.StringVar(value="trapecio")

        # Ajuste de curvas
        self.aj_grado = tk.StringVar(value="auto")
        self.aj_x_eval = tk.StringVar(value="")
        self.aj_puntos: tk.Text = placeholder_text

    def _alternar_pantalla_completa(self, _event=None):
        self._pantalla_completa = not self._pantalla_completa
        self.root.attributes("-fullscreen", self._pantalla_completa)

    def _salir_pantalla_completa(self, _event=None):
        if self._pantalla_completa:
            self._pantalla_completa = False
            self.root.attributes("-fullscreen", False)

    # ----- Encabezado --------------------------------------------------------

    def _agregar_encabezado(self, padre, fondo, color_texto):
        widgets.EncabezadoUACH(
            padre, fondo=fondo, color_texto=color_texto,
            imagen_fing=self._img_fing, imagen_uach=self._img_uach,
        ).pack(fill="x")

    # ============================================================
    #  Portada
    # ============================================================

    def _mostrar_portada(self):
        self._limpiar_root()
        self.metodo_activo = ""
        self.root.configure(bg=tema.COLOR_FONDO_OSCURO)

        marco = widgets.MarcoConScroll(self.root, bg=tema.COLOR_FONDO_OSCURO)
        marco.pack(fill="both", expand=True)
        cont = marco.interior

        self._agregar_encabezado(cont, tema.COLOR_FONDO_OSCURO, tema.COLOR_TEXTO_CLARO)

        # Marco hero
        hero = tk.Frame(
            cont, bg=tema.COLOR_FONDO_OSCURO,
            highlightthickness=1, highlightbackground=tema.COLOR_ACENTO_ORO,
        )
        hero.pack(fill="x", padx=tema.PAD_PAGINA_X * 2, pady=(24, 18))

        tk.Label(
            hero, text="Presentación Final",
            font=tema.FUENTE_PORTADA,
            bg=tema.COLOR_FONDO_OSCURO, fg=tema.COLOR_TEXTO_CLARO,
        ).pack(pady=(28, 8))
        tk.Label(
            hero, text=SUBTITULO_PORTADA,
            font=tema.FUENTE_SUBTITULO,
            bg=tema.COLOR_FONDO_OSCURO, fg="#C9B98D",
        ).pack(pady=(0, 22))

        # Tarjeta del equipo
        tarjeta = tk.Frame(
            hero, bg="#1E1410",
            highlightthickness=1, highlightbackground=tema.COLOR_ACENTO_ORO,
        )
        tarjeta.pack(padx=80, pady=(0, 30))

        tk.Label(
            tarjeta, text="Integrantes del Equipo",
            font=(tema.FAMILIA_SERIF_DECORATIVA, 14, "bold"),
            bg="#1E1410", fg="#E8DFC6",
        ).pack(pady=(16, 12), padx=42)

        rejilla = tk.Frame(tarjeta, bg="#1E1410")
        rejilla.pack(padx=30, pady=(0, 20))

        tk.Label(
            rejilla, text="Nombre", font=(tema.FAMILIA_SERIF, 11, "bold"),
            bg="#1E1410", fg="#A8997C",
        ).grid(row=0, column=0, sticky="w", padx=(0, 32), pady=(0, 6))
        tk.Label(
            rejilla, text="Matrícula", font=(tema.FAMILIA_SERIF, 11, "bold"),
            bg="#1E1410", fg="#A8997C",
        ).grid(row=0, column=1, sticky="w", pady=(0, 6))

        for i, (nombre, matricula) in enumerate(INTEGRANTES, start=1):
            tk.Label(
                rejilla, text=nombre, font=(tema.FAMILIA_SERIF, 12),
                bg="#1E1410", fg=tema.COLOR_TEXTO_CLARO,
            ).grid(row=i, column=0, sticky="w", padx=(0, 32), pady=4)
            tk.Label(
                rejilla, text=matricula, font=tema.FUENTE_ENTRADA,
                bg="#1E1410", fg=tema.COLOR_TEXTO_CLARO,
            ).grid(row=i, column=1, sticky="w", pady=4)

        # Acciones principales
        acciones = tk.Frame(cont, bg=tema.COLOR_FONDO_OSCURO)
        acciones.pack(pady=(8, 20))

        widgets.BotonClasico(
            acciones, "Acceder al índice de temas",
            comando=self._mostrar_indice, tipo="principal", ancho=28,
        ).pack(side="left", padx=8)
        widgets.BotonClasico(
            acciones, "Salir",
            comando=self.root.quit, tipo="peligro", ancho=12,
        ).pack(side="left", padx=8)

        tk.Label(
            cont, text="F11 alterna pantalla completa · use la rueda del ratón para desplazarse.",
            font=tema.FUENTE_PEQUENA_IT,
            bg=tema.COLOR_FONDO_OSCURO, fg="#9B8B70",
        ).pack(pady=(0, 24))

    # ============================================================
    #  Índice de temas (menú principal)
    # ============================================================

    def _mostrar_indice(self):
        self._limpiar_root()
        self.metodo_activo = ""
        self.root.configure(bg=tema.COLOR_FONDO)

        marco = widgets.MarcoConScroll(self.root, bg=tema.COLOR_FONDO)
        marco.pack(fill="both", expand=True)
        cont = marco.interior

        self._agregar_encabezado(cont, tema.COLOR_FONDO, tema.COLOR_TITULO)

        tk.Label(
            cont, text="Índice de Temas",
            font=tema.FUENTE_TITULO,
            bg=tema.COLOR_FONDO, fg=tema.COLOR_TITULO,
        ).pack(pady=(12, 4))
        tk.Label(
            cont,
            text="Seleccione un método para abrir su presentación.",
            font=tema.FUENTE_SUBTITULO,
            bg=tema.COLOR_FONDO, fg=tema.COLOR_TEXTO_SUAVE,
        ).pack(pady=(0, 16))

        tarjetas = tk.Frame(cont, bg=tema.COLOR_FONDO)
        tarjetas.pack(fill="x", padx=tema.PAD_PAGINA_X, pady=(0, 16))

        for idx, (titulo, metodos) in enumerate(GRUPOS_TEMARIO):
            fila, col = divmod(idx, 2)
            tarj = widgets.Tarjeta(tarjetas)
            tarj.grid(row=fila, column=col, sticky="nsew", padx=10, pady=10)

            tk.Label(
                tarj, text=titulo,
                font=(tema.FAMILIA_SERIF_DECORATIVA, 14, "bold"),
                bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_TITULO,
            ).pack(anchor="w", padx=18, pady=(14, 4))
            tk.Label(
                tarj,
                text="Métodos disponibles en este bloque:",
                font=tema.FUENTE_PEQUENA_IT,
                bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_TEXTO_SUAVE,
            ).pack(anchor="w", padx=18, pady=(0, 10))

            zona_btn = tk.Frame(tarj, bg=tema.COLOR_FONDO_TARJETA)
            zona_btn.pack(fill="x", padx=18, pady=(0, 16))
            for m in metodos:
                widgets.BotonClasico(
                    zona_btn, m,
                    comando=lambda met=m: self._mostrar_pagina(met, "portada"),
                    tipo="principal",
                ).pack(fill="x", pady=3)

        tarjetas.grid_columnconfigure(0, weight=1, uniform="cols")
        tarjetas.grid_columnconfigure(1, weight=1, uniform="cols")

        pie = tk.Frame(cont, bg=tema.COLOR_FONDO)
        pie.pack(fill="x", padx=tema.PAD_PAGINA_X, pady=(8, 22))
        widgets.BotonClasico(
            pie, "← Volver a la portada",
            comando=self._mostrar_portada, tipo="neutro", ancho=22,
        ).pack(side="left")
        widgets.BotonClasico(
            pie, "Salir",
            comando=self.root.quit, tipo="peligro", ancho=12,
        ).pack(side="right")

    # ============================================================
    #  Páginas del método (portada, capítulo, tema, fórmulas)
    # ============================================================

    SECUENCIA_PAGINAS = ["portada", "capitulo", "tema", "formulas"]

    def _mostrar_pagina(self, metodo: str, pagina: str):
        if metodo not in METODOS:
            return
        self.metodo_activo = metodo
        self._limpiar_root()
        self.root.configure(bg=tema.COLOR_FONDO)

        cfg = METODOS[metodo]
        marco = widgets.MarcoConScroll(self.root, bg=tema.COLOR_FONDO)
        marco.pack(fill="both", expand=True)
        cont = marco.interior

        self._agregar_encabezado(cont, tema.COLOR_FONDO, tema.COLOR_TITULO)

        # Título del método
        tk.Label(
            cont, text=cfg["nombre"],
            font=tema.FUENTE_TITULO,
            bg=tema.COLOR_FONDO, fg=tema.COLOR_TITULO,
        ).pack(pady=(10, 4))
        tk.Label(
            cont, text=cfg["capitulo"],
            font=tema.FUENTE_SUBTITULO,
            bg=tema.COLOR_FONDO, fg=tema.COLOR_TEXTO_SUAVE,
        ).pack(pady=(0, 16))

        # Tarjeta de contenido
        tarjeta = widgets.Tarjeta(cont)
        tarjeta.pack(fill="x", padx=tema.PAD_PAGINA_X, pady=(0, 12))

        encabezado_pagina = {
            "portada":  "Portada del Método",
            "capitulo": "Capítulo / Tema",
            "tema":     "¿Qué resuelve y dónde se aplica?",
            "formulas": "Fórmulas y expresiones clave",
        }
        tk.Label(
            tarjeta, text=encabezado_pagina.get(pagina, pagina.title()),
            font=tema.FUENTE_SECCION,
            bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_ACENTO_ORO,
        ).pack(anchor="w", padx=tema.PAD_CARD_X, pady=(tema.PAD_CARD_Y, 4))
        widgets.Separador(tarjeta).pack(fill="x", padx=tema.PAD_CARD_X, pady=(0, 10))

        if pagina == "portada":
            contenido = (
                f"{cfg['nombre']}\n\n"
                "Programa — Métodos Numéricos\n"
                "Facultad de Ingeniería · Universidad Autónoma de Chihuahua\n\n"
                "Integrantes del equipo:\n"
                + "\n".join(f"  · {n}    {mat}" for n, mat in INTEGRANTES)
            )
        elif pagina == "capitulo":
            contenido = f"{cfg['capitulo']}\n\nTema: {cfg['nombre']}"
        else:
            contenido = cfg.get(pagina, "")

        texto = scrolledtext.ScrolledText(
            tarjeta,
            font=tema.FUENTE_TEXTO_LARGO,
            bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_TEXTO,
            wrap="word", relief="flat", bd=0,
            padx=14, pady=8, height=14,
        )
        texto.insert("end", contenido)
        texto.configure(state="disabled")
        texto.pack(fill="x", padx=tema.PAD_CARD_X, pady=(0, tema.PAD_CARD_Y))

        # Navegación entre páginas
        nav = tk.Frame(cont, bg=tema.COLOR_FONDO)
        nav.pack(pady=12)

        widgets.BotonClasico(
            nav, "← Índice", comando=self._mostrar_indice, tipo="neutro",
        ).pack(side="left", padx=4)

        idx = self.SECUENCIA_PAGINAS.index(pagina)
        if idx > 0:
            prev_pag = self.SECUENCIA_PAGINAS[idx - 1]
            widgets.BotonClasico(
                nav, "← Anterior",
                comando=lambda: self._mostrar_pagina(metodo, prev_pag),
                tipo="neutro",
            ).pack(side="left", padx=4)
        if idx < len(self.SECUENCIA_PAGINAS) - 1:
            next_pag = self.SECUENCIA_PAGINAS[idx + 1]
            widgets.BotonClasico(
                nav, "Siguiente →",
                comando=lambda: self._mostrar_pagina(metodo, next_pag),
                tipo="principal",
            ).pack(side="left", padx=4)
        else:
            widgets.BotonClasico(
                nav, "Ir al programa ▸",
                comando=self._ir_al_programa,
                tipo="exito",
            ).pack(side="left", padx=4)

    def _ir_al_programa(self):
        if self.metodo_activo not in METODOS:
            return
        tipo = METODOS[self.metodo_activo]["tipo"]
        despachador = {
            "raices":        self._calc_raices,
            "ssel":          self._calc_ssel,
            "iterativo":     self._calc_iterativo,
            "interpolacion": self._calc_interpolacion,
            "integracion":   self._calc_integracion,
            "ajuste":        self._calc_ajuste,
        }
        fn = despachador.get(tipo)
        if fn is None:
            messagebox.showinfo("Aviso", "No hay calculadora configurada para este método.")
            return
        fn()

    # ============================================================
    #  Andamiaje base para calculadoras
    # ============================================================

    def _construir_esqueleto_calculadora(
        self, titulo: str, tipo_ejemplo: str,
        descripcion_corta: str | None = None,
    ):
        """Construye el esqueleto común de cualquier calculadora.

        Devuelve (cont, content_card) donde:
          - cont: marco scrolleable (su .interior es el destino real)
          - content_card: tarjeta interior donde se agregan los campos

        El esqueleto incluye:
          - Encabezado institucional
          - Selector de subtema (Combobox) — permite cambiar de método sin
            volver al menú
          - Barra de acciones (fórmulas, ejemplo, resultados, índice, salir)
          - Tarjeta de "Datos de entrada"
        """
        self._limpiar_root()
        self.root.configure(bg=tema.COLOR_FONDO)

        marco = widgets.MarcoConScroll(self.root, bg=tema.COLOR_FONDO)
        marco.pack(fill="both", expand=True)
        cont = marco.interior

        self._agregar_encabezado(cont, tema.COLOR_FONDO, tema.COLOR_TITULO)

        # Título de la calculadora
        tk.Label(
            cont, text=titulo, font=tema.FUENTE_TITULO,
            bg=tema.COLOR_FONDO, fg=tema.COLOR_TITULO,
        ).pack(pady=(8, 2))
        if descripcion_corta:
            tk.Label(
                cont, text=descripcion_corta,
                font=tema.FUENTE_SUBTITULO,
                bg=tema.COLOR_FONDO, fg=tema.COLOR_TEXTO_SUAVE,
            ).pack(pady=(0, 10))

        # Selector de subtema dentro de la calculadora
        self._agregar_selector_subtema(cont)

        # Barra de acciones (índice, fórmulas, ejemplo, resultados, salir)
        acciones = [
            {"texto": "← Índice de temas", "comando": self._mostrar_indice, "tipo": "neutro"},
            {"texto": "Ver fórmulas",
             "comando": lambda: self._abrir_ventana_info(
                 f"Fórmulas · {titulo}",
                 METODOS.get(self.metodo_activo, {}).get("formulas", "")),
             "tipo": "informacion"},
            {"texto": "Ver ejemplo",
             "comando": lambda: self._abrir_ventana_info(
                 f"Ejemplo · {titulo}",
                 EJEMPLOS.get(tipo_ejemplo, "Sin ejemplo configurado.")),
             "tipo": "informacion"},
            {"texto": "Ventana de resultados",
             "comando": lambda: self._abrir_ventana_resultados(f"Resultados · {titulo}"),
             "tipo": "principal"},
            {"texto": "Salir", "comando": self.root.quit, "tipo": "peligro"},
        ]
        barra = widgets.BarraDeAcciones(cont, acciones, bg=tema.COLOR_FONDO,
                                         columnas_max=5)
        barra.pack(fill="x", padx=tema.PAD_PAGINA_X, pady=(6, 12))

        # Tarjeta con datos de entrada
        marco_tarjeta = tk.Frame(cont, bg=tema.COLOR_FONDO)
        marco_tarjeta.pack(fill="both", expand=True,
                           padx=tema.PAD_PAGINA_X, pady=(0, 18))

        tarjeta = widgets.Tarjeta(marco_tarjeta)
        tarjeta.pack(fill="both", expand=True)

        tk.Label(
            tarjeta, text="Datos de entrada", font=tema.FUENTE_SECCION,
            bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_ACENTO_ORO,
        ).pack(anchor="w", padx=tema.PAD_CARD_X, pady=(tema.PAD_CARD_Y, 4))
        widgets.Separador(tarjeta).pack(fill="x", padx=tema.PAD_CARD_X, pady=(0, 10))

        content = tk.Frame(tarjeta, bg=tema.COLOR_FONDO_TARJETA)
        content.pack(fill="both", expand=True,
                     padx=tema.PAD_CARD_X, pady=(0, tema.PAD_CARD_Y))

        return marco, content

    def _agregar_selector_subtema(self, padre):
        """Muestra un combobox para saltar a otra calculadora directamente."""
        if self.metodo_activo not in METODOS:
            return

        tipo = METODOS[self.metodo_activo]["tipo"]
        subtemas_propios = SUBTEMAS_POR_TIPO.get(tipo, [])

        # Lista completa de métodos disponibles
        todos = [m for _, lista in GRUPOS_TEMARIO for m in lista if m in METODOS]

        contenedor = tk.Frame(padre, bg=tema.COLOR_FONDO)
        contenedor.pack(fill="x", padx=tema.PAD_PAGINA_X, pady=(0, 4))

        izq = tk.Frame(contenedor, bg=tema.COLOR_FONDO)
        izq.pack(side="left", fill="x", expand=True)

        # Selector de subtema del mismo bloque
        if len(subtemas_propios) > 1:
            tk.Label(
                izq, text="Cambiar subtema:",
                font=tema.FUENTE_ETIQUETA_B,
                bg=tema.COLOR_FONDO, fg=tema.COLOR_TEXTO_SUAVE,
            ).pack(side="left", padx=(0, 8))

            var_sub = tk.StringVar(value=self.metodo_activo
                                   if self.metodo_activo in subtemas_propios
                                   else subtemas_propios[0])
            combo = ttk.Combobox(
                izq, textvariable=var_sub, values=subtemas_propios,
                state="readonly", width=22, style="Clasico.TCombobox",
            )
            combo.pack(side="left", padx=(0, 16))

            def _cambiar_subtema(_e=None):
                nuevo = var_sub.get()
                if nuevo != self.metodo_activo and nuevo in METODOS:
                    self.metodo_activo = nuevo
                    self._ir_al_programa()
            combo.bind("<<ComboboxSelected>>", _cambiar_subtema)

        # Selector global para saltar a cualquier otro tema
        tk.Label(
            izq, text="Ir a otro tema:",
            font=tema.FUENTE_ETIQUETA_B,
            bg=tema.COLOR_FONDO, fg=tema.COLOR_TEXTO_SUAVE,
        ).pack(side="left", padx=(0, 8))

        var_global = tk.StringVar(value=self.metodo_activo)
        combo_g = ttk.Combobox(
            izq, textvariable=var_global, values=todos,
            state="readonly", width=28, style="Clasico.TCombobox",
        )
        combo_g.pack(side="left")

        def _cambiar_global(_e=None):
            nuevo = var_global.get()
            if nuevo != self.metodo_activo and nuevo in METODOS:
                self.metodo_activo = nuevo
                self._ir_al_programa()
        combo_g.bind("<<ComboboxSelected>>", _cambiar_global)

    # ----- Ventanas de información / resultados ------------------------------

    def _abrir_ventana_resultados(self, titulo="Resultados"):
        """Reutiliza una única ventana de resultados (consola oscura)."""
        if self._ventana_resultados and self._ventana_resultados.winfo_exists():
            self._ventana_resultados.title(titulo)
            self._texto_resultados.configure(state="normal")
            self._texto_resultados.delete("1.0", "end")
            try:
                self._ventana_resultados.lift()
                self._ventana_resultados.focus_force()
            except tk.TclError:
                pass
            return self._texto_resultados

        win = tk.Toplevel(self.root)
        win.title(titulo)
        win.geometry("1000x620")
        win.configure(bg=tema.COLOR_FONDO)

        cabecera = tk.Frame(win, bg=tema.COLOR_FONDO)
        cabecera.pack(fill="x", padx=tema.PAD_PAGINA_X, pady=(14, 6))
        tk.Label(
            cabecera, text=titulo, font=tema.FUENTE_TITULO,
            bg=tema.COLOR_FONDO, fg=tema.COLOR_TITULO,
        ).pack(side="left")

        barra = tk.Frame(win, bg=tema.COLOR_FONDO)
        barra.pack(fill="x", padx=tema.PAD_PAGINA_X, pady=(0, 8))
        widgets.BotonClasico(
            barra, "Limpiar consola",
            comando=lambda: texto.delete("1.0", "end"),
            tipo="neutro",
        ).pack(side="left", padx=4)
        widgets.BotonClasico(
            barra, "Cerrar",
            comando=win.destroy, tipo="peligro",
        ).pack(side="right", padx=4)

        texto = scrolledtext.ScrolledText(
            win, font=tema.FUENTE_CONSOLA,
            bg=tema.COLOR_FONDO_RESULTADO, fg=tema.COLOR_TEXTO_RESULT,
            insertbackground=tema.COLOR_TEXTO_CLARO,
            wrap="word", relief="flat", bd=0, padx=14, pady=10,
        )
        texto.pack(fill="both", expand=True,
                   padx=tema.PAD_PAGINA_X, pady=(0, 14))

        def _cerrar():
            win.destroy()
            self._ventana_resultados = None
            self._texto_resultados = None

        win.protocol("WM_DELETE_WINDOW", _cerrar)
        self._ventana_resultados = win
        self._texto_resultados = texto
        return texto

    def _abrir_ventana_info(self, titulo: str, cuerpo: str):
        win = tk.Toplevel(self.root)
        win.title(titulo)
        win.geometry("780x580")
        win.configure(bg=tema.COLOR_FONDO)

        tk.Label(
            win, text=titulo, font=tema.FUENTE_TITULO,
            bg=tema.COLOR_FONDO, fg=tema.COLOR_TITULO,
        ).pack(pady=(14, 4), padx=tema.PAD_PAGINA_X, anchor="w")
        widgets.Separador(win).pack(
            fill="x", padx=tema.PAD_PAGINA_X, pady=(0, 10),
        )

        texto = scrolledtext.ScrolledText(
            win, font=tema.FUENTE_TEXTO_LARGO,
            bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_TEXTO,
            wrap="word", relief="flat", bd=0, padx=14, pady=10,
        )
        texto.insert("end", cuerpo)
        texto.configure(state="disabled")
        texto.pack(fill="both", expand=True,
                   padx=tema.PAD_PAGINA_X, pady=(0, 10))

        widgets.BotonClasico(
            win, "Cerrar", comando=win.destroy, tipo="neutro", ancho=14,
        ).pack(pady=(0, 16))

    # ============================================================
    #  Utilidades de parsing
    # ============================================================

    def _parsear_puntos(self, raw: str):
        puntos = []
        for n, linea in enumerate(raw.strip().splitlines(), start=1):
            if not linea.strip():
                continue
            partes = [p for p in linea.replace(",", " ").split() if p]
            if len(partes) != 2:
                raise ValueError(f"Línea {n}: se esperaban 2 valores 'x y' → '{linea}'")
            try:
                puntos.append((float(partes[0]), float(partes[1])))
            except ValueError as exc:
                raise ValueError(f"Línea {n}: '{linea}' no es numérica") from exc
        if len(puntos) < 2:
            raise ValueError("Se requieren al menos 2 puntos.")
        return puntos

    # ============================================================
    #  Calculadora · Raíces
    # ============================================================

    def _calc_raices(self):
        _, contenido = self._construir_esqueleto_calculadora(
            "Calculadora · Raíces de Ecuaciones",
            tipo_ejemplo="raices",
            descripcion_corta="Bisección · Falsa Posición · Newton-Raphson",
        )

        self.r_metodo.set(
            self.metodo_activo
            if self.metodo_activo in ("Bisección", "Falsa Posición", "Newton-Raphson")
            else "Bisección"
        )

        # Fila 1 – Método
        fila1 = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        fila1.pack(anchor="w", fill="x", pady=(4, 8))
        tk.Label(fila1, text="Método:", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA_B,
                 fg=tema.COLOR_TEXTO).pack(side="left", padx=(0, 10))
        for m in ("Bisección", "Falsa Posición", "Newton-Raphson"):
            tk.Radiobutton(
                fila1, text=m, value=m, variable=self.r_metodo,
                bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_TEXTO,
                font=tema.FUENTE_ETIQUETA, activebackground=tema.COLOR_FONDO_TARJETA,
                selectcolor=tema.COLOR_FONDO_INPUT,
            ).pack(side="left", padx=8)

        # Fila 2 – Función
        fila2 = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        fila2.pack(anchor="w", fill="x", pady=4)
        tk.Label(fila2, text="Función f(x):", bg=tema.COLOR_FONDO_TARJETA,
                 width=14, anchor="w",
                 font=tema.FUENTE_ETIQUETA).pack(side="left")
        tk.Entry(fila2, textvariable=self.r_expr, width=46,
                 font=tema.FUENTE_ENTRADA,
                 bg=tema.COLOR_FONDO_INPUT).pack(side="left", padx=6, fill="x", expand=True)

        # Fila 3 – Parámetros
        params = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        params.pack(anchor="w", pady=10, fill="x")

        def _agregar_campo(parent, etiqueta, var, fila, col, ancho=11):
            tk.Label(parent, text=etiqueta, bg=tema.COLOR_FONDO_TARJETA,
                     font=tema.FUENTE_ETIQUETA, anchor="w",
                     ).grid(row=fila, column=col * 2, sticky="w",
                            padx=(0, 6), pady=4)
            tk.Entry(parent, textvariable=var, width=ancho,
                     font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT,
                     ).grid(row=fila, column=col * 2 + 1, sticky="w",
                            padx=(0, 22), pady=4)

        _agregar_campo(params, "a:",                self.r_a,    0, 0, 12)
        _agregar_campo(params, "b:",                self.r_b,    0, 1, 12)
        _agregar_campo(params, "x₀ (Newton):",      self.r_x0,   0, 2, 12)
        _agregar_campo(params, "Tolerancia:",       self.r_tol,  1, 0, 12)
        _agregar_campo(params, "Iteraciones máx.:", self.r_iter, 1, 1, 12)
        _agregar_campo(params, "Decimales:",        self.r_dec,  1, 2, 12)

        tk.Checkbutton(
            contenido, text="Trigonometría en grados",
            variable=self.r_grados,
            bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_TEXTO,
            font=tema.FUENTE_ETIQUETA,
            activebackground=tema.COLOR_FONDO_TARJETA,
            selectcolor=tema.COLOR_FONDO_INPUT,
        ).pack(anchor="w", pady=(4, 10))

        botonera = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        botonera.pack(anchor="w", pady=(4, 4))
        widgets.BotonClasico(
            botonera, "Calcular", comando=self._raices_calcular,
            tipo="exito", ancho=14,
        ).pack(side="left", padx=4)
        widgets.BotonClasico(
            botonera, "Cargar ejemplo", comando=self._raices_ejemplo,
            tipo="informacion",
        ).pack(side="left", padx=4)
        widgets.BotonClasico(
            botonera, "Limpiar campos", comando=self._raices_limpiar,
            tipo="neutro",
        ).pack(side="left", padx=4)

        tk.Label(
            contenido,
            text="Los resultados aparecen en una ventana aparte para mantener limpia la zona de datos.",
            font=tema.FUENTE_PEQUENA_IT,
            bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_TEXTO_SUAVE,
        ).pack(anchor="w", pady=(6, 0))

    def _raices_ejemplo(self):
        self.r_expr.set("x**3 - 2*x - 5")
        self.r_a.set("2"); self.r_b.set("3"); self.r_x0.set("2")
        self.r_tol.set("1e-6"); self.r_iter.set("50"); self.r_dec.set("6")
        self.r_grados.set(False)
        messagebox.showinfo("Ejemplo cargado",
                            "Datos del ejemplo cargados. Pulse 'Calcular' para ver el procedimiento.")

    def _raices_limpiar(self):
        for v in (self.r_expr, self.r_a, self.r_b, self.r_x0,
                  self.r_tol, self.r_iter, self.r_dec):
            v.set("")
        self.r_grados.set(False)

    def _raices_calcular(self):
        if biseccion is None:
            messagebox.showerror("Error", "No se encontró el módulo de raíces.")
            return
        metodo = self.r_metodo.get()
        expr = self.r_expr.get().strip()
        try:
            a = float(self.r_a.get())
            b = float(self.r_b.get())
            x0 = float(self.r_x0.get())
            tol = float(self.r_tol.get())
            it = int(self.r_iter.get())
            dec = int(self.r_dec.get())
        except ValueError as e:
            messagebox.showerror("Error", f"Parámetros inválidos: {e}")
            return

        env = construir_entorno_matematico(
            obtener_entorno_trig(self.r_grados.get())
            if obtener_entorno_trig else None
        )

        def f(x):
            local = dict(env)
            local["x"] = x
            return evaluar_expresion(expr, local)

        texto = self._abrir_ventana_resultados(f"Resultados · {metodo}")
        texto.insert("end", f"Método: {metodo}\n")
        texto.insert("end", f"f(x) = {expr}\n")
        texto.insert("end", f"Decimales: {dec}\n")
        texto.insert("end", "─" * 72 + "\n\n")

        def log(linea):
            texto.insert("end", str(linea) + "\n")
            texto.see("end")

        try:
            if metodo == "Bisección":
                biseccion(f, a, b, tol, it, "D", dec, logger=log)
            elif metodo == "Falsa Posición":
                falsa_posicion(f, a, b, tol, it, "D", dec, logger=log)
            else:
                newton_raphson(f, None, x0, tol, it, "D", dec, logger=log)
        except (ValueError, ArithmeticError, OverflowError, ZeroDivisionError) as exc:
            messagebox.showerror("Error", f"Cálculo falló: {exc}")

    # ============================================================
    #  Calculadora · SSEL exactos
    # ============================================================

    def _calc_ssel(self):
        _, contenido = self._construir_esqueleto_calculadora(
            "Calculadora · SSEL Exactos",
            tipo_ejemplo="ssel",
            descripcion_corta="Eliminación Gaussiana · Gauss-Jordan · Inversa · Cramer",
        )

        mapa_inicial = {"Gauss": "gauss", "Gauss-Jordan": "gauss_jordan",
                        "Inversa": "inversa", "Cramer": "cramer"}
        self.s_metodo.set(mapa_inicial.get(self.metodo_activo, "gauss"))
        self.s_tam.set("3")
        self.s_dec.set("6")

        params = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        params.pack(anchor="w", fill="x", pady=(4, 8))

        tk.Label(params, text="Método:", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA_B).grid(row=0, column=0, sticky="w",
                                                    padx=(0, 8), pady=(0, 4))
        for col, (lbl, val) in enumerate([
            ("Gauss", "gauss"), ("Gauss-Jordan", "gauss_jordan"),
            ("Inversa", "inversa"), ("Cramer", "cramer"),
        ], start=1):
            tk.Radiobutton(
                params, text=lbl, value=val, variable=self.s_metodo,
                bg=tema.COLOR_FONDO_TARJETA, font=tema.FUENTE_ETIQUETA,
                activebackground=tema.COLOR_FONDO_TARJETA,
                selectcolor=tema.COLOR_FONDO_INPUT, fg=tema.COLOR_TEXTO,
            ).grid(row=0, column=col, sticky="w", padx=6, pady=(0, 4))

        tk.Label(params, text="Tamaño (n):", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA).grid(row=1, column=0, sticky="w", pady=6)
        tk.Spinbox(params, from_=2, to=8, textvariable=self.s_tam,
                   width=5, font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT,
                   ).grid(row=1, column=1, sticky="w", padx=4, pady=6)
        tk.Label(params, text="Decimales:", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA).grid(row=1, column=2, sticky="w",
                                                  padx=(20, 4), pady=6)
        tk.Spinbox(params, from_=2, to=12, textvariable=self.s_dec,
                   width=5, font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT,
                   ).grid(row=1, column=3, sticky="w", padx=4, pady=6)

        widgets.BotonClasico(
            params, "Generar matriz", comando=self._ssel_generar_matriz,
            tipo="principal",
        ).grid(row=1, column=4, padx=(20, 4), pady=6)
        widgets.BotonClasico(
            params, "Cargar ejemplo", comando=self._ssel_ejemplo,
            tipo="informacion",
        ).grid(row=1, column=5, padx=4, pady=6)

        tk.Label(
            contenido,
            text="Introduzca los coeficientes de la matriz aumentada [ A | b ]. "
                 "La última columna corresponde al vector de términos independientes.",
            font=tema.FUENTE_PEQUENA_IT,
            bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_TEXTO_SUAVE,
        ).pack(anchor="w", pady=(4, 4))

        self.s_frame_matriz = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        self.s_frame_matriz.pack(anchor="w", pady=4)

        botonera = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        botonera.pack(anchor="w", pady=(8, 4))
        widgets.BotonClasico(
            botonera, "Calcular", comando=self._ssel_calcular,
            tipo="exito", ancho=14,
        ).pack(side="left", padx=4)
        widgets.BotonClasico(
            botonera, "Limpiar matriz", comando=self._ssel_limpiar,
            tipo="neutro",
        ).pack(side="left", padx=4)

        self._ssel_generar_matriz()

    def _ssel_generar_matriz(self):
        try:
            n = int(self.s_tam.get())
            if not 2 <= n <= 8:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El tamaño debe ser un entero entre 2 y 8.")
            return
        for w in self.s_frame_matriz.winfo_children():
            w.destroy()

        self.s_entradas = []
        for i in range(n):
            fila_ent = []
            tk.Label(self.s_frame_matriz, text=f"F{i+1}",
                     bg=tema.COLOR_FONDO_TARJETA, font=tema.FUENTE_ETIQUETA,
                     fg=tema.COLOR_TEXTO_SUAVE
                     ).grid(row=i, column=0, padx=(0, 8), pady=2)
            for j in range(n):
                e = tk.Entry(self.s_frame_matriz, width=8, justify="right",
                             font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT,
                             relief="solid", bd=1,
                             highlightthickness=0)
                e.grid(row=i, column=j + 1, padx=2, pady=2)
                fila_ent.append(e)
            tk.Label(self.s_frame_matriz, text="│",
                     bg=tema.COLOR_FONDO_TARJETA, font=tema.FUENTE_ETIQUETA,
                     fg=tema.COLOR_ACENTO_ORO
                     ).grid(row=i, column=n + 1, padx=4)
            eb = tk.Entry(self.s_frame_matriz, width=8, justify="right",
                          font=tema.FUENTE_ENTRADA, bg="#FFF7E6",
                          relief="solid", bd=1, highlightthickness=0)
            eb.grid(row=i, column=n + 2, padx=2, pady=2)
            fila_ent.append(eb)
            self.s_entradas.append(fila_ent)

    def _ssel_ejemplo(self):
        self.s_tam.set("3")
        self._ssel_generar_matriz()
        valores = [[2, 1, -1, 8], [-3, -1, 2, -11], [-2, 1, 2, -3]]
        for i, fila in enumerate(valores):
            for j, val in enumerate(fila):
                self.s_entradas[i][j].delete(0, "end")
                self.s_entradas[i][j].insert(0, str(val))

    def _ssel_limpiar(self):
        for fila in self.s_entradas:
            for e in fila:
                e.delete(0, "end")

    def _ssel_calcular(self):
        if gauss is None:
            messagebox.showerror("Error", "No se encontró el módulo SSEL.")
            return
        try:
            dec = int(self.s_dec.get())
        except ValueError:
            messagebox.showerror("Error", "Decimales inválidos.")
            return
        matriz = []
        for i, fila in enumerate(self.s_entradas):
            vals = []
            for j, e in enumerate(fila):
                t = e.get().strip()
                try:
                    vals.append(float(t) if t else 0.0)
                except ValueError:
                    messagebox.showerror(
                        "Error",
                        f"Valor inválido en F{i+1}, columna {j+1}: '{t}'",
                    )
                    return
            matriz.append(vals)

        metodo = self.s_metodo.get()
        nombres = {"gauss": "Eliminación Gaussiana",
                   "gauss_jordan": "Gauss-Jordan",
                   "inversa": "Inversa de Matriz", "cramer": "Cramer"}
        texto = self._abrir_ventana_resultados(f"Resultados · {nombres.get(metodo, metodo)}")

        def log(linea):
            texto.insert("end", str(linea) + "\n")
            texto.see("end")

        try:
            if metodo == "gauss":
                gauss(matriz, dec, "D", log)
            elif metodo == "gauss_jordan":
                gauss_jordan(matriz, dec, "D", log)
            elif metodo == "inversa":
                inversa_matriz(matriz, dec, "D", log)
            else:
                cramer(matriz, dec, "D", log)
        except (ValueError, ArithmeticError, OverflowError, ZeroDivisionError) as exc:
            messagebox.showerror("Error", f"Cálculo falló: {exc}")

    # ============================================================
    #  Calculadora · Iterativo (Gauss-Seidel)
    # ============================================================

    def _calc_iterativo(self):
        _, contenido = self._construir_esqueleto_calculadora(
            "Calculadora · Gauss-Seidel (Iterativo)",
            tipo_ejemplo="iterativo",
            descripcion_corta="Método iterativo con relajaciones por residuos",
        )

        self.i_tam = tk.StringVar(value="3")
        self.i_tol = tk.StringVar(value="0.01")
        self.i_iter = tk.StringVar(value="50")

        params = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        params.pack(anchor="w", fill="x", pady=(4, 8))

        tk.Label(params, text="Tamaño (n):", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA).grid(row=0, column=0, sticky="w")
        tk.Spinbox(params, from_=2, to=8, textvariable=self.i_tam,
                   width=5, font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT
                   ).grid(row=0, column=1, sticky="w", padx=4)
        tk.Label(params, text="Tolerancia:", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA).grid(row=0, column=2, sticky="w", padx=(20, 4))
        tk.Entry(params, textvariable=self.i_tol, width=10,
                 font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT
                 ).grid(row=0, column=3, sticky="w", padx=4)
        tk.Label(params, text="Iteraciones máx.:", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA).grid(row=0, column=4, sticky="w", padx=(20, 4))
        tk.Entry(params, textvariable=self.i_iter, width=8,
                 font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT
                 ).grid(row=0, column=5, sticky="w", padx=4)

        widgets.BotonClasico(
            params, "Generar matriz", comando=self._iter_generar_matriz,
            tipo="principal",
        ).grid(row=0, column=6, padx=(20, 4))
        widgets.BotonClasico(
            params, "Cargar ejemplo", comando=self._iter_ejemplo,
            tipo="informacion",
        ).grid(row=0, column=7, padx=4)

        tk.Label(
            contenido,
            text="Introduzca los coeficientes de [ A | b ]. Se recomienda una matriz diagonalmente dominante.",
            font=tema.FUENTE_PEQUENA_IT,
            bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_TEXTO_SUAVE,
        ).pack(anchor="w", pady=(4, 4))

        self.i_frame_matriz = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        self.i_frame_matriz.pack(anchor="w", pady=4)

        botonera = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        botonera.pack(anchor="w", pady=(8, 4))
        widgets.BotonClasico(
            botonera, "Calcular", comando=self._iter_calcular,
            tipo="exito", ancho=14,
        ).pack(side="left", padx=4)
        widgets.BotonClasico(
            botonera, "Limpiar matriz", comando=self._iter_limpiar,
            tipo="neutro",
        ).pack(side="left", padx=4)

        self._iter_generar_matriz()

    def _iter_generar_matriz(self):
        try:
            n = int(self.i_tam.get())
            if not 2 <= n <= 8:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El tamaño debe ser un entero entre 2 y 8.")
            return
        for w in self.i_frame_matriz.winfo_children():
            w.destroy()
        self.i_entradas = []
        for i in range(n):
            fila_ent = []
            tk.Label(self.i_frame_matriz, text=f"F{i+1}",
                     bg=tema.COLOR_FONDO_TARJETA, font=tema.FUENTE_ETIQUETA,
                     fg=tema.COLOR_TEXTO_SUAVE
                     ).grid(row=i, column=0, padx=(0, 8), pady=2)
            for j in range(n):
                e = tk.Entry(self.i_frame_matriz, width=8, justify="right",
                             font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT,
                             relief="solid", bd=1, highlightthickness=0)
                e.grid(row=i, column=j + 1, padx=2, pady=2)
                fila_ent.append(e)
            tk.Label(self.i_frame_matriz, text="│",
                     bg=tema.COLOR_FONDO_TARJETA, font=tema.FUENTE_ETIQUETA,
                     fg=tema.COLOR_ACENTO_ORO
                     ).grid(row=i, column=n + 1, padx=4)
            eb = tk.Entry(self.i_frame_matriz, width=8, justify="right",
                          font=tema.FUENTE_ENTRADA, bg="#FFF7E6",
                          relief="solid", bd=1, highlightthickness=0)
            eb.grid(row=i, column=n + 2, padx=2, pady=2)
            fila_ent.append(eb)
            self.i_entradas.append(fila_ent)

    def _iter_ejemplo(self):
        self.i_tam.set("3")
        self._iter_generar_matriz()
        valores = [[10, -1, 2, 6], [-1, 11, -1, 25], [2, -1, 10, -11]]
        for i, fila in enumerate(valores):
            for j, val in enumerate(fila):
                self.i_entradas[i][j].delete(0, "end")
                self.i_entradas[i][j].insert(0, str(val))

    def _iter_limpiar(self):
        for fila in self.i_entradas:
            for e in fila:
                e.delete(0, "end")

    def _iter_calcular(self):
        if gauss_seidel_hoja is None:
            messagebox.showerror("Error", "No se encontró el módulo de Gauss-Seidel.")
            return
        try:
            tol = float(self.i_tol.get())
            mit = int(self.i_iter.get())
        except ValueError:
            messagebox.showerror("Error", "Tolerancia o iteraciones inválidas.")
            return
        A, b = [], []
        for i, fila in enumerate(self.i_entradas):
            fila_A = []
            for j, e in enumerate(fila[:-1]):
                t = e.get().strip()
                try:
                    fila_A.append(float(t) if t else 0.0)
                except ValueError:
                    messagebox.showerror(
                        "Error",
                        f"Valor inválido en F{i+1}, A[{j+1}]: '{t}'",
                    )
                    return
            t_b = fila[-1].get().strip()
            try:
                b.append(float(t_b) if t_b else 0.0)
            except ValueError:
                messagebox.showerror("Error", f"Valor inválido en b de F{i+1}: '{t_b}'")
                return
            A.append(fila_A)

        texto = self._abrir_ventana_resultados("Resultados · Gauss-Seidel")
        try:
            rep = gauss_seidel_hoja(A, b, tol=tol, max_iter=mit, step_decimals=6)
        except (ValueError, ZeroDivisionError, ArithmeticError) as exc:
            messagebox.showerror("Error", f"Cálculo falló: {exc}")
            return

        texto.insert("end", "Sistema introducido [ A | b ]:\n")
        for i, f in enumerate(A):
            texto.insert("end",
                         "  " + "  ".join(f"{v:>9.4f}" for v in f) +
                         f"  |  {b[i]:>9.4f}\n")
        texto.insert("end", f"\nTolerancia: {tol}    Iteraciones máx.: {mit}\n")
        texto.insert("end", f"Reordenamiento aplicado: {rep['row_order']}\n")
        texto.insert("end", "─" * 60 + "\n")
        texto.insert("end", "Iteración    " +
                     "    ".join(f"x{i+1:<8}" for i in range(rep["n"])) + "\n")
        for k, v in enumerate(rep["values"]):
            texto.insert("end", f"{('V'+str(k)):<12}" +
                         "    ".join(f"{val:<9.6f}" for val in v) + "\n")
        texto.insert("end", "─" * 60 + "\n")
        texto.insert("end", f"Iteraciones realizadas: {rep['iterations']}\n")
        texto.insert("end", f"Convergió: {'Sí' if rep['converged'] else 'No'}\n\n")
        texto.insert("end", "Solución aproximada:\n")
        for i, v in enumerate(rep["x"]):
            texto.insert("end", f"  x{i+1} = {v:.6f}\n")
        texto.see("end")

    # ============================================================
    #  Calculadora · Interpolación
    # ============================================================

    def _calc_interpolacion(self):
        _, contenido = self._construir_esqueleto_calculadora(
            "Calculadora · Interpolación",
            tipo_ejemplo="interpolacion",
            descripcion_corta="Lineal por tramos · Polinomio de Lagrange",
        )

        self.it_metodo = tk.StringVar(value="lineal")
        self.it_x = tk.StringVar(value="2")

        ops = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        ops.pack(anchor="w", fill="x", pady=(4, 8))
        tk.Label(ops, text="Método:", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA_B).pack(side="left", padx=(0, 10))
        for txt, val in (("Lineal", "lineal"), ("Lagrange", "lagrange")):
            tk.Radiobutton(
                ops, text=txt, value=val, variable=self.it_metodo,
                bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_TEXTO,
                font=tema.FUENTE_ETIQUETA,
                activebackground=tema.COLOR_FONDO_TARJETA,
                selectcolor=tema.COLOR_FONDO_INPUT,
            ).pack(side="left", padx=8)

        tk.Label(ops, text="x a estimar:", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA).pack(side="left", padx=(24, 6))
        tk.Entry(ops, textvariable=self.it_x, width=10,
                 font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT).pack(side="left", padx=4)

        tk.Label(
            contenido,
            text="Puntos (uno por línea, formato 'x y' o 'x, y'):",
            font=tema.FUENTE_ETIQUETA,
            bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_TEXTO,
        ).pack(anchor="w", pady=(4, 2))

        self.it_puntos = tk.Text(contenido, height=8, width=44,
                                  font=tema.FUENTE_ENTRADA, bd=1, relief="solid",
                                  bg=tema.COLOR_FONDO_INPUT, fg=tema.COLOR_TEXTO,
                                  highlightthickness=0)
        self.it_puntos.pack(anchor="w", pady=4)
        self.it_puntos.insert("end", "1 2\n3 6\n5 12\n")

        botonera = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        botonera.pack(anchor="w", pady=(8, 4))
        widgets.BotonClasico(
            botonera, "Calcular", comando=self._interp_calcular,
            tipo="exito", ancho=14,
        ).pack(side="left", padx=4)
        widgets.BotonClasico(
            botonera, "Cargar ejemplo", comando=self._interp_ejemplo,
            tipo="informacion",
        ).pack(side="left", padx=4)
        widgets.BotonClasico(
            botonera, "Limpiar", comando=self._interp_limpiar,
            tipo="neutro",
        ).pack(side="left", padx=4)

    def _interp_ejemplo(self):
        self.it_puntos.delete("1.0", "end")
        self.it_puntos.insert("end", "1 2\n3 6\n5 12\n")
        self.it_x.set("2")

    def _interp_limpiar(self):
        self.it_puntos.delete("1.0", "end")
        self.it_x.set("")

    def _interp_calcular(self):
        if interpolacion_lineal_piecewise_y is None:
            messagebox.showerror("Error", "No se encontró el módulo de interpolación.")
            return
        try:
            xt = float(self.it_x.get())
            puntos = self._parsear_puntos(self.it_puntos.get("1.0", "end"))
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))
            return

        metodo = self.it_metodo.get()
        nombre = "Lineal" if metodo == "lineal" else "Lagrange"
        texto = self._abrir_ventana_resultados(f"Resultados · Interpolación {nombre}")
        texto.insert("end", "Puntos:\n")
        for x, y in puntos:
            texto.insert("end", f"  ({x}, {y})\n")
        texto.insert("end", f"\nx solicitado: {xt}\n")
        texto.insert("end", "─" * 60 + "\n")

        try:
            if metodo == "lineal":
                y = interpolacion_lineal_piecewise_y(puntos, xt)
                texto.insert("end", "Interpolación lineal por tramos:\n")
                texto.insert("end", f"  y({xt}) ≈ {y:.6f}\n")
            else:
                y, pasos = interpolacion_lagrange(puntos, xt, verbose=True)
                texto.insert("end", "Polinomio de Lagrange:\n")
                texto.insert("end", pasos + "\n")
                texto.insert("end", f"\nResultado final: y({xt}) ≈ {y:.6f}\n")
        except (ValueError, ZeroDivisionError, ArithmeticError) as exc:
            messagebox.showerror("Error", f"Cálculo falló: {exc}")
        texto.see("end")

    # ============================================================
    #  Calculadora · Integración
    # ============================================================

    def _calc_integracion(self):
        _, contenido = self._construir_esqueleto_calculadora(
            "Calculadora · Integración Definida",
            tipo_ejemplo="integracion",
            descripcion_corta="Trapecio · Simpson 1/3 · Simpson 3/8 · 2/45 · Romberg",
        )

        self.in_expr = tk.StringVar(value="x**2")
        self.in_a = tk.StringVar(value="0")
        self.in_b = tk.StringVar(value="1")
        self.in_n = tk.StringVar(value="4")
        self.in_metodo = tk.StringVar(value="trapecio")

        fila = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        fila.pack(anchor="w", fill="x", pady=4)
        tk.Label(fila, text="Función f(x):", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA, width=14, anchor="w").pack(side="left")
        tk.Entry(fila, textvariable=self.in_expr, width=44,
                 font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT,
                 ).pack(side="left", padx=6, fill="x", expand=True)

        params = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        params.pack(anchor="w", pady=10)
        tk.Label(params, text="a:", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA).grid(row=0, column=0, sticky="w", padx=(0, 4))
        tk.Entry(params, textvariable=self.in_a, width=10,
                 font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT
                 ).grid(row=0, column=1, padx=(0, 18))
        tk.Label(params, text="b:", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA).grid(row=0, column=2, sticky="w", padx=(0, 4))
        tk.Entry(params, textvariable=self.in_b, width=10,
                 font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT
                 ).grid(row=0, column=3, padx=(0, 18))
        tk.Label(params, text="N (subintervalos):", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA).grid(row=0, column=4, sticky="w", padx=(0, 4))
        tk.Entry(params, textvariable=self.in_n, width=10,
                 font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT
                 ).grid(row=0, column=5, padx=(0, 18))

        fila_m = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        fila_m.pack(anchor="w", pady=4, fill="x")
        tk.Label(fila_m, text="Método:", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA_B).pack(side="left", padx=(0, 8))
        for lbl, val in (
            ("Trapecio", "trapecio"),
            ("Simpson 1/3", "simpson13"),
            ("Simpson 3/8", "simpson38"),
            ("Regla 2/45", "regla245"),
            ("Romberg", "romberg"),
        ):
            tk.Radiobutton(
                fila_m, text=lbl, value=val, variable=self.in_metodo,
                bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_TEXTO,
                font=tema.FUENTE_ETIQUETA,
                activebackground=tema.COLOR_FONDO_TARJETA,
                selectcolor=tema.COLOR_FONDO_INPUT,
            ).pack(side="left", padx=6)

        botonera = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        botonera.pack(anchor="w", pady=(10, 4))
        widgets.BotonClasico(
            botonera, "Calcular", comando=self._integ_calcular,
            tipo="exito", ancho=14,
        ).pack(side="left", padx=4)
        widgets.BotonClasico(
            botonera, "Cargar ejemplo", comando=self._integ_ejemplo,
            tipo="informacion",
        ).pack(side="left", padx=4)
        widgets.BotonClasico(
            botonera, "Limpiar", comando=self._integ_limpiar,
            tipo="neutro",
        ).pack(side="left", padx=4)

    def _integ_ejemplo(self):
        self.in_expr.set("x**2"); self.in_a.set("0"); self.in_b.set("1")
        self.in_n.set("4"); self.in_metodo.set("trapecio")

    def _integ_limpiar(self):
        for v in (self.in_expr, self.in_a, self.in_b, self.in_n):
            if v is not None:
                v.set("")

    def _integ_calcular(self):
        if trapezoidal_rule is None:
            messagebox.showerror("Error", "No se encontró el módulo de integración.")
            return
        try:
            a = float(self.in_a.get())
            b = float(self.in_b.get())
            n = int(self.in_n.get())
            expr = self.in_expr.get().strip()
        except ValueError as e:
            messagebox.showerror("Error", f"Parámetros inválidos: {e}")
            return

        env = construir_entorno_matematico()
        try:
            import numpy as _np
            env_np = dict(env)
            env_np.update({
                "sin": _np.sin, "cos": _np.cos, "tan": _np.tan,
                "exp": _np.exp, "log": _np.log, "sqrt": _np.sqrt,
                "abs": _np.abs,
            })
        except ImportError:
            env_np = env

        def f(x):
            local = dict(env_np)
            local["x"] = x
            return evaluar_expresion(expr, local)

        metodo = self.in_metodo.get()
        nombres = {"trapecio": "Trapecio", "simpson13": "Simpson 1/3",
                   "simpson38": "Simpson 3/8", "regla245": "Regla 2/45",
                   "romberg": "Romberg"}
        texto = self._abrir_ventana_resultados(f"Resultados · {nombres.get(metodo, metodo)}")
        texto.insert("end", f"f(x) = {expr}\nIntervalo: [{a}, {b}]\nN = {n}\n"
                            f"Método: {nombres.get(metodo)}\n")
        texto.insert("end", "─" * 60 + "\n")

        try:
            if metodo == "trapecio":
                val = trapezoidal_rule(f, a, b, n)
            elif metodo == "simpson13":
                val = simpson_one_third(f, a, b, n)
            elif metodo == "simpson38":
                val = simpson_three_eighths(f, a, b, n)
            elif metodo == "regla245":
                val = newton_cotes(f, a, b, n, 4)
            else:
                R, val = richardson_extrapolation(f, a, b, max(1, n // 4 or 1), 4)
                texto.insert("end", "\nTabla de Romberg:\n")
                for k, fila in enumerate(R):
                    texto.insert("end", f"  k={k}: " +
                                 "   ".join(f"{v:>12.8f}" for v in fila[:k + 1]) + "\n")
                texto.insert("end", "\n")
            texto.insert("end", f"Resultado:  I ≈ {float(val):.8f}\n")
        except (ValueError, ZeroDivisionError, ArithmeticError, TypeError) as exc:
            messagebox.showerror("Error", f"Cálculo falló: {exc}")
        texto.see("end")

    # ============================================================
    #  Calculadora · Ajuste de curvas
    # ============================================================

    def _calc_ajuste(self):
        _, contenido = self._construir_esqueleto_calculadora(
            "Calculadora · Ajuste de Curvas",
            tipo_ejemplo="ajuste",
            descripcion_corta="Mínimos cuadrados polinomiales con selección automática de grado",
        )

        self.aj_grado = tk.StringVar(value="auto")
        self.aj_x_eval = tk.StringVar(value="")

        ops = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        ops.pack(anchor="w", fill="x", pady=(4, 6))
        tk.Label(ops, text="Grado:", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA_B).pack(side="left", padx=(0, 6))
        tk.Entry(ops, textvariable=self.aj_grado, width=8,
                 font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT).pack(side="left", padx=4)
        tk.Label(ops, text="(entero o 'auto')", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_PEQUENA_IT, fg=tema.COLOR_TEXTO_SUAVE
                 ).pack(side="left", padx=4)
        tk.Label(ops, text="Evaluar en x:", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_ETIQUETA).pack(side="left", padx=(24, 6))
        tk.Entry(ops, textvariable=self.aj_x_eval, width=10,
                 font=tema.FUENTE_ENTRADA, bg=tema.COLOR_FONDO_INPUT).pack(side="left", padx=4)
        tk.Label(ops, text="(opcional)", bg=tema.COLOR_FONDO_TARJETA,
                 font=tema.FUENTE_PEQUENA_IT, fg=tema.COLOR_TEXTO_SUAVE
                 ).pack(side="left", padx=4)

        tk.Label(
            contenido,
            text="Puntos (uno por línea, formato 'x y' o 'x, y'):",
            font=tema.FUENTE_ETIQUETA,
            bg=tema.COLOR_FONDO_TARJETA, fg=tema.COLOR_TEXTO,
        ).pack(anchor="w", pady=(6, 2))

        self.aj_puntos = tk.Text(contenido, height=8, width=44,
                                  font=tema.FUENTE_ENTRADA, bd=1, relief="solid",
                                  bg=tema.COLOR_FONDO_INPUT, fg=tema.COLOR_TEXTO,
                                  highlightthickness=0)
        self.aj_puntos.pack(anchor="w", pady=4)
        self.aj_puntos.insert("end", "0 1\n1 3\n2 5\n3 7\n4 9\n")

        botonera = tk.Frame(contenido, bg=tema.COLOR_FONDO_TARJETA)
        botonera.pack(anchor="w", pady=(8, 4))
        widgets.BotonClasico(
            botonera, "Calcular", comando=self._ajuste_calcular,
            tipo="exito", ancho=14,
        ).pack(side="left", padx=4)
        widgets.BotonClasico(
            botonera, "Cargar ejemplo", comando=self._ajuste_ejemplo,
            tipo="informacion",
        ).pack(side="left", padx=4)
        widgets.BotonClasico(
            botonera, "Limpiar", comando=self._ajuste_limpiar,
            tipo="neutro",
        ).pack(side="left", padx=4)

    def _ajuste_ejemplo(self):
        self.aj_puntos.delete("1.0", "end")
        self.aj_puntos.insert("end", "0 1\n1 3\n2 5\n3 7\n4 9\n")
        self.aj_grado.set("auto")
        self.aj_x_eval.set("2.5")

    def _ajuste_limpiar(self):
        self.aj_puntos.delete("1.0", "end")
        self.aj_grado.set("")
        self.aj_x_eval.set("")

    def _ajuste_calcular(self):
        if coeficientes_polinomio_con_pasos is None:
            messagebox.showerror("Error", "No se encontró el módulo de ajuste de curvas.")
            return
        try:
            puntos = self._parsear_puntos(self.aj_puntos.get("1.0", "end"))
        except ValueError as exc:
            messagebox.showerror("Error", str(exc))
            return
        xs = [p[0] for p in puntos]
        ys = [p[1] for p in puntos]

        gtxt = self.aj_grado.get().strip().lower()
        texto = self._abrir_ventana_resultados("Resultados · Ajuste de Curvas")
        texto.insert("end", "Puntos:\n")
        for x, y in puntos:
            texto.insert("end", f"  ({x}, {y})\n")
        texto.insert("end", "─" * 60 + "\n")

        try:
            if gtxt in ("", "auto"):
                grado, coef, error = mejor_ajuste(xs, ys)
                texto.insert("end", f"Grado óptimo (mínimo RSS): {grado}\n")
            else:
                grado = int(gtxt)
                coef, pasos = coeficientes_polinomio_con_pasos(xs, ys, grado)
                texto.insert("end", f"Grado solicitado: {grado}\n")
                texto.insert("end", "─" * 60 + "\n")
                texto.insert("end", "Procedimiento:\n")
                texto.insert("end", pasos + "\n")
                error = rss(xs, ys, coef)

            texto.insert("end", "─" * 60 + "\n")
            texto.insert("end", "Coeficientes:\n")
            for i, c in enumerate(coef):
                texto.insert("end", f"  K{i} = {c:.8f}\n")
            texto.insert("end", f"\nEcuación: y = {formato_ecuacion(coef)}\n")
            texto.insert("end", f"RSS = {error:.8f}\n")

            xe = self.aj_x_eval.get().strip()
            if xe:
                try:
                    xv = float(xe)
                    yv = evaluar_polinomio(coef, xv)
                    texto.insert("end", f"\nEvaluación: y({xv}) = {yv:.8f}\n")
                except ValueError:
                    texto.insert("end", f"\n(x de evaluación inválido: '{xe}')\n")
        except (ValueError, ZeroDivisionError, ArithmeticError) as exc:
            messagebox.showerror("Error", f"Cálculo falló: {exc}")
        texto.see("end")


# ---------------------------------------------------------------------------
#  Entry-point para ejecución directa del módulo
# ---------------------------------------------------------------------------

def lanzar_aplicacion():
    AplicacionMetodosNumericos().run()


if __name__ == "__main__":
    lanzar_aplicacion()
