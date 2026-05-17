"""Widgets reutilizables para la aplicación.

Incluye:
    MarcoConScroll  - contenedor con scroll vertical y soporte de rueda del ratón
    BotonClasico    - botón con paleta unificada del tema clásico
    EncabezadoUACH  - banda institucional reusable
    Separador       - línea fina con color del tema
    BarraDeAcciones - distribuye varios botones con saltos automáticos
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Iterable, Sequence

from . import tema


# ---------------------------------------------------------------------------
#  Contenedor con desplazamiento vertical
# ---------------------------------------------------------------------------

class MarcoConScroll(tk.Frame):
    """Frame scrolleable con scroll del ratón global mientras el cursor lo cubre.

    Uso:
        contenedor = MarcoConScroll(parent)
        contenedor.pack(fill="both", expand=True)
        contenedor.interior  # frame al que se le agregan los hijos
    """

    def __init__(self, padre, bg=None, **kwargs):
        bg = bg or tema.COLOR_FONDO
        super().__init__(padre, bg=bg, **kwargs)

        self.canvas = tk.Canvas(
            self, bg=bg, highlightthickness=0, borderwidth=0,
        )
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview,
            style="Clasico.Vertical.TScrollbar",
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.interior = tk.Frame(self.canvas, bg=bg)
        self._window_id = self.canvas.create_window(
            (0, 0), window=self.interior, anchor="nw",
        )

        self.interior.bind("<Configure>", self._actualizar_region_scroll)
        self.canvas.bind("<Configure>", self._sincronizar_ancho)

        # Captura de la rueda del ratón sólo mientras el puntero está encima.
        self.canvas.bind("<Enter>", self._enlazar_rueda)
        self.canvas.bind("<Leave>", self._desenlazar_rueda)

    def _actualizar_region_scroll(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _sincronizar_ancho(self, event):
        # Hace que el frame interior siempre tenga el ancho del canvas:
        # garantiza que no aparezca scroll horizontal y que el contenido
        # se expanda al pasar a pantalla completa.
        self.canvas.itemconfig(self._window_id, width=event.width)

    def _enlazar_rueda(self, _event=None):
        self.canvas.bind_all("<MouseWheel>", self._scroll_windows)
        self.canvas.bind_all("<Button-4>", self._scroll_linux)
        self.canvas.bind_all("<Button-5>", self._scroll_linux)

    def _desenlazar_rueda(self, _event=None):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _scroll_windows(self, event):
        # Windows entrega event.delta múltiplos de 120.
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _scroll_linux(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def ir_al_inicio(self):
        self.canvas.yview_moveto(0)


# ---------------------------------------------------------------------------
#  Botón clásico
# ---------------------------------------------------------------------------

def BotonClasico(padre, texto: str, comando: Callable, *,
                 tipo: str = "principal", ancho: int | None = None,
                 fuente=None) -> tk.Button:
    """Crea un tk.Button con la paleta del tema clásico.

    tipo: 'principal' | 'exito' | 'informacion' | 'peligro' | 'neutro' | 'discreto'
    """
    estilo = tema.ESTILOS_BOTON.get(tipo, tema.ESTILOS_BOTON["principal"])
    boton = tk.Button(
        padre,
        text=texto,
        command=comando,
        bg=estilo["bg"],
        fg=estilo["fg"],
        activebackground=estilo["activebg"],
        activeforeground=estilo["activefg"],
        font=fuente or tema.FUENTE_BOTON,
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=14,
        pady=7,
    )
    if ancho:
        boton.configure(width=ancho)
    return boton


# ---------------------------------------------------------------------------
#  Encabezado institucional
# ---------------------------------------------------------------------------

class EncabezadoUACH(tk.Frame):
    """Banda con escudos y leyenda institucional. Soporta fondo claro u oscuro."""

    def __init__(self, padre, *, fondo: str, color_texto: str,
                 imagen_fing=None, imagen_uach=None,
                 subtitulo: str = "Métodos Numéricos · Presentación Final"):
        super().__init__(padre, bg=fondo)
        self._fondo = fondo
        self._color = color_texto
        self._construir(imagen_fing, imagen_uach, subtitulo)

    def _construir(self, img_fing, img_uach, subtitulo):
        cont = tk.Frame(self, bg=self._fondo)
        cont.pack(fill="x", padx=tema.PAD_PAGINA_X, pady=(16, 8))

        if img_fing is not None:
            tk.Label(cont, image=img_fing, bg=self._fondo).pack(side="left", padx=(0, 14))

        centro = tk.Frame(cont, bg=self._fondo)
        centro.pack(side="left", expand=True, fill="x")
        tk.Label(
            centro,
            text="Universidad Autónoma de Chihuahua",
            font=(tema.FAMILIA_SERIF_DECORATIVA, 20, "bold"),
            bg=self._fondo, fg=self._color,
        ).pack()
        tk.Label(
            centro,
            text="Facultad de Ingeniería",
            font=(tema.FAMILIA_SERIF_DECORATIVA, 13),
            bg=self._fondo, fg=self._color,
        ).pack()
        tk.Label(
            centro,
            text=subtitulo,
            font=(tema.FAMILIA_SERIF_DECORATIVA, 11, "italic"),
            bg=self._fondo, fg=self._color,
        ).pack(pady=(2, 0))

        if img_uach is not None:
            tk.Label(cont, image=img_uach, bg=self._fondo).pack(side="right", padx=(14, 0))

        Separador(self, color=tema.COLOR_SEPARADOR).pack(
            fill="x", padx=tema.PAD_PAGINA_X, pady=(0, 2)
        )


# ---------------------------------------------------------------------------
#  Separador horizontal
# ---------------------------------------------------------------------------

class Separador(tk.Frame):
    def __init__(self, padre, color=None, alto: int = 1, **kwargs):
        super().__init__(padre, bg=color or tema.COLOR_SEPARADOR,
                         height=alto, **kwargs)


# ---------------------------------------------------------------------------
#  Barra de acciones con saltos automáticos
# ---------------------------------------------------------------------------

class BarraDeAcciones(tk.Frame):
    """Barra horizontal de botones que se reorganiza en filas si el ancho falta.

    Cada acción es un dict con: texto, comando, tipo (opcional), ancho (opcional).
    """

    def __init__(self, padre, acciones: Sequence[dict],
                 bg=None, columnas_min: int = 1, columnas_max: int = 5,
                 **kwargs):
        bg = bg or tema.COLOR_FONDO
        super().__init__(padre, bg=bg, **kwargs)
        self._acciones = list(acciones)
        self._bg = bg
        self._columnas_max = columnas_max
        self._columnas_min = columnas_min
        self._botones = []
        self._construir()
        self.bind("<Configure>", self._reorganizar)

    def _construir(self):
        for accion in self._acciones:
            b = BotonClasico(
                self,
                texto=accion["texto"],
                comando=accion["comando"],
                tipo=accion.get("tipo", "principal"),
                ancho=accion.get("ancho"),
            )
            self._botones.append(b)

    def _reorganizar(self, _event=None):
        # Limpia el layout actual
        for b in self._botones:
            b.grid_forget()
        ancho_disponible = self.winfo_width()
        ancho_botones = max(180, max((b.winfo_reqwidth() for b in self._botones),
                                     default=180))
        cols = max(self._columnas_min,
                   min(self._columnas_max,
                       ancho_disponible // (ancho_botones + 10) or 1))
        for idx, b in enumerate(self._botones):
            fila = idx // cols
            col = idx % cols
            b.grid(row=fila, column=col, padx=6, pady=4, sticky="ew")
        for c in range(cols):
            self.grid_columnconfigure(c, weight=1)


# ---------------------------------------------------------------------------
#  Tarjeta envolvente con borde fino
# ---------------------------------------------------------------------------

class Tarjeta(tk.Frame):
    def __init__(self, padre, **kwargs):
        kwargs.setdefault("bg", tema.COLOR_FONDO_TARJETA)
        kwargs.setdefault("highlightthickness", tema.GROSOR_BORDE)
        kwargs.setdefault("highlightbackground", tema.COLOR_BORDE)
        kwargs.setdefault("highlightcolor", tema.COLOR_BORDE)
        super().__init__(padre, **kwargs)
