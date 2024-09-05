import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class DrawingCanvas(QWidget):
    def __init__(self, parent=None):
        super(DrawingCanvas, self).__init__(parent)
        self.setWindowTitle("Prototipo BigOcto")
        
        # Set fixed size for the window
        self.setFixedSize(1200, 800)

        # Initial brush settings
        self.brush_color = Qt.black
        self.brush_size = 5
        self.last_point = QPoint()
        self.pen_is_down = False
        self.eraser_mode = False

        # Create layout
        self.layout = QHBoxLayout(self)

        # Create and add the canvas
        self.canvas = QImage(800, 800, QImage.Format_RGB888)
        self.canvas.fill(Qt.white)
        self.canvas_label = QLabel(self)
        self.canvas_label.setPixmap(QPixmap.fromImage(self.canvas))
        self.layout.addWidget(self.canvas_label, 1)

        # Create a frame for controls
        self.control_frame = QFrame(self)
        self.control_frame.setFixedWidth(300)
        self.control_layout = QVBoxLayout(self.control_frame)

        # Create a spacer to push controls to the right
        self.spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.control_layout.addItem(self.spacer)

        # Clear button
        self.clear_btn = QPushButton("Clear", self)
        self.clear_btn.clicked.connect(self.clear_canvas)
        self.control_layout.addWidget(self.clear_btn)

        # Eraser button
        self.eraser_btn = QPushButton("Eraser", self)
        self.eraser_btn.setCheckable(True)
        self.eraser_btn.toggled.connect(self.toggle_eraser)
        self.control_layout.addWidget(self.eraser_btn)

        # Color Palette
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

        # Recent Colors
        self.recent_colors = []
        self.recent_palette_frame = QFrame(self)
        self.recent_palette_layout = QGridLayout(self.recent_palette_frame)
        self.update_recent_palette()

        # Add recent colors to layout
        self.control_layout.addWidget(self.recent_palette_frame)

        # Custom Color Button
        self.custom_color_btn = QPushButton("Custom Color", self)
        self.custom_color_btn.clicked.connect(self.choose_color)
        self.control_layout.addWidget(self.custom_color_btn)

        # Add control frame to layout
        self.layout.addWidget(self.control_frame)

        self.setLayout(self.layout)

    def tabletEvent(self, tabletEvent):
        if tabletEvent.type() in (QTabletEvent.TabletPress, QTabletEvent.TabletMove):
            self.brush_size = max(1, int(tabletEvent.pressure() * 50))  # Scale pressure to a brush size
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
        self.pen_is_down = True
        self.last_point = event.pos()

    def mouseReleaseEvent(self, event):
        self.pen_is_down = False
        self.last_point = QPoint()

    def draw_line(self, start_point, end_point):
        painter = QPainter(self.canvas)
        if self.eraser_mode:
            painter.setPen(QPen(Qt.white, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        else:
            painter.setPen(QPen(self.brush_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(start_point, end_point)
        painter.end()  # Make sure to end the painter
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
                self.recent_colors.pop(0)  # Remove oldest color
            self.recent_colors.append(color)
            self.update_recent_palette()

    def update_recent_palette(self):
        # Clear existing widgets
        for i in reversed(range(self.recent_palette_layout.count())):
            widget = self.recent_palette_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Add recent colors to the palette
        for i, color in enumerate(self.recent_colors):
            color_btn = QPushButton()
            color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            color_btn.setFixedSize(50, 50)
            color_btn.clicked.connect(lambda checked, col=color: self.set_color(col))
            self.recent_palette_layout.addWidget(color_btn, i // 2, i % 2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    canvas = DrawingCanvas()
    canvas.show()
    app.exec_()
