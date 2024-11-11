import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PIL import Image as PILImage
from capa import Capa
from administrador_capas import AdministradorCapas
from estilos import *
from herramientas import *
from barra_menu import BarraMenu  # Importar la clase de barra de menú

class LienzoDeDibujo(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prototipo BigOcto")
        self.setFixedSize(1200, 800)

        # Crear un widget central y establecer el layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.diseno_principal = QHBoxLayout(self.central_widget)

        # Create the scroll area
        self.scroll_area = QScrollArea(self)  # Initialize the scroll area
        self.scroll_area.setWidgetResizable(True)  # Allow the widget to resize
        self.diseno_principal.addWidget(self.scroll_area)  # Add scroll area to the main layout

        # Crear la barra de menú
        self.menu_bar = BarraMenu(self)  # Asegúrate de pasar la instancia correcta
        self.setMenuBar(self.menu_bar)  # Establecer la barra de menú

        # Crear los atajos
        self.setup_shortcuts()

        # Atributos del pincel y herramientas
        self.color_pincel = Qt.GlobalColor.black
        self.tamaño_pincel = 5
        self.opacidad_pincel = 1.0
        self.ultimo_punto = QPoint()
        self.pincel_abajo = False
        self.modo_borrador = False
        self.seleccion_activa = False  # Estado de la selección
        self.modo_pixel = False  # Modo del pincel: False = Normal, True = Pixelado
        
        # Atributos de zoom
        self.zoom_factor = 1.0  # Factor de zoom inicial
        self.zoom_step = 0.1     # Incremento/decremento del zoom
        self.mouse_pos = None  # Asegúrate de definir cómo se obtiene la posición del mouse
        self.previous_zoom_pos = (0, 0)  # Guardamos la posición previa del zoom
        self.zoom_locked = False  # Bloqueo del zoom

        # Inicializa el lienzo
        self.lienzo = QImage(800, 800, QImage.Format.Format_ARGB32)
        self.lienzo.fill(Qt.GlobalColor.white)
        self.etiqueta_lienzo = QLabel(self)
        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(self.lienzo))
        self.diseno_principal.addWidget(self.etiqueta_lienzo, 1)

        self.scroll_area.setWidget(self.etiqueta_lienzo)

        # Configuración del marco de control
        self.marco_control = QFrame(self)
        self.marco_control.setFixedWidth(300)
        self.diseno_control = QVBoxLayout(self.marco_control)

        self.espaciador = QSpacerItem(20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.diseno_control.addItem(self.espaciador)

        # Botón de cambiar tema
        self.boton_cambiar_tema = QPushButton("Cambiar tema", self)
        self.menu_cambiar_tema = QMenu(self.boton_cambiar_tema)
        self.menu_cambiar_tema.addAction("Oscuro", lambda: self.change_theme('tema_oscuro'))
        self.menu_cambiar_tema.addAction("Claro", lambda: self.change_theme('tema_claro'))
        self.menu_cambiar_tema.addAction("Rosita", lambda: self.change_theme('tema_rosa'))
        self.boton_cambiar_tema.setMenu(self.menu_cambiar_tema)
        self.diseno_control.addWidget(self.boton_cambiar_tema)

        # Inicializar capas
        self.capas = [Capa("Capa 1", QImage(800, 800, QImage.Format.Format_ARGB32))]
        self.capas[0].imagen.fill(Qt.GlobalColor.white)
        self.indice_capa_actual = 0

        # Botón para abrir la ventana de administración de capas
        self.boton_administrar_capas = QPushButton(" Administrar capas", self)
        self.boton_administrar_capas.clicked.connect(self.abrir_administrador_capas)
        self.diseno_control.addWidget(self.boton_administrar_capas)

        # Mantener la referencia de la ventana de capas
        self.ventana_administrador_capas = None

        # Grupo de botones para herramientas
        self.grupo_botones_herramientas = QButtonGroup(self)

        # Botón de selección
        self.boton_seleccionar = QPushButton("Selección", self)
        self.boton_seleccionar.setCheckable(True)
        self.boton_seleccionar.toggled.connect(self.toggle_selection)
        self.grupo_botones_herramientas.addButton(self.boton_seleccionar)
        self.diseno_control.addWidget(self.boton_seleccionar)

        # Botón de limpiar
        self.boton_limpiar = QPushButton("Limpiar", self)
        self.boton_limpiar.clicked.connect(self.clear_canvas)
        self.diseno_control.addWidget(self.boton_limpiar)

        # Botón de borrador
        self.boton_borrador = QPushButton("Borrador", self)
        self.boton_borrador.setCheckable(True)
        self.boton_borrador.toggled.connect(self.toggle_eraser)
        self.grupo_botones_herramientas.addButton(self.boton_borrador)
        self.diseno_control.addWidget(self.boton_borrador)

        # Botón de relleno
        self.boton_rellenar = QPushButton("Rellenar", self)
        self.boton_rellenar.setCheckable(True)
        self.grupo_botones_herramientas.addButton(self.boton_rellenar)
        self.diseno_control.addWidget(self.boton_rellenar)

        # Botón de pincel con submenú
        self.boton_menu_pincel = QPushButton("Pincel...", self)
        self.menu_pincel = QMenu(self)

        self.accion_pincel_normal = QAction("Normal", self)
        self.accion_pincel_normal.triggered.connect(self.select_normal_brush)

        self.accion_pincel_pixel = QAction("Pixel", self)
        self.accion_pincel_pixel.triggered.connect(self.select_pixel_brush)

        self.menu_pincel.addAction(self.accion_pincel_normal)
        self.menu_pincel.addAction(self.accion_pincel_pixel)

        self.boton_menu_pincel.setMenu(self.menu_pincel)
        self.diseno_control.addWidget(self.boton_menu_pincel)

        # Control deslizante para ajustar el tamaño del pincel
        self.control_deslizante_tamaño = QSlider(Qt.Orientation.Horizontal, self)
        self.control_deslizante_tamaño.setRange(1, 50)
        self.control_deslizante_tamaño.setValue(self.tamaño_pincel)
        self.control_deslizante_tamaño.valueChanged.connect(self.change_brush_size)
        self.diseno_control.addWidget(QLabel("Tamaño del pincel"))
        self.diseno_control.addWidget(self.control_deslizante_tamaño)

        # Control deslizante para ajustar la opacidad del pincel
        self.control_deslizante_opacidad = QSlider(Qt.Orientation.Horizontal, self)
        self.control_deslizante_opacidad.setRange(1, 100)
        self.control_deslizante_opacidad.setValue(int(self.opacidad_pincel * 100))
        self.control_deslizante_opacidad.valueChanged.connect(self.change_brush_opacity)
        self.diseno_control.addWidget(QLabel("Opacidad del pincel"))
        self.diseno_control.addWidget(self.control_deslizante_opacidad)

        # Control deslizante para ajustar la tolerancia del relleno
        self.control_deslizante_tolerancia = QSlider(Qt.Orientation.Horizontal, self)
        self.control_deslizante_tolerancia.setRange(0, 255)
        self.control_deslizante_tolerancia.setValue(0)
        self.control_deslizante_tolerancia.valueChanged.connect(self.change_tolerance)
        self.diseno_control.addWidget(QLabel("Tolerancia(Relleno)"))
        self.diseno_control.addWidget(self.control_deslizante_tolerancia)

        self.tolerancia = 0

        # Paleta de colores predeterminados
        self.paleta_colores = ["#FCDAB9", "#F8B3A4", "#F78888", "#A26B7F", "#738089", "#A4B7B9"]
        self.botones_colores = []
        self.marco_paleta = QFrame(self)
        self.diseno_paleta = QGridLayout(self.marco_paleta)

        for i, color in enumerate(self.paleta_colores):
            boton_color = QPushButton()
            boton_color.setStyleSheet(f"background-color: {color }; border: 1px solid black;")
            boton_color.setFixedSize(50, 50)
            boton_color.clicked.connect(lambda checked, col=color: self.set_color(col))
            self.botones_colores.append(boton_color)
            self.diseno_paleta.addWidget(boton_color, i // 2, i % 2)

        self.diseno_control.addWidget(self.marco_paleta)

        # Paleta de colores recientes
        self.colores_recientes = []
        self.marco_paleta_reciente = QFrame(self)
        self.diseno_paleta_reciente = QGridLayout(self.marco_paleta_reciente)
        self.update_recent_palette()

        self.diseno_control.addWidget(self.marco_paleta_reciente)

        # Botón de color personalizado
        self.boton_color_personalizado = QPushButton("Custom Color", self)
        self.boton_color_personalizado.clicked.connect(self.choose_color)
        self.diseno_control.addWidget(self.boton_color_personalizado)

        self.diseno_principal.addWidget(self.marco_control)
    
    def setup_shortcuts(self):
        # Crear atajo para zoom in
        self.shortcut_zoom_in = QShortcut(QKeySequence("Ctrl++"), self)
        self.shortcut_zoom_in.activated.connect(self.zoom_in)

        # Crear atajo para zoom out
        self.shortcut_zoom_out = QShortcut(QKeySequence("Ctrl+-"), self)
        self.shortcut_zoom_out.activated.connect(self.zoom_out)

        # Crear atajo para deshacer
        self.shortcut_undo = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.shortcut_undo.activated.connect(self.undo)

        # Crear atajo para rehacer
        self.shortcut_redo = QShortcut(QKeySequence("Ctrl+Y"), self)
        self.shortcut_redo.activated.connect(self.redo)

        # Crear atajo para guardar
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.guardar_lienzo)

        # Crear atajo para nueva capa
        self.shortcut_new = QShortcut(QKeySequence("Ctrl+N"), self)
        self.shortcut_new.activated.connect(self.clear_canvas)

        # Crear atajo para pincel
        self.shortcut_brush = QShortcut(QKeySequence("B"), self)
        self.shortcut_brush.activated.connect(self.seleccion_normie)

        # Crear atajo para pixel
        self.shortcut_brush = QShortcut(QKeySequence("P"), self)
        self.shortcut_brush.activated.connect(self.seleccion_pixel)

        # Crear atajo para cambiar color
        self.shortcut_color = QShortcut(QKeySequence("C"), self)
        self.shortcut_color.activated.connect(self.choose_color)

    def undo(self):
        """Deshacer la última acción."""
        print("Deshacer acción")

    def redo(self):
        """Rehacer la última acción."""
        print("Rehacer acción")

    def abrir_administrador_capas(self):
        """ Abre la ventana de administración de capas. """
        if self.ventana_administrador_capas is None:
            self.ventana_administrador_capas = AdministradorCapas(self)
        self.ventana_administrador_capas.show()

    def crear_nueva_capa(self, name="Nueva Capa"):
        nueva_capa = Capa(name, QImage(800, 800, QImage.Format.Format_ARGB32))
        nueva_capa.imagen.fill(Qt.GlobalColor.transparent)  # Transparente por defecto
        self.capas.append(nueva_capa)
        
        # Seleccionar la nueva capa como activa
        self.indice_capa_actual = len(self.capas) - 1

        # Actualizar el lienzo
        self.update_canvas()

    def eliminar_capa(self, indice):
        """ Elimina una capa y actualiza el lienzo. """
        if len(self.capas) > 1:
            del self.capas[indice]
            self.indice_capa_actual = min(self.indice_capa_actual, len(self.capas) - 1)
            self.update_canvas()  # Actualiza la visualización
        else:
            print("No se puede eliminar la última capa")

    def bloquear_capa(self, indice):
        """ Bloquea la capa seleccionada. """
        if 0 <= indice < len(self.capas):
            self.capas[indice].bloquear()
            self.update_canvas()

    def desbloquear_capa(self, indice):
        """ Desbloquea la capa seleccionada. """
        if 0 <= indice < len(self.capas):
            self.capas[indice].desbloquear()
            self.update_canvas()

    def ajustar_opacidad(self, indice, nueva_opacidad):
        """ Ajusta la opacidad de la capa especificada. """
        if 0 <= indice < len(self.capas):
            self.capas[indice].ajustar_opacidad(nueva_opacidad)
            self.update_canvas()

    def ocultar_capa(self, indice):
        """ Oculta la capa y actualiza el lienzo. """
        if 0 <= indice < len(self.capas):
            self.capas[indice].visible = False
            self.update_canvas()  # Actualiza el lienzo

    def mostrar_capa(self, indice):
        """ Muestra la capa y actualiza el lienzo. """
        if 0 <= indice < len(self.capas):
            self.capas[indice].visible = True
            self.update_canvas()  # Actualiza el lienzo
    
    def update_canvas(self):
        """ Actualiza la visualización del lienzo con todas las capas visibles combinadas. """
        lienzo_completo = QImage(self.lienzo.size(), QImage.Format.Format_RGBA8888)
        lienzo_completo.fill(Qt.GlobalColor.transparent)  # Llenar con transparencia

        # Crear un pintor para dibujar en el lienzo
        painter = QPainter(lienzo_completo)

        # Dibujar un fondo blanco
        painter.fillRect(0, 0, lienzo_completo.width(), lienzo_completo.height(), Qt.GlobalColor.white)

        # Dibujar todas las capas visibles
        for capa in self.capas:
            if capa.visible:  # Solo combinar capas visibles
                lienzo_completo = self.combinar_imagenes(lienzo_completo, capa.imagen, capa.opacidad)

        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(lienzo_completo)) 
        self.update()
    
    def fusionar_capas(self, indice_capa):
        """ Fusiona la capa actual con la capa inferior . """
        if indice_capa > 0 and indice_capa < len(self.capas):
            capa_superior = self.capas[indice_capa]
            capa_inferior = self.capas[indice_capa - 1]

            # Crear un nuevo QImage para la capa fusionada
            nueva_imagen = QImage(capa_superior.imagen.size(), QImage.Format.Format_ARGB32)
            nueva_imagen.fill(Qt.GlobalColor.transparent)

            # Dibujar la capa superior sobre la inferior
            painter = QPainter(nueva_imagen)
            painter.drawImage(0, 0, capa_inferior.imagen)
            painter.drawImage(0, 0, capa_superior.imagen)
            painter.end()

            # Reemplazar la capa superior con la nueva imagen fusionada
            self.capas[indice_capa - 1].imagen = nueva_imagen
            self.eliminar_capa(indice_capa)  # Eliminar la capa superior después de fusionar

            # Actualizar el lienzo
            self.update_canvas()

    def renombrar_capa(self, indice_capa, nuevo_nombre):
        """ Renombra la capa especificada por el índice. """
        if 0 <= indice_capa < len(self.capas):
            self.capas[indice_capa].renombrar(nuevo_nombre)  # Llama al método renombrar de la clase Capa
            self.update_canvas()  # Actualiza el lienzo para reflejar el cambio
    
    def clonar_capa(self, indice_capa):
        """ Clona la capa especificada por el índice. """
        if 0 <= indice_capa < len(self.capas):
            capa_a_clonar = self.capas[indice_capa]
            nueva_capa = capa_a_clonar.clonar()  # Usa el método clonar de la clase Capa
            self.capas.append(nueva_capa)  # Agrega la nueva capa a la lista de capas
            self.indice_capa_actual = len(self.capas) - 1  # Seleccionar la nueva capa como activa
            self.update_canvas()  # Actualizar el lienzo
    
    def reorganizar_capas(self, indice_capa, nueva_posicion):
        """ Reorganiza la capa especificada por el índice a una nueva posición. """
        if 0 <= indice_capa < len(self.capas) and 0 <= nueva_posicion < len(self.capas):
            # Extrae la capa que se va a mover
            capa = self.capas.pop(indice_capa)
            # Inserta la capa en la nueva posición
            self.capas.insert(nueva_posicion, capa)
            self.update_canvas()  # Actualiza el lienzo para reflejar el cambio

    def ajustar_opacidad(self, indice, opacidad):
        self.capas[indice].opacidad = opacidad
        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(self.capas[self.indice_capa_actual].imagen))
        self.update()

    def set_mouse_position(self, pos):
        """Actualiza la posición del mouse"""
        self.mouse_pos = pos

    def wheelEvent(self, event: QWheelEvent):
        """Maneja el evento de la rueda del ratón para hacer zoom con Ctrl"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Detectar la dirección de la rueda
            if event.angleDelta().y() > 0:  # Si rueda hacia arriba
                self.zoom_in()
            else:  # Si rueda hacia abajo
                self.zoom_out()
        else:
            # Aquí puedes agregar otros comportamientos si es necesario
            super().wheelEvent(event)

    def zoom_in(self):
        """Aumenta el zoom del lienzo."""
        self.zoom_factor += self.zoom_step
        self.update_zoom()

    def zoom_out(self):
        """Disminuye el zoom del lienzo."""
        self.zoom_factor = max(0.1, self.zoom_factor - self.zoom_step)
        self.update_zoom()

    def update_zoom(self):
        """Actualiza la visualización del lienzo según el factor de zoom y la posición del mouse"""
        if self.mouse_pos is None:
            return  # Si no hay una posición del mouse, no hacer nada
        
        # Obtenemos la posición del mouse en el lienzo
        mouse_x, mouse_y = self.mouse_pos.x(), self.mouse_pos.y()
        print(f"Posición del mouse antes del zoom: ({mouse_x}, {mouse_y})")

        # Calculamos el tamaño de la imagen escalada
        scaled_width = self.lienzo.width() * self.zoom_factor
        scaled_height = self.lienzo.height() * self.zoom_factor
        print(f"Tamaño escalado después del zoom: ({scaled_width}, {scaled_height})")

        # Calculamos el tamaño previo (con el zoom anterior)
        prev_scaled_width = self.lienzo.width() * (self.zoom_factor - self.zoom_step)
        prev_scaled_height = self.lienzo.height() * (self.zoom_factor - self.zoom_step)
        print(f"Tamaño previo al zoom: ({prev_scaled_width}, {prev_scaled_height})")

        # Calculamos el desplazamiento necesario para mantener la zona debajo del mouse
        offset_x = (mouse_x * (scaled_width - prev_scaled_width)) / self.lienzo.width()
        offset_y = (mouse_y * (scaled_height - prev_scaled_height)) / self.lienzo.height()

        print(f"Desplazamiento calculado - offset_x: {offset_x}, offset_y: {offset_y}")

        # Aplicamos el zoom centrado en el mouse
        scaled_image = self.lienzo.scaled(self.lienzo.size() * self.zoom_factor,
                                          Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)

        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(scaled_image))

        # Guardamos la posición de la vista después de hacer el zoom
        self.previous_zoom_pos = (mouse_x - offset_x, mouse_y - offset_y)

        # Calculamos las nuevas posiciones de la vista (mantenemos la posición relativa)
        new_pos_x, new_pos_y = self.previous_zoom_pos

        # Aseguramos que las nuevas posiciones no se desborden fuera del lienzo
        new_pos_x = max(0, min(new_pos_x, scaled_width - self.lienzo.width()))
        new_pos_y = max(0, min(new_pos_y, scaled_height - self.lienzo.height()))

        print(f"Nueva posición de la imagen después del zoom: ({new_pos_x}, {new_pos_y})")

        # Para mover la imagen con el desplazamiento calculado, usamos `QScrollArea`
        self.scroll_area.horizontalScrollBar().setValue(int(new_pos_x))
        self.scroll_area.verticalScrollBar().setValue(int(new_pos_y))

        # Bloquear el zoom hasta el siguiente cambio de vista
        self.zoom_locked = True

        self.update()  # Actualiza la ventana para reflejar los cambios

    def activar_seleccion(self, checked):
        self.seleccion_activa = checked

    def activar_goma(self, checked):
        self.modo_borrador = checked

    def seleccion_normie(self):
        self.modo_pixel = False

    def seleccion_pixel(self):
        self.modo_pixel = True

    def tamañopincel(self, value):
        self.tamaño_pincel = value

    def opacidadpincel(self, value):
        self.opacidad_pincel = value / 100.0

    def toleranciadelrelleno(self, value):
        self.tolerancia = value

    def set_color(self, color):
        self.color_pincel = QColor(color)
        if color not in self.colores_recientes:
            self.colores_recientes.append(color)
            if len(self.colores_recientes) > 6:
                self.colores_recientes.pop(0)
            self.update_recent_palette()

    def update_recent_palette(self):
        """ Actualiza la visualización de los colores recientes. """
        for i, color in enumerate(self.colores_recientes):
            btn = QPushButton()
            btn.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            btn.setFixedSize(50, 50)
            btn.clicked.connect(lambda checked, col=color: self.set_color(col))
            self.diseno_paleta_reciente.addWidget(btn, i // 2, i % 2)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.set_color(color.name())

    def clear_canvas(self):
        """ Limpia el lienzo actual. """
        self.lienzo.fill(Qt.GlobalColor.transparent)
        self.update_canvas()

    def change_theme(self, theme_name):
        """ Cambia el tema de la aplicación. """
        if theme_name == 'tema_oscuro':
            self.setStyleSheet(tema_oscuro)
        elif theme_name == 'tema_claro':
            self.setStyleSheet(tema_claro)
        elif theme_name == 'tema_rosa':
            self.setStyleSheet(tema_rosa)

    def toggle_selection(self, checked):
        self.seleccion_activa = checked
        # Desactivar otros botones si la selección está activa
        if checked:
            self.boton_borrador.setChecked(False)
            self.boton_rellenar.setChecked(False)
            self.modo_borrador = False  # Asegúrate de desactivar el borrador

    def select_normal_brush(self):
        self.modo_pixel = False  # Desactiva el modo pixel
        print("Modo pincel normal activado")

    def select_pixel_brush(self):
        self.modo_pixel = True  # Activa el modo pixel
        print("Modo pincel pixelado Activado")

    def change_brush_size(self, value):
        self.tamaño_pincel = value

    def change_brush_opacity(self, value):
        self.opacidad_pincel = value / 100.0

    def tabletEvent(self, event: QTabletEvent):
        # Ajustar el tamaño del pincel según la presión del lápiz
        if event.type() in (QEvent.Type.TabletPress, QEvent.Type.TabletMove):
            self.tamaño_pincel = max(1, int(event.pressure() * 50))  # Ajusta la escala si es necesario
            current_point = event.position().toPoint()  # Utiliza position() para obtener la posición local

            if self.pincel_abajo:
                self.draw_on_canvas(current_point)  # Llama a la función de dibujo en lugar de draw_line

            self.ultimo_punto = current_point
            self.pincel_abajo = True
        elif event.type() == QEvent.Type.TabletRelease:
            self.tabletReleaseEvent(event)  # Manejo de liberación de la tableta

    def draw_on_canvas(self, current_point):
        painter = QPainter(self.lienzo)

        # Configura el color y la opacidad del pincel
        brush_color_with_opacity = QColor(self.color_pincel)
        brush_color_with_opacity.setAlphaF(self.opacidad_pincel)

        # Si el borrador está activo, dibuja en blanco
        if self.modo_borrador:
            painter.setPen(QPen(Qt.GlobalColor.white, self.tamaño_pincel, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        else:
            if self.modo_pixel:
                # Configuración para pincel pixelado (sin suavizado)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
                painter.setPen(QPen(brush_color_with_opacity, self.tamaño_pincel, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.BevelJoin))
            else:
                # Configuración para pincel normal (con suavizado)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                painter.setPen(QPen(brush_color_with_opacity, self.tamaño_pincel, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

        # Dibuja la línea
        painter.drawLine(self.ultimo_punto, current_point)
        painter.end()

        # Actualiza el lienzo
        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(self.lienzo))
        self.update()

    def tabletReleaseEvent(self, event: QTabletEvent):
        """ Maneja el evento de liberación de la tableta para detener el dibujo. """
        self.pincel_abajo = False
        self.ultimo_punto = QPoint()  # Restablecer el último punto cuando se levanta el lápiz

    def tabletPressEvent(self, event: QTabletEvent):
        """ Maneja el evento de presión de la tableta para comenzar a dibujar. """
        self.pincel_abajo = True
        self.ultimo_punto = event.position().toPoint()  # Establecer el último punto en la posición actual

    def paintEvent(self, event):
        painter = QPainter(self)

    def mousePressEvent(self, event):
        """Cuando se presiona el ratón, verificamos si se está dibujando"""
        if self.zoom_locked:
            # Si el zoom está bloqueado, no permitimos que se reestablezca la posición
            return
        
        if self.boton_rellenar.isChecked():
            start_pos = event.position().toPoint()
            fill_color = QColor(self.color_pincel)
            self.fill_canvas(start_pos, fill_color)
        else:
            self.pincel_abajo = True
            self.ultimo_punto = event.position().toPoint()
            # Guardamos la posición actual del mouse para asegurarnos que el zoom no cambie
            self.mouse_pos = event.pos()  # Actualizamos la posición del mouse cuando se presiona el ratón

    def mouseMoveEvent(self, event):
        """Cuando se mueve el ratón, verificamos si estamos dibujando"""
        self.set_mouse_position(event.pos())
        if self.pincel_abajo:
            current_point = event.position().toPoint()
            self.draw_on_canvas(current_point)  # Llama a la función de dibujo en lugar de draw_line

    def mouseReleaseEvent(self, event):
        """Cuando se suelta el ratón, desbloqueamos el zoom si es necesario"""
        self.pincel_abajo = False
        self.ultimo_punto = QPoint()
        if self.zoom_locked:
            self.zoom_locked = False  # Desbloqueamos el zoom después del trazo

        # Si el zoom está bloqueado, no se vuelve a aplicar
        super().mouseReleaseEvent(event)

    def update_canvas(self):
        """ Actualiza la visualización del lienzo con todas las capas. """
        lienzo_completo = QImage(self.lienzo.size(), QImage.Format.Format_RGBA8888)
        lienzo_completo.fill(Qt.GlobalColor.transparent)

        # Dibujar todas las capas visibles
        for capa in self.capas:
            lienzo_completo = self.combinar_imagenes(lienzo_completo, capa.imagen)

        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(lienzo_completo))

    def combinar_imagenes(self, imagen1, imagen2):
        # Create a new QImage that contains the combination of imagen1 and imagen2
        lienzo_completo = QImage(self.lienzo.size(), QImage.Format.Format_RGBA8888)  # Correct access here
        lienzo_completo.fill(Qt.GlobalColor.transparent)  # Fill with transparency

        painter = QPainter(lienzo_completo)
        painter.drawImage(0, 0, imagen1)  # Draw the first image

        # Use imagen2 directly since it is already a QImage
        painter.drawImage(0, 0, imagen2)  # Draw the second image
        painter.end()

        return lienzo_completo

    def draw_line(self, start_point, end_point):
        painter = QPainter(self.lienzo)

        # Configura el color y la opacidad del pincel
        brush_color_with_opacity = QColor(self.color_pincel)
        brush_color_with_opacity.setAlphaF(self.opacidad_pincel)

        # Si el borrador está activo, dibuja en blanco
        if self.modo_borrador:
            painter.setPen(QPen(Qt.GlobalColor.white, self.tamaño_pincel, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        else:
            if self.modo_pixel:
                # Configuración para pincel pixelado (sin suavizado)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
                painter.setPen(QPen(brush_color_with_opacity, self.tamaño_pincel, Qt.PenStyle.SolidLine, Qt.PenCapStyle.SquareCap, Qt.PenJoinStyle.BevelJoin))
            else:
                # Configuración para pincel normal (con suavizado)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                painter.setPen(QPen(brush_color_with_opacity, self.tamaño_pincel, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))

        # Dibuja la línea
        painter.drawLine(start_point, end_point)
        painter.end()

        # Actualiza el lienzo
        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(self.lienzo))
        self.update()

    def clear_canvas(self):
        self.lienzo.fill(Qt.GlobalColor.white)
        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(self.lienzo))
        self.update()

    def toggle_eraser(self, checked):
        self.modo_borrador = checked
        if checked:
            self.color_pincel = Qt.GlobalColor.white
            self.boton_rellenar.setChecked(False)
            self.boton_seleccionar.setChecked(False)  # Desactivar la selección
        else:
            self.color_pincel = Qt.GlobalColor.black

    def set_color(self, color):
        self.color_pincel = QColor(color)
        self.modo_borrador = False
        self.update_recent_colors(color)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_pincel = color
            self.modo_borrador = False
            self.update_recent_colors(color.name())

    def update_recent_colors(self, color):
        if color not in self.colores_recientes:
            if len(self.colores_recientes) >= 4:
                self.colores_recientes.pop(0)
            self.colores_recientes.append(color)
            self.update_recent_palette()

    def update_recent_palette(self):
        # Limpia la paleta reciente
        for i in reversed(range(self.diseno_paleta_reciente.count())):
            widget = self.diseno_paleta_reciente.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Añade los colores recientes
        for i, color in enumerate(self.colores_recientes):
            color_btn = QPushButton ()
            color_btn.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            color_btn.setFixedSize(50, 50)
            color_btn.clicked.connect(lambda checked, col=color: self.set_color(col))
            self.diseno_paleta_reciente.addWidget(color_btn, i // 2, i % 2)

    def change_tolerance(self, value):
        self.tolerancia = value

    def fill_canvas(self, start_pos, fill_color):
        target_color = QColor(self.lienzo.pixel(start_pos))
        if target_color != fill_color:
            self.flood_fill(start_pos, fill_color)
            self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(self.lienzo))
            self.update()

    def flood_fill(self, start, fill_color):
        width = self.lienzo.width()
        height = self.lienzo.height()

        target_color = QColor(self.lienzo.pixel(start.x(), start.y()))

        if self.is_similar_color(target_color, fill_color):
            return

        stack = [start]

        while stack:
            point = stack.pop()
            x, y = point.x(), point.y()

            if x < 0 or x >= width or y < 0 or y >= height:
                continue

            current_color = QColor(self.lienzo.pixel(x, y))
            if not self.is_similar_color(current_color, target_color):
                continue

            self.lienzo.setPixelColor(x, y, fill_color)
            stack.extend([QPoint(x + 1, y), QPoint(x - 1, y), QPoint(x, y + 1), QPoint(x, y - 1)])

        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(self.lienzo))
        self.update()

    def is_similar_color(self, color1, color2):
        return (abs(color1.red() - color2.red()) <= self.tolerancia and
                abs(color1.green() - color2.green()) <= self.tolerancia and
                abs(color1.blue () - color2.blue()) <= self.tolerancia)
                
    def guardar_lienzo(self, ruta=None, formato="PNG"):
        """ Guarda el contenido del lienzo en un archivo en el formato especificado (PNG o JPG). """
        if ruta is None:
            # Si no se pasa ruta, abre un cuadro de diálogo para elegir dónde guardar el archivo
            ruta, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Imagen PNG (*.png);;Imagen JPG (*.jpg)")
        
        if ruta:
            # Renderizar el contenido del lienzo en un QImage
            lienzo_completo = QImage(self.lienzo.size(), QImage.Format.Format_RGB32)
            lienzo_completo.fill(Qt.GlobalColor.transparent)  # Lienzo transparente

            painter = QPainter(lienzo_completo)
            self.etiqueta_lienzo.render(painter)
            painter.end()

            # Convertir el QImage a un formato que PIL pueda manejar y guardarlo
            buffer = lienzo_completo.bits()
            buffer.setsize(lienzo_completo.bytesPerLine() * lienzo_completo.height())  
            data = buffer.asstring(lienzo_completo.bytesPerLine() * lienzo_completo.height())

            # Crear la imagen PIL a partir del buffer
            pil_image = PILImage.frombuffer("RGBA", (lienzo_completo.width(), lienzo_completo.height()), data, "raw", "BGRA", 0, 1)

            # Guardar la imagen usando Pillow
            if formato == "PNG":
                pil_image.save(ruta, format="PNG") 
            elif formato == "JPEG":
                pil_image = pil_image.convert("RGB")
                pil_image.save(ruta, format="JPEG", quality=95)
