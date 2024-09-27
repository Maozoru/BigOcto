from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class LayerManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Layer Manager")
        self.setFixedSize(300, 400)

        self.layers = []  # List to store layers (QImage)
        self.active_layer_index = 0

        # Set up UI for the layer manager (e.g., list of layers, buttons)
        self.layout = QVBoxLayout(self)
        self.layer_list = QListWidget(self)
        self.layout.addWidget(self.layer_list)

        # Add buttons to add and remove layers
        self.add_layer_button = QPushButton("Add Layer", self)
        self.add_layer_button.clicked.connect(self.add_layer)
        self.layout.addWidget(self.add_layer_button)

        self.remove_layer_button = QPushButton("Remove Layer", self)
        self.remove_layer_button.clicked.connect(self.remove_layer)
        self.layout.addWidget(self.remove_layer_button)

        self.update_layer_list()

    def add_layer(self):
        new_layer = QImage(self.size(), QImage.Format.Format_ARGB32_Premultiplied)
        new_layer.fill(Qt.GlobalColor.transparent)
        self.layers.append(new_layer)
        self.update_layer_list()

    def remove_layer(self):
        if self.layers:
            self.layers.pop(self.active_layer_index)
            self.active_layer_index = max(0, self.active_layer_index - 1)
            self.update_layer_list()

    def update_layer_list(self):
        self.layer_list.clear()
        for index, layer in enumerate(self.layers):
            self.layer_list.addItem(f"Layer {index + 1}")
        if self.layers:
            self.layer_list.setCurrentRow(self.active_layer_index)