from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtCore import Qt

class DrawCommand:
    def __init__(self, lienzo, start_point, end_point, color, tamaño):
        self.lienzo = lienzo
        self.start_point = start_point
        self.end_point = end_point
        self.color = color
        self.tamaño = tamaño

    def execute(self):
        painter = QPainter(self.lienzo)
        painter.setPen(QPen(self.color, self.tamaño, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(self.start_point, self.end_point)

    def undo(self):
        # Implementar la lógica para deshacer el dibujo
        # Esto podría ser borrando la línea dibujada
        pass

class UndoRedoManager:
    def __init__(self):
        self.undo_stack = []  # Pila de deshacer
        self.redo_stack = []  # Pila de rehacer

    def add_command(self, command):
        self.undo_stack.append(command)
        self.redo_stack.clear()  # Limpia la pila de rehacer cada vez que se agrega un nuevo comando

    def undo(self):
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)  # Agrega a la pila de rehacer

    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.undo_stack.append(command)  # Agrega a la pila de deshacer
