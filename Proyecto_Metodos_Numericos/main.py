"""Entry-point del proyecto unificado de Métodos Numéricos.

Ejecutar con:
    python main.py

Atajos de teclado dentro de la aplicación:
    F11    – Alterna pantalla completa
    Esc    – Sale de pantalla completa
    Rueda  – Desplazamiento vertical en cualquier vista
"""

from __future__ import annotations

import os
import sys


# Asegura que los paquetes locales se encuentren sin importar desde dónde se ejecute.
DIR_PROYECTO = os.path.dirname(os.path.abspath(__file__))
if DIR_PROYECTO not in sys.path:
    sys.path.insert(0, DIR_PROYECTO)


def main() -> None:
    from app.aplicacion import AplicacionMetodosNumericos
    AplicacionMetodosNumericos().run()


if __name__ == "__main__":
    main()
