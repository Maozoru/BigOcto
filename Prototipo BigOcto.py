import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class DrawingCanvas(QWidget):
    def __init__(self, parent=None):
        super(DrawingCanvas, self).__init__(parent)
        self.setWindowTitle("Prototipo BigOcto")
        self.setFixedSize(1200, 800)

        self.brush_color = Qt.black
        self.brush_size = 5
        self.brush_opacity = 1.0
        self.last_point = QPoint()
        self.pen_is_down = False
        self.eraser_mode = False

        self.layout = QHBoxLayout(self)

        self.canvas = QImage(800, 800, QImage.Format_RGB888)
        self.canvas.fill(Qt.white)
        self.canvas_label = QLabel(self)
        self.canvas_label.setPixmap(QPixmap.fromImage(self.canvas))
        self.layout.addWidget(self.canvas_label, 1)

        self.control_frame = QFrame(self)
        self.control_frame.setFixedWidth(300)
        self.control_layout = QVBoxLayout(self.control_frame)

        self.spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.control_layout.addItem(self.spacer)

        # Botón de limpiar
        self.clear_btn = QPushButton("Clear", self)
        self.clear_btn.clicked.connect(self.clear_canvas)
        self.control_layout.addWidget(self.clear_btn)

        # Botón de borrador
        self.eraser_btn = QPushButton("Eraser", self)
        self.eraser_btn.setCheckable(True)
        self.eraser_btn.toggled.connect(self.toggle_eraser)
        self.control_layout.addWidget(self.eraser_btn)

        # Botón de relleno
        self.fill_btn = QPushButton("Fill", self)
        self.fill_btn.setCheckable(True)
        self.control_layout.addWidget(self.fill_btn)

        # Control deslizante para ajustar el tamaño del pincel
        self.size_slider = QSlider(Qt.Horizontal, self)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(self.brush_size)
        self.size_slider.valueChanged.connect(self.change_brush_size)
        self.control_layout.addWidget(QLabel("Brush Size"))
        self.control_layout.addWidget(self.size_slider)

        # Control deslizante para ajustar la opacidad del pincel
        self.opacity_slider = QSlider(Qt.Horizontal, self)
        self.opacity_slider.setRange(1, 100)
        self.opacity_slider.setValue(int(self.brush_opacity * 100))
        self.opacity_slider.valueChanged.connect(self.change_brush_opacity)
        self.control_layout.addWidget(QLabel("Brush Opacity"))
        self.control_layout.addWidget(self.opacity_slider)

        # Control deslizante para ajustar la tolerancia del relleno
        self.tolerance_slider = QSlider(Qt.Horizontal, self)
        self.tolerance_slider.setRange(0, 255)
        self.tolerance_slider.setValue(0)
        self.tolerance_slider.valueChanged.connect(self.change_tolerance)
        self.control_layout.addWidget(QLabel("Tolerance"))
        self.control_layout.addWidget(self.tolerance_slider)

        self.tolerance = 0

        # Paleta de colores
        self.color_palette = ["#FCDAB9", "#F8B3A4", "#F78888", "#A26B7F", "#738089", "#A4B7B9"]
        self.color_buttons = []
        self.palette_frame = QFrame(self)
        self.palette_layout = QGridLayout(self.palette_frame)

        for i, color in enumerate(self.color_palette):
            color_btn = QPushButton()
            color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            color_btn.setFixedSize(50, 50)
            color_btn.clicked.connect(lambda checked, col=color: self.set_color(col))
            self.color_buttons.append(color_btn)
            self.palette_layout.addWidget(color_btn, i // 2, i % 2)

        self.control_layout.addWidget(self.palette_frame)

        self.recent_colors = []
        self.recent_palette_frame = QFrame(self)
        self.recent_palette_layout = QGridLayout(self.recent_palette_frame)
        self.update_recent_palette()

        self.control_layout.addWidget(self.recent_palette_frame)

        self.custom_color_btn = QPushButton("Custom Color", self)
        self.custom_color_btn.clicked.connect(self.choose_color)
        self.control_layout.addWidget(self.custom_color_btn)

        self.layout.addWidget(self.control_frame)

        self.setLayout(self.layout)

    def change_brush_size(self, value):
        self.brush_size = value

    def change_brush_opacity(self, value):
        self.brush_opacity = value / 100.0

    def tabletEvent(self, tabletEvent):
        if tabletEvent.type() in (QTabletEvent.TabletPress, QTabletEvent.TabletMove):
            self.brush_size = max(1, int(tabletEvent.pressure() * 50))
            current_point = QPoint(tabletEvent.x(), tabletEvent.y())
            if self.pen_is_down:
                self.draw_line(self.last_point, current_point)
            self.last_point = current_point
            self.pen_is_down = True
        elif tabletEvent.type() == QTabletEvent.TabletRelease:
            self.pen_is_down = False
            self.last_point = QPoint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.canvas)

    def mouseMoveEvent(self, event):
        if self.pen_is_down:
            current_point = event.pos()
            self.draw_line(self.last_point, current_point)
            self.last_point = current_point
            self.update()

    def mousePressEvent(self, event):
        if self.fill_btn.isChecked():
            # Si el botón de relleno está activo, iniciamos el relleno en el punto clicado
            start_pos = event.pos()
            fill_color = QColor(self.brush_color)
            self.fill_canvas(start_pos, fill_color)
        else:
            # Si no estamos en modo relleno, usamos el pincel normal
            self.pen_is_down = True
            self.last_point = event.pos()

    def mouseReleaseEvent(self, event):
        self.pen_is_down = False
        self.last_point = QPoint()

    def draw_line(self, start_point, end_point):
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.Antialiasing)
        brush_color_with_opacity = QColor(self.brush_color)
        brush_color_with_opacity.setAlphaF(self.brush_opacity)
        if self.eraser_mode:
            painter.setPen(QPen(Qt.white, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        else:
            painter.setPen(QPen(brush_color_with_opacity, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(start_point, end_point)
        painter.end()
        self.canvas_label.setPixmap(QPixmap.fromImage(self.canvas))
        self.update()

    def clear_canvas(self):
        self.canvas.fill(Qt.white)
        self.canvas_label.setPixmap(QPixmap.fromImage(self.canvas))
        self.update()

    def toggle_eraser(self, checked):
        self.eraser_mode = checked
        if checked:
            self.brush_color = Qt.white
        else:
            self.brush_color = Qt.black

    def set_color(self, color):
        self.brush_color = QColor(color)
        self.eraser_mode = False
        self.update_recent_colors(color)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.brush_color = color
            self.eraser_mode = False
            self.update_recent_colors(color.name())

    def update_recent_colors(self, color):
        if color not in self.recent_colors:
            if len(self.recent_colors) >= 4:
                self.recent_colors.pop(0)
            self.recent_colors.append(color)
            self.update_recent_palette()

    def update_recent_palette(self):
        for i in reversed(range(self.recent_palette_layout.count())):
            widget = self.recent_palette_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        for i, color in enumerate(self.recent_colors):
            color_btn = QPushButton()
            color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            color_btn.setFixedSize(50, 50)
            color_btn.clicked.connect(lambda checked, col=color: self.set_color(col))
            self.recent_palette_layout.addWidget(color_btn, i // 2, i % 2)

    def change_tolerance(self, value):
        self.tolerance = value

    def fill_canvas(self, start_pos, fill_color):
        target_color = QColor(self.canvas.pixel(start_pos))
        if target_color != fill_color:
            self.flood_fill(start_pos, fill_color)
            self.canvas_label.setPixmap(QPixmap.fromImage(self.canvas))  # Actualizar la imagen después de rellenar
            self.update()

    def flood_fill(self, start, fill_color):
        width = self.canvas.width()
        height = self.canvas.height()

        # Obtener el color objetivo desde el punto clicado
        target_color = QColor(self.canvas.pixel(start.x(), start.y()))

        # Si el color objetivo es el mismo que el de relleno, no hacemos nada
        if self.is_similar_color(target_color, fill_color):
            return

        stack = [start]

        while stack:
            point = stack.pop()
            x, y = point.x(), point.y()

            # Verificamos que esté dentro del área del lienzo
            if x < 0 or x >= width or y < 0 or y >= height:
                continue

            # Si el píxel no tiene el color objetivo, se ignora
            current_color = QColor(self.canvas.pixel(x, y))
            if not self.is_similar_color(current_color, target_color):
                continue

            # Pintamos el píxel con el color de relleno
            self.canvas.setPixelColor(x, y, fill_color)

            # Añadimos los píxeles vecinos a la pila
            stack.extend([QPoint(x + 1, y), QPoint(x - 1, y), QPoint(x, y + 1), QPoint(x, y - 1)])

        # Actualizamos la visualización del lienzo
        self.canvas_label.setPixmap(QPixmap.fromImage(self.canvas))
        self.update()

    def is_similar_color(self, color1, color2):
        # Calcula la diferencia en el valor RGB entre dos colores
        return abs(color1.red() - color2.red()) <= self.tolerance and \
            abs(color1.green() - color2.green()) <= self.tolerance and \
            abs(color1.blue() - color2.blue()) <= self.tolerance


if __name__ == "__main__":
    app = QApplication(sys.argv)
    canvas = DrawingCanvas()
    canvas.show()
    app.exec_()
