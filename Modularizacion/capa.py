from PyQt6.QtGui import QImage

class Capa:
    def __init__(self, nombre, imagen):
        self.nombre = nombre
        self.imagen = imagen
        self.visible = True
        self.bloqueada = False
        self.opacidad = 1.0

    def renombrar(self, nuevo_nombre):
        self.nombre = nuevo_nombre
