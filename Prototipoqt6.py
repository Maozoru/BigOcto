import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from layer_manager import LayerManager

class DrawingCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prototipo BigOcto")
        self.setFixedSize(1200, 800)

        self.brush_color = Qt.GlobalColor.black
        self.brush_size = 5
        self.brush_opacity = 1.0
        self.last_point = QPoint()
        self.pen_is_down = False
        self.eraser_mode = False
        self.selection_active = False  # Estado de la selección

        self.layout = QHBoxLayout(self)

        # Inicializa el lienzo
        self.canvas = QImage(800, 800, QImage.Format.Format_RGB888)
        self.canvas.fill(Qt.GlobalColor.white)
        self.canvas_label = QLabel(self)
        self.canvas_label.setPixmap(QPixmap.fromImage(self.canvas))
        self.layout.addWidget(self.canvas_label, 1)

        # Configuración del marco de control
        self.control_frame = QFrame(self)
        self.control_frame.setFixedWidth(300)
        self.control_layout = QVBoxLayout(self.control_frame)

        self.spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.control_layout.addItem(self.spacer)

        # Grupo de botones para herramientas
        self.tool_button_group = QButtonGroup(self)

        # Botón de selección
        self.select_btn = QPushButton("Select", self)
        self.select_btn.setCheckable(True)
        self.select_btn.toggled.connect(self.toggle_selection)
        self.tool_button_group.addButton(self.select_btn)
        self.control_layout.addWidget(self.select_btn)

        # Botón de limpiar
        self.clear_btn = QPushButton("Clear", self)
        self.clear_btn.clicked.connect(self.clear_canvas)
        self.control_layout.addWidget(self.clear_btn)

        # Botón de borrador
        self.eraser_btn = QPushButton("Eraser", self)
        self.eraser_btn.setCheckable(True)
        self.eraser_btn.toggled.connect(self.toggle_eraser)
        self.tool_button_group.addButton(self.eraser_btn)
        self.control_layout.addWidget(self.eraser_btn)

        # Botón de relleno
        self.fill_btn = QPushButton("Fill", self)
        self.fill_btn.setCheckable(True)
        self.tool_button_group.addButton(self.fill_btn)
        self.control_layout.addWidget(self.fill_btn)

        # Control deslizante para ajustar el tamaño del pincel
        self.size_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(self.brush_size)
        self.size_slider.valueChanged.connect(self.change_brush_size)
        self.control_layout.addWidget(QLabel("Brush Size"))
        self.control_layout.addWidget(self.size_slider)

        # Control deslizante para ajustar la opacidad del pincel
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.opacity_slider.setRange(1, 100)
        self.opacity_slider.setValue(int(self.brush_opacity * 100))
        self.opacity_slider.valueChanged.connect(self.change_brush_opacity)
        self.control_layout.addWidget(QLabel("Brush Opacity"))
        self.control_layout.addWidget(self.opacity_slider)

        # Control deslizante para ajustar la tolerancia del relleno
        self.tolerance_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.tolerance_slider.setRange(0, 255)
        self.tolerance_slider.setValue(0)
        self.tolerance_slider.valueChanged.connect(self.change_tolerance)
        self.control_layout.addWidget(QLabel("Tolerance"))
        self.control_layout.addWidget(self.tolerance_slider)

        self.tolerance = 0

        # Paleta de colores predeterminadas
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

    def toggle_selection(self, checked):
        self.selection_active = checked
        # Desactivar otros botones si la selección está activa
        if checked:
            self.eraser_btn.setChecked(False)
            self.fill_btn.setChecked(False)
            self.eraser_mode = False  # Asegúrate de desactivar el borrador

    def change_brush_size(self, value):
        self.brush_size = value

    def change_brush_opacity(self, value):
        self.brush_opacity = value / 100.0

    def tabletEvent(self, event: QTabletEvent):
        # Ajustar el tamaño del pincel según la presión del lápiz
        if event.type() in (QEvent.Type.TabletPress, QEvent.Type.TabletMove):
            self.brush_size = max(1, int(event.pressure() * 50))  # Ajusta la escala si es necesario
            current_point = event.position().toPoint()  # Utiliza position() para obtener la posición local

            if self.pen_is_down:
                self.draw_line(self.last_point, current_point)

            self.last_point = current_point
            self.pen_is_down = True
        elif event.type() == QEvent.Type.TabletRelease:
            self.pen_is_down = False
            self.last_point = QPoint()

    def paintEvent(self, event):
        painter = QPainter(self)

    def mouseMoveEvent(self, event):
        if self.pen_is_down:
            current_point = event.position().toPoint()
            self.draw_line(self.last_point, current_point)
            self.last_point = current_point
            self.update()

    def mousePressEvent(self, event):
        if self.fill_btn.isChecked():
            start_pos = event.position().toPoint()
            fill_color = QColor(self.brush_color)
            self.fill_canvas(start_pos, fill_color)
        else:
            self.pen_is_down = True
            self.last_point = event.position().toPoint()

    def mouseReleaseEvent(self, event):
        self.pen_is_down = False
        self.last_point = QPoint()

    def draw_line(self, start_point, end_point):
        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        brush_color_with_opacity = QColor(self.brush_color)
        brush_color_with_opacity.setAlphaF(self.brush_opacity)
        if self.eraser_mode:
            painter.setPen(QPen(Qt.GlobalColor.white, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        else:
            painter.setPen(QPen(brush_color_with_opacity, self.brush_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.drawLine(start_point, end_point)
        painter.end()
        self.canvas_label.setPixmap(QPixmap.fromImage(self.canvas))
        self.update()

    def clear_canvas(self):
        self.canvas.fill(Qt.GlobalColor.white)
        self.canvas_label.setPixmap(QPixmap.fromImage(self.canvas))
        self.update()

    def toggle_eraser(self, checked):
        self.eraser_mode = checked
        if checked:
            self.brush_color = Qt.GlobalColor.white
            self.fill_btn.setChecked(False)
            self.select_btn.setChecked(False)  # Desactivar la selección
        else:
            self.brush_color = Qt.GlobalColor.black

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
            self.canvas_label.setPixmap(QPixmap.fromImage(self.canvas))
            self.update()

    def flood_fill(self, start, fill_color):
        width = self.canvas.width()
        height = self.canvas.height()

        target_color = QColor(self.canvas.pixel(start.x(), start.y()))

        if self.is_similar_color(target_color, fill_color):
            return

        stack = [start]

        while stack:
            point = stack.pop()
            x, y = point.x(), point.y()

            if x < 0 or x >= width or y < 0 or y >= height:
                continue

            current_color = QColor(self.canvas.pixel(x, y))
            if not self.is_similar_color(current_color, target_color):
                continue

            self.canvas.setPixelColor(x, y, fill_color)
            stack.extend([QPoint(x + 1, y), QPoint(x - 1, y), QPoint(x, y + 1), QPoint(x, y - 1)])

        self.canvas_label.setPixmap(QPixmap.fromImage(self.canvas))
        self.update()

    def is_similar_color(self, color1, color2):
        return (abs(color1.red() - color2.red()) <= self.tolerance and
                abs(color1.green() - color2.green()) <= self.tolerance and
                abs(color1.blue() - color2.blue()) <= self.tolerance)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    canvas = DrawingCanvas()
    canvas.show()
    app.exec()
