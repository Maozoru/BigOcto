from PyQt6.QtGui import QImage

class Layer:
    def __init__(self, width, height):
        self.image = QImage(width, height, QImage.Format.Format_ARGB32)
        self.image.fill(Qt.GlobalColor.transparent)
        self.visible = True

    def toggle_visibility(self):
        self.visible = not self.visible
