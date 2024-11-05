from PyQt6.QtWidgets import QMainWindow, QColorDialog
from PyQt6.QtGui import QKeySequence, QAction

class Shortcuts(QMainWindow):
    def __init__(self, lienzo_de_dibujo):
        super().__init__()
        self.lienzo = lienzo_de_dibujo  # Conexión con LienzoDeDibujo
        self.init_ui()

    def init_ui(self):
        self.set_shortcuts()

    def set_shortcuts(self):
        zoom_in_action = self.create_action("Zoom In", self.lienzo.zoom_in, "Ctrl++")
        self.addAction(zoom_in_action)

        zoom_out_action = self.create_action("Zoom Out", self.lienzo.zoom_out, "Ctrl+-")
        self.addAction(zoom_out_action)

        undo_action = self.create_action("Deshacer", self.lienzo.undo, "Ctrl+Z")
        self.addAction(undo_action)

        redo_action = self.create_action("Rehacer", self.lienzo.redo, "Ctrl+Y")
        self.addAction(redo_action)

        save_action = self.create_action("Guardar", self.lienzo.guardar_lienzo, "Ctrl+S")
        self.addAction(save_action)

        new_action = self.create_action("Nuevo lienzo", self.lienzo.clear_canvas, "Ctrl+N")
        self.addAction(new_action)

        brush_action = self.create_action("Herramienta pincel", self.lienzo.seleccion_normie, "B")
        self.addAction(brush_action)

        eraser_action = self.create_action("Herramienta borrador", self.lienzo.activar_goma, "E")
        self.addAction(eraser_action)

        color_action = self.create_action("Cambiar color", self.lienzo.choose_color, "C")
        self.addAction(color_action)

    def create_action(self, name, slot, shortcut):
        action = QAction(name, self)
        action.triggered.connect(slot)
        action.setShortcut(QKeySequence(shortcut))
        return action

