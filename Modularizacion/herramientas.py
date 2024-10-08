from PyQt6.QtCore import *
from PyQt6.QtGui import *

class Herramientas:
    def __init__(self):
        self.pincel = Pincel()
        self.borrador = Borrador()
        self.relleno = Relleno()

    def set_color(self, color):
        self.pincel.set_color(color)
    def activar_seleccion(self, checked):
        self.seleccion_activa = checked



    def toleranciadelrelleno(self, value):
        self.tolerancia = value

    def update_recent_palette(self):
        """ Actualiza la visualización de los colores recientes. """
        for i, color in enumerate(self.colores_recientes):
            btn = QPushButton()
            btn.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            btn.setFixedSize(50, 50)
            btn.clicked.connect(lambda checked, col=color: self.set_color(col))
            self.diseno_paleta_reciente.addWidget(btn, i // 2, i % 2)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.set_color(color.name())

    def clear_canvas(self):
        """ Limpia el lienzo actual. """
        self.lienzo.fill(Qt.GlobalColor.transparent)
        self.update_canvas()

class Pincel:
    def __init__(self):
        def seleccion_normie(self):
            self.modo_pixel = False

        def seleccion_pixel(self):
            self.modo_pixel = True

        def tamañopincel(self, value):
            self.tamaño_pincel = value

        def opacidadpincel(self, value):
            self.opacidad_pincel = value / 100.0

        def set_color(self, color):
            self.color = QColor(color)

        def set_color(self, color):
            self.color_pincel = QColor(color)
            if color not in self.colores_recientes:
                self.colores_recientes.append(color)
                if len(self.colores_recientes) > 6:
                    self.colores_recientes.pop(0)
                self.update_recent_palette()

class Borrador:
    def __init__(self):
        def activar_goma(self, checked):
            self.modo_borrador = checked

class Relleno:
    def __init__(self):
        self.color = QColor(Qt.GlobalColor.black)
        self.tolerancia = 0

    def set_color(self, color):
        self.color = QColor(color)

class PixelBrush:
    def __init__(self, canvas: QImage):
        self.canvas = canvas
        self.color = QColor(0, 0, 0)  # Default color is black
        self.size = 1  # Default size of the brush (1 pixel)

    def draw(self, x: int, y: int):
        # Draw a single pixel at the position (x, y)
        self.canvas.setPixel(x, y, self.color.rgb())
        
        # Optionally, draw a square based on the brush size
        for i in range(-self.size // 2, self.size // 2 + 1):
            for j in range(-self.size // 2, self.size // 2 + 1):
                self.canvas.setPixel(x + i, y + j, self.color.rgb())

    def set_color(self, color: QColor):
        """Set the brush color."""
        self.color = color

    def set_size(self, size: int):
        """Set the size of the brush."""
        if size > 0:
            self.size = size
        else:
            raise ValueError("Size must be a positive integer.")
