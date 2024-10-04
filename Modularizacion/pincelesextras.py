class PixelBrush:
    def __init__(self, canvas):
        self.canvas = canvas
        self.color = QColor(0, 0, 0)  # Color negro por defecto

    def draw(self, x, y):
        # Dibuja un solo pixel en la posición (x, y)
        self.canvas.setPixel(x, y, self.color.rgb())
