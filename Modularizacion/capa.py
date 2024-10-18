from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QWidget, QListWidget, QInputDialog, QSlider
from PyQt6.QtCore import Qt

class Capa:
    def __init__(self, name, imagen):
        self.name = name
        self.imagen = imagen
        self.visible = True
        self.bloqueada = False
        self.opacidad = 1.0

    def renombrar(self, nuevo_nombre):
        self.name = nuevo_nombre

    def eliminar(self):
        # Implementar la lógica para eliminar la capa
        pass

    def ajustar_opacidad(self, nueva_opacidad):
        self.opacidad = nueva_opacidad

    def fusionar(self, otra_capa):
        if not self.visible or not otra_capa.visible:
            return  # No fusionar si alguna capa está oculta
        # Suponiendo que imagen es un QImage o una imagen manipulable
        # Aplicar opacidad de la capa actual sobre la otra capa
        painter = QPainter(otra_capa.imagen)
        painter.setOpacity(self.opacidad)
        painter.drawImage(0, 0, self.imagen)
        painter.end()

    def clonar(self):
        # Crear una nueva capa con el mismo nombre y una copia de la imagen
        nueva_capa = Capa(self.name + " (Copia)", self.imagen.copy())
        nueva_capa.visible = self.visible
        nueva_capa.opacidad = self.opacidad
        nueva_capa.bloqueada = self.bloqueada
        return nueva_capa

    def bloquear(self):
        """Bloquea la capa para evitar modificaciones."""
        self.bloqueada = True

    def desbloquear(self):
        """Desbloquea la capa para permitir modificaciones."""
        self.bloqueada = False

    def ocultar(self):
        self.visible = False

    def mostrar(self):
        self.visible = True