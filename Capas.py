import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class DrawingCanvas(QWidget):
    def __init__(self, parent=None):
        super(DrawingCanvas, self).__init__(parent)
        self.setWindowTitle("Canvas con Capas")
        self.setFixedSize(1000, 800)

        # Inicializar las capas (máximo 100)
        self.max_layers = 100
        self.layers = []
        self.current_layer = None
        self.current_layer_index = -1  # Índice de la capa activa

        # Crear layout principal
        main_layout = QHBoxLayout(self)

        # Widget de lista de capas
        self.layer_list = QListWidget(self)
        self.layer_list.setFixedWidth(200)
        self.layer_list.itemClicked.connect(self.switch_layer)

        # Botón para agregar capa
        self.add_layer_button = QPushButton("Agregar Capa", self)
        self.add_layer_button.clicked.connect(self.add_layer)

        # Layout para las capas y el botón
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.layer_list)
        left_layout.addWidget(self.add_layer_button)

        # Canvas de dibujo
        self.canvas = QImage(800, 800, QImage.Format_ARGB32)
        self.canvas.fill(Qt.white)

        # Añadir layouts a la ventana principal
        main_layout.addLayout(left_layout)
        self.setLayout(main_layout)

    def add_layer(self):
        """Agrega una nueva capa (hasta 100)."""
        if len(self.layers) >= self.max_layers:
            QMessageBox.warning(self, "Límite de capas", "No puedes agregar más de 100 capas.")
            return

        # Crear una nueva capa
        new_layer = QImage(800, 800, QImage.Format_ARGB32)
        new_layer.fill(Qt.transparent)
        self.layers.append(new_layer)
        self.current_layer = new_layer
        self.current_layer_index = len(self.layers) - 1

        # Crear miniatura de la capa
        self.update_layer_preview(self.current_layer_index)

    def switch_layer(self, item):
        """Cambia la capa activa al hacer clic en una capa de la lista."""
        index = self.layer_list.row(item)
        if 0 <= index < len(self.layers):
            self.current_layer_index = index
            self.current_layer = self.layers[self.current_layer_index]
            self.update()

    def update_layer_preview(self, index):
        """Actualiza la miniatura de una capa en la lista de capas."""
        # Crear miniatura de 100x100
        thumbnail = self.layers[index].scaled(100, 100, Qt.KeepAspectRatio)
        icon = QIcon(QPixmap.fromImage(thumbnail))

        # Añadir o actualizar el elemento en la lista de capas
        if index < self.layer_list.count():
            item = self.layer_list.item(index)
            item.setIcon(icon)
        else:
            item = QListWidgetItem(f"Capa {index + 1}")
            item.setIcon(icon)
            self.layer_list.addItem(item)

    def paintEvent(self, event):
        """Dibuja las capas en el canvas."""
        painter = QPainter(self)
        painter.drawImage(200, 0, self.canvas)  # Dibuja el fondo (canvas)

        # Dibuja cada capa
        for layer in self.layers:
            painter.drawImage(200, 0, layer)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.current_layer is not None:
            # Comienza a dibujar en la capa actual
            self.last_point = event.pos() - QPoint(200, 0)  # Ajuste para la posición del canvas

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.current_layer is not None:
            # Dibuja en la capa actual
            painter = QPainter(self.current_layer)
            pen = QPen(Qt.black, 5, Qt.SolidLine)
            painter.setPen(pen)
            new_point = event.pos() - QPoint(200, 0)
            painter.drawLine(self.last_point, new_point)
            self.last_point = new_point
            self.update()

            # Actualiza la miniatura de la capa actual
            self.update_layer_preview(self.current_layer_index)

    def mouseReleaseEvent(self, event):
        """Finaliza el dibujo."""
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DrawingCanvas()
    window.show()
    sys.exit(app.exec_())
