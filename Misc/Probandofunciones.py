from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPainter, QImage, QColor
from PyQt5.QtCore import Qt, QPoint
import sys

class FillWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.image = QImage(400, 400, QImage.Format_RGB888)
        self.image.fill(Qt.white)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        fillButton = QPushButton('Fill', self)
        fillButton.clicked.connect(self.fill)
        layout.addWidget(fillButton)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

    def fill(self):
        start_pos = QPoint(100, 100)  # Puedes cambiar la posición de inicio
        fill_color = QColor(Qt.red)
        target_color = QColor(self.image.pixel(start_pos))

        if target_color == fill_color:
            return

        self.floodFill(start_pos, fill_color, target_color)
        self.update()

    def floodFill(self, start, fill_color, target_color):
        if target_color == fill_color:
            return
        width = self.image.width()
        height = self.image.height()
        stack = [start]

        while stack:
            x, y = stack.pop()
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
            if QColor(self.image.pixel(x, y)) != target_color:
                continue
            
            self.image.setPixelColor(x, y, fill_color)
            stack.extend([QPoint(x+1, y), QPoint(x-1, y), QPoint(x, y+1), QPoint(x, y-1)])

app = QApplication(sys.argv)
window = FillWidget()
window.resize(400, 400)
window.setWindowTitle('Flood Fill Algorithm')
window.show()
sys.exit(app.exec_())
