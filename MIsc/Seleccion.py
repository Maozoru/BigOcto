import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class DrawingCanvas(QWidget):
    def __init__(self, parent=None):
        super(DrawingCanvas, self).__init__(parent)
        self.setWindowTitle("Canvas con Herramienta de Selección")
        self.setFixedSize(800, 600)

        # Parámetros de selección
        self.selection_started = False
        self.selection_rect = QRect()
        
        # Imagen/canvas donde dibujar
        self.image = QImage(self.size(), QImage.Format_ARGB32)
        self.image.fill(Qt.white)

        # Almacena el área seleccionada
        self.selected_area = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Iniciar selección
            self.selection_started = True
            self.selection_rect.setTopLeft(event.pos())
            self.selection_rect.setBottomRight(event.pos())
            self.update()

    def mouseMoveEvent(self, event):
        if self.selection_started:
            # Ajustar el rectángulo de selección al mover el mouse
            self.selection_rect.setBottomRight(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Finalizar la selección
            self.selection_started = False
            self.selected_area = self.selection_rect
            self.update()

    def paintEvent(self, event):
        # Pintar el canvas y el área seleccionada
        painter = QPainter(self)
        painter.drawImage(self.rect(), self.image, self.image.rect())
        
        # Si hay una selección, dibujar el rectángulo de selección
        if self.selection_started or self.selected_area:
            painter.setPen(QPen(Qt.blue, 2, Qt.DashLine))
            painter.drawRect(self.selection_rect)

    def clear_selection(self):
        """Limpia la selección actual."""
        self.selected_area = None
        self.selection_rect = QRect()
        self.update()

if __name__ == "__main__":
    app = QApplication([])
    window = DrawingCanvas()
    window.show()
    sys.exit(app.exec_())
