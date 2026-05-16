import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import subprocess
import sys


class PresentationApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Métodos Aproximados")
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
        style.configure("TFrame", background="#0f2a10")
        style.configure("Card.TFrame", background="#0f2a10")
        style.configure("Header.TLabel", background="#0f2a10", foreground="#f9fcf8", font=(font_ui, 26, "bold"))
        style.configure("SubHeader.TLabel", background="#0f2a10", foreground="#cbd5e1", font=(font_ui, 12))
        style.configure("Title.TLabel", background="#0f2a10", foreground="#f8fafc", font=(font_ui, 20, "bold"))
        style.configure("Body.TLabel", background="#0f2a10", foreground="#e4f0e2", font=(font_ui, 14), wraplength=930, justify="left")
        style.configure("CenterBody.TLabel", background="#0f2a10", foreground="#e2f0e2", font=(font_ui, 14), wraplength=930, justify="center")
        style.configure("MethodTag.TLabel", background="#0f2a10", foreground="#7dfc7d", font=("Georgia", 13, "bold italic"))
        style.configure("Small.TLabel", background="#0f2a10", foreground="#9ab894", font=(font_ui, 10))
        style.configure("Accent.TButton", font=(font_ui, 10, "bold"), padding=(16, 10))
        style.map("Accent.TButton", foreground=[("active", "white")], background=[("active", "#25eb2f")])

    def _create_page(self, title, subtitle=None, header_left_image=None, header_right_image=None, content_image=None, image_position="bottom"):
        page = ttk.Frame(self.root, style="TFrame")

        header = ttk.Frame(page, style="TFrame")
        header.pack(fill="x", padx=26, pady=(24, 12))

        header_row = ttk.Frame(header, style="TFrame")
        header_row.pack(anchor="center")

        if header_left_image is not None:
            ttk.Label(header_row, image=header_left_image, background="#0f2a10").pack(side="left", padx=(0, 12))

        ttk.Label(header_row, text=title, style="Header.TLabel").pack(side="left")

        if header_right_image is not None:
            ttk.Label(header_row, image=header_right_image, background="#0f2a10").pack(side="left", padx=(12, 0))

        if subtitle:
            ttk.Label(header, text=subtitle, style="SubHeader.TLabel").pack(anchor="center", pady=(6, 0))

        # Marco decorativo global para todas las diapositivas
        card_shell = tk.Frame(
            page,
            bg="#233b1e",
            highlightthickness=1,
            highlightbackground="#365533"
        )
        card_shell.pack(fill="both", expand=True, padx=26, pady=(6, 18))

        card = ttk.Frame(card_shell, style="Card.TFrame")
        card.pack(fill="both", expand=True, padx=12, pady=12)

        # Barra superior de acento para una apariencia más limpia
        accent_bar = tk.Frame(card, bg="#48f838", height=3)
        accent_bar.pack(fill="x", pady=(0, 12))

        # Contenedor principal para texto e imagen
        main_content = ttk.Frame(card, style="Card.TFrame")
        main_content.pack(fill="both", expand=True)

        if content_image and image_position == "right":
            # Contenido a la izquierda, imagen a la derecha
            content = ttk.Frame(main_content, style="Card.TFrame")
            content.pack(side="left", fill="both", expand=True, padx=(0, 12))
            
            img_label = ttk.Label(main_content, image=content_image, background="#233b1e")
            img_label.pack(side="right", padx=12)
        elif content_image and image_position == "bottom":
            # Texto arriba, imagen abajo
            content = ttk.Frame(main_content, style="Card.TFrame")
            content.pack(fill="both", expand=True, pady=(0, 12))
            
            img_frame = ttk.Frame(main_content, style="Card.TFrame")
            img_frame.pack(fill="x", pady=(12, 0))
            
            img_label = ttk.Label(img_frame, image=content_image, background="#233b1e")
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

        ttk.Label(nav, text=f"Ventana {page_index + 1} de {len(self.pages)}", background="#0f2a10", foreground="#cbe1cb", font=("Aptos", 10)).pack(side="left", padx=18)

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

            dot = tk.Label(inner, text="•", bg="#0f2a10", fg="#48f838", font=("Aptos", 16, "bold"))
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
        image.put("#233b1e", to=(0, 0, width, height))
        
        # Dibujar un borde
        for x in range(width):
            image.put("#48f838", (x, 0))
            image.put("#48f838", (x, height - 1))
        for y in range(height):
            image.put("#48f838", (0, y))
            image.put("#48f838", (width - 1, y))
        
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

        ttk.Label(center_content, text="Capítulo 2: Solución de Sistemas de Ecuaciones No Lineales \nMétodos Aproximados", style="Title.TLabel", anchor="center", justify="center").pack(fill="x", pady=(12, 8))
        ttk.Label(center_content, text="Equipo:\n Aryam Desiree Méndez Sánchez -373025 \n Francisco Javier Ponce Saenz -325000\n", style="CenterBody.TLabel", anchor="center", justify="center").pack(fill="x", pady=3)
        ttk.Label(center_content, text="Maestro: Óscar Mauricio Borunda Carrasco\n", style="CenterBody.TLabel", anchor="center", justify="center").pack(fill="x", pady=3)
        ttk.Label(center_content, text="Materia: Métodos Numéricos\n", style="CenterBody.TLabel", anchor="center", justify="center").pack(fill="x", pady=3)
        ttk.Label(center_content, text="Fecha: 19 de mayo de 2026", style="CenterBody.TLabel", anchor="center", justify="center").pack(fill="x", pady=3)
        ttk.Label(center_content, text="Programa desarrollado para resolver ecuaciones no lineales con dos métodos clásicos.", style="CenterBody.TLabel", anchor="center", justify="center").pack(fill="x", pady=(24, 0))
        self.pages.append((page, nav))

        # 2. Capítulo y tema
        img2 = self._load_logo([""], max_size=(200, 200))
        if img2:
            self.images.append(img2)
        page, card, nav = self._create_page("Capítulo 2: Solución de Sistemas de Ecuaciones No Lineales", "¿Qué se estudia en este capítulo?", content_image=img2, image_position="bottom")
        method_row = ttk.Frame(card, style="Card.TFrame")
        method_row.pack(fill="x", pady=(8, 6))
        ttk.Label(method_row, text="Métodos aproximados: Gauss-Seidel y Relajaciones", style="MethodTag.TLabel").pack(anchor="center", pady=(0, 12))
        ttk.Label(method_row, text="Resuelven sistemas de ecuaciones lineales mediante aproximaciones sucesivas hasta obtener una solución cercana al valor real.", style="Body.TLabel", justify="center").pack(anchor="center", pady=(0, 12))
        self._bullet_list(card, [
            "Método de Gauss-Seidel: Actualiza cada variable en función de las últimas aproximaciones, utilizando los valores más recientes para acelerar la convergencia.",
            "\nMétodo de Relajaciones: Ajusta los valores calculados en cada iteración para obtener resultados más rápidos y precisos.",
            "\nRequieren que el sistema sea diagonalmente dominante",
        ])
        self.pages.append((page, nav))

        # 3. Tema y utilidad
        img3 = self._create_placeholder_image()
        if img3:
            self.images.append(img3)
        page, card, nav = self._create_page("Utilidad", "¿Para qué sirve?")
        self._bullet_list(card, [
            "Permiten resolver sistemas grandes de ecuaciones lineales que surgen en problemas de ingeniería, física y matemáticas aplicadas.",
            "Ofrecen soluciones aproximadas cuando los métodos directos son inviables."
        ])
        self.pages.append((page, nav))

        # 4. Aplicaciones
        img4 = self._create_placeholder_image()
        if img4:
            self.images.append(img4)
        page, card, nav = self._create_page("Aplicaciones", "Dónde se usan estos métodos")
        self._bullet_list(card, [
            "Son fundamentales para la simulación numérica, análisis de estructuras, dinámica de fluidos y optimización de procesos industriales.",
            "Simulación de fenómenos físicos como transferencia de calor, dinámica de fluidos y análisis estructural.",
            "Optimización de procesos industriales y modelado de sistemas complejos.",
            "Análisis de circuitos eléctricos y sistemas de control.",
            "Modelado de problemas de ingeniería civil, como el análisis de estructuras y la mecánica de suelos.",
            "Diseño de algoritmos para inteligencia artificial y aprendizaje automático, especialmente en la optimización de funciones objetivo."
        ])
        self.pages.append((page, nav))

        # 5. Tipo de funciones
        img5 = self._create_placeholder_image()
        if img5:
            self.images.append(img5)
        page, card, nav = self._create_page("Tipos de matrices", "¿Para qué matrices está diseñado el programa?")
        self._bullet_list(card, [
            "Matrices cuadradas con coeficientes reales y vector de términos independientes.",
            "Matrices que tienen una diagonal dominante",
            "Matrices de hasta 6x6 para garantizar tiempos de cálculo razonables.",
            ])
        self.pages.append((page, nav))

        # 6. El programa en sí
        img6 = self._create_placeholder_image()
        if img6:
            self.images.append(img6)
        page, card, nav = self._create_page("Procedimiento", "Lo que hace la aplicación")
        self._bullet_list(card, [
            "\nGauss Seidel:\n"
            "\nEncuentra la matriz dominante",
            "\nDespeja cada variable en función de las otras",
            "\nRealiza iteraciones sucesivas hasta alcanzar la convergencia",
            "\nRelajaciones:\n"
            "\nEncuentra la matriz dominante",
            "\nArma el cuadro base",
            "\nRealiza iteraciones ajustando los valores para acelerar la convergencia"
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
        program_path = os.path.join(os.path.dirname(__file__), "4.pSSELS aproximados.py")
        if not os.path.exists(program_path):
            return

        subprocess.Popen([sys.executable, program_path])
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    PresentationApp().run()