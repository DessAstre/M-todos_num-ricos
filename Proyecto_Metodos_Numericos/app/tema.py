"""Tema visual elegante y clásico para la aplicación.

Paleta inspirada en bibliotecas universitarias clásicas: pergamino, nogal,
oro envejecido y borgoña. Sin colores llamativos: serif para títulos,
fuente sans neutra para datos y monoespaciada para resultados.

Todas las vistas usan exactamente estas constantes — modifíquelas aquí para
ajustar el tema en toda la aplicación.
"""

# ---------------------------------------------------------------------------
#  Paleta de colores
# ---------------------------------------------------------------------------

# Fondos
COLOR_FONDO        = "#F1EADA"   # pergamino cálido (página)
COLOR_FONDO_OSCURO = "#2A1E18"   # nogal profundo (encabezado / barra inferior)
COLOR_FONDO_TARJETA = "#FBF8F1"  # marfil cálido (tarjetas / inputs)
COLOR_FONDO_INPUT  = "#FFFFFF"   # blanco puro para entradas
COLOR_FONDO_RESULTADO = "#1C1814"  # mocha oscuro para consola de resultados
COLOR_FONDO_RAYADO = "#EFE7D2"   # tono alterno suave para filas / cabeceras

# Texto
COLOR_TITULO       = "#2A1E18"   # nogal profundo
COLOR_TEXTO        = "#3A2E22"   # chocolate
COLOR_TEXTO_SUAVE  = "#6E5E48"   # café cálido apagado
COLOR_TEXTO_CLARO  = "#F5EFE0"   # pergamino claro (sobre fondo oscuro)
COLOR_TEXTO_RESULT = "#E8DFC6"   # marfil tenue sobre consola

# Acentos
COLOR_ACENTO_ORO   = "#8A6B30"   # oro envejecido
COLOR_ACENTO_BORGONA = "#6B2C39" # borgoña
COLOR_ACENTO_BOSQUE = "#3D5A40"  # verde bosque
COLOR_ACENTO_AZUL_PROFUNDO = "#1F3551"  # azul medianoche para acciones primarias

# Bordes y separadores
COLOR_BORDE        = "#C9BBA5"   # tan cálido
COLOR_BORDE_SUAVE  = "#DCD2BD"
COLOR_SEPARADOR    = "#B8A88A"

# ---------------------------------------------------------------------------
#  Tipografías
# ---------------------------------------------------------------------------

# Familia serif clásica disponible en Windows (con fallbacks razonables)
FAMILIA_SERIF = "Cambria"
FAMILIA_SERIF_DECORATIVA = "Georgia"
FAMILIA_SANS = "Segoe UI"
FAMILIA_MONO = "Consolas"

FUENTE_PORTADA     = (FAMILIA_SERIF_DECORATIVA, 28, "bold")
FUENTE_TITULO      = (FAMILIA_SERIF_DECORATIVA, 22, "bold")
FUENTE_SUBTITULO   = (FAMILIA_SERIF_DECORATIVA, 14, "italic")
FUENTE_SECCION     = (FAMILIA_SERIF, 12, "bold")
FUENTE_ETIQUETA    = (FAMILIA_SANS, 11)
FUENTE_ETIQUETA_B  = (FAMILIA_SANS, 11, "bold")
FUENTE_ENTRADA     = (FAMILIA_MONO, 11)
FUENTE_BOTON       = (FAMILIA_SANS, 11, "bold")
FUENTE_BOTON_SUAVE = (FAMILIA_SANS, 10)
FUENTE_PEQUENA     = (FAMILIA_SANS, 10)
FUENTE_PEQUENA_IT  = (FAMILIA_SANS, 10, "italic")
FUENTE_TEXTO_LARGO = (FAMILIA_SERIF, 12)
FUENTE_CONSOLA     = (FAMILIA_MONO, 11)

# ---------------------------------------------------------------------------
#  Dimensiones / espaciado
# ---------------------------------------------------------------------------

PAD_PAGINA_X = 32
PAD_PAGINA_Y = 18
PAD_CARD_X = 22
PAD_CARD_Y = 16
ESPACIO_FILA = 6

# Anchos estándar para botones (en caracteres)
ANCHO_BOTON = 18
ANCHO_BOTON_LARGO = 24
ANCHO_BOTON_CORTO = 12

# Bordes
GROSOR_BORDE = 1
RADIO_VISUAL = 0  # tkinter no soporta esquinas redondeadas en Buttons clásicos

# ---------------------------------------------------------------------------
#  Estilos de botones (planos, sobrios)
# ---------------------------------------------------------------------------

ESTILOS_BOTON = {
    # acción dominante (avanzar / ejecutar primario)
    "principal": {
        "bg": COLOR_ACENTO_AZUL_PROFUNDO,
        "fg": COLOR_TEXTO_CLARO,
        "activebg": "#163047",
        "activefg": COLOR_TEXTO_CLARO,
    },
    # acción de cálculo / confirmación positiva
    "exito": {
        "bg": COLOR_ACENTO_BOSQUE,
        "fg": COLOR_TEXTO_CLARO,
        "activebg": "#324930",
        "activefg": COLOR_TEXTO_CLARO,
    },
    # acción de información / secundaria suave
    "informacion": {
        "bg": COLOR_ACENTO_ORO,
        "fg": COLOR_TEXTO_CLARO,
        "activebg": "#6F5526",
        "activefg": COLOR_TEXTO_CLARO,
    },
    # acción destructiva (cerrar, salir, limpiar fuerte)
    "peligro": {
        "bg": COLOR_ACENTO_BORGONA,
        "fg": COLOR_TEXTO_CLARO,
        "activebg": "#52222C",
        "activefg": COLOR_TEXTO_CLARO,
    },
    # acción neutra (volver, cancelar, limpiar)
    "neutro": {
        "bg": "#5C4A38",
        "fg": COLOR_TEXTO_CLARO,
        "activebg": "#473829",
        "activefg": COLOR_TEXTO_CLARO,
    },
    # botón discreto sobre tarjeta (estilo "fantasma")
    "discreto": {
        "bg": COLOR_FONDO_RAYADO,
        "fg": COLOR_TITULO,
        "activebg": COLOR_BORDE_SUAVE,
        "activefg": COLOR_TITULO,
    },
}


def configurar_estilo_ttk(estilo):
    """Aplica el tema clásico-elegante a los widgets ttk usados (Combobox, etc.)."""
    estilo.theme_use("clam")

    estilo.configure(
        "Clasico.TCombobox",
        fieldbackground=COLOR_FONDO_INPUT,
        background=COLOR_FONDO_TARJETA,
        foreground=COLOR_TEXTO,
        bordercolor=COLOR_BORDE,
        lightcolor=COLOR_BORDE,
        darkcolor=COLOR_BORDE,
        selectbackground=COLOR_ACENTO_AZUL_PROFUNDO,
        selectforeground=COLOR_TEXTO_CLARO,
        arrowcolor=COLOR_TITULO,
        font=("Segoe UI", 11),
    )
    estilo.map(
        "Clasico.TCombobox",
        fieldbackground=[("readonly", COLOR_FONDO_INPUT)],
        foreground=[("readonly", COLOR_TEXTO)],
        background=[("readonly", COLOR_FONDO_TARJETA)],
    )

    estilo.configure(
        "Clasico.Vertical.TScrollbar",
        background=COLOR_FONDO_TARJETA,
        troughcolor=COLOR_FONDO_RAYADO,
        bordercolor=COLOR_BORDE,
        arrowcolor=COLOR_TITULO,
        gripcount=0,
    )

    estilo.configure(
        "Clasico.TSeparator",
        background=COLOR_SEPARADOR,
    )
