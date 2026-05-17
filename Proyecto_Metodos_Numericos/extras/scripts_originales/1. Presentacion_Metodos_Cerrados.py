import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import subprocess
import sys


class PresentationApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Presentación: Métodos de Raíces")
        self.root.geometry("1100x650")
        self.root.minsize(1000, 600)
        self.root.configure(bg="#0f172a")

        self.pages = []
        self.current_page = 0
        self.images = []  # Almacenar referencias a todas las imágenes

        self._configure_style()
        self._build_pages()
        self._show_page(0)

    def _configure_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        font_ui = "Aptos"
        style.configure("TFrame", background="#0f172a")
        style.configure("Card.TFrame", background="#111827")
        style.configure("Header.TLabel", background="#0f172a", foreground="#f8fafc", font=(font_ui, 26, "bold"))
        style.configure("SubHeader.TLabel", background="#0f172a", foreground="#cbd5e1", font=(font_ui, 12))
        style.configure("Title.TLabel", background="#111827", foreground="#f8fafc", font=(font_ui, 20, "bold"))
        style.configure("Body.TLabel", background="#111827", foreground="#e2e8f0", font=(font_ui, 14), wraplength=930, justify="left")
        style.configure("CenterBody.TLabel", background="#111827", foreground="#e2e8f0", font=(font_ui, 14), wraplength=930, justify="center")
        style.configure("MethodTag.TLabel", background="#111827", foreground="#7dd3fc", font=("Georgia", 13, "bold italic"))
        style.configure("Small.TLabel", background="#111827", foreground="#94a3b8", font=(font_ui, 10))
        style.configure("Accent.TButton", font=(font_ui, 10, "bold"), padding=(16, 10))
        style.map("Accent.TButton", foreground=[("active", "white")], background=[("active", "#2563eb")])

    def _create_page(self, title, subtitle=None, header_left_image=None, header_right_image=None, content_image=None, image_position="bottom"):
        page = ttk.Frame(self.root, style="TFrame")

        header = ttk.Frame(page, style="TFrame")
        header.pack(fill="x", padx=26, pady=(24, 12))

        header_row = ttk.Frame(header, style="TFrame")
        header_row.pack(anchor="center")

        if header_left_image is not None:
            ttk.Label(header_row, image=header_left_image, background="#0f172a").pack(side="left", padx=(0, 12))

        ttk.Label(header_row, text=title, style="Header.TLabel").pack(side="left")

        if header_right_image is not None:
            ttk.Label(header_row, image=header_right_image, background="#0f172a").pack(side="left", padx=(12, 0))

        if subtitle:
            ttk.Label(header, text=subtitle, style="SubHeader.TLabel").pack(anchor="center", pady=(6, 0))

        # Marco decorativo global para todas las diapositivas
        card_shell = tk.Frame(
            page,
            bg="#1e293b",
            highlightthickness=1,
            highlightbackground="#334155"
        )
        card_shell.pack(fill="both", expand=True, padx=26, pady=(6, 18))

        card = ttk.Frame(card_shell, style="Card.TFrame")
        card.pack(fill="both", expand=True, padx=12, pady=12)

        # Barra superior de acento para una apariencia más limpia
        accent_bar = tk.Frame(card, bg="#38bdf8", height=3)
        accent_bar.pack(fill="x", pady=(0, 12))

        # Contenedor principal para texto e imagen
        main_content = ttk.Frame(card, style="Card.TFrame")
        main_content.pack(fill="both", expand=True)

        if content_image and image_position == "right":
            # Contenido a la izquierda, imagen a la derecha
            content = ttk.Frame(main_content, style="Card.TFrame")
            content.pack(side="left", fill="both", expand=True, padx=(0, 12))
            
            img_label = ttk.Label(main_content, image=content_image, background="#111827")
            img_label.pack(side="right", padx=12)
        elif content_image and image_position == "bottom":
            # Texto arriba, imagen abajo
            content = ttk.Frame(main_content, style="Card.TFrame")
            content.pack(fill="both", expand=True, pady=(0, 12))
            
            img_frame = ttk.Frame(main_content, style="Card.TFrame")
            img_frame.pack(fill="x", pady=(12, 0))
            
            img_label = ttk.Label(img_frame, image=content_image, background="#111827")
            img_label.pack(anchor="center", padx=12)
        else:
            content = main_content

        nav = ttk.Frame(page, style="TFrame")
        nav.pack(fill="x", padx=26, pady=(0, 18))

        return page, content, nav

    def _nav_buttons(self, nav, page_index):
        if page_index > 0:
            ttk.Button(nav, text="Anterior", style="Accent.TButton", command=self._prev_page).pack(side="left")
        else:
            ttk.Button(nav, text="Salir", style="Accent.TButton", command=self.root.destroy).pack(side="left")

        ttk.Label(nav, text=f"Ventana {page_index + 1} de {len(self.pages)}", background="#0f172a", foreground="#cbd5e1", font=("Aptos", 10)).pack(side="left", padx=18)

        if page_index < len(self.pages) - 1:
            ttk.Button(nav, text="Siguiente", style="Accent.TButton", command=self._next_page).pack(side="right")
        else:
            ttk.Button(nav, text="Abrir programa", style="Accent.TButton", command=self._launch_program).pack(side="right")

    def _bullet_list(self, parent, items):
        for item in items:
            row = ttk.Frame(parent, style="Card.TFrame")
            row.pack(fill="x", pady=4)

            inner = ttk.Frame(row, style="Card.TFrame")
            inner.pack(anchor="center")

            dot = tk.Label(inner, text="•", bg="#111827", fg="#60a5fa", font=("Aptos", 16, "bold"))
            dot.pack(side="left", anchor="center")
            text = ttk.Label(inner, text=item, style="CenterBody.TLabel", justify="center")
            text.pack(side="left", anchor="center", padx=(8, 0))

    def _load_logo(self, filenames, max_size=(180, 180)):
        for name in filenames:
            path = os.path.join(os.path.dirname(__file__), name)
            if os.path.exists(path):
                try:
                    # Abrir imagen con PIL
                    image = Image.open(path)
                    image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    # Convertir a PhotoImage para Tkinter
                    photo_image = ImageTk.PhotoImage(image)
                    return photo_image
                except Exception as e:
                    print(f"Error al cargar {path}: {e}")
        return None

    def _create_placeholder_image(self, width=250, height=200, label="Imagen"):
        """Crea una imagen placeholder con Tkinter PhotoImage"""
        image = tk.PhotoImage(width=width, height=height)
        # Llenar con color de fondo
        image.put("#1e293b", to=(0, 0, width, height))
        
        # Dibujar un borde
        for x in range(width):
            image.put("#38bdf8", (x, 0))
            image.put("#38bdf8", (x, height - 1))
        for y in range(height):
            image.put("#38bdf8", (0, y))
            image.put("#38bdf8", (width - 1, y))
        
        return image

    def _build_pages(self):
        # 1. Portada
        left_logo = self._load_logo([
            "Escudo_UACH_neutral.svg.png"
        ], max_size=(120, 120))
        right_logo = self._load_logo([
            "fing-escudo.png"
        ], max_size=(200, 200))

        page, card, nav = self._create_page(
            "     Universidad Autónoma de Chihuahua\n                 Facultad de Ingeniería",
            header_left_image=left_logo,
            header_right_image=right_logo
        )

        self.cover_left_logo = left_logo
        self.cover_right_logo = right_logo
        if left_logo:
            self.images.append(left_logo)
        if right_logo:
            self.images.append(right_logo)

        cover = ttk.Frame(card, style="Card.TFrame")
        cover.pack(fill="both", expand=True, padx=24, pady=24)

        center_content = ttk.Frame(cover, style="Card.TFrame")
        center_content.pack(expand=True)

        ttk.Label(center_content, text="Capítulo 1: Solución de Ecuaciones No Lineales\nRaíces de polinomios", style="Title.TLabel", anchor="center", justify="center").pack(fill="x", pady=(12, 8))
        ttk.Label(center_content, text="Equipo:\n Aryam Desiree Méndez Sánchez -373025 \n Francisco Javier Ponce Saenz -325000\n", style="CenterBody.TLabel", anchor="center", justify="center").pack(fill="x", pady=3)
        ttk.Label(center_content, text="Maestro: Óscar Mauricio Borunda Carrasco\n", style="CenterBody.TLabel", anchor="center", justify="center").pack(fill="x", pady=3)
        ttk.Label(center_content, text="Materia: Métodos Numéricos\n", style="CenterBody.TLabel", anchor="center", justify="center").pack(fill="x", pady=3)
        ttk.Label(center_content, text="Fecha: 19 de mayo de 2026", style="CenterBody.TLabel", anchor="center", justify="center").pack(fill="x", pady=3)
        ttk.Label(center_content, text="Programa desarrollado para resolver ecuaciones no lineales con dos métodos clásicos.", style="CenterBody.TLabel", anchor="center", justify="center").pack(fill="x", pady=(24, 0))
        self.pages.append((page, nav))

        # 2. Capítulo y tema
        img2 = self._load_logo(["biseccion1.png"], max_size=(200, 200))
        if img2:
            self.images.append(img2)
        page, card, nav = self._create_page("Capítulo 1: Solución de Ecuaciones No Lineales (raíces de polinomios)", "¿Qué se estudia en este capítulo?", content_image=img2, image_position="bottom")
        method_row = ttk.Frame(card, style="Card.TFrame")
        method_row.pack(fill="x", pady=(8, 6))
        ttk.Label(method_row, text="\nMétodos cerrados: Bisección y Falsa Posición", style="MethodTag.TLabel").pack(anchor="center", pady=(0, 12))
        ttk.Label(method_row, text="Se necesita conocer un intervalo que encierre a la raíz", style="Body.TLabel").pack(anchor="center", pady=(0, 12))
        self._bullet_list(card, [
            "Método de Bisección: Divide el intervalo a la mitad en cada iteración hasta que la longitud del subintervalo sea menor que alguna tolerancia especificada",
            "\nMétodo de Falsa Posición: Utiliza una línea secante entre los extremos del intervalo para aproximar la raíz",
            "\nRequieren que la función cambie de signo en el intervalo inicial para asegurar la existencia de una raíz.",
        ])
        self.pages.append((page, nav))

        # 3. Tema y utilidad
        img3 = self._create_placeholder_image()
        if img3:
            self.images.append(img3)
        page, card, nav = self._create_page("Utilidad", "¿Para qué sirve?")
        self._bullet_list(card, [
            "Permite encontrar raíces cuando no es posible despejar algebraicamente la variable.",
            "Ayuda a identificar una aproximación numérica confiable de la solución.",
            "Es útil en ingeniería, física, economía y problemas donde aparecen modelos no lineales.",
            "El programa muestra la evolución iterativa para entender cómo se obtiene la respuesta."
        ])
        self.pages.append((page, nav))

        # 4. Aplicaciones
        img4 = self._create_placeholder_image()
        if img4:
            self.images.append(img4)
        page, card, nav = self._create_page("Aplicaciones", "Dónde se usan estos métodos")
        self._bullet_list(card, [
            "Cálculo de raíces en ecuaciones de diseño estructural.",
            "Modelos de transferencia de calor y dinámica de fluidos.",
            "Ajuste de modelos matemáticos en ingeniería y ciencias aplicadas.",
            "Solución de funciones transcedentes o polinomiales sin solución cerrada directa.",
            "Análisis numérico en software educativo y de investigación."
        ])
        self.pages.append((page, nav))

        # 5. Tipo de funciones
        img5 = self._create_placeholder_image()
        if img5:
            self.images.append(img5)
        page, card, nav = self._create_page("Tipos de funciones", "¿Para qué funciones está diseñado el programa?")
        self._bullet_list(card, [
            "Funciones continuas en un intervalo dado.",
            "Funciones polinomiales, racionales y trascendentes simples.",
            "Expresiones con x, exp(x), log(x), log10(x), sqrt(x), sin(x), cos(x), tan(x), pi, e y abs(x).",
            "Requiere que el intervalo tenga cambio de signo para aplicar Bisección o Falsa Posición.",
            "No debe incluir puntos fuera del dominio real, por ejemplo log(x+1) con x ≤ -1 o divisiones por cero.",
            "Ejemplos válidos: x**3 - 4*x + 1, (x+2)/(x-1), exp(x) - 3*x, log(x+1) - 2, sin(x) - 0.5.",
            "Ejemplo mixto: (x**2 + 1)*cos(x) - sqrt(x+4)."])
        self.pages.append((page, nav))

        # 6. El programa en sí
        img6 = self._create_placeholder_image()
        if img6:
            self.images.append(img6)
        page, card, nav = self._create_page("Fórmulas", "Lo que hace la aplicación")
        self._bullet_list(card, [
            "\nFórmulas de Bisección:\n"
            "\nc = (b - a) / 2\nx = a + c\nCondición: |c| ≤ tolerancia",
            "\nFórmulas de Falsa Posición:\n"
            "\nΔx = f(a)(b-a)/(f(a)-f(b))\nx = a + Δx\nCondición: |Δx| ≤ tolerancia"
        ])
        ttk.Label(card, text="Al pulsar 'Abrir programa' se cerrará esta presentación y se abrirá la interfaz principal.", style="Small.TLabel").pack(anchor="w", padx=28, pady=(18, 0))
        self.pages.append((page, nav))

    def _show_page(self, index):
        for page, _ in self.pages:
            page.pack_forget()

        self.current_page = index
        page, nav = self.pages[index]
        page.pack(fill="both", expand=True)

        for widget in nav.winfo_children():
            widget.destroy()
        self._nav_buttons(nav, index)

    def _next_page(self):
        if self.current_page < len(self.pages) - 1:
            self._show_page(self.current_page + 1)

    def _prev_page(self):
        if self.current_page > 0:
            self._show_page(self.current_page - 1)

    def _launch_program(self):
        program_path = os.path.join(os.path.dirname(__file__), "1.pMetodos_Cerrados.py")
        if not os.path.exists(program_path):
            return

        subprocess.Popen([sys.executable, program_path])
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    PresentationApp().run()