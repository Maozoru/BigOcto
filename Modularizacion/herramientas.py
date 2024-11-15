from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QPushButton, QColorDialog, QVBoxLayout

class Herramientas:
    def __init__(self):
        self.pincel = Pincel()
        self.borrador = Borrador()
        self.relleno = Relleno()
        self.colores_recientes = []
        self.diseno_paleta_reciente = QVBoxLayout()  # Asegúrate de que esto esté en tu layout

    def set_color(self, color):
        self.pincel.set_color(color)

    def activar_seleccion(self, checked):
        self.seleccion_activa = checked

    def toleranciadelrelleno(self, value):
        self.relleno.tolerancia = value  # Asegúrate de asignar la tolerancia al objeto Relleno

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
        self.color_pincel = QColor(Qt.GlobalColor.black)  # Color predeterminado
        self.colores_recientes = []

    def seleccion_normie(self):
        self.modo_pixel = False

    def seleccion_pixel(self):
        self.modo_pixel = True

    def tamañopincel(self, value):
        self.tamaño_pincel = value

    def opacidadpincel(self, value):
        self.opacidad_pincel = value / 100.0

    def set_color(self, color):
        self.color_pincel = QColor(color)
        if color not in self.colores_recientes:
            self.colores_recientes.append(color)
            if len(self.colores_recientes) > 6:
                self.colores_recientes.pop(0)

class Borrador:
    def __init__(self):
        self.modo_borrador = False

    def activar_goma(self, checked):
        self.modo_borrador = checked

class Relleno:
    def __init__(self):
        self.color = QColor(Qt.GlobalColor.black)
        self.tolerancia = 0

    def set_color(self, color):
        self.color = QColor(color)


class PixelBrush:
    def __init__(self, canvas):
        self.canvas = canvas
        self.color = QColor(0, 0, 0)  # Color predeterminado es negro
        self.size = 1  # Tamaño predeterminado del pincel (1 píxel)

    def draw(self, x: int, y: int):
        """Dibuja una línea vertical desde la posición (x, y)."""
        half_size = self.size // 2
        
        # Dibuja solo en la dirección vertical
        for offset in range(-half_size, half_size + 1):
            self.canvas.setPixel(x, y + offset, self.color.rgb())

    def set_color(self, color: QColor):
        """Establece el color del pincel."""
        self.color = color

    def set_size(self, size: int):
        """Establece el tamaño del pincel."""
        if size > 0:
            self.size = size
        else:
            raise ValueError("El tamaño debe ser un entero positivo.")
