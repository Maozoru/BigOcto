import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from capa import Capa
from administrador_capas import AdministradorCapas
from estilos import tema_oscuro, tema_claro, tema_rosa

class LienzoDeDibujo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prototipo BigOcto")
        self.setFixedSize(1200, 800)

        # Atributos del pincel y herramientas
        self.color_pincel = Qt.GlobalColor.black
        self.tamaño_pincel = 5
        self.opacidad_pincel = 1.0
        self.ultimo_punto = QPoint()
        self.pincel_abajo = False
        self.modo_borrador = False
        self.seleccion_activa = False  # Estado de la selección
        self.modo_pixel = False  # Modo del pincel: False = Normal, True = Pixelado

        # Layout principal
        self.diseno_principal = QHBoxLayout(self)

        # Inicializa el lienzo
        self.lienzo = QImage(800, 800, QImage.Format.Format_ARGB32)
        self.lienzo.fill(Qt.GlobalColor.white)
        self.etiqueta_lienzo = QLabel(self)
        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(self.lienzo))
        self.diseno_principal.addWidget(self.etiqueta_lienzo, 1)

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
        self.boton_administrar_capas = QPushButton("Administrar capas", self)
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
            boton_color.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
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

        self.setLayout(self.diseno_principal)

    def abrir_administrador_capas(self):
        """ Abre la ventana de administración de capas. """
        if self.ventana_administrador_capas is None:
            self.ventana_administrador_capas = AdministradorCapas(self)
        self.ventana_administrador_capas.show()

    def crear_nueva_capa(self, name="Nueva Capa"):
        # Crea una nueva capa en blanco
        nueva_capa = Capa(name, QImage(800 , 800, QImage.Format.Format_ARGB32))
        nueva_capa.imagen.fill(Qt.GlobalColor.white)
        
        # Agrega la nueva capa a la lista de capas
        self.capas.append(nueva_capa)
        
        # Actualiza el índice de la capa actual
        self.indice_capa_actual = len(self.capas) - 1
        
        # Actualiza la lista de capas en la ventana de administración
        if self.ventana_administrador_capas is not None:
            self.ventana_administrador_capas.actualizar_lista_capas()

    def eliminar_capa(self, indice):
        if len(self.capas) > 1:
            del self.capas[indice]
            if indice < self.indice_capa_actual:
                self.indice_capa_actual -= 1
            elif indice == self.indice_capa_actual:
                if self.indice_capa_actual > 0:
                    self.indice_capa_actual -= 1
                else:
                    self.indice_capa_actual = 0
            if self.ventana_administrador_capas is not None:
                self.ventana_administrador_capas.actualizar_lista_capas()
            self.update_canvas()
        else:
            print("No se puede eliminar la última capa")

    def renombrar_capa(self, indice, nuevo_nombre):
        self.capas[indice].renombrar(nuevo_nombre)
        if self.ventana_administrador_capas is not None:
            self.ventana_administrador_capas.actualizar_lista_capas()

    def ocultar_capa(self, indice):
        self.capas[indice].visible = False
        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(self.capas[self.indice_capa_actual].imagen))
        self.update()

    def mostrar_capa(self, indice):
        self.capas[indice].visible = True
        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(self.capas[self.indice_capa_actual].imagen))
        self.update()

    def bloquear_capa(self, indice):
        self.capas[indice].bloqueada = True

    def desbloquear_capa(self, indice):
        self.capas[indice].bloqueada = False

    def ajustar_opacidad(self, indice, opacidad):
        self.capas[indice].opacidad = opacidad
        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(self.capas[self.indice_capa_actual].imagen))
        self.update()

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
        print("Modo Pincel Normal Activado")

    def select_pixel_brush(self):
        self.modo_pixel = True  # Activa el modo pixel
        print("Modo Pincel Pixelado Activado")

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
                self.draw_line(self.ultimo_punto, current_point)

            self.ultimo_punto = current_point
            self.pincel_abajo = True
        elif event.type() == QEvent.Type.TabletRelease:
            self.pincel_abajo = False
            self.ultimo_punto = QPoint()
    def draw_on_canvas(self, current_point):
        painter = QPainter(self.lienzo)
        painter.setPen(QPen(self.color_pincel, self.tamaño_pincel, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setOpacity(self.opacidad_pincel)

        if self.modo_borrador:
            painter.setCompositionMode(QPainter.CompositionMode.Clear)

        if self.modo_pixel:
            # Implement the pixelated brush drawing
            painter.drawPoint(current_point)
        else:
            if not self.ultimo_punto.isNull():
                painter.drawLine(self.ultimo_punto, current_point)

        self.ultimo_punto = current_point
        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(self.lienzo))
        self.update()

    def tabletReleaseEvent(self, event: QTabletEvent):
        """ Handle tablet release event to stop drawing. """
        self.pincel_abajo = False
        self.ultimo_punto = QPoint()  # Reset last point when the pen is lifted

    def tabletPressEvent(self, event: QTabletEvent):
        """ Handle tablet press event to start drawing. """
        self.pincel_abajo = True
        self.ultimo_punto = event.position().toPoint()  # Set the last point to the current position

    def paintEvent(self, event):
        painter = QPainter(self)

    def mouseMoveEvent(self, event):
        if self.pincel_abajo:
            current_point = event.position().toPoint()
            self.draw_line(self.ultimo_punto, current_point)
            self.ultimo_punto = current_point
            self.update()

    def mousePressEvent(self, event):
        if self.boton_rellenar.isChecked():
            start_pos = event.position().toPoint()
            fill_color = QColor(self.color_pincel)
            self.fill_canvas(start_pos, fill_color)
        else:
            self.pincel_abajo = True
            self.ultimo_punto = event.position().toPoint()

    def mouseReleaseEvent(self, event):
        self.pincel_abajo = False
        self.ultimo_punto = QPoint()

    def update_canvas(self):
        """ Actualiza la visualización del lienzo con todas las capas. """
        lienzo_completo = QImage(self.lienzo.size(), QImage.Format.Format_ARGB32)
        lienzo_completo.fill(Qt.GlobalColor.transparent)

        # Dibujar todas las capas visibles
        for capa in self.capas:
            lienzo_completo = self.combinar_imagenes(lienzo_completo, capa.imagen)

        self.etiqueta_lienzo.setPixmap(QPixmap.fromImage(lienzo_completo))

    def combinar_imagenes(self, imagen1, imagen2):
        """ Combina dos imágenes QImage respetando la transparencia. """
        pixmap1 = QPixmap.fromImage(imagen1)
        pixmap2 = QPixmap.fromImage(imagen2)

        painter = QPainter(pixmap1)
        painter.drawPixmap(0, 0, pixmap2)
        painter.end()

        return pixmap1.toImage()

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
            color_btn = QPushButton()
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
                abs(color1.blue() - color2.blue()) <= self.tolerancia)
