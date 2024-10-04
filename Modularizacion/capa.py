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
        # Implementar la lógica para fusionar las capas
        pass

    def clonar(self):
        # Implementar la lógica para clonar la capa
        pass

    def bloquear(self):
        self.bloqueada = True

    def desbloquear(self):
        self.bloqueada = False

    def ocultar(self):
        self.visible = False

    def mostrar(self):
        self.visible = True