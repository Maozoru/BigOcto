import tkinter as tk
from tkinter.colorchooser import askcolor
from pynput import mouse

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Colorful Drawing App")

        # Crear un Frame para controles
        self.control_frame = tk.Frame(root, bg="lightgray", padx=5, pady=5)
        self.control_frame.grid(row=0, column=0, sticky="ew")

        # Paleta de colores fija
        self.color_palette = ["#FF5733", "#33FF57", "#3357FF", "#FF33A8", "#33FFF7", "#FFF933", "#A833FF"]
        self.brush_color = self.color_palette[0]
        self.brush_size = 5
        self.eraser_mode = False

        # Crear la paleta de colores
        for color in self.color_palette:
            btn = tk.Button(self.control_frame, bg=color, width=3, height=2, command=lambda col=color: self.set_color(col))
            btn.pack(side="left", padx=5)

        # Botón para seleccionar color personalizado
        self.custom_color_btn = tk.Button(self.control_frame, text="Custom Color", command=self.choose_color)
        self.custom_color_btn.pack(side="left", padx=5)

        # Botón para la goma de borrar
        self.eraser_btn = tk.Button(self.control_frame, text="Eraser", command=self.toggle_eraser)
        self.eraser_btn.pack(side="left", padx=5)

        # Control para el tamaño del pincel
        self.size_label = tk.Label(self.control_frame, text="Brush Size:")
        self.size_label.pack(side="left", padx=5)
        self.size_slider = tk.Scale(self.control_frame, from_=1, to=20, orient="horizontal", command=self.change_size)
        self.size_slider.set(self.brush_size)
        self.size_slider.pack(side="left", padx=5)

        # Botón para limpiar el lienzo
        self.clear_btn = tk.Button(self.control_frame, text="Clear", command=self.clear_canvas)
        self.clear_btn.pack(side="left", padx=5)

        # Lienzo de dibujo
        self.canvas = tk.Canvas(root, bg="white", width=500, height=500)
        self.canvas.grid(row=1, column=0, pady=10)

        # Eventos de dibujo
        self.canvas.bind('<Button-1>', self.start_draw)
        self.canvas.bind('<B1-Motion>', self.draw)

        # Inicialización de pynput para captura del mouse
        self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move)
        self.mouse_listener.start()

    def set_color(self, new_color):
        self.brush_color = new_color
        self.eraser_mode = False

    def choose_color(self):
        color = askcolor()[1]  # Muestra un diálogo de selección de color
        if color:
            self.brush_color = color
            self.eraser_mode = False

    def toggle_eraser(self):
        self.eraser_mode = not self.eraser_mode
        if self.eraser_mode:
            self.brush_color = "white"  # Usar blanco para borrar

    def change_size(self, new_size):
        self.brush_size = int(new_size)

    def clear_canvas(self):
        self.canvas.delete("all")

    def start_draw(self, event):
        self.last_x, self.last_y = event.x, event.y

    def draw(self, event):
        x, y = event.x, event.y
        if self.eraser_mode:
            self.canvas.create_oval(x - self.brush_size, y - self.brush_size, x + self.brush_size, y + self.brush_size, fill="white", outline="white")
        else:
            self.canvas.create_line(self.last_x, self.last_y, x, y, width=self.brush_size, fill=self.brush_color, capstyle=tk.ROUND, smooth=True)
        self.last_x, self.last_y = x, y

    def on_mouse_move(self, x, y):
        # Aquí puedes ajustar el tamaño del pincel o realizar otras acciones en función del movimiento del mouse
        pass

# Inicializar la aplicación
root = tk.Tk()
app = DrawingApp(root)
root.mainloop()
